"""Tests for ETHICS-006 geographic guard in boundary_match.

Context: the v6.1.1 audit found 133/211 NE matches had the entity's
capital OUTSIDE the assigned polygon (Garenganze -> Russia, Primer
Imperio Mexicano -> Belgium, CSA -> Italy, ...). The fix adds a
capital-in-polygon check to every fuzzy match and to exact-name
matches. These tests lock that behavior in.
"""

from __future__ import annotations

import pytest

pytest.importorskip("rapidfuzz", reason="fuzzy tests need rapidfuzz")
pytest.importorskip("shapely", reason="geographic guard needs shapely")

from src.ingestion.boundary_match import (
    _capital_in_geojson,
    match_entity,
)


# ─── Synthetic Natural Earth fixtures ───────────────────────────────────────

def _square(lon_c: float, lat_c: float, half: float) -> dict:
    """Return a GeoJSON Polygon: square around (lon_c, lat_c) with half-side `half`."""
    return {
        "type": "Polygon",
        "coordinates": [[
            [lon_c - half, lat_c - half],
            [lon_c + half, lat_c - half],
            [lon_c + half, lat_c + half],
            [lon_c - half, lat_c + half],
            [lon_c - half, lat_c - half],
        ]],
    }


@pytest.fixture
def ne_fake():
    """Fake ne_by_iso mimicking real Natural Earth output.

    We place two records far apart:
      - RUS: big square around Moscow (37°E, 55°N)
      - COD: big square around Kinshasa (15°E, -4°N)
    And a distractor "Kingdom of Wonderland" near Zanzibar so that
    fuzzy matching on generic "Kingdom" tokens has targets.
    """
    return {
        "RUS": {
            "name": "Russia",
            "name_long": "Russian Federation",
            "iso_a3": "RUS",
            "sovereign": "Russia",
            "names_alt": {"en": "Russian Empire", "ru": "Россия"},
            "geojson": _square(37.0, 55.0, 20.0),  # covers most of W Russia
        },
        "COD": {
            "name": "DR Congo",
            "name_long": "Democratic Republic of the Congo",
            "iso_a3": "COD",
            "sovereign": "DR Congo",
            "names_alt": {"fr": "République démocratique du Congo"},
            "geojson": _square(22.0, -3.0, 10.0),  # covers central Africa
        },
        "WND": {
            "name": "Wonderland",
            "name_long": "Kingdom of Wonderland",
            "iso_a3": "WND",
            "sovereign": "Wonderland",
            "names_alt": {},
            "geojson": _square(40.0, -6.0, 2.0),  # Zanzibar area
        },
    }


# ─── Pure predicate tests ───────────────────────────────────────────────────

def test_capital_in_geojson_inside():
    poly = _square(0.0, 0.0, 5.0)
    assert _capital_in_geojson({"capital_lat": 1.0, "capital_lon": 1.0}, poly) is True


def test_capital_in_geojson_outside():
    poly = _square(0.0, 0.0, 5.0)
    assert _capital_in_geojson({"capital_lat": 50.0, "capital_lon": 50.0}, poly) is False


def test_capital_in_geojson_missing_coords():
    poly = _square(0.0, 0.0, 5.0)
    assert _capital_in_geojson({}, poly) is False
    assert _capital_in_geojson({"capital_lat": None, "capital_lon": None}, poly) is False


def test_capital_in_geojson_malformed_geometry():
    assert _capital_in_geojson({"capital_lat": 0, "capital_lon": 0}, None) is False
    assert _capital_in_geojson({"capital_lat": 0, "capital_lon": 0}, {"type": "bogus"}) is False


# ─── End-to-end matcher behavior ────────────────────────────────────────────

def test_fuzzy_match_rejected_when_capital_outside(ne_fake):
    """Garenganze regression: African kingdom must NOT match Russia
    even if the fuzzy scorer gives a high name-similarity score."""
    garenganze = {
        "name_original": "Garenganze",
        "name_original_lang": "sw",
        "entity_type": "kingdom",
        "year_start": 1856,
        "year_end": 1891,
        "capital_name": "Bunkeya",
        "capital_lat": -10.38,
        "capital_lon": 26.96,
        "name_variants": [
            {"name": "Yeke Kingdom", "lang": "en"},
            {"name": "Royaume du Garenganze", "lang": "fr"},
            {"name": "Msiri's Kingdom", "lang": "en"},
            {"name": "Ugarenganze", "lang": "sw"},
        ],
    }
    result = match_entity(garenganze, ne_fake)
    # Must not be matched to RUS. Either matches COD (capital inside
    # central Africa square) or falls through to no-match.
    if result.matched:
        assert result.ne_iso_a3 != "RUS", (
            "Regression: Garenganze fuzzy-matched to Russia, ignoring "
            "capital-in-polygon guard."
        )


def test_fuzzy_match_accepted_when_capital_inside(ne_fake):
    """A plausible fuzzy match (Russia for Russian Empire) should still work
    when the capital is inside the matched polygon."""
    russia = {
        "name_original": "Russian Empire",
        "entity_type": "empire",
        "year_start": 1721,
        "year_end": 1917,
        "capital_name": "Saint Petersburg",
        "capital_lat": 59.9,
        "capital_lon": 30.3,  # inside RUS square (37, 55, ±20)
        "name_variants": [],
    }
    result = match_entity(russia, ne_fake)
    assert result.matched is True
    assert result.ne_iso_a3 == "RUS"


def test_exact_name_match_rejected_when_capital_outside(ne_fake):
    """Exact-name matches must also respect the geographic guard."""
    # Entity named exactly "Russia" but with a capital in Congo —
    # contrived, but locks in the rule.
    fake = {
        "name_original": "Russia",
        "entity_type": "republic",
        "year_start": 1900,
        "year_end": None,
        "capital_name": "Kinshasa-like",
        "capital_lat": -4.0,
        "capital_lon": 15.0,
        "name_variants": [],
    }
    result = match_entity(fake, ne_fake)
    assert not (result.matched and result.ne_iso_a3 == "RUS"), (
        "Exact-name match ignored capital-outside-polygon guard."
    )


def test_fuzzy_match_rejected_when_entity_has_no_capital(ne_fake):
    """Entities without capital coords cannot be validated -> refuse fuzzy."""
    headless = {
        "name_original": "Russian Empire",
        "entity_type": "empire",
        "year_start": 1900,
        "year_end": None,
        # no capital_lat / capital_lon
        "name_variants": [],
    }
    result = match_entity(headless, ne_fake)
    # Should either be unmatched or matched via a non-fuzzy strategy
    # (ISO explicit / exact_name / capital_in_polygon — all but fuzzy).
    assert result.strategy != "fuzzy", (
        "Fuzzy match accepted for entity without capital coords — "
        "the geographic guard cannot validate, so it must refuse."
    )
