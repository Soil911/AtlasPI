"""Seed database per AtlasPI — caricamento entita' da JSON.

ETHICS: ogni entita' dimostra i principi etici del progetto.
I nomi originali hanno priorita' (ETHICS-001).
Le conquiste sono documentate esplicitamente (ETHICS-002).
I territori contestati mostrano tutte le versioni (ETHICS-003).

Le entita' sono caricate da file JSON in data/entities/*.json.
"""

import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from src.db.database import SessionLocal
from src.db.models import (
    EventEntityLink,
    EventSource,
    GeoEntity,
    HistoricalEvent,
    HistoricalPeriod,
    NameVariant,
    Source,
    TerritoryChange,
)

logger = logging.getLogger(__name__)

ENTITIES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "entities"
# v6.3: separate directory for historical events — ETHICS-007 + ETHICS-008.
EVENTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "events"
# v6.27: structured historical periods/epochs.
PERIODS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "periods"


def load_all_entities() -> list[dict]:
    """Carica tutte le entita' dai file JSON in data/entities/."""
    all_entities: list[dict] = []
    if not ENTITIES_DIR.exists():
        logger.warning("Directory entita' non trovata: %s", ENTITIES_DIR)
        return all_entities

    json_files = sorted(ENTITIES_DIR.glob("*.json"))
    for json_file in json_files:
        try:
            with open(json_file, encoding="utf-8") as f:
                entities = json.load(f)
            if isinstance(entities, list):
                all_entities.extend(entities)
                logger.info("Caricato %s: %d entita'", json_file.name, len(entities))
            else:
                logger.warning("File %s non contiene una lista", json_file.name)
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Errore caricamento %s: %s", json_file.name, e)

    # Deduplicazione per name_original — l'ultima occorrenza vince.
    # I file sono caricati in ordine alfabetico (batch_00, batch_01, ...),
    # quindi un batch successivo puo' sovrascrivere un'entita' precedente.
    # Questo consente batch correttivi (es. batch_32_confidence_boost).
    seen: dict[str, int] = {}
    unique: list[dict] = []
    for ent in all_entities:
        name = ent.get("name_original", "")
        if name in seen:
            idx = seen[name]
            logger.info("Entita' '%s' sovrascritta da batch successivo", name)
            unique[idx] = ent
        else:
            seen[name] = len(unique)
            unique.append(ent)

    return unique


def seed_database():
    """Popola il database con le entita' da JSON se e' vuoto."""
    db: Session = SessionLocal()
    try:
        count = db.query(GeoEntity).count()
        if count > 0:
            logger.info("Database gia' popolato (%d entita'). Skip seed.", count)
            return

        all_entities = load_all_entities()
        if not all_entities:
            logger.warning("Nessuna entita' trovata nei file JSON.")
            return

        logger.info("Seeding database con %d entita'...", len(all_entities))

        for data in all_entities:
            entity = GeoEntity(
                name_original=data["name_original"],
                name_original_lang=data["name_original_lang"],
                entity_type=data["entity_type"],
                year_start=data["year_start"],
                year_end=data.get("year_end"),
                capital_name=data.get("capital_name"),
                capital_lat=data.get("capital_lat"),
                capital_lon=data.get("capital_lon"),
                boundary_geojson=json.dumps(data["boundary_geojson"]) if data.get("boundary_geojson") else None,
                # ETHICS-005: boundary provenance tracking.
                boundary_source=data.get("boundary_source"),
                boundary_aourednik_name=data.get("boundary_aourednik_name"),
                boundary_aourednik_year=data.get("boundary_aourednik_year"),
                boundary_aourednik_precision=data.get("boundary_aourednik_precision"),
                boundary_ne_iso_a3=data.get("boundary_ne_iso_a3"),
                confidence_score=data.get("confidence_score", 0.5),
                status=data.get("status", "confirmed"),
                ethical_notes=data.get("ethical_notes"),
            )

            for nv in data.get("name_variants", []):
                entity.name_variants.append(NameVariant(**nv))

            for tc in data.get("territory_changes", []):
                # ETHICS: population_affected deve essere un intero nel DB.
                # Stringhe descrittive vengono convertite a None per evitare
                # perdita di contesto numerico. Il campo description mantiene
                # il contesto narrativo completo.
                tc_data = dict(tc)
                pa = tc_data.get("population_affected")
                if pa is not None and not isinstance(pa, int):
                    try:
                        tc_data["population_affected"] = int(pa)
                    except (ValueError, TypeError):
                        tc_data["population_affected"] = None
                entity.territory_changes.append(TerritoryChange(**tc_data))

            for src in data.get("sources", []):
                entity.sources.append(Source(**src))

            db.add(entity)

        db.commit()
        logger.info("Seed completato: %d entita' inserite.", len(all_entities))

    except Exception:
        db.rollback()
        logger.error("Errore durante il seed", exc_info=True)
        raise
    finally:
        db.close()


