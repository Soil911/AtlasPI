"""v6.34: tests per `/v1/where-was` — reverse-geocoding temporale.

Testa:
- Point-in-polygon base su entita' con boundary
- include_history=true ritorna timeline cronologica
- Punti in oceano / zone senza copertura
- Validazione coordinate (lat/lon range)
- Validazione year range
- Errore 400 se ne year ne include_history
- Backend header X-WhereWas-Backend
- ETHICS-003: entita' disputed surfacciate
"""

import json

import pytest
from sqlalchemy import text

from src.db.models import GeoEntity


# ─── Helpers ─────────────────────────────────────────────────────────

def _seed_test_entity_with_boundary(
    db,
    name: str,
    year_start: int,
    year_end: int | None,
    boundary_coords: list[list[list[float]]],
    status: str = "confirmed",
) -> GeoEntity:
    """Inserisce un'entita' con boundary rettangolare in SQLite di test."""
    boundary_geojson = json.dumps({
        "type": "Polygon",
        "coordinates": boundary_coords,
    })
    entity = GeoEntity(
        name_original=name,
        name_original_lang="en",
        entity_type="kingdom",
        year_start=year_start,
        year_end=year_end,
        boundary_geojson=boundary_geojson,
        boundary_source="test_fixture",
        confidence_score=0.8,
        status=status,
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


# ─── Tests base ──────────────────────────────────────────────────────

def test_where_was_requires_year_or_history(client):
    """Senza year e senza include_history → 400 esplicito."""
    r = client.get("/v1/where-was?lat=41.9&lon=12.5")
    assert r.status_code == 400
    assert "year" in r.json()["detail"].lower()


def test_where_was_invalid_lat(client):
    """lat > 90 → 422 da Pydantic validation."""
    r = client.get("/v1/where-was?lat=100&lon=12.5&year=1000")
    assert r.status_code == 422


def test_where_was_invalid_lon(client):
    """lon < -180 → 422."""
    r = client.get("/v1/where-was?lat=41.9&lon=-300&year=1000")
    assert r.status_code == 422


def test_where_was_year_out_of_range(client):
    """year < -5000 → 422."""
    r = client.get("/v1/where-was?lat=41.9&lon=12.5&year=-10000")
    assert r.status_code == 422


def test_where_was_year_too_future(client):
    """year > 2100 → 422."""
    r = client.get("/v1/where-was?lat=41.9&lon=12.5&year=3000")
    assert r.status_code == 422


# ─── Test con entita' reali dal seed ─────────────────────────────────

def test_where_was_rome_in_100ce_returns_entities(client):
    """Coordinate di Roma (41.9, 12.5) nel 100 CE → deve trovare almeno
    l'Impero Romano (se presente con boundary nel seed).

    Non facciamo assert su un nome specifico perche' il seed puo' variare,
    ma verifichiamo struttura + che il campo backend sia corretto.
    """
    r = client.get("/v1/where-was?lat=41.9&lon=12.5&year=100")
    assert r.status_code == 200
    data = r.json()
    assert "query" in data
    assert data["query"]["lat"] == 41.9
    assert data["query"]["lon"] == 12.5
    assert data["query"]["year"] == 100
    assert data["query"]["include_history"] is False
    assert "count" in data
    assert "entities" in data
    assert isinstance(data["entities"], list)
    # Header backend
    assert r.headers.get("X-WhereWas-Backend") in ("shapely", "postgis")


def test_where_was_response_entity_shape(client):
    """Se c'e' almeno un'entita' nella response, ha i campi richiesti."""
    r = client.get("/v1/where-was?lat=41.9&lon=12.5&year=100")
    assert r.status_code == 200
    data = r.json()
    for e in data["entities"]:
        assert "id" in e
        assert "name_original" in e
        assert "entity_type" in e
        assert "year_start" in e
        assert "year_end" in e
        assert "confidence_score" in e
        assert "status" in e


def test_where_was_ocean_point_empty(client):
    """Punto a metà Pacifico → nessuna entità dovrebbe contenerlo."""
    r = client.get("/v1/where-was?lat=0&lon=-150&year=1500")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 0
    assert data["entities"] == []


# ─── include_history mode ────────────────────────────────────────────

def test_where_was_include_history_structure(client):
    """include_history=true ritorna timeline, non entities."""
    r = client.get("/v1/where-was?lat=41.9&lon=12.5&include_history=true")
    assert r.status_code == 200
    data = r.json()
    assert data["query"]["include_history"] is True
    assert "timeline" in data
    assert "total_entities" in data
    assert "point_covered_years" in data
    assert "timeline_span" in data
    assert isinstance(data["timeline"], list)


def test_where_was_include_history_sorted_chronologically(client):
    """Timeline in ordine cronologico crescente."""
    r = client.get("/v1/where-was?lat=41.9&lon=12.5&include_history=true")
    assert r.status_code == 200
    timeline = r.json()["timeline"]
    if len(timeline) >= 2:
        year_starts = [e["year_start"] for e in timeline]
        assert year_starts == sorted(year_starts), "Timeline must be chronological"


def test_where_was_include_history_with_year_filter(client):
    """include_history=true + year=X → is_current marcato per entita' attive in X."""
    r = client.get("/v1/where-was?lat=41.9&lon=12.5&year=100&include_history=true")
    assert r.status_code == 200
    data = r.json()
    assert data["query"]["year"] == 100
    # Se ci sono entita' nella timeline, quelle con is_current=True sono
    # effettivamente attive nell'anno 100
    for e in data["timeline"]:
        if e["is_current"]:
            assert e["year_start"] <= 100
            assert e["year_end"] is None or e["year_end"] >= 100


# ─── Test isolati con entita' mock-up ────────────────────────────────

def test_where_was_point_inside_synthetic_boundary(client, db):
    """Crea un boundary rettangolare sintetico e verifica che un punto
    al suo centro sia matchato."""
    # Rettangolo attorno a (10,10)-(20,20) — lat/lon
    # GeoJSON coords: [lon, lat]
    coords = [[[10.0, 10.0], [20.0, 10.0], [20.0, 20.0], [10.0, 20.0], [10.0, 10.0]]]
    entity = _seed_test_entity_with_boundary(
        db,
        name="TestRectKingdom",
        year_start=500,
        year_end=600,
        boundary_coords=coords,
    )

    # Punto interno (15, 15)
    r = client.get("/v1/where-was?lat=15&lon=15&year=550")
    assert r.status_code == 200
    data = r.json()
    names = [e["name_original"] for e in data["entities"]]
    assert "TestRectKingdom" in names

    # Punto esterno (5, 5)
    r = client.get("/v1/where-was?lat=5&lon=5&year=550")
    assert r.status_code == 200
    names = [e["name_original"] for e in r.json()["entities"]]
    assert "TestRectKingdom" not in names

    # Cleanup
    db.delete(entity)
    db.commit()


def test_where_was_year_filter_excludes_out_of_range(client, db):
    """Entita' con year_start=500, year_end=600: un query con year=400
    non deve trovarla."""
    coords = [[[30.0, 30.0], [40.0, 30.0], [40.0, 40.0], [30.0, 40.0], [30.0, 30.0]]]
    entity = _seed_test_entity_with_boundary(
        db,
        name="TestRangeKingdom",
        year_start=500,
        year_end=600,
        boundary_coords=coords,
    )

    # Year troppo presto
    r = client.get("/v1/where-was?lat=35&lon=35&year=400")
    assert r.status_code == 200
    names = [e["name_original"] for e in r.json()["entities"]]
    assert "TestRangeKingdom" not in names

    # Year corretto
    r = client.get("/v1/where-was?lat=35&lon=35&year=550")
    assert r.status_code == 200
    names = [e["name_original"] for e in r.json()["entities"]]
    assert "TestRangeKingdom" in names

    # Year troppo tardi
    r = client.get("/v1/where-was?lat=35&lon=35&year=700")
    assert r.status_code == 200
    names = [e["name_original"] for e in r.json()["entities"]]
    assert "TestRangeKingdom" not in names

    db.delete(entity)
    db.commit()


def test_where_was_open_ended_entity(client, db):
    """Entita' con year_end=NULL (tuttora esistente): deve essere trovata
    per qualsiasi year >= year_start."""
    coords = [[[50.0, 50.0], [60.0, 50.0], [60.0, 60.0], [50.0, 60.0], [50.0, 50.0]]]
    entity = _seed_test_entity_with_boundary(
        db,
        name="TestOpenKingdom",
        year_start=1900,
        year_end=None,
        boundary_coords=coords,
    )

    for year in [1950, 2000, 2020]:
        r = client.get(f"/v1/where-was?lat=55&lon=55&year={year}")
        assert r.status_code == 200, f"Failed for year {year}"
        names = [e["name_original"] for e in r.json()["entities"]]
        assert "TestOpenKingdom" in names, f"Open-ended entity not found for year {year}"

    db.delete(entity)
    db.commit()


# ─── ETHICS-003 ──────────────────────────────────────────────────────

def test_where_was_disputed_entity_surfaced(client, db):
    """ETHICS-003: entita' con status='disputed' DEVONO apparire."""
    coords = [[[70.0, 70.0], [80.0, 70.0], [80.0, 80.0], [70.0, 80.0], [70.0, 70.0]]]
    entity = _seed_test_entity_with_boundary(
        db,
        name="TestDisputedRegion",
        year_start=1900,
        year_end=None,
        boundary_coords=coords,
        status="disputed",
    )

    r = client.get("/v1/where-was?lat=75&lon=75&year=2020")
    assert r.status_code == 200
    found = [e for e in r.json()["entities"] if e["name_original"] == "TestDisputedRegion"]
    assert len(found) == 1
    assert found[0]["status"] == "disputed"

    db.delete(entity)
    db.commit()


# ─── Backend dispatch ────────────────────────────────────────────────

def test_where_was_backend_header_present(client):
    """Header X-WhereWas-Backend presente e con valore valido."""
    r = client.get("/v1/where-was?lat=41.9&lon=12.5&year=100")
    assert r.status_code == 200
    backend = r.headers.get("X-WhereWas-Backend")
    assert backend in ("shapely", "postgis")


def test_where_was_caching_headers(client):
    """Cache-Control header set a public max-age."""
    r = client.get("/v1/where-was?lat=41.9&lon=12.5&year=100")
    assert r.status_code == 200
    assert "max-age" in r.headers.get("Cache-Control", "")
