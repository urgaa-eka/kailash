"""Reporting (L2/L4) — trial balance, Schedule III statements, snapshots."""
from __future__ import annotations

from decimal import Decimal

import psycopg

from .posting import as_money


def trial_balance(conn: psycopg.Connection, fy: str) -> dict:
    rows = conn.execute(
        "SELECT * FROM co_v_trial_balance WHERE fy = %s ORDER BY account_code",
        (fy,),
    ).fetchall()
    total_debit = sum((Decimal(str(r["total_debit"])) for r in rows), Decimal("0"))
    total_credit = sum((Decimal(str(r["total_credit"])) for r in rows), Decimal("0"))
    return {
        "fy": fy,
        "accounts": [
            {
                "account_code": r["account_code"],
                "account_name": r["account_name"],
                "schedule_iii_group": r["schedule_iii_group"],
                "fin_class": r["fin_class"],
                "normal_balance": r["normal_balance"],
                "total_debit": str(as_money(r["total_debit"])),
                "total_credit": str(as_money(r["total_credit"])),
                "net_movement": str(as_money(r["net_movement"])),
            }
            for r in rows
        ],
        "total_debit": str(as_money(total_debit)),
        "total_credit": str(as_money(total_credit)),
        "balanced": as_money(total_debit) == as_money(total_credit),
    }


def schedule_iii(conn: psycopg.Connection, fy: str) -> dict:
    rows = conn.execute(
        "SELECT * FROM co_v_schedule_iii WHERE fy = %s ORDER BY statement, schedule_iii_group",
        (fy,),
    ).fetchall()
    pl = [r for r in rows if r["statement"] == "PL"]
    bs = [r for r in rows if r["statement"] == "BS"]

    eq = conn.execute(
        "SELECT * FROM co_v_accounting_equation WHERE fy = %s", (fy,)
    ).fetchone()
    profit = Decimal(str(eq["profit"])) if eq else Decimal("0")
    assets = Decimal(str(eq["assets"])) if eq else Decimal("0")
    liabilities = Decimal(str(eq["liabilities"])) if eq else Decimal("0")
    equity = Decimal(str(eq["equity"])) if eq else Decimal("0")

    return {
        "fy": fy,
        "profit_and_loss": [
            {"schedule_iii_group": r["schedule_iii_group"], "amount": str(as_money(r["amount"]))}
            for r in pl
        ],
        "balance_sheet": [
            {"schedule_iii_group": r["schedule_iii_group"], "amount": str(as_money(r["amount"]))}
            for r in bs
        ],
        "profit_after_adjustments": str(as_money(profit)),
        "equation": {
            "assets": str(as_money(assets)),
            "liabilities": str(as_money(liabilities)),
            "equity": str(as_money(equity)),
            "profit": str(as_money(profit)),
            # Retained profit closes into equity at year end; in-year the
            # identity is assets = liabilities + equity + profit.
            "holds": as_money(assets) == as_money(liabilities + equity + profit),
        },
    }


def snapshot_financials(conn: psycopg.Connection, fy: str) -> dict:
    """Version the current Schedule III rollup into co_financial_statement_line."""
    ver_row = conn.execute(
        "SELECT COALESCE(MAX(version), 0) + 1 AS v FROM co_financial_statement_line WHERE fy = %s",
        (fy,),
    ).fetchone()
    version = ver_row["v"]
    rows = conn.execute(
        "SELECT * FROM co_v_schedule_iii WHERE fy = %s", (fy,)
    ).fetchall()
    for r in rows:
        conn.execute(
            """
            INSERT INTO co_financial_statement_line
                (fy, statement, schedule_iii_group, amount, version)
            VALUES (%s,%s,%s,%s,%s)
            """,
            (fy, r["statement"], r["schedule_iii_group"], r["amount"], version),
        )
    return {"fy": fy, "version": version, "lines": len(rows)}


def ledger_account_balance(conn: psycopg.Connection, fy: str, codes: list[str]) -> Decimal:
    row = conn.execute(
        """
        SELECT COALESCE(SUM(l.debit - l.credit), 0) AS bal
        FROM co_journal_line l
        JOIN co_journal j ON j.journal_id = l.journal_id AND j.fy = l.fy
        JOIN co_account a ON a.account_id = l.account_id
        WHERE j.status IN ('posted','reversed') AND l.fy = %s
          AND a.account_code = ANY(%s)
        """,
        (fy, codes),
    ).fetchone()
    return Decimal(str(row["bal"]))
