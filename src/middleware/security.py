"""Middleware di sicurezza: header protettivi su ogni risposta.

Aggiunge header standard di sicurezza HTTP:
- Content-Security-Policy-Report-Only (v6.66.0, audit #security)
- Strict-Transport-Security con includeSubDomains + preload
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY / SAMEORIGIN / ALLOWALL a seconda del path
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: disabilita geolocation, camera, microphone, payment

ETHICS / Security: v6.66.0 rimuove X-XSS-Protection (header deprecato che
puo' introdurre XSS nei browser vecchi). CSP sostituisce la protezione XSS
in modo moderno e granulare.

CSP strategy: report-only per 1-2 settimane (v6.66.0 → v6.67.x). Dopo aver
raccolto i report via /v1/csp-report, si passa a enforce mode in release
successiva. Non rompere la produzione con CSP e' prioritario.

Il path /embed e /widget/* ricevono regole X-Frame-Options rilassate per
consentire l'embedding in siti terzi (v6.12+).
"""

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.config import ENVIRONMENT

# ─── Content Security Policy (report-only) ────────────────────────
# Permette:
#   - unpkg.com       : Leaflet + plugin JS/CSS caricati dalla mappa
#   - openstreetmap / cartodb / arcgis / fastly : tile servers della mappa
#   - data: nei font/img per favicon e markers inline
#
# Nota: 'unsafe-inline' e' necessario fino a quando static/index.html
# contiene <script> inline. v6.68+ pianifica migrazione a nonce/hash.
#
# report-uri: i violation reports arrivano su POST /v1/csp-report e
# vengono loggati (non salvati a DB) per auditing.
CSP_REPORT_ONLY = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://unpkg.com; "
    "style-src 'self' 'unsafe-inline' https://unpkg.com; "
    "img-src 'self' data: blob: "
    "https://*.tile.openstreetmap.org "
    "https://*.openstreetmap.fr "
    # v6.68 fix: CSP wildcard non è valido nel mezzo del hostname
    # (`cartodb-basemaps-*.global.ssl.fastly.net` browser-rejected).
    # Enumero esplicitamente i 4 subdomain a/b/c/d usati da CARTO DB.
    "https://cartodb-basemaps-a.global.ssl.fastly.net "
    "https://cartodb-basemaps-b.global.ssl.fastly.net "
    "https://cartodb-basemaps-c.global.ssl.fastly.net "
    "https://cartodb-basemaps-d.global.ssl.fastly.net "
    "https://*.basemaps.cartocdn.com "
    "https://server.arcgisonline.com; "
    "font-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'self'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "report-uri /v1/csp-report"
)

# Permissions-Policy: disabilita API sensibili che l'app non usa.
# Sintassi moderna (W3C Permissions-Policy, sostituisce Feature-Policy).
PERMISSIONS_POLICY = (
    "geolocation=(), "
    "camera=(), "
    "microphone=(), "
    "payment=(), "
    "usb=(), "
    "magnetometer=(), "
    "gyroscope=(), "
    "accelerometer=()"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Aggiunge header di sicurezza a ogni risposta."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time"] = f"{duration_ms:.1f}"

        # ── Header di base (sempre presenti) ────────────────────
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = PERMISSIONS_POLICY

        # v6.66.0: X-XSS-Protection deprecato e potenzialmente dannoso.
        # Rimuoviamo esplicitamente qualunque valore che starlette
        # o proxy a monte avessero settato. Setta a "0" per disabilitare
        # il filtro legacy (raccomandazione OWASP 2023+).
        response.headers["X-Xss-Protection"] = "0"

        # ── X-Frame-Options: dipende dal path ─────────────────
        # /embed e' progettato per iframe → SAMEORIGIN
        # /widget/* e' per embed in siti terzi → ALLOWALL + CSP frame-ancestors *
        # Altri path → DENY (no iframe)
        path = request.url.path
        if path.startswith("/widget"):
            response.headers["X-Frame-Options"] = "ALLOWALL"
            # Per widget pubblici, CSP deve permettere embedding ovunque
            response.headers["Content-Security-Policy"] = "frame-ancestors *"
        elif path.startswith("/embed"):
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
            # Per /embed applichiamo CSP report-only ma con frame-ancestors
            # rilassato (iframe da stesso origin). In futuro whitelist domini.
            response.headers["Content-Security-Policy-Report-Only"] = (
                CSP_REPORT_ONLY.replace("frame-ancestors 'self'", "frame-ancestors *")
            )
        else:
            response.headers["X-Frame-Options"] = "DENY"
            # CSP in report-only (v6.66.0) — non rompe nulla, raccoglie
            # dati. In v6.67+ si passa a "Content-Security-Policy" (enforce)
            # dopo review dei report.
            response.headers["Content-Security-Policy-Report-Only"] = CSP_REPORT_ONLY

        # ── HSTS (solo HTTPS, ambienti non-localhost) ────────────
        # v6.66.0: aggiunto includeSubDomains + preload.
        # NOTA: l'header preload da solo non basta — serve submission
        # manuale a https://hstspreload.org/ per l'inclusione effettiva
        # nella lista preload dei browser. Ma settare l'header e' requisito
        # preliminare (Chrome non accetta submission senza questo header).
        host = request.headers.get("host", "")
        is_localhost = host.startswith("localhost") or host.startswith("127.0.0.1")
        if not is_localhost and ENVIRONMENT != "development":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response
