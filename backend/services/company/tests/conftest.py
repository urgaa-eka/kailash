"""Test harness — isolates every run in a dedicated Postgres database.

The base DSN comes from COMPANY_DB_URL, which has no default — no
credential lives in this file. A throwaway database ``kailash_company_test`` is
dropped + recreated per session; COMPANY_DB_URL is re-pointed at it BEFORE
the app is imported. DB-dependent tests skip cleanly when Postgres is
unreachable (health tests still run).
"""
from __future__ import annotations

import os

import pytest

TEST_DB_NAME = "kailash_company_test"
_BASE_URL = os.environ.get("COMPANY_DB_URL")

# Used only when COMPANY_DB_URL is unset: app.settings requires the variable,
# so the app cannot import without one, but every DB-backed test skips in that
# case. This DSN carries no password and is never expected to authenticate.
_NO_DB_URL = f"postgresql://kailash@127.0.0.1:5432/{TEST_DB_NAME}"


def _swap_dbname(url: str, dbname: str) -> str:
    head, _, tail = url.rpartition("/")
    tail = tail.split("?")[0]
    return f"{head}/{dbname}"


DB_AVAILABLE = False
_TEST_URL = _swap_dbname(_BASE_URL, TEST_DB_NAME) if _BASE_URL else _NO_DB_URL

try:
    if not _BASE_URL:
        raise RuntimeError("COMPANY_DB_URL is not set")

    import psycopg

    with psycopg.connect(_BASE_URL, autocommit=True, connect_timeout=3) as admin:
        admin.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME} WITH (FORCE)")
        admin.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    DB_AVAILABLE = True
except Exception:  # pragma: no cover - environment-dependent
    DB_AVAILABLE = False

# Point the service at the throwaway DB before the app/settings import.
os.environ["COMPANY_DB_URL"] = _TEST_URL


@pytest.fixture(scope="session")
def client():
    from app.main import app
    from fastapi.testclient import TestClient

    return TestClient(app)


@pytest.fixture(scope="session")
def db(client):
    """Initialized schema + seeded masters; skips if Postgres is down."""
    if not DB_AVAILABLE:
        pytest.skip("PostgreSQL unavailable — set COMPANY_DB_URL")
    r = client.post("/admin/init")
    assert r.status_code == 200, r.text
    return client


@pytest.fixture(scope="session")
def raw_conn(db):
    """Direct psycopg connection to the test DB for adversarial SQL."""
    import psycopg
    from psycopg.rows import dict_row

    conn = psycopg.connect(
        _TEST_URL, row_factory=dict_row,
        options="-c search_path=company,public", autocommit=True,
    )
    yield conn
    conn.close()
