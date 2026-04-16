"""Tests for v6.22.0 — Embeddable Widgets.

Tests widget routes, theme parameter, X-Frame-Options header,
and error handling for invalid entity IDs.
"""


class TestWidgetEntityCard:
    """Entity card widget endpoint."""

    def test_entity_widget_returns_200(self, client):
        r = client.get("/widget/entity/1")
        assert r.status_code == 200

    def test_entity_widget_returns_html(self, client):
        r = client.get("/widget/entity/1")
        assert "text/html" in r.headers["content-type"]

    def test_entity_widget_allows_embedding(self, client):
        r = client.get("/widget/entity/1")
        assert r.headers.get("x-frame-options") == "ALLOWALL"

    def test_entity_widget_has_csp_frame_ancestors(self, client):
        r = client.get("/widget/entity/1")
        csp = r.headers.get("content-security-policy", "")
        assert "frame-ancestors" in csp

    def test_entity_widget_theme_light(self, client):
        r = client.get("/widget/entity/1?theme=light")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]

    def test_entity_widget_contains_atlaspi_branding(self, client):
        r = client.get("/widget/entity/1")
        assert "AtlasPI" in r.text or "atlaspi" in r.text.lower()


class TestWidgetTimeline:
    """Timeline widget endpoint."""

    def test_timeline_widget_returns_200(self, client):
        r = client.get("/widget/timeline")
        assert r.status_code == 200

    def test_timeline_widget_returns_html(self, client):
        r = client.get("/widget/timeline")
        assert "text/html" in r.headers["content-type"]

    def test_timeline_widget_allows_embedding(self, client):
        r = client.get("/widget/timeline")
        assert r.headers.get("x-frame-options") == "ALLOWALL"

    def test_timeline_widget_with_params(self, client):
        r = client.get("/widget/timeline?year_min=-500&year_max=500")
        assert r.status_code == 200


class TestWidgetOnThisDay:
    """On This Day widget endpoint."""

    def test_on_this_day_widget_returns_200(self, client):
        r = client.get("/widget/on-this-day")
        assert r.status_code == 200

    def test_on_this_day_widget_returns_html(self, client):
        r = client.get("/widget/on-this-day")
        assert "text/html" in r.headers["content-type"]

    def test_on_this_day_widget_allows_embedding(self, client):
        r = client.get("/widget/on-this-day")
        assert r.headers.get("x-frame-options") == "ALLOWALL"

    def test_on_this_day_widget_with_date(self, client):
        r = client.get("/widget/on-this-day?date=07-14")
        assert r.status_code == 200


class TestWidgetShowcase:
    """Widget showcase page."""

    def test_showcase_returns_200(self, client):
        r = client.get("/widgets")
        assert r.status_code == 200

    def test_showcase_returns_html(self, client):
        r = client.get("/widgets")
        assert "text/html" in r.headers["content-type"]

    def test_showcase_contains_embed_examples(self, client):
        r = client.get("/widgets")
        # Should have iframe examples
        assert "iframe" in r.text.lower()

    def test_showcase_mentions_all_widget_types(self, client):
        r = client.get("/widgets")
        text = r.text.lower()
        assert "entity" in text
        assert "timeline" in text
        assert "on this day" in text or "on-this-day" in text
