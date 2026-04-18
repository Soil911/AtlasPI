"""Prometheus metrics endpoint — /metrics.

Exposes basic operational metrics in the Prometheus text exposition format.
Free, no dependencies beyond the standard library — we emit the format by
hand since adding prometheus_client would be overkill for a few counters.

v6.66 FIX 6: endpoint protetto da IP allowlist + basic auth come fallback.
Configurazione via env (default: deny tutto se non configurato):
- METRICS_ALLOWED_IPS: comma-separated list (es. "127.0.0.1,10.0.0.5").
  Match anche su X-Forwarded-For (primo hop). "*" disabilita la protezione.
- METRICS_USER / METRICS_PASS: basic auth come fallback se gli IP non
  combaciano. Se nessuno dei due e' configurato, l'endpoint risponde 403.

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
        basic_auth:
          username: {{METRICS_USER}}
          password: {{METRICS_PASS}}
"""

from __future__ import annotations

import base64
import os
import time
from collections import defaultdict
from threading import Lock

from fastapi import APIRouter, Depends, HTTPException, Request
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


# ─── v6.66 FIX 6: access control for /metrics ─────────────────────

def _metrics_allowed_ips() -> set[str]:
    """Parse METRICS_ALLOWED_IPS env var into a set of IPs.

    "*" disabilita completamente la protezione IP (convenience per dev).
    Default: vuoto (nessun IP ammesso → tutte le richieste devono passare
    per basic auth oppure vengono rifiutate con 403).
    """
    raw = os.getenv("METRICS_ALLOWED_IPS", "").strip()
    if not raw:
        return set()
    return {ip.strip() for ip in raw.split(",") if ip.strip()}


def _extract_client_ip(request: Request) -> str:
    """Ricava il client IP considerando X-Forwarded-For (reverse proxy Nginx)."""
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    if request.client:
        return request.client.host
    return ""


def _check_basic_auth(request: Request) -> bool:
    """True se la richiesta ha Authorization: Basic valido con METRICS_USER/PASS."""
    user = os.getenv("METRICS_USER", "").strip()
    pwd = os.getenv("METRICS_PASS", "").strip()
    if not user or not pwd:
        return False
    auth_header = request.headers.get("authorization", "")
    if not auth_header.lower().startswith("basic "):
        return False
    try:
        encoded = auth_header.split(" ", 1)[1].strip()
        decoded = base64.b64decode(encoded).decode("utf-8", errors="ignore")
        candidate_user, candidate_pwd = decoded.split(":", 1)
    except (ValueError, IndexError):
        return False
    return candidate_user == user and candidate_pwd == pwd


def _authorize_metrics(request: Request) -> None:
    """Raise 403 se la richiesta a /metrics non e' autorizzata.

    Policy:
    1. Se METRICS_ALLOWED_IPS contiene "*" → passa tutti (dev only).
    2. Se client IP e' in METRICS_ALLOWED_IPS → passa.
    3. Se basic auth matcha METRICS_USER/METRICS_PASS → passa.
    4. Altrimenti 403 con WWW-Authenticate header.

    Default (nessuna env): deny. Deliberato per evitare leak in ambienti
    misconfigurati.
    """
    allowed = _metrics_allowed_ips()

    if "*" in allowed:
        return

    client_ip = _extract_client_ip(request)
    if client_ip and client_ip in allowed:
        return

    if _check_basic_auth(request):
        return

    raise HTTPException(
        status_code=403,
        detail="Access denied. Configure METRICS_ALLOWED_IPS or supply Basic auth (METRICS_USER/METRICS_PASS).",
        headers={"WWW-Authenticate": 'Basic realm="atlaspi-metrics"'},
    )


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
def prometheus_metrics(request: Request, db: Session = Depends(get_db)) -> str:
    """Return Prometheus-format metrics for scraping.

    v6.66 FIX 6: require IP allowlist or Basic auth. See module docstring
    for configuration.
    """
    _authorize_metrics(request)

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
