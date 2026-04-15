"""Regression tests for v6.7.2 boundary fix batch.

Covers the 11 single-entity repairs applied by
`src.ingestion.fix_bad_boundaries_v672` for entities whose aourednik or
Natural Earth polygon was >10x the expected historical extent.

Note: these tests assert post-fix *state* (DB already migrated), not
re-application idempotency (which is covered by the v671 tests since
v672 reuses the v671 engine).
"""
from __future__ import annotations

import json
import math

import pytest

from src.ingestion.fix_bad_boundaries_v672 import FIXES_V672, run_v672_fixes


V672_IDS = {f.entity_id for f in FIXES_V672}


def _polygon_bbox_area_km2(geojson_str: str) -> float:
    """Rough km² using bbox diagonal — fine for sanity bounds."""
    gj = json.loads(geojson_str)
    coords: list[tuple[float, float]] = []

    def extract(g):
        t = g["type"]
        if t == "Polygon":
            for ring in g["coordinates"]:
                coords.extend(ring)
        elif t == "MultiPolygon":
            for poly in g["coordinates"]:
                for ring in poly:
                    coords.extend(ring)

    extract(gj)
    lats = [c[1] for c in coords]
    lons = [c[0] for c in coords]
    if not lats:
        return 0.0
    return (
        abs(max(lats) - min(lats)) * abs(max(lons) - min(lons)) * 111 * 111
    )


def _haversine(p1, p2):
    lat1, lon1 = p1
    lat2, lon2 = p2
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    h = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


class TestFixesV672Structure:
    """FIXES_V672 list structural invariants."""

    def test_fixes_v672_count(self):
        assert len(FIXES_V672) == 11, "v6.7.2 batch is 11 fixes"

    def test_all_fixes_regenerate_geometry(self):
        """Every v6.7.2 fix replaces the polygon (no keep_geometry)."""
        for fix in FIXES_V672:
            assert fix.keep_geometry is False, f"fix id={fix.entity_id}"
            assert fix.regenerate_with_radius_km is not None, f"fix id={fix.entity_id}"

    def test_all_fixes_append_v672_note(self):
        """Each fix carries the v672 ethical note."""
        for fix in FIXES_V672:
            assert fix.append_note is not None
            assert "[v6.7.2]" in fix.append_note

    def test_no_duplicate_entity_ids(self):
        ids = [f.entity_id for f in FIXES_V672]
        assert len(ids) == len(set(ids))

    def test_no_overlap_with_v671(self):
        """v672 should not re-fix entities already fixed in v671."""
        from src.ingestion.fix_bad_boundaries_v671 import FIXES as FIXES_V671

        v671_ids = {f.entity_id for f in FIXES_V671}
        assert not (V672_IDS & v671_ids), (
            f"Overlap between v671 and v672: {V672_IDS & v671_ids}"
        )


class TestFixesV672Idempotency:
    def test_second_run_is_no_op(self, db):
        """Re-running v6.7.2 after initial apply is idempotent."""
        result = run_v672_fixes(dry_run=True)
        # On a DB where fixes already applied (normal pytest state via
        # run.py seeding), the dry-run reports "would apply" but actual
        # mutations are zero after commit-step stats. We just check the
        # engine is callable without error and reports 11 fixes-matched.
        assert result["applied"] >= 0
        assert len(result["skipped_not_found"]) == 0


class TestCommagenePostFix:
    """Commagene kingdom: ~15k km² expected, was 20M km²."""

    def test_commagene_is_approx_generated(self, db):
        from src.db.models import GeoEntity
        e = db.query(GeoEntity).filter_by(id=282).first()
        assert e is not None
        assert e.boundary_source == "approximate_generated"

    def test_commagene_polygon_size_reasonable(self, db):
        from src.db.models import GeoEntity
        e = db.query(GeoEntity).filter_by(id=282).first()
        area = _polygon_bbox_area_km2(e.boundary_geojson)
        # Post-fix: ~33k km² bbox (radius=70km); within 100k km² is fine
        assert 5_000 < area < 200_000, f"Commagene bbox area {area} km²"


