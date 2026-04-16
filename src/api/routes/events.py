"""Endpoint per eventi storici — v6.3 + v6.14 date precision.

GET  /v1/events                          list + filter (year, event_type, status, known_silence, month, day)
GET  /v1/events/types                    enumera EventType
GET  /v1/events/map                      lightweight payload for map marker rendering
GET  /v1/events/on-this-day/{mm_dd}      eventi che cadono in un dato giorno/mese
GET  /v1/events/at-date/{date_str}       eventi in una data esatta (supporta BCE)
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
from src.cache import cache_response
from src.db.database import get_db
from src.db.enums import EventRole, EventType
from src.db.models import EventEntityLink, GeoEntity, HistoricalEvent

logger = logging.getLogger(__name__)

router = APIRouter(tags=["eventi"])


class EventNotFoundError(AtlasError):
    def __init__(self, event_id: int):
        super().__init__(404, f"Evento con id={event_id} non trovato", "NOT_FOUND")


def _event_summary(e: HistoricalEvent) -> dict:
    """Rappresentazione compatta di un evento (usata nelle liste).

    v6.14: include i campi di date precision (month, day, date_precision,
    iso_date) anche nel summary — consente al client di ordinare/filtrare
    senza fetch del detail.
    """
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
        "main_actor": e.main_actor,
        "status": e.status,
        "confidence_score": e.confidence_score,
        "known_silence": e.known_silence,
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
    summary="Lista eventi storici",
    description=(
        "Lista paginata di eventi storici con filtri su anno, tipo, stato e silenzi. "
        "ETHICS-007: nessun eufemismo nei termini EventType (GENOCIDE, COLONIAL_VIOLENCE, ...). "
        "ETHICS-008: `known_silence=true` restituisce solo eventi con documentazione "
        "contemporanea assente/cancellata."
    ),
)
@cache_response(ttl_seconds=300)
def list_events(
    request: Request,
    response: Response,
    year_min: int | None = Query(None, description="Anno minimo (incluso)"),
    year_max: int | None = Query(None, description="Anno massimo (incluso)"),
    event_type: str | None = Query(None, description="Filtra per EventType (es. BATTLE, GENOCIDE)"),
    status: str | None = Query(None, description="confirmed / uncertain / disputed"),
    known_silence: bool | None = Query(None, description="Solo eventi con silenzio documentato"),
    # v6.14: date precision filters.
    month: int | None = Query(None, ge=1, le=12, description="Filtra per mese (1-12)"),
    day: int | None = Query(None, ge=1, le=31, description="Filtra per giorno (1-31)"),
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
    summary="Enumera i tipi di evento",
    description=(
        "Restituisce i tipi di evento supportati (EventType enum) "
        "con breve descrizione dell'uso corretto. "
        "ETHICS-007: i termini sono espliciti — GENOCIDE, COLONIAL_VIOLENCE, "
        "ETHNIC_CLEANSING, MASSACRE, DEPORTATION — e non vanno sostituiti "
        "con eufemismi."
    ),
)
def list_event_types(response: Response):
    response.headers["Cache-Control"] = "public, max-age=86400"

    descriptions = {
        "BATTLE": "Scontro militare circoscritto nel tempo.",
        "SIEGE": "Assedio di una città o fortificazione.",
        "TREATY": "Accordo formale tra entità.",
        "REBELLION": "Insurrezione contro il potere costituito.",
        "REVOLUTION": "Cambio di regime su scala politica-sociale.",
        "CORONATION": "Ascesa al trono di un sovrano.",
        "DEATH_OF_RULER": "Morte di un sovrano (naturale o violenta).",
        "MARRIAGE_DYNASTIC": "Unione matrimoniale con impatto dinastico/territoriale.",
        "FOUNDING_CITY": "Fondazione di una città.",
        "FOUNDING_STATE": "Fondazione di un'entità geopolitica.",
        "DISSOLUTION_STATE": "Dissoluzione di un'entità geopolitica.",
        "CONQUEST": "Annessione territoriale militare.",
        "COLONIAL_VIOLENCE": "Violenza coloniale organizzata — NON 'pacification'.",
        "GENOCIDE": "Distruzione sistematica di un gruppo — NON 'massacre' né 'conflict'.",
        "ETHNIC_CLEANSING": "Rimozione etnica forzata — NON 'population exchange'.",
        "MASSACRE": "Uccisione di massa a scala sub-genocidale.",
        "DEPORTATION": "Trasferimento forzato di popolazione.",
        "MIGRATION": "Movimento di massa di popolazione (es. Bantu expansion, Slavic settlement).",
        "COLLAPSE": "Collasso statale/civile (distinto da dissoluzione deliberata).",
        "FAMINE": "Carestia strutturale — NON 'food crisis'.",
        "EPIDEMIC": "Epidemia o pandemia.",
        "EARTHQUAKE": "Terremoto documentato.",
        "VOLCANIC_ERUPTION": "Eruzione vulcanica.",
        "TSUNAMI": "Tsunami.",
        "FLOOD": "Inondazione maggiore.",
        "DROUGHT": "Siccità estesa.",
        "FIRE": "Incendio catastrofico.",
        "EXPLORATION": "Esplorazione geografica (framing attento, ETHICS-007).",
        "TRADE_AGREEMENT": "Accordo commerciale formale.",
        "RELIGIOUS_EVENT": "Conversione, scisma, proclamazione religiosa.",
        "INTELLECTUAL_EVENT": "Pubblicazione o cancellazione di opera fondamentale.",
        "TECHNOLOGICAL_EVENT": "Invenzione o adozione di tecnologia.",
        "OTHER": "Evento non classificabile nei tipi precedenti.",
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
    summary="Eventi per visualizzazione mappa",
    description=(
        "Payload leggero ottimizzato per il rendering di marker su mappa. "
        "Restituisce solo eventi con coordinate (lat/lon non null) entro "
        "una finestra temporale centrata su `year`. La finestra si auto-espande "
        "per epoche antiche: ±50 per anni < -1000, ±25 per anni da -1000 a 0."
    ),
)
def events_for_map(
    year: int = Query(..., description="Anno centrale della finestra temporale"),
    window: int = Query(10, ge=1, le=500, description="Semi-ampiezza finestra in anni (auto-espansa per epoche antiche)"),
    limit: int = Query(200, ge=1, le=500, description="Numero massimo di eventi"),
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
    summary="Eventi accaduti in un giorno dell'anno",
    description=(
        "Restituisce gli eventi storici con month/day corrispondenti, ordinati per anno. "
        "Formato path: MM-DD (es. 07-14 per il 14 luglio). "
        "Restituisce lista vuota (non 404) se nessun evento coincide."
    ),
)
def events_on_this_day(
    mm_dd: str = Path(..., description="Mese-giorno in formato MM-DD", pattern=r"^\d{2}-\d{2}$"),
    response: Response = None,
    db: Session = Depends(get_db),
):
    if not _MM_DD_RE.match(mm_dd):
        raise HTTPException(status_code=422, detail="Formato richiesto: MM-DD (es. 07-14)")

    parts = mm_dd.split("-")
    m, d = int(parts[0]), int(parts[1])

    if m < 1 or m > 12:
        raise HTTPException(status_code=422, detail=f"Mese non valido: {m} (1-12)")
    if d < 1 or d > 31:
        raise HTTPException(status_code=422, detail=f"Giorno non valido: {d} (1-31)")

    results = (
        db.query(HistoricalEvent)
        .filter(HistoricalEvent.month == m, HistoricalEvent.day == d)
        .order_by(HistoricalEvent.year)
        .all()
    )

    response.headers["Cache-Control"] = "public, max-age=3600"

    return {
        "month": m,
        "day": d,
        "total": len(results),
        "events": [_event_summary(e) for e in results],
    }


@router.get(
    "/v1/events/at-date/{date_str}",
    summary="Eventi in una data esatta",
    description=(
        "Restituisce gli eventi in una data esatta ISO-like. "
        "Formato: YYYY-MM-DD (es. 1789-07-14) o -YYYY-MM-DD per BCE "
        "(es. -0331-10-01 per il 1 ottobre 331 a.C.). "
        "Restituisce lista vuota (non 404) se nessun evento coincide."
    ),
)
def events_at_date(
    date_str: str = Path(..., description="Data in formato [-]YYYY-MM-DD"),
    response: Response = None,
    db: Session = Depends(get_db),
):
    if not _DATE_RE.match(date_str):
        raise HTTPException(
            status_code=422,
            detail="Formato richiesto: YYYY-MM-DD o -YYYY-MM-DD per BCE (es. -0331-10-01)",
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
        raise HTTPException(status_code=422, detail=f"Mese non valido: {m} (1-12)")
    if d < 1 or d > 31:
        raise HTTPException(status_code=422, detail=f"Giorno non valido: {d} (1-31)")

    results = (
        db.query(HistoricalEvent)
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
        "events": [_event_summary(e) for e in results],
    }


@router.get(
    "/v1/events/{event_id}",
    summary="Dettaglio evento storico",
    description=(
        "Dettaglio completo di un evento con entity_links (ruolo esplicito per "
        "ogni entità coinvolta) e sources. ETHICS-007: main_actor obbligatorio."
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
    summary="Eventi collegati a un'entità",
    description=(
        "Restituisce tutti gli eventi in cui l'entità compare (qualunque ruolo). "
        "Utile per ricostruire la storia eventuale di un'entità: fondazione, "
        "conquiste, dissoluzione, eventi subiti (violenze coloniali, epidemie)."
    ),
)
def get_events_for_entity(
    entity_id: int,
    response: Response,
    role: str | None = Query(None, description="Filtra per ruolo (es. MAIN_ACTOR, VICTIM)"),
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
