"""Posting engine — the only writer to the L1 ledger.

Flow: draft journal + lines -> maker-checker post (DB triggers enforce
Σdr=Σcr, maker≠checker, immutability) -> corrections via reversal only.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import psycopg

from backend.shared import NotFoundError, ValidationError

from . import events
from .db import audit, fy_for

VOUCHER_PREFIX = {
    "SALES": "INV", "PURCHASE": "PUR", "RECEIPT": "RCT", "PAYMENT": "PAY",
    "CONTRA": "CTR", "JOURNAL": "JRN", "CREDIT_NOTE": "CRN",
    "DEBIT_NOTE": "DBN", "OPENING": "OPN", "PAYROLL": "PRL",
}


def next_voucher_no(
    conn: psycopg.Connection, gstin_id: int, voucher_type: str, fy: str
) -> str:
    """Gap-free, per-GSTIN, per-FY numbering (row-locked increment)."""
    row = conn.execute(
        """
        SELECT series_id, prefix, last_number FROM co_document_series
        WHERE gstin_id = %s AND voucher_type = %s AND fy = %s
        FOR UPDATE
        """,
        (gstin_id, voucher_type, fy),
    ).fetchone()
    if row is None:
        prefix = VOUCHER_PREFIX.get(voucher_type, "VCH")
        row = conn.execute(
            """
            INSERT INTO co_document_series (gstin_id, voucher_type, fy, prefix, last_number)
            VALUES (%s, %s, %s, %s, 0)
            RETURNING series_id, prefix, last_number
            """,
            (gstin_id, voucher_type, fy, prefix),
        ).fetchone()
    number = row["last_number"] + 1
    conn.execute(
        "UPDATE co_document_series SET last_number = %s WHERE series_id = %s",
        (number, row["series_id"]),
    )
    return f"{row['prefix']}/{fy}/{number:05d}"


def find_journal_by_hash(conn: psycopg.Connection, source_hash: str) -> dict | None:
    """Global (cross-FY) idempotency lookup."""
    return conn.execute(
        "SELECT journal_id, fy, voucher_no, status FROM co_journal WHERE source_hash = %s",
        (source_hash,),
    ).fetchone()


def create_journal(
    conn: psycopg.Connection,
    *,
    voucher_type: str,
    voucher_date: date,
    gstin_id: int,
    lines: list[dict],
    narration: str | None = None,
    source_ref: str | None = None,
    source_hash: str | None = None,
    origin: str = "KAILASH",
    maker: str,
    fy: str | None = None,
    reverses_journal_id: int | None = None,
    reverses_fy: str | None = None,
) -> dict:
    """Insert a draft journal with its lines. Lines: {account_id, debit,
    credit, party_id?, item_id?, tax_rate_id?, hsn_sac?, place_of_supply?}."""
    if not lines:
        raise ValidationError("journal requires at least one line")
    fy = fy or fy_for(voucher_date)
    if source_hash:
        existing = find_journal_by_hash(conn, source_hash)
        if existing:
            return {**existing, "deduped": True}
    voucher_no = next_voucher_no(conn, gstin_id, voucher_type, fy)
    j = conn.execute(
        """
        INSERT INTO co_journal
            (voucher_type, voucher_no, voucher_date, fy, gstin_id, narration,
             source_ref, source_hash, origin, maker,
             reverses_journal_id, reverses_fy)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING journal_id, fy, voucher_no, status
        """,
        (
            voucher_type, voucher_no, voucher_date, fy, gstin_id,
            narration, source_ref, source_hash, origin, maker,
            reverses_journal_id, reverses_fy,
        ),
    ).fetchone()
    for i, ln in enumerate(lines, start=1):
        conn.execute(
            """
            INSERT INTO co_journal_line
                (journal_id, fy, line_no, account_id, debit, credit,
                 party_id, item_id, cost_center_id, tax_rate_id, hsn_sac,
                 place_of_supply)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                j["journal_id"], fy, i, ln["account_id"],
                ln.get("debit", 0), ln.get("credit", 0),
                ln.get("party_id"), ln.get("item_id"), ln.get("cost_center_id"),
                ln.get("tax_rate_id"), ln.get("hsn_sac"), ln.get("place_of_supply"),
            ),
        )
    return {**j, "deduped": False}


