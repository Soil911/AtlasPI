"""Tests for v6.7.1 boundary-quality cleanups.

Covers:
  - cleanup_shared_polygons: scoring, cluster decisions, idempotency
  - fix_bad_boundaries_v671: targeted entity repairs with capital backfill
"""

from __future__ import annotations

import json

import pytest

from src.db.models import GeoEntity
from src.ingestion.cleanup_shared_polygons import (
    KEEP_THRESHOLD,
    analyze_clusters,
    best_name_score,
    strip_generic_tokens,
)
from src.ingestion.fix_bad_boundaries_v671 import FIXES, run_fixes
from tests.conftest import TestSession


# ─── strip_generic_tokens ───────────────────────────────────────────────────


def test_strip_generic_drops_administrative_suffix():
    assert strip_generic_tokens("Sui Dynasty") == "sui"
    assert strip_generic_tokens("Kingdom of Mycenae") == "mycenae"
    assert strip_generic_tokens("Sultanate of Delhi") == "delhi"
    assert strip_generic_tokens("Republic of Pisa") == "pisa"


def test_strip_generic_returns_empty_for_non_latin():
    # Arabic, Chinese, Hebrew get stripped to empty (no Latin tokens)
    assert strip_generic_tokens("الخلافة العباسية") == ""
    assert strip_generic_tokens("隋朝") == ""
    assert strip_generic_tokens("ממלכת ישראל") == ""


def test_strip_generic_keeps_distinctive_tokens():
    # "Holy Roman Empire" → "holy roman" (empire is generic)
    assert strip_generic_tokens("Holy Roman Empire") == "holy roman"
    # "Byzantine Empire" → "byzantine"
    assert strip_generic_tokens("Byzantine Empire") == "byzantine"


# ─── best_name_score ────────────────────────────────────────────────────────


def test_best_name_score_synonym_suffixes():
    # Sui Dynasty == Sui Empire should score 1.00 (only "sui" left after stripping)
    assert best_name_score(["Sui Dynasty"], "Sui Empire") == 1.0


def test_best_name_score_reordered_tokens():
    # Sultanate of Delhi == Delhi Sultanate
    assert best_name_score(["Sultanate of Delhi"], "Delhi Sultanate") == 1.0


def test_best_name_score_identity():
    assert best_name_score(["Fatimid Caliphate"], "Fatimid Caliphate") == 1.0


def test_best_name_score_no_match():
    # Unrelated entities should score well below the keep threshold
    assert best_name_score(["Grevskabet Flandern"], "Holy Roman Empire") < KEEP_THRESHOLD
    assert best_name_score(["Duche de Savoie"], "Holy Roman Empire") < KEEP_THRESHOLD


def test_best_name_score_picks_best_from_variants():
    # Entity's native name may not match, but one of its variants does
    names = ["الخلافة العباسية", "Abbasid Caliphate", "Califfato Abbaside"]
    assert best_name_score(names, "Abbasid Caliphate") == 1.0


def test_best_name_score_non_latin_entity_no_variants_returns_zero():
    # Non-Latin name with no Latin variant scores 0 (not in cluster match)
    assert best_name_score(["隋以前北朝"], "Sui Empire") == 0.0


# ─── analyze_clusters ───────────────────────────────────────────────────────


def test_analyze_clusters_is_idempotent_post_cleanup(setup_test_db):
    """After the v6.7.1 cleanup, no cluster should have ≥3 entities.

    This test validates that cleanup_shared_polygons ran on the seed data
    and the DB is clean.
    """
    session = TestSession()
    try:
        decisions = analyze_clusters(session)
        # Every remaining cluster that's still present in the DB must be
        # below the MIN_SHARED_CLUSTER_SIZE threshold, OR every entity in
        # the cluster has score >= KEEP_THRESHOLD (all legitimate owners).
        for d in decisions:
            assert len(d.entity_ids_to_drop) == 0, (
                f"Cluster {d.aourednik_name!r} still has "
                f"{len(d.entity_ids_to_drop)} drop candidates post-cleanup: "
                f"{d.entity_ids_to_drop}"
            )
    finally:
        session.close()


# ─── fix_bad_boundaries_v671 ────────────────────────────────────────────────


