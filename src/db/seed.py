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
from src.db.models import GeoEntity, NameVariant, Source, TerritoryChange

logger = logging.getLogger(__name__)

ENTITIES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "entities"


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

    # Deduplicazione per name_original
    seen = set()
    unique = []
    for ent in all_entities:
        name = ent.get("name_original", "")
        if name not in seen:
            seen.add(name)
            unique.append(ent)
        else:
            logger.warning("Entita' duplicata ignorata: %s", name)

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
