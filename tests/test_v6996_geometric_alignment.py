"""Tests for v6.99.96 — geometric analyzer aligned with the auto-fixer.

Suggestion #77 / ETHICS-014. The analyzer used to flag entities the fixer would
never reset (curated entities, a 1.5×→3.0× oversize band, polar-biased areas,
and every shared polygon including legitimate co-location / name-variant
duplicates). This produced persistent noise ("flagged 34, auto-fix reset 0").

These tests lock in the four corrections:
  1. equal-area km² removes the polar over-estimate;
  2. curated boundary sources are skipped from oversize flagging;
  3. benign shared polygons (small approximation / curated sources) are
     suppressed, while raw-inheritance shares stay flagged;
  4. the oversize threshold matches the fixer (ceiling × 3.0 / × 2.5 strict).

Tests use the analyzer's full `total_suspects` count (a delta before/after
adding an entity) rather than the 30-item payload preview, so membership checks
are robust to however many real suspects the seed corpus carries.
"""

import json
import math

from scripts.ai_cofounder_analyze import _equal_area_km2, analyze_geometric_bugs
from src.db.models import AiSuggestion, GeoEntity


# Explicit ids far above any real entity id (max curated id is 1040), so test
# entities can never collide with MANUALLY_CURATED_IDS and get falsely skipped.
_NEXT_ID = [9_000_001]


def _make_entity(
    db, name, boundary_geojson=None, entity_type="kingdom",
    capital_lat=20.0, capital_lon=10.0, boundary_source=None, confidence=0.8,
):
    eid = _NEXT_ID[0]
    _NEXT_ID[0] += 1
    e = GeoEntity(
        id=eid,
        name_original=name,
        name_original_lang="en",
        entity_type=entity_type,
        year_start=1000,
        year_end=1100,
        capital_lat=capital_lat,
        capital_lon=capital_lon,
        boundary_geojson=boundary_geojson,
        boundary_source=boundary_source,
        confidence_score=confidence,
        status="confirmed",
    )
    db.add(e)
    db.flush()
    return e


def _box(lon0, lat0, lon1, lat1):
    return {
        "type": "Polygon",
        "coordinates": [[
            [lon0, lat0], [lon1, lat0], [lon1, lat1], [lon0, lat1], [lon0, lat0],
        ]],
    }


def _long_poly(cx, cy, r=0.5, n=12):
    """A small N-gon whose JSON serialization exceeds the 100-char threshold
    used by the shared-polygon hash path (a 4-point box is too short)."""
    pts = [
        [round(cx + r * math.cos(2 * math.pi * i / n), 3),
         round(cy + r * math.sin(2 * math.pi * i / n), 3)]
        for i in range(n)
    ]
    pts.append(pts[0])
    return {"type": "Polygon", "coordinates": [pts]}


def _total_suspects(db):
    """Full suspect count the analyzer would report (not the 30-item preview).

    Clears prior geometric_bug suggestions first so repeated calls in one test
    measure the current run, then returns total_suspects (0 if none)."""
    db.query(AiSuggestion).filter(AiSuggestion.category == "geometric_bug").delete()
    db.flush()
    existing: set[str] = set()
    analyze_geometric_bugs(db, existing)
    db.flush()  # TestSession has autoflush=False; make the new suggestion visible
    tot = 0
    for s in db.query(AiSuggestion).filter(AiSuggestion.category == "geometric_bug").all():
        if s.detail_json:
            tot = max(tot, json.loads(s.detail_json).get("total_suspects", 0))
    return tot


# ── 1. Equal-area correction ────────────────────────────────────────────────

def test_equal_area_corrects_polar_bias():
    """A high-latitude box must measure far smaller geodesically than the
    legacy degree²×111² estimate (which inflated polar polygons)."""
    from shapely.geometry import shape

    geom = shape(_box(20, 60, 30, 70))  # 10°×10° box up north
    naive = geom.area * 111 * 111
    geodesic = _equal_area_km2(geom)

    assert geodesic > 0
    # Longitude degrees shrink toward the pole → geodesic must be well below
    # the naive estimate (cos(65°) ≈ 0.42).
    assert geodesic < naive * 0.6


# ── 2. Curated sources skipped from oversize flagging ───────────────────────

