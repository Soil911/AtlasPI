"""Pipeline di importazione dati.

Questo modulo gestisce l'importazione di dati da fonti esterne
e la loro normalizzazione nel formato AtlasPI.

ETHICS: ogni dato importato deve mantenere la tracciabilità
della fonte originale. Non importare dati senza source[].
"""

import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from src.db.models import GeoEntity, NameVariant, Source, TerritoryChange
from src.validation.confidence import validate_confidence

logger = logging.getLogger(__name__)


def import_entity_from_dict(data: dict, db: Session) -> GeoEntity:
    """Importa una singola entità da un dizionario normalizzato.

    ETHICS: rifiuta entità senza fonti documentate.
    """
    if not data.get("sources"):
        raise ValueError(
            f"Entità '{data.get('name_original', '?')}' rifiutata: nessuna fonte. "
            "Ogni dato deve essere tracciabile (CLAUDE.md, principio 3)."
        )

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
        confidence_score=validate_confidence(data.get("confidence_score", 0.5)),
        status=data.get("status", "confirmed"),
        ethical_notes=data.get("ethical_notes"),
    )

    for nv in data.get("name_variants", []):
        entity.name_variants.append(NameVariant(**nv))

    for tc in data.get("territory_changes", []):
        # ETHICS: ogni cambio territoriale deve avere change_type (ETHICS-002)
        if not tc.get("change_type"):
            logger.warning(
                "Cambio territoriale senza change_type per '%s', anno %s. "
                "Impostato a UNKNOWN — da verificare.",
                data["name_original"],
                tc.get("year"),
            )
            tc["change_type"] = "UNKNOWN"
        tc["confidence_score"] = validate_confidence(tc.get("confidence_score", 0.5))
        entity.territory_changes.append(TerritoryChange(**tc))

    for src in data.get("sources", []):
        entity.sources.append(Source(**src))

    db.add(entity)
    return entity


def import_from_json_file(filepath: Path, db: Session) -> list[GeoEntity]:
    """Importa entità da un file JSON."""
    with open(filepath, encoding="utf-8") as f:
        records = json.load(f)

    entities = []
    for record in records:
        try:
            entity = import_entity_from_dict(record, db)
            entities.append(entity)
        except (ValueError, KeyError) as e:
            logger.error("Errore importando record: %s", e)

    db.commit()
    logger.info("Importate %d entità da %s", len(entities), filepath)
    return entities
