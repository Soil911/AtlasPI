"""Test per l'endpoint di health check."""

from src.config import APP_VERSION


def test_health_returns_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "ok"
    # v6.92.1: version assertion contro APP_VERSION dinamico (evita
    # update manuale del test ad ogni bump).
    assert d["version"] == APP_VERSION
    assert d["entity_count"] >= 50


def test_health_reports_database_type(client):
    r = client.get("/health")
    d = r.json()
    assert "database" in d
    assert "connected" in d["database"]


def test_health_has_request_id_header(client):
    r = client.get("/health")
    assert "x-request-id" in r.headers
