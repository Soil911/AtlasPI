"""Endpoint per relazioni tra entità.

GET /v1/entities/{id}/related          entità correlate
GET /v1/entities/{id}/contemporaries   entità attive nello stesso periodo
GET /v1/entities/{id}/similar          entità più simili (scored)
GET /v1/entities/{id}/evolution        evoluzione temporale dell'entità
GET /v1/entities/{id}/timeline         timeline unificata (eventi + territory + chain)
GET /v1/compare/{id1}/{id2}            confronto tra due entità
"""

import json
import logging

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from src.api.errors import EntityNotFoundError
from src.cache import cache_response
from src.db.database import get_db
from src.db.models import (
    ChainLink,
    DynastyChain,
    EventEntityLink,
    GeoEntity,
    HistoricalEvent,
)

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


# ─── Similarity ──────────────────────────────────────────────


def _similarity_score(source: GeoEntity, candidate: GeoEntity) -> float:
    """Compute a 0.0-1.0 similarity score between two entities.

    Factors (weighted):
    - Same entity_type: +0.35
    - Temporal overlap ratio: +0.30 (proportion of overlapping years)
    - Duration similarity: +0.15 (how close lifespans are)
    - Similar confidence: +0.10
    - Same status: +0.10
    """
    score = 0.0

    # Type match (0.35)
    if source.entity_type == candidate.entity_type:
        score += 0.35

    # Temporal overlap (0.30)
    s_end = source.year_end or 2025
    c_end = candidate.year_end or 2025
    overlap = max(0, min(s_end, c_end) - max(source.year_start, candidate.year_start))
    s_dur = max(1, s_end - source.year_start)
    c_dur = max(1, c_end - candidate.year_start)
    max_dur = max(s_dur, c_dur)
    if max_dur > 0:
        score += 0.30 * (overlap / max_dur)

    # Duration similarity (0.15) — how similar the lifespans are
    dur_ratio = min(s_dur, c_dur) / max(s_dur, c_dur) if max(s_dur, c_dur) > 0 else 1.0
    score += 0.15 * dur_ratio

    # Confidence similarity (0.10)
    s_conf = source.confidence_score or 0.5
    c_conf = candidate.confidence_score or 0.5
    score += 0.10 * (1.0 - abs(s_conf - c_conf))

    # Same status (0.10)
    if source.status == candidate.status:
        score += 0.10

    return round(score, 3)


@router.get(
    "/v1/entities/{entity_id}/similar",
    summary="Entità più simili",
    description=(
        "Trova entità simili a quella data, ordinate per punteggio di similarità "
        "(0.0-1.0). Il punteggio considera: tipo di entità (35%), sovrapposizione "
        "temporale (30%), durata simile (15%), confidence simile (10%), stesso "
        "status (10%). Utile per agenti AI che cercano paragoni storici."
    ),
)
@cache_response(ttl_seconds=3600)
def get_similar(
    entity_id: int,
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    min_score: float = Query(0.3, ge=0.0, le=1.0, description="Minimum similarity score"),
    response: Response = None,
    db: Session = Depends(get_db),
):
    entity = db.query(GeoEntity).filter(GeoEntity.id == entity_id).first()
    if not entity:
        raise EntityNotFoundError(entity_id)

    # Score all candidates (excluding self)
    candidates = db.query(GeoEntity).filter(GeoEntity.id != entity_id).all()
    scored = []
    for c in candidates:
        s = _similarity_score(entity, c)
        if s >= min_score:
            scored.append((c, s))

    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:limit]

    response.headers["Cache-Control"] = "public, max-age=3600"

    return {
        "entity_id": entity_id,
        "entity_name": entity.name_original,
        "entity_type": entity.entity_type,
        "year_start": entity.year_start,
        "year_end": entity.year_end,
        "total_similar": len(scored),
        "similar": [
            {
                "id": c.id,
                "name_original": c.name_original,
                "entity_type": c.entity_type,
                "year_start": c.year_start,
                "year_end": c.year_end,
                "status": c.status,
                "confidence_score": c.confidence_score,
                "similarity_score": s,
            }
            for c, s in top
        ],
    }


# ─── Evolution ─────────────────────────────────────────────────


