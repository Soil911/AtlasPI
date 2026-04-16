"""Test per la pagina API Explorer (/docs-ui) — v6.20.0."""


def test_docs_ui_returns_200(client):
    """GET /docs-ui returns 200 with HTML content."""
    r = client.get("/docs-ui")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")


def test_docs_ui_contains_title(client):
    """The page contains the AtlasPI API Explorer title."""
    r = client.get("/docs-ui")
    assert "AtlasPI API Explorer" in r.text


def test_docs_ui_contains_entities_section(client):
    """The page contains the Entities API section."""
    r = client.get("/docs-ui")
    assert 'id="entities"' in r.text
    assert "/v1/entity" in r.text


def test_docs_ui_contains_events_section(client):
    """The page contains the Events API section."""
    r = client.get("/docs-ui")
    assert 'id="events"' in r.text
    assert "/v1/events" in r.text


def test_docs_ui_contains_chains_section(client):
    """The page contains the Dynasty Chains section."""
    r = client.get("/docs-ui")
    assert 'id="chains"' in r.text
    assert "/v1/chains" in r.text


def test_docs_ui_contains_try_it_buttons(client):
    """The page contains Try It buttons for live testing."""
    r = client.get("/docs-ui")
    assert "try-btn" in r.text
    assert "data-path" in r.text


def test_docs_ui_loads_static_assets(client):
    """The page references its CSS and JS assets."""
    r = client.get("/docs-ui")
    assert "/static/docs-ui/style.css" in r.text
    assert "/static/docs-ui/docs.js" in r.text
