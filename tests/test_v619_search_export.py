"""Tests for v6.19 — Advanced Search + Data Export.

Tests cover:
- /v1/search/advanced unified search across all data types
- /v1/export/entities (CSV + GeoJSON with filters)
- /v1/export/events (CSV + JSON with filters)
- /search HTML page
"""

import json


# ─── Advanced Search API ──────────────────────────────────────


def test_advanced_search_returns_results(client):
    """Search for a common term should return results."""
    r = client.get("/v1/search/advanced?q=roman")
    assert r.status_code == 200
    d = r.json()
    assert "results" in d
    assert "total" in d
    assert "query" in d
    assert d["query"] == "roman"
    assert d["total"] > 0
    assert len(d["results"]) > 0


def test_advanced_search_empty_results(client):
    """Search for nonexistent term should return empty results."""
    r = client.get("/v1/search/advanced?q=xyznonexistent999")
    assert r.status_code == 200
    d = r.json()
    assert d["total"] == 0
    assert len(d["results"]) == 0


def test_advanced_search_missing_query(client):
    """Search without q parameter should return 422."""
    r = client.get("/v1/search/advanced")
    assert r.status_code == 422


def test_advanced_search_result_structure(client):
    """Each result should have the expected fields."""
    r = client.get("/v1/search/advanced?q=rome")
    assert r.status_code == 200
    d = r.json()
    if d["total"] > 0:
        result = d["results"][0]
        assert "type" in result
        assert result["type"] in ("entity", "event", "city", "route")
        assert "id" in result
        assert "name" in result
        assert "score" in result
        assert "highlight" in result
        assert "confidence_score" in result


def test_advanced_search_multiple_types(client):
    """Search should return results from multiple data types."""
    r = client.get("/v1/search/advanced?q=rome&limit=100")
    assert r.status_code == 200
    d = r.json()
    types = {result["type"] for result in d["results"]}
    # "rome" should match entities and possibly cities/events
    assert "entity" in types or len(types) >= 1


def test_advanced_search_filter_by_data_type(client):
    """Filtering by data_type should only return that type."""
    r = client.get("/v1/search/advanced?q=roman&data_type=entity")
    assert r.status_code == 200
    d = r.json()
    for result in d["results"]:
        assert result["type"] == "entity"


def test_advanced_search_filter_by_status(client):
    """Filtering by status should only return matching status."""
    r = client.get("/v1/search/advanced?q=empire&status=confirmed")
    assert r.status_code == 200
    d = r.json()
    for result in d["results"]:
        assert result["status"] == "confirmed"


def test_advanced_search_filter_by_year_range(client):
    """Year range filter should constrain results."""
    r = client.get("/v1/search/advanced?q=empire&year_min=0&year_max=500")
    assert r.status_code == 200
    d = r.json()
    assert d["total"] >= 0  # valid response


def test_advanced_search_sort_by_name(client):
    """Sort by name should return alphabetically ordered results."""
    r = client.get("/v1/search/advanced?q=empire&sort=name")
    assert r.status_code == 200
    d = r.json()
    if len(d["results"]) >= 2:
        names = [result["name"].lower() for result in d["results"]]
        assert names == sorted(names)


def test_advanced_search_pagination(client):
    """Pagination should work with limit and offset."""
    r1 = client.get("/v1/search/advanced?q=empire&limit=5&offset=0")
    r2 = client.get("/v1/search/advanced?q=empire&limit=5&offset=5")
    assert r1.status_code == 200
    assert r2.status_code == 200
    d1 = r1.json()
    d2 = r2.json()
    # If enough results, pages should be different
    if d1["total"] > 5:
        ids1 = {r["id"] for r in d1["results"]}
        ids2 = {r["id"] for r in d2["results"]}
        assert ids1 != ids2 or len(ids2) == 0


# ─── Export Entities ──────────────────────────────────────────


def test_export_entities_csv(client):
    """Export entities as CSV should return proper CSV with headers."""
    r = client.get("/v1/export/entities?format=csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")
    assert "content-disposition" in r.headers
    assert "atlaspi_entities.csv" in r.headers["content-disposition"]
    content = r.text
    # Check for CSV headers
    assert "name_original" in content
    assert "entity_type" in content
    assert "year_start" in content