@router.get(
    "/v1/entities/{entity_id}/evolution",
    summary="Evoluzione temporale di un'entità",
    description=(
        "Restituisce la cronologia completa di un'entità: fondazione, "
        "cambiamenti territoriali ordinati, fase finale. Utile per agenti AI "
        "che devono ricostruire la storia di un'entità nel tempo."
    ),
)
def get_evolution(
    entity_id: int,
    response: Response,
    db: Session = Depends(get_db),
):
    """Cronologia completa di un'entità storica.

    ETHICS: ogni cambiamento territoriale mantiene il change_type
    originale (conquest, colonization, etc.) senza eufemismi.
    """
    entity = (
        db.query(GeoEntity)
        .options(
            joinedload(GeoEntity.territory_changes),
            joinedload(GeoEntity.sources),
            joinedload(GeoEntity.name_variants),
        )
        .filter(GeoEntity.id == entity_id)
        .first()
    )
    if not entity:
        raise EntityNotFoundError(entity_id)

    # Ordina cambiamenti per anno
    changes = sorted(entity.territory_changes, key=lambda tc: tc.year)

    # Calcola fasi: espansione, contrazione, stabilità
    expansion_years = sum(1 for tc in changes if tc.change_type in (
        "expansion", "conquest", "colonization", "unification",
    ))
    contraction_years = sum(1 for tc in changes if tc.change_type in (
        "contraction", "dissolution", "partition", "secession",
    ))

    duration = (entity.year_end or 2025) - entity.year_start

    response.headers["Cache-Control"] = "public, max-age=3600"

    return {
        "entity_id": entity_id,
        "name_original": entity.name_original,
        "entity_type": entity.entity_type,
        "year_start": entity.year_start,
        "year_end": entity.year_end,
        "duration_years": duration,
        "total_changes": len(changes),
        "summary": {
            "expansion_events": expansion_years,
            "contraction_events": contraction_years,
            "sources_count": len(entity.sources),
            "name_variants_count": len(entity.name_variants),
        },
        "timeline": [
            {
                "year": tc.year,
                "change_type": tc.change_type,
                "region": tc.region,
                "description": tc.description,
                "population_affected": tc.population_affected,
                "confidence_score": tc.confidence_score,
            }
            for tc in changes
        ],
    }


# ─── Unified Timeline (v6.7) ────────────────────────────────────


