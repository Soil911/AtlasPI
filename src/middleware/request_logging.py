"""Middleware per logging automatico di ogni richiesta."""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.logging_config import request_id_var

logger = logging.getLogger("atlaspi.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log ogni richiesta con metodo, path, status, durata."""

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
        return response
