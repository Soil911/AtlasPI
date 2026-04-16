"""Entity Comparison Tool — v6.18.

GET /compare                            Interactive comparison page
GET /v1/compare?ids=1,2,3               Multi-entity comparison API

Extends the existing /v1/compare/{id1}/{id2} (two-entity) endpoint in
relations.py with a richer multi-entity comparison that includes events,
chain context, and temporal overlap calculation.

ETHICS: comparison data preserves all ethical metadata (status, confidence,
ethical_notes, known_silence on events). The tool does NOT rank entities
by "importance" — it presents them side by side and lets the user draw
conclusions. Disputed territories and contested events are marked as such.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from src.api.errors import AtlasError, EntityNotFoundError
from src.db.database import get_db
from src.db.models import (
    ChainLink,
    DynastyChain,
    EventEntityLink,
    GeoEntity,
    HistoricalEvent,
    NameVariant,
)

logger = logging.getLogger(__name__)

router = APIRouter()

STATIC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "static"


@router.get("/compare", include_in_schema=False)
async def serve_compare():
    """Serve the interactive entity comparison page."""
    return FileResponse(STATIC_DIR / "compare" / "index.html")


def _entity_detail(entity: GeoEntity) -> dict:
    """Full entity detail for comparison view."""
    # Get English name variant if available
    english_name = None
    for nv in entity.name_variants:
        if nv.lang == "en":
            english_name = nv.name
            break

    return {
        "id": entity.id,
        "name_original": entity.name_original,
        "name_original_lang": entity.name_original_lang,
        "name_english": english_name,
        "entity_type": entity.entity_type,
        "year_start": entity.year_start,
        "year_end": entity.year_end,
        "duration_years": (entity.year_end or 2025) - entity.year_start,
        "capital": {
            "name": entity.capital_name,
            "lat": entity.capital_lat,
            "lon": entity.capital_lon,
        }
        if entity.capital_name
        else None,
        "confidence_score": entity.confidence_score,
        "status": entity.status,
        "ethical_notes": entity.ethical_notes,
        "name_variants_count": len(entity.name_variants),
        "territory_changes_count": len(entity.territory_changes),
        "sources_count": len(entity.sources),
        "has_boundary": entity.boundary_geojson is not None,
        "boundary_source": entity.boundary_source,
    }


def _event_summary(ev: HistoricalEvent) -> dict:
    """Compact event representation for comparison."""
    return {
        "id": ev.id,
        "name_original": ev.name_original,
        "event_type": ev.event_type,
        "year": ev.year,
        "year_end": ev.year_end,
        "month": ev.month,
        "day": ev.day,
        "date_precision": ev.date_precision,
        "main_actor": ev.main_actor,
        "status": ev.status,
        "confidence_score": ev.confidence_score,
        "known_silence": ev.known_silence,
    }


@router.get(
    "/v1/compare",
    summary="Confronta 2-4 entita' storiche",
    tags=["relazioni"],
    description=(
        "Confronto multi-entita' strutturato. Restituisce dettagli completi "
        "per ogni entita', eventi collegati, catene successorie e calcolo "
        "dell'overlap temporale. Minimo 2, massimo 4 entita' per richiesta."
    ),
)
def compare_entities(
    response: Response,
    ids: str = Query(
        ...,
        description="Comma-separated entity IDs (2-4), e.g. ids=1,2,3",
        examples=["1,2"],
    ),
    db: Session = Depends(get_db),
):
    # Parse and validate IDs
    try:
        id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    except ValueError:
        raise AtlasError(
            422,
            "ids must be comma-separated integers, e.g. ids=1,2,3",
            "VALIDATION_ERROR",
        )

    if len(id_list) < 2:
        raise AtlasError(
            422,
            "At least 2 entity IDs required for comparison",
            "VALIDATION_ERROR",
        )

    if len(id_list) > 4:
        raise AtlasError(
            422,
            "Maximum 4 entity IDs allowed for comparison",
            "VALIDATION_ERROR",
        )

    # Remove duplicates preserving order
    seen = set()
    unique_ids = []
    for eid in id_list:
        if eid not in seen:
            seen.add(eid)
            unique_ids.append(eid)
    id_list = unique_ids

    if len(id_list) < 2:
        raise AtlasError(
            422,
            "At least 2 distinct entity IDs required for comparison",
            "VALIDATION_ERROR",
        )

    # Fetch entities with eager loading
    entities = (
        db.query(GeoEntity)
        .options(
            joinedload(GeoEntity.name_variants),
            joinedload(GeoEntity.territory_changes),
            joinedload(GeoEntity.sources),
        )
        .filter(GeoEntity.id.in_(id_list))
        .all()
    )

    # Check all IDs were found
    found_ids = {e.id for e in entities}
    missing = [eid for eid in id_list if eid not in found_ids]
    if missing:
        raise AtlasError(
            404,
            f"Entities not found: {missing}",
            "NOT_FOUND",
        )

    # Preserve requested order
    entity_map = {e.id: e for e in entities}
    entities = [entity_map[eid] for eid in id_list]

    # Build entity details
    entity_details = [_entity_detail(e) for e in entities]

    # Fetch events for each entity
    events_by_entity = {}
    all_event_ids = set()
    for e in entities:
        links = (
            db.query(HistoricalEvent, EventEntityLink.role)
            .join(EventEntityLink, EventEntityLink.event_id == HistoricalEvent.id)
            .filter(EventEntityLink.entity_id == e.id)
            .all()
        )
        evts = []
        for ev, role in links:
            evt_data = _event_summary(ev)
            evt_data["role"] = role
            evts.append(evt_data)
            all_event_ids.add(ev.id)
        evts.sort(key=lambda x: x["year"])
        events_by_entity[str(e.id)] = evts

    # Find common events (events linked to more than one compared entity)
    event_entity_map: dict[int, list[int]] = {}
    for e in entities:
        links = (
            db.query(EventEntityLink)
            .filter(EventEntityLink.entity_id == e.id)
            .all()
        )
        for lk in links:
            if lk.event_id not in event_entity_map:
                event_entity_map[lk.event_id] = []
            event_entity_map[lk.event_id].append(e.id)

    common_event_ids = [
        eid for eid, ents in event_entity_map.items() if len(ents) > 1
    ]
    common_events = []
    if common_event_ids:
        common_evts = (
            db.query(HistoricalEvent)
            .filter(HistoricalEvent.id.in_(common_event_ids))
            .all()
        )
        for ev in common_evts:
            evt_data = _event_summary(ev)
            evt_data["shared_by"] = event_entity_map[ev.id]
            common_events.append(evt_data)
        common_events.sort(key=lambda x: x["year"])

    # Fetch chain context for each entity
    chains_by_entity = {}
    for e in entities:
        my_links = (
            db.query(ChainLink)
            .options(
                joinedload(ChainLink.chain).joinedload(DynastyChain.links).joinedload(ChainLink.entity)
            )
            .filter(ChainLink.entity_id == e.id)
            .all()
        )
        chains = []
        seen_chains = set()
        for ml in my_links:
            if ml.chain_id in seen_chains:
                continue
            seen_chains.add(ml.chain_id)
            chain = ml.chain
            chain_links = sorted(chain.links, key=lambda lk: lk.sequence_order)
            chains.append({
                "chain_id": chain.id,
                "chain_name": chain.name,
                "chain_type": chain.chain_type,
                "region": chain.region,
                "links": [
                    {
                        "entity_id": lk.entity_id,
                        "entity_name": lk.entity.name_original if lk.entity else None,
                        "sequence": lk.sequence_order,
                        "transition_year": lk.transition_year,
                        "transition_type": lk.transition_type,
                        "is_violent": lk.is_violent,
                        "is_compared": lk.entity_id in found_ids,
                    }
                    for lk in chain_links
                ],
            })
        chains_by_entity[str(e.id)] = chains

    # Calculate temporal overlap (pairwise for all combinations)
    # Also calculate global overlap (period when ALL entities coexist)
    global_start = max(e.year_start for e in entities)
    global_end = min(e.year_end or 2025 for e in entities)
    global_overlap_years = max(0, global_end - global_start)

    overlap = {
        "all": {
            "start": global_start if global_overlap_years > 0 else None,
            "end": global_end if global_overlap_years > 0 else None,
            "years": global_overlap_years,
        },
    }

    # Pairwise overlaps
    pairwise = []
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            e1, e2 = entities[i], entities[j]
            ov_start = max(e1.year_start, e2.year_start)
            ov_end = min(e1.year_end or 2025, e2.year_end or 2025)
            ov_years = max(0, ov_end - ov_start)
            pairwise.append({
                "entity_ids": [e1.id, e2.id],
                "start": ov_start if ov_years > 0 else None,
                "end": ov_end if ov_years > 0 else None,
                "years": ov_years,
            })
    overlap["pairwise"] = pairwise

    response.headers["Cache-Control"] = "public, max-age=3600"

    return {
        "entities": entity_details,
        "events_by_entity": events_by_entity,
        "chains_by_entity": chains_by_entity,
        "overlap": overlap,
        "common_events": common_events,
    }
