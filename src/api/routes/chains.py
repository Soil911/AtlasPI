"""Endpoint per catene successorie / dinastiche — v6.5.

GET /v1/chains                          list + filter (chain_type, region, year)
GET /v1/chains/{id}                     detail (con links ordinati + entities)
GET /v1/chains/types                    enumera ChainType + TransitionType
GET /v1/entities/{id}/predecessors      catene in cui l'entità ha un predecessore
GET /v1/entities/{id}/successors        catene in cui l'entità ha un successore

ETHICS-002: il transition_type DEVE essere esplicito su ogni link.
CONQUEST e REVOLUTION non sono sostituibili da "succession" generico —
una conquista violenta NON è una successione pacifica, e il consumatore
dell'API deve poter distinguere.

ETHICS-003: catene IDEOLOGICAL (Holy Roman Empire → German Empire →
Third Reich) portano avvertimento esplicito che la self-proclaimed
continuità ≠ legittimità storica. ethical_notes obbligatorie.
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session, joinedload

from src.api.errors import AtlasError
from src.db.database import get_db
from src.db.enums import ChainType, TransitionType
from src.db.models import ChainLink, DynastyChain, GeoEntity

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chains"])


class ChainNotFoundError(AtlasError):
    def __init__(self, chain_id: int):
        super().__init__(404, f"Catena con id={chain_id} non trovata", "NOT_FOUND")


class EntityNotFoundError(AtlasError):
    def __init__(self, entity_id: int):
        super().__init__(404, f"Entità con id={entity_id} non trovata", "NOT_FOUND")


# ─── helpers ───────────────────────────────────────────────────────────────


def _chain_summary(c: DynastyChain) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "name_lang": c.name_lang,
        "chain_type": c.chain_type,
        "region": c.region,
        "confidence_score": c.confidence_score,
        "status": c.status,
        "link_count": len(c.links) if c.links else 0,
    }


def _link_dict(link: ChainLink, include_entity: bool = True) -> dict:
    out = {
        "id": link.id,
        "sequence_order": link.sequence_order,
        "transition_year": link.transition_year,
        "transition_type": link.transition_type,
        "is_violent": link.is_violent,
        "description": link.description,
        "ethical_notes": link.ethical_notes,
        "entity_id": link.entity_id,
    }
    if include_entity and link.entity is not None:
        out["entity_name"] = link.entity.name_original
        out["entity_lang"] = link.entity.name_original_lang
        out["entity_type"] = link.entity.entity_type
        out["entity_year_start"] = link.entity.year_start
        out["entity_year_end"] = link.entity.year_end
    return out


def _chain_detail(c: DynastyChain) -> dict:
    base = _chain_summary(c)
    sources = json.loads(c.sources) if c.sources else []
    base.update(
        {
            "description": c.description,
            "ethical_notes": c.ethical_notes,
            "sources": sources,
            "links": [_link_dict(l) for l in c.links],
        }
    )
    return base


# ─── CHAINS ────────────────────────────────────────────────────────────────


@router.get(
    "/v1/chains",
    summary="Lista catene successorie",
    description=(
        "Lista paginata di catene successorie / dinastiche / coloniali. "
        "Ogni catena lega più entità geopolitiche con un transition_type "
        "esplicito (ETHICS-002): CONQUEST e REVOLUTION non sono "
        "sostituibili da SUCCESSION generico. Filtri opzionali su "
        "chain_type, region, year (almeno una entità della catena attiva "
        "in quell'anno)."
    ),
)
def list_chains(
    response: Response,
    chain_type: str | None = Query(
        None,
        description="DYNASTY / SUCCESSION / RESTORATION / COLONIAL / IDEOLOGICAL / OTHER",
    ),
    region: str | None = Query(
        None, description="Filtro substring case-insensitive sul campo region"
    ),
    year: int | None = Query(
        None,
        description=(
            "Anno di interesse: ritorna catene con almeno un'entità attiva "
            "in quell'anno."
        ),
    ),
    status: str | None = Query(
        None, description="confirmed / uncertain / disputed"
    ),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(DynastyChain).options(joinedload(DynastyChain.links))

    if chain_type is not None:
        q = q.filter(DynastyChain.chain_type == chain_type)
    if region is not None:
        q = q.filter(DynastyChain.region.ilike(f"%{region}%"))
    if status is not None:
        q = q.filter(DynastyChain.status == status)

    if year is not None:
        # Catena attiva in `year` se almeno una sua entità è attiva.
        # year_start <= year <= year_end (o year_end IS NULL).
        chain_ids_active = (
            db.query(ChainLink.chain_id)
            .join(GeoEntity, GeoEntity.id == ChainLink.entity_id)
            .filter(GeoEntity.year_start <= year)
            .filter(
                (GeoEntity.year_end.is_(None)) | (GeoEntity.year_end >= year)
            )
            .distinct()
        )
        q = q.filter(DynastyChain.id.in_(chain_ids_active))

    total = q.distinct().count()
    results = (
        q.order_by(DynastyChain.name, DynastyChain.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    # Dedup (joinedload può duplicare le righe).
    seen = set()
    unique_results = []
    for c in results:
        if c.id not in seen:
            seen.add(c.id)
            unique_results.append(c)

    response.headers["Cache-Control"] = "public, max-age=1800"
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "chains": [_chain_summary(c) for c in unique_results],
    }


@router.get(
    "/v1/chains/types",
    summary="Enumera ChainType + TransitionType",
    description="Restituisce gli enum di tipologia per catene e transizioni.",
)
def list_chain_types(response: Response):
    response.headers["Cache-Control"] = "public, max-age=86400"
    chain_descriptions = {
        "DYNASTY": "Stessa entità politica con dinastie consecutive (es. Cina: Han→Tang→Song).",
        "SUCCESSION": "Una entità succede a un'altra su un tema territoriale/politico.",
        "RESTORATION": "Entità formalmente restaurata dopo interruzione (es. Restoration France 1814).",
        "COLONIAL": "Catena coloniale (es. Tawantinsuyu → Vicereame del Perù → Repubblica del Perù).",
        "IDEOLOGICAL": "Linea di continuità ideologica anche con cesura statale (avvertimento: continuità self-proclaimed ≠ legittimità).",
        "OTHER": "Altri tipi di catena.",
    }
    transition_descriptions = {
        "CONQUEST": "Conquista militare violenta. ETHICS-002: NON usare 'succession' generico.",
        "REVOLUTION": "Cambio di regime interno (es. 1789, 1917).",
        "REFORM": "Trasformazione legale/amministrativa (es. Diocletian 285).",
        "SUCCESSION": "Successione dinastica/legittima (no rottura politica).",
        "RESTORATION": "Ripristino formale dopo interruzione.",
        "DECOLONIZATION": "Indipendenza da potenza coloniale (es. India 1947).",
        "PARTITION": "Divisione territoriale (es. India/Pakistan 1947).",
        "UNIFICATION": "Fusione di più entità (es. Italia 1861).",
        "DISSOLUTION": "Collasso interno (es. URSS 1991).",
        "ANNEXATION": "Incorporazione formale (es. Texas 1845).",
        "OTHER": "Altri tipi di transizione.",
    }
    return {
        "chain_types": [
            {"type": t.value, "description": chain_descriptions.get(t.value, "")}
            for t in ChainType
        ],
        "transition_types": [
            {"type": t.value, "description": transition_descriptions.get(t.value, "")}
            for t in TransitionType
        ],
    }


@router.get(
    "/v1/chains/{chain_id}",
    summary="Dettaglio catena successoria",
    description=(
        "Dettaglio di una catena con tutti i link in ordine cronologico. "
        "Ogni link include transition_type esplicito (ETHICS-002) + "
        "is_violent + ethical_notes specifiche della transizione."
    ),
)
def get_chain(chain_id: int, response: Response, db: Session = Depends(get_db)):
    c = (
        db.query(DynastyChain)
        .options(joinedload(DynastyChain.links).joinedload(ChainLink.entity))
        .filter(DynastyChain.id == chain_id)
        .first()
    )
    if not c:
        raise ChainNotFoundError(chain_id)
    response.headers["Cache-Control"] = "public, max-age=3600"
    return _chain_detail(c)


# ─── PREDECESSORS / SUCCESSORS PER ENTITY ──────────────────────────────────


@router.get(
    "/v1/entities/{entity_id}/predecessors",
    summary="Predecessori di un'entità nelle catene",
    description=(
        "Restituisce le catene in cui questa entità ha un predecessore "
        "(sequence_order > 0), insieme al predecessore immediato e al "
        "tipo di transizione che ha portato A questa entità."
    ),
)
def get_entity_predecessors(
    entity_id: int, response: Response, db: Session = Depends(get_db)
):
    # Verifica che l'entità esista.
    ent = db.query(GeoEntity).filter(GeoEntity.id == entity_id).first()
    if not ent:
        raise EntityNotFoundError(entity_id)

    # Trova tutti i link in cui questa entità appare con sequence_order > 0
    # (cioè ha un predecessore nella stessa catena).
    my_links = (
        db.query(ChainLink)
        .options(joinedload(ChainLink.chain))
        .filter(ChainLink.entity_id == entity_id)
        .filter(ChainLink.sequence_order > 0)
        .all()
    )

    predecessors = []
    for ml in my_links:
        # Trova il predecessore: il link nella stessa catena con
        # sequence_order = ml.sequence_order - 1.
        pred_link = (
            db.query(ChainLink)
            .options(joinedload(ChainLink.entity))
            .filter(ChainLink.chain_id == ml.chain_id)
            .filter(ChainLink.sequence_order == ml.sequence_order - 1)
            .first()
        )
        if pred_link is None:
            continue
        predecessors.append({
            "chain_id": ml.chain_id,
            "chain_name": ml.chain.name if ml.chain else None,
            "chain_type": ml.chain.chain_type if ml.chain else None,
            "transition_year": ml.transition_year,
            "transition_type": ml.transition_type,
            "is_violent": ml.is_violent,
            "description": ml.description,
            "ethical_notes": ml.ethical_notes,
            "predecessor_entity_id": pred_link.entity_id,
            "predecessor_entity_name": (
                pred_link.entity.name_original if pred_link.entity else None
            ),
            "predecessor_year_end": (
                pred_link.entity.year_end if pred_link.entity else None
            ),
        })

    response.headers["Cache-Control"] = "public, max-age=3600"
    return {
        "entity_id": entity_id,
        "entity_name": ent.name_original,
        "predecessors": predecessors,
    }


@router.get(
    "/v1/entities/{entity_id}/successors",
    summary="Successori di un'entità nelle catene",
    description=(
        "Restituisce le catene in cui questa entità ha un successore, "
        "insieme al successore immediato e al tipo di transizione che "
        "ha portato DA questa entità all'entità successiva."
    ),
)
def get_entity_successors(
    entity_id: int, response: Response, db: Session = Depends(get_db)
):
    ent = db.query(GeoEntity).filter(GeoEntity.id == entity_id).first()
    if not ent:
        raise EntityNotFoundError(entity_id)

    # Trova tutti i link in cui questa entità appare. Per ognuno, se esiste
    # un link successivo nella stessa catena, lo riportiamo come successor.
    my_links = (
        db.query(ChainLink)
        .options(joinedload(ChainLink.chain))
        .filter(ChainLink.entity_id == entity_id)
        .all()
    )

    successors = []
    for ml in my_links:
        # Trova il successore: il link nella stessa catena con
        # sequence_order = ml.sequence_order + 1.
        succ_link = (
            db.query(ChainLink)
            .options(joinedload(ChainLink.entity))
            .filter(ChainLink.chain_id == ml.chain_id)
            .filter(ChainLink.sequence_order == ml.sequence_order + 1)
            .first()
        )
        if succ_link is None:
            continue
        successors.append({
            "chain_id": ml.chain_id,
            "chain_name": ml.chain.name if ml.chain else None,
            "chain_type": ml.chain.chain_type if ml.chain else None,
            "transition_year": succ_link.transition_year,
            "transition_type": succ_link.transition_type,
            "is_violent": succ_link.is_violent,
            "description": succ_link.description,
            "ethical_notes": succ_link.ethical_notes,
            "successor_entity_id": succ_link.entity_id,
            "successor_entity_name": (
                succ_link.entity.name_original if succ_link.entity else None
            ),
            "successor_year_start": (
                succ_link.entity.year_start if succ_link.entity else None
            ),
        })

    response.headers["Cache-Control"] = "public, max-age=3600"
    return {
        "entity_id": entity_id,
        "entity_name": ent.name_original,
        "successors": successors,
    }
