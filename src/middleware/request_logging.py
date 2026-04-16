"""Middleware per logging automatico di ogni richiesta.

Combina due funzioni:
1. Log testuale di ogni richiesta (metodo, path, status, durata)
2. Write analytics a DB in background thread (api_request_logs table)
"""

import logging
import time
import uuid
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.logging_config import request_id_var

logger = logging.getLogger("atlaspi.access")

# ─── Analytics path filtering ──────────────────────────────────────────

_API_PREFIXES = ("/v1/", "/health", "/admin/", "/docs", "/redoc", "/openapi.json")
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


def _extract_client_ip(request: Request) -> str:
    """Return the real client IP from X-Forwarded-For (first hop) or socket."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = request.client
    return client.host if client else "unknown"


def _write_analytics_entry(
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


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log ogni richiesta con metodo, path, status, durata.

    Also writes API-relevant requests to the api_request_logs table
    via a fire-and-forget background thread (v6.12 analytics layer).
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = uuid.uuid4().hex[:12]
        request_id_var.set(request_id)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        # Skip log per static files
        path = request.url.path
        if not path.startswith("/static"):
            logger.info(
                "%s %s → %d (%.1fms)",
                request.method,
                path,
                response.status_code,
                duration_ms,
            )

        response.headers["X-Request-ID"] = request_id

        # ── Analytics DB write (v6.12) ─────────────────────────────
        if _is_api_relevant(path):
            timestamp = datetime.now(timezone.utc).isoformat()
            qs = str(request.url.query) if request.url.query else None
            # Synchronous write — fast enough for now (<5ms per INSERT).
            # If latency becomes an issue, switch to background thread
            # or async task queue.
            _write_analytics_entry(
                timestamp,
                request.method,
                path,
                qs,
                response.status_code,
                duration_ms,
                _extract_client_ip(request),
                request.headers.get("user-agent"),
                request.headers.get("referer"),
            )

        return response
