"""Endpoint per relazioni tra entità.

GET /v1/entities/{id}/related          entità correlate
GET /v1/entities/{id}/contemporaries   entità attive nello stesso periodo
GET /v1/compare/{id1}/{id2}            confronto tra due entità
"""

import json
import logging

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from src.api.errors import EntityNotFoundError
from src.db.database import get_db
from src.db.models import GeoEntity

logger = logging.getLogger(__name__)

router = APIRouter(tags=["relazioni"])


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


# ─── Compare ────────────────────────────────────────────────────

def _entity_compare_data(entity: GeoEntity) -> dict:
    """Costruisce dati confronto per un'entità."""
    geojson = None
    if entity.boundary_geojson:
        try:
            geojson = json.loads(entity.boundary_geojson)
        except (json.JSONDecodeError, TypeError):
            pass

    return {
        "id": entity.id,
        "name_original": entity.name_original,
        "name_original_lang": entity.name_original_lang,
        "entity_type": entity.entity_type,
        "year_start": entity.year_start,
        "year_end": entity.year_end,
        "status": entity.status,
        "confidence_score": entity.confidence_score,
        "capital": {"name": entity.capital_name, "lat": entity.capital_lat, "lon": entity.capital_lon}
        if entity.capital_name else None,
        "boundary_geojson": geojson,
        "name_variants_count": len(entity.name_variants),
        "territory_changes_count": len(entity.territory_changes),
        "sources_count": len(entity.sources),
        "duration_years": (entity.year_end or 2025) - entity.year_start,
        "ethical_notes": entity.ethical_notes,
    }


@router.get(
    "/v1/compare/{id1}/{id2}",
    summary="Confronta due entità storiche",
    description=(
        "Restituisce un confronto strutturato tra due entità: "
        "durata, overlap temporale, metriche di qualità dati."
    ),
)
def compare_entities(
    id1: int,
    id2: int,
    response: Response,
    db: Session = Depends(get_db),
):
    e1 = (
        db.query(GeoEntity)
        .options(
            joinedload(GeoEntity.name_variants),
            joinedload(GeoEntity.territory_changes),
            joinedload(GeoEntity.sources),
        )
        .filter(GeoEntity.id == id1)
        .first()
    )
    e2 = (
        db.query(GeoEntity)
        .options(
            joinedload(GeoEntity.name_variants),
            joinedload(GeoEntity.territory_changes),
            joinedload(GeoEntity.sources),
        )
        .filter(GeoEntity.id == id2)
        .first()
    )

    if not e1:
        raise EntityNotFoundError(id1)
    if not e2:
        raise EntityNotFoundError(id2)

    # Calcola overlap temporale
    overlap_start = max(e1.year_start, e2.year_start)
    overlap_end = min(e1.year_end or 2025, e2.year_end or 2025)
    temporal_overlap = max(0, overlap_end - overlap_start)

    response.headers["Cache-Control"] = "public, max-age=3600"

    return {
        "entity_a": _entity_compare_data(e1),
        "entity_b": _entity_compare_data(e2),
        "comparison": {
            "temporal_overlap_years": temporal_overlap,
            "overlap_period": f"{overlap_start} — {overlap_end}" if temporal_overlap > 0 else None,
            "same_type": e1.entity_type == e2.entity_type,
            "same_status": e1.status == e2.status,
            "confidence_diff": round(abs(e1.confidence_score - e2.confidence_score), 3),
            "duration_diff": abs(
                ((e1.year_end or 2025) - e1.year_start) - ((e2.year_end or 2025) - e2.year_start)
            ),
        },
    }
