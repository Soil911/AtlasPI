"""Aggiorna i confini nel database con dati da fonti accademiche reali.

Questo script va eseguito dopo il seed iniziale per sostituire
i confini approssimativi con quelli estratti da dataset accademici.

Fonti utilizzate:
- aourednik/historical-basemaps (CC BY-SA 4.0)
- Natural Earth (pubblico dominio)
"""

import json
import logging

from sqlalchemy.orm import Session

from src.db.database import SessionLocal
from src.db.models import GeoEntity, Source
from src.ingestion.extract_boundaries import extract_all_boundaries

logger = logging.getLogger(__name__)


def update_all_boundaries():
    """Aggiorna i confini di tutte le entità mappate."""
    boundaries = extract_all_boundaries()
    if not boundaries:
        logger.warning("Nessun confine estratto.")
        return

    db: Session = SessionLocal()
    try:
        updated = 0
        for entity_name, data in boundaries.items():
            entity = db.query(GeoEntity).filter(
                GeoEntity.name_original == entity_name
            ).first()

            if not entity:
                logger.warning("Entità '%s' non trovata nel DB.", entity_name)
                continue

            # Aggiorna il confine
            entity.boundary_geojson = json.dumps(data["geojson"])

            # Aggiungi fonte del dataset se non presente
            source_citation = f"Confini: {data['source']}"
            existing = db.query(Source).filter(
                Source.entity_id == entity.id,
                Source.citation == source_citation,
            ).first()

            if not existing:
                db.add(Source(
                    entity_id=entity.id,
                    citation=source_citation,
                    source_type="academic",
                ))

            updated += 1
            logger.info("Aggiornato confine per: %s (precisione: %s)",
                        entity_name, data["precision"])

        db.commit()
        logger.info("Aggiornati %d confini su %d estratti.", updated, len(boundaries))

    except Exception:
        db.rollback()
        logger.exception("Errore durante l'aggiornamento dei confini")
        raise
    finally:
        db.close()