def post_journal(
    conn: psycopg.Connection, journal_id: int, fy: str, checker: str
) -> dict:
    """Flip draft -> posted. The DB triggers enforce balance + maker≠checker."""
    try:
        row = conn.execute(
            """
            UPDATE co_journal SET status = 'posted', checker = %s
            WHERE journal_id = %s AND fy = %s AND status = 'draft'
            RETURNING journal_id, fy, voucher_no, status, posted_at, maker, checker
            """,
            (checker, journal_id, fy),
        ).fetchone()
    except psycopg.errors.RaiseException as exc:
        raise ValidationError(str(exc.diag.message_primary or exc)) from exc
    if row is None:
        exists = conn.execute(
            "SELECT status FROM co_journal WHERE journal_id = %s AND fy = %s",
            (journal_id, fy),
        ).fetchone()
        if exists is None:
            raise NotFoundError(f"journal {journal_id} ({fy}) not found")
        raise ValidationError(
            f"journal {journal_id} is '{exists['status']}', only drafts can be posted"
        )
    audit(conn, checker, "post", "co_journal", f"{journal_id}/{fy}",
          after={"voucher_no": row["voucher_no"], "status": "posted"})
    events.journal_posted(row)
    return row


def create_and_post(
    conn: psycopg.Connection, *, maker: str, checker: str, **kwargs
) -> dict:
    j = create_journal(conn, maker=maker, **kwargs)
    if j.get("deduped"):
        return j
    posted = post_journal(conn, j["journal_id"], j["fy"], checker)
    return {**posted, "deduped": False}


def reverse_journal(
    conn: psycopg.Connection,
    journal_id: int,
    fy: str,
    *,
    maker: str,
    checker: str,
    narration: str | None = None,
) -> dict:
    """Correction path: post an equal-and-opposite journal, then mark the
    original 'reversed'. Never mutates the original's lines."""
    original = conn.execute(
        "SELECT * FROM co_journal WHERE journal_id = %s AND fy = %s",
        (journal_id, fy),
    ).fetchone()
    if original is None:
        raise NotFoundError(f"journal {journal_id} ({fy}) not found")
    if original["status"] != "posted":
        raise ValidationError("only posted journals can be reversed")
    lines = conn.execute(
        "SELECT * FROM co_journal_line WHERE journal_id = %s AND fy = %s ORDER BY line_no",
        (journal_id, fy),
    ).fetchall()
    flipped = [
        {
            "account_id": ln["account_id"],
            "debit": ln["credit"],
            "credit": ln["debit"],
            "party_id": ln["party_id"],
            "item_id": ln["item_id"],
            "cost_center_id": ln["cost_center_id"],
            "tax_rate_id": ln["tax_rate_id"],
            "hsn_sac": ln["hsn_sac"],
            "place_of_supply": ln["place_of_supply"],
        }
        for ln in lines
    ]
    rev = create_journal(
        conn,
        voucher_type="JOURNAL",
        voucher_date=original["voucher_date"],
        gstin_id=original["gstin_id"],
        lines=flipped,
        narration=narration or f"Reversal of {original['voucher_no']}",
        source_ref=f"reversal:{original['voucher_no']}",
        maker=maker,
        fy=fy,
        reverses_journal_id=journal_id,
        reverses_fy=fy,
    )
    post_journal(conn, rev["journal_id"], rev["fy"], checker)
    conn.execute(
        "UPDATE co_journal SET status = 'reversed' WHERE journal_id = %s AND fy = %s",
        (journal_id, fy),
    )
    audit(conn, checker, "reverse", "co_journal", f"{journal_id}/{fy}",
          after={"reversal_journal_id": rev["journal_id"]})
    return {
        "reversed_journal_id": journal_id,
        "reversal_journal_id": rev["journal_id"],
        "fy": fy,
    }


def get_journal(conn: psycopg.Connection, journal_id: int, fy: str) -> dict:
    j = conn.execute(
        "SELECT * FROM co_journal WHERE journal_id = %s AND fy = %s",
        (journal_id, fy),
    ).fetchone()
    if j is None:
        raise NotFoundError(f"journal {journal_id} ({fy}) not found")
    j["lines"] = conn.execute(
        "SELECT * FROM co_journal_line WHERE journal_id = %s AND fy = %s ORDER BY line_no",
        (journal_id, fy),
    ).fetchall()
    return j


def as_money(v) -> Decimal:
    return Decimal(str(v)).quantize(Decimal("0.01"))
