"""Middleware that logs API requests to the api_request_logs table.

Only logs API-relevant paths: /v1/*, /health, /admin/*, /docs, /redoc, /openapi.json.
Excludes: /static/*, favicon.*, robots.txt, sitemap.xml, manifest.json, sw.js.

Implemented as a **pure ASGI middleware** (not BaseHTTPMiddleware) for
compatibility with gunicorn + uvicorn workers. Logging is fire-and-forget
in a background thread to avoid slowing responses.
"""

import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any

from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)

# Paths that ARE logged (prefix match)
_API_PREFIXES = ("/v1/", "/health", "/admin/", "/docs", "/redoc", "/openapi.json")

# Paths that are NEVER logged (exact or prefix match)
_EXCLUDED_EXACT = {"/robots.txt", "/sitemap.xml", "/manifest.json", "/sw.js"}
_EXCLUDED_PREFIXES = ("/static/", "/favicon")


def _is_api_relevant(path: str) -> bool:
    """Return True if *path* should be logged to the analytics table."""
    if path in _EXCLUDED_EXACT:
        return False
    for prefix in _EXCLUDED_PREFIXES:
        if path.startswith(prefix):
            return False
    for prefix in _API_PREFIXES:
        if path.startswith(prefix):
            return True
    return False


def _extract_client_ip(scope: Scope) -> str:
    """Return the real client IP from headers or socket."""
    headers = dict(scope.get("headers", []))
    forwarded = headers.get(b"x-forwarded-for")
    if forwarded:
        return forwarded.decode("latin-1").split(",")[0].strip()
    client = scope.get("client")
    return client[0] if client else "unknown"


def _extract_header(scope: Scope, name: bytes) -> str | None:
    """Extract a header value from ASGI scope."""
    for key, val in scope.get("headers", []):
        if key == name:
            return val.decode("latin-1")
    return None


def _write_log_entry(
    timestamp: str,
    method: str,
    path: str,
    query_string: str | None,
    status_code: int,
    response_time_ms: float,
    client_ip: str,
    user_agent: str | None,
    referer: str | None,
) -> None:
    """Write a single ApiRequestLog row (runs in a background thread)."""
    try:
        from src.db.database import SessionLocal
        from src.db.models import ApiRequestLog

        db = SessionLocal()
        try:
            entry = ApiRequestLog(
                timestamp=timestamp,
                method=method,
                path=path,
                query_string=query_string,
                status_code=status_code,
                response_time_ms=response_time_ms,
                client_ip=client_ip,
                user_agent=user_agent,
                referer=referer,
            )
            db.add(entry)
            db.commit()
        except Exception:
            db.rollback()
            logger.warning("Failed to write analytics log entry", exc_info=True)
        finally:
            db.close()
    except Exception:
        logger.warning("Failed to obtain DB session for analytics log", exc_info=True)


class AnalyticsMiddleware:
    """Pure ASGI middleware that logs API requests to ``api_request_logs``.

    Non-API paths (static files, favicons, etc.) are silently passed through.
    The DB write happens in a daemon thread so it never delays the response.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Only intercept HTTP requests
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if not _is_api_relevant(path):
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        status_code = 0

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
            await send(message)

        await self.app(scope, receive, send_wrapper)

        elapsed_ms = (time.perf_counter() - start) * 1000

        # v6.33: Prometheus in-memory counters
        try:
            from src.api.metrics import record_request
            record_request(path, scope.get("method", "?"), status_code, elapsed_ms / 1000.0)
        except Exception:
            pass

        # Collect request metadata from ASGI scope
        method = scope.get("method", "?")
        qs_raw = scope.get("query_string", b"")
        query_string = qs_raw.decode("latin-1") if qs_raw else None
        client_ip = _extract_client_ip(scope)
        user_agent = _extract_header(scope, b"user-agent")
        referer = _extract_header(scope, b"referer")
        timestamp = datetime.now(timezone.utc).isoformat()

        # Fire-and-forget DB write
        thread = threading.Thread(
            target=_write_log_entry,
            args=(
                timestamp, method, path, query_string,
                status_code, elapsed_ms, client_ip,
                user_agent, referer,
            ),
            daemon=True,
        )
        thread.start()
