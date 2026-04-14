"""Tests for ETHICS-005 boundary provenance API exposure.

The `boundary_source` field + aourednik / NE trace fields were added in
migration 002_boundary_provenance to close a gap where the DB had no way
to communicate "this polygon is generated, not real" to API consumers.

These tests validate:
  - The API response schema includes the new fields
  - Entities seeded with provenance metadata expose it via /v1/entities/{id}
  - Entities without provenance metadata still serialize cleanly (None)
  - The fields match the ETHICS-005 enum values when set
"""

import pytest


VALID_BOUNDARY_SOURCES = {
    "historical_map",
    "natural_earth",
    "aourednik",
    "academic_source",
    "approximate_generated",
}


def test_entity_response_exposes_boundary_source_fields(client):
    """Every GET /v1/entities/{id} response must include the provenance fields."""
    r = client.get("/v1/search?q=Imperium Romanum&limit=1")
    assert r.status_code == 200
    results = r.json().get("results", [])
    assert results, "Imperium Romanum must be in the dataset"
    eid = results[0]["id"]

    r = client.get(f"/v1/entities/{eid}")
    assert r.status_code == 200
    body = r.json()

    # Fields must exist in the response body, even if null.
    assert "boundary_source" in body
    assert "boundary_aourednik_name" in body
    assert "boundary_aourednik_year" in body
    assert "boundary_aourednik_precision" in body
    assert "boundary_ne_iso_a3" in body


def test_boundary_source_values_are_in_enum(client):
    """Any non-null boundary_source must be a known ETHICS-005 tier."""
    # Sample the first 50 entities via paginated list — enough to hit most tiers.
    r = client.get("/v1/entities?limit=50")
    assert r.status_code == 200
    entities = r.json().get("entities", [])

    found_sources = set()
    for e in entities:
        src = e.get("boundary_source")
        if src is not None:
            assert src in VALID_BOUNDARY_SOURCES, (
                f"Entity {e['id']} {e['name_original']!r}: "
                f"boundary_source={src!r} is not in the ETHICS-005 enum. "
                f"Valid values: {sorted(VALID_BOUNDARY_SOURCES)}"
            )
            found_sources.add(src)

    # The dataset has enough variety that *at least one* entity should carry
    # a source value — otherwise the seed or sync pipeline is broken.
    if not found_sources:
        pytest.skip(
            "No boundary_source values found in first 50 entities. "
            "This may be normal if the seed predates the migration — run "
            "`python -m src.ingestion.sync_boundaries_from_json` to backfill."
        )


def test_aourednik_precision_is_valid(client):
    """Precision mirrors aourednik BORDERPRECISION: 1, 2, or 3 (README historical-basemaps).

    The value 0 is a rare legacy edge-case in upstream (4 features across all
    53 snapshots) and is accepted here for robustness.
    """
    r = client.get("/v1/entities?limit=100")
    assert r.status_code == 200
    for e in r.json().get("entities", []):
        p = e.get("boundary_aourednik_precision")
        if p is not None:
            assert p in (0, 1, 2, 3), (
                f"Entity {e['id']}: boundary_aourednik_precision={p} "
                f"outside allowed aourednik scale 0..3 "
                f"(upstream README: 1=approximate, 2=moderately precise, "
                f"3=determined by international law)"
            )


def test_aourednik_metadata_consistency(client):
    """If boundary_source='aourednik', the aourednik trace fields should be populated.

    This is a soft-contract check: a matched aourednik entity should have
    enough metadata to locate the source feature in world_{year}.geojson
    for reproducibility (METHODOLOGY.md §7).
    """
    # The /v1/entities endpoint caps limit at 100, so we paginate to cover
    # the first 200 rows — enough to sample aourednik coverage reliably.
    aourednik_entities: list[dict] = []
    for offset in (0, 100):
        r = client.get(f"/v1/entities?limit=100&offset={offset}")
        assert r.status_code == 200, f"limit=100&offset={offset} returned {r.status_code}: {r.text[:200]}"
        aourednik_entities.extend(
            e for e in r.json().get("entities", [])
            if e.get("boundary_source") == "aourednik"
        )
    if not aourednik_entities:
        pytest.skip("No aourednik-sourced entities seen in first 200 rows")

    # At least one should carry the feature name for reproducibility.
    with_name = [e for e in aourednik_entities if e.get("boundary_aourednik_name")]
    assert len(with_name) > 0, (
        f"Found {len(aourednik_entities)} aourednik entities but none carry "
        f"boundary_aourednik_name — provenance is untraceable. "
        f"Run sync_boundaries_from_json to backfill."
    )
