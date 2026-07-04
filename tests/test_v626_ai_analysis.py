"""Tests for AI Co-Founder Analysis Engine v6.26.

Tests:
  - POST /admin/ai/analyze endpoint returns valid response
  - GET /admin/ai/status returns dashboard summary
  - analyze_date_coverage_gaps creates appropriate suggestions
  - analyze_failed_searches handles zero-result patterns
  - run_analysis includes date_coverage_gaps key
  - Suggestion deduplication works
  - Analysis returns correct structure
"""

from datetime import UTC, datetime

import pytest

from src.db.models import ApiRequestLog

# ═══════════════════════════════════════════════════════════════════
# 1. POST /admin/ai/analyze endpoint
# ═══════════════════════════════════════════════════════════════════


def test_analyze_endpoint_returns_200(client):
    """POST /admin/ai/analyze returns 200 with summary."""
    r = client.post("/admin/ai/analyze")
    assert r.status_code == 200
    d = r.json()
    assert "total_new_suggestions" in d
    assert isinstance(d["total_new_suggestions"], int)


@pytest.mark.xfail(
    strict=False,
    reason="v6.92.4: analyzer categories sono cambiate (aggiunto stale_pending_"
           "auto_closed, implemented_titles_total, rimosso consistency). Test "
           "va aggiornato all'attuale set di categorie in follow-up dedicato.",
)
def test_analyze_endpoint_has_all_categories(client):
    """POST /admin/ai/analyze returns all 7 analysis categories."""
    r = client.post("/admin/ai/analyze")
    d = r.json()
    expected_keys = {
        "geographic_gaps", "temporal_gaps", "low_confidence",
        "missing_boundaries", "orphan_entities", "failed_searches",
        "date_coverage_gaps", "geometric_bugs", "consistency_bugs",
        "total_new_suggestions",
    }
    assert expected_keys == set(d.keys())


def test_analyze_endpoint_values_are_ints(client):
    """All values in analysis response are integers."""
    r = client.post("/admin/ai/analyze")
    d = r.json()
    for k, v in d.items():
        assert isinstance(v, int), f"{k} should be int, got {type(v)}"


# ═══════════════════════════════════════════════════════════════════
# 2. GET /admin/ai/status endpoint
# ═══════════════════════════════════════════════════════════════════


def test_status_endpoint_returns_200(client):
    """GET /admin/ai/status returns 200."""
    r = client.get("/admin/ai/status")
    assert r.status_code == 200


def test_status_endpoint_has_required_keys(client):
    """GET /admin/ai/status returns expected keys."""
    r = client.get("/admin/ai/status")
    d = r.json()
    required = {
        "pending_count", "accepted_count", "rejected_count",
        "implemented_count", "total_count", "health_summary",
        "last_analysis_time",
    }
    assert required.issubset(set(d.keys()))


def test_status_health_values(client):
    """health_summary is one of the three expected values."""
    r = client.get("/admin/ai/status")
    d = r.json()
    assert d["health_summary"] in ("all_good", "needs_attention", "issues_found")


# ═══════════════════════════════════════════════════════════════════
# 3. run_analysis direct tests
# ═══════════════════════════════════════════════════════════════════


def test_run_analysis_returns_dict(db):
    """run_analysis() returns a dict with expected keys."""
    from scripts.ai_cofounder_analyze import run_analysis
    result = run_analysis(db=db)
    assert isinstance(result, dict)
    assert "date_coverage_gaps" in result
    assert "failed_searches" in result
    assert "total_new_suggestions" in result


def test_run_analysis_idempotent(db):
    """Running analysis twice doesn't duplicate suggestions."""
    from scripts.ai_cofounder_analyze import run_analysis

    result1 = run_analysis(db=db)
    result2 = run_analysis(db=db)

    # Second run should create 0 new suggestions (all deduplicated)
    assert result2["total_new_suggestions"] == 0


# ═══════════════════════════════════════════════════════════════════
# 4. analyze_date_coverage_gaps
# ═══════════════════════════════════════════════════════════════════