def test_curated_source_skipped_from_oversize(db):
    """An entity with a curated boundary_source is never flagged, even with a
    grossly oversized polygon (the fixer would never reset it)."""
    base = _total_suspects(db)
    _make_entity(
        db, name="ZZ_CuratedHuge_v6996",
        boundary_geojson=json.dumps(_box(0, 0, 80, 60)),  # huge
        entity_type="city-state",
        capital_lat=30, capital_lon=40,
        boundary_source="historical_approximation",
    )
    assert _total_suspects(db) == base, "curated source must be skipped"
    db.rollback()


def test_noncurated_huge_is_flagged(db):
    """Control for the curated test: the SAME huge polygon with a non-curated
    source IS flagged."""
    base = _total_suspects(db)
    _make_entity(
        db, name="ZZ_RawHuge_v6996",
        boundary_geojson=json.dumps(_box(0, 0, 80, 60)),
        entity_type="city-state",
        capital_lat=30, capital_lon=40,
        boundary_source=None,
    )
    assert _total_suspects(db) == base + 1, "non-curated huge polygon must be flagged"
    db.rollback()


# ── 3. Shared-polygon classification ────────────────────────────────────────

def test_benign_shared_sources_suppressed(db):
    """Two entities sharing a small approximate_circle polygon are legitimate
    co-location — the shared-polygon detector must NOT add a suspect."""
    poly = json.dumps(_long_poly(10, 20))  # >100 chars, small area
    base = _total_suspects(db)
    _make_entity(db, "ZZ_BenignShareA_v6996", boundary_geojson=poly,
                 entity_type="city-state", boundary_source="approximate_circle")
    _make_entity(db, "ZZ_BenignShareB_v6996", boundary_geojson=poly,
                 entity_type="city-state", boundary_source="approximate_circle")
    assert _total_suspects(db) == base, "benign shared polygon must be suppressed"
    db.rollback()


def test_raw_shared_polygon_still_flagged(db):
    """Two entities sharing a polygon with a NON-benign (raw-inheritance)
    source must still be flagged — exactly one new shared-polygon suspect."""
    poly = json.dumps(_long_poly(0, 0))  # >100 chars, small area
    base = _total_suspects(db)
    _make_entity(db, "ZZ_RawShareA_v6996", boundary_geojson=poly,
                 entity_type="city-state", boundary_source=None)
    _make_entity(db, "ZZ_RawShareB_v6996", boundary_geojson=poly,
                 entity_type="city-state", boundary_source=None)
    assert _total_suspects(db) == base + 1, "raw shared polygon must stay actionable"
    db.rollback()


# ── 4. Oversize threshold matches the fixer ─────────────────────────────────

def test_oversize_uses_fixer_factor(db):
    """An area between the OLD 1.5× band and the fixer's 3.0× factor must NOT
    be flagged; an area clearly above 3.0× must be flagged."""
    from shapely.geometry import shape
    from src.ingestion.fix_antimeridian_and_wrong_polygons import (
        AUTO_FIX_OVERSIZE_FACTOR, TYPE_MAX_AREA_KM2,
    )

    ceiling = TYPE_MAX_AREA_KM2["kingdom"]  # 8,000,000; kingdom => factor 3.0
    factor = AUTO_FIX_OVERSIZE_FACTOR

    in_band = shape(_box(0, 0, 40, 30))
    area = _equal_area_km2(in_band)
    if not (ceiling * 1.5 < area < ceiling * factor):
        import pytest
        pytest.skip(f"chosen box area {area:,.0f} not in target band")

    base = _total_suspects(db)
    _make_entity(db, "ZZ_InBandKingdom_v6996",
                 boundary_geojson=json.dumps(_box(0, 0, 40, 30)),
                 entity_type="kingdom", capital_lat=15, capital_lon=20,
                 boundary_source=None)
    assert _total_suspects(db) == base, (
        "area within old 1.5× band but below fixer 3× must not be flagged"
    )
    db.rollback()

    base = _total_suspects(db)
    _make_entity(db, "ZZ_HugeKingdom_v6996",
                 boundary_geojson=json.dumps(_box(-90, -40, 90, 60)),
                 entity_type="kingdom", capital_lat=10, capital_lon=0,
                 boundary_source=None)
    assert _total_suspects(db) == base + 1, "clearly oversize kingdom must be flagged"
    db.rollback()
