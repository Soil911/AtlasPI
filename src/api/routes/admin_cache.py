"""Cache administration endpoints — v6.21.

GET  /admin/cache-stats    — Redis cache statistics
POST /admin/cache/flush    — Flush all cached responses
"""

from __future__ import annotations

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.cache import flush_cache, get_cache_stats

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin"])


@router.get(
    "/admin/cache-stats",
    summary="Redis cache statistics",
    description=(
        "Returns cache connection status, total cached keys, hit/miss ratio, "
        "and Redis memory usage.  Works even if Redis is unavailable "
        "(returns zeroed stats with redis_connected=false)."
    ),
    include_in_schema=False,
)
def cache_stats():
    """Return current cache statistics."""
    stats = get_cache_stats()
    return JSONResponse(
        content=stats,
        headers={"Cache-Control": "no-cache"},
    )


@router.post(
    "/admin/cache/flush",
    summary="Flush all cached responses",
    description=(
        "Deletes all cache:* keys from Redis.  Returns the number of keys "
        "deleted.  Safe to call when Redis is unavailable (returns 0)."
    ),
    include_in_schema=False,
)
def cache_flush():
    """Flush all cached API responses."""
    deleted = flush_cache()
    logger.info("Cache flush: %d keys deleted", deleted)
    return JSONResponse(
        content={"flushed": deleted},
        headers={"Cache-Control": "no-cache"},
    )
