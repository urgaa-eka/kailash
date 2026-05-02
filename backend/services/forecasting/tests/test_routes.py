from fastapi.testclient import TestClient
from app.main import app


def test_forecast_basic():
    client = TestClient(app)
    r = client.post("/forecast", json={"series": list(range(1, 31)), "horizon": 5})
    assert r.status_code == 200
    d = r.json()["data"]
    assert len(d["yhat"]) == 5
    assert len(d["yhat_lower"]) == 5
    assert len(d["yhat_upper"]) == 5


def test_forecast_bad_horizon():
    client = TestClient(app)
    r = client.post("/forecast", json={"series": [1, 2, 3], "horizon": 0})
    assert r.status_code == 422


def test_forecast_too_short():
    client = TestClient(app)
    r = client.post("/forecast", json={"series": [1], "horizon": 3})
    assert r.status_code == 422
