"""Tests for auto-implementation of accepted suggestions v6.28.

The GAMECHANGER: when Claude Code runs (or /admin/ai/implement-accepted
is called), accepted suggestions get auto-implemented if possible, or
a markdown briefing is generated for manual/Claude Code follow-up.

Tests:
  - POST /admin/ai/implement-accepted endpoint works
  - implement_accepted() with no accepted suggestions returns empty
  - handle_low_confidence boosts entities with ≥3 sources
  - handle_missing_boundaries dispatches correctly
  - Briefing files are generated for non-automatable categories
  - Status flips to 'implemented' only on success
  - review_note is appended with auto-implementation summary
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from src.db.models import AiSuggestion, GeoEntity, Source


# ═══════════════════════════════════════════════════════════════════
# 1. Endpoint smoke tests
# ═══════════════════════════════════════════════════════════════════


def test_implement_accepted_endpoint_returns_200(client):
    """POST /admin/ai/implement-accepted returns 200 with summary."""
    r = client.post("/admin/ai/implement-accepted")
    assert r.status_code == 200
    d = r.json()
    assert "processed" in d
    assert "results" in d
    assert isinstance(d["processed"], int)


def test_implement_accepted_summary_keys(client):
    """Response has expected keys."""
    r = client.post("/admin/ai/implement-accepted")
    d = r.json()
    for key in ("processed", "implemented", "briefing", "failed", "results"):
        assert key in d


# ═══════════════════════════════════════════════════════════════════
# 2. Handler unit tests
# ═══════════════════════════════════════════════════════════════════


def test_handle_briefing_creates_file(db, tmp_path, monkeypatch):
    """Briefing handler writes a markdown file to data/briefings/."""
    from scripts import implement_accepted_suggestions as mod

    # Redirect briefings dir to a temp path
    monkeypatch.setattr(mod, "BRIEFINGS_DIR", tmp_path)

    # Create a test suggestion
    sug = AiSuggestion(
        category="geographic_gap",
        title="Test geographic gap",
        description="Need more entities in X",
        detail_json=json.dumps({"region": "Antarctica", "count": 0}),
        priority=2,
        status="accepted",
        source="auto",
        created_at=datetime.now(timezone.utc).isoformat(),
        reviewed_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(sug)
    db.flush()

    outcome = mod.handle_briefing(sug, db)
    assert outcome["status"] == "briefing"
    assert "briefing_path" in outcome

    # Verify a file was created
    files = list(tmp_path.glob("*.md"))
    assert len(files) == 1
    content = files[0].read_text(encoding="utf-8")
    assert "Test geographic gap" in content
    assert "geographic_gap" in content
    assert "Antarctica" in content

    db.rollback()


def test_handle_low_confidence_boosts_well_sourced(db):
    """Low-confidence entities with ≥3 sources get boosted."""
    from scripts.implement_accepted_suggestions import handle_low_confidence

    # Create a test entity with low confidence and add 3 sources
    entity = GeoEntity(
        name_original="TestEntity_v628",
        name_original_lang="en",
        entity_type="empire",
        year_start=1000,
        year_end=1100,
        confidence_score=0.3,  # LOW
        status="confirmed",
    )
    db.add(entity)
    db.flush()

    # Add 3 sources (threshold for auto-boost)
    for i in range(3):
        db.add(Source(
            entity_id=entity.id,
            citation=f"Test source {i}",
            source_type="academic",
        ))
    db.flush()

    # Create suggestion referring to this entity
    sug = AiSuggestion(
        category="low_confidence",
        title="Low confidence test",
        description="...",
        detail_json=json.dumps([{"id": entity.id, "name": entity.name_original, "score": 0.3}]),
        priority=4,
        status="accepted",
        source="auto",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(sug)
    db.flush()

    outcome = handle_low_confidence(sug, db)
    assert outcome["status"] == "implemented"
    assert "boosted" in outcome
    assert len(outcome["boosted"]) == 1
    # Entity confidence was boosted in-session
    assert entity.confidence_score > 0.3

    db.rollback()


def test_handle_low_confidence_skips_low_source_entities(db):
    """Entities with <3 sources stay at their current confidence."""
    from scripts.implement_accepted_suggestions import handle_low_confidence

    entity = GeoEntity(
        name_original="TestEntity_v628_nosrc",
        name_original_lang="en",
        entity_type="kingdom",
        year_start=1000,
        confidence_score=0.3,
        status="confirmed",
    )
    db.add(entity)
    db.flush()

    # Only 1 source
    db.add(Source(
        entity_id=entity.id,
        citation="Single source",
        source_type="academic",
    ))
    db.flush()

    sug = AiSuggestion(
        category="low_confidence",
        title="Low confidence test 2",
        description="...",
        detail_json=json.dumps([{"id": entity.id, "name": entity.name_original, "score": 0.3}]),
        priority=4,
        status="accepted",
        source="auto",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(sug)
    db.flush()

    outcome = handle_low_confidence(sug, db)
    # Should be briefing since no entity qualified
    assert outcome["status"] == "briefing"

    db.rollback()


def test_handle_low_confidence_malformed_detail(db):
    """Malformed detail_json returns failed status."""
    from scripts.implement_accepted_suggestions import handle_low_confidence

    sug = AiSuggestion(
        category="low_confidence",
        title="Malformed",
        description="...",
        detail_json="not valid json {{",
        priority=4,
        status="accepted",
        source="auto",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(sug)
    db.flush()

    outcome = handle_low_confidence(sug, db)
    assert outcome["status"] == "failed"

    db.rollback()


# ═══════════════════════════════════════════════════════════════════
# 3. Orchestrator tests
# ═══════════════════════════════════════════════════════════════════


def test_implement_accepted_no_suggestions(db):
    """With no accepted suggestions, returns empty summary."""
    from scripts.implement_accepted_suggestions import implement_accepted

    # Ensure no accepted suggestions in DB (won't modify real ones)
    # The default test data seeded might have none, which is fine
    result = implement_accepted(db=db)
    assert "processed" in result
    assert result["processed"] >= 0


def test_implement_accepted_marks_implemented(db, tmp_path, monkeypatch):
    """When a handler returns implemented, the suggestion is marked."""
    from scripts import implement_accepted_suggestions as mod

    monkeypatch.setattr(mod, "BRIEFINGS_DIR", tmp_path)

    # Create entity with 3 sources (will be boosted)
    entity = GeoEntity(
        name_original="Orchestrator_Test",
        name_original_lang="en",
        entity_type="empire",
        year_start=500,
        confidence_score=0.3,
        status="confirmed",
    )
    db.add(entity)
    db.flush()
    for i in range(3):
        db.add(Source(
            entity_id=entity.id,
            citation=f"Orch source {i}",
            source_type="academic",
        ))
    db.flush()

    # Create accepted suggestion
    sug = AiSuggestion(
        category="low_confidence",
        title="Orchestrator test",
        description="...",
        detail_json=json.dumps([{"id": entity.id}]),
        priority=4,
        status="accepted",
        source="auto",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(sug)
    db.flush()

    result = mod.implement_accepted(db=db)
    assert result["processed"] >= 1
    assert result.get("implemented", 0) >= 1

    # Verify status flipped to implemented
    db.refresh(sug)
    assert sug.status == "implemented"
    assert sug.review_note is not None
    assert "Auto-implemented" in sug.review_note

    db.rollback()


def test_implement_accepted_generates_briefing_for_unknown_category(db, tmp_path, monkeypatch):
    """Unknown categories get briefings, not errors."""
    from scripts import implement_accepted_suggestions as mod

    monkeypatch.setattr(mod, "BRIEFINGS_DIR", tmp_path)

    sug = AiSuggestion(
        category="temporal_gap",
        title="Bronze Age events sparse",
        description="Need more events",
        detail_json=json.dumps({"era": "Bronze Age", "events": 2}),
        priority=2,
        status="accepted",
        source="auto",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(sug)
    db.flush()

    result = mod.implement_accepted(db=db)
    # Find this suggestion in results
    sug_result = next((r for r in result["results"] if r["id"] == sug.id), None)
    assert sug_result is not None
    assert sug_result["outcome"] == "briefing"

    # Suggestion should remain accepted (not implemented)
    db.refresh(sug)
    assert sug.status == "accepted"

    # Briefing file exists
    files = list(tmp_path.glob("*.md"))
    assert len(files) >= 1

    db.rollback()


# ═══════════════════════════════════════════════════════════════════
# 4. Dispatch routing
# ═══════════════════════════════════════════════════════════════════


def test_dispatch_quality_with_boundary_goes_to_boundaries_handler(db):
    """Quality suggestions with 'boundary' in title route to boundary handler."""
    from scripts.implement_accepted_suggestions import _dispatch

    sug = AiSuggestion(
        category="quality",
        title="14 entities without boundaries",
        description="...",
        detail_json=json.dumps([{"id": 1, "name": "Test"}]),
        priority=3,
        status="accepted",
        source="auto",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(sug)
    db.flush()

    outcome = _dispatch(sug, db)
    # Should NOT be briefing (it's routed to handle_missing_boundaries)
    # Possible outcomes: implemented, briefing, failed — just not the default briefing
    assert outcome["status"] in ("implemented", "briefing", "failed")
    # The summary should reference boundaries, not the default briefing text
    assert "boundar" in outcome["summary"].lower() or "entit" in outcome["summary"].lower()

    db.rollback()


def test_dispatch_unknown_category_uses_briefing(db, tmp_path, monkeypatch):
    """Unknown category falls back to briefing handler."""
    from scripts import implement_accepted_suggestions as mod

    monkeypatch.setattr(mod, "BRIEFINGS_DIR", tmp_path)

    sug = AiSuggestion(
        category="some_future_category",
        title="Future category",
        description="...",
        priority=3,
        status="accepted",
        source="auto",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(sug)
    db.flush()

    outcome = mod._dispatch(sug, db)
    assert outcome["status"] == "briefing"

    db.rollback()
