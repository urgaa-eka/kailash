def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "company"
    assert body["status"] == "ok"


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "company"


def test_metrics(client):
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text
