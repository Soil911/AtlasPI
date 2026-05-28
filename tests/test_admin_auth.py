"""Test che gli endpoint /admin/* siano protetti da verify_admin (Wave 1.1).

# ETHICS: questi test prevengono regressioni dove un nuovo /admin/* viene
# aggiunto senza la dependency verify_admin, lasciandolo esposto.
# Vedi docs/auto-iter-wave0/wave-1-1/inventory-and-design.md.
"""
import base64
import re

import pytest


TEST_TOKEN = "test-admin-token-CHANGE"


@pytest.fixture(autouse=True)
def admin_token_env(monkeypatch):
    """Setta ATLASPI_ADMIN_TOKEN per ogni test."""
    monkeypatch.setenv("ATLASPI_ADMIN_TOKEN", TEST_TOKEN)
    yield


def _admin_routes(client):
    """Tutti i (method, path) /admin/* registrati nell'app."""
    out = []
    for r in client.app.routes:
        path = getattr(r, "path", "") or ""
        methods = getattr(r, "methods", set()) or set()
        if path.startswith("/admin/"):
            for m in methods:
                if m in ("GET", "POST", "PATCH", "DELETE", "PUT"):
                    out.append((m, path))
    return out


def _safe_path(path: str) -> str:
    """Sostituisce path params {x} con valore dummy per testing."""
    return re.sub(r"\{[^}]+\}", "1", path) if "{" in path else path


class TestAdminAuth:

    def test_admin_routes_discovered(self, client):
        """Sanity: ci sono almeno 15 route /admin/* registrate."""
        routes = _admin_routes(client)
        assert len(routes) >= 15, (
            f"Expected >=15 admin routes, got {len(routes)}: {routes}"
        )

    def test_unauth_returns_401(self, unauth_client):
        """Senza header auth → 401 per OGNI route /admin/*."""
        failed = []
        for method, path in _admin_routes(unauth_client):
            url = _safe_path(path)
            r = unauth_client.request(method, url)
            if r.status_code != 401:
                failed.append(f"{method} {url} -> {r.status_code}")
            elif "Basic" not in r.headers.get("WWW-Authenticate", ""):
                failed.append(f"{method} {url} -> 401 ma WWW-Authenticate manca")
        assert not failed, "Routes non protetti:\n" + "\n".join(failed)

    def test_x_admin_token_grants_access(self, unauth_client):
        """X-Admin-Token corretto → non più 401."""
        failed = []
        for method, path in _admin_routes(unauth_client):
            url = _safe_path(path)
            r = unauth_client.request(
                method, url, headers={"X-Admin-Token": TEST_TOKEN}
            )
            if r.status_code == 401:
                failed.append(f"{method} {url} ancora 401 con token corretto")
        assert not failed, "Token NON accettato:\n" + "\n".join(failed)

    def test_basic_auth_grants_access(self, unauth_client):
        """Basic Auth user=admin pass=TOKEN → non più 401."""
        creds = base64.b64encode(f"admin:{TEST_TOKEN}".encode()).decode()
        failed = []
        for method, path in _admin_routes(unauth_client):
            url = _safe_path(path)
            r = unauth_client.request(
                method, url, headers={"Authorization": f"Basic {creds}"}
            )
            if r.status_code == 401:
                failed.append(f"{method} {url} ancora 401 con Basic Auth")
        assert not failed, "Basic Auth NON accettato:\n" + "\n".join(failed)

    def test_wrong_token_returns_401(self, unauth_client):
        """Token sbagliato → 401."""
        r = unauth_client.get(
            "/admin/cache-stats", headers={"X-Admin-Token": "wrong"}
        )
        assert r.status_code == 401

    def test_basic_auth_wrong_password(self, unauth_client):
        """Basic Auth con password sbagliata → 401."""
        creds = base64.b64encode(b"admin:wrongpass").decode()
        r = unauth_client.get(
            "/admin/cache-stats", headers={"Authorization": f"Basic {creds}"}
        )
        assert r.status_code == 401

    def test_failsafe_env_unset(self, unauth_client, monkeypatch):
        """ATLASPI_ADMIN_TOKEN unset → tutti 401 anche con token corretto."""
        monkeypatch.delenv("ATLASPI_ADMIN_TOKEN", raising=False)
        r = unauth_client.get(
            "/admin/cache-stats", headers={"X-Admin-Token": TEST_TOKEN}
        )
        assert r.status_code == 401

    def test_failsafe_env_empty(self, unauth_client, monkeypatch):
        """ATLASPI_ADMIN_TOKEN vuoto → tutti 401."""
        monkeypatch.setenv("ATLASPI_ADMIN_TOKEN", "")
        r = unauth_client.get(
            "/admin/cache-stats", headers={"X-Admin-Token": TEST_TOKEN}
        )
        assert r.status_code == 401

    def test_basic_auth_malformed_b64(self, unauth_client):
        """Basic Auth con base64 invalido → 401."""
        r = unauth_client.get(
            "/admin/cache-stats",
            headers={"Authorization": "Basic not!!base64@@@"},
        )
        assert r.status_code == 401

    def test_basic_auth_missing_colon(self, unauth_client):
        """Basic Auth senza colon (no password) → 401."""
        creds = base64.b64encode(b"admin").decode()
        r = unauth_client.get(
            "/admin/cache-stats", headers={"Authorization": f"Basic {creds}"}
        )
        assert r.status_code == 401

    def test_basic_auth_wrong_username(self, unauth_client):
        """Basic Auth con username != "admin" → 401 (even with correct token)."""
        for bad_user in ("foo", "root", "", "Admin", "ADMIN"):
            creds = base64.b64encode(f"{bad_user}:{TEST_TOKEN}".encode()).decode()
            r = unauth_client.get(
                "/admin/cache-stats", headers={"Authorization": f"Basic {creds}"}
            )
            assert r.status_code == 401, (
                f"Basic Auth con user='{bad_user}' è passato (atteso 401)"
            )

    def test_public_endpoints_unaffected(self, unauth_client):
        """Sanity: endpoint pubblici NON sono protetti dalla nuova dep."""
        r = unauth_client.get("/health")
        assert r.status_code == 200
        r = unauth_client.get("/v1/entities/light?limit=1")
        assert r.status_code == 200

    def test_no_query_param_bypass(self, unauth_client):
        """Token via query param NON deve funzionare (solo header)."""
        r = unauth_client.get(f"/admin/cache-stats?X-Admin-Token={TEST_TOKEN}")
        assert r.status_code == 401
        r = unauth_client.get(f"/admin/cache-stats?admin_token={TEST_TOKEN}")
        assert r.status_code == 401
