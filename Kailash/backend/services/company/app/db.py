"""Database layer — connections, schema bootstrap, master seeding.

The ledger lives in PostgreSQL schema ``company`` (see
company-segment/schema/company_segment_schema.sql). Every connection pins
``search_path`` so the ``co_*`` objects resolve without qualification.
"""
from __future__ import annotations

import csv
import json
from contextlib import contextmanager
from datetime import date
from decimal import Decimal
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from backend.shared import UpstreamError, get_logger

from .settings import settings

log = get_logger("company.db")


def scaffold_dir() -> Path:
    if settings.company_scaffold_dir:
        return Path(settings.company_scaffold_dir)
    # backend/services/company/app/db.py -> repo root is 4 levels up.
    return Path(__file__).resolve().parents[4] / "company-segment"


@contextmanager
def get_conn():
    """One transaction per request: commit on success, rollback on error."""
    try:
        conn = psycopg.connect(
            settings.company_db_url,
            row_factory=dict_row,
            options="-c search_path=company,public",
        )
    except psycopg.OperationalError as exc:  # DB down/unreachable
        raise UpstreamError(
            "ledger database unavailable",
            hint="check COMPANY_DB_URL and that postgres is running",
        ) from exc
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fy_for(d: date) -> str:
    """Indian financial year label, e.g. 2025-06-01 -> '2025-26'."""
    start_year = d.year if d.month >= 4 else d.year - 1
    return f"{start_year}-{str(start_year + 1)[2:]}"


def gst_period_for(d: date) -> str:
    return f"{d.month:02d}{d.year}"


# ---------------------------------------------------------------------------
# Schema bootstrap
# ---------------------------------------------------------------------------

def init_schema(conn: psycopg.Connection) -> None:
    ddl = (scaffold_dir() / "schema" / "company_segment_schema.sql").read_text(
        encoding="utf-8"
    )
    conn.execute(ddl)
    log.info("schema_applied", extra={"event": "init"})


def populate_fiscal_calendar(conn: psycopg.Connection, d_from: date, d_to: date) -> int:
    row = conn.execute(
        "SELECT co_populate_fiscal_calendar(%s, %s) AS n", (d_from, d_to)
    ).fetchone()
    return row["n"]


# ---------------------------------------------------------------------------
# Master seeding from the scaffold CSVs (idempotent)
# ---------------------------------------------------------------------------

def _read_csv(name: str) -> list[dict]:
    path = scaffold_dir() / "templates" / name
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def seed_chart_of_accounts(conn: psycopg.Connection) -> int:
    rows = _read_csv("chart_of_accounts.csv")
    inserted = 0
    # Two passes: parents first (rows with no parent_code), then children —
    # the CSV is ordered parent-before-child, so a single ordered pass works.
    for r in rows:
        parent_id = None
        if r["parent_code"]:
            parent = conn.execute(
                "SELECT account_id FROM co_account WHERE account_code = %s",
                (r["parent_code"],),
            ).fetchone()
            if parent is None:
                raise ValueError(
                    f"COA row {r['account_code']}: parent {r['parent_code']} not found"
                )
            parent_id = parent["account_id"]
        cur = conn.execute(
            """
            INSERT INTO co_account
                (account_code, account_name, parent_id, account_type,
                 normal_balance, schedule_iii_group, tax_nature, is_leaf)
            VALUES (%s, %s, %s, %s, %s, %s, NULLIF(%s, ''), %s)
            ON CONFLICT (account_code) DO NOTHING
            """,
            (
                r["account_code"], r["account_name"], parent_id,
                r["account_type"], r["normal_balance"],
                r["schedule_iii_group"], r["tax_nature"],
                r["parent_code"] != "",  # groups become non-leaf below
            ),
        )
        inserted += cur.rowcount
    # Any account that is a parent is not a leaf.
    conn.execute(
        """
        UPDATE co_account a SET is_leaf = FALSE
        WHERE EXISTS (SELECT 1 FROM co_account c WHERE c.parent_id = a.account_id)
        """
    )
    return inserted


