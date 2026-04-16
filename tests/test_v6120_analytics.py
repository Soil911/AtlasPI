"""Test per il layer analytics (v6.12.0).

Verifica:
- Modello ApiRequestLog funzionante
- Middleware che logga richieste API (non static)
- Dashboard HTML + JSON data endpoint
- Query aggregate corrette
"""

import pytest

from src.db.models import ApiRequestLog


# ─── Model ──────────────────────────────────────────────────────────────

class TestApiRequestLogModel:
    """Verifica che il modello ORM sia corretto."""

    def test_tablename(self):
        assert ApiRequestLog.__tablename__ == "api_request_logs"

    def test_has_required_columns(self):
        cols = {c.name for c in ApiRequestLog.__table__.columns}
        expected = {
            "id", "timestamp", "method", "path", "query_string",
            "status_code", "response_time_ms", "client_ip",
            "user_agent", "referer",
        }
        assert expected.issubset(cols), f"Missing: {expected - cols}"

    def test_has_indexes(self):
        idx_names = {idx.name for idx in ApiRequestLog.__table__.indexes}
        assert "ix_api_logs_timestamp" in idx_names
        assert "ix_api_logs_path" in idx_names
        assert "ix_api_logs_client_ip" in idx_names
        assert "ix_api_logs_status_code" in idx_names


# ─── Middleware path filtering ──────────────────────────────────────────

class TestMiddlewarePathFilter:
    """Verifica che _is_api_relevant filtri correttamente."""

    def test_api_v1_paths_included(self):
        from src.middleware.request_logging import _is_api_relevant
        assert _is_api_relevant("/v1/entities") is True
        assert _is_api_relevant("/v1/stats") is True
        assert _is_api_relevant("/v1/chains") is True

    def test_health_included(self):
        from src.middleware.request_logging import _is_api_relevant
        assert _is_api_relevant("/health") is True

    def test_admin_included(self):
        from src.middleware.request_logging import _is_api_relevant
        assert _is_api_relevant("/admin/analytics") is True
        assert _is_api_relevant("/admin/analytics/data") is True

    def test_static_excluded(self):
        from src.middleware.request_logging import _is_api_relevant
        assert _is_api_relevant("/static/app.js") is False
        assert _is_api_relevant("/static/style.css") is False

    def test_favicon_excluded(self):
        from src.middleware.request_logging import _is_api_relevant
        assert _is_api_relevant("/favicon.ico") is False
        assert _is_api_relevant("/favicon.svg") is False

    def test_robots_sitemap_excluded(self):
        from src.middleware.request_logging import _is_api_relevant
        assert _is_api_relevant("/robots.txt") is False
        assert _is_api_relevant("/sitemap.xml") is False

    def test_root_excluded(self):
        from src.middleware.request_logging import _is_api_relevant
        # Root landing page is NOT an API path
        assert _is_api_relevant("/") is False

    def test_docs_included(self):
        from src.middleware.request_logging import _is_api_relevant
        assert _is_api_relevant("/docs") is True
        assert _is_api_relevant("/redoc") is True


# ─── Dashboard endpoints ────────────────────────────────────────────────

class TestAnalyticsDashboard:
    """Verifica che gli endpoint analytics rispondano."""

    def test_dashboard_html_returns_200(self, client):
        r = client.get("/admin/analytics")
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "")

    def test_dashboard_html_contains_title(self, client):
        r = client.get("/admin/analytics")
        assert "AtlasPI Analytics Dashboard" in r.text

    def test_dashboard_html_has_chart_canvas(self, client):
        r = client.get("/admin/analytics")
        assert '<canvas id="chart">' in r.text

    def test_dashboard_html_auto_refresh(self, client):
        r = client.get("/admin/analytics")
        assert "setInterval" in r.text
        assert "60000" in r.text

    def test_data_endpoint_returns_200(self, client):
        r = client.get("/admin/analytics/data")
        assert r.status_code == 200

    def test_data_endpoint_json_structure(self, client):
        r = client.get("/admin/analytics/data")
        d = r.json()
        assert "summary" in d
        assert "requests_per_day" in d
        assert "top_endpoints" in d
        assert "top_ips" in d
        assert "top_user_agents" in d
        assert "recent_requests" in d

    def test_data_summary_fields(self, client):
        r = client.get("/admin/analytics/data")
        s = r.json()["summary"]
        assert "total_requests" in s
        assert "unique_ips" in s
        assert "avg_response_time_ms" in s
        assert isinstance(s["total_requests"], int)
        assert isinstance(s["unique_ips"], int)


# ─── Middleware + DB integration ────────────────────────────────────────

class TestMiddlewareWrites:
    """Verifica che il middleware scriva effettivamente nel DB."""

    def test_health_request_gets_logged(self, client, db):
        """Dopo una richiesta /health, un record deve comparire in api_request_logs."""
        # Count before
        before = db.query(ApiRequestLog).filter(
            ApiRequestLog.path == "/health"
        ).count()

        # Make a request that the middleware should log
        r = client.get("/health")
        assert r.status_code == 200

        # Wait briefly for the background thread to write
        # Write is synchronous — no sleep needed

        after = db.query(ApiRequestLog).filter(
            ApiRequestLog.path == "/health"
        ).count()
        assert after > before, "Middleware did not log /health request"

    def test_v1_request_gets_logged(self, client, db):
        before = db.query(ApiRequestLog).filter(
            ApiRequestLog.path == "/v1/stats"
        ).count()

        client.get("/v1/stats")
        # Write is synchronous — no sleep needed

        after = db.query(ApiRequestLog).filter(
            ApiRequestLog.path == "/v1/stats"
        ).count()
        assert after > before, "Middleware did not log /v1/stats request"

    def test_logged_entry_has_correct_fields(self, client, db):
        """Verifica che i campi del log siano sensati."""
        client.get("/v1/stats")
        # Write is synchronous — no sleep needed

        entry = db.query(ApiRequestLog).filter(
            ApiRequestLog.path == "/v1/stats"
        ).order_by(ApiRequestLog.id.desc()).first()
        assert entry is not None

        assert entry.method == "GET"
        assert entry.status_code == 200
        assert entry.response_time_ms >= 0
        assert entry.client_ip is not None
        assert entry.timestamp is not None
        assert "T" in entry.timestamp  # ISO format

    def test_analytics_data_reflects_logged_requests(self, client):
        """Dopo alcune richieste, /admin/analytics/data deve mostrare i dati."""
        # Make a few requests
        for _ in range(3):
            client.get("/health")
        # Write is synchronous — no sleep needed

        r = client.get("/admin/analytics/data")
        d = r.json()
        assert d["summary"]["total_requests"] > 0
        assert d["summary"]["unique_ips"] > 0


# ─── Alembic migration file ────────────────────────────────────────────

class TestAlembicMigration:
    """Verifica che la migration 007 esista e abbia la struttura corretta."""

    def test_migration_file_exists(self):
        import os
        path = os.path.join("alembic", "versions", "007_api_request_logs.py")
        assert os.path.exists(path), f"Migration file not found: {path}"

    def test_migration_has_correct_revision_chain(self):
        import importlib.util
        import os

        migration_path = os.path.join("alembic", "versions", "007_api_request_logs.py")
        spec = importlib.util.spec_from_file_location("m007", migration_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        assert mod.revision == "007_api_request_logs"
        assert mod.down_revision == "006_dynasty_chains"
