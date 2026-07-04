"""Endpoint per eventi storici — v6.3 + v6.14 date precision.

GET  /v1/events                          list + filter (year, event_type, status, known_silence, month, day)
GET  /v1/events/types                    enumera EventType
GET  /v1/events/map                      lightweight payload for map marker rendering
GET  /v1/events/on-this-day/{mm_dd}      eventi che cadono in un dato giorno/mese
GET  /v1/events/at-date/{date_str}       eventi in una data esatta (supporta BCE)
GET  /v1/events/date-coverage            quali date MM-DD hanno eventi
GET  /v1/events/{id}                     detail
GET  /v1/entities/{id}/events            events linked to an entity

ETHICS-007: ogni evento espone main_actor + event_entity_links.role in
voce attiva. Terminologia accademica (GENOCIDE, COLONIAL_VIOLENCE)
non viene sostituita da eufemismi.

ETHICS-008: il filtro `known_silence=true` permette a ricercatori di
estrarre specificamente gli eventi la cui documentazione contemporanea
è assente/cancellata, distinguendoli dagli eventi non documentati.
"""

from __future__ import annotations

import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from src.api.errors import AtlasError, EntityNotFoundError
from src.api.schemas import EventListResponse
from src.cache import cache_response
from src.db.database import get_db
from src.db.enums import EventRole, EventType
from src.db.models import EventEntityLink, GeoEntity, HistoricalEvent

logger = logging.getLogger(__name__)

router = APIRouter(tags=["events"])


class EventNotFoundError(AtlasError):
    def __init__(self, event_id: int):
        super().__init__(404, f"Event with id={event_id} not found", "NOT_FOUND")


def _event_summary(e: HistoricalEvent, include_entities: bool = False) -> dict:
    """Rappresentazione compatta di un evento (usata nelle liste).

    v6.14: include i campi di date precision (month, day, date_precision,
    iso_date) anche nel summary — consente al client di ordinare/filtrare
    senza fetch del detail.

    v6.66 FIX 3: aggiunti location_lat/lon al summary. Il frontend usa
    /v1/events (list) per clusterizzare eventi sulla mappa e non poteva
    farlo senza coordinate. location_name e' la stringa human-readable,
    location_lat/lon sono i valori numerici per il rendering markers.

    v6.99.120 (agent-UX, M3): `include_entities=True` aggiunge gli
    entity_links leggeri (id, nome, ruolo). on-this-day/at-date forzavano
    un fetch di detail per OGNI evento solo per sapere QUALI entità erano
    coinvolte (N+1 lato client). Va usato SOLO con eager-loading
    (joinedload di entity_links → entity) per non spostare l'N+1 sul DB.
    """
    base = _event_summary_base(e)
    if include_entities:
        base["entities"] = [
            {
                "entity_id": link.entity_id,
                "entity_name": link.entity.name_original if link.entity else None,
                "role": link.role,
            }
            for link in e.entity_links
        ]
    return base


def _event_summary_base(e: HistoricalEvent) -> dict:
    return {
        "id": e.id,
        "name_original": e.name_original,
        "name_original_lang": e.name_original_lang,
        "event_type": e.event_type,
        "year": e.year,
        "year_end": e.year_end,
        # v6.14 date precision fields.
        "month": e.month,
        "day": e.day,
        "date_precision": e.date_precision,
        "iso_date": e.iso_date,
        "location_name": e.location_name,
        # v6.66 FIX 3: coordinate per map rendering in list view.
        "location_lat": e.location_lat,
        "location_lon": e.location_lon,
        "main_actor": e.main_actor,
        "status": e.status,
        "confidence_score": e.confidence_score,
        "known_silence": e.known_silence,
        # v6.99.109 (agent-UX): estratto della descrizione anche nel summary —
        # on-this-day/liste forzavano un fetch di detail per OGNI evento (N+1)
        # solo per capire di cosa parlasse l'evento.
        "description_short": (
            (e.description[:277] + "...")
            if e.description and len(e.description) > 280
            else e.description
        ),
    }


