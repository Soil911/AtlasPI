"""Test per gli endpoint delle entit\u00e0."""


def test_list_entities(client):
    response = client.get("/v1/entities")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 10
    assert len(data["entities"]) == data["count"]


def test_get_entity_by_id(client):
    response = client.get("/v1/entities/1")
    assert response.status_code == 200
    entity = response.json()
    assert entity["id"] == 1
    assert entity["name_original"] is not None


def test_get_entity_not_found(client):
    response = client.get("/v1/entities/9999")
    assert response.status_code == 404


def test_query_by_name(client):
    response = client.get("/v1/entity?name=Roma")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1


def test_query_by_year_filters_correctly(client):
    """Le entit\u00e0 con year_start > year cercato non devono apparire."""
    response = client.get("/v1/entity?year=100")
    data = response.json()
    for e in data["entities"]:
        assert e["year_start"] <= 100


def test_query_by_status(client):
    response = client.get("/v1/entity?status=disputed")
    data = response.json()
    for e in data["entities"]:
        assert e["status"] == "disputed"


def test_entity_has_required_fields(client):
    """Verifica che ogni entit\u00e0 abbia i campi richiesti da ADR-002."""
    response = client.get("/v1/entities")
    data = response.json()
    for e in data["entities"]:
        assert "name_original" in e
        assert "name_original_lang" in e
        assert "confidence_score" in e
        assert "status" in e
        assert "name_variants" in e
        assert "sources" in e
        assert "territory_changes" in e
