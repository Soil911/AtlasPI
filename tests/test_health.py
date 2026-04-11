"""Test per l'endpoint di health check."""


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
    assert data["entity_count"] >= 10


def test_health_has_entity_count(client):
    response = client.get("/health")
    data = response.json()
    assert isinstance(data["entity_count"], int)
    assert data["entity_count"] > 0