def _event_detail(e: HistoricalEvent) -> dict:
    """Rappresentazione completa di un evento (singola entità).

    v6.14: aggiunge calendar_note al detail (non nel summary perché è
    potenzialmente lungo e serve solo a chi ispeziona un singolo evento).
    """
    base = _event_summary(e)
    base.update(
        {
            # v6.14: calendar_note solo nel detail.
            "calendar_note": e.calendar_note,
            "location_lat": e.location_lat,
            "location_lon": e.location_lon,
            "description": e.description,
            "casualties_low": e.casualties_low,
            "casualties_high": e.casualties_high,
            "casualties_source": e.casualties_source,
            "silence_reason": e.silence_reason,
            "ethical_notes": e.ethical_notes,
            "entity_links": [
                {
                    "entity_id": link.entity_id,
                    "entity_name": link.entity.name_original if link.entity else None,
                    "role": link.role,
                    "notes": link.notes,
                }
                for link in e.entity_links
            ],
            "sources": [
                {
                    "citation": s.citation,
                    "url": s.url,
                    "source_type": s.source_type,
                }
                for s in e.sources
            ],
        }
    )
    return base


@router.get(
    "/v1/events",
    response_model=EventListResponse,
    summary="List historical events",
    description=(
        "Paginated list of historical events with filters on year, type, status and silences. "
        "ETHICS-007: no euphemisms in EventType terms (GENOCIDE, COLONIAL_VIOLENCE, ...). "
        "ETHICS-008: `known_silence=true` returns only events whose contemporary "
        "documentation is absent/erased."
    ),
)
@cache_response(ttl_seconds=300)
def list_events(
    request: Request,
    response: Response,
    year_min: int | None = Query(None, description="Minimum year (inclusive)"),
    year_max: int | None = Query(None, description="Maximum year (inclusive)"),
    event_type: str | None = Query(None, description="Filter by EventType (e.g. BATTLE, GENOCIDE)"),
    status: str | None = Query(None, description="confirmed / uncertain / disputed"),
    known_silence: bool | None = Query(None, description="Only events with documented silence"),
    # v6.14: date precision filters.
    month: int | None = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    day: int | None = Query(None, ge=1, le=31, description="Filter by day (1-31)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(HistoricalEvent)

    if year_min is not None:
        q = q.filter(HistoricalEvent.year >= year_min)
    if year_max is not None:
        q = q.filter(
            or_(HistoricalEvent.year <= year_max, HistoricalEvent.year_end <= year_max)
        )
    if event_type is not None:
        # Case-sensitive against enum — matches tokenization in seed data.
        q = q.filter(HistoricalEvent.event_type == event_type)
    if status is not None:
        q = q.filter(HistoricalEvent.status == status)
    if known_silence is not None:
        q = q.filter(HistoricalEvent.known_silence == known_silence)
    # v6.14: sub-annual filters.
    if month is not None:
        q = q.filter(HistoricalEvent.month == month)
    if day is not None:
        q = q.filter(HistoricalEvent.day == day)

    total = q.count()
    results = q.order_by(HistoricalEvent.year, HistoricalEvent.id).offset(offset).limit(limit).all()

    response.headers["Cache-Control"] = "public, max-age=1800"

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "events": [_event_summary(e) for e in results],
    }


@router.get(
    "/v1/events/types",
    summary="Enumerate event types",
    description=(
        "Returns the supported event types (EventType enum) "
        "with a short description of correct usage. "
        "ETHICS-007: the terms are explicit — GENOCIDE, COLONIAL_VIOLENCE, "
        "ETHNIC_CLEANSING, MASSACRE, DEPORTATION — and must not be replaced "
        "with euphemisms."
    ),
)
def list_event_types(response: Response):
    response.headers["Cache-Control"] = "public, max-age=86400"

    descriptions = {
        "BATTLE": "Military engagement bounded in time.",
        "SIEGE": "Siege of a city or fortification.",
        "TREATY": "Formal agreement between entities.",
        "REBELLION": "Insurrection against established power.",
        "REVOLUTION": "Regime change at a political-social scale.",
        "CORONATION": "Accession of a ruler to the throne.",
        "DEATH_OF_RULER": "Death of a ruler (natural or violent).",
        "MARRIAGE_DYNASTIC": "Marriage union with dynastic/territorial impact.",
        "FOUNDING_CITY": "Founding of a city.",
        "FOUNDING_STATE": "Founding of a geopolitical entity.",
        "DISSOLUTION_STATE": "Dissolution of a geopolitical entity.",
        "CONQUEST": "Military territorial annexation.",
        "COLONIAL_VIOLENCE": "Organized colonial violence — NOT 'pacification'.",
        "GENOCIDE": "Systematic destruction of a group — NOT 'massacre' nor 'conflict'.",
        "ETHNIC_CLEANSING": "Forced ethnic removal — NOT 'population exchange'.",
        "MASSACRE": "Mass killing at sub-genocidal scale.",
        "DEPORTATION": "Forced transfer of population.",
        "MIGRATION": "Mass movement of population (e.g. Bantu expansion, Slavic settlement).",
        "COLLAPSE": "State/civilizational collapse (distinct from deliberate dissolution).",
        "FAMINE": "Structural famine — NOT 'food crisis'.",
        "EPIDEMIC": "Epidemic or pandemic.",
        "EARTHQUAKE": "Documented earthquake.",
        "VOLCANIC_ERUPTION": "Volcanic eruption.",
        "TSUNAMI": "Tsunami.",
        "FLOOD": "Major flood.",
        "DROUGHT": "Extended drought.",
        "FIRE": "Catastrophic fire.",
        "EXPLORATION": "Geographic exploration (careful framing, ETHICS-007).",
        "TRADE_AGREEMENT": "Formal trade agreement.",
        "RELIGIOUS_EVENT": "Religious conversion, schism, or proclamation.",
        "INTELLECTUAL_EVENT": "Publication or erasure of a foundational work.",
        "TECHNOLOGICAL_EVENT": "Invention or adoption of technology.",
        "OTHER": "Event not classifiable under the preceding types.",
    }

    return {
        "event_types": [
            {"type": t.value, "description": descriptions.get(t.value, "")}
            for t in EventType
        ],
        "event_roles": [
            {"role": r.value} for r in EventRole
        ],
    }


# ─── Map display endpoint ───────────────────────────────────────────────────


def _event_map_marker(e: HistoricalEvent) -> dict:
    """Minimal representation of an event for map marker rendering.

    Only the fields needed to place and label a marker on the map.
    Heavier fields (description, sources, entity_links, casualties)
    are excluded — the client fetches /v1/events/{id} on click.
    """
    return {
        "id": e.id,
        "name_original": e.name_original,
        "event_type": e.event_type,
        "year": e.year,
        "location_lat": e.location_lat,
        "location_lon": e.location_lon,
        "location_name": e.location_name,
        "status": e.status,
        "confidence_score": e.confidence_score,
        "main_actor": e.main_actor,
    }


@cache_response(ttl_seconds=300)
@router.get(
    "/v1/events/map",
    summary="Events for map display",
    description=(
        "Lightweight payload optimized for map marker rendering. "
        "Returns only events with coordinates (non-null lat/lon) within "
        "a temporal window centered on `year`. The window auto-expands "
        "for ancient eras: ±50 for years < -1000, ±25 for years from -1000 to 0."
    ),
)
def events_for_map(
    year: int = Query(..., description="Central year of the temporal window"),
    window: int = Query(10, ge=1, le=500, description="Window half-width in years (auto-expanded for ancient eras)"),
    limit: int = Query(200, ge=1, le=500, description="Maximum number of events"),
    response: Response = None,
    db: Session = Depends(get_db),
):
    # Auto-expand window for ancient periods where data is sparser.
    effective_window = window
    if year < -1000:
        effective_window = max(window, 50)
    elif year < 0:
        effective_window = max(window, 25)

    year_min = year - effective_window
    year_max = year + effective_window

    q = (
        db.query(HistoricalEvent)
        .filter(
            HistoricalEvent.location_lat.isnot(None),
            HistoricalEvent.location_lon.isnot(None),
            HistoricalEvent.year >= year_min,
            HistoricalEvent.year <= year_max,
        )
        .order_by(HistoricalEvent.year, HistoricalEvent.id)
    )

    total = q.count()
    results = q.limit(limit).all()

    response.headers["Cache-Control"] = "public, max-age=300"

    return {
        "year": year,
        "window": effective_window,
        "total": total,
        "events": [_event_map_marker(e) for e in results],
    }


# ─── v6.14: Date Precision endpoints ────────────────────────────────────────

_MM_DD_RE = re.compile(r"^\d{2}-\d{2}$")
_DATE_RE = re.compile(r"^-?\d{4}-\d{2}-\d{2}$")


@router.get(
    "/v1/events/on-this-day/{mm_dd}",
    summary="Events that occurred on a given day of the year",
    description=(
        "Returns historical events with matching month/day, ordered by year. "
        "Path format: MM-DD (e.g. 07-14 for July 14). "
        "Returns an empty list (not 404) if no event matches."
    ),
)
def events_on_this_day(
    mm_dd: str = Path(..., description="Month-day in MM-DD format", pattern=r"^\d{2}-\d{2}$"),
    response: Response = None,
    db: Session = Depends(get_db),
):
    if not _MM_DD_RE.match(mm_dd):
        raise HTTPException(status_code=422, detail="Required format: MM-DD (e.g. 07-14)")

    parts = mm_dd.split("-")
    m, d = int(parts[0]), int(parts[1])

    if m < 1 or m > 12:
        raise HTTPException(status_code=422, detail=f"Invalid month: {m} (1-12)")
    if d < 1 or d > 31:
        raise HTTPException(status_code=422, detail=f"Invalid day: {d} (1-31)")

    results = (
        db.query(HistoricalEvent)
        .options(joinedload(HistoricalEvent.entity_links).joinedload(EventEntityLink.entity))
        .filter(HistoricalEvent.month == m, HistoricalEvent.day == d)
        .order_by(HistoricalEvent.year)
        .all()
    )

    response.headers["Cache-Control"] = "public, max-age=3600"

    return {
        "month": m,
        "day": d,
        "total": len(results),
        "events": [_event_summary(e, include_entities=True) for e in results],
    }


@router.get(
    "/v1/events/at-date/{date_str}",
    summary="Events at an exact date",
    description=(
        "Returns events at an exact ISO-like date. "
        "Format: YYYY-MM-DD (e.g. 1789-07-14) or -YYYY-MM-DD for BCE "
        "(e.g. -0331-10-01 for October 1, 331 BCE). "
        "Returns an empty list (not 404) if no event matches."
    ),
)
def events_at_date(
    date_str: str = Path(..., description="Date in [-]YYYY-MM-DD format"),
    response: Response = None,
    db: Session = Depends(get_db),
):
    if not _DATE_RE.match(date_str):
        raise HTTPException(
            status_code=422,
            detail="Required format: YYYY-MM-DD or -YYYY-MM-DD for BCE (e.g. -0331-10-01)",
        )

    # Parse year (may be negative for BCE), month, day.
    if date_str.startswith("-"):
        # BCE: e.g. "-0331-10-01" → year=-331, month=10, day=1
        rest = date_str[1:]  # "0331-10-01"
        parts = rest.split("-")
        year = -int(parts[0])
        m = int(parts[1])
        d = int(parts[2])
    else:
        parts = date_str.split("-")
        year = int(parts[0])
        m = int(parts[1])
        d = int(parts[2])

    if m < 1 or m > 12:
        raise HTTPException(status_code=422, detail=f"Invalid month: {m} (1-12)")
    if d < 1 or d > 31:
        raise HTTPException(status_code=422, detail=f"Invalid day: {d} (1-31)")

    results = (
        db.query(HistoricalEvent)
        .options(joinedload(HistoricalEvent.entity_links).joinedload(EventEntityLink.entity))
        .filter(
            HistoricalEvent.year == year,
            HistoricalEvent.month == m,
            HistoricalEvent.day == d,
        )
        .order_by(HistoricalEvent.id)
        .all()
    )

    response.headers["Cache-Control"] = "public, max-age=3600"

    return {
        "date": date_str,
        "year": year,
        "month": m,
        "day": d,
        "total": len(results),
        "events": [_event_summary(e, include_entities=True) for e in results],
    }


@router.get(
    "/v1/events/date-coverage",
    summary="Date coverage for on-this-day",
    description=(
        "Returns the dates (MM-DD) that have at least one event in the dataset. "
        "Useful for an AI agent that wants to know, before calling "
        "on-this-day, whether that date will have results, or to suggest "
        "'interesting' dates to the user."
    ),
)
@cache_response(ttl_seconds=3600)
def events_date_coverage(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    from sqlalchemy import func

    rows = (
        db.query(
            HistoricalEvent.month,
            HistoricalEvent.day,
            func.count(HistoricalEvent.id).label("event_count"),
        )
        .filter(HistoricalEvent.month.isnot(None), HistoricalEvent.day.isnot(None))
        .group_by(HistoricalEvent.month, HistoricalEvent.day)
        .order_by(HistoricalEvent.month, HistoricalEvent.day)
        .all()
    )

    dates = [
        {
            "mm_dd": f"{r.month:02d}-{r.day:02d}",
            "month": r.month,
            "day": r.day,
            "event_count": r.event_count,
        }
        for r in rows
    ]

    total_events_with_date = sum(d["event_count"] for d in dates)

    response.headers["Cache-Control"] = "public, max-age=3600"

    return {
        "unique_dates": len(dates),
        "total_days_in_year": 366,
        "coverage_pct": round(len(dates) / 366 * 100, 1),
        "total_events_with_date": total_events_with_date,
        "dates": dates,
    }


@router.get(
    "/v1/events/{event_id}",
    summary="Historical event detail",
    description=(
        "Full detail of an event with entity_links (explicit role for "
        "each involved entity) and sources. ETHICS-007: main_actor is mandatory."
    ),
)
@cache_response(ttl_seconds=3600)
def get_event(event_id: int, request: Request, response: Response, db: Session = Depends(get_db)):
    event = (
        db.query(HistoricalEvent)
        .options(
            joinedload(HistoricalEvent.entity_links).joinedload(EventEntityLink.entity),
            joinedload(HistoricalEvent.sources),
        )
        .filter(HistoricalEvent.id == event_id)
        .first()
    )
    if not event:
        raise EventNotFoundError(event_id)

    response.headers["Cache-Control"] = "public, max-age=3600"
    return _event_detail(event)


@router.get(
    "/v1/entities/{entity_id}/events",
    summary="Events linked to an entity",
    description=(
        "Returns all events in which the entity appears (any role). "
        "Useful to reconstruct an entity's event history: founding, "
        "conquests, dissolution, events suffered (colonial violence, epidemics)."
    ),
)
def get_events_for_entity(
    entity_id: int,
    response: Response,
    role: str | None = Query(None, description="Filter by role (e.g. MAIN_ACTOR, VICTIM)"),
    db: Session = Depends(get_db),
):
    entity = db.query(GeoEntity).filter(GeoEntity.id == entity_id).first()
    if not entity:
        raise EntityNotFoundError(entity_id)

    q = (
        db.query(HistoricalEvent)
        .join(EventEntityLink, EventEntityLink.event_id == HistoricalEvent.id)
        .filter(EventEntityLink.entity_id == entity_id)
    )
    if role is not None:
        q = q.filter(EventEntityLink.role == role)

    results = q.order_by(HistoricalEvent.year).all()

    # Annota con il ruolo specifico che l'entità ha in ciascun evento.
    links_by_event = {}
    for link in (
        db.query(EventEntityLink)
        .filter(EventEntityLink.entity_id == entity_id)
        .all()
    ):
        links_by_event.setdefault(link.event_id, []).append(link.role)

    response.headers["Cache-Control"] = "public, max-age=3600"

    payload = []
    for e in results:
        summary = _event_summary(e)
        summary["role_in_event"] = links_by_event.get(e.id, [])
        payload.append(summary)

    return {
        "entity_id": entity_id,
        "entity_name": entity.name_original,
        "total": len(payload),
        "events": payload,
    }
