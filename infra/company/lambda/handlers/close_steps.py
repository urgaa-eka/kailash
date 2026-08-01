"""Period-end close — the Step Functions state machine's step handlers.

One Lambda, dispatched on event["step"]:
  lock_period -> build_gstr1 -> build_gstr3b -> build_statements
              -> run_recon -> publish_facts

Input shape (threaded through the whole execution):
  {"step": "...", "fy": "2025-26", "gstin": "27...", "period": "102025",
   "externals": {...optional CA figures...}}

Every step is a pure function of the ledger; a re-run is safe (returns
upsert, snapshots version, recon appends a new run).
"""
from __future__ import annotations

from handlers.common import resolve_db_url

resolve_db_url()

from decimal import Decimal  # noqa: E402

from backend.services.company.app import events, gst, recon, reports  # noqa: E402
from backend.services.company.app.db import audit, get_conn  # noqa: E402


def _lock_period(conn, p):
    # The ledger is already append-only; "locking" is an audited statement
    # of intent that the period build has begun (visible at diligence).
    audit(conn, "period-close", "lock_period", "co_journal",
          f"{p['fy']}/{p['period']}", after={"period": p["period"]})
    return {"locked": True}


def _build_gstr1(conn, p):
    payload = gst.generate_gstr1(conn, p["gstin"], p["period"])
    return {"invoices": payload["totals"]["invoices"],
            "taxable_value": payload["totals"]["taxable_value"]}


def _build_gstr3b(conn, p):
    return gst.generate_gstr3b(conn, p["gstin"], p["period"])


def _build_statements(conn, p):
    return reports.snapshot_financials(conn, p["fy"])


def _run_recon(conn, p):
    result = recon.run_reconciliation(
        conn, fy=p["fy"], period_label=p.get("period") or p["fy"],
        externals=p.get("externals") or {},
    )
    return {k: result[k] for k in
            ("control_points_run", "matched", "open_variances")}


def _publish_facts(conn, p):
    s3 = reports.schedule_iii(conn, p["fy"])
    tb = reports.trial_balance(conn, p["fy"])
    facts = {
        "fy": p["fy"],
        "revenue": next((r["amount"] for r in s3["profit_and_loss"]
                         if r["schedule_iii_group"] == "Revenue from Operations"),
                        "0.00"),
        "profit": s3["profit_after_adjustments"],
        "assets": s3["equation"]["assets"],
        "books_balanced": tb["balanced"],
        "equation_holds": s3["equation"]["holds"],
    }
    events.financial_facts_published(facts)
    return facts


STEPS = {
    "lock_period": _lock_period,
    "build_gstr1": _build_gstr1,
    "build_gstr3b": _build_gstr3b,
    "build_statements": _build_statements,
    "run_recon": _run_recon,
    "publish_facts": _publish_facts,
}


def handler(event, context=None):  # noqa: ANN001
    step = event["step"]
    fn = STEPS.get(step)
    if fn is None:
        raise ValueError(f"unknown close step {step}")
    with get_conn() as conn:
        out = fn(conn, event)

    def _plain(v):
        return str(v) if isinstance(v, Decimal) else v

    return {**event, "result": {k: _plain(v) for k, v in out.items()}}
