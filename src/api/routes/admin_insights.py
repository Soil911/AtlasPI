"""AI Co-Founder Intelligence Layer — v6.15.

GET /admin/insights          — traffic analysis and usage patterns
GET /admin/coverage-report   — data quality and completeness analysis
GET /admin/suggestions       — smart suggestions for what to add next

These endpoints analyse the existing DB (api_request_logs, geo_entities,
historical_events, dynasty_chains, etc.) and return structured JSON that
an AI co-founder (or human operator) can act on.
"""

from __future__ import annotations

import logging
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import func, distinct, or_
from sqlalchemy.orm import Session

from src.cache import cache_response
from src.db.database import get_db
from src.db.models import (
    ApiRequestLog,
    ChainLink,
    DynastyChain,
    EventEntityLink,
    GeoEntity,
    HistoricalCity,
    HistoricalEvent,
    TradeRoute,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin"])

# ─── Known internal IPs (VPS, localhost, dev machines) ─────────────
INTERNAL_IPS = frozenset({
    "127.0.0.1",
    "::1",
    "77.81.229.242",      # VPS itself
    "172.17.0.1",         # Docker bridge
    "172.18.0.1",         # Docker compose network
    "10.0.0.1",           # Generic private
    "testclient",         # FastAPI TestClient
})

# ─── User-Agent classification patterns ────────────────────────────
_BOT_PATTERNS = re.compile(
    r"(bot|crawl|spider|slurp|baiduspider|yandex|duckduck|semrush|ahref|"
    r"mj12bot|dotbot|petalbot|bytespider|gptbot|chatgpt|claudebot|"
    r"anthropic|google|bing|facebook|twitter|telegram|whatsapp|"
    r"curl|wget|httpie|python-requests|python-urllib|go-http|"
    r"postman|insomnia|axios|node-fetch|scrapy|headless)",
    re.IGNORECASE,
)
_BROWSER_PATTERNS = re.compile(
    r"(mozilla|chrome|safari|firefox|edge|opera|brave|vivaldi|samsung)",
    re.IGNORECASE,
)


def _classify_ua(ua: str | None) -> str:
    """Classify a user-agent string into bot/browser/api_client."""
    if not ua:
        return "unknown"
    if _BOT_PATTERNS.search(ua):
        return "bot_or_crawler"
    if _BROWSER_PATTERNS.search(ua):
        return "browser"
    return "api_client"


def _lat_to_continent(lat: float | None, lon: float | None) -> str:
    """Very rough continent assignment from capital coordinates.

    Not geographically precise — just good enough for coverage buckets.
    """
    if lat is None or lon is None:
        return "Unknown"
    if lat > 35 and lon > -30 and lon < 60:
        return "Europe"
    # East/Southeast Asia: lon >= 100 takes priority over Central/South
    if lon >= 100 and lon < 180:
        return "Asia (East/Southeast)"
    if lat > 12 and lon >= 60 and lon < 100:
        return "Asia (Central/South)"
    if lat <= 12 and lon >= 60 and lon < 100:
        return "Asia (Central/South)"
    if lat < 35 and lon >= -20 and lon < 55:
        return "Africa / Middle East"
    if lat > 15 and lon >= -170 and lon < -30:
        return "Americas (North)"
    if lat <= 15 and lon >= -170 and lon < -30:
        return "Americas (South/Central)"
    if lat < -10 and lon >= 100:
        return "Oceania"
    # Fallback for edge cases
    if lon >= 25 and lon < 60 and lat > 10 and lat <= 45:
        return "Africa / Middle East"
    return "Other"


def _year_to_era(year: int) -> str:
    """Map a year to a human-readable era bucket."""
    if year < -3000:
        return "Pre-3000 BCE"
    if year < -1000:
        return "3000-1000 BCE"
    if year < -500:
        return "1000-500 BCE"
    if year < 0:
        return "500-1 BCE"
    if year < 500:
        return "1-500 CE"
    if year < 1000:
        return "500-1000 CE"
    if year < 1500:
        return "1000-1500 CE"
    if year < 1800:
        return "1500-1800 CE"
    if year < 1900:
        return "1800-1900 CE"
    if year < 2000:
        return "1900-2000 CE"
    return "2000-present"


# ═══════════════════════════════════════════════════════════════════
# 1. Traffic Insights
# ═══════════════════════════════════════════════════════════════════


@router.get(
    "/admin/insights",
    summary="Traffic and usage insights (JSON)",
    description="Analisi del traffico API: volume, endpoint, errori, user agent, utenti esterni, ore di punta.",
    include_in_schema=False,
)
@cache_response(ttl_seconds=300)
def insights(request: Request, db: Session = Depends(get_db)):
    """Structured traffic insights from api_request_logs."""

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    # We use string comparisons on the ISO timestamp column.
    # This works because ISO 8601 strings sort lexicographically.
    day_ago = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

    # ── Traffic summary ────────────────────────────────────────
    total_all = db.query(func.count(ApiRequestLog.id)).scalar() or 0

    total_24h = (
        db.query(func.count(ApiRequestLog.id))
        .filter(ApiRequestLog.timestamp >= day_ago)
        .scalar() or 0
    )
    total_7d = (
        db.query(func.count(ApiRequestLog.id))
        .filter(ApiRequestLog.timestamp >= week_ago)
        .scalar() or 0
    )
    total_30d = (
        db.query(func.count(ApiRequestLog.id))
        .filter(ApiRequestLog.timestamp >= month_ago)
        .scalar() or 0
    )

    unique_ips_30d = (
        db.query(func.count(distinct(ApiRequestLog.client_ip)))
        .filter(ApiRequestLog.timestamp >= month_ago)
        .scalar() or 0
    )

    avg_response = (
        db.query(func.avg(ApiRequestLog.response_time_ms))
        .filter(ApiRequestLog.timestamp >= month_ago)
        .scalar()
    )
    avg_response = round(avg_response, 2) if avg_response else 0.0

    traffic_summary = {
        "total_all_time": total_all,
        "total_24h": total_24h,
        "total_7d": total_7d,
        "total_30d": total_30d,
        "unique_ips_30d": unique_ips_30d,
        "avg_response_time_ms_30d": avg_response,
    }

    # ── Top endpoints (last 30 days) ──────────────────────────
    te_rows = (
        db.query(
            ApiRequestLog.path,
            func.count(ApiRequestLog.id).label("hits"),
            func.avg(ApiRequestLog.response_time_ms).label("avg_ms"),
        )
        .filter(ApiRequestLog.timestamp >= month_ago)
        .group_by(ApiRequestLog.path)
        .order_by(func.count(ApiRequestLog.id).desc())
        .limit(20)
        .all()
    )
    top_endpoints = [
        {"path": r.path, "hits": r.hits, "avg_ms": round(r.avg_ms or 0, 2)}
        for r in te_rows
    ]

    # ── Error analysis (last 30 days) ─────────────────────────
    error_rows = (
        db.query(
            ApiRequestLog.status_code,
            ApiRequestLog.path,
            func.count(ApiRequestLog.id).label("count"),
        )
        .filter(
            ApiRequestLog.timestamp >= month_ago,
            ApiRequestLog.status_code >= 400,
        )
        .group_by(ApiRequestLog.status_code, ApiRequestLog.path)
        .order_by(func.count(ApiRequestLog.id).desc())
        .limit(20)
        .all()
    )
    errors_4xx = [
        {"status": r.status_code, "path": r.path, "count": r.count}
        for r in error_rows if 400 <= r.status_code < 500
    ]
    errors_5xx = [
        {"status": r.status_code, "path": r.path, "count": r.count}
        for r in error_rows if r.status_code >= 500
    ]
    error_analysis = {
        "total_4xx": sum(e["count"] for e in errors_4xx),
        "total_5xx": sum(e["count"] for e in errors_5xx),
        "top_4xx_paths": errors_4xx[:10],
        "top_5xx_paths": errors_5xx[:10],
    }

    # ── User agent analysis ───────────────────────────────────
    ua_rows = (
        db.query(ApiRequestLog.user_agent)
        .filter(ApiRequestLog.timestamp >= month_ago)
        .all()
    )
    ua_counts: dict[str, int] = Counter()
    for (ua,) in ua_rows:
        ua_counts[_classify_ua(ua)] += 1
    user_agent_analysis = dict(ua_counts)

    # ── External users ────────────────────────────────────────
    ip_rows = (
        db.query(
            ApiRequestLog.client_ip,
            func.count(ApiRequestLog.id).label("hits"),
            func.max(ApiRequestLog.timestamp).label("last_seen"),
        )
        .filter(ApiRequestLog.timestamp >= month_ago)
        .group_by(ApiRequestLog.client_ip)
        .order_by(func.count(ApiRequestLog.id).desc())
        .all()
    )
    external_users = [
        {"ip": r.client_ip, "hits": r.hits, "last_seen": r.last_seen}
        for r in ip_rows
        if r.client_ip not in INTERNAL_IPS
    ]

    # ── Peak hours (UTC) ──────────────────────────────────────
    # Extract hour from the ISO timestamp: "2026-04-16T14:30:00" → "14"
    hour_col = func.substr(ApiRequestLog.timestamp, 12, 2).label("hour")
    ph_rows = (
        db.query(hour_col, func.count(ApiRequestLog.id).label("count"))
        .filter(ApiRequestLog.timestamp >= month_ago)
        .group_by(hour_col)
        .order_by(hour_col)
        .all()
    )
    peak_hours = [
        {"hour_utc": r.hour or "??", "requests": r.count}
        for r in ph_rows
    ]

    return JSONResponse(
        content={
            "generated_at": now_str,
            "traffic_summary": traffic_summary,
            "top_endpoints": top_endpoints,
            "error_analysis": error_analysis,
            "user_agent_analysis": user_agent_analysis,
            "external_users": external_users[:30],
            "peak_hours": peak_hours,
        },
        headers={"Cache-Control": "public, max-age=300"},
    )


# ═══════════════════════════════════════════════════════════════════
# 2. Coverage Report
# ═══════════════════════════════════════════════════════════════════


@router.get(
    "/admin/coverage-report",
    summary="Data coverage and quality report (JSON)",
    description="Analisi della copertura dati: distribuzione geografica, temporale, confidenza, confini, catene.",
    include_in_schema=False,
)
@cache_response(ttl_seconds=600)
def coverage_report(request: Request, db: Session = Depends(get_db)):
    """Analyse data quality across entities, events, chains."""

    # ── Entity counts ─────────────────────────────────────────
    total_entities = db.query(func.count(GeoEntity.id)).scalar() or 0
    total_events = db.query(func.count(HistoricalEvent.id)).scalar() or 0
    total_chains = db.query(func.count(DynastyChain.id)).scalar() or 0
    total_cities = db.query(func.count(HistoricalCity.id)).scalar() or 0
    total_routes = db.query(func.count(TradeRoute.id)).scalar() or 0

    # ── By region (using capital coordinates) ─────────────────
    entities = db.query(
        GeoEntity.id,
        GeoEntity.capital_lat,
        GeoEntity.capital_lon,
        GeoEntity.year_start,
        GeoEntity.year_end,
        GeoEntity.confidence_score,
        GeoEntity.boundary_geojson,
        GeoEntity.entity_type,
    ).all()

    region_counts: dict[str, int] = Counter()
    type_counts: dict[str, int] = Counter()
    for e in entities:
        region_counts[_lat_to_continent(e.capital_lat, e.capital_lon)] += 1
        type_counts[e.entity_type or "unknown"] += 1

    by_region = [
        {"region": r, "entity_count": c}
        for r, c in sorted(region_counts.items(), key=lambda x: -x[1])
    ]
    by_type = [
        {"entity_type": t, "count": c}
        for t, c in sorted(type_counts.items(), key=lambda x: -x[1])
    ]

    # ── By era ────────────────────────────────────────────────
    era_entity_counts: dict[str, int] = Counter()
    for e in entities:
        era_entity_counts[_year_to_era(e.year_start)] += 1

    event_years = db.query(HistoricalEvent.year).all()
    era_event_counts: dict[str, int] = Counter()
    for (y,) in event_years:
        era_event_counts[_year_to_era(y)] += 1

    # Ordered eras for display
    _era_order = [
        "Pre-3000 BCE", "3000-1000 BCE", "1000-500 BCE", "500-1 BCE",
        "1-500 CE", "500-1000 CE", "1000-1500 CE", "1500-1800 CE",
        "1800-1900 CE", "1900-2000 CE", "2000-present",
    ]
    by_era = [
        {
            "era": era,
            "entities": era_entity_counts.get(era, 0),
            "events": era_event_counts.get(era, 0),
        }
        for era in _era_order
    ]

    # ── Confidence distribution ───────────────────────────────
    def _confidence_histogram(scores):
        buckets = {"0.0-0.3": 0, "0.3-0.5": 0, "0.5-0.7": 0, "0.7-0.9": 0, "0.9-1.0": 0}
        for s in scores:
            if s < 0.3:
                buckets["0.0-0.3"] += 1
            elif s < 0.5:
                buckets["0.3-0.5"] += 1
            elif s < 0.7:
                buckets["0.5-0.7"] += 1
            elif s < 0.9:
                buckets["0.7-0.9"] += 1
            else:
                buckets["0.9-1.0"] += 1
        return buckets

    entity_confidence = [e.confidence_score for e in entities]
    event_confidence_rows = db.query(HistoricalEvent.confidence_score).all()
    event_confidence = [r[0] for r in event_confidence_rows]

    confidence_distribution = {
        "entities": _confidence_histogram(entity_confidence),
        "events": _confidence_histogram(event_confidence),
    }

    # ── Boundary coverage ─────────────────────────────────────
    with_boundary = sum(1 for e in entities if e.boundary_geojson)
    boundary_coverage = {
        "total_entities": total_entities,
        "with_boundary": with_boundary,
        "without_boundary": total_entities - with_boundary,
        "percentage": round(with_boundary / total_entities * 100, 1) if total_entities else 0,
    }

    # ── Date precision coverage (v6.14) ───────────────────────
    dp_rows = db.query(
        HistoricalEvent.date_precision,
        func.count(HistoricalEvent.id).label("count"),
    ).group_by(HistoricalEvent.date_precision).all()

    date_precision_map = {(r.date_precision or "NONE"): r.count for r in dp_rows}
    sub_annual = sum(
        v for k, v in date_precision_map.items()
        if k in ("DAY", "MONTH", "SEASON")
    )
    date_precision_coverage = {
        "by_precision": date_precision_map,
        "sub_annual_count": sub_annual,
        "sub_annual_percentage": round(sub_annual / total_events * 100, 1) if total_events else 0,
    }

    # ── Chain coverage ────────────────────────────────────────
    entity_ids_in_chains = set(
        r[0] for r in db.query(distinct(ChainLink.entity_id)).all()
    )
    chain_coverage = {
        "entities_in_chains": len(entity_ids_in_chains),
        "orphan_entities": total_entities - len(entity_ids_in_chains),
        "chain_coverage_pct": round(
            len(entity_ids_in_chains) / total_entities * 100, 1
        ) if total_entities else 0,
    }

    # ── Overall data completeness score (0-100) ──────────────
    # Weighted composite: boundary 20%, confidence 20%, chains 15%,
    # date precision 15%, region balance 15%, era balance 15%.
    score = 0.0

    # Boundary: % with boundary → score 0-20
    score += (boundary_coverage["percentage"] / 100) * 20

    # Confidence: avg confidence * 20
    avg_conf = sum(entity_confidence) / len(entity_confidence) if entity_confidence else 0
    score += avg_conf * 20

    # Chain coverage: % in chains → score 0-15
    score += (chain_coverage["chain_coverage_pct"] / 100) * 15

    # Date precision: % sub-annual → score 0-15
    score += (date_precision_coverage["sub_annual_percentage"] / 100) * 15

    # Region balance: more regions represented = better (0-15)
    # 8 regions = max, penalise if concentrated
    region_variety = min(len(region_counts), 8) / 8
    score += region_variety * 15

    # Era balance: more eras with entities = better (0-15)
    eras_with_entities = sum(1 for e in by_era if e["entities"] > 0)
    era_variety = min(eras_with_entities, len(_era_order)) / len(_era_order)
    score += era_variety * 15

    return JSONResponse(
        content={
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "totals": {
                "entities": total_entities,
                "events": total_events,
                "chains": total_chains,
                "cities": total_cities,
                "trade_routes": total_routes,
            },
            "by_region": by_region,
            "by_type": by_type,
            "by_era": by_era,
            "confidence_distribution": confidence_distribution,
            "boundary_coverage": boundary_coverage,
            "date_precision_coverage": date_precision_coverage,
            "chain_coverage": chain_coverage,
            "data_completeness_score": round(score, 1),
        },
        headers={"Cache-Control": "public, max-age=600"},
    )


# ═══════════════════════════════════════════════════════════════════
# 3. Suggestions
# ═══════════════════════════════════════════════════════════════════


def _extract_failed_searches(db: Session, since: str) -> list[dict]:
    """Find query_string patterns on entity/event endpoints that likely
    returned empty results (status 200 but small payload ≈ empty list).

    Heuristic: look for requests with query_string containing search-like
    params (name=, q=, year=, event_type=) and status 200 with fast
    response time (< 50ms typically means empty DB hit).
    """
    search_paths = ("/v1/entities", "/v1/events")
    rows = (
        db.query(
            ApiRequestLog.path,
            ApiRequestLog.query_string,
            func.count(ApiRequestLog.id).label("times"),
        )
        .filter(
            ApiRequestLog.timestamp >= since,
            ApiRequestLog.query_string.isnot(None),
            ApiRequestLog.query_string != "",
            or_(
                *[ApiRequestLog.path.like(f"{p}%") for p in search_paths]
            ),
            ApiRequestLog.status_code == 200,
            # Fast response = likely empty result
            ApiRequestLog.response_time_ms < 100,
        )
        .group_by(ApiRequestLog.path, ApiRequestLog.query_string)
        .order_by(func.count(ApiRequestLog.id).desc())
        .limit(20)
        .all()
    )
    return [
        {"path": r.path, "query": r.query_string, "times_searched": r.times}
        for r in rows
    ]


@router.get(
    "/admin/suggestions",
    summary="Smart suggestions for data expansion (JSON)",
    description="Suggerimenti intelligenti: ricerche fallite, gap geografici, gap temporali, entita' orfane, bassa confidenza.",
    include_in_schema=False,
)
def suggestions(db: Session = Depends(get_db)):
    """Generate prioritised suggestions for expanding the dataset."""

    month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

    # ── 1. Failed searches (potential demand signals) ─────────
    failed_searches = _extract_failed_searches(db, month_ago)

    # ── 2. Geographic gaps ────────────────────────────────────
    entities = db.query(
        GeoEntity.capital_lat, GeoEntity.capital_lon,
    ).all()
    region_counts: dict[str, int] = Counter()
    for e in entities:
        region_counts[_lat_to_continent(e.capital_lat, e.capital_lon)] += 1

    # Regions below the average are "gaps"
    avg_per_region = sum(region_counts.values()) / max(len(region_counts), 1)
    geographic_gaps = [
        {"region": r, "entity_count": c, "below_avg_by": round(avg_per_region - c)}
        for r, c in sorted(region_counts.items(), key=lambda x: x[1])
        if c < avg_per_region * 0.6  # significantly below average
    ]

    # ── 3. Temporal gaps ──────────────────────────────────────
    event_years = db.query(HistoricalEvent.year).all()
    era_event_counts: dict[str, int] = Counter()
    for (y,) in event_years:
        era_event_counts[_year_to_era(y)] += 1

    entity_years = db.query(GeoEntity.year_start).all()
    era_entity_counts: dict[str, int] = Counter()
    for (y,) in entity_years:
        era_entity_counts[_year_to_era(y)] += 1

    _era_order = [
        "Pre-3000 BCE", "3000-1000 BCE", "1000-500 BCE", "500-1 BCE",
        "1-500 CE", "500-1000 CE", "1000-1500 CE", "1500-1800 CE",
        "1800-1900 CE", "1900-2000 CE", "2000-present",
    ]
    avg_events_per_era = sum(era_event_counts.values()) / max(len(_era_order), 1)
    temporal_gaps = [
        {
            "era": era,
            "events": era_event_counts.get(era, 0),
            "entities": era_entity_counts.get(era, 0),
        }
        for era in _era_order
        if era_event_counts.get(era, 0) < avg_events_per_era * 0.5
    ]

    # ── 4. Missing connections (entities not in any chain) ────
    entity_ids_in_chains = set(
        r[0] for r in db.query(distinct(ChainLink.entity_id)).all()
    )
    orphan_entities = (
        db.query(GeoEntity.id, GeoEntity.name_original, GeoEntity.entity_type)
        .filter(~GeoEntity.id.in_(entity_ids_in_chains) if entity_ids_in_chains else True)
        .order_by(GeoEntity.name_original)
        .all()
    )
    missing_connections = [
        {"id": e.id, "name": e.name_original, "type": e.entity_type}
        for e in orphan_entities[:30]
    ]
    missing_connections_total = len(orphan_entities)

    # ── 5. Low confidence items ───────────────────────────────
    low_conf_entities = (
        db.query(
            GeoEntity.id, GeoEntity.name_original,
            GeoEntity.confidence_score, GeoEntity.entity_type,
        )
        .filter(GeoEntity.confidence_score < 0.5)
        .order_by(GeoEntity.confidence_score)
        .limit(20)
        .all()
    )
    low_conf_events = (
        db.query(
            HistoricalEvent.id, HistoricalEvent.name_original,
            HistoricalEvent.confidence_score, HistoricalEvent.event_type,
        )
        .filter(HistoricalEvent.confidence_score < 0.5)
        .order_by(HistoricalEvent.confidence_score)
        .limit(20)
        .all()
    )
    low_confidence = {
        "entities": [
            {"id": e.id, "name": e.name_original, "score": e.confidence_score, "type": e.entity_type}
            for e in low_conf_entities
        ],
        "events": [
            {"id": e.id, "name": e.name_original, "score": e.confidence_score, "type": e.event_type}
            for e in low_conf_events
        ],
    }

    # ── 6. Entities without boundary ──────────────────────────
    no_boundary = (
        db.query(GeoEntity.id, GeoEntity.name_original, GeoEntity.entity_type)
        .filter(
            or_(
                GeoEntity.boundary_geojson.is_(None),
                GeoEntity.boundary_geojson == "",
            )
        )
        .order_by(GeoEntity.name_original)
        .limit(20)
        .all()
    )
    missing_boundaries = [
        {"id": e.id, "name": e.name_original, "type": e.entity_type}
        for e in no_boundary
    ]

    return JSONResponse(
        content={
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "failed_searches": failed_searches,
            "geographic_gaps": geographic_gaps,
            "temporal_gaps": temporal_gaps,
            "missing_connections": {
                "total_orphan_entities": missing_connections_total,
                "sample": missing_connections,
            },
            "low_confidence": low_confidence,
            "missing_boundaries": missing_boundaries,
        },
        headers={"Cache-Control": "public, max-age=600"},
    )
