"""Test boundary_match.py Phase H area sanity guard (ETHICS-012).

The Natural Earth matcher in `boundary_match.py` used capital-in-polygon
and fuzzy match strategies. Phase H discovered that NE polygons can be
enormous (Indonesia 148 deg², Brazil 707 deg², Russia 2884 deg²) — if a
small entity (city-state, principality, chiefdom) was matched to one of
these, the polygon was geographically meaningless for that entity.

Example pre-Phase-H regression:
  Kesultanan Banten (city-state, capital Banten in Indonesia)
  → matched to Indonesia polygon (148 deg² = 7× the city-state ceiling of 4)
  Result: small sultanate "inherits" entire Dutch East Indies polygon.

Phase H added `_is_ne_polygon_too_large_for_type()` to reject these.
"""

from __future__ import annotations

import pytest

from src.ingestion.boundary_match import (
    NE_TYPE_MAX_AREA_DEG2,
    _is_ne_polygon_too_large_for_type,
    _ne_polygon_area_deg2,
)


def _make_polygon(width_deg: float, height_deg: float) -> dict:
    w, h = width_deg / 2, height_deg / 2
    return {
        "type": "Polygon",
        "coordinates": [
            [[-w, -h], [w, -h], [w, h], [-w, h], [-w, -h]]
        ],
    }


# ─── Area calculation ────────────────────────────────────────────────────


def test_area_calculation_basic_polygon():
    """1° × 1° rectangle should have area 1 deg²."""
    p = _make_polygon(1, 1)
    assert _ne_polygon_area_deg2(p) == pytest.approx(1.0, abs=0.01)


def test_area_calculation_multipolygon():
    """MultiPolygon should sum component areas."""
    mp = {
        "type": "MultiPolygon",
        "coordinates": [
            _make_polygon(2, 2)["coordinates"],  # 4 deg²
            _make_polygon(1, 1)["coordinates"],  # 1 deg²
        ],
    }
    assert _ne_polygon_area_deg2(mp) == pytest.approx(5.0, abs=0.01)


def test_area_handles_null():
    """None geometry must not raise."""
    assert _ne_polygon_area_deg2(None) == 0.0
    assert _ne_polygon_area_deg2({}) == 0.0
    assert _ne_polygon_area_deg2({"type": "Polygon"}) == 0.0


# ─── Sanity check rejections ────────────────────────────────────────────


def test_city_state_rejects_indonesia_size():
    """Kesultanan Banten city-state should not match Indonesia (148 deg²)."""
    indonesia = _make_polygon(40, 7)  # ~280 deg²
    assert _is_ne_polygon_too_large_for_type(indonesia, "city-state") is True


def test_city_state_accepts_small_country():
    """A city-state can match a small modern country (e.g. Luxembourg ~0.2 deg²)."""
    luxembourg = _make_polygon(0.5, 0.5)  # 0.25 deg²
    assert _is_ne_polygon_too_large_for_type(luxembourg, "city-state") is False


def test_chiefdom_rejects_modern_brazil():
    """Phase H found Bushoong/Garenganze/Mangbetu chiefdoms matched to Congo."""
    drc = _make_polygon(20, 20)  # 400 deg²
    assert _is_ne_polygon_too_large_for_type(drc, "chiefdom") is True


def test_kingdom_accepts_large_modern_country():
    """A historical kingdom can match a country up to its ceiling."""
    # Kingdom ceiling: 640 deg² × 3 = 1920 deg² max
    medium = _make_polygon(30, 20)  # 600 deg² ≤ 1920
    assert _is_ne_polygon_too_large_for_type(medium, "kingdom") is False


def test_kingdom_rejects_continent_sized():
    """Even kingdoms can't be continent-sized."""
    huge = _make_polygon(60, 50)  # 3000 deg² > 1920 (3× ceiling)
    assert _is_ne_polygon_too_large_for_type(huge, "kingdom") is True


def test_empire_accepts_continent_sized():
    """Empires can legitimately span continents."""
    russia = _make_polygon(100, 60)  # 6000 deg²
    # Empire ceiling: 3200 × 3 = 9600 → 6000 OK
    assert _is_ne_polygon_too_large_for_type(russia, "empire") is False


def test_unknown_type_passes_through():
    """Unknown types should not be rejected."""
    huge = _make_polygon(100, 100)
    assert _is_ne_polygon_too_large_for_type(huge, "fictional") is False


def test_null_inputs_pass_through():
    """Defensive: None should not raise."""
    assert _is_ne_polygon_too_large_for_type(None, "city-state") is False
    assert _is_ne_polygon_too_large_for_type(_make_polygon(1, 1), None) is False


# ─── Coverage ────────────────────────────────────────────────────────────


def test_all_common_entity_types_have_ceilings():
    """All entity_types currently in production DB should have a ceiling."""
    required = {
        "city", "city-state", "kingdom", "empire", "republic",
        "confederation", "chiefdom", "sultanate", "dynasty",
        "khanate", "caliphate",
    }
    missing = required - set(NE_TYPE_MAX_AREA_DEG2.keys())
    assert not missing, f"Missing type ceilings: {missing}"
