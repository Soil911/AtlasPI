"""Endpoint per Timeline Visualization — v6.17.

GET /timeline                       Interactive timeline HTML page
GET /v1/timeline-data               Optimized JSON payload for timeline rendering

Combines entities, events, and dynasty chains into a single lightweight
response optimized for the SVG timeline renderer.  No descriptions, no
GeoJSON — just the temporal fields the frontend needs.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from src.db.database import get_db
from src.db.models import ChainLink, DynastyChain, GeoEntity, HistoricalEvent

logger = logging.getLogger(__name__)

router = APIRouter()

STATIC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "static"


@router.get("/timeline", include_in_schema=False)
async def serve_timeline():
    """Serve the interactive timeline visualization page."""
    return FileResponse(STATIC_DIR / "timeline" / "index.html")


@router.get(
    "/v1/timeline-data",
    summary="Dati ottimizzati per la timeline",
    tags=["esportazione"],
    description=(
        "Restituisce entita', eventi e catene successorie in un unico payload "
        "leggero, ottimizzato per il rendering della timeline SVG interattiva. "
        "Nessuna descrizione, nessun GeoJSON — solo i campi temporali necessari. "
        "Cache aggressiva (1 ora)."
    ),
)
def get_timeline_data(
    response: Response,
    db: Session = Depends(get_db),
):
    # --- Entities: lightweight temporal data only ---
    entities_q = db.query(GeoEntity).all()
    entities = [
        {
            "id": e.id,
            "name": e.name_original,
            "type": e.entity_type,
            "year_start": e.year_start,
            "year_end": e.year_end,
            "status": e.status,
            "confidence": e.confidence_score,
        }
        for e in entities_q
    ]

    # --- Events: temporal + type + precision ---
    events_q = db.query(HistoricalEvent).all()
    events = [
        {
            "id": ev.id,
            "name": ev.name_original,
            "type": ev.event_type,
            "year": ev.year,
            "year_end": ev.year_end,
            "month": ev.month,
            "day": ev.day,
            "precision": ev.date_precision,
            "confidence": ev.confidence_score,
            "status": ev.status,
        }
        for ev in events_q
    ]

    # --- Chains: links with transition info ---
    chains_q = (
        db.query(DynastyChain)
        .options(joinedload(DynastyChain.links).joinedload(ChainLink.entity))
        .all()
    )
    # Dedup from joinedload
    seen_chains = set()
    chains = []
    for c in chains_q:
        if c.id in seen_chains:
            continue
        seen_chains.add(c.id)
        links = []
        for lk in c.links:
            links.append(
                {
                    "entity_id": lk.entity_id,
                    "entity_name": lk.entity.name_original if lk.entity else None,
                    "entity_year_start": lk.entity.year_start if lk.entity else None,
                    "entity_year_end": lk.entity.year_end if lk.entity else None,
                    "sequence": lk.sequence_order,
                    "year": lk.transition_year,
                    "transition": lk.transition_type,
                    "violent": lk.is_violent,
                }
            )
        chains.append(
            {
                "id": c.id,
                "name": c.name,
                "type": c.chain_type,
                "region": c.region,
                "links": links,
            }
        )

    # Aggressive cache — timeline data changes only on new deploys.
    response.headers["Cache-Control"] = "public, max-age=3600"

    return {
        "entities": entities,
        "events": events,
        "chains": chains,
    }
