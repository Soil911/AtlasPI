"""Endpoint per le entità geopolitiche — vedi ADR-002.

GET /v1/entity?name=...&year=...   query principale
GET /v1/entities                    elenco entità
GET /v1/entities/{id}               dettaglio entità
"""

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from src.api.schemas import (
    CapitalResponse,
    EntityListResponse,
    EntityResponse,
)
from src.db.database import get_db
from src.db.models import GeoEntity, NameVariant

router = APIRouter(tags=["entities"])


def _entity_to_response(entity: GeoEntity) -> EntityResponse:
    """Converte un record ORM in risposta API."""
    capital = None
    if entity.capital_name and entity.capital_lat is not None:
        capital = CapitalResponse(
            name=entity.capital_name,
            lat=entity.capital_lat,
            lon=entity.capital_lon,
        )

    geojson = None
    if entity.boundary_geojson:
        try:
            geojson = json.loads(entity.boundary_geojson)
        except (json.JSONDecodeError, TypeError):
            geojson = None

    return EntityResponse(
        id=entity.id,
        entity_type=entity.entity_type,
        year_start=entity.year_start,
        year_end=entity.year_end,
        name_original=entity.name_original,
        name_original_lang=entity.name_original_lang,
        name_variants=entity.name_variants,
        capital=capital,
        boundary_geojson=geojson,
        confidence_score=entity.confidence_score,
        status=entity.status,
        territory_changes=entity.territory_changes,
        sources=entity.sources,
        ethical_notes=entity.ethical_notes,
    )


def _eager_query(db: Session):
    return db.query(GeoEntity).options(
        joinedload(GeoEntity.name_variants),
        joinedload(GeoEntity.territory_changes),
        joinedload(GeoEntity.sources),
    )


@router.get("/v1/entity", response_model=EntityListResponse)
def query_entity(
    name: str | None = Query(None, description="Nome (parziale) dell'entità"),
    year: int | None = Query(None, description="Anno di riferimento (negativo = a.C.)"),
    status: str | None = Query(None, description="Filtra per status: confirmed, uncertain, disputed"),
    db: Session = Depends(get_db),
):
    """Endpoint principale — vedi ADR-002.

    Cerca entità per nome e/o anno. Il nome viene cercato
    sia in name_original che nelle name_variants.
    """
    q = _eager_query(db)

    if name:
        pattern = f"%{name}%"
        variant_ids = (
            select(NameVariant.entity_id)
            .where(NameVariant.name.ilike(pattern))
        )
        q = q.filter(
            or_(
                GeoEntity.name_original.ilike(pattern),
                GeoEntity.id.in_(variant_ids),
            )
        )

    if year is not None:
        q = q.filter(GeoEntity.year_start <= year)
        q = q.filter(
            or_(GeoEntity.year_end.is_(None), GeoEntity.year_end >= year)
        )

    if status:
        q = q.filter(GeoEntity.status == status)

    results = q.all()
    entities = [_entity_to_response(e) for e in results]
    return EntityListResponse(count=len(entities), entities=entities)


@router.get("/v1/entities", response_model=EntityListResponse)
def list_entities(db: Session = Depends(get_db)):
    """Elenco completo di tutte le entità."""
    results = _eager_query(db).all()
    entities = [_entity_to_response(e) for e in results]
    return EntityListResponse(count=len(entities), entities=entities)


@router.get("/v1/entities/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: int, db: Session = Depends(get_db)):
    """Dettaglio di una singola entità per ID."""
    entity = _eager_query(db).filter(GeoEntity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entità non trovata")
    return _entity_to_response(entity)
