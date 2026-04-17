"""Endpoint per lingue storiche geocoded — v6.44.

GET /v1/languages                      list paginato con filtri
GET /v1/languages/at-year/{year}       lingue attive in un anno
GET /v1/languages/families             enum language families con counts
GET /v1/languages/{id}                 detail

ETHICS: soppressioni coloniali documentate in ethical_notes.
"""

import json
import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from src.cache import cache_response
from src.db.database import get_db
from src.db.models import HistoricalLanguage

logger = logging.getLogger(__name__)

router = APIRouter(tags=["lingue"])


def _lang_to_dict(lang: HistoricalLanguage) -> dict:
    try:
        sources = json.loads(lang.sources) if lang.sources else []
    except (json.JSONDecodeError, TypeError):
        sources = []
    try:
        variants = json.loads(lang.name_variants) if lang.name_variants else []
    except (json.JSONDecodeError, TypeError):
        variants = []
    return {
        "id": lang.id,
        "name_original": lang.name_original,
        "name_original_lang": lang.name_original_lang,
        "iso_code": lang.iso_code,
        "family": lang.family,
        "script": lang.script,
        "center_lat": lang.center_lat,
        "center_lon": lang.center_lon,
        "region_name": lang.region_name,
        "period_start": lang.period_start,
        "period_end": lang.period_end,
        "vitality_status": lang.vitality_status,
        "description": lang.description,
        "confidence_score": lang.confidence_score,
        "status": lang.status,
        "ethical_notes": lang.ethical_notes,
        "sources": sources,
        "name_variants": variants,
    }


@router.get(
    "/v1/languages",
    summary="List historical languages (paginated)",
)
@cache_response(ttl_seconds=3600)
def list_languages(
    request: Request,
    response: Response,
    family: str | None = Query(None, max_length=100),
    region: str | None = Query(None, max_length=200),
    iso_code: str | None = Query(None, max_length=10),
    vitality_status: str | None = Query(None, max_length=30),
    year: int | None = Query(None, ge=-10000, le=2100, description="Language active in this year"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(HistoricalLanguage)
    if family:
        q = q.filter(HistoricalLanguage.family.ilike(f"%{family}%"))
    if region:
        q = q.filter(HistoricalLanguage.region_name.ilike(f"%{region}%"))
    if iso_code:
        q = q.filter(HistoricalLanguage.iso_code == iso_code)
    if vitality_status:
        q = q.filter(HistoricalLanguage.vitality_status == vitality_status)
    if year is not None:
        q = q.filter(
            or_(HistoricalLanguage.period_start.is_(None), HistoricalLanguage.period_start <= year)
        )
        q = q.filter(
            or_(HistoricalLanguage.period_end.is_(None), HistoricalLanguage.period_end >= year)
        )

    total = q.count()
    langs = (
        q.order_by(HistoricalLanguage.name_original).offset(offset).limit(limit).all()
    )
    response.headers["Cache-Control"] = "public, max-age=3600"
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "languages": [_lang_to_dict(l) for l in langs],
    }


@router.get(
    "/v1/languages/at-year/{year}",
    summary="Lingue attive in un dato anno",
)
@cache_response(ttl_seconds=3600)
def languages_at_year(
    year: int,
    request: Request,
    response: Response,
    region: str | None = Query(None, max_length=200),
    db: Session = Depends(get_db),
):
    if year < -10000 or year > 2100:
        raise HTTPException(status_code=400, detail=f"year {year} out of range")

    q = db.query(HistoricalLanguage).filter(
        or_(HistoricalLanguage.period_start.is_(None), HistoricalLanguage.period_start <= year)
    )
    q = q.filter(
        or_(HistoricalLanguage.period_end.is_(None), HistoricalLanguage.period_end >= year)
    )
    if region:
        q = q.filter(HistoricalLanguage.region_name.ilike(f"%{region}%"))

    langs = q.order_by(HistoricalLanguage.region_name, HistoricalLanguage.name_original).all()
    response.headers["Cache-Control"] = "public, max-age=3600"
    return {
        "year": year,
        "region": region,
        "count": len(langs),
        "languages": [_lang_to_dict(l) for l in langs],
    }


@router.get(
    "/v1/languages/families",
    summary="Language families with counts",
)
def language_families(db: Session = Depends(get_db)):
    rows = (
        db.query(HistoricalLanguage.family, func.count(HistoricalLanguage.id))
        .filter(HistoricalLanguage.family.isnot(None))
        .group_by(HistoricalLanguage.family)
        .order_by(desc(func.count(HistoricalLanguage.id)))
        .all()
    )
    return [{"family": f, "count": c} for f, c in rows]


@router.get("/v1/languages/{lang_id}", summary="Language detail")
@cache_response(ttl_seconds=3600)
def get_language(
    lang_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    lang = db.query(HistoricalLanguage).filter(HistoricalLanguage.id == lang_id).first()
    if not lang:
        raise HTTPException(status_code=404, detail=f"Language {lang_id} not found")
    response.headers["Cache-Control"] = "public, max-age=3600"
    return _lang_to_dict(lang)
