"""Middleware centralizzati per AtlasPI.

Re-esporta i middleware dalle loro posizioni canoniche e aggiunge
il RateLimitMiddleware stub (in-memory, predisposto per Redis).
"""

import logging
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Re-export per import centralizzato
from src.middleware.request_logging import RequestLoggingMiddleware  # noqa: F401
from src.middleware.security import SecurityHeadersMiddleware  # noqa: F401

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiter in-memory a finestra fissa (stub, interfaccia Redis-ready).

    Parametri:
        max_requests: numero massimo di richieste per finestra.
        window_seconds: durata della finestra temporale in secondi.

    In produzione sostituire _get_count / _increment con chiamate Redis
    (INCR + EXPIRE) senza modificare l'interfaccia esterna.
    """

    def __init__(self, app, max_requests: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # {client_ip: [(timestamp, ...]}
        self._store: dict[str, list[float]] = defaultdict(list)

    # ── Backend astratto (sostituire con Redis) ──────────────
    def _client_key(self, request: Request) -> str:
        """Ritorna una chiave univoca per il client."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        client = request.client
        return client.host if client else "unknown"

    def _get_count(self, key: str, now: float) -> int:
        """Conta le richieste nella finestra corrente."""
        cutoff = now - self.window_seconds
        self._store[key] = [t for t in self._store[key] if t > cutoff]
        return len(self._store[key])

    def _increment(self, key: str, now: float) -> None:
        """Registra una nuova richiesta."""
        self._store[key].append(now)

    # ── dispatch ─────────────────────────────────────────────
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        now = time.time()
        key = self._client_key(request)
        count = self._get_count(key, now)

        if count >= self.max_requests:
            retry_after = str(self.window_seconds)
            logger.warning("Rate limit superato per %s (%d richieste)", key, count)
            return Response(
                content='{"error":{"code":"RATE_LIMITED","message":"Troppe richieste, riprova tra poco."}}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": retry_after},
            )

        self._increment(key, now)
        response = await call_next(request)

        # Header informativi
        remaining = max(0, self.max_requests - count - 1)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response