# ─── v6.3: eventi storici ──────────────────────────────────────────────────


def load_all_events() -> list[dict]:
    """Carica tutti gli eventi storici dai file JSON in data/events/*.json.

    ETHICS-007: nessuna sostituzione di termini (GENOCIDE, COLONIAL_VIOLENCE,
    ETHNIC_CLEANSING, DEPORTATION, FAMINE restano quelli).
    ETHICS-008: campo `known_silence` propagato così com'è.
    """
    all_events: list[dict] = []
    if not EVENTS_DIR.exists():
        logger.info("Directory eventi non trovata (normale in dev): %s", EVENTS_DIR)
        return all_events

    json_files = sorted(EVENTS_DIR.glob("batch_*.json"))
    for json_file in json_files:
        try:
            with open(json_file, encoding="utf-8") as f:
                events = json.load(f)
            if isinstance(events, list):
                all_events.extend(events)
                logger.info("Caricato %s: %d eventi", json_file.name, len(events))
            else:
                logger.warning("File eventi %s non e' una lista", json_file.name)
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Errore caricamento %s: %s", json_file.name, e)

    # Dedup per (name_original, year): un evento stesso anno/nome è duplicato.
    seen = set()
    unique: list[dict] = []
    for ev in all_events:
        key = (ev.get("name_original", ""), ev.get("year"))
        if key not in seen:
            seen.add(key)
            unique.append(ev)
        else:
            logger.warning("Evento duplicato ignorato: %s (%s)", key[0], key[1])
    return unique


