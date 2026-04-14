"""Test per v6.1 — Reliability layer.

Copre:
- Health check esteso (uptime, sentry_active, checks dict, environment)
- Endpoint SEO (robots.txt, sitemap.xml)
- Modulo monitoring (import senza errori, sentry off-by-default)
- Backup script presente ed eseguibile (smoke check)
"""

import os
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent


# ─── TestExtendedHealthCheck ─────────────────────────────────────


class TestExtendedHealthCheck:
    """Health check ora ritorna molti piu' dettagli operativi."""

    def test_health_includes_environment(self, client):
        d = client.get("/health").json()
        assert "environment" in d
        # In test mode l'env viene ereditata; deve essere stringa non vuota
        assert isinstance(d["environment"], str)
        assert d["environment"]

    def test_health_includes_uptime(self, client):
        d = client.get("/health").json()
        assert "uptime_seconds" in d
        assert isinstance(d["uptime_seconds"], (int, float))
        assert d["uptime_seconds"] >= 0

    def test_health_includes_check_duration(self, client):
        d = client.get("/health").json()
        assert "check_duration_ms" in d
        # Deve essere veloce: meno di 500ms anche su CI lenta
        assert 0 <= d["check_duration_ms"] < 500

    def test_health_sentry_inactive_in_tests(self, client):
        # In test mode SENTRY_DSN non e' configurato
        d = client.get("/health").json()
        assert d["sentry_active"] is False

    def test_health_checks_dict_has_database(self, client):
        d = client.get("/health").json()
        assert "checks" in d
        assert isinstance(d["checks"], dict)
        assert d["checks"].get("database") == "ok"

    def test_health_checks_dict_has_seed(self, client):
        d = client.get("/health").json()
        # Test DB ha entita' seedate, quindi seed = "ok"
        assert d["checks"].get("seed") == "ok"

    def test_health_checks_dict_has_sentry(self, client):
        d = client.get("/health").json()
        assert d["checks"].get("sentry") == "disabled"

    def test_health_status_is_ok_with_full_data(self, client):
        # Con DB up e seed ok, status deve essere "ok"
        d = client.get("/health").json()
        assert d["status"] == "ok"


# ─── TestSEOEndpoints ────────────────────────────────────────────


class TestSEOEndpoints:
    """Endpoint per crawler SEO devono essere presenti e ben formati."""

    def test_robots_txt_served(self, client):
        r = client.get("/robots.txt")
        assert r.status_code == 200
        assert "text/plain" in r.headers["content-type"]
        body = r.text
        assert "User-agent:" in body
        assert "Sitemap:" in body

    def test_robots_allows_ai_crawlers(self, client):
        r = client.get("/robots.txt")
        body = r.text
        # AtlasPI e' progettato per AI agents: GPTBot e ClaudeBot
        # devono essere esplicitamente permessi
        assert "GPTBot" in body
        assert "ClaudeBot" in body

    def test_sitemap_xml_served(self, client):
        r = client.get("/sitemap.xml")
        assert r.status_code == 200
        assert "xml" in r.headers["content-type"]
        body = r.text
        assert "<urlset" in body
        assert "<loc>" in body

    def test_sitemap_includes_canonical_root(self, client):
        body = client.get("/sitemap.xml").text
        # La home del dominio canonico deve essere indicizzata
        assert "atlaspi.cra-srl.com" in body


# ─── TestMonitoringModule ────────────────────────────────────────


class TestMonitoringModule:
    """Il modulo `src.monitoring` deve essere safe da importare senza Sentry."""

    def test_monitoring_imports_without_sentry_dsn(self):
        # Anche senza SENTRY_DSN il modulo deve caricarsi
        assert "SENTRY_DSN" not in os.environ or not os.environ["SENTRY_DSN"]

        from src import monitoring
        assert hasattr(monitoring, "init_sentry")
        assert hasattr(monitoring, "sentry_is_active")
        assert hasattr(monitoring, "uptime_seconds")
        assert hasattr(monitoring, "capture_exception")

    def test_init_sentry_returns_false_without_dsn(self):
        from src.monitoring import init_sentry, sentry_is_active

        # In test mode SENTRY_DSN e' vuoto: init deve essere no-op
        assert init_sentry() is False
        # Idempotente
        assert init_sentry() is False
        # Sentry inactive
        assert sentry_is_active() is False

    def test_uptime_seconds_is_positive(self):
        from src.monitoring import uptime_seconds
        u = uptime_seconds()
        assert isinstance(u, float)
        assert u > 0  # il processo gira da almeno 0+ secondi

    def test_capture_exception_does_not_raise_without_sentry(self):
        # Anche senza Sentry, non deve esplodere
        from src.monitoring import capture_exception

        try:
            raise ValueError("test exception")
        except ValueError as e:
            capture_exception(e, where="test", extra="data")  # no raise


# ─── TestBackupScripts ───────────────────────────────────────────


class TestBackupScripts:
    """Verifica presenza e shape degli script operativi."""

    def test_backup_script_exists(self):
        f = REPO_ROOT / "scripts" / "backup.sh"
        assert f.exists(), f"missing: {f}"

    def test_restore_script_exists(self):
        f = REPO_ROOT / "scripts" / "restore.sh"
        assert f.exists(), f"missing: {f}"

    def test_smoke_test_script_exists(self):
        f = REPO_ROOT / "scripts" / "smoke_test.sh"
        assert f.exists(), f"missing: {f}"

    def test_backup_script_handles_sqlite_and_postgres(self):
        body = (REPO_ROOT / "scripts" / "backup.sh").read_text(encoding="utf-8")
        assert "sqlite" in body.lower()
        assert "pg_dump" in body.lower()

    def test_smoke_test_covers_critical_endpoints(self):
        body = (REPO_ROOT / "scripts" / "smoke_test.sh").read_text(encoding="utf-8")
        for endpoint in [
            "/health",
            "/v1/stats",
            "/v1/entities",
            "/v1/snapshot",
            "/v1/aggregation",
            "/v1/random",
            "/v1/nearby",
            "/docs",
            "/robots.txt",
            "/sitemap.xml",
        ]:
            assert endpoint in body, f"smoke test missing endpoint: {endpoint}"

    def test_operations_runbook_exists(self):
        f = REPO_ROOT / "docs" / "OPERATIONS.md"
        assert f.exists(), "missing operational runbook"
        body = f.read_text(encoding="utf-8")
        # Deve coprire le situazioni critiche
        for section in ["Quick actions", "Backup", "Monitoring", "Sentry", "UptimeRobot"]:
            assert section in body


# ─── TestConfigDefaults ──────────────────────────────────────────


class TestConfigDefaults:
    """Default sicuri per produzione."""

    def test_sentry_dsn_default_is_empty(self):
        # Default sicuro: nessun dato esfiltrato senza configurazione esplicita
        from src.config import SENTRY_DSN
        # Puo' essere "" o whitespace ma non deve essere un placeholder valido
        assert not SENTRY_DSN or SENTRY_DSN.startswith("https://")

    def test_public_base_url_is_https(self):
        from src.config import PUBLIC_BASE_URL
        assert PUBLIC_BASE_URL.startswith("https://")

    def test_sentry_traces_sample_rate_is_sane(self):
        from src.config import SENTRY_TRACES_SAMPLE_RATE
        assert 0.0 <= SENTRY_TRACES_SAMPLE_RATE <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
