"""Tests for v6.16 AI Co-Founder Dashboard.

Covers:
- AiSuggestion model CRUD
- API endpoints (list, accept, reject, implement, status)
- HTML dashboard serving
- Analysis script logic
- Deduplication
- Filtering and ordering
"""

from datetime import datetime, timezone

from src.db.models import AiSuggestion


# ═══════════════════════════════════════════════════════════════════
# Model CRUD
# ═══════════════════════════════════════════════════════════════════


def test_create_suggestion(db):
    """Create an AiSuggestion and verify fields."""
    s = AiSuggestion(
        category="geographic_gap",
        title="Test: Add Oceania entities",
        description="Oceania has fewer entities than other regions.",
        priority=3,
        status="pending",
        source="auto",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(s)
    db.commit()
    db.refresh(s)

    assert s.id is not None
    assert s.category == "geographic_gap"
    assert s.status == "pending"
    assert s.priority == 3
    assert s.source == "auto"
    assert s.reviewed_at is None


def test_update_suggestion_status(db):
    """Update suggestion status to accepted."""
    s = AiSuggestion(
        category="temporal_gap",
        title="Test: Events for Pre-3000 BCE",
        description="No events in Pre-3000 BCE.",
        priority=2,
        status="pending",
        source="auto",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(s)
    db.commit()

    s.status = "accepted"
    s.reviewed_at = datetime.now(timezone.utc).isoformat()
    s.review_note = "Will add Sumerian events"
    db.commit()
    db.refresh(s)

    assert s.status == "accepted"
    assert s.reviewed_at is not None
    assert s.review_note == "Will add Sumerian events"


def test_suggestion_with_detail_json(db):
    """Suggestion can store detail_json."""
    s = AiSuggestion(
        category="quality",
        title="Test: Entities without boundaries detail",
        description="3 entities lack boundaries.",
        priority=3,
        status="pending",
        source="auto",
        created_at=datetime.now(timezone.utc).isoformat(),
        detail_json='[{"id": 1, "name": "Test Entity"}]',
    )
    db.add(s)
    db.commit()
    db.refresh(s)

    assert s.detail_json is not None
    assert "Test Entity" in s.detail_json


def test_delete_suggestion(db):
    """Delete a suggestion."""
    s = AiSuggestion(
        category="low_confidence",
        title="Test: Delete me",
        description="Temporary suggestion.",
        priority=5,
        status="pending",
        source="manual",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(s)
    db.commit()
    sid = s.id

    db.delete(s)
    db.commit()

    assert db.query(AiSuggestion).filter(AiSuggestion.id == sid).first() is None


# ═══════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════


def _seed_suggestions(db):
    """Insert test suggestions for API tests."""
    # Clean up any existing test suggestions
    db.query(AiSuggestion).filter(AiSuggestion.title.like("API-Test:%")).delete(synchronize_session=False)
    db.commit()

    suggestions = [
        AiSuggestion(
            category="geographic_gap", title="API-Test: Geographic gap Americas",
            description="Americas has few entities.", priority=2, status="pending",
            source="auto", created_at="2026-04-16T10:00:00+00:00",
        ),
        AiSuggestion(
            category="temporal_gap", title="API-Test: Temporal gap Pre-3000",
            description="No events in Pre-3000 BCE.", priority=1, status="pending",
            source="auto", created_at="2026-04-16T09:00:00+00:00",
        ),
        AiSuggestion(
            category="quality", title="API-Test: Low confidence entities",
            description="Some entities below 0.4.", priority=4, status="accepted",
            source="auto", created_at="2026-04-15T10:00:00+00:00",
            reviewed_at="2026-04-16T11:00:00+00:00",
        ),
        AiSuggestion(
            category="missing_chain", title="API-Test: Orphan entities",
            description="800 entities not in chains.", priority=5, status="rejected",
            source="auto", created_at="2026-04-14T10:00:00+00:00",
            reviewed_at="2026-04-15T10:00:00+00:00", review_note="Not a priority now",
        ),
        AiSuggestion(
            category="traffic_pattern", title="API-Test: 404 on /v1/entity/9999",
            description="Path queried 5 times.", priority=3, status="implemented",
            source="auto", created_at="2026-04-13T10:00:00+00:00",
            reviewed_at="2026-04-14T10:00:00+00:00",
        ),
    ]
    for s in suggestions:
        db.add(s)
    db.commit()


def test_list_suggestions_returns_200(client, db):
    _seed_suggestions(db)
    r = client.get("/admin/ai/suggestions")
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)


def test_list_suggestions_has_fields(client, db):
    _seed_suggestions(db)
    r = client.get("/admin/ai/suggestions")
    data = r.json()
    if data["suggestions"]:
        s = data["suggestions"][0]
        for field in ["id", "category", "title", "description", "priority", "status", "source", "created_at"]:
            assert field in s, f"Missing field: {field}"


def test_list_filter_by_status_pending(client, db):
    _seed_suggestions(db)
    r = client.get("/admin/ai/suggestions?status=pending")
    data = r.json()
    for s in data["suggestions"]:
        assert s["status"] == "pending"


def test_list_filter_by_status_accepted(client, db):
    _seed_suggestions(db)
    r = client.get("/admin/ai/suggestions?status=accepted")
    data = r.json()
    for s in data["suggestions"]:
        assert s["status"] == "accepted"


def test_list_filter_by_status_rejected(client, db):
    _seed_suggestions(db)
    r = client.get("/admin/ai/suggestions?status=rejected")
    data = r.json()
    for s in data["suggestions"]:
        assert s["status"] == "rejected"


def test_list_priority_ordering(client, db):
    """Suggestions should be sorted by priority asc (critical first)."""
    _seed_suggestions(db)
    r = client.get("/admin/ai/suggestions")
    data = r.json()
    sugs = data["suggestions"]
    if len(sugs) >= 2:
        priorities = [s["priority"] for s in sugs]
        assert priorities == sorted(priorities), "Suggestions should be ordered by priority"


def test_list_with_limit_and_offset(client, db):
    _seed_suggestions(db)
    r = client.get("/admin/ai/suggestions?limit=2&offset=0")
    data = r.json()
    assert len(data["suggestions"]) <= 2


def test_accept_suggestion(client, db):
    _seed_suggestions(db)
    # Find a pending suggestion
    pending = db.query(AiSuggestion).filter(
        AiSuggestion.status == "pending",
        AiSuggestion.title.like("API-Test:%"),
    ).first()
    assert pending is not None

    r = client.post(f"/admin/ai/suggestions/{pending.id}/accept")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "accepted"
    assert data["reviewed_at"] is not None


def test_reject_suggestion(client, db):
    _seed_suggestions(db)
    pending = db.query(AiSuggestion).filter(
        AiSuggestion.status == "pending",
        AiSuggestion.title.like("API-Test:%"),
    ).first()
    assert pending is not None

    r = client.post(f"/admin/ai/suggestions/{pending.id}/reject?note=Not%20useful")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "rejected"
    assert data["review_note"] == "Not useful"


def test_implement_suggestion(client, db):
    _seed_suggestions(db)
    accepted = db.query(AiSuggestion).filter(
        AiSuggestion.status == "accepted",
        AiSuggestion.title.like("API-Test:%"),
    ).first()
    assert accepted is not None

    r = client.post(f"/admin/ai/suggestions/{accepted.id}/implement")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "implemented"


def test_action_on_nonexistent_returns_404(client):
    r = client.post("/admin/ai/suggestions/999999/accept")
    assert r.status_code == 404


def test_ai_status_returns_200(client, db):
    _seed_suggestions(db)
    r = client.get("/admin/ai/status")
    assert r.status_code == 200
    data = r.json()
    for field in ["pending_count", "accepted_count", "rejected_count", "implemented_count", "health_summary", "total_count"]:
        assert field in data, f"Missing field: {field}"


def test_ai_status_health_summary_values(client, db):
    """Health summary should be one of the valid values."""
    r = client.get("/admin/ai/status")
    data = r.json()
    assert data["health_summary"] in ("all_good", "needs_attention", "issues_found")


def test_ai_status_counts_are_integers(client, db):
    r = client.get("/admin/ai/status")
    data = r.json()
    assert isinstance(data["pending_count"], int)
    assert isinstance(data["accepted_count"], int)
    assert isinstance(data["rejected_count"], int)
    assert isinstance(data["implemented_count"], int)
    assert isinstance(data["total_count"], int)


# ═══════════════════════════════════════════════════════════════════
# HTML Dashboard
# ═══════════════════════════════════════════════════════════════════


def test_brief_returns_200(client):
    r = client.get("/admin/brief")
    assert r.status_code == 200


def test_brief_returns_html(client):
    r = client.get("/admin/brief")
    assert "text/html" in r.headers.get("content-type", "")


def test_brief_contains_title(client):
    r = client.get("/admin/brief")
    assert "Co-Founder Brief" in r.text


# ═══════════════════════════════════════════════════════════════════
# Analysis Script Logic
# ═══════════════════════════════════════════════════════════════════


def test_analysis_can_run(db):
    """The analysis script can run without errors."""
    from scripts.ai_cofounder_analyze import run_analysis
    results = run_analysis(db)
    assert "total_new_suggestions" in results
    assert isinstance(results["total_new_suggestions"], int)


def test_analysis_dedup(db):
    """Running analysis twice should not duplicate suggestions."""
    from scripts.ai_cofounder_analyze import run_analysis

    # First run
    results1 = run_analysis(db)
    n1 = results1["total_new_suggestions"]

    # Second run — same data, should produce 0 new
    results2 = run_analysis(db)
    n2 = results2["total_new_suggestions"]

    assert n2 == 0, f"Dedup failed: second run created {n2} suggestions (first run: {n1})"


def test_analysis_returns_all_categories(db):
    """Analysis result contains all expected category keys."""
    from scripts.ai_cofounder_analyze import run_analysis
    results = run_analysis(db)

    expected_keys = [
        "geographic_gaps", "temporal_gaps", "low_confidence",
        "missing_boundaries", "orphan_entities", "failed_searches",
    ]
    for key in expected_keys:
        assert key in results, f"Missing analysis category: {key}"


def test_analysis_helper_lat_to_continent():
    """Test the continent assignment helper."""
    from scripts.ai_cofounder_analyze import _lat_to_continent
    assert _lat_to_continent(48.8, 2.3) == "Europe"  # Paris
    assert _lat_to_continent(35.7, 139.7) == "Asia (East/Southeast)"  # Tokyo
    assert _lat_to_continent(None, None) == "Unknown"


def test_analysis_helper_year_to_era():
    """Test the era assignment helper."""
    from scripts.ai_cofounder_analyze import _year_to_era
    assert _year_to_era(-4000) == "Pre-3000 BCE"
    assert _year_to_era(-500) == "500-1 BCE"
    assert _year_to_era(100) == "1-500 CE"
    assert _year_to_era(1789) == "1500-1800 CE"
    assert _year_to_era(2024) == "2000-present"


# ═══════════════════════════════════════════════════════════════════
# Edge Cases
# ═══════════════════════════════════════════════════════════════════


def test_suggestion_categories_valid(db):
    """All suggestions in DB should have valid categories."""
    valid = {"geographic_gap", "temporal_gap", "quality", "traffic_pattern",
             "missing_entity", "missing_chain", "low_confidence",
             "search_demand", "date_coverage", "geometric_bug"}
    sugs = db.query(AiSuggestion.category).distinct().all()
    for (cat,) in sugs:
        assert cat in valid, f"Invalid category: {cat}"


def test_suggestion_statuses_valid(db):
    """All suggestions in DB should have valid statuses."""
    valid = {"pending", "accepted", "rejected", "implemented"}
    sugs = db.query(AiSuggestion.status).distinct().all()
    for (st,) in sugs:
        assert st in valid, f"Invalid status: {st}"


def test_suggestion_priorities_valid(db):
    """All suggestion priorities should be 1-5."""
    sugs = db.query(AiSuggestion.priority).distinct().all()
    for (p,) in sugs:
        assert 1 <= p <= 5, f"Invalid priority: {p}"