@router.get(
    "/v1/entities/{entity_id}/timeline",
    summary="Timeline unificata di un'entità",
    description=(
        "Fonde in un unico stream cronologico: "
        "(1) territory_changes dell'entità, "
        "(2) historical_events che coinvolgono l'entità (via event_entity_links), "
        "(3) chain_transitions dove l'entità entra/esce da una catena dinastica. "
        "Ogni evento ha un campo `kind` (territory_change|event|chain_transition) "
        "per disambiguare la sorgente. Utile per agenti AI che devono "
        "ricostruire la traiettoria completa di un'entità storica senza "
        "fare 3-4 chiamate separate."
    ),
)
def get_entity_timeline(
    entity_id: int,
    response: Response,
    include_entity_links: bool = Query(
        True,
        description=(
            "Se True include tutti gli eventi con un link all'entità (MAIN_ACTOR, "
            "VICTIM, PARTICIPANT, AFFECTED, WITNESS, FOUNDED, DISSOLVED). "
            "Se False include solo eventi dove l'entità è MAIN_ACTOR o FOUNDED/DISSOLVED."
        ),
    ),
    db: Session = Depends(get_db),
):
    """Timeline unificata — events + territory_changes + chain_transitions.

    ETHICS-007: event_type e change_type preservati letteralmente (GENOCIDE,
    COLONIAL_VIOLENCE, CONQUEST) senza eufemismi. role preservato (VICTIM non
    viene softened in "affected").
    """
    entity = (
        db.query(GeoEntity)
        .options(joinedload(GeoEntity.territory_changes))
        .filter(GeoEntity.id == entity_id)
        .first()
    )
    if not entity:
        raise EntityNotFoundError(entity_id)

    timeline: list[dict] = []

    # 1) Territory changes (ordered by year).
    for tc in entity.territory_changes:
        timeline.append(
            {
                "kind": "territory_change",
                "year": tc.year,
                "change_type": tc.change_type,
                "region": tc.region,
                "description": tc.description,
                "population_affected": tc.population_affected,
                "confidence_score": tc.confidence_score,
            }
        )

    # 2) Historical events linked to this entity.
    q_events = (
        db.query(HistoricalEvent, EventEntityLink.role, EventEntityLink.notes)
        .join(EventEntityLink, EventEntityLink.event_id == HistoricalEvent.id)
        .filter(EventEntityLink.entity_id == entity_id)
    )
    if not include_entity_links:
        q_events = q_events.filter(
            EventEntityLink.role.in_(["MAIN_ACTOR", "FOUNDED", "DISSOLVED"])
        )
    for ev, role, notes in q_events.all():
        timeline.append(
            {
                "kind": "event",
                "year": ev.year,
                "year_end": ev.year_end,
                "event_id": ev.id,
                "name_original": ev.name_original,
                "name_original_lang": ev.name_original_lang,
                "event_type": ev.event_type,  # ETHICS-007: preserved verbatim.
                "role": role,  # ETHICS-007: VICTIM stays VICTIM.
                "link_notes": notes,
                "main_actor": ev.main_actor,
                "known_silence": ev.known_silence,
                "confidence_score": ev.confidence_score,
                "status": ev.status,
            }
        )

    # 3) Chain transitions involving this entity.
    # For each chain_link with entity_id = X, include the transition INTO X
    # (from sequence_order-1) if it exists, and the transition OUT OF X
    # (the next link with sequence_order+1) if it exists.
    my_links = (
        db.query(ChainLink)
        .options(joinedload(ChainLink.chain))
        .filter(ChainLink.entity_id == entity_id)
        .all()
    )
    for ml in my_links:
        chain = ml.chain
        # Incoming transition (if this entity is not the first in the chain).
        if ml.transition_year is not None and ml.transition_type is not None:
            # Find the predecessor entity (sequence_order - 1).
            predecessor = (
                db.query(ChainLink)
                .options(joinedload(ChainLink.entity))
                .filter(
                    ChainLink.chain_id == chain.id,
                    ChainLink.sequence_order == ml.sequence_order - 1,
                )
                .first()
            )
            timeline.append(
                {
                    "kind": "chain_transition",
                    "year": ml.transition_year,
                    "chain_id": chain.id,
                    "chain_name": chain.name,
                    "chain_type": chain.chain_type,
                    "transition_type": ml.transition_type,  # ETHICS-002 preserved.
                    "is_violent": ml.is_violent,
                    "direction": "inbound",
                    "from_entity_id": predecessor.entity_id if predecessor else None,
                    "from_entity_name": (
                        predecessor.entity.name_original if predecessor else None
                    ),
                    "to_entity_id": entity_id,
                    "to_entity_name": entity.name_original,
                    "description": ml.description,
                    "ethical_notes": ml.ethical_notes,
                }
            )
        # Outgoing transition (if a successor exists in the same chain).
        successor = (
            db.query(ChainLink)
            .options(joinedload(ChainLink.entity))
            .filter(
                ChainLink.chain_id == chain.id,
                ChainLink.sequence_order == ml.sequence_order + 1,
            )
            .first()
        )
        if (
            successor is not None
            and successor.transition_year is not None
            and successor.transition_type is not None
        ):
            timeline.append(
                {
                    "kind": "chain_transition",
                    "year": successor.transition_year,
                    "chain_id": chain.id,
                    "chain_name": chain.name,
                    "chain_type": chain.chain_type,
                    "transition_type": successor.transition_type,
                    "is_violent": successor.is_violent,
                    "direction": "outbound",
                    "from_entity_id": entity_id,
                    "from_entity_name": entity.name_original,
                    "to_entity_id": successor.entity_id,
                    "to_entity_name": successor.entity.name_original,
                    "description": successor.description,
                    "ethical_notes": successor.ethical_notes,
                }
            )

    # Sort merged stream chronologically — ties resolved by kind priority
    # (events before territory_changes before chain_transitions of same year,
    # purely for stable rendering; no semantic meaning).
    kind_rank = {"event": 0, "territory_change": 1, "chain_transition": 2}
    timeline.sort(key=lambda e: (e["year"], kind_rank.get(e["kind"], 9)))

    counts = {
        "events": sum(1 for e in timeline if e["kind"] == "event"),
        "territory_changes": sum(1 for e in timeline if e["kind"] == "territory_change"),
        "chain_transitions": sum(1 for e in timeline if e["kind"] == "chain_transition"),
        "total": len(timeline),
    }

    response.headers["Cache-Control"] = "public, max-age=3600"

    return {
        "entity_id": entity_id,
        "entity_name": entity.name_original,
        "entity_type": entity.entity_type,
        "year_start": entity.year_start,
        "year_end": entity.year_end,
        "counts": counts,
        "timeline": timeline,
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
