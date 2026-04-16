"""Endpoint for historical periods/epochs — v6.27.

GET /v1/periods                          list + filter (region, period_type, year)
GET /v1/periods/types                    enumerate period_type values
GET /v1/periods/regions                  enumerate region values
GET /v1/periods/at-year/{year}           periods that include a given year
GET /v1/periods/by-slug/{slug}           period detail by URL-friendly slug
GET /v1/periods/{id}                     period detail by numeric ID

ETHICS: periodizations are historiographic constructs, not objective facts.
Each period declares its `region` scope (no Eurocentric defaults) and
optionally a `historiographic_note` documenting scholarly debates.
`alternative_names` lists competing/deprecated labels.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.cache import cache_response
from src.db.database import get_db
from src.db.models import HistoricalPeriod

logger = logging.getLogger(__name__)

router = APIRouter(tags=["periods"])


# ─── helpers ───────────────────────────────────────────────────────────


def _period_summary(p: HistoricalPeriod) -> dict[str, Any]:
    return {
        "id": p.id,
        "name": p.name,
        "name_lang": p.name_lang,
        "slug": p.slug,
        "name_native": p.name_native,
        "name_native_lang": p.name_native_lang,
        "period_type": p.period_type,
        "region": p.region,
        "year_start": p.year_start,
        "year_end": p.year_end,
        "confidence_score": p.confidence_score,
        "status": p.status,
    }


def _period_detail(p: HistoricalPeriod) -> dict[str, Any]:
    """Full detail with description, historiographic note, sources."""
    alt_names = None
    if p.alternative_names:
        try:
            alt_names = json.loads(p.alternative_names)
        except json.JSONDecodeError:
            alt_names = None

    sources = None
    if p.sources:
        try:
            sources = json.loads(p.sources)
        except json.JSONDecodeError:
            sources = None

    return {
        **_period_summary(p),
        "description": p.description,
        "historiographic_note": p.historiographic_note,
        "alternative_names": alt_names,
        "sources": sources,
    }


# ─── list + filter ───────────────────────────────────────────────────


@router.get(
    "/v1/periods",
    summary="List historical periods",
    description="Lista strutturata di epoche storiche. Filtrabile per regione, tipo, anno e status.",
)
@cache_response(ttl_seconds=3600)
def list_periods(
    request: Request,
    response: Response,
    region: str | None = Query(None, description="Filter by region scope"),
    period_type: str | None = Query(None, description="Filter by period type (age, era, period, dynasty, epoch)"),
    year: int | None = Query(None, description="Only periods that include this year"),
    status: str | None = Query(None, description="Filter by status (confirmed, debated, deprecated)"),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Return periods matching the filters, ordered by year_start."""
    q = db.query(HistoricalPeriod)

    if region:
        q = q.filter(HistoricalPeriod.region == region)
    if period_type:
        q = q.filter(HistoricalPeriod.period_type == period_type)
    if status:
        q = q.filter(HistoricalPeriod.status == status)
    if year is not None:
        q = q.filter(
            HistoricalPeriod.year_start <= year,
            or_(
                HistoricalPeriod.year_end.is_(None),
                HistoricalPeriod.year_end >= year,
            ),
        )

    total = q.count()

    items = (
        q.order_by(HistoricalPeriod.year_start, HistoricalPeriod.name)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "periods": [_period_summary(p) for p in items],
    }


# ─── enumeration endpoints ────────────────────────────────────────────


@router.get(
    "/v1/periods/types",
    summary="List all period types in the database",
)
@cache_response(ttl_seconds=3600)
def period_types(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """Return the distinct period_type values used in the dataset."""
    rows = db.query(HistoricalPeriod.period_type).distinct().all()
    return {"types": sorted({r[0] for r in rows if r[0]})}


@router.get(
    "/v1/periods/regions",
    summary="List all regions used by periods",
)
@cache_response(ttl_seconds=3600)
def period_regions(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """Return the distinct region values used in the dataset."""
    rows = db.query(HistoricalPeriod.region).distinct().all()
    return {"regions": sorted({r[0] for r in rows if r[0]})}


# ─── at-year ──────────────────────────────────────────────────────────


@router.get(
    "/v1/periods/at-year/{year}",
    summary="Find periods that include a given year",
    description="Returns all periods whose range includes the given year, across regions.",
)
@cache_response(ttl_seconds=3600)
def periods_at_year(
    request: Request,
    response: Response,
    year: int = Path(..., ge=-4000000, le=3000, description="Year to query (negative = BCE)"),
    region: str | None = Query(None, description="Optional region filter"),
    db: Session = Depends(get_db),
):
    """Return all periods containing the given year."""
    q = db.query(HistoricalPeriod).filter(
        HistoricalPeriod.year_start <= year,
        or_(
            HistoricalPeriod.year_end.is_(None),
            HistoricalPeriod.year_end >= year,
        ),
    )
    if region:
        q = q.filter(HistoricalPeriod.region == region)

    items = q.order_by(HistoricalPeriod.region, HistoricalPeriod.year_start).all()

    return {
        "year": year,
        "total": len(items),
        "periods": [_period_summary(p) for p in items],
    }


# ─── by slug ──────────────────────────────────────────────────────────


@router.get(
    "/v1/periods/by-slug/{slug}",
    summary="Get period by URL-friendly slug",
    description="Fetch a single period by its unique slug (e.g. 'bronze-age', 'edo-period').",
)
def period_by_slug(
    slug: str = Path(..., min_length=1, max_length=200),
    db: Session = Depends(get_db),
):
    """Return a period matching the given slug."""
    p = db.query(HistoricalPeriod).filter(HistoricalPeriod.slug == slug).first()
    if p is None:
        raise HTTPException(status_code=404, detail=f"Period with slug '{slug}' not found")
    return _period_detail(p)


# ─── detail by id ─────────────────────────────────────────────────────


@router.get(
    "/v1/periods/{period_id}",
    summary="Get period detail by numeric ID",
)
def period_detail(
    period_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    """Return full detail for a period by ID."""
    p = db.query(HistoricalPeriod).filter(HistoricalPeriod.id == period_id).first()
    if p is None:
        raise HTTPException(status_code=404, detail=f"Period with id={period_id} not found")
    return _period_detail(p)
