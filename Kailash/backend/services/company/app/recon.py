"""Reconciliation engine (L3) — internal Kailash <-> CA/Tally/GSTN.

Each control point computes its internal value from the ledger; the
external value comes from the CA/portal (request payload) or, for the
cross-internal checks (GSTR1_VS_3B, BOOKS_VS_GST_TURNOVER), from the other
internal artefact. Variances get a tolerance-banded severity and a
resolution workflow; nothing is auto-erased.
"""
from __future__ import annotations

from decimal import Decimal

import psycopg

from backend.platform import NotFoundError, ValidationError

from . import events
from .posting import as_money
from .reports import ledger_account_balance

REVENUE_GROUPS = ("Revenue from Operations",)
PURCHASE_GROUPS = ("Purchases of Stock-in-Trade", "Cost of Materials Consumed")


def _sum_schedule_groups(conn, fy: str, groups: tuple, credit_normal: bool) -> Decimal:
    row = conn.execute(
        """
        SELECT COALESCE(SUM(CASE WHEN %s THEN l.credit - l.debit
                                 ELSE l.debit - l.credit END), 0) AS v
        FROM co_journal_line l
        JOIN co_journal j ON j.journal_id = l.journal_id AND j.fy = l.fy
        JOIN co_account a ON a.account_id = l.account_id
        WHERE j.status IN ('posted','reversed') AND l.fy = %s
          AND a.schedule_iii_group = ANY(%s)
        """,
        (credit_normal, fy, list(groups)),
    ).fetchone()
    return Decimal(str(row["v"]))


def _gstr1_taxable_total(conn, fy: str) -> Decimal:
    row = conn.execute(
        """
        SELECT COALESCE(SUM(f.taxable_value), 0) AS v
        FROM co_v_gstr1_feed f
        JOIN co_fiscal_calendar c ON c.cal_date = f.invoice_date
        WHERE c.fy = %s
        """,
        (fy,),
    ).fetchone()
    return Decimal(str(row["v"]))


def _gstr3b_outward_total(conn, fy: str) -> Decimal:
    row = conn.execute(
        """
        SELECT COALESCE(SUM(s.outward_taxable), 0) AS v
        FROM co_gstr3b_summary s
        WHERE EXISTS (
            SELECT 1 FROM co_fiscal_calendar c
            WHERE c.gst_period = s.gst_period AND c.fy = %s
        )
        """,
        (fy,),
    ).fetchone()
    return Decimal(str(row["v"]))


def compute_internal(conn: psycopg.Connection, code: str, fy: str) -> Decimal:
    if code == "FY_SALES":
        return _sum_schedule_groups(conn, fy, REVENUE_GROUPS, credit_normal=True)
    if code == "FY_PURCHASES":
        return _sum_schedule_groups(conn, fy, PURCHASE_GROUPS, credit_normal=False)
    if code == "OUTPUT_TAX":
        row = conn.execute(
            """
            SELECT COALESCE(SUM(s.output_tax), 0) AS v FROM co_gstr3b_summary s
            WHERE EXISTS (SELECT 1 FROM co_fiscal_calendar c
                          WHERE c.gst_period = s.gst_period AND c.fy = %s)
            """,
            (fy,),
        ).fetchone()
        return Decimal(str(row["v"]))
    if code == "GSTR1_VS_3B":
        return _gstr1_taxable_total(conn, fy)
    if code == "ITC_CLAIMED":
        row = conn.execute(
            """
            SELECT COALESCE(SUM(i.itc_amount), 0) AS v FROM co_itc_register i
            WHERE i.status = 'eligible'
              AND EXISTS (SELECT 1 FROM co_fiscal_calendar c
                          WHERE c.gst_period = i.gst_period AND c.fy = %s)
            """,
            (fy,),
        ).fetchone()
        return Decimal(str(row["v"]))
    if code == "BOOKS_VS_GST_TURNOVER":
        return _sum_schedule_groups(conn, fy, REVENUE_GROUPS, credit_normal=True)
    if code == "NET_PROFIT":
        row = conn.execute(
            "SELECT profit FROM co_v_accounting_equation WHERE fy = %s", (fy,)
        ).fetchone()
        return Decimal(str(row["profit"])) if row else Decimal("0")
    if code == "CLOSING_BALANCES":
        # bank + cash + debtors - creditors (net working position of the
        # key control ledgers, matching Tally's closing-balance sheet).
        return (
            ledger_account_balance(conn, fy, ["5030", "5020", "5010"])
            - (-ledger_account_balance(conn, fy, ["3010"]))
        )
    if code == "TDS_DEDUCTED":
        row = conn.execute(
            "SELECT COALESCE(SUM(tds_amount),0) AS v FROM co_tds_ledger WHERE fy = %s",
            (fy,),
        ).fetchone()
        return Decimal(str(row["v"]))
    if code == "BANK_BALANCE":
        return ledger_account_balance(conn, fy, ["5030"])
    raise ValidationError(f"unknown control point {code}")


