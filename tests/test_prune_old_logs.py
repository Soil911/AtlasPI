"""Test della retention policy api_request_logs (v6.92.3 — audit R10)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def _make_log(db, days_ago: int, path: str = "/v1/entities") -> None:
    """Inserisce una riga api_request_logs con timestamp `days_ago` giorni fa."""
    from src.db.models import ApiRequestLog

    ts = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    db.add(ApiRequestLog(
        timestamp=ts,
        method="GET",
        path=path,
        query_string=None,
        status_code=200,
        response_time_ms=15.5,
        client_ip="127.0.0.1",
        user_agent="pytest",
        referer=None,
    ))
    db.commit()


def test_prune_dry_run_does_not_delete(db):
    """dry_run=True deve solo contare, non cancellare."""
    from scripts.prune_old_logs import prune_old_logs
    from src.db.models import ApiRequestLog

    _make_log(db, days_ago=200, path="/v1/test_dry_run_old")
    _make_log(db, days_ago=10, path="/v1/test_dry_run_recent")

    before = db.query(ApiRequestLog).count()
    deleted = prune_old_logs(days=90, dry_run=True)
    after = db.query(ApiRequestLog).count()

    assert deleted == 0  # dry-run sempre ritorna 0
    assert before == after  # nessuna cancellazione


def test_prune_actual_deletes_old_only(db):
    """days=90 deve cancellare righe > 90gg, lasciare quelle recenti."""
    from scripts.prune_old_logs import prune_old_logs
    from src.db.models import ApiRequestLog

    # Pulisco eventuali residui di altri test
    db.query(ApiRequestLog).delete()
    db.commit()

    _make_log(db, days_ago=200, path="/v1/test_actual_old")
    _make_log(db, days_ago=100, path="/v1/test_actual_borderline_old")
    _make_log(db, days_ago=89, path="/v1/test_actual_borderline_recent")
    _make_log(db, days_ago=1, path="/v1/test_actual_recent")

    assert db.query(ApiRequestLog).count() == 4

    deleted = prune_old_logs(days=90, dry_run=False)
    assert deleted == 2  # i due > 90 giorni

    remaining = db.query(ApiRequestLog).all()
    paths = sorted(r.path for r in remaining)
    assert paths == ["/v1/test_actual_borderline_recent", "/v1/test_actual_recent"]


def test_prune_zero_when_nothing_old(db):
    """Tabella senza righe vecchie: deleted == 0, no crash."""
    from scripts.prune_old_logs import prune_old_logs
    from src.db.models import ApiRequestLog

    db.query(ApiRequestLog).delete()
    db.commit()

    _make_log(db, days_ago=5, path="/v1/test_only_recent")

    deleted = prune_old_logs(days=90, dry_run=False)
    assert deleted == 0
    assert db.query(ApiRequestLog).count() == 1


def test_prune_idempotent(db):
    """Doppio prune consecutivo: secondo deve ritornare 0."""
    from scripts.prune_old_logs import prune_old_logs
    from src.db.models import ApiRequestLog

    db.query(ApiRequestLog).delete()
    db.commit()

    _make_log(db, days_ago=200, path="/v1/test_idem_old")

    first = prune_old_logs(days=90, dry_run=False)
    second = prune_old_logs(days=90, dry_run=False)

    assert first == 1
    assert second == 0
    assert db.query(ApiRequestLog).count() == 0
