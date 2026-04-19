"""Test per l'endpoint di health check."""


def test_health_returns_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "ok"
    assert d["version"] == "6.78.0"
    assert d["entity_count"] >= 50


def test_health_reports_database_type(client):
    r = client.get("/health")
    d = r.json()
    assert "database" in d
    assert "connected" in d["database"]


def test_health_has_request_id_header(client):
    r = client.get("/health")
    assert "x-request-id" in r.headers
