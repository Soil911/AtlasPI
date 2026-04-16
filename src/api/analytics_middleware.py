"""Middleware that logs API requests to the api_request_logs table.

Only logs API-relevant paths: /v1/*, /health, /admin/*, /docs, /redoc, /openapi.json.
Excludes: /static/*, favicon.*, robots.txt, sitemap.xml, manifest.json, sw.js.

Logging is fire-and-forget in a background thread to avoid slowing responses.
"""

import logging
import threading
import time
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Paths that ARE logged (prefix match)
_API_PREFIXES = ("/v1/", "/health", "/admin/", "/docs", "/redoc", "/openapi.json")

# Paths that are NEVER logged (exact or prefix match)
_EXCLUDED_EXACT = {"/robots.txt", "/sitemap.xml", "/manifest.json", "/sw.js"}
_EXCLUDED_PREFIXES = ("/static/", "/favicon")


def _is_api_relevant(path: str) -> bool:
    """Return True if *path* should be logged to the analytics table."""
    # Exclude first (cheaper check)
    if path in _EXCLUDED_EXACT:
        return False
    for prefix in _EXCLUDED_PREFIXES:
        if path.startswith(prefix):
            return False
    # Include only known API prefixes
    for prefix in _API_PREFIXES:
        if path.startswith(prefix):
            return True
    return False


def _extract_client_ip(request: Request) -> str:
    """Return the real client IP from X-Forwarded-For (first hop) or socket."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = request.client
    return client.host if client else "unknown"


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


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Log API requests to the ``api_request_logs`` table.

    Non-API paths (static files, favicons, etc.) are silently skipped.
    The DB write happens in a daemon thread so it never delays the response.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        path = request.url.path
        if not _is_api_relevant(path):
            return response

        # Collect request metadata
        timestamp = datetime.now(timezone.utc).isoformat()
        method = request.method
        query_string = str(request.url.query) if request.url.query else None
        status_code = response.status_code
        client_ip = _extract_client_ip(request)
        user_agent = request.headers.get("user-agent")
        referer = request.headers.get("referer")

        # Fire-and-forget: write in a daemon thread so the response is not delayed
        thread = threading.Thread(
            target=_write_log_entry,
            args=(
                timestamp,
                method,
                path,
                query_string,
                status_code,
                elapsed_ms,
                client_ip,
                user_agent,
                referer,
            ),
            daemon=True,
        )
        thread.start()

        return response
