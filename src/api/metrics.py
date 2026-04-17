"""Prometheus metrics endpoint — /metrics.

Exposes basic operational metrics in the Prometheus text exposition format.
Free, no dependencies beyond the standard library — we emit the format by
hand since adding prometheus_client would be overkill for a few counters.

Metrics exposed:
- atlaspi_requests_total{path,method,status} — counter
- atlaspi_request_duration_seconds_sum{path} — histogram sum
- atlaspi_request_duration_seconds_count{path} — histogram count
- atlaspi_entities_total — gauge
- atlaspi_events_total — gauge
- atlaspi_periods_total — gauge
- atlaspi_chains_total — gauge
- atlaspi_suggestions_pending — gauge
- atlaspi_suggestions_accepted — gauge
- atlaspi_process_uptime_seconds — gauge

Scrape with Prometheus/Grafana by adding a scrape config:
    scrape_configs:
      - job_name: atlaspi
        static_configs:
          - targets: ['atlaspi.cra-srl.com:443']
        scheme: https
        metrics_path: /metrics
"""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.config import PROCESS_START_TIME
from src.db.database import get_db
from src.db.models import (
    AiSuggestion,
    DynastyChain,
    GeoEntity,
    HistoricalEvent,
    HistoricalPeriod,
)

router = APIRouter(tags=["metrics"])


# ─── In-memory counters (reset on process restart — fine for dashboards) ──

_lock = Lock()
_request_counter: dict[tuple[str, str, int], int] = defaultdict(int)
_duration_sum: dict[str, float] = defaultdict(float)
_duration_count: dict[str, int] = defaultdict(int)


def record_request(path: str, method: str, status_code: int, duration_s: float) -> None:
    """Called from middleware — records a request observation."""
    # Collapse long paths with IDs to a template so we don't explode cardinality
    template = _path_template(path)
    with _lock:
        _request_counter[(template, method, status_code)] += 1
        _duration_sum[template] += duration_s
        _duration_count[template] += 1


def _path_template(path: str) -> str:
    """Replace numeric IDs and date strings with placeholders.

    /v1/entities/42 -> /v1/entities/{id}
    /v1/events/on-this-day/07-14 -> /v1/events/on-this-day/{mm_dd}
    /v1/events/at-date/1789-07-14 -> /v1/events/at-date/{date}
    """
    import re
    p = path
    p = re.sub(r"/\d+(/|$)", r"/{id}\1", p)
    p = re.sub(r"/\d{2}-\d{2}(/|$)", r"/{mm_dd}\1", p)
    p = re.sub(r"/-?\d{4}-\d{2}-\d{2}(/|$)", r"/{date}\1", p)
    # Trim after '?' if any slipped in
    p = p.split("?")[0]
    return p


def _render_counter(name: str, help_text: str, values: dict) -> str:
    """Render a Prometheus counter."""
    lines = [f"# HELP {name} {help_text}", f"# TYPE {name} counter"]
    for labels_tuple, val in values.items():
        if isinstance(labels_tuple, tuple):
            # (path, method, status_code)
            labels = ",".join(f'{k}="{v}"' for k, v in zip(
                ["path", "method", "status"], labels_tuple
            ))
        else:
            labels = ""
        if labels:
            lines.append(f'{name}{{{labels}}} {val}')
        else:
            lines.append(f"{name} {val}")
    return "\n".join(lines)


def _render_gauge(name: str, help_text: str, value: float) -> str:
    """Render a Prometheus gauge."""
    return f"# HELP {name} {help_text}\n# TYPE {name} gauge\n{name} {value}"


@router.get("/metrics", include_in_schema=False, response_class=PlainTextResponse)
def prometheus_metrics(db: Session = Depends(get_db)) -> str:
    """Return Prometheus-format metrics for scraping."""
    lines: list[str] = []

    # Request counters
    with _lock:
        snap_counters = dict(_request_counter)
        snap_sum = dict(_duration_sum)
        snap_count = dict(_duration_count)

    if snap_counters:
        lines.append(_render_counter(
            "atlaspi_requests_total",
            "Total HTTP requests, by path template, method, status code",
            snap_counters,
        ))

    # Duration histogram
    if snap_sum:
        lines.append('# HELP atlaspi_request_duration_seconds_sum Sum of request durations by path')
        lines.append('# TYPE atlaspi_request_duration_seconds_sum counter')
        for path, total in snap_sum.items():
            lines.append(f'atlaspi_request_duration_seconds_sum{{path="{path}"}} {total:.4f}')
        lines.append('# HELP atlaspi_request_duration_seconds_count Count of requests by path')
        lines.append('# TYPE atlaspi_request_duration_seconds_count counter')
        for path, c in snap_count.items():
            lines.append(f'atlaspi_request_duration_seconds_count{{path="{path}"}} {c}')

    # Dataset gauges
    entities_count = db.query(func.count(GeoEntity.id)).scalar() or 0
    events_count = db.query(func.count(HistoricalEvent.id)).scalar() or 0
    periods_count = db.query(func.count(HistoricalPeriod.id)).scalar() or 0
    chains_count = db.query(func.count(DynastyChain.id)).scalar() or 0
    pending_sug = (
        db.query(func.count(AiSuggestion.id))
        .filter(AiSuggestion.status == "pending").scalar() or 0
    )
    accepted_sug = (
        db.query(func.count(AiSuggestion.id))
        .filter(AiSuggestion.status == "accepted").scalar() or 0
    )

    lines.append(_render_gauge("atlaspi_entities_total", "Total geopolitical entities", entities_count))
    lines.append(_render_gauge("atlaspi_events_total", "Total historical events", events_count))
    lines.append(_render_gauge("atlaspi_periods_total", "Total historical periods", periods_count))
    lines.append(_render_gauge("atlaspi_chains_total", "Total dynasty chains", chains_count))
    lines.append(_render_gauge("atlaspi_suggestions_pending", "Pending AI suggestions", pending_sug))
    lines.append(_render_gauge("atlaspi_suggestions_accepted", "Accepted AI suggestions awaiting daily run", accepted_sug))

    # Uptime
    uptime = time.time() - PROCESS_START_TIME
    lines.append(_render_gauge("atlaspi_process_uptime_seconds", "Seconds since process started", round(uptime, 1)))

    return "\n".join(lines) + "\n"
