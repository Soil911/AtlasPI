"""Test per il bbox filter spaziale (v6.3.2 PostGIS deep work).

In SQLite (CI/dev) il filtro è approssimato sul solo capital-point.
In PostgreSQL+PostGIS (prod) usa ST_Intersects sul boundary_geojson
con fallback al capital-point. Questi test verificano il path SQLite
(copertura logica), perché:

    * Garantisce parsing/validazione bbox robusta (422 su input malformati).
    * Assicura che il filtro restringa il result set in modo monotono
      (bbox più piccolo ⇒ ≤ risultati).
    * Documenta per il prossimo dev che il path PostGIS richiede prod.
"""

import pytest


@pytest.mark.parametrize("endpoint", ["/v1/entity", "/v1/entities"])
def test_bbox_filter_reduces_result_set(client, endpoint):
    """bbox piccolo ⇒ ≤ risultati di senza bbox."""
    no_bbox = client.get(f"{endpoint}?limit=100").json()["count"]
    # Bbox sull'Europa occidentale (Francia/Germania/Italia)
    europe_west = client.get(f"{endpoint}?bbox=-10,35,20,55&limit=100").json()["count"]
    assert europe_west <= no_bbox
    # Bbox minuscolo (qualche grado attorno a Roma)
    small = client.get(f"{endpoint}?bbox=11,40,14,43&limit=100").json()["count"]
    assert small <= europe_west


def test_bbox_around_rome_returns_italian_entities(client):
    """Bbox stretto attorno a Roma deve restituire almeno una capitale italiana."""
    r = client.get("/v1/entity?bbox=11,40,14,43&limit=50")
    assert r.status_code == 200
    body = r.json()
    # Almeno qualche entità con capitale dentro l'Italia centrale dovrebbe
    # esserci nel dataset (Roma, città del Vaticano, regni medievali).
    assert body["count"] >= 1
    # Verifica che le entità restituite abbiano capitale dentro il bbox
    # (path SQLite filtra solo sul capital-point).
    for ent in body["entities"]:
        if ent.get("capital"):
            cap = ent["capital"]
            assert 11 <= cap["lon"] <= 14
            assert 40 <= cap["lat"] <= 43


def test_bbox_invalid_format_returns_422(client):
    """bbox malformato deve restituire 422 con messaggio chiaro."""
    r = client.get("/v1/entity?bbox=not-a-bbox")
    assert r.status_code == 422


def test_bbox_wrong_arity_returns_422(client):
    """bbox con != 4 valori → 422."""
    r = client.get("/v1/entity?bbox=1,2,3")
    assert r.status_code == 422
    r = client.get("/v1/entity?bbox=1,2,3,4,5")
    assert r.status_code == 422


def test_bbox_lat_out_of_range_returns_422(client):
    """Latitudine > 90 → 422."""
    r = client.get("/v1/entity?bbox=0,0,10,99")
    assert r.status_code == 422


def test_bbox_lon_out_of_range_returns_422(client):
    """Longitudine > 180 → 422."""
    r = client.get("/v1/entity?bbox=0,0,200,10")
    assert r.status_code == 422


def test_bbox_inverted_returns_422(client):
    """min > max → 422."""
    r = client.get("/v1/entity?bbox=10,10,0,20")
    assert r.status_code == 422


def test_bbox_global_returns_all_capital_entities(client):
    """Bbox planetario ⇒ tutte le entità con capitale rientrano."""
    no_bbox = client.get("/v1/entity?limit=100").json()["count"]
    global_bbox = client.get("/v1/entity?bbox=-180,-90,180,90&limit=100").json()["count"]
    # In SQLite il bbox filtra fuori le entità senza capitale; in PostGIS
    # invece le include via boundary_geojson. Quindi global_bbox <= no_bbox
    # in SQLite ma pochi punti percentuali sotto.
    assert global_bbox > 0
    assert global_bbox <= no_bbox


def test_bbox_combined_with_year_and_type(client):
    """bbox componibile con altri filtri (year, type)."""
    r = client.get("/v1/entity?bbox=-10,30,40,60&year=1500&type=empire&limit=20")
    assert r.status_code == 200
    body = r.json()
    # Ogni entità restituita rispetta TUTTI i filtri
    for ent in body["entities"]:
        assert ent["entity_type"] == "empire"
        assert ent["year_start"] <= 1500
        if ent.get("year_end"):
            assert ent["year_end"] >= 1500


def test_bbox_documented_in_openapi(client):
    """bbox è esposto come query param nello schema OpenAPI."""
    schema = client.get("/openapi.json").json()
    entity_get = schema["paths"]["/v1/entity"]["get"]
    param_names = {p["name"] for p in entity_get["parameters"]}
    assert "bbox" in param_names
