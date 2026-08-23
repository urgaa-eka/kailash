"""Tests for the Go4Garage JSON API (frontend / Zoho-mapping seam).

Asserts the payloads are JSON-serialisable (no Decimal leaks), carry the store's
key shape, and that the confirmed Net Payable waterfall still ties when rebuilt
from the emitted strings.
"""
from __future__ import annotations

import json
from decimal import Decimal

from app.go4garage import api, defects, model
from app.go4garage.provider import KnowledgePackProvider, NullProvider


def test_overview_payload_shape():
    d = api.overview_payload(KnowledgePackProvider())
    assert d["entity"]["cin"] == model.ENTITY["cin"]
    assert len(d["financial_years"]) == len(model.FINANCIAL_YEARS)
    assert len(d["departments"]) == len(model.DEPARTMENTS)
    assert len(d["defects"]) == len(defects.DEFECTS)
    assert len(d["decisions"]) == len(defects.OPEN_DECISIONS)
    assert d["provider"]["name"] == "knowledge-pack" and d["provider"]["connected"] is True
    assert d["rates"] == {"commission": "0.15", "tds": "0.02"}
    assert len(d["trend"]) == len(model.FINANCIAL_YEARS)
    fy2324 = next(t for t in d["trend"] if t["fy"] == "2023-24")
    assert fy2324["revenue"] == "25238000"          # exact string, not float
    json.dumps(d)                                    # fully serialisable


def test_fy_payload_store_shape_and_ties():
    fin = KnowledgePackProvider().fy_financials("2023-24")
    p = api.fy_payload(fin)
    assert p["fy"] == "2023-24"
    assert p["audit_status"] == "AUDITED_QUALIFIED"
    assert p["sales"]["invoices"] == 1363
    assert p["purchase"]["net_payable"] == "16865684.42"
    pu = p["purchase"]
    assert (Decimal(pu["approved"]) - Decimal(pu["commission"])
            - Decimal(pu["tds"]) - Decimal(pu["igst_deducted"])) == Decimal(pu["net_payable"])
    json.dumps(p)                                    # no Decimal leaks


def test_null_provider_is_all_awaiting():
    p = api.fy_payload(NullProvider().fy_financials("2023-24"))
    assert p["revenue"] is None
    assert p["purchase"]["net_payable"] is None
    assert p["sales"]["invoices"] is None
    assert p["gst"] == [] and p["bank"] == []


def test_export_csv_is_flat_store_shape():
    text = api.export_csv(KnowledgePackProvider())
    lines = text.strip().splitlines()
    header = lines[0].split(",")
    assert header == api.EXPORT_FIELDS
    assert len(lines) == 1 + len(model.FINANCIAL_YEARS)   # header + one row per FY
    # FY2023-24 row carries the confirmed net payable as an exact string.
    row = next(ln for ln in lines[1:] if ln.startswith("2023-24,"))
    assert "16865684.42" in row


def test_routes_serve_json(client):
    r = client.get("/go4garage/api/overview")
    assert r.status_code == 200
    assert r.json()["data"]["entity"]["pan"] == model.ENTITY["pan"]

    r2 = client.get("/go4garage/api/fy/2023-24")
    assert r2.status_code == 200
    assert r2.json()["data"]["sales"]["invoices"] == 1363

    r3 = client.get("/go4garage/api/fy/1990-91")
    assert r3.status_code >= 400                      # unknown FY rejected

    r4 = client.get("/go4garage/api/export.csv")
    assert r4.status_code == 200
    assert "text/csv" in r4.headers["content-type"]
    assert "attachment" in r4.headers.get("content-disposition", "")
    assert r4.text.splitlines()[0].startswith("fy,audit_status,posture")
