from fastapi.testclient import TestClient
from app.main import app


def test_upsert_search_roundtrip():
    client = TestClient(app)
    docs = [
        {"id": "a", "text": "Tata Nexon EV charger specifications", "metadata": {"src": "manual"}},
        {"id": "b", "text": "GST rate for electric vehicles", "metadata": {"src": "gst"}},
        {"id": "c", "text": "Driving license renewal RTO Delhi", "metadata": {"src": "rto"}},
    ]
    r = client.post("/upsert", json={"docs": docs})
    assert r.status_code == 200
    assert r.json()["data"]["upserted"] == 3

    r = client.post("/search", json={"query": "GST rate for electric vehicles", "k": 2})
    assert r.status_code == 200
    hits = r.json()["data"]["hits"]
    assert len(hits) == 2
    # Hash embedding is deterministic, so identical query → doc b ranks #1.
    assert hits[0]["id"] == "b"


def test_stats():
    client = TestClient(app)
    r = client.get("/stats")
    assert r.status_code == 200
    assert r.json()["data"]["documents"] >= 0
