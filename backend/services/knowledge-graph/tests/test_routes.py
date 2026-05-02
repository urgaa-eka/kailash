from fastapi.testclient import TestClient
from app.main import app


def test_upsert_and_neighbours():
    client = TestClient(app)
    assert client.post("/nodes", json={"id": "n1", "labels": ["Vehicle"], "props": {"make": "Tata"}}).status_code == 200
    assert client.post("/nodes", json={"id": "n2", "labels": ["Part"], "props": {"hsn": "8708"}}).status_code == 200
    assert client.post("/nodes", json={"id": "n3", "labels": ["Part"], "props": {"hsn": "8511"}}).status_code == 200

    client.post("/edges", json={"src": "n1", "rel": "HAS_PART", "dst": "n2"})
    client.post("/edges", json={"src": "n2", "rel": "RELATED_TO", "dst": "n3"})

    r = client.get("/neighbours/n1?depth=2")
    assert r.status_code == 200
    d = r.json()["data"]
    ids = {n["id"] for n in d["nodes"]}
    assert {"n2", "n3"}.issubset(ids)


def test_bad_edge():
    client = TestClient(app)
    r = client.post("/edges", json={"src": "ghost", "rel": "X", "dst": "phantom"})
    assert r.status_code == 404
