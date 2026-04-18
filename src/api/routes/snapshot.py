"""World snapshot endpoint — v6.30.

GET /v1/snapshot/year/{year} — rich aggregated view of the world at a given year.

Returns entities, events, periods, cities, chains all in a single response,
optimized for AI agents asking 'Tell me what the world looked like in 1250'.

Unlike individual resource endpoints, this aggregates across ALL dimensions
and provides context (top-N selections, region breakdowns, statistics).
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Any

from fastapi import APIRouter, Depends, Path, Query, Request, Response
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from src.cache import cache_response
from src.db.database import get_db
from src.db.models import (
    ChainLink,
    DynastyChain,
    GeoEntity,
    HistoricalCity,
    HistoricalEvent,
    HistoricalPeriod,
)
# v6.66.0 (audit #security): limite specifico per /v1/snapshot/year/*
# Endpoint pesante che aggrega periods+entities+events+cities+chains
# → 60/minute basta per uso interattivo, previene abuse via scraper.
from src.middleware.rate_limit import RATE_LIMIT_SNAPSHOT, limiter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["snapshot"])


def _year_to_display(year: int) -> str:
    """Format year with era (BCE/CE) for human-readable output."""
    if year < 0:
        return f"{abs(year)} BCE"
    return f"{year} CE"


@router.get(
    "/v1/snapshot/year/{year}",
    summary="World snapshot at a given year",
    description=(
        "Aggregated snapshot of the world at a specific year: active entities, "
        "historical periods in effect, events that year, active cities, "
        "chains in progress. Designed for AI agents answering 'What was the "
        "world like in year X?' with a single API call."
    ),
)
@limiter.limit(RATE_LIMIT_SNAPSHOT)
@cache_response(ttl_seconds=3600)
def world_snapshot(
    request: Request,
    response: Response,
    year: int = Path(..., ge=-5000, le=2025, description="Year (negative = BCE)"),
    top_n: int = Query(10, ge=1, le=50, description="How many top-items to include per category"),
    db: Session = Depends(get_db),
):
    """Return a rich snapshot of the world at the given year.

    Fields:
      - year, year_display (human-readable with BCE/CE)
      - periods: list of historical periods in effect, by region
      - entities: active entities, total + top-N + breakdown by region/type
      - events_that_year: events with year == year
      - cities: active cities at that year + breakdown by type
      - chains: dynasty chains with at least one link active at that year
    """

    # ── 1. Active periods ─────────────────────────────────────────
    periods = (
        db.query(HistoricalPeriod)
        .filter(
            HistoricalPeriod.year_start <= year,
            or_(
                HistoricalPeriod.year_end.is_(None),
                HistoricalPeriod.year_end >= year,
            ),
        )
        .order_by(HistoricalPeriod.region, HistoricalPeriod.year_start)
        .all()
    )

    # ── 2. Active entities (any entity existing at `year`) ────────
    active_entities_q = db.query(GeoEntity).filter(
        GeoEntity.year_start <= year,
        or_(
            GeoEntity.year_end.is_(None),
            GeoEntity.year_end >= year,
        ),
    )

    total_entities = active_entities_q.count()

    top_entities = (
        active_entities_q
        .order_by(GeoEntity.confidence_score.desc(), GeoEntity.year_start)
        .limit(top_n)
        .all()
    )

    # Breakdown by type + region (based on capital coordinates)
    entity_types_rows = (
        active_entities_q
        .with_entities(GeoEntity.entity_type, func.count(GeoEntity.id))
        .group_by(GeoEntity.entity_type)
        .all()
    )
    entity_by_type = {row[0]: row[1] for row in entity_types_rows}

    # ── 3. Events that year ──────────────────────────────────────
    events_that_year = (
        db.query(HistoricalEvent)
        .filter(HistoricalEvent.year == year)
        .order_by(
            HistoricalEvent.month.asc().nullslast(),
            HistoricalEvent.day.asc().nullslast(),
            HistoricalEvent.confidence_score.desc(),
        )
        .all()
    )

    # ── 4. Active cities ─────────────────────────────────────────
    # A city is "active" if founded_year <= year AND (abandoned_year is None OR >= year)
    active_cities_q = db.query(HistoricalCity).filter(
        or_(
            HistoricalCity.founded_year.is_(None),
            HistoricalCity.founded_year <= year,
        ),
        or_(
            HistoricalCity.abandoned_year.is_(None),
            HistoricalCity.abandoned_year >= year,
        ),
    )
    total_cities = active_cities_q.count()
    city_types_rows = (
        active_cities_q
        .with_entities(HistoricalCity.city_type, func.count(HistoricalCity.id))
        .group_by(HistoricalCity.city_type)
        .all()
    )
    cities_by_type = {row[0]: row[1] for row in city_types_rows}

    top_cities = (
        active_cities_q
        .order_by(
            HistoricalCity.confidence_score.desc(),
            HistoricalCity.population_peak.desc().nullslast(),
        )
        .limit(top_n)
        .all()
    )

    # ── 5. Active chains (chains with at least one link active at year) ──
    # A chain is "active" if any of its links has transition_year <= year
    # (best-effort: we count chains where year falls within the entities)
    chain_ids_active = (
        db.query(ChainLink.chain_id)
        .join(GeoEntity, ChainLink.entity_id == GeoEntity.id)
        .filter(
            GeoEntity.year_start <= year,
            or_(
                GeoEntity.year_end.is_(None),
                GeoEntity.year_end >= year,
            ),
        )
        .distinct()
        .all()
    )
    chain_ids = [c[0] for c in chain_ids_active]

    active_chains = []
    if chain_ids:
        active_chains = (
            db.query(DynastyChain)
            .filter(DynastyChain.id.in_(chain_ids))
            .limit(top_n)
            .all()
        )

    # ── Build response ───────────────────────────────────────────
    return {
        "year": year,
        "year_display": _year_to_display(year),
        "periods": {
            "total": len(periods),
            "items": [
                {
                    "id": p.id,
                    "name": p.name,
                    "slug": p.slug,
                    "period_type": p.period_type,
                    "region": p.region,
                    "year_start": p.year_start,
                    "year_end": p.year_end,
                }
                for p in periods
            ],
        },
        "entities": {
            "total_active": total_entities,
            "by_type": entity_by_type,
            "top_by_confidence": [
                {
                    "id": e.id,
                    "name": e.name_original,
                    "entity_type": e.entity_type,
                    "year_start": e.year_start,
                    "year_end": e.year_end,
                    "confidence_score": e.confidence_score,
                    "status": e.status,
                }
                for e in top_entities
            ],
        },
        "events_that_year": {
            "total": len(events_that_year),
            "items": [
                {
                    "id": e.id,
                    "name": e.name_original,
                    "event_type": e.event_type,
                    "month": e.month,
                    "day": e.day,
                    "location_name": e.location_name,
                    "confidence_score": e.confidence_score,
                }
                for e in events_that_year[:top_n]
            ],
        },
        "cities": {
            "total_active": total_cities,
            "by_type": cities_by_type,
            "top": [
                {
                    "id": c.id,
                    "name": c.name_original,
                    "city_type": c.city_type,
                    "latitude": c.latitude,
                    "longitude": c.longitude,
                    "founded_year": c.founded_year,
                    "population_peak": c.population_peak,
                }
                for c in top_cities
            ],
        },
        "chains": {
            "total_active": len(chain_ids),
            "items": [
                {
                    "id": c.id,
                    "name": c.name,
                    "chain_type": c.chain_type,
                    "region": c.region,
                }
                for c in active_chains
            ],
        },
    }
