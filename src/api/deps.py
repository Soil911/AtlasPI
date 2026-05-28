"""Authentication dependencies for AtlasPI admin endpoints.

# ETHICS: questa logica protegge endpoint che possono modificare/leakare
# stato interno (cache flush, AI suggestions, dev-ip dashboard, analytics).
# Failsafe: se ATLASPI_ADMIN_TOKEN non è settato → tutti bloccati
# (closed-by-default). Decisione e razionale in
# docs/auto-iter-wave0/wave-1-1/inventory-and-design.md.
#
# Note: l'IP allowlist è stata SCARTATA (cross-check GPT-5.5 ha mostrato
# che dietro nginx reverse proxy `request.client.host` riceve l'IP del
# proxy, non del client reale, rendendo `127.0.0.1` un bypass per
# chiunque). Solo token-based: X-Admin-Token header O Basic Auth.
"""
import base64
import hmac
import os

from fastapi import HTTPException, Request

_AUTH_HEADERS = {"WWW-Authenticate": 'Basic realm="AtlasPI Admin"'}


def verify_admin(request: Request) -> None:
    """Token-based auth dependency for /admin/* routes.

    Accepts (in order):
    1. ``X-Admin-Token: <token>`` header (curl/cron friendly)
    2. ``Authorization: Basic <b64(any-user:token)>`` (browser friendly,
       auto-cached after first prompt)

    Raises 401 with ``WWW-Authenticate: Basic realm="AtlasPI Admin"``
    on failure, so browsers prompt for credentials on first visit.

    Failsafe: if ``ATLASPI_ADMIN_TOKEN`` env is unset or empty, ALL
    requests are denied (better closed than open).
    """
    expected = os.getenv("ATLASPI_ADMIN_TOKEN", "").strip()
    if not expected:
        raise HTTPException(
            status_code=401,
            detail="Admin endpoint not configured (ATLASPI_ADMIN_TOKEN unset)",
            headers=_AUTH_HEADERS,
        )

    # 1. X-Admin-Token header
    token = request.headers.get("X-Admin-Token", "").strip()
    if token and hmac.compare_digest(
        token.encode("utf-8"), expected.encode("utf-8")
    ):
        return

    # 2. Authorization: Basic <b64(admin:token)>
    # Note: username DEVE essere esattamente "admin" (cross-check GPT-5.5:
    # accettare qualunque username era policy mismatch + confondeva password
    # manager dei browser).
    authz = request.headers.get("Authorization", "")
    if authz.startswith("Basic "):
        try:
            decoded = base64.b64decode(authz[6:], validate=True).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            decoded = ""
        if ":" in decoded:
            username, password = decoded.split(":", 1)
            if (
                username == "admin"
                and password
                and hmac.compare_digest(
                    password.encode("utf-8"), expected.encode("utf-8")
                )
            ):
                return

    raise HTTPException(
        status_code=401,
        detail="Admin authentication required",
        headers=_AUTH_HEADERS,
    )
