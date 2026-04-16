"""Tests for v6.17 Timeline Visualization.

Covers:
- /v1/timeline-data endpoint (JSON structure, cache headers)
- /timeline HTML page (200 response)
- Data shape validation (entities, events, chains)
"""


def test_timeline_data_returns_200(client):
    """GET /v1/timeline-data returns 200 with JSON body."""
    r = client.get("/v1/timeline-data")
    assert r.status_code == 200
    d = r.json()
    assert "entities" in d
    assert "events" in d
    assert "chains" in d


def test_timeline_data_entities_structure(client):
    """Entities array has required fields for timeline rendering."""
    r = client.get("/v1/timeline-data")
    entities = r.json()["entities"]
    assert len(entities) > 0
    e = entities[0]
    assert "id" in e
    assert "name" in e
    assert "type" in e
    assert "year_start" in e
    assert "year_end" in e  # may be None but key must exist
    assert "confidence" in e


def test_timeline_data_entities_no_heavy_fields(client):
    """Entities must NOT include heavy fields like boundary_geojson or description."""
    r = client.get("/v1/timeline-data")
    entities = r.json()["entities"]
    for e in entities[:10]:
        assert "boundary_geojson" not in e
        assert "description" not in e
        assert "sources" not in e


def test_timeline_data_events_structure(client):
    """Events array has required temporal + type fields."""
    r = client.get("/v1/timeline-data")
    events = r.json()["events"]
    assert len(events) > 0
    ev = events[0]
    assert "id" in ev
    assert "name" in ev
    assert "type" in ev
    assert "year" in ev
    assert "confidence" in ev


def test_timeline_data_events_date_precision(client):
    """Events include date precision fields from v6.14."""
    r = client.get("/v1/timeline-data")
    events = r.json()["events"]
    assert len(events) > 0
    ev = events[0]
    # Keys must exist (values may be None)
    assert "month" in ev
    assert "day" in ev
    assert "precision" in ev


def test_timeline_data_chains_structure(client):
    """Chains array has required fields with links."""
    r = client.get("/v1/timeline-data")
    chains = r.json()["chains"]
    assert len(chains) > 0
    ch = chains[0]
    assert "id" in ch
    assert "name" in ch
    assert "type" in ch
    assert "links" in ch
    assert isinstance(ch["links"], list)


def test_timeline_data_chain_links_structure(client):
    """Chain links include transition info for timeline rendering."""
    r = client.get("/v1/timeline-data")
    chains = r.json()["chains"]
    # Find a chain with links
    chain_with_links = None
    for ch in chains:
        if len(ch.get("links", [])) > 0:
            chain_with_links = ch
            break
    assert chain_with_links is not None, "Expected at least one chain with links"
    lk = chain_with_links["links"][0]
    assert "entity_id" in lk
    assert "entity_name" in lk
    assert "sequence" in lk
    assert "violent" in lk


def test_timeline_data_chain_links_transition(client):
    """Non-first chain links include transition type and year."""
    r = client.get("/v1/timeline-data")
    chains = r.json()["chains"]
    for ch in chains:
        links = ch.get("links", [])
        if len(links) >= 2:
            # Second link should have transition info
            lk = links[1]
            assert "transition" in lk
            assert "year" in lk
            assert "violent" in lk
            return
    # If no chain has 2+ links, skip
    assert True


def test_timeline_data_cache_header(client):
    """Response must include Cache-Control header."""
    r = client.get("/v1/timeline-data")
    assert "cache-control" in r.headers
    assert "max-age" in r.headers["cache-control"]


def test_timeline_page_returns_html(client):
    """/timeline returns 200 with HTML content."""
    r = client.get("/timeline")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")


def test_timeline_page_contains_svg(client):
    """/timeline HTML includes the SVG canvas element."""
    r = client.get("/timeline")
    assert b"tl-svg" in r.content


def test_timeline_page_contains_controls(client):
    """/timeline HTML includes timeline controls."""
    r = client.get("/timeline")
    body = r.content
    assert b"layer-entities" in body
    assert b"layer-events" in body
    assert b"layer-chains" in body
    assert b"zoom-slider" in body
    assert b"tl-search-input" in body


def test_timeline_data_entity_types_present(client):
    """Multiple entity types should be present for color-coded rendering."""
    r = client.get("/v1/timeline-data")
    entities = r.json()["entities"]
    types = set(e["type"] for e in entities)
    # At least 3 different types
    assert len(types) >= 3


def test_timeline_data_entities_year_range(client):
    """Entities should span a wide historical range (BCE to CE)."""
    r = client.get("/v1/timeline-data")
    entities = r.json()["entities"]
    years = [e["year_start"] for e in entities]
    assert min(years) < 0, "Expected some BCE entities"
    assert max(years) > 1000, "Expected some modern entities"