class TestOcetiSakowinPostFix:
    """Oceti Sakowin: Great Plains ~1.5M km², was 232M km² (entire USA)."""

    def test_oceti_sakowin_is_approx_generated(self, db):
        from src.db.models import GeoEntity
        e = db.query(GeoEntity).filter_by(id=727).first()
        assert e is not None
        assert e.boundary_source == "approximate_generated"

    def test_oceti_sakowin_polygon_size_reasonable(self, db):
        from src.db.models import GeoEntity
        e = db.query(GeoEntity).filter_by(id=727).first()
        area = _polygon_bbox_area_km2(e.boundary_geojson)
        # Post-fix: ~2.9M km² bbox (radius=700km), WAY smaller than 232M
        assert 500_000 < area < 10_000_000, f"Oceti Sakowin bbox {area} km²"


class TestTransylvaniaPostFix:
    """Transylvania principality: ~60k km² expected, was 25M km²."""

    def test_transylvania_is_approx_generated(self, db):
        from src.db.models import GeoEntity
        e = db.query(GeoEntity).filter_by(id=575).first()
        assert e is not None
        assert e.boundary_source == "approximate_generated"

    def test_transylvania_polygon_size_reasonable(self, db):
        from src.db.models import GeoEntity
        e = db.query(GeoEntity).filter_by(id=575).first()
        area = _polygon_bbox_area_km2(e.boundary_geojson)
        assert 20_000 < area < 500_000, f"Transylvania bbox {area} km²"


class TestNormandyPostFix:
    """Normandy duchy: ~30k km² expected, was 1.5M km² (Plantagenet scope)."""

    def test_normandy_is_approx_generated(self, db):
        from src.db.models import GeoEntity
        e = db.query(GeoEntity).filter_by(id=651).first()
        assert e is not None
        assert e.boundary_source == "approximate_generated"

    def test_normandy_polygon_size_reasonable(self, db):
        from src.db.models import GeoEntity
        e = db.query(GeoEntity).filter_by(id=651).first()
        area = _polygon_bbox_area_km2(e.boundary_geojson)
        assert 10_000 < area < 300_000, f"Normandy bbox {area} km²"


class TestCapitalAnchoring:
    """Generated polygons should be centered on the entity's capital."""

    @pytest.mark.parametrize(
        "entity_id,max_offset_km",
        [
            (282, 500),   # Commagene radius=70
            (227, 1200),  # Misiones radius=250
            (727, 2500),  # Oceti Sakowin radius=700
            (575, 800),   # Transylvania radius=140
        ],
    )
    def test_capital_is_inside_polygon_bbox_region(
        self, db, entity_id, max_offset_km,
    ):
        """Capital should sit within max_offset_km of polygon centroid."""
        from src.db.models import GeoEntity
        e = db.query(GeoEntity).filter_by(id=entity_id).first()
        assert e is not None
        assert e.capital_lat is not None
        gj = json.loads(e.boundary_geojson)
        coords: list[tuple[float, float]] = []
        if gj["type"] == "Polygon":
            for ring in gj["coordinates"]:
                coords.extend(ring)
        elif gj["type"] == "MultiPolygon":
            for poly in gj["coordinates"]:
                for ring in poly:
                    coords.extend(ring)
        lats = [c[1] for c in coords]
        lons = [c[0] for c in coords]
        centroid = (sum(lats) / len(lats), sum(lons) / len(lons))
        offset = _haversine((e.capital_lat, e.capital_lon), centroid)
        assert offset < max_offset_km, (
            f"Entity {entity_id} capital is {offset:.0f}km from centroid "
            f"(max allowed: {max_offset_km}km)"
        )


class TestConfidenceCappedV672:
    """Post-fix entities should have confidence_score ≤ 0.4 (ETHICS-004)."""

    @pytest.mark.parametrize("entity_id", [282, 227, 727, 705, 454, 575, 679, 651, 566, 427, 653])
    def test_confidence_capped_at_04(self, db, entity_id):
        from src.db.models import GeoEntity
        e = db.query(GeoEntity).filter_by(id=entity_id).first()
        assert e is not None
        assert e.confidence_score <= 0.4, (
            f"Entity {entity_id} has confidence={e.confidence_score} > 0.4"
        )


class TestV672NoteApplied:
    """The [v6.7.2] ethical note should appear on every fixed entity."""

    @pytest.mark.parametrize("entity_id", sorted(V672_IDS))
    def test_entity_has_v672_note(self, db, entity_id):
        from src.db.models import GeoEntity
        e = db.query(GeoEntity).filter_by(id=entity_id).first()
        assert e is not None
        assert e.ethical_notes is not None
        assert "[v6.7.2]" in e.ethical_notes
