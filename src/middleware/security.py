"""Middleware di sicurezza: header protettivi su ogni risposta.

Aggiunge header standard di sicurezza HTTP. Per il path /embed
usa X-Frame-Options: SAMEORIGIN anziche' DENY, perche' la UI
embed e' progettata per essere incorporata in iframe.
"""

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.config import ENVIRONMENT


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Aggiunge header di sicurezza a ogni risposta."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time"] = f"{duration_ms:.1f}"

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # /embed e' progettato per iframe — permetti SAMEORIGIN
        if request.url.path.startswith("/embed"):
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
        else:
            response.headers["X-Frame-Options"] = "DENY"

        # HSTS solo in ambienti non-localhost (production / staging)
        host = request.headers.get("host", "")
        is_localhost = host.startswith("localhost") or host.startswith("127.0.0.1")
        if not is_localhost and ENVIRONMENT != "development":
            response.headers["Strict-Transport-Security"] = "max-age=31536000"

        return response