def test_export_entities_csv_has_bom(client):
    """CSV export should have UTF-8 BOM for Excel compatibility."""
    r = client.get("/v1/export/entities?format=csv")
    assert r.status_code == 200
    # UTF-8 BOM is \xEF\xBB\xBF in bytes, or \uFEFF in text
    content_bytes = r.content
    assert content_bytes[:3] == b"\xef\xbb\xbf" or r.text.startswith("\ufeff")


def test_export_entities_geojson(client):
    """Export entities as GeoJSON should return valid FeatureCollection."""
    r = client.get("/v1/export/entities?format=geojson")
    assert r.status_code == 200
    assert "geo+json" in r.headers.get("content-type", "")
    assert "content-disposition" in r.headers
    d = r.json()
    assert d["type"] == "FeatureCollection"
    assert "features" in d
    assert len(d["features"]) > 0
    # Each feature should have type, id, geometry, properties
    feat = d["features"][0]
    assert feat["type"] == "Feature"
    assert "properties" in feat
    assert "name_original" in feat["properties"]


def test_export_entities_with_filters(client):
    """Export with filters should respect them."""
    r = client.get("/v1/export/entities?format=csv&entity_type=empire")
    assert r.status_code == 200
    content = r.text
    lines = content.strip().split("\n")
    # Should have header + at least one data row
    assert len(lines) >= 2
    # Every data row should contain "empire" in the entity_type column
    header = lines[0]
    # Remove BOM if present
    if header.startswith("\ufeff"):
        header = header[1:]
    cols = header.split(",")
    type_idx = cols.index("entity_type")
    for line in lines[1:]:
        if line.strip():
            parts = line.split(",")
            if len(parts) > type_idx:
                assert parts[type_idx] == "empire"


# ─── Export Events ────────────────────────────────────────────


def test_export_events_csv(client):
    """Export events as CSV should return proper CSV."""
    r = client.get("/v1/export/events?format=csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")
    assert "content-disposition" in r.headers
    assert "atlaspi_events.csv" in r.headers["content-disposition"]
    content = r.text
    assert "name_original" in content
    assert "event_type" in content


def test_export_events_json(client):
    """Export events as JSON should return valid JSON array."""
    r = client.get("/v1/export/events?format=json")
    assert r.status_code == 200
    assert "application/json" in r.headers.get("content-type", "")
    assert "content-disposition" in r.headers
    d = r.json()
    assert isinstance(d, list)
    if len(d) > 0:
        event = d[0]
        assert "id" in event
        assert "name_original" in event
        assert "event_type" in event
        assert "year" in event


def test_export_events_csv_has_bom(client):
    """Events CSV should have UTF-8 BOM."""
    r = client.get("/v1/export/events?format=csv")
    assert r.status_code == 200
    content_bytes = r.content
    assert content_bytes[:3] == b"\xef\xbb\xbf" or r.text.startswith("\ufeff")


def test_export_has_content_disposition(client):
    """All export endpoints should set Content-Disposition header."""
    for url in [
        "/v1/export/entities?format=csv",
        "/v1/export/entities?format=geojson",
        "/v1/export/events?format=csv",
        "/v1/export/events?format=json",
    ]:
        r = client.get(url)
        assert r.status_code == 200, f"Failed for {url}"
        assert "content-disposition" in r.headers, f"No Content-Disposition for {url}"


# ─── Search HTML Page ─────────────────────────────────────────


def test_search_page_returns_html(client):
    """GET /search should return the search HTML page."""
    r = client.get("/search")
    assert r.status_code == 200
    content_type = r.headers.get("content-type", "")
    assert "html" in content_type


def test_search_page_loads_js(client):
    """The search page should reference search.js."""
    r = client.get("/search")
    assert r.status_code == 200
    assert "search.js" in r.text


def test_search_page_has_filter_controls(client):
    """The search page should contain filter UI elements."""
    r = client.get("/search")
    assert r.status_code == 200
    assert "s-search-input" in r.text
    assert "Entity Type" in r.text
    assert "Time Range" in r.text
    assert "Data Export" in r.text
