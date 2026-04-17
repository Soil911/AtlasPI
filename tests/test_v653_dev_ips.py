"""v6.53: tests per dev IPs management + filter integration."""

import datetime

import pytest

from src.db.models import ApiRequestLog, KnownDevIp


def _cleanup(db):
    db.query(ApiRequestLog).delete()
    db.query(KnownDevIp).delete()
    db.commit()


def _insert_log(db, client_ip: str, path: str = "/v1/entities"):
    log = ApiRequestLog(
        timestamp="2026-04-17T12:00:00",
        method="GET",
        path=path,
        status_code=200,
        response_time_ms=10.0,
        client_ip=client_ip,
        user_agent="Mozilla/5.0 Firefox/121.0",
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


# ─── Endpoint POST /admin/dev-ips/mark-current ───────────────────

def test_mark_current_creates_record(client, db):
    _cleanup(db)
    # TestClient sets client.host = "testclient" by default — FastAPI
    # _get_client_ip returns that. We just check response shape.
    r = client.post("/admin/dev-ips/mark-current?label=unittest")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "marked"
    assert "ip" in data
    assert data["label"] == "unittest"
    assert "marked_at" in data
    _cleanup(db)


def test_mark_current_idempotent(client, db):
    _cleanup(db)
    r1 = client.post("/admin/dev-ips/mark-current?label=first")
    assert r1.status_code == 200
    assert r1.json()["status"] == "marked"

    # Second call for same IP → already_marked
    r2 = client.post("/admin/dev-ips/mark-current?label=updated")
    assert r2.status_code == 200
    assert r2.json()["status"] == "already_marked"
    assert r2.json()["label"] == "updated"  # label updates
    _cleanup(db)


# ─── Endpoint GET /admin/dev-ips ──────────────────────────────────

def test_list_dev_ips_empty(client, db):
    _cleanup(db)
    r = client.get("/admin/dev-ips")
    assert r.status_code == 200
    assert r.json()["count"] == 0
    assert r.json()["dev_ips"] == []


def test_list_dev_ips_populated(client, db):
    _cleanup(db)
    client.post("/admin/dev-ips/mark-current?label=laptop")
    r = client.get("/admin/dev-ips")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 1
    assert data["dev_ips"][0]["label"] == "laptop"
    _cleanup(db)


# ─── Endpoint DELETE /admin/dev-ips/{id} ──────────────────────────

def test_delete_dev_ip(client, db):
    _cleanup(db)
    r1 = client.post("/admin/dev-ips/mark-current")
    id_ = r1.json()["id"]
    r2 = client.delete(f"/admin/dev-ips/{id_}")
    assert r2.status_code == 200
    assert r2.json()["status"] == "deleted"

    # Now list empty
    r3 = client.get("/admin/dev-ips")
    assert r3.json()["count"] == 0
    _cleanup(db)


def test_delete_nonexistent_dev_ip(client, db):
    _cleanup(db)
    r = client.delete("/admin/dev-ips/99999")
    assert r.status_code == 404


# ─── Filter integration ─────────────────────────────────────────

def test_external_filter_excludes_dev_ips(client, db):
    """Verify that marking an IP as dev excludes it from external scope."""
    _cleanup(db)

    # Insert logs from two IPs (middleware will add /admin/* logs too but
    # those are filtered by path in external scope).
    _insert_log(db, client_ip="91.13.45.6")
    _insert_log(db, client_ip="91.13.45.6")
    _insert_log(db, client_ip="8.8.8.8")

    # Before marking: external counts 91.13.45.6 AND 8.8.8.8 (and /admin calls filtered by path)
    r1 = client.get("/admin/analytics/data")
    baseline_external = r1.json()["summary"]["total_requests"]
    assert baseline_external >= 3  # 3 inserted + maybe 0 passing filter

    # Mark 91.13.45.6 as dev directly via model
    db.add(KnownDevIp(
        ip="91.13.45.6",
        label="test-dev",
        marked_at=datetime.datetime.now().isoformat(),
    ))
    db.commit()

    # After marking: 91.13.45.6 removed from external. Expect >= 2 fewer.
    r2 = client.get("/admin/analytics/data")
    after_mark = r2.json()["summary"]["total_requests"]
    assert after_mark <= baseline_external - 2, (
        f"Expected dev_ip filter to reduce count. baseline={baseline_external}, after={after_mark}"
    )

    # Scope=all still counts them (all_total > external_filtered)
    r3 = client.get("/admin/analytics/data?scope=all")
    all_total = r3.json()["summary"]["total_requests"]
    assert all_total >= after_mark + 2  # at least the 2 91.13.45.6 logs

    _cleanup(db)
