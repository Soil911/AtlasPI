"""Endpoint per le entità geopolitiche — vedi ADR-002.

GET /v1/entity?name=...&year=...&status=...   query principale
GET /v1/entities?limit=...&offset=...          elenco paginato
GET /v1/entities/{id}                          dettaglio entità
"""

import json
import logging
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from src.api.errors import EntityNotFoundError
from src.api.schemas import (
    CapitalResponse,
    EntityResponse,
    PaginatedEntityResponse,
)
from src.db.database import get_db
from src.db.models import GeoEntity, NameVariant

logger = logging.getLogger(__name__)

router = APIRouter(tags=["entità"])

# Tipo per validazione status
StatusFilter = Literal["confirmed", "uncertain", "disputed"] | None


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
            logger.warning("GeoJSON malformato per entità %d", entity.id)

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


@router.get(
    "/v1/entity",
    response_model=PaginatedEntityResponse,
    summary="Cerca entità per nome e/o anno",
    description=(
        "Endpoint principale (ADR-002). Cerca per nome (anche varianti), "
        "filtra per anno e status. Il nome viene cercato con match parziale "
        "sia in name_original che nelle name_variants."
    ),
)
def query_entity(
    response: Response,
    name: str | None = Query(None, max_length=200, description="Nome (parziale) dell'entità"),
    year: int | None = Query(None, ge=-4000, le=2100, description="Anno di riferimento (negativo = a.C.)"),
    status: StatusFilter = Query(None, description="Filtra per status"),
    limit: int = Query(20, ge=1, le=100, description="Risultati per pagina"),
    offset: int = Query(0, ge=0, description="Offset per paginazione"),
    db: Session = Depends(get_db),
):
    q = _eager_query(db)

    if name:
        pattern = f"%{name}%"
        variant_ids = select(NameVariant.entity_id).where(NameVariant.name.ilike(pattern))
        q = q.filter(
            or_(
                GeoEntity.name_original.ilike(pattern),
                GeoEntity.id.in_(variant_ids),
            )
        )

    if year is not None:
        q = q.filter(GeoEntity.year_start <= year)
        q = q.filter(or_(GeoEntity.year_end.is_(None), GeoEntity.year_end >= year))

    if status:
        q = q.filter(GeoEntity.status == status)

    # Conta totale prima della paginazione
    total = q.count()

    results = q.offset(offset).limit(limit).all()
    entities = [_entity_to_response(e) for e in results]

    # Cache: dati storici cambiano raramente
    response.headers["Cache-Control"] = "public, max-age=3600"

    return PaginatedEntityResponse(count=total, limit=limit, offset=offset, entities=entities)


@router.get(
    "/v1/entities",
    response_model=PaginatedEntityResponse,
    summary="Elenco paginato di tutte le entità",
)
def list_entities(
    response: Response,
    limit: int = Query(20, ge=1, le=100, description="Risultati per pagina"),
    offset: int = Query(0, ge=0, description="Offset"),
    db: Session = Depends(get_db),
):
    total = db.query(GeoEntity).count()
    results = _eager_query(db).offset(offset).limit(limit).all()
    entities = [_entity_to_response(e) for e in results]

    response.headers["Cache-Control"] = "public, max-age=3600"

    return PaginatedEntityResponse(count=total, limit=limit, offset=offset, entities=entities)


@router.get(
    "/v1/entities/{entity_id}",
    response_model=EntityResponse,
    summary="Dettaglio di una singola entità",
)
def get_entity(entity_id: int, response: Response, db: Session = Depends(get_db)):
    entity = _eager_query(db).filter(GeoEntity.id == entity_id).first()
    if not entity:
        raise EntityNotFoundError(entity_id)

    response.headers["Cache-Control"] = "public, max-age=3600"

    return _entity_to_response(entity)