def test_fixes_declare_all_required_entity_ids():
    # Audit identifies 11 targeted fixes; FIXES list must cover each ID
    expected_ids = {325, 338, 3, 562, 218, 545, 524, 525, 528, 530, 531}
    actual_ids = {f.entity_id for f in FIXES}
    assert expected_ids == actual_ids


def test_pechenegs_has_capital_post_fix(setup_test_db):
    """Pechenegs (325) and Nogai Horde (338) had NULL capital coords; the
    v6.7.1 fix backfilled them so they can be rendered. This test catches
    regressions if the fix is un-applied."""
    session = TestSession()
    try:
        for eid in (325, 338):
            e = session.get(GeoEntity, eid)
            if e is None:
                # Entity not in seed (DB subset) — skip gracefully
                continue
            assert e.capital_lat is not None, (
                f"Entity {eid} still has NULL capital_lat; v6.7.1 fix not applied"
            )
            assert e.capital_lon is not None, (
                f"Entity {eid} still has NULL capital_lon; v6.7.1 fix not applied"
            )
    finally:
        session.close()


def test_istanbul_has_small_city_polygon(setup_test_db):
    """Istanbul (id=3) had the Phrygians polygon (~462k km²) pre-v6.7.1.
    Post-fix, it's a small generated polygon around the city coordinates."""
    session = TestSession()
    try:
        e = session.get(GeoEntity, 3)
        if e is None:
            pytest.skip("Istanbul not in seeded test DB")
        geom = json.loads(e.boundary_geojson)
        # Small polygon = small bounding box. We don't depend on exact
        # vertex count, just assert the polygon is reasonably small.
        coords = geom["coordinates"][0]
        lats = [c[1] for c in coords]
        lons = [c[0] for c in coords]
        lat_span = max(lats) - min(lats)
        lon_span = max(lons) - min(lons)
        # City-radius polygons span <1 degree of lat/lon, whereas the old
        # Phrygians polygon spanned many degrees.
        assert lat_span < 1.0, f"Istanbul polygon too tall: {lat_span}"
        assert lon_span < 1.0, f"Istanbul polygon too wide: {lon_span}"
        # aourednik provenance must be cleared
        assert e.boundary_aourednik_name is None
    finally:
        session.close()


def test_placeholder_boxes_have_ethical_note(setup_test_db):
    """The 5 entities flagged as 5-point placeholder rectangles must carry
    an explicit note so consumers know the polygon is a placeholder."""
    session = TestSession()
    try:
        for eid in (524, 525, 528, 530, 531):
            e = session.get(GeoEntity, eid)
            if e is None:
                continue
            assert e.ethical_notes is not None, (
                f"Entity {eid} missing ethical_notes"
            )
            assert "placeholder" in e.ethical_notes.lower() or "v6.7.1" in e.ethical_notes, (
                f"Entity {eid} ethical_notes doesn't flag placeholder: "
                f"{e.ethical_notes[:100]!r}"
            )
            # Status must be demoted from confirmed
            assert e.status != "confirmed", (
                f"Entity {eid} still confirmed with placeholder box"
            )
    finally:
        session.close()


def test_run_fixes_dry_run_is_noop(setup_test_db):
    """run_fixes(dry_run=True) must not mutate the DB."""
    session = TestSession()
    try:
        pre_state = {}
        for fix in FIXES:
            e = session.get(GeoEntity, fix.entity_id)
            if e is not None:
                pre_state[fix.entity_id] = (
                    e.boundary_geojson, e.boundary_source, e.status,
                    e.ethical_notes, e.capital_lat, e.capital_lon,
                )
        result = run_fixes(dry_run=True, session=session)
        assert result["db_committed"] is False
        # State unchanged
        for fix in FIXES:
            e = session.get(GeoEntity, fix.entity_id)
            if e is None or fix.entity_id not in pre_state:
                continue
            post = (
                e.boundary_geojson, e.boundary_source, e.status,
                e.ethical_notes, e.capital_lat, e.capital_lon,
            )
            assert post == pre_state[fix.entity_id], (
                f"Entity {fix.entity_id} mutated during dry-run"
            )
    finally:
        session.rollback()
        session.close()
