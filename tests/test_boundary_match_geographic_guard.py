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
    FUZZY_CENTROID_MAX_KM,
    _capital_in_geojson,
    _capital_to_centroid_km,
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


# ─── Centroid-distance soft check (v6.2) ────────────────────────────────────

def test_capital_to_centroid_km_basic():
    """Centroid of a square at (0, 0) -> capital at (1, 1) ≈ 157 km."""
    poly = _square(0.0, 0.0, 5.0)
    d = _capital_to_centroid_km(
        {"capital_lat": 1.0, "capital_lon": 1.0}, poly
    )
    assert d is not None
    # Point at (1°, 1°) from (0,0) ≈ 157 km
    assert 150 < d < 170, f"Expected ~157 km, got {d}"


def test_capital_to_centroid_km_missing():
    poly = _square(0.0, 0.0, 5.0)
    assert _capital_to_centroid_km({}, poly) is None
    assert _capital_to_centroid_km({"capital_lat": 0.0, "capital_lon": 0.0}, None) is None


def test_fuzzy_match_rejected_when_centroid_too_far():
    """Simulate an NE polygon with exclave: capital falls inside an
    outlier patch but polygon centroid is >500 km away — fuzzy must
    refuse even if capital-in-polygon passes."""
    # Polygon as MultiPolygon: main body in Europe + tiny pocket in Africa.
    # Centroid ends up in Europe, but capital sits inside the African pocket.
    exclave_poly = {
        "type": "MultiPolygon",
        "coordinates": [
            # Europe main body (approx France area)
            [[
                [0.0, 45.0], [4.0, 45.0], [4.0, 49.0],
                [0.0, 49.0], [0.0, 45.0],
            ]],
            # Africa pocket (approx Guyane Française size, but in W Africa)
            [[
                [10.0, 5.0], [11.0, 5.0], [11.0, 6.0],
                [10.0, 6.0], [10.0, 5.0],
            ]],
        ],
    }
    ne = {
        "FAK": {
            "name": "Fakeland",
            "name_long": "Kingdom of Fakeland",
            "iso_a3": "FAK",
            "sovereign": "Fakeland",
            "names_alt": {},
            "geojson": exclave_poly,
        },
    }
    # Entity whose name fuzzy-matches "Fakeland" (share Kingdom token)
    # and whose capital is inside the African pocket.
    entity = {
        "name_original": "Kingdom of Makeland",
        "entity_type": "kingdom",
        "year_start": 1900,
        "year_end": None,
        "capital_lat": 5.5,
        "capital_lon": 10.5,  # inside African pocket
        "name_variants": [],
    }
    result = match_entity(entity, ne)
    # Either not matched or matched via non-fuzzy strategy. What we must
    # forbid is: fuzzy match to Fakeland when capital is in an exclave
    # far from the polygon centroid.
    assert not (result.matched and result.strategy == "fuzzy" and result.ne_iso_a3 == "FAK"), (
        "Centroid-distance soft check failed: entity in African exclave "
        "fuzzy-matched to Fakeland despite centroid being in Europe "
        f"(threshold {FUZZY_CENTROID_MAX_KM} km)."
    )


def test_fuzzy_match_accepted_when_centroid_close():
    """Capital inside polygon AND within 500 km of centroid → accept."""
    # Single square, capital near centroid
    poly = _square(10.0, 10.0, 5.0)  # square around (10°E, 10°N), ~550 km side
    ne = {
        "CTR": {
            "name": "Centerland",
            "name_long": "Republic of Centerland",
            "iso_a3": "CTR",
            "sovereign": "Centerland",
            "names_alt": {},
            "geojson": poly,
        },
    }
    entity = {
        "name_original": "Republic of Centrolandia",
        "entity_type": "republic",
        "year_start": 1900,
        "year_end": None,
        "capital_lat": 11.0,  # ~111 km from centroid (10, 10)
        "capital_lon": 10.5,
        "name_variants": [{"name": "Centerland", "lang": "en"}],
    }
    result = match_entity(entity, ne)
    assert result.matched is True
    assert result.ne_iso_a3 == "CTR"
