from fastapi.testclient import TestClient
from app.main import app


def test_models():
    r = TestClient(app).get("/models")
    assert r.status_code == 200
    tiers = r.json()["data"]["tiers"]
    assert set(tiers) == {"fast", "balanced", "long"}


def test_route_auto_fast():
    r = TestClient(app).post("/route", json={"prompt": "short"})
    assert r.status_code == 200
    assert r.json()["data"]["tier"] == "fast"


def test_route_auto_long():
    r = TestClient(app).post("/route", json={"prompt": "x" * 9000})
    assert r.status_code == 200
    assert r.json()["data"]["tier"] == "long"


def test_route_explicit_tier():
    r = TestClient(app).post("/route", json={"prompt": "hi", "tier": "balanced"})
    assert r.json()["data"]["tier"] == "balanced"
