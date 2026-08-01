"""Adversarial DB-level tests — prove each hardened invariant is enforced
by the database itself, not just by the API layer.

Every attack goes straight at Postgres via raw SQL (bypassing the service),
mirroring the schema-review findings C1-C4 / N4 / N6 / N7.
"""
from __future__ import annotations

import psycopg
import pytest

FY = "2025-26"
GSTIN = "27AAICG1234F1Z5"


@pytest.fixture(scope="module", autouse=True)
def inv_env(db):
    """Self-sufficient fixtures: this module must pass regardless of whether
    the e2e module ran first. Company setup is idempotent; the seed journal
    touches balance-sheet accounts only (no P&L side effects for e2e)."""
    r = db.post("/admin/company", json={
        "legal_name": "Go4Garage Test Pvt Ltd",
        "incorporation_dt": "2024-06-01",
        "gstin": GSTIN,
    })
    assert r.status_code == 200, r.text
    j = db.post("/journal", json={
        "gstin": GSTIN, "voucher_date": "2025-05-01",
        "narration": "invariant fixture", "maker": "alice",
        "lines": [
            {"account_code": "5020", "debit": 10},
            {"account_code": "1010", "credit": 10},
        ],
    }).json()["data"]
    p = db.post(f"/journal/{j['fy']}/{j['journal_id']}/post",
                json={"checker": "bob"})
    assert p.status_code == 200, p.text


def _any_gstin_id(raw_conn) -> int:
    row = raw_conn.execute("SELECT gstin_id FROM co_gstin LIMIT 1").fetchone()
    assert row, "inv_env must have created a GSTIN"
    return row["gstin_id"]


def _posted_journal(raw_conn) -> dict:
    row = raw_conn.execute(
        "SELECT journal_id, fy FROM co_journal WHERE status = 'posted' LIMIT 1"
    ).fetchone()
    assert row, "inv_env must have posted at least one journal"
    return row


def test_c1_insert_as_posted_rejected(raw_conn):
    gid = _any_gstin_id(raw_conn)
    with pytest.raises(psycopg.errors.RaiseException, match="cannot be INSERTed as posted"):
        raw_conn.execute(
            """
            INSERT INTO co_journal (voucher_type, voucher_no, voucher_date,
                                    fy, gstin_id, status)
            VALUES ('JOURNAL', 'ATTACK-1', '2025-06-01', %s, %s, 'posted')
            """,
            (FY, gid),
        )


def test_c2_posted_lines_frozen(raw_conn):
    j = _posted_journal(raw_conn)
    with pytest.raises(psycopg.errors.RaiseException, match="immutable"):
        raw_conn.execute(
            "UPDATE co_journal_line SET debit = 999999 WHERE journal_id = %s AND fy = %s AND debit > 0",
            (j["journal_id"], j["fy"]),
        )
    with pytest.raises(psycopg.errors.RaiseException, match="immutable"):
        raw_conn.execute(
            "DELETE FROM co_journal_line WHERE journal_id = %s AND fy = %s",
            (j["journal_id"], j["fy"]),
        )
    with pytest.raises(psycopg.errors.RaiseException, match="immutable"):
        raw_conn.execute(
            """
            INSERT INTO co_journal_line (journal_id, fy, line_no, account_id, debit, credit)
            SELECT %s, %s, 99, account_id, 1, 0 FROM co_account LIMIT 1
            """,
            (j["journal_id"], j["fy"]),
        )


def test_c3_unpost_rejected(raw_conn):
    j = _posted_journal(raw_conn)
    with pytest.raises(psycopg.errors.RaiseException, match="Cannot un-post"):
        raw_conn.execute(
            "UPDATE co_journal SET status = 'draft' WHERE journal_id = %s AND fy = %s",
            (j["journal_id"], j["fy"]),
        )


def test_c3_posted_header_immutable(raw_conn):
    j = _posted_journal(raw_conn)
    with pytest.raises(psycopg.errors.RaiseException, match="immutable"):
        raw_conn.execute(
            "UPDATE co_journal SET narration = 'tampered' WHERE journal_id = %s AND fy = %s",
            (j["journal_id"], j["fy"]),
        )
    with pytest.raises(psycopg.errors.RaiseException, match="immutable"):
        raw_conn.execute(
            "DELETE FROM co_journal WHERE journal_id = %s AND fy = %s",
            (j["journal_id"], j["fy"]),
        )


