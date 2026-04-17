"""Regression tests for v6.7.3 boundary fix batch.

Covers the 4 entities (Kalmyk, Hotaki, Bactria, Kazan) whose real
geodesic polygon area was still >2x historical peak after v6.7.2.
"""
from __future__ import annotations

import json

import pytest
from pyproj import Geod
from shapely.geometry import shape

from src.ingestion.fix_bad_boundaries_v673 import FIXES_V673

V673_IDS = {f.entity_id for f in FIXES_V673}

_GEOD = Geod(ellps="WGS84")


def _real_area_km2(geojson_str: str) -> float:
    geom = shape(json.loads(geojson_str))
    area_m2 = abs(_GEOD.geometry_area_perimeter(geom)[0])
    return area_m2 / 1_000_000


class TestFixesV673Structure:
    def test_fixes_v673_count(self):
        assert len(FIXES_V673) == 4

    def test_all_fixes_regenerate(self):
        for fix in FIXES_V673:
            assert fix.keep_geometry is False
            assert fix.regenerate_with_radius_km is not None
            assert fix.regenerate_with_radius_km >= 500.0

    def test_all_fixes_have_v673_note(self):
        for fix in FIXES_V673:
            assert fix.append_note is not None
            assert "[v6.7.3]" in fix.append_note

    def test_no_overlap_with_v671_v672(self):
        from src.ingestion.fix_bad_boundaries_v671 import FIXES as FV671
        from src.ingestion.fix_bad_boundaries_v672 import FIXES_V672 as FV672

        v671 = {f.entity_id for f in FV671}
        v672 = {f.entity_id for f in FV672}
        assert not (V673_IDS & v671)
        assert not (V673_IDS & v672)


class TestV673RealAreaBounds:
    """Post-fix real geodesic area should be in historical-peak range."""

    @pytest.mark.parametrize(
        "entity_id,min_km2,max_km2,label",
        [
            (604, 500_000, 2_000_000, "Kalmyk Khanate"),
            (343, 700_000, 2_500_000, "Hotaki dynasty"),
            (350, 500_000, 1_500_000, "Bactria kingdom"),
            (330, 400_000, 1_200_000, "Kazan Khanate"),
        ],
    )
    def test_real_area_in_range(self, db, entity_id, min_km2, max_km2, label):
        """v6.7.3 fix only applies if entity is still approximate_generated with v6.7.3 note.

        If a later run (v6.29 boundary enrichment, v6.30 displacement rollback)
        modified the boundary, the v6.7.3 area range no longer applies.
        """
        from src.db.models import GeoEntity
        e = db.query(GeoEntity).filter_by(id=entity_id).first()
        assert e is not None
        if e.boundary_source != "approximate_generated":
            pytest.skip(
                f"{label} upgraded to {e.boundary_source} — v6.7.3 range check not applicable"
            )
        if e.ethical_notes and "[v6.30-displaced-rollback]" in e.ethical_notes:
            pytest.skip(
                f"{label} was reverted by v6.30 displaced-rollback — v6.7.3 range no longer applies"
            )
        area = _real_area_km2(e.boundary_geojson)
        assert min_km2 <= area <= max_km2, (
            f"{label} (id={entity_id}) real area {area:.0f} km² "
            f"outside [{min_km2}, {max_km2}]"
        )


class TestV673EthicalNotes:
    @pytest.mark.parametrize("entity_id", sorted(V673_IDS))
    def test_entity_has_v673_note(self, db, entity_id):
        from src.db.models import GeoEntity
        e = db.query(GeoEntity).filter_by(id=entity_id).first()
        assert e is not None
        assert e.ethical_notes is not None
        assert "[v6.7.3]" in e.ethical_notes


class TestV673ConfidenceCapped:
    @pytest.mark.parametrize("entity_id", sorted(V673_IDS))
    def test_confidence_capped_at_04(self, db, entity_id):
        """Confidence cap only applies if boundary is still approximate_generated.

        When v6.29+ boundary enrichment upgrades the entity to real historical
        data (aourednik/natural_earth), the confidence is no longer capped.
        """
        from src.db.models import GeoEntity
        e = db.query(GeoEntity).filter_by(id=entity_id).first()
        assert e is not None
        if e.boundary_source != "approximate_generated":
            pytest.skip(
                f"entity {entity_id} upgraded to {e.boundary_source} — v6.7.3 cap not applicable"
            )
        assert e.confidence_score <= 0.4
