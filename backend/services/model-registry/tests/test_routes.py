import os
import tempfile

from fastapi.testclient import TestClient


def _client(tmp_path):
    # Isolate the sqlite file per test run.
    os.environ["MODEL_REGISTRY_DB"] = str(tmp_path / "reg.db")
    from importlib import reload
    import app.service as svc  # noqa: WPS433
    reload(svc)
    import app.main as m
    reload(m)
    return TestClient(m.app)


def test_register_and_fetch(tmp_path):
    client = _client(tmp_path)
    r = client.post("/models", json={
        "name": "kailash-ocr", "version": "1.0.0", "stage": "dev",
        "metrics": {"f1": 0.91}, "tags": {"owner": "platform"},
    })
    assert r.status_code == 200, r.text
    assert r.json()["data"]["stage"] == "dev"

    r = client.get("/models/kailash-ocr/1.0.0")
    assert r.status_code == 200
    assert r.json()["data"]["metrics"]["f1"] == 0.91


def test_promote_and_list(tmp_path):
    client = _client(tmp_path)
    client.post("/models", json={"name": "m", "version": "1"})
    r = client.post("/models/m/1/promote", json={"stage": "prod"})
    assert r.status_code == 200
    assert r.json()["data"]["stage"] == "prod"

    r = client.get("/models")
    assert r.status_code == 200
    assert len(r.json()["data"]["models"]) >= 1


def test_not_found(tmp_path):
    client = _client(tmp_path)
    r = client.get("/models/nope/1")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"
