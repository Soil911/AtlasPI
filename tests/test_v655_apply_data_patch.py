"""v6.55: tests per apply_data_patch script."""

import json
import pytest

from scripts.apply_data_patch import apply_patches, PATCHABLE_FIELDS, RESOURCE_MAP
from src.db.models import GeoEntity, HistoricalEvent


def _cleanup(db):
    db.query(HistoricalEvent).delete()
    # Non delete GeoEntity — other tests have seeded data
    db.commit()


def test_patchable_fields_safe():
    """id and structural relations must NOT be patchable."""
    for resource in PATCHABLE_FIELDS:
        assert "id" not in PATCHABLE_FIELDS[resource]


def test_resource_map_complete():
    """All 5 resources mapped."""
    assert set(RESOURCE_MAP.keys()) == {"entity", "event", "site", "ruler", "language"}


def test_dry_run_no_write(db):
    """Dry run reports 'applied' count but does NOT write."""
    # Pick an arbitrary entity
    ent = db.query(GeoEntity).first()
    assert ent is not None
    original = ent.confidence_score

    patches = [{
        "resource": "entity",
        "id": ent.id,
        "field": "confidence_score",
        "new_value": 0.999,
        "rationale": "test-dry-run",
    }]
    stats = apply_patches(patches, dry_run=True)
    assert stats["applied"] == 1

    # Verify no write
    db.expire_all()
    ent2 = db.query(GeoEntity).filter(GeoEntity.id == ent.id).first()
    assert ent2.confidence_score == original


def test_skip_unchanged(db):
    """Patch with new_value == current is skipped_unchanged."""
    ent = db.query(GeoEntity).first()
    assert ent is not None
    current = ent.confidence_score

    patches = [{
        "resource": "entity",
        "id": ent.id,
        "field": "confidence_score",
        "new_value": current,
        "rationale": "idempotent",
    }]
    stats = apply_patches(patches, dry_run=True)
    assert stats["skipped_unchanged"] == 1
    assert stats["applied"] == 0


def test_skip_missing_entity(db):
    patches = [{
        "resource": "entity",
        "id": 9_999_999,
        "field": "year_end",
        "new_value": 2000,
        "rationale": "ghost",
    }]
    stats = apply_patches(patches, dry_run=True)
    assert stats["skipped_missing"] == 1


def test_skip_invalid_field(db):
    patches = [{
        "resource": "entity",
        "id": 1,
        "field": "id",  # NOT patchable (safety)
        "new_value": 999,
        "rationale": "evil",
    }]
    stats = apply_patches(patches, dry_run=True)
    assert stats["skipped_invalid_field"] == 1


def test_skip_invalid_resource(db):
    patches = [{
        "resource": "nuke",  # not a resource
        "id": 1,
        "field": "anything",
        "new_value": 0,
        "rationale": "x",
    }]
    stats = apply_patches(patches, dry_run=True)
    assert stats["skipped_invalid_field"] == 1


def test_apply_real_write(db):
    """Full flow — apply a patch, verify DB changed."""
    ent = db.query(GeoEntity).first()
    assert ent is not None
    original_ethical = ent.ethical_notes

    marker = "v6.55-test-marker-please-remove"
    patches = [{
        "resource": "entity",
        "id": ent.id,
        "field": "ethical_notes",
        "new_value": marker,
        "rationale": "test apply",
    }]
    stats = apply_patches(patches, dry_run=False)
    assert stats["applied"] == 1

    db.expire_all()
    ent2 = db.query(GeoEntity).filter(GeoEntity.id == ent.id).first()
    assert ent2.ethical_notes == marker

    # Restore
    ent2.ethical_notes = original_ethical
    db.commit()