def _cross_external(conn: psycopg.Connection, code: str, fy: str) -> Decimal | None:
    """External side computable from another internal artefact."""
    if code == "GSTR1_VS_3B":
        return _gstr3b_outward_total(conn, fy)
    if code == "BOOKS_VS_GST_TURNOVER":
        return _gstr1_taxable_total(conn, fy)
    return None


def run_reconciliation(
    conn: psycopg.Connection,
    *,
    fy: str,
    period_label: str | None = None,
    externals: dict[str, float] | None = None,
) -> dict:
    externals = externals or {}
    period_label = period_label or fy
    cps = conn.execute(
        "SELECT * FROM co_recon_control_point WHERE active ORDER BY cp_id"
    ).fetchall()
    results = []
    for cp in cps:
        code = cp["code"]
        internal = as_money(compute_internal(conn, code, fy))
        if code in externals and externals[code] is not None:
            external = as_money(externals[code])
            ref_ext = "provided:CA/portal"
        else:
            cross = _cross_external(conn, code, fy)
            if cross is None:
                continue  # no external value available -> not run this cycle
            external = as_money(cross)
            ref_ext = "computed:cross-internal"

        run = conn.execute(
            """
            INSERT INTO co_recon_run
                (cp_id, period_label, value_internal, value_external,
                 ref_internal, ref_external)
            VALUES (%s,%s,%s,%s,%s,%s)
            RETURNING run_id
            """,
            (cp["cp_id"], period_label, internal, external,
             cp["source_a"], ref_ext),
        ).fetchone()

        variance = internal - external
        tol_abs = Decimal(str(cp["tolerance_abs"]))
        tol_pct = Decimal(str(cp["tolerance_pct"]))
        tol = max(tol_abs, abs(external) * tol_pct / 100)
        if abs(variance) <= tol:
            severity, status = "matched", "resolved"
        elif abs(variance) <= max(abs(external), Decimal("1")) * Decimal("0.01"):
            severity, status = "minor", "open"
        else:
            severity, status = "material", "open"
        variance_pct = (
            float(variance / external * 100) if external != 0 else None
        )
        conn.execute(
            """
            INSERT INTO co_recon_variance
                (run_id, variance_amt, variance_pct, severity, status)
            VALUES (%s,%s,%s,%s,%s)
            """,
            (run["run_id"], as_money(variance), variance_pct, severity, status),
        )
        results.append({
            "code": code,
            "internal": str(internal),
            "external": str(external),
            "external_ref": ref_ext,
            "variance": str(as_money(variance)),
            "severity": severity,
            "status": status,
        })
    open_count = sum(1 for r in results if r["status"] == "open")
    summary = {
        "fy": fy, "period_label": period_label,
        "control_points_run": len(results),
        "matched": sum(1 for r in results if r["severity"] == "matched"),
        "open_variances": open_count,
        "results": results,
    }
    events.reconciliation_completed(summary)
    return summary


def open_variances(conn: psycopg.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM co_v_open_variances ORDER BY code"
    ).fetchall()
    return [
        {**r,
         "value_internal": str(r["value_internal"]),
         "value_external": str(r["value_external"]),
         "variance_amt": str(r["variance_amt"]),
         "variance_pct": float(r["variance_pct"]) if r["variance_pct"] is not None else None}
        for r in rows
    ]


def resolve_variance(
    conn: psycopg.Connection,
    variance_id: int,
    *,
    status: str,
    owner: str | None = None,
    root_cause: str | None = None,
    note: str | None = None,
) -> dict:
    if status not in ("open", "investigating", "resolved", "accepted"):
        raise ValidationError(f"invalid variance status {status}")
    row = conn.execute(
        """
        UPDATE co_recon_variance
        SET status = %s,
            owner = COALESCE(%s, owner),
            root_cause = COALESCE(%s, root_cause),
            note = COALESCE(%s, note),
            updated_at = now()
        WHERE variance_id = %s
        RETURNING variance_id, status, owner, root_cause, note
        """,
        (status, owner, root_cause, note, variance_id),
    ).fetchone()
    if row is None:
        raise NotFoundError(f"variance {variance_id} not found")
    return row
