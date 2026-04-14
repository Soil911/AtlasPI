"""Test suite for src.ingestion.sync_boundaries_from_json.

Covers the monotonic-upgrade contract:
  - DB boundary is upgraded when batch has a meaningfully bigger real geometry
  - DB boundary is NEVER downgraded (higher-vertex DB wins over smaller batch)
  - Disputed entities cannot have confidence raised above 0.70 (ETHICS-003)
  - Dry-run mode reports the same counts without mutating the DB
  - Idempotency: running twice is a no-op after the first pass
"""

import json

import pytest

from src.db.models import GeoEntity
from src.ingestion.sync_boundaries_from_json import (
    _backfill_provenance,
    _count_vertices,
    _should_upgrade,
    sync_boundaries_from_json,
)
from tests.conftest import TestSession


# ─── unit tests: pure predicates ───────────────────────────────────────────

def test_count_vertices_handles_shapes():
    assert _count_vertices({"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [0, 1], [0, 0]]]}) == 4
    assert _count_vertices({"type": "MultiPolygon", "coordinates": [
        [[[0, 0], [1, 0], [0, 1], [0, 0]]],
        [[[2, 2], [3, 2], [2, 3], [2, 2]]],
    ]}) == 8
    assert _count_vertices({"type": "Point", "coordinates": [0, 0]}) == 0
    assert _count_vertices(None) == 0
    assert _count_vertices({}) == 0


def _poly(n: int) -> dict:
    """Generate a closed Polygon with `n` vertices (including closure)."""
    coords = [[i * 0.1, i * 0.1] for i in range(n - 1)]
    coords.append(coords[0])
    return {"type": "Polygon", "coordinates": [coords]}


def test_should_upgrade_empty_db_accepts_real_batch():
    assert _should_upgrade(None, {"boundary_geojson": _poly(100)}) is True


def test_should_upgrade_db_point_accepts_real_batch():
    db_point = json.dumps({"type": "Point", "coordinates": [0, 0]})
    assert _should_upgrade(db_point, {"boundary_geojson": _poly(100)}) is True


def test_should_upgrade_rejects_batch_point():
    batch = {"boundary_geojson": {"type": "Point", "coordinates": [0, 0]}}
    assert _should_upgrade(json.dumps(_poly(13)), batch) is False


def test_should_upgrade_rejects_tiny_batch():
    # Degenerate batch with <8 verts is always rejected.
    assert _should_upgrade(None, {"boundary_geojson": _poly(5)}) is False


def test_should_upgrade_monotonic_guard_blocks_downgrade():
    """A larger DB polygon must NOT be overwritten by a smaller batch one."""
    db = json.dumps(_poly(1000))
    batch = {"boundary_geojson": _poly(100)}
    assert _should_upgrade(db, batch) is False


def test_should_upgrade_requires_material_gain():
    """20% floor: a 10% increase is not enough to trigger churn."""
    db = json.dumps(_poly(100))
    batch = {"boundary_geojson": _poly(109)}  # +9%
    assert _should_upgrade(db, batch) is False

    batch = {"boundary_geojson": _poly(125)}  # +25%
    assert _should_upgrade(db, batch) is True


# ─── integration tests: full sync against a fake DB ─────────────────────────

@pytest.fixture
def stale_db(setup_test_db, tmp_path, monkeypatch):
    """Set up a test DB with a handful of entities having stale boundaries."""
    # The real batch index is loaded by the function from data/entities/*.json,
    # which the test_db already seeds into the DB. For this test we simulate
    # drift by directly mutating the DB's boundary_geojson *after* seeding.
    session = TestSession()
    try:
        # Pick three known entities and downgrade their boundaries to Point-like stubs.
        targets = session.query(GeoEntity).limit(3).all()
        original = []
        for e in targets:
            original.append((e.id, e.boundary_geojson, e.confidence_score))
            e.boundary_geojson = json.dumps(_poly(13))  # tiny seeded polygon
            e.confidence_score = 0.4
        session.commit()
        ids = [e.id for e in targets]
    finally:
        session.close()
    yield ids
    # Restore originals so other tests don't see the drift.
    session = TestSession()
    try:
        for (eid, geom, conf) in original:
            ent = session.get(GeoEntity, eid)
            if ent is not None:
                ent.boundary_geojson = geom
                ent.confidence_score = conf
        session.commit()
    finally:
        session.close()


def test_sync_dry_run_reports_upgrades_without_writing(stale_db):
    session = TestSession()
    try:
        stats = sync_boundaries_from_json(dry_run=True, session=session)
    finally:
        session.close()
    assert stats.total_db > 0
    assert stats.matched_in_batch > 0
    # Verify nothing changed in the DB.
    verify = TestSession()
    try:
        for eid in stale_db:
            ent = verify.get(GeoEntity, eid)
            assert ent is not None
            geom = json.loads(ent.boundary_geojson)
            assert _count_vertices(geom) == 13, "dry-run must not mutate DB"
    finally:
        verify.close()


def test_sync_upgrades_stale_entities(stale_db):
    session = TestSession()
    try:
        stats = sync_boundaries_from_json(dry_run=False, session=session)
    finally:
        session.close()

    # At least the three we stubbed should have been upgraded, assuming their
    # batch counterparts carry real boundaries (they do in v6.1.1).
    assert stats.upgraded >= 3, f"expected ≥3 upgrades, got {stats.upgraded}"

    # Verify the stubbed entities now have > 13 vertices.
    verify = TestSession()
    try:
        upgraded_count = 0
        for eid in stale_db:
            ent = verify.get(GeoEntity, eid)
            geom = json.loads(ent.boundary_geojson)
            if _count_vertices(geom) > 13:
                upgraded_count += 1
        assert upgraded_count == 3, (
            f"expected all 3 stubbed entities upgraded, got {upgraded_count}"
        )
    finally:
        verify.close()


def test_sync_is_idempotent(stale_db):
    """Running sync twice yields zero additional upgrades."""
    session = TestSession()
    try:
        first = sync_boundaries_from_json(dry_run=False, session=session)
    finally:
        session.close()

    session = TestSession()
    try:
        second = sync_boundaries_from_json(dry_run=False, session=session)
    finally:
        session.close()

    assert first.upgraded >= 3
    assert second.upgraded == 0, f"second run must be a no-op, got {second.upgraded}"


# ─── ETHICS-006 displacement-correction path ───────────────────────────────

def test_db_capital_displaced_detects_gross_displacement():
    """Unit test: capital very far from polygon -> True; inside -> False."""
    from src.ingestion.sync_boundaries_from_json import _db_capital_displaced

    class FakeEntity:
        def __init__(self, lat, lon, geom):
            self.capital_lat = lat
            self.capital_lon = lon
            self.boundary_geojson = json.dumps(geom) if geom else None

    # Polygon around (0, 0) with half-side 1 deg (~111 km)
    square = {
        "type": "Polygon",
        "coordinates": [[
            [-1, -1], [1, -1], [1, 1], [-1, 1], [-1, -1],
        ]],
    }
    # Inside -> False
    assert _db_capital_displaced(FakeEntity(0.0, 0.0, square)) is False
    # ~111 km south, just outside -> distance ~0 km -> False (within tolerance)
    assert _db_capital_displaced(FakeEntity(-1.0, 0.0, square)) is False
    # 5 deg south, ~555 km away -> True
    assert _db_capital_displaced(FakeEntity(-6.0, 0.0, square)) is True
    # Cross-continent (Africa vs Europe polygon) -> True
    assert _db_capital_displaced(FakeEntity(-20.0, 30.0, square)) is True


def test_sync_accepts_displacement_downgrade():
    """If DB has aourednik polygon but capital is way outside and JSON now
    says approximate_generated, the sync should downgrade — one legitimate
    exception to the monotonic-upgrade rule (ETHICS-006 v6.2)."""
    from tempfile import TemporaryDirectory
    import pathlib as _pl
    from unittest.mock import patch

    # Create a test DB row with a catastrophically displaced aourednik polygon
    session = TestSession()
    try:
        # Pick a known entity and force displacement
        ent = session.query(GeoEntity).filter(
            GeoEntity.name_original == "Imperium Romanum"
        ).first()
        if not ent:
            pytest.skip("Imperium Romanum not seeded — cannot run test")

        original_geom = ent.boundary_geojson
        original_source = ent.boundary_source
        original_conf = ent.confidence_score

        # Plant a displaced aourednik polygon: square in Antarctica while
        # capital (Rome) stays at 41.9N, 12.5E.
        antarctica = {
            "type": "Polygon",
            "coordinates": [[
                [-10, -75], [10, -75], [10, -70], [-10, -70], [-10, -75],
            ]],
        }
        ent.boundary_geojson = json.dumps(antarctica)
        ent.boundary_source = "aourednik"
        ent.boundary_aourednik_name = "Imposter"
        ent.confidence_score = 0.8
        session.commit()
    finally:
        session.close()

    # Build a fake batch JSON dir where Imperium Romanum is approximate_generated
    with TemporaryDirectory() as td:
        tdp = _pl.Path(td)
        fake_batch = [
            {
                "name_original": "Imperium Romanum",
                "boundary_geojson": _poly(20),  # valid 20-vertex polygon
                "boundary_source": "approximate_generated",
                "confidence_score": 0.4,
            }
        ]
        (tdp / "batch_00_test.json").write_text(json.dumps(fake_batch), encoding="utf-8")

        with patch(
            "src.ingestion.sync_boundaries_from_json.ENTITIES_DIR", tdp
        ):
            session = TestSession()
            try:
                stats = sync_boundaries_from_json(dry_run=False, session=session)
            finally:
                session.close()

    assert stats.displacement_downgraded >= 1, (
        f"expected ≥1 displacement downgrade, got {stats.displacement_downgraded}"
    )

    # Verify DB was actually corrected
    verify = TestSession()
    try:
        ent = verify.query(GeoEntity).filter(
            GeoEntity.name_original == "Imperium Romanum"
        ).first()
        assert ent.boundary_source == "approximate_generated"
        assert ent.boundary_aourednik_name is None
        assert ent.confidence_score == 0.4
    finally:
        verify.close()

    # Restore original state so other tests aren't affected
    restore = TestSession()
    try:
        ent = restore.query(GeoEntity).filter(
            GeoEntity.name_original == "Imperium Romanum"
        ).first()
        ent.boundary_geojson = original_geom
        ent.boundary_source = original_source
        ent.confidence_score = original_conf
        ent.boundary_aourednik_name = None
        restore.commit()
    finally:
        restore.close()


def test_backfill_provenance_copies_when_db_null(setup_test_db):
    """When DB has NULL provenance but the batch has a value, backfill copies."""
    session = TestSession()
    try:
        entity = session.query(GeoEntity).first()
        entity.boundary_source = None
        entity.boundary_ne_iso_a3 = None
        entity.boundary_aourednik_precision = None

        batch = {
            "boundary_source": "natural_earth",
            "boundary_ne_iso_a3": "ITA",
            "boundary_aourednik_precision": 3,
        }
        touched = _backfill_provenance(entity, batch, dry_run=False)
        assert touched is True
        assert entity.boundary_source == "natural_earth"
        assert entity.boundary_ne_iso_a3 == "ITA"
        assert entity.boundary_aourednik_precision == 3
    finally:
        session.rollback()
        session.close()


def test_backfill_provenance_never_overwrites_existing(setup_test_db):
    """When DB already has a provenance value, backfill must not touch it."""
    session = TestSession()
    try:
        entity = session.query(GeoEntity).first()
        entity.boundary_source = "academic_source"  # already set
        entity.boundary_ne_iso_a3 = None  # missing, should backfill

        batch = {
            "boundary_source": "natural_earth",  # different from DB
            "boundary_ne_iso_a3": "ITA",
        }
        touched = _backfill_provenance(entity, batch, dry_run=False)
        assert touched is True  # because ne_iso_a3 was NULL
        # But boundary_source was preserved
        assert entity.boundary_source == "academic_source"
        assert entity.boundary_ne_iso_a3 == "ITA"
    finally:
        session.rollback()
        session.close()


def test_backfill_provenance_dry_run_does_not_mutate(setup_test_db):
    """Dry-run returns True for 'would touch' but does not set attributes."""
    session = TestSession()
    try:
        entity = session.query(GeoEntity).first()
        entity.boundary_source = None

        batch = {"boundary_source": "natural_earth"}
        touched = _backfill_provenance(entity, batch, dry_run=True)
        assert touched is True
        # But the attribute was NOT written.
        assert entity.boundary_source is None
    finally:
        session.rollback()
        session.close()


def test_backfill_provenance_noop_when_batch_has_nothing(setup_test_db):
    """If the batch has no provenance fields, backfill is a clean no-op."""
    session = TestSession()
    try:
        entity = session.query(GeoEntity).first()
        entity.boundary_source = None

        touched = _backfill_provenance(entity, {}, dry_run=False)
        assert touched is False
        assert entity.boundary_source is None
    finally:
        session.rollback()
        session.close()


def test_sync_respects_ethics_003_cap(setup_test_db):
    """Disputed entities get confidence capped at 0.70 even when batch says higher."""
    # Pick a disputed entity and verify the cap is applied.
    session = TestSession()
    try:
        disputed = session.query(GeoEntity).filter(GeoEntity.status == "disputed").first()
        if disputed is None:
            pytest.skip("No disputed entities in test DB — cap can't be exercised")

        # Force drift so the upgrade path fires.
        original_geom = disputed.boundary_geojson
        original_conf = disputed.confidence_score
        disputed.boundary_geojson = json.dumps(_poly(13))
        disputed.confidence_score = 0.30
        session.commit()
        disputed_id = disputed.id
    finally:
        session.close()

    try:
        session = TestSession()
        try:
            sync_boundaries_from_json(dry_run=False, session=session)
        finally:
            session.close()

        verify = TestSession()
        try:
            ent = verify.get(GeoEntity, disputed_id)
            assert ent.confidence_score <= 0.70, (
                f"ETHICS-003: disputed entity confidence must not exceed 0.70, "
                f"got {ent.confidence_score} after sync"
            )
        finally:
            verify.close()
    finally:
        # Restore.
        restore = TestSession()
        try:
            ent = restore.get(GeoEntity, disputed_id)
            if ent is not None:
                ent.boundary_geojson = original_geom
                ent.confidence_score = original_conf
                restore.commit()
        finally:
            restore.close()
