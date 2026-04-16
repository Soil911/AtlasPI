"""Test per Entity Comparison Tool — v6.18.

Verifica:
- /v1/compare?ids=... API endpoint (validazione, risposta, overlap, eventi, catene)
- /compare pagina HTML
- Cache headers
"""


# ── API endpoint tests ───────────────────────────────────────────


def test_compare_two_entities(client):
    """Compare two valid entity IDs returns structured comparison."""
    r = client.get("/v1/compare?ids=1,2")
    assert r.status_code == 200
    d = r.json()
    assert "entities" in d
    assert len(d["entities"]) == 2
    assert "events_by_entity" in d
    assert "chains_by_entity" in d
    assert "overlap" in d
    assert "common_events" in d


def test_compare_three_entities(client):
    """Compare three valid entity IDs."""
    r = client.get("/v1/compare?ids=1,2,3")
    assert r.status_code == 200
    d = r.json()
    assert len(d["entities"]) == 3
    # Pairwise overlap should have 3 pairs for 3 entities
    assert len(d["overlap"]["pairwise"]) == 3


def test_compare_invalid_id_returns_404(client):
    """Non-existent entity IDs return 404."""
    r = client.get("/v1/compare?ids=1,999999")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


def test_compare_too_many_ids_returns_422(client):
    """More than 4 IDs return 422."""
    r = client.get("/v1/compare?ids=1,2,3,4,5")
    assert r.status_code == 422
    assert "Maximum 4" in r.json()["detail"]


def test_compare_single_id_returns_422(client):
    """Only 1 ID returns 422 (need at least 2)."""
    r = client.get("/v1/compare?ids=1")
    assert r.status_code == 422
    assert "at least 2" in r.json()["detail"].lower()


def test_compare_non_integer_ids_returns_422(client):
    """Non-integer IDs return 422."""
    r = client.get("/v1/compare?ids=abc,def")
    assert r.status_code == 422


def test_compare_entity_detail_fields(client):
    """Each entity in the response has the expected fields."""
    r = client.get("/v1/compare?ids=1,2")
    d = r.json()
    e = d["entities"][0]
    required = [
        "id", "name_original", "entity_type", "year_start",
        "duration_years", "confidence_score", "status",
        "has_boundary", "sources_count",
    ]
    for field in required:
        assert field in e, f"Missing field: {field}"


def test_compare_overlap_structure(client):
    """Overlap contains global and pairwise data."""
    r = client.get("/v1/compare?ids=1,2")
    d = r.json()
    ov = d["overlap"]
    assert "all" in ov
    assert "years" in ov["all"]
    assert "pairwise" in ov
    assert len(ov["pairwise"]) == 1  # 2 entities = 1 pair


def test_compare_events_by_entity_keys(client):
    """events_by_entity uses string entity IDs as keys."""
    r = client.get("/v1/compare?ids=1,2")
    d = r.json()
    for e in d["entities"]:
        assert str(e["id"]) in d["events_by_entity"]


def test_compare_chains_by_entity_keys(client):
    """chains_by_entity uses string entity IDs as keys."""
    r = client.get("/v1/compare?ids=1,2")
    d = r.json()
    for e in d["entities"]:
        assert str(e["id"]) in d["chains_by_entity"]


def test_compare_cache_header(client):
    """Response includes Cache-Control header."""
    r = client.get("/v1/compare?ids=1,2")
    assert r.status_code == 200
    assert "max-age" in r.headers.get("cache-control", "").lower()


def test_compare_deduplicates_ids(client):
    """Duplicate IDs are deduplicated; 1,1 returns 422 (< 2 distinct)."""
    r = client.get("/v1/compare?ids=1,1")
    assert r.status_code == 422
    assert "distinct" in r.json()["detail"].lower()


# ── HTML page test ───────────────────────────────────────────


def test_compare_page_returns_html(client):
    """GET /compare returns the HTML comparison page."""
    r = client.get("/compare")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")


def test_compare_page_has_compare_js(client):
    """The comparison page loads compare.js."""
    r = client.get("/compare")
    assert b"compare.js" in r.content