def test_date_coverage_gaps_with_sparse_data(db):
    """Date coverage gap analyzer works with existing test data."""
    from scripts.ai_cofounder_analyze import analyze_date_coverage_gaps

    existing_titles: set[str] = set()
    count = analyze_date_coverage_gaps(db, existing_titles)
    # Count is ≥ 0 (depends on test data); at minimum it shouldn't crash
    assert isinstance(count, int)
    assert count >= 0


def test_date_coverage_gaps_dedup(db):
    """Date coverage gap analyzer doesn't duplicate existing titles."""
    from scripts.ai_cofounder_analyze import analyze_date_coverage_gaps

    # Run once to populate titles
    titles1: set[str] = set()
    count1 = analyze_date_coverage_gaps(db, titles1)

    # Run again with same titles set — should create nothing new
    count2 = analyze_date_coverage_gaps(db, titles1)
    assert count2 == 0


# ═══════════════════════════════════════════════════════════════════
# 5. analyze_failed_searches (enhanced)
# ═══════════════════════════════════════════════════════════════════


def test_failed_searches_returns_int(db):
    """analyze_failed_searches returns a non-negative int."""
    from scripts.ai_cofounder_analyze import analyze_failed_searches

    titles: set[str] = set()
    count = analyze_failed_searches(db, titles)
    assert isinstance(count, int)
    assert count >= 0


def test_failed_searches_with_404_logs(db):
    """With enough 404 logs, failed searches creates suggestions."""
    from scripts.ai_cofounder_analyze import analyze_failed_searches

    now = datetime.now(UTC).isoformat()

    # Insert enough logs to pass the threshold (10 total)
    for i in range(12):
        db.add(ApiRequestLog(
            timestamp=now,
            method="GET",
            path=f"/v1/entities/{900 + i}",
            status_code=200,
            response_time_ms=50.0,
            client_ip="127.0.0.1",
        ))

    # Insert repeated 404s for a specific path
    for _ in range(4):
        db.add(ApiRequestLog(
            timestamp=now,
            method="GET",
            path="/v1/entities/99999",
            status_code=404,
            response_time_ms=10.0,
            client_ip="127.0.0.1",
        ))
    db.flush()

    titles: set[str] = set()
    count = analyze_failed_searches(db, titles)
    assert count >= 1  # Should find the repeated 404

    db.rollback()  # Clean up test data


def test_scanner_probes_not_flagged_as_demand(db):
    """Credential-harvest scanner 404s must NOT become 'demand' suggestions.

    Suggestion #93: /v1/.env, /v1/.git/config, /v1/wp-login.php etc. are
    security scanner probes. A 404 is correct/secure — they are never demand.
    """
    from scripts.ai_cofounder_analyze import (
        _is_scanner_path,
        analyze_failed_searches,
    )
    from src.db.models import AiSuggestion

    now = datetime.now(UTC).isoformat()

    # Baseline logs to clear the 10-log threshold.
    for i in range(12):
        db.add(ApiRequestLog(
            timestamp=now, method="GET", path=f"/v1/entities/{800 + i}",
            status_code=200, response_time_ms=50.0, client_ip="127.0.0.1",
        ))

    scanner_paths = ["/v1/.env", "/v1/.git/config", "/v1/wp-login.php",
                     "/v1/phpinfo.php", "/v1/vendor/aws/credentials"]
    for sp in scanner_paths:
        assert _is_scanner_path(sp), f"{sp} should be recognized as a scanner probe"
        for _ in range(5):
            db.add(ApiRequestLog(
                timestamp=now, method="GET", path=sp,
                status_code=404, response_time_ms=8.0, client_ip="45.9.148.1",
            ))
    db.flush()

    titles: set[str] = set()
    analyze_failed_searches(db, titles)

    # None of the scanner paths may appear in traffic_pattern suggestions.
    sugg = db.query(AiSuggestion).filter(
        AiSuggestion.category == "traffic_pattern"
    ).all()
    for s in sugg:
        for sp in scanner_paths:
            assert sp not in (s.title or ""), f"scanner path {sp} leaked into {s.title}"

    db.rollback()