def seed_tax_rates(conn: psycopg.Connection) -> int:
    rows = _read_csv("hsn_gst_rate_master.csv")
    inserted = 0
    for r in rows:
        cur = conn.execute(
            """
            INSERT INTO co_tax_rate
                (label, total_rate, cgst_rate, sgst_rate, igst_rate,
                 cess_rate, effective_from, effective_to)
            SELECT %s, %s, %s, %s, %s, %s, %s, NULLIF(%s, '')::date
            WHERE NOT EXISTS (
                SELECT 1 FROM co_tax_rate
                WHERE label = %s AND effective_from = %s::date
            )
            """,
            (
                r["label"], r["total_rate"], r["cgst_rate"], r["sgst_rate"],
                r["igst_rate"], r["cess_rate"] or "0", r["effective_from"],
                r["effective_to"], r["label"], r["effective_from"],
            ),
        )
        inserted += cur.rowcount
    return inserted


def seed_parties(conn: psycopg.Connection) -> int:
    rows = _read_csv("party_master.csv")
    inserted = 0
    for r in rows:
        ledger = conn.execute(
            "SELECT account_id FROM co_account WHERE account_code = %s",
            (r["ledger_account_code"],),
        ).fetchone()
        cur = conn.execute(
            """
            INSERT INTO co_party
                (party_name, party_type, gstin, pan, state_code, is_msme,
                 udyam_no, tds_applicable, ledger_account_id)
            SELECT %s, %s, NULLIF(%s,''), NULLIF(%s,''), NULLIF(%s,''),
                   %s, NULLIF(%s,''), %s, %s
            WHERE NOT EXISTS (SELECT 1 FROM co_party WHERE party_name = %s)
            """,
            (
                r["party_name"], r["party_type"], r["gstin"], r["pan"],
                r["state_code"], r["is_msme"].upper() == "TRUE",
                r["udyam_no"], r["tds_applicable"].upper() == "TRUE",
                ledger["account_id"] if ledger else None,
                r["party_name"],
            ),
        )
        inserted += cur.rowcount
    return inserted


def seed_recon_control_points(conn: psycopg.Connection) -> int:
    rows = _read_csv("reconciliation_control_points.csv")
    inserted = 0
    for r in rows:
        cur = conn.execute(
            """
            INSERT INTO co_recon_control_point
                (code, description, source_a, source_b, tolerance_abs, tolerance_pct)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (code) DO NOTHING
            """,
            (
                r["code"], r["description"], r["source_a_internal"],
                r["source_b_external"], r["tolerance_abs"] or "0",
                r["tolerance_pct"] or "0",
            ),
        )
        inserted += cur.rowcount
    return inserted


def seed_all(conn: psycopg.Connection) -> dict:
    cal = populate_fiscal_calendar(conn, date(2023, 4, 1), date(2027, 3, 31))
    return {
        "fiscal_calendar_days": cal,
        "accounts": seed_chart_of_accounts(conn),
        "tax_rates": seed_tax_rates(conn),
        "parties": seed_parties(conn),
        "recon_control_points": seed_recon_control_points(conn),
    }


# ---------------------------------------------------------------------------
# Shared lookups
# ---------------------------------------------------------------------------

def account_by_code(conn: psycopg.Connection, code: str) -> dict:
    row = conn.execute(
        "SELECT * FROM co_account WHERE account_code = %s", (code,)
    ).fetchone()
    if row is None:
        raise ValueError(f"account {code} not found — seed the chart of accounts first")
    return row


def effective_tax_rate(
    conn: psycopg.Connection, total_rate: Decimal, on: date
) -> dict | None:
    return conn.execute(
        """
        SELECT * FROM co_tax_rate
        WHERE total_rate = %s AND effective_from <= %s
          AND (effective_to IS NULL OR effective_to >= %s)
        ORDER BY effective_from DESC LIMIT 1
        """,
        (total_rate, on, on),
    ).fetchone()


def audit(
    conn: psycopg.Connection,
    actor: str,
    action: str,
    entity: str,
    entity_id: str | None = None,
    before: dict | None = None,
    after: dict | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO co_audit_log (actor, action, entity, entity_id, before_val, after_val)
        VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb)
        """,
        (
            actor, action, entity, entity_id,
            json.dumps(before, default=str) if before is not None else None,
            json.dumps(after, default=str) if after is not None else None,
        ),
    )
