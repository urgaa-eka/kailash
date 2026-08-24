"""Tests for the Go4Garage data store and the DB-backed provider.

The round-trip tests need PostgreSQL (they use the `raw_conn` fixture, which
skips when COMPANY_DB_URL is unavailable); CI runs them against a live Postgres.
The provider-wiring test needs no database.
"""
from __future__ import annotations

from decimal import Decimal

from app.go4garage import DbProvider, store


class _FakeCursor:
    def fetchone(self):
        return None

    def fetchall(self):
        return []


class _FakeConn:
    def execute(self, *a, **k):
        return _FakeCursor()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_db_provider_reads_through_the_factory_without_data():
    prov = DbProvider(lambda: _FakeConn())
    assert prov.connected() is True and prov.name() == "db"
    fin = prov.fy_financials("2023-24")     # empty DB -> empty, never an error
    assert fin.fy == "2023-24"
    assert fin.purchase.net_payable is None


def test_seed_and_read_round_trip(raw_conn):
    store.init_schema(raw_conn)
    n = store.seed_from_kp(raw_conn)
    assert n == 5

    fin = store.read_fy(raw_conn, "2023-24")
    assert fin.revenue == Decimal("25238000")
    assert fin.purchase.net_payable == Decimal("16865684.42")
    assert fin.sales.invoices == 1363
    assert fin.flags                           # FY23-24 carries flags
    # The waterfall ties from what the DB stored.
    p = fin.purchase
    assert p.approved - p.commission - p.tds - p.igst_deducted == p.net_payable

    # FY24-25 workbook detail seeds through to the store: the Zoomcar receivable is
    # loaded; the register's unreliable Outstanding column (defect D2) is not.
    fy2425 = store.read_fy(raw_conn, "2024-25")
    assert fy2425.sales.receivable == Decimal("13071497.61")
    assert fy2425.purchase.outstanding is None


def test_upsert_edits_a_year(raw_conn):
    store.init_schema(raw_conn)
    store.seed_from_kp(raw_conn)
    store.upsert_fy(raw_conn, "2024-25", {"sales": {"invoices": 999, "total_sales": "12345.67"}})
    fin = store.read_fy(raw_conn, "2024-25")
    assert fin.sales.invoices == 999
    assert fin.sales.total_sales == Decimal("12345.67")


def test_unknown_year_reads_empty(raw_conn):
    store.init_schema(raw_conn)
    fin = store.read_fy(raw_conn, "1990-91")
    assert fin.purchase.net_payable is None and fin.revenue is None