def seed_events_database():
    """Popola la tabella historical_events se è vuota.

    ETHICS-007: i link evento ↔ entità sono creati tramite name_original
    (ground truth), con ruolo esplicito nel payload JSON. Un evento che
    referenzia un'entità inesistente è loggato ma non blocca il seed.
    """
    db: Session = SessionLocal()
    try:
        count = db.query(HistoricalEvent).count()
        if count > 0:
            logger.info("Tabella eventi già popolata (%d eventi). Skip seed.", count)
            return

        all_events = load_all_events()
        if not all_events:
            logger.info("Nessun evento da seed.")
            return

        logger.info("Seeding eventi storici: %d da inserire...", len(all_events))

        # Costruiamo una mappa name_original → entity_id per i link.
        entity_map = {e.name_original: e.id for e in db.query(GeoEntity).all()}

        inserted = 0
        missing_refs: list[str] = []
        for ev_data in all_events:
            event = HistoricalEvent(
                name_original=ev_data["name_original"],
                name_original_lang=ev_data["name_original_lang"],
                event_type=ev_data["event_type"],
                year=ev_data["year"],
                year_end=ev_data.get("year_end"),
                # v6.14: date precision fields (optional in JSON).
                month=ev_data.get("month"),
                day=ev_data.get("day"),
                date_precision=ev_data.get("date_precision"),
                iso_date=ev_data.get("iso_date"),
                calendar_note=ev_data.get("calendar_note"),
                location_name=ev_data.get("location_name"),
                location_lat=ev_data.get("location_lat"),
                location_lon=ev_data.get("location_lon"),
                main_actor=ev_data.get("main_actor"),
                description=ev_data["description"],
                casualties_low=ev_data.get("casualties_low"),
                casualties_high=ev_data.get("casualties_high"),
                casualties_source=ev_data.get("casualties_source"),
                confidence_score=ev_data.get("confidence_score", 0.7),
                status=ev_data.get("status", "confirmed"),
                known_silence=ev_data.get("known_silence", False),
                silence_reason=ev_data.get("silence_reason"),
                ethical_notes=ev_data.get("ethical_notes"),
            )
            # Sorgenti
            for src in ev_data.get("sources", []):
                event.sources.append(EventSource(**src))
            # Link a entità (se esistono nel DB)
            for link in ev_data.get("entity_links", []):
                ent_name = link.get("entity_name_original")
                entity_id = entity_map.get(ent_name) if ent_name else None
                if entity_id is None:
                    # L'evento è valido anche se non tutti i link risolvono:
                    # un evento può coinvolgere entità non (ancora) seedate.
                    missing_refs.append(f"{ev_data['name_original']} → {ent_name}")
                    continue
                event.entity_links.append(
                    EventEntityLink(
                        entity_id=entity_id,
                        role=link.get("role", "AFFECTED"),
                        notes=link.get("notes"),
                    )
                )
            db.add(event)
            inserted += 1

        db.commit()
        logger.info(
            "Seed eventi completato: %d eventi inseriti; %d link a entità mancanti",
            inserted,
            len(missing_refs),
        )
        if missing_refs:
            # Log solo i primi 5 per non inondare.
            for ref in missing_refs[:5]:
                logger.debug("link evento→entita mancante: %s", ref)

    except Exception:
        db.rollback()
        logger.error("Errore durante il seed eventi", exc_info=True)
        raise
    finally:
        db.close()


def sync_new_events() -> dict:
    """Inserisci solo eventi nuovi (non già presenti nel DB).

    A differenza di seed_events_database() che opera solo su DB vuoto,
    questa funzione confronta gli eventi nei file JSON con quelli nel DB
    e inserisce solo quelli mancanti. Dedup basato su (name_original, year).

    Returns: {"inserted": N, "skipped": N, "errors": [...]}
    """
    db: Session = SessionLocal()
    result = {"inserted": 0, "skipped": 0, "errors": []}
    try:
        all_events = load_all_events()
        if not all_events:
            return result

        # Mappa entità per i link.
        entity_map = {e.name_original: e.id for e in db.query(GeoEntity).all()}

        # Indice degli eventi già presenti: (name_original, year).
        existing = set()
        for e in db.query(HistoricalEvent).all():
            existing.add((e.name_original, e.year))

        for ev_data in all_events:
            key = (ev_data.get("name_original", ""), ev_data.get("year"))
            if key in existing:
                result["skipped"] += 1
                continue

            try:
                event = HistoricalEvent(
                    name_original=ev_data["name_original"],
                    name_original_lang=ev_data["name_original_lang"],
                    event_type=ev_data["event_type"],
                    year=ev_data["year"],
                    year_end=ev_data.get("year_end"),
                    month=ev_data.get("month"),
                    day=ev_data.get("day"),
                    date_precision=ev_data.get("date_precision"),
                    iso_date=ev_data.get("iso_date"),
                    calendar_note=ev_data.get("calendar_note"),
                    location_name=ev_data.get("location_name"),
                    location_lat=ev_data.get("location_lat"),
                    location_lon=ev_data.get("location_lon"),
                    main_actor=ev_data.get("main_actor"),
                    description=ev_data["description"],
                    casualties_low=ev_data.get("casualties_low"),
                    casualties_high=ev_data.get("casualties_high"),
                    casualties_source=ev_data.get("casualties_source"),
                    confidence_score=ev_data.get("confidence_score", 0.7),
                    status=ev_data.get("status", "confirmed"),
                    known_silence=ev_data.get("known_silence", False),
                    silence_reason=ev_data.get("silence_reason"),
                    ethical_notes=ev_data.get("ethical_notes"),
                )
                for src in ev_data.get("sources", []):
                    event.sources.append(EventSource(**src))
                for link in ev_data.get("entity_links", []):
                    ent_name = link.get("entity_name_original")
                    entity_id = entity_map.get(ent_name) if ent_name else None
                    if entity_id:
                        event.entity_links.append(
                            EventEntityLink(
                                entity_id=entity_id,
                                role=link.get("role", "AFFECTED"),
                                notes=link.get("notes"),
                            )
                        )
                db.add(event)
                result["inserted"] += 1
            except Exception as exc:
                result["errors"].append(f"{ev_data.get('name_original', '?')}: {exc}")

        db.commit()
        logger.info(
            "Event sync: %d inserted, %d skipped, %d errors",
            result["inserted"],
            result["skipped"],
            len(result["errors"]),
        )
    except Exception:
        db.rollback()
        logger.error("Error during event sync", exc_info=True)
        raise
    finally:
        db.close()
    return result


