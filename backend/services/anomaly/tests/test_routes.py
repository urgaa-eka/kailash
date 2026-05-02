import random

from fastapi.testclient import TestClient
from app.main import app


def test_detect_finds_outliers():
    random.seed(0)
    pts = [[random.gauss(0, 1)] for _ in range(50)]
    pts += [[10.0], [-9.0]]
    client = TestClient(app)
    r = client.post("/detect", json={"points": pts, "contamination": 0.05})
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["n"] == 52
    assert d["n_anomalies"] >= 1


def test_detect_too_few():
    client = TestClient(app)
    r = client.post("/detect", json={"points": [[0.0], [1.0]]})
    assert r.status_code == 422
