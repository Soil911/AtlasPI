"""v6.52: tests per filter external traffic in analytics."""

import pytest
from sqlalchemy.orm import Session

from src.api.routes.analytics import (
    apply_external_filter,
    _INTERNAL_IP_LIKES,
    _INTERNAL_IPS_EXACT,
    _INTERNAL_PATHS_EXACT,
    _INTERNAL_PATH_PREFIXES,
)
from src.db.models import ApiRequestLog


# ─── Constants ─────────────────────────────────────────────────

def test_internal_ip_patterns_present():
    assert "127.%" in _INTERNAL_IP_LIKES
    assert "10.%" in _INTERNAL_IP_LIKES
    assert "192.168.%" in _INTERNAL_IP_LIKES
    # Docker private class B 172.16 through 172.31
    for i in range(16, 32):
        assert f"172.{i}.%" in _INTERNAL_IP_LIKES


def test_internal_ips_exact():
    assert "::1" in _INTERNAL_IPS_EXACT
    assert "77.81.229.242" in _INTERNAL_IPS_EXACT  # VPS self


def test_internal_paths():
    assert "/health" in _INTERNAL_PATHS_EXACT
    assert "/metrics" in _INTERNAL_PATHS_EXACT
    assert "/admin" in _INTERNAL_PATH_PREFIXES
    assert "/static" in _INTERNAL_PATH_PREFIXES


# ─── Integration: filter queries correctly ────────────────────

def _insert_log(db, client_ip: str, path: str, user_agent: str = "curl/8.0", status: int = 200):
    log = ApiRequestLog(
        timestamp="2026-04-17T12:00:00",
        method="GET",
        path=path,
        status_code=status,
        response_time_ms=10.0,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def _cleanup(db):
    db.query(ApiRequestLog).delete()
    db.commit()


def test_filter_excludes_localhost(db):
    _cleanup(db)
    _insert_log(db, client_ip="127.0.0.1", path="/health")
    _insert_log(db, client_ip="8.8.8.8", path="/v1/entities")

    filtered = apply_external_filter(db.query(ApiRequestLog)).all()
    assert len(filtered) == 1
    assert filtered[0].client_ip == "8.8.8.8"
    _cleanup(db)


def test_filter_excludes_docker_ips(db):
    _cleanup(db)
    _insert_log(db, client_ip="172.18.0.5", path="/v1/entities")
    _insert_log(db, client_ip="172.31.255.1", path="/v1/entities")
    _insert_log(db, client_ip="1.2.3.4", path="/v1/entities")

    filtered = apply_external_filter(db.query(ApiRequestLog)).all()
    ips = [f.client_ip for f in filtered]
    assert "1.2.3.4" in ips
    assert "172.18.0.5" not in ips
    assert "172.31.255.1" not in ips
    _cleanup(db)


def test_filter_excludes_vps_self(db):
    _cleanup(db)
    _insert_log(db, client_ip="77.81.229.242", path="/v1/entities")
    _insert_log(db, client_ip="8.8.8.8", path="/v1/entities")

    filtered = apply_external_filter(db.query(ApiRequestLog)).all()
    assert len(filtered) == 1
    assert filtered[0].client_ip == "8.8.8.8"
    _cleanup(db)


def test_filter_excludes_health_metrics(db):
    _cleanup(db)
    _insert_log(db, client_ip="8.8.8.8", path="/health")
    _insert_log(db, client_ip="8.8.8.8", path="/metrics")
    _insert_log(db, client_ip="8.8.8.8", path="/v1/entities")

    filtered = apply_external_filter(db.query(ApiRequestLog)).all()
    paths = [f.path for f in filtered]
    assert "/v1/entities" in paths
    assert "/health" not in paths
    assert "/metrics" not in paths
    _cleanup(db)


def test_filter_excludes_admin_and_static(db):
    _cleanup(db)
    _insert_log(db, client_ip="8.8.8.8", path="/admin/analytics")
    _insert_log(db, client_ip="8.8.8.8", path="/admin/analytics/data")
    _insert_log(db, client_ip="8.8.8.8", path="/static/app.js")
    _insert_log(db, client_ip="8.8.8.8", path="/v1/entities")

    filtered = apply_external_filter(db.query(ApiRequestLog)).all()
    paths = [f.path for f in filtered]
    assert paths == ["/v1/entities"]
    _cleanup(db)


def test_filter_includes_public_ip_real_path(db):
    """Public IP + real API path → included."""
    _cleanup(db)
    _insert_log(db, client_ip="91.13.45.6", path="/v1/entities/42")
    _insert_log(db, client_ip="91.13.45.6", path="/v1/where-was?lat=41.9&lon=12.5")

    filtered = apply_external_filter(db.query(ApiRequestLog)).all()
    assert len(filtered) == 2
    _cleanup(db)


# ─── Endpoint contract ─────────────────────────────────────────

def test_analytics_data_default_scope_external(client, db):
    _cleanup(db)
    _insert_log(db, client_ip="127.0.0.1", path="/health")  # internal
    _insert_log(db, client_ip="8.8.8.8", path="/v1/entities")  # external

    r = client.get("/admin/analytics/data")
    assert r.status_code == 200
    data = r.json()
    assert data["summary"]["scope"] == "external"
    assert data["summary"]["total_requests"] == 1  # solo external
    assert data["summary"]["raw_total"] == 2
    assert data["summary"]["filtered_out"] == 1
    _cleanup(db)


def test_analytics_data_scope_all(client, db):
    _cleanup(db)
    _insert_log(db, client_ip="127.0.0.1", path="/health")
    _insert_log(db, client_ip="8.8.8.8", path="/v1/entities")

    r = client.get("/admin/analytics/data?scope=all")
    assert r.status_code == 200
    data = r.json()
    assert data["summary"]["scope"] == "all"
    assert data["summary"]["total_requests"] == 2
    assert data["summary"]["filtered_out"] == 0
    _cleanup(db)


def test_analytics_data_invalid_scope_422(client):
    r = client.get("/admin/analytics/data?scope=banana")
    assert r.status_code == 422
