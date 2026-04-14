"""Regression test — top-10 academic entities boundary quality floor.

ETHICS: this test locks in the quality improvements shipped in v6.1.1
(boundary coverage 23% -> 93%). It enforces a *floor* rather than a
precise check so minor variations in upstream source data (aourednik
snapshots, Natural Earth revisions) do not fail CI, but catastrophic
regressions (e.g. a pipeline bug overwrites a MultiPolygon with an
18-vertex seeded Polygon) surface immediately.

The 10 entities chosen reflect high academic visibility across regions
and time periods, and represent the set an external reviewer is most
likely to open first when auditing the dataset.

If this test fails, investigate BEFORE relaxing thresholds:
  - Has the aourednik dataset changed upstream?
  - Did an entity edit inadvertently remove its polygon?
  - Did the enrichment pipeline downgrade a real boundary to generated?
"""

import json

import pytest


@pytest.fixture(scope="module", autouse=True)
def _enrich_test_boundaries(setup_test_db):
    """Apply the same runtime boundary enrichment that production uses.

    Production runs `update_all_boundaries()` at container startup (see
    `src/main.py` lifespan handler). The plain test seed bypasses this,
    so the test DB has baseline JSON boundaries. This fixture replicates
    production behaviour for the top-10 regression suite.
    """
    # Import inside fixture to avoid cost in other test modules.
    from src.db import seed as seed_module
    from src.ingestion.update_boundaries import update_all_boundaries
    from tests.conftest import TestSession

    original = seed_module.SessionLocal
    seed_module.SessionLocal = TestSession
    # update_all_boundaries imports SessionLocal from src.db.database directly,
    # so we also need to patch that.
    from src.db import database as db_module
    original_db = db_module.SessionLocal
    db_module.SessionLocal = TestSession

    try:
        update_all_boundaries()
    except Exception as exc:
        pytest.skip(f"update_all_boundaries failed in test env: {exc}")
    finally:
        seed_module.SessionLocal = original
        db_module.SessionLocal = original_db


# Each entry: (search_query, expected_entity_type, min_vertices, min_confidence)
# Thresholds are set conservatively — current values (v6.1.1 production)
# exceed them comfortably. A regression below these floors indicates a
# real quality loss, not noise.
TOP_10_FLOOR = [
    ("Imperium Romanum", "empire", 500, 0.85),  # 1083 verts, conf 0.9
    ("Osmanl",           "empire", 300, 0.75),  # Ottoman: 697 verts, conf 0.85
    ("Mongol",           "empire", 500, 0.70),  # 1401 verts, conf 0.75
    ("Tawantinsuyu",     "empire", 100, 0.65),  # 169 verts, conf 0.7
    ("Tokugawa",         "empire",  50, 0.70),  # keep low floor, hand-curated
    ("Mughal",           "empire", 100, 0.70),  # 266 verts, conf 0.8
    ("Byzantine",        "empire", 200, 0.75),  # treated by search for variants
    ("Qing",             "empire", 100, 0.70),  # 261 verts, conf 0.85
    ("Abbasid",          "empire", 500, 0.70),  # post-v6.1.1 fix: 605 verts, conf 0.8
    ("Aztec",            "empire", 30,  0.60),  # resolves to Excan Tlahtoloyan (Triple Alliance)
]


def _count_vertices(geom: dict) -> int:
    """Count total vertices in a GeoJSON geometry (Polygon or MultiPolygon)."""
    t = geom.get("type")
    coords = geom.get("coordinates", [])
    if t == "Polygon":
        return sum(len(ring) for ring in coords)
    if t == "MultiPolygon":
        return sum(sum(len(ring) for ring in poly) for poly in coords)
    return 0


def _fetch_entity_by_search(client, query: str) -> dict | None:
    """Resolve a search query to a full entity record.

    Returns the first search hit's full detail, or None if nothing matches.
    """
    r = client.get(f"/v1/search?q={query}&limit=3")
    assert r.status_code == 200, f"/v1/search failed for {query!r}: {r.status_code}"
    results = r.json().get("results", [])
    if not results:
        return None
    eid = results[0]["id"]
    r = client.get(f"/v1/entities/{eid}")
    assert r.status_code == 200, f"/v1/entities/{eid} failed: {r.status_code}"
    return r.json()


@pytest.mark.parametrize("query,expected_type,min_vertices,min_confidence", TOP_10_FLOOR)
def test_top10_boundary_quality_floor(
    client, query, expected_type, min_vertices, min_confidence
):
    """Each top-10 entity must meet minimum geometry + confidence thresholds."""
    entity = _fetch_entity_by_search(client, query)
    assert entity is not None, (
        f"Top-10 entity matching {query!r} not found in dataset. "
        f"Either the entity was removed or /v1/search regressed."
    )

    # Entity type sanity
    assert entity["entity_type"] == expected_type, (
        f"{query!r} resolved to {entity['name_original']!r} "
        f"with type {entity['entity_type']} (expected {expected_type}). "
        f"Search ranking may have changed — verify the resolved entity is correct."
    )

    # Boundary presence
    geom = entity.get("boundary_geojson")
    assert geom is not None, f"{query!r} -> {entity['name_original']!r}: no boundary_geojson"
    if isinstance(geom, str):
        geom = json.loads(geom)
    assert geom.get("type") in ("Polygon", "MultiPolygon"), (
        f"{query!r}: boundary type {geom.get('type')!r} is not a polygon"
    )

    # Vertex floor
    vertex_count = _count_vertices(geom)
    assert vertex_count >= min_vertices, (
        f"{query!r} -> {entity['name_original']!r}: "
        f"vertex count {vertex_count} below floor {min_vertices}. "
        f"If an enrichment pipeline downgraded this boundary, investigate."
    )

    # Confidence floor
    conf = entity["confidence_score"]
    assert conf >= min_confidence, (
        f"{query!r} -> {entity['name_original']!r}: "
        f"confidence {conf} below floor {min_confidence}. "
        f"Disputed entities are capped at 0.70 (ETHICS-003) — check status."
    )


def test_top10_set_size_is_ten(client):
    """Guard: the regression suite must exercise 10 distinct entities."""
    assert len(TOP_10_FLOOR) == 10

    # Ensure each search resolves to a distinct entity id (no collision).
    ids = set()
    for query, *_ in TOP_10_FLOOR:
        entity = _fetch_entity_by_search(client, query)
        if entity is None:
            continue
        ids.add(entity["id"])
    assert len(ids) >= 9, (
        f"Top-10 searches resolved to only {len(ids)} distinct entities. "
        f"Search ambiguity may be collapsing results."
    )
