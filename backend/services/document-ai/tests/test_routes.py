from fastapi.testclient import TestClient
from app.main import app


def test_profiles():
    client = TestClient(app)
    r = client.get("/profiles")
    assert r.status_code == 200
    data = r.json()["data"]
    assert "gst_invoice" in data["profiles"]


def test_validate_ok():
    client = TestClient(app)
    r = client.post("/validate", json={
        "profile": "gst_invoice",
        "fields": {"gstin": "22AAAAA0000A1Z5", "invoice_no": "INV-1", "total_amount": 100},
    })
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["ok"] is True
    assert d["missing_fields"] == []


def test_validate_missing():
    client = TestClient(app)
    r = client.post("/validate", json={"profile": "gst_invoice", "fields": {}})
    assert r.status_code == 200
    assert r.json()["data"]["missing_fields"]


def test_validate_unknown_profile():
    client = TestClient(app)
    r = client.post("/validate", json={"profile": "nope", "fields": {}})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"
