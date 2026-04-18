"""Test unitari per scripts/wikidata_bootstrap.py e wikidata_drift_check.py.

Copertura:
- `parse_wd_time` per date CE / BCE
- `extract_claim_values` su fixture minimali
- `compute_score` su combinazioni label/type/year
- `find_coord_autofix` per swap/sign flip
- `haversine_km` sanity
- Pydantic `EntityResponse` espone `wikidata_qid`
- `GeoEntity` model ha il campo
"""

from __future__ import annotations

import pytest

from scripts.wikidata_bootstrap import (
    compute_score,
    extract_claim_values,
    parse_wd_time,
)
from scripts.wikidata_drift_check import (
    find_coord_autofix,
    haversine_km,
)


def test_parse_wd_time_ce():
    assert parse_wd_time("+1299-01-01T00:00:00Z") == 1299
    assert parse_wd_time("+0476-10-04T00:00:00Z") == 476


def test_parse_wd_time_bce():
    # Wikidata astronomical: -0044 = 44 BCE → parse to -44 per AtlasPI.
    assert parse_wd_time("-0044-03-15T00:00:00Z") == -44


def test_parse_wd_time_invalid():
    assert parse_wd_time(None) is None
    assert parse_wd_time("") is None
    assert parse_wd_time("not-a-date") is None


def test_extract_claim_values_entity():
    ent = {
        "claims": {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "datavalue": {
                            "type": "wikibase-entityid",
                            "value": {"id": "Q48349", "entity-type": "item"},
                        },
                    }
                }
            ]
        }
    }
    assert extract_claim_values(ent, "P31") == ["Q48349"]


def test_extract_claim_values_time():
    ent = {
        "claims": {
            "P571": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "datavalue": {
                            "type": "time",
                            "value": {"time": "-0027-01-16T00:00:00Z"},
                        },
                    }
                }
            ]
        }
    }
    assert extract_claim_values(ent, "P571") == ["-0027-01-16T00:00:00Z"]


def test_extract_claim_values_missing():
    assert extract_claim_values({"claims": {}}, "P571") == []
    assert extract_claim_values({"claims": {"P571": []}}, "P571") == []


def test_compute_score_perfect_match():
    atlas = {
        "id": 2,
        "name_original": "Osmanlı İmparatorluğu",
        "name_original_lang": "tr",
        "entity_type": "empire",
        "year_start": 1299,
        "year_end": 1922,
        "name_variants": [{"name": "Ottoman Empire", "lang": "en"}],
    }
    wd_entity = {
        "labels": {"en": {"value": "Ottoman Empire"}},
        "aliases": {},
        "claims": {
            "P31": [
                {"mainsnak": {"snaktype": "value", "datavalue": {"type": "wikibase-entityid", "value": {"id": "Q48349"}}}},
            ],
            "P571": [
                {"mainsnak": {"snaktype": "value", "datavalue": {"type": "time", "value": {"time": "+1299-01-01T00:00:00Z"}}}},
            ],
            "P576": [
                {"mainsnak": {"snaktype": "value", "datavalue": {"type": "time", "value": {"time": "+1922-11-01T00:00:00Z"}}}},
            ],
        },
    }
    score, reasons, flags = compute_score(atlas, wd_entity)
    assert score >= 0.95
    assert flags["exact_label"] is True
    assert flags["type_exact"] is True
    assert flags["year_match"] is True


def test_compute_score_type_mismatch():
    """Label match but wrong type (e.g. 'Athens' mapped to modern city Q1524)."""
    atlas = {
        "id": 8,
        "name_original": "Ἀθῆναι",
        "name_original_lang": "grc",
        "entity_type": "city-state",
        "year_start": -507,
        "year_end": -323,
        "name_variants": [{"name": "Athens", "lang": "en"}],
    }
    wd_entity = {
        "labels": {"en": {"value": "Athens"}},
        "aliases": {},
        "claims": {
            "P31": [
                # Q1549591 = big city (modern), not in empire/city-state set
                {"mainsnak": {"snaktype": "value", "datavalue": {"type": "wikibase-entityid", "value": {"id": "Q1549591"}}}},
            ],
        },
    }
    score, reasons, flags = compute_score(atlas, wd_entity)
    # label match → 0.4, no type (city-state expects Q515 etc.) → ~0.4
    assert score < 0.7
    assert flags["exact_label"] is True
    assert flags["type_exact"] is False


def test_find_coord_autofix_swap():
    """Lat/lon swap: (lat=12.4, lon=41.9) should flip to (41.9, 12.4) for Rome."""
    # AtlasPI has (12.4964, 41.9028) but Wikidata Rome is (41.9028, 12.4964)
    fix = find_coord_autofix(12.4964, 41.9028, 41.9028, 12.4964)
    assert fix is not None
    assert abs(fix[0] - 41.9028) < 0.1
    assert abs(fix[1] - 12.4964) < 0.1


def test_find_coord_autofix_no_drift():
    """Already close → no fix."""
    fix = find_coord_autofix(41.9, 12.5, 41.9028, 12.4964)
    assert fix is None


def test_find_coord_autofix_unrecoverable():
    """Random far apart → no fix."""
    # Moscow vs Rome — no swap/sign flip makes them close
    fix = find_coord_autofix(55.75, 37.61, 41.9028, 12.4964)
    assert fix is None


def test_haversine_km_zero():
    assert haversine_km(0, 0, 0, 0) == 0


def test_haversine_km_rome_paris():
    # ~1100 km Rome to Paris
    km = haversine_km(41.9028, 12.4964, 48.8566, 2.3522)
    assert 1000 < km < 1200


def test_entity_response_has_wikidata_qid():
    """v6.69: EntityResponse schema exposes wikidata_qid field."""
    from src.api.schemas import EntityResponse

    # Build a minimal example
    response = EntityResponse(
        id=1,
        entity_type="empire",
        year_start=-27,
        year_end=476,
        name_original="Imperium Romanum",
        name_original_lang="la",
        confidence_score=0.9,
        status="confirmed",
        wikidata_qid="Q2277",
    )
    assert response.wikidata_qid == "Q2277"

    # None default
    response2 = EntityResponse(
        id=2,
        entity_type="kingdom",
        year_start=1000,
        name_original="Test",
        name_original_lang="en",
        confidence_score=0.5,
        status="confirmed",
    )
    assert response2.wikidata_qid is None


def test_geo_entity_model_has_wikidata_qid():
    """v6.69: GeoEntity ORM model has wikidata_qid column."""
    from src.db.models import GeoEntity

    # Attribute exists on class
    assert hasattr(GeoEntity, "wikidata_qid")
    # Column metadata
    col = GeoEntity.__table__.columns["wikidata_qid"]
    assert col.nullable is True
    assert str(col.type) == "VARCHAR(20)"


def test_patchable_fields_includes_wikidata_qid():
    """v6.69: apply_data_patch can patch wikidata_qid on entity resource."""
    from scripts.apply_data_patch import PATCHABLE_FIELDS

    assert "wikidata_qid" in PATCHABLE_FIELDS["entity"]
