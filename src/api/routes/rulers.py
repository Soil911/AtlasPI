"""Endpoint per sovrani storici — v6.38.

GET /v1/rulers                              list paginated con filtri
GET /v1/rulers/at-year/{year}               sovrani in carica in un anno
GET /v1/rulers/by-entity/{entity_id}        sovrani di un'entità
GET /v1/rulers/{id}                         detail

ETHICS-001: nome originale primario (武曌 non "Wu Zetian").
ETHICS-002/007: ethical_notes esplicita violenze, genocidi, schiavitù.
"""

import json
import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from src.cache import cache_response
from src.db.database import get_db
from src.db.models import GeoEntity, HistoricalRuler

logger = logging.getLogger(__name__)

router = APIRouter(tags=["sovrani"])


# ─── Response helpers ──────────────────────────────────────────────

def _ruler_to_dict(ruler: HistoricalRuler) -> dict:
    """Serializza un sovrano in dict JSON-ready."""
    try:
        sources = json.loads(ruler.sources) if ruler.sources else []
    except (json.JSONDecodeError, TypeError):
        sources = []
    try:
        name_variants = json.loads(ruler.name_variants) if ruler.name_variants else []
    except (json.JSONDecodeError, TypeError):
        name_variants = []
    try:
        notable_events = json.loads(ruler.notable_events) if ruler.notable_events else []
    except (json.JSONDecodeError, TypeError):
        notable_events = []

    return {
        "id": ruler.id,
        "name_original": ruler.name_original,
        "name_original_lang": ruler.name_original_lang,
        "name_regnal": ruler.name_regnal,
        "birth_year": ruler.birth_year,
        "death_year": ruler.death_year,
        "reign_start": ruler.reign_start,
        "reign_end": ruler.reign_end,
        "title": ruler.title,
        "entity_id": ruler.entity_id,
        "entity_name_fallback": ruler.entity_name_fallback,
        "region": ruler.region,
        "description": ruler.description,
        "dynasty": ruler.dynasty,
        "confidence_score": ruler.confidence_score,
        "status": ruler.status,
        "ethical_notes": ruler.ethical_notes,
        "sources": sources,
        "name_variants": name_variants,
        "notable_events": notable_events,
    }


# ─── Endpoints ──────────────────────────────────────────────────────

@router.get(
    "/v1/rulers",
    summary="List historical rulers (paginated)",
    description=(
        "Returns historical rulers: emperors, kings, sultans, khagan, "
        "presidents, dictators. Indexed by name_original (in native script). "
        "Use filters to narrow by region, dynasty, title, reign year.\n\n"
        "**ETHICS**: `ethical_notes` documents violence, genocides, slavery "
        "explicitly — no euphemism. Leopoldo II's Congo atrocities, Qin Shi "
        "Huangdi's book-burning, Aurangzeb's temple destruction all surfaced."
    ),
)
@cache_response(ttl_seconds=3600)
def list_rulers(
    request: Request,
    response: Response,
    region: str | None = Query(None, max_length=50),
    dynasty: str | None = Query(None, max_length=200),
    title: str | None = Query(None, max_length=100),
    entity_id: int | None = Query(None, ge=1),
    year: int | None = Query(None, ge=-5000, le=2100, description="Ruler in reign in this year"),
    status: Literal["confirmed", "uncertain", "disputed", "legendary"] | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(HistoricalRuler)

    if region:
        q = q.filter(HistoricalRuler.region == region)
    if dynasty:
        q = q.filter(HistoricalRuler.dynasty.ilike(f"%{dynasty}%"))
    if title:
        q = q.filter(HistoricalRuler.title == title)
    if entity_id is not None:
        q = q.filter(HistoricalRuler.entity_id == entity_id)
    if status:
        q = q.filter(HistoricalRuler.status == status)
    if year is not None:
        q = q.filter(
            or_(HistoricalRuler.reign_start.is_(None), HistoricalRuler.reign_start <= year)
        )
        q = q.filter(
            or_(HistoricalRuler.reign_end.is_(None), HistoricalRuler.reign_end >= year)
        )

    total = q.count()
    rulers = (
        q.order_by(HistoricalRuler.reign_start.asc().nulls_last(), HistoricalRuler.name_original)
        .offset(offset).limit(limit).all()
    )

    response.headers["Cache-Control"] = "public, max-age=3600"
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "rulers": [_ruler_to_dict(r) for r in rulers],
    }


@router.get(
    "/v1/rulers/at-year/{year}",
    summary="Rulers in office in a given year",
    description=(
        "Returns all historical rulers who were actively reigning in the "
        "specified year. Optionally filtered by region.\n\n"
        "Critical for 'who ruled X in year Y' queries — AI agents can "
        "answer 'Chi regnava in Cina nel 1200?' directly."
    ),
)
@cache_response(ttl_seconds=3600)
def rulers_at_year(
    year: int,
    request: Request,
    response: Response,
    region: str | None = Query(None, max_length=50),
    db: Session = Depends(get_db),
):
    if year < -5000 or year > 2100:
        raise HTTPException(status_code=400, detail=f"Year {year} out of range [-5000, 2100]")

    q = db.query(HistoricalRuler).filter(
        or_(HistoricalRuler.reign_start.is_(None), HistoricalRuler.reign_start <= year)
    )
    q = q.filter(
        or_(HistoricalRuler.reign_end.is_(None), HistoricalRuler.reign_end >= year)
    )
    if region:
        q = q.filter(HistoricalRuler.region == region)

    rulers = q.order_by(HistoricalRuler.region, HistoricalRuler.reign_start).all()

    response.headers["Cache-Control"] = "public, max-age=3600"
    return {
        "year": year,
        "region": region,
        "count": len(rulers),
        "rulers": [_ruler_to_dict(r) for r in rulers],
    }


@router.get(
    "/v1/rulers/by-entity/{entity_id}",
    summary="Rulers of a specific historical entity",
    description="All rulers linked to a specific GeoEntity (via entity_id FK).",
)
@cache_response(ttl_seconds=3600)
def rulers_by_entity(
    entity_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    entity = db.query(GeoEntity).filter(GeoEntity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

    rulers = (
        db.query(HistoricalRuler)
        .filter(HistoricalRuler.entity_id == entity_id)
        .order_by(HistoricalRuler.reign_start.asc().nulls_last())
        .all()
    )

    response.headers["Cache-Control"] = "public, max-age=3600"
    return {
        "entity_id": entity_id,
        "entity_name_original": entity.name_original,
        "count": len(rulers),
        "rulers": [_ruler_to_dict(r) for r in rulers],
    }


@router.get(
    "/v1/rulers/{ruler_id}",
    summary="Ruler detail",
    description="Full biography, sources, ethical_notes.",
)
@cache_response(ttl_seconds=3600)
def get_ruler(
    ruler_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    ruler = db.query(HistoricalRuler).filter(HistoricalRuler.id == ruler_id).first()
    if not ruler:
        raise HTTPException(status_code=404, detail=f"Ruler {ruler_id} not found")
    response.headers["Cache-Control"] = "public, max-age=3600"
    return _ruler_to_dict(ruler)