def test_c4_duplicate_source_hash_rejected(raw_conn):
    gid = _any_gstin_id(raw_conn)
    raw_conn.execute(
        """
        INSERT INTO co_journal (voucher_type, voucher_no, voucher_date, fy,
                                gstin_id, maker, source_hash)
        VALUES ('JOURNAL', 'DUP-A', '2025-06-02', %s, %s, 'x', 'dup-hash-1')
        """,
        (FY, gid),
    )
    with pytest.raises(psycopg.errors.UniqueViolation):
        raw_conn.execute(
            """
            INSERT INTO co_journal (voucher_type, voucher_no, voucher_date, fy,
                                    gstin_id, maker, source_hash)
            VALUES ('JOURNAL', 'DUP-B', '2025-06-03', %s, %s, 'x', 'dup-hash-1')
            """,
            (FY, gid),
        )


def test_n6_maker_checker_enforced_in_db(raw_conn):
    gid = _any_gstin_id(raw_conn)
    raw_conn.execute(
        """
        INSERT INTO co_journal (voucher_type, voucher_no, voucher_date, fy,
                                gstin_id, maker)
        VALUES ('JOURNAL', 'MC-1', '2025-06-04', %s, %s, 'mallory')
        """,
        (FY, gid),
    )
    acc = raw_conn.execute("SELECT account_id FROM co_account LIMIT 2").fetchall()
    jid = raw_conn.execute(
        "SELECT journal_id FROM co_journal WHERE voucher_no = 'MC-1' AND fy = %s",
        (FY,),
    ).fetchone()["journal_id"]
    raw_conn.execute(
        "INSERT INTO co_journal_line (journal_id, fy, line_no, account_id, debit) VALUES (%s,%s,1,%s,10)",
        (jid, FY, acc[0]["account_id"]),
    )
    raw_conn.execute(
        "INSERT INTO co_journal_line (journal_id, fy, line_no, account_id, credit) VALUES (%s,%s,2,%s,10)",
        (jid, FY, acc[1]["account_id"]),
    )
    with pytest.raises(psycopg.errors.RaiseException, match="distinct checker"):
        raw_conn.execute(
            "UPDATE co_journal SET status='posted', checker='mallory' WHERE journal_id = %s AND fy = %s",
            (jid, FY),
        )


def test_n7_audit_log_append_only(raw_conn):
    raw_conn.execute(
        "INSERT INTO co_audit_log (actor, action, entity) VALUES ('t', 'x', 'y')"
    )
    with pytest.raises(psycopg.errors.RaiseException, match="append-only"):
        raw_conn.execute("UPDATE co_audit_log SET actor = 'z' WHERE actor = 't'")
    with pytest.raises(psycopg.errors.RaiseException, match="append-only"):
        raw_conn.execute("DELETE FROM co_audit_log WHERE actor = 't'")


def test_n4_inconsistent_tax_rate_rejected(raw_conn):
    with pytest.raises(psycopg.errors.CheckViolation):
        raw_conn.execute(
            """
            INSERT INTO co_tax_rate (label, total_rate, cgst_rate, sgst_rate,
                                     igst_rate, effective_from)
            VALUES ('BAD SPLIT', 18, 5, 5, 18, '2025-09-22')
            """
        )


def test_n1_historical_fy_lands_in_default_partition(raw_conn):
    gid = _any_gstin_id(raw_conn)
    raw_conn.execute(
        """
        INSERT INTO co_journal (voucher_type, voucher_no, voucher_date, fy,
                                gstin_id, maker, origin)
        VALUES ('OPENING', 'HIST-1', '2022-04-01', '2022-23', %s, 'migration',
                'TALLY_MIGRATION')
        """,
        (gid,),
    )
    row = raw_conn.execute(
        "SELECT tableoid::regclass::text AS part FROM co_journal WHERE voucher_no = 'HIST-1'"
    ).fetchone()
    assert "default" in row["part"]
