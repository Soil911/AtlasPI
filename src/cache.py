"""Redis response cache for AtlasPI API.

Provides a decorator-based caching layer for FastAPI route handlers.
Uses Redis as backend with configurable TTL per endpoint.

Graceful degradation: if Redis is unavailable (dev mode, connection error),
the cache is bypassed silently and the original handler runs normally.
No crash, no error — just uncached responses.

Key format: cache:{method}:{path}:{sorted_query_params}
"""

import json
import logging
import os
import time
from functools import wraps
from typing import Any, Callable

import redis

logger = logging.getLogger(__name__)

# ─── Redis connection ────────────────────────────────────────────────

_redis_client: redis.Redis | None = None
_redis_available: bool = False

# Hit/miss counters (in-process; reset on restart).
_cache_hits: int = 0
_cache_misses: int = 0


def init_redis() -> None:
    """Initialise the Redis connection pool.

    Called once at app startup.  If REDIS_URL is not set or the connection
    fails, Redis is marked as unavailable and all cache operations become
    no-ops.
    """
    global _redis_client, _redis_available

    redis_url = os.getenv("REDIS_URL", "").strip()
    if not redis_url:
        logger.info("REDIS_URL not set — cache disabled (dev mode)")
        _redis_client = None
        _redis_available = False
        return

    try:
        _redis_client = redis.Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=2,
            retry_on_timeout=False,
        )
        _redis_client.ping()
        _redis_available = True
        logger.info("Redis cache connected: %s", redis_url.split("@")[-1] if "@" in redis_url else redis_url)
    except Exception:
        logger.warning("Redis connection failed — cache disabled", exc_info=True)
        _redis_client = None
        _redis_available = False


def get_redis() -> redis.Redis | None:
    """Return the Redis client (or None if unavailable)."""
    return _redis_client if _redis_available else None


def is_redis_available() -> bool:
    """Check if Redis is connected and responsive."""
    if not _redis_available or _redis_client is None:
        return False
    try:
        _redis_client.ping()
        return True
    except Exception:
        return False


# ─── Cache key construction ──────────────────────────────────────────


def _build_cache_key(method: str, path: str, query_params: dict[str, Any]) -> str:
    """Build a deterministic cache key from request components.

    Query params are sorted so that ?limit=10&offset=0 and
    ?offset=0&limit=10 produce the same key.
    """
    sorted_qs = "&".join(
        f"{k}={v}" for k, v in sorted(query_params.items()) if v is not None
    )
    return f"cache:{method}:{path}:{sorted_qs}"


# ─── Cache decorator ────────────────────────────────────────────────


def cache_response(ttl_seconds: int = 300):
    """Decorator that caches the JSON response body in Redis.

    Usage::

        @router.get("/v1/entities")
        @cache_response(ttl_seconds=300)
        def list_entities(...):
            ...

    The decorator inspects the incoming ``Request`` object (which FastAPI
    injects automatically) to build the cache key.  If the handler returns
    a dict or list, it is serialised to JSON for storage; if it returns a
    FastAPI ``Response`` subclass, caching is skipped (file downloads,
    custom media types, etc.).

    On cache hit the stored JSON is returned as a ``JSONResponse`` with an
    ``X-Cache: HIT`` header.  On miss the handler runs normally and the
    result is stored with the configured TTL.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global _cache_hits, _cache_misses

            # If Redis is not available, run handler normally.
            if not _redis_available or _redis_client is None:
                return func(*args, **kwargs)

            # Extract Request from kwargs (FastAPI injects it).
            from starlette.requests import Request
            from starlette.responses import Response as StarletteResponse

            request: Request | None = kwargs.get("request")

            # If we cannot find the Request, try positional args or
            # the FastAPI Response object to sniff the request.
            if request is None:
                # Look through kwargs for anything that is a Request.
                for v in kwargs.values():
                    if isinstance(v, Request):
                        request = v
                        break

            if request is None:
                # Cannot build cache key without a request — skip cache.
                _cache_misses += 1
                return func(*args, **kwargs)

            method = request.method
            path = request.url.path
            query_params = dict(request.query_params)
            cache_key = _build_cache_key(method, path, query_params)

            # Try cache lookup.
            try:
                cached = _redis_client.get(cache_key)
                if cached is not None:
                    _cache_hits += 1
                    from fastapi.responses import JSONResponse
                    data = json.loads(cached)
                    resp = JSONResponse(content=data)
                    resp.headers["X-Cache"] = "HIT"
                    resp.headers["X-Cache-Key"] = cache_key
                    return resp
            except Exception:
                logger.debug("Redis GET failed for %s", cache_key, exc_info=True)

            _cache_misses += 1

            # Run the actual handler.
            result = func(*args, **kwargs)

            # Cache dict/list results directly.
            if isinstance(result, (dict, list)):
                try:
                    serialized = json.dumps(result, ensure_ascii=False, default=str)
                    _redis_client.setex(cache_key, ttl_seconds, serialized)
                except Exception:
                    logger.debug("Redis SET failed for %s", cache_key, exc_info=True)
            else:
                # Also handle JSONResponse (used by admin endpoints).
                from fastapi.responses import JSONResponse
                if isinstance(result, JSONResponse):
                    try:
                        body = result.body.decode("utf-8")
                        _redis_client.setex(cache_key, ttl_seconds, body)
                    except Exception:
                        logger.debug("Redis SET failed for %s", cache_key, exc_info=True)

            return result

        return wrapper

    return decorator


# ─── Cache invalidation ─────────────────────────────────────────────


def invalidate_pattern(pattern: str) -> int:
    """Delete all cache keys matching a glob pattern.

    Example: invalidate_pattern("cache:GET:/v1/entities*") clears all
    cached entity list/detail responses.

    Returns the number of keys deleted (0 if Redis unavailable).
    """
    if not _redis_available or _redis_client is None:
        return 0
    try:
        keys = list(_redis_client.scan_iter(match=pattern, count=500))
        if keys:
            return _redis_client.delete(*keys)
        return 0
    except Exception:
        logger.warning("Cache invalidation failed for pattern %s", pattern, exc_info=True)
        return 0


def flush_cache() -> int:
    """Delete ALL cache:* keys (full flush).

    Returns the number of keys deleted.
    """
    return invalidate_pattern("cache:*")


# ─── Cache stats ─────────────────────────────────────────────────────


def get_cache_stats() -> dict:
    """Return cache statistics.

    Includes: connection status, total cached keys, in-process hit/miss
    counters, and Redis memory usage.
    """
    stats: dict[str, Any] = {
        "redis_connected": False,
        "total_cached_keys": 0,
        "cache_hits": _cache_hits,
        "cache_misses": _cache_misses,
        "hit_ratio": 0.0,
        "memory_used_bytes": 0,
        "memory_used_human": "0B",
    }

    if not _redis_available or _redis_client is None:
        return stats

    try:
        _redis_client.ping()
        stats["redis_connected"] = True

        # Count cache:* keys.
        count = 0
        for _ in _redis_client.scan_iter(match="cache:*", count=500):
            count += 1
        stats["total_cached_keys"] = count

        # Hit ratio.
        total = _cache_hits + _cache_misses
        if total > 0:
            stats["hit_ratio"] = round(_cache_hits / total, 4)

        # Memory info.
        info = _redis_client.info("memory")
        stats["memory_used_bytes"] = info.get("used_memory", 0)
        stats["memory_used_human"] = info.get("used_memory_human", "0B")

    except Exception:
        logger.warning("Failed to collect cache stats", exc_info=True)
        stats["redis_connected"] = False

    return stats
