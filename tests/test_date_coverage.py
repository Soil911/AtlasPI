"""Tests for GET /v1/events/date-coverage endpoint — v6.25.0.

Verifies the date coverage metadata endpoint returns correct stats
about which MM-DD dates have events in the dataset.
"""


class TestDateCoverageEndpoint:
    """GET /v1/events/date-coverage"""

    def test_returns_200(self, client):
        r = client.get("/v1/events/date-coverage")
        assert r.status_code == 200

    def test_response_structure(self, client):
        r = client.get("/v1/events/date-coverage")
        data = r.json()
        assert "unique_dates" in data
        assert "total_days_in_year" in data
        assert "coverage_pct" in data
        assert "total_events_with_date" in data
        assert "dates" in data
        assert isinstance(data["dates"], list)

    def test_total_days_is_366(self, client):
        """366 because we count Feb 29 as a valid date."""
        r = client.get("/v1/events/date-coverage")
        assert r.json()["total_days_in_year"] == 366

    def test_unique_dates_is_positive(self, client):
        """We have at least some events with dates in the test DB."""
        r = client.get("/v1/events/date-coverage")
        data = r.json()
        assert data["unique_dates"] > 0

    def test_coverage_pct_is_valid(self, client):
        r = client.get("/v1/events/date-coverage")
        pct = r.json()["coverage_pct"]
        assert 0 <= pct <= 100

    def test_date_entry_structure(self, client):
        r = client.get("/v1/events/date-coverage")
        dates = r.json()["dates"]
        if dates:
            entry = dates[0]
            assert "mm_dd" in entry
            assert "month" in entry
            assert "day" in entry
            assert "event_count" in entry
            assert entry["event_count"] >= 1

    def test_dates_are_sorted(self, client):
        r = client.get("/v1/events/date-coverage")
        dates = r.json()["dates"]
        mm_dds = [d["mm_dd"] for d in dates]
        assert mm_dds == sorted(mm_dds)

    def test_mm_dd_format(self, client):
        """All mm_dd values must be in MM-DD format."""
        import re
        r = client.get("/v1/events/date-coverage")
        for d in r.json()["dates"]:
            assert re.match(r"^\d{2}-\d{2}$", d["mm_dd"])
            assert 1 <= d["month"] <= 12
            assert 1 <= d["day"] <= 31

    def test_total_events_matches_sum(self, client):
        """total_events_with_date should equal sum of all event_counts."""
        r = client.get("/v1/events/date-coverage")
        data = r.json()
        computed = sum(d["event_count"] for d in data["dates"])
        assert data["total_events_with_date"] == computed

    def test_no_duplicate_dates(self, client):
        r = client.get("/v1/events/date-coverage")
        mm_dds = [d["mm_dd"] for d in r.json()["dates"]]
        assert len(mm_dds) == len(set(mm_dds))
