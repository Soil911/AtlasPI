"""Tests for v6.21 — Redis caching layer.

These tests run WITHOUT a real Redis server.  The cache module must
degrade gracefully: no crashes, handlers run normally, stats return
zeroed values.
"""

import json
from unittest.mock import MagicMock, patch

import pytest


# ═══════════════════════════════════════════════════════════════════
# 1. Module import & graceful degradation
# ═══════════════════════════════════════════════════════════════════


def test_cache_module_importable():
    """src.cache can be imported without error."""
    from src import cache
    assert hasattr(cache, "cache_response")
    assert hasattr(cache, "get_cache_stats")
    assert hasattr(cache, "flush_cache")
    assert hasattr(cache, "invalidate_pattern")
    assert hasattr(cache, "init_redis")


def test_cache_stats_without_redis():
    """get_cache_stats() returns valid dict even with no Redis."""
    from src.cache import get_cache_stats
    stats = get_cache_stats()
    assert isinstance(stats, dict)
    assert stats["redis_connected"] is False
    assert stats["total_cached_keys"] == 0
    assert "cache_hits" in stats
    assert "cache_misses" in stats
    assert "hit_ratio" in stats


def test_flush_cache_without_redis():
    """flush_cache() returns 0 when Redis is not available."""
    from src.cache import flush_cache
    result = flush_cache()
    assert result == 0


def test_invalidate_pattern_without_redis():
    """invalidate_pattern() returns 0 when Redis is not available."""
    from src.cache import invalidate_pattern
    result = invalidate_pattern("cache:*")
    assert result == 0


def test_is_redis_available_without_redis():
    """is_redis_available() returns False when not connected."""
    from src.cache import is_redis_available
    assert is_redis_available() is False


def test_get_redis_without_connection():
    """get_redis() returns None when Redis is not configured."""
    from src.cache import get_redis
    assert get_redis() is None


# ═══════════════════════════════════════════════════════════════════
# 2. Cache key construction
# ═══════════════════════════════════════════════════════════════════


def test_cache_key_deterministic():
    """Same request produces the same cache key regardless of param order."""
    from src.cache import _build_cache_key
    key1 = _build_cache_key("GET", "/v1/entities", {"limit": "10", "offset": "0"})
    key2 = _build_cache_key("GET", "/v1/entities", {"offset": "0", "limit": "10"})
    assert key1 == key2


def test_cache_key_different_params():
    """Different query params produce different cache keys."""
    from src.cache import _build_cache_key
    key1 = _build_cache_key("GET", "/v1/entities", {"limit": "10"})
    key2 = _build_cache_key("GET", "/v1/entities", {"limit": "20"})
    assert key1 != key2


def test_cache_key_different_paths():
    """Different paths produce different cache keys."""
    from src.cache import _build_cache_key
    key1 = _build_cache_key("GET", "/v1/entities", {})
    key2 = _build_cache_key("GET", "/v1/events", {})
    assert key1 != key2


def test_cache_key_ignores_none_params():
    """None-valued params are excluded from cache key."""
    from src.cache import _build_cache_key
    key1 = _build_cache_key("GET", "/v1/entities", {"limit": "10", "type": None})
    key2 = _build_cache_key("GET", "/v1/entities", {"limit": "10"})
    assert key1 == key2


# ═══════════════════════════════════════════════════════════════════
# 3. Admin cache endpoints
# ═══════════════════════════════════════════════════════════════════


def test_cache_stats_endpoint(client):
    """GET /admin/cache-stats returns valid JSON."""
    r = client.get("/admin/cache-stats")
    assert r.status_code == 200
    d = r.json()
    assert "redis_connected" in d
    assert "total_cached_keys" in d
    assert "cache_hits" in d
    assert "cache_misses" in d
    assert "hit_ratio" in d
    assert "memory_used_bytes" in d


def test_cache_flush_endpoint(client):
    """POST /admin/cache/flush returns valid JSON."""
    r = client.post("/admin/cache/flush")
    assert r.status_code == 200
    d = r.json()
    assert "flushed" in d
    assert d["flushed"] == 0  # no Redis in test


# ═══════════════════════════════════════════════════════════════════
# 4. Decorator graceful degradation (no Redis)
# ═══════════════════════════════════════════════════════════════════


def test_cached_endpoint_still_works_without_redis(client):
    """Endpoints decorated with @cache_response work when Redis is down."""
    # /v1/entities is decorated — must still return data.
    r = client.get("/v1/entities?limit=5")
    assert r.status_code == 200
    d = r.json()
    assert "entities" in d
    assert d["count"] >= 1


def test_cached_event_endpoint_works_without_redis(client):
    """GET /v1/events works with cache decorator and no Redis."""
    r = client.get("/v1/events?limit=5")
    assert r.status_code == 200
    d = r.json()
    assert "events" in d


def test_cached_entity_detail_works_without_redis(client):
    """GET /v1/entities/1 works with cache decorator and no Redis."""
    r = client.get("/v1/entities/1")
    assert r.status_code == 200
    d = r.json()
    assert "name_original" in d


# ═══════════════════════════════════════════════════════════════════
# 5. Version bump
# ═══════════════════════════════════════════════════════════════════


def test_version_is_v621():
    """APP_VERSION should be >= 6.21.0."""
    from src.config import APP_VERSION
    assert APP_VERSION >= "6.21.0"
