"""Endpoint per relazioni tra entità.

GET /v1/entities/{id}/related     entità temporalmente e tipologicamente correlate
GET /v1/entities/{id}/contemporaries  entità attive nello stesso periodo
"""

import logging

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.api.errors import EntityNotFoundError
from src.db.database import get_db
from src.db.models import GeoEntity

logger = logging.getLogger(__name__)

router = APIRouter(tags=["relazioni"])


class RelatedEntity:
    """Helper per serializzazione."""
    pass


@router.get(
    "/v1/entities/{entity_id}/contemporaries",
    summary="Entità contemporanee",
    description="Restituisce le entità attive nello stesso periodo dell'entità data.",
)
def get_contemporaries(
    entity_id: int,
    response: Response,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    entity = db.query(GeoEntity).filter(GeoEntity.id == entity_id).first()
    if not entity:
        raise EntityNotFoundError(entity_id)

    # Trova entità che si sovrappongono temporalmente
    q = db.query(GeoEntity).filter(GeoEntity.id != entity_id)
    q = q.filter(GeoEntity.year_start <= (entity.year_end or 2025))
    q = q.filter(or_(GeoEntity.year_end.is_(None), GeoEntity.year_end >= entity.year_start))

    results = q.limit(limit).all()

    response.headers["Cache-Control"] = "public, max-age=3600"

    return {
        "entity_id": entity_id,
        "entity_name": entity.name_original,
        "period": f"{entity.year_start} — {entity.year_end or 'presente'}",
        "count": len(results),
        "contemporaries": [
            {
                "id": e.id,
                "name_original": e.name_original,
                "entity_type": e.entity_type,
                "year_start": e.year_start,
                "year_end": e.year_end,
                "status": e.status,
                "overlap_start": max(entity.year_start, e.year_start),
                "overlap_end": min(entity.year_end or 2025, e.year_end or 2025),
            }
            for e in results
        ],
    }


@router.get(
    "/v1/entities/{entity_id}/related",
    summary="Entità correlate",
    description=(
        "Restituisce entità correlate per tipo, periodo e riferimenti incrociati "
        "nei cambi territoriali."
    ),
)
def get_related(
    entity_id: int,
    response: Response,
    db: Session = Depends(get_db),
):
    entity = db.query(GeoEntity).filter(GeoEntity.id == entity_id).first()
    if not entity:
        raise EntityNotFoundError(entity_id)

    # 1. Stesso tipo
    same_type = (
        db.query(GeoEntity)
        .filter(GeoEntity.id != entity_id, GeoEntity.entity_type == entity.entity_type)
        .limit(5)
        .all()
    )

    # 2. Stessa regione temporale (overlap > 50 anni)
    temporal = (
        db.query(GeoEntity)
        .filter(GeoEntity.id != entity_id)
        .filter(GeoEntity.year_start <= (entity.year_end or 2025))
        .filter(or_(GeoEntity.year_end.is_(None), GeoEntity.year_end >= entity.year_start))
        .limit(10)
        .all()
    )
    # Calcola overlap e ordina
    scored = []
    for e in temporal:
        overlap = min(entity.year_end or 2025, e.year_end or 2025) - max(entity.year_start, e.year_start)
        if overlap > 50:
            scored.append((e, overlap))
    scored.sort(key=lambda x: x[1], reverse=True)

    response.headers["Cache-Control"] = "public, max-age=3600"

    def _mini(e):
        return {"id": e.id, "name_original": e.name_original, "entity_type": e.entity_type,
                "year_start": e.year_start, "year_end": e.year_end, "status": e.status}

    return {
        "entity_id": entity_id,
        "entity_name": entity.name_original,
        "same_type": [_mini(e) for e in same_type],
        "temporal_overlap": [
            {**_mini(e), "overlap_years": ov}
            for e, ov in scored[:5]
        ],
    }