# ─── v6.27: Historical Periods seed ──────────────────────────────────


def load_all_periods() -> list[dict]:
    """Load all historical periods from JSON files in data/periods/."""
    all_periods: list[dict] = []
    if not PERIODS_DIR.exists():
        logger.warning("Periods directory not found: %s", PERIODS_DIR)
        return all_periods

    for json_file in sorted(PERIODS_DIR.glob("*.json")):
        try:
            with open(json_file, encoding="utf-8") as f:
                periods = json.load(f)
            if isinstance(periods, list):
                all_periods.extend(periods)
                logger.info("Loaded %s: %d periods", json_file.name, len(periods))
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Error loading %s: %s", json_file.name, e)

    return all_periods


def seed_periods_database():
    """Populate historical_periods table if empty.

    ETHICS: periodizations are historiographic constructs. Each period
    declares its `region` scope and optionally a `historiographic_note`
    documenting scholarly debates.
    """
    db: Session = SessionLocal()
    try:
        count = db.query(HistoricalPeriod).count()
        if count > 0:
            logger.info("Periods table already populated (%d). Skip seed.", count)
            return

        all_periods = load_all_periods()
        if not all_periods:
            logger.info("No periods to seed.")
            return

        logger.info("Seeding historical periods: %d to insert...", len(all_periods))

        inserted = 0
        for p_data in all_periods:
            period = HistoricalPeriod(
                name=p_data["name"],
                name_lang=p_data.get("name_lang", "en"),
                slug=p_data["slug"],
                name_native=p_data.get("name_native"),
                name_native_lang=p_data.get("name_native_lang"),
                period_type=p_data.get("period_type", "period"),
                region=p_data.get("region", "global"),
                year_start=p_data["year_start"],
                year_end=p_data.get("year_end"),
                description=p_data["description"],
                historiographic_note=p_data.get("historiographic_note"),
                alternative_names=(
                    json.dumps(p_data["alternative_names"], ensure_ascii=False)
                    if p_data.get("alternative_names") else None
                ),
                confidence_score=p_data.get("confidence_score", 0.8),
                status=p_data.get("status", "confirmed"),
                sources=(
                    json.dumps(p_data["sources"], ensure_ascii=False)
                    if p_data.get("sources") else None
                ),
            )
            db.add(period)
            inserted += 1

        db.commit()
        logger.info("Period seed complete: %d periods inserted.", inserted)
    except Exception:
        db.rollback()
        logger.error("Error during period seed", exc_info=True)
        raise
    finally:
        db.close()
