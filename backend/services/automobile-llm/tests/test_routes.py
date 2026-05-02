from fastapi.testclient import TestClient
from app.main import app


def test_model_info():
    r = TestClient(app).get("/model")
    assert r.status_code == 200
    d = r.json()["data"]
    assert "default" in d and "active" in d


def test_chat_without_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    r = TestClient(app).post("/chat", json={
        "messages": [{"role": "user", "content": "What is HSN 8711?"}],
    })
    assert r.status_code == 502
    assert r.json()["error"]["code"] == "upstream_error"
