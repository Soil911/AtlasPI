"""Tests for v6.15 AI Co-Founder Intelligence Layer.

Covers:
  - /admin/insights — traffic analysis
  - /admin/coverage-report — data quality
  - /admin/suggestions — smart suggestions
  - Helper functions (UA classification, continent mapping, era mapping)
  - Daily brief script
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.api.routes.admin_insights import (
    _classify_ua,
    _lat_to_continent,
    _year_to_era,
    INTERNAL_IPS,
)


# ═══════════════════════════════════════════════════════════════════
# Helper function tests
# ═══════════════════════════════════════════════════════════════════


class TestClassifyUA:
    """User-agent classification."""

    def test_bot_googlebot(self):
        assert _classify_ua("Mozilla/5.0 (compatible; Googlebot/2.1)") == "bot_or_crawler"

    def test_bot_curl(self):
        assert _classify_ua("curl/7.68.0") == "bot_or_crawler"

    def test_bot_python_requests(self):
        assert _classify_ua("python-requests/2.28.0") == "bot_or_crawler"

    def test_bot_gptbot(self):
        assert _classify_ua("GPTBot/1.0") == "bot_or_crawler"

    def test_browser_chrome(self):
        # Standard Chrome UA has no bot keywords — should classify as browser.
        assert _classify_ua(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ) == "browser"

    def test_api_client(self):
        assert _classify_ua("MyCustomApp/1.0") == "api_client"

    def test_none_ua(self):
        assert _classify_ua(None) == "unknown"

    def test_empty_ua(self):
        assert _classify_ua("") == "unknown"


class TestLatToContinent:
    """Rough continent assignment from coordinates."""

    def test_rome_europe(self):
        assert _lat_to_continent(41.9, 12.5) == "Europe"

    def test_cairo_africa(self):
        assert _lat_to_continent(30.0, 31.2) == "Africa / Middle East"

    def test_delhi_asia(self):
        assert _lat_to_continent(28.6, 77.2) == "Asia (Central/South)"

    def test_beijing_asia(self):
        assert _lat_to_continent(39.9, 116.4) == "Asia (East/Southeast)"

    def test_new_york_americas(self):
        assert _lat_to_continent(40.7, -74.0) == "Americas (North)"

    def test_lima_americas_south(self):
        assert _lat_to_continent(-12.0, -77.0) == "Americas (South/Central)"

    def test_none_values(self):
        assert _lat_to_continent(None, None) == "Unknown"

    def test_none_lat(self):
        assert _lat_to_continent(None, 12.5) == "Unknown"


class TestYearToEra:
    """Year-to-era bucket mapping."""

    def test_ancient(self):
        assert _year_to_era(-4000) == "Pre-3000 BCE"

    def test_bronze_age(self):
        assert _year_to_era(-2000) == "3000-1000 BCE"

    def test_classical(self):
        assert _year_to_era(-400) == "500-1 BCE"

    def test_late_antiquity(self):
        assert _year_to_era(400) == "1-500 CE"

    def test_medieval(self):
        assert _year_to_era(1200) == "1000-1500 CE"

    def test_modern(self):
        assert _year_to_era(1950) == "1900-2000 CE"

    def test_contemporary(self):
        assert _year_to_era(2020) == "2000-present"


# ═══════════════════════════════════════════════════════════════════
# Endpoint tests
# ═══════════════════════════════════════════════════════════════════


class TestInsightsEndpoint:
    """GET /admin/insights — traffic analysis."""

    def test_returns_200(self, client):
        r = client.get("/admin/insights")
        assert r.status_code == 200

    def test_response_structure(self, client):
        r = client.get("/admin/insights")
        d = r.json()
        assert "traffic_summary" in d
        assert "top_endpoints" in d
        assert "error_analysis" in d
        assert "user_agent_analysis" in d
        assert "external_users" in d
        assert "peak_hours" in d
        assert "generated_at" in d

    def test_traffic_summary_fields(self, client):
        r = client.get("/admin/insights")
        ts = r.json()["traffic_summary"]
        assert "total_all_time" in ts
        assert "total_24h" in ts
        assert "total_7d" in ts
        assert "total_30d" in ts
        assert "unique_ips_30d" in ts
        assert "avg_response_time_ms_30d" in ts

    def test_has_cache_header(self, client):
        r = client.get("/admin/insights")
        assert "cache-control" in r.headers
        assert "max-age" in r.headers["cache-control"]


class TestCoverageReportEndpoint:
    """GET /admin/coverage-report — data quality analysis."""

    def test_returns_200(self, client):
        r = client.get("/admin/coverage-report")
        assert r.status_code == 200

    def test_response_structure(self, client):
        r = client.get("/admin/coverage-report")
        d = r.json()
        assert "totals" in d
        assert "by_region" in d
        assert "by_type" in d
        assert "by_era" in d
        assert "confidence_distribution" in d
        assert "boundary_coverage" in d
        assert "date_precision_coverage" in d
        assert "chain_coverage" in d
        assert "data_completeness_score" in d

    def test_totals_are_positive(self, client):
        r = client.get("/admin/coverage-report")
        totals = r.json()["totals"]
        assert totals["entities"] > 0
        assert totals["events"] > 0
        assert totals["chains"] > 0

    def test_completeness_score_is_0_to_100(self, client):
        r = client.get("/admin/coverage-report")
        score = r.json()["data_completeness_score"]
        assert 0 <= score <= 100

    def test_boundary_coverage_has_percentage(self, client):
        r = client.get("/admin/coverage-report")
        bc = r.json()["boundary_coverage"]
        assert "percentage" in bc
        assert bc["total_entities"] > 0
        assert bc["with_boundary"] + bc["without_boundary"] == bc["total_entities"]

    def test_by_era_has_all_eras(self, client):
        r = client.get("/admin/coverage-report")
        eras = r.json()["by_era"]
        assert len(eras) == 11  # 11 era buckets defined

    def test_confidence_distribution_structure(self, client):
        r = client.get("/admin/coverage-report")
        cd = r.json()["confidence_distribution"]
        assert "entities" in cd
        assert "events" in cd
        # Each should have 5 buckets
        assert len(cd["entities"]) == 5
        assert len(cd["events"]) == 5

    def test_chain_coverage_fields(self, client):
        r = client.get("/admin/coverage-report")
        cc = r.json()["chain_coverage"]
        assert "entities_in_chains" in cc
        assert "orphan_entities" in cc
        assert "chain_coverage_pct" in cc

    def test_has_cache_header(self, client):
        r = client.get("/admin/coverage-report")
        assert "cache-control" in r.headers


class TestSuggestionsEndpoint:
    """GET /admin/suggestions — smart suggestions."""

    def test_returns_200(self, client):
        r = client.get("/admin/suggestions")
        assert r.status_code == 200

    def test_response_structure(self, client):
        r = client.get("/admin/suggestions")
        d = r.json()
        assert "failed_searches" in d
        assert "geographic_gaps" in d
        assert "temporal_gaps" in d
        assert "missing_connections" in d
        assert "low_confidence" in d
        assert "missing_boundaries" in d
        assert "generated_at" in d

    def test_missing_connections_has_total(self, client):
        r = client.get("/admin/suggestions")
        mc = r.json()["missing_connections"]
        assert "total_orphan_entities" in mc
        assert "sample" in mc

    def test_low_confidence_has_entities_and_events(self, client):
        r = client.get("/admin/suggestions")
        lc = r.json()["low_confidence"]
        assert "entities" in lc
        assert "events" in lc

    def test_has_cache_header(self, client):
        r = client.get("/admin/suggestions")
        assert "cache-control" in r.headers


# ═══════════════════════════════════════════════════════════════════
# Internal IPs constant
# ═══════════════════════════════════════════════════════════════════


class TestInternalIPs:
    """INTERNAL_IPS constant correctness."""

    def test_localhost_is_internal(self):
        assert "127.0.0.1" in INTERNAL_IPS

    def test_vps_is_internal(self):
        assert "77.81.229.242" in INTERNAL_IPS

    def test_docker_bridge_is_internal(self):
        assert "172.17.0.1" in INTERNAL_IPS

    def test_testclient_is_internal(self):
        assert "testclient" in INTERNAL_IPS

    def test_random_ip_is_external(self):
        assert "8.8.8.8" not in INTERNAL_IPS


# ═══════════════════════════════════════════════════════════════════
# Daily brief script
# ═══════════════════════════════════════════════════════════════════


class TestDailyBrief:
    """scripts/generate_daily_brief.py."""

    def test_import_and_generate(self):
        """Test that the brief generates without error and contains key sections."""
        from scripts.generate_daily_brief import generate_brief
        brief = generate_brief()
        assert isinstance(brief, str)
        assert "# AtlasPI Daily Brief" in brief
        assert "## Dataset overview" in brief
        assert "## Traffic highlights" in brief
        assert "## Data quality" in brief

    def test_brief_has_entity_count(self):
        from scripts.generate_daily_brief import generate_brief
        brief = generate_brief()
        # Should contain "Entities" in the dataset table
        assert "Entities" in brief

    def test_brief_has_quality_metrics(self):
        from scripts.generate_daily_brief import generate_brief
        brief = generate_brief()
        assert "Avg confidence" in brief
        assert "Boundary coverage" in brief
        assert "Chain coverage" in brief
