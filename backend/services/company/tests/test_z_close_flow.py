"""Period-end close + Tally migration — the Step Functions step handlers
run locally, in the exact sequence the state machines execute them.

The handlers live in infra/company/lambda/handlers; this test imports them
directly (sys.path) so the same code that runs on Lambda is exercised
against the local throwaway Postgres. EventBridge/DynamoDB/S3 are
env-gated off, so every cloud touchpoint is a verified no-op here.

Named test_z_* so the e2e module's absolute-value assertions (exact profit
figures) run on a pristine ledger before this module posts more revenue.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

FY = "2025-26"
GSTIN = "27AAICG1234F1Z5"
PERIOD = "102025"

_REPO = Path(__file__).resolve().parents[4]
_HANDLERS = _REPO / "infra" / "company" / "lambda"


def _load(name: str):
    if "handlers" not in sys.modules:
        import types

        pkg = types.ModuleType("handlers")
        pkg.__path__ = [str(_HANDLERS / "handlers")]
        sys.modules["handlers"] = pkg
    if name != "common" and "handlers.common" not in sys.modules:
        _load("common")  # handlers do `from handlers.common import ...`
    if f"handlers.{name}" in sys.modules:
        return sys.modules[f"handlers.{name}"]
    spec = importlib.util.spec_from_file_location(
        f"handlers.{name}", _HANDLERS / "handlers" / f"{name}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"handlers.{name}"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def close_env(db):
    """Ledger state for the close: company + one posted sales invoice."""
    r = db.post("/admin/company", json={
        "legal_name": "Go4Garage Test Pvt Ltd",
        "incorporation_dt": "2024-06-01",
        "gstin": GSTIN,
    })
    assert r.status_code == 200, r.text
    r = db.post("/ingest/sales", json={
        "source_hash": "close-sale-001",
        "gstin": GSTIN,
        "invoice_no": "G4G/25-26/CLOSE-1",
        "invoice_date": "2025-10-20",
        "party": {"name": "Close Flow Customer", "gstin": "27AACCF1234B1Z6",
                  "state_code": "27"},
        "supply_type": "B2B",
        "place_of_supply": "27",
        "lines": [{"hsn_sac": "998313", "taxable_value": 40000, "gst_rate": 18}],
    })
    assert r.status_code == 200, r.text
    return db


def test_close_sequence_end_to_end(close_env):
    close_steps = _load("close_steps")
    state = {"fy": FY, "gstin": GSTIN, "period": PERIOD, "externals": {}}
    order = ["lock_period", "build_gstr1", "build_gstr3b",
             "build_statements", "run_recon", "publish_facts"]
    results = {}
    for step in order:
        state = close_steps.handler({**state, "step": step})
        results[step] = state["result"]

    assert results["build_gstr1"]["invoices"] >= 1
    assert float(results["build_gstr3b"]["output_tax"]) > 0
    assert results["build_statements"]["lines"] >= 1
    assert results["run_recon"]["control_points_run"] >= 2
    assert results["publish_facts"]["books_balanced"] is True
    assert results["publish_facts"]["equation_holds"] is True
    assert float(results["publish_facts"]["revenue"]) > 0


def test_close_unknown_step_rejected(close_env):
    close_steps = _load("close_steps")
    with pytest.raises(ValueError, match="unknown close step"):
        close_steps.handler({"step": "drop_tables", "fy": FY,
                             "gstin": GSTIN, "period": PERIOD})


def test_tally_migration_steps(close_env, tmp_path, monkeypatch):
    tally = _load("tally_migration")

    staged = {"lines": [
        {"account_code": "5030", "debit": 250000, "credit": 0},
        {"account_code": "2010", "debit": 0, "credit": 250000},
    ]}
    staged_file = tmp_path / "tally_tb.json"
    staged_file.write_text(json.dumps(staged))
    monkeypatch.setattr(
        tally, "_fetch", lambda bucket, key: staged_file.read_bytes()
    )

    base = {"bucket": "test", "key": "tally_tb.json", "gstin": GSTIN,
            "as_of": "2024-04-01", "maker": "migration",
            "checker": "ca-verified"}

    out = tally.handler({**base, "step": "stage"})
    assert out["result"]["balanced"] is True
    assert out["result"]["lines"] == 2

    out = tally.handler({**base, "step": "post_opening"})
    assert out["result"]["status"] == "posted"
    assert out["result"]["fy"] == "2024-25"  # historical FY -> DEFAULT partition
    assert out["result"]["voucher_no"].startswith("OPN/")

    out = tally.handler({**base, "step": "verify"})
    assert out["result"]["fy"] == "2024-25"
    assert out["result"]["balanced"] is True
    assert out["result"]["total_debit"] == "250000.00"


def test_tally_xml_parser():
    tally = _load("tally_migration")
    xml = b"""<?xml version="1.0"?>
    <ENVELOPE><BODY><DATA><TALLYMESSAGE>
      <LEDGER NAME="HDFC Bank"><OPENINGBALANCE>-100000</OPENINGBALANCE></LEDGER>
      <LEDGER NAME="Share Capital"><OPENINGBALANCE>100000</OPENINGBALANCE></LEDGER>
      <LEDGER NAME="No Balance"></LEDGER>
    </TALLYMESSAGE></DATA></BODY></ENVELOPE>"""
    lines = tally.parse_tally_xml(xml)
    assert len(lines) == 2
    bank = next(x for x in lines if x["tally_name"] == "HDFC Bank")
    cap = next(x for x in lines if x["tally_name"] == "Share Capital")
    assert bank["debit"] == 100000.0 and bank["credit"] == 0.0
    assert cap["credit"] == 100000.0 and cap["debit"] == 0.0


def test_calendar_alert_handler(close_env):
    cal = _load("calendar_alert")
    out = cal.handler({})
    assert out["checked"] > 0
    # events.publish is a no-op locally (no EVENT_BUS_NAME) but the alert
    # scan itself must classify due/overdue items.
    assert out["alerts"] >= 0
    assert isinstance(out["items"], list)
