"""Tests for event statistics in GET /v1/stats — v6.25.0.

Verifies the enhanced stats endpoint includes event-level statistics
(total, date precision breakdown, date coverage).
"""


class TestStatsEventsSection:
    """GET /v1/stats → events object."""

    def test_stats_has_events_key(self, client):
        r = client.get("/v1/stats")
        assert r.status_code == 200
        assert "events" in r.json()

    def test_events_stats_structure(self, client):
        data = client.get("/v1/stats").json()["events"]
        assert "total_events" in data
        assert "events_with_day" in data
        assert "events_with_month" in data
        assert "date_coverage_unique_days" in data
        assert "date_coverage_pct" in data
        assert "date_precision_breakdown" in data

    def test_total_events_positive(self, client):
        data = client.get("/v1/stats").json()["events"]
        assert data["total_events"] > 0

    def test_events_with_day_leq_total(self, client):
        data = client.get("/v1/stats").json()["events"]
        assert data["events_with_day"] <= data["total_events"]

    def test_events_with_month_leq_total(self, client):
        data = client.get("/v1/stats").json()["events"]
        assert data["events_with_month"] <= data["total_events"]

    def test_events_with_day_leq_month(self, client):
        """If an event has a day, it must also have a month."""
        data = client.get("/v1/stats").json()["events"]
        assert data["events_with_day"] <= data["events_with_month"]

    def test_date_coverage_pct_range(self, client):
        data = client.get("/v1/stats").json()["events"]
        assert 0 <= data["date_coverage_pct"] <= 100

    def test_date_precision_breakdown_sums_to_total(self, client):
        data = client.get("/v1/stats").json()["events"]
        breakdown_total = sum(data["date_precision_breakdown"].values())
        assert breakdown_total == data["total_events"]

    def test_date_precision_has_known_keys(self, client):
        data = client.get("/v1/stats").json()["events"]
        # At minimum, YEAR and DAY should exist in the test DB
        keys = set(data["date_precision_breakdown"].keys())
        assert "YEAR" in keys or "DAY" in keys or "UNKNOWN" in keys