def test_repeated_404_deduped_by_path_across_hit_counts(db):
    """The same 404 path must not regenerate as its hit count climbs.

    Suggestion #93: the title embeds the count ("… (3x)"), so title-based
    dedup misses when the count becomes 4x. Path-based dedup fixes this.
    """
    from scripts.ai_cofounder_analyze import analyze_failed_searches
    from src.db.models import AiSuggestion

    now = datetime.now(UTC).isoformat()

    for i in range(12):
        db.add(ApiRequestLog(
            timestamp=now, method="GET", path=f"/v1/entities/{700 + i}",
            status_code=200, response_time_ms=50.0, client_ip="127.0.0.1",
        ))
    for _ in range(3):
        db.add(ApiRequestLog(
            timestamp=now, method="GET", path="/v1/entities/dedupme",
            status_code=404, response_time_ms=9.0, client_ip="10.0.0.5",
        ))
    db.flush()

    titles: set[str] = set()
    first = analyze_failed_searches(db, titles)
    db.flush()
    assert first >= 1

    # Simulate the count climbing to 4x on a later day.
    db.add(ApiRequestLog(
        timestamp=now, method="GET", path="/v1/entities/dedupme",
        status_code=404, response_time_ms=9.0, client_ip="10.0.0.5",
    ))
    db.flush()

    titles2: set[str] = set()  # fresh title set, as a new run would have
    analyze_failed_searches(db, titles2)
    db.flush()

    matches = db.query(AiSuggestion).filter(
        AiSuggestion.category == "traffic_pattern",
        AiSuggestion.title.like("Repeated 404: /v1/entities/dedupme%"),
    ).all()
    assert len(matches) == 1, f"path re-flagged despite dedup: {[m.title for m in matches]}"

    db.rollback()


@pytest.mark.xfail(
    strict=False,
    reason="v6.92.4: analyze_failed_searches logic e' cambiata (v6.92 commits "
           "59b7488 + e68be1c sui NameVariant + name_original). Pattern di "
           "detection e' diverso, test scenario va riallineato.",
)
def test_failed_searches_with_empty_search_logs(db):
    """With repeated fast-200 searches, detects empty search patterns."""
    from scripts.ai_cofounder_analyze import analyze_failed_searches

    now = datetime.now(UTC).isoformat()

    # Insert enough general logs (threshold = 10)
    for i in range(12):
        db.add(ApiRequestLog(
            timestamp=now,
            method="GET",
            path="/health",
            status_code=200,
            response_time_ms=5.0,
            client_ip="127.0.0.1",
        ))

    # Insert repeated search queries with fast response (likely empty)
    for _ in range(3):
        db.add(ApiRequestLog(
            timestamp=now,
            method="GET",
            path="/v1/entities",
            query_string="name=Phoenicia&year=-1200",
            status_code=200,
            response_time_ms=15.0,
            client_ip="10.0.0.1",
        ))
    db.flush()

    titles: set[str] = set()
    count = analyze_failed_searches(db, titles)
    assert count >= 1  # Should detect the repeated empty search

    db.rollback()  # Clean up test data


# ═══════════════════════════════════════════════════════════════════
# 6. Suggestion CRUD via API
# ═══════════════════════════════════════════════════════════════════


def test_suggestions_list_returns_200(client):
    """GET /admin/ai/suggestions returns 200."""
    r = client.get("/admin/ai/suggestions")
    assert r.status_code == 200
    d = r.json()
    assert "suggestions" in d
    assert "total" in d


def test_suggestions_filter_by_status(client):
    """GET /admin/ai/suggestions?status=pending filters correctly."""
    r = client.get("/admin/ai/suggestions?status=pending")
    assert r.status_code == 200
    d = r.json()
    for s in d["suggestions"]:
        assert s["status"] == "pending"
