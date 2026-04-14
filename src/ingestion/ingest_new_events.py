"""Idempotent ingestion of new historical events from data/events/batch_*.json.

Purpose:
    Insert events from JSON files whose ``(name_original, year)`` tuple is
    NOT yet in the database, skipping any that already exist. Mirror of
    ``ingest_new_entities.py`` but for the v6.3 events layer.

    Unlike ``seed_events_database()`` (which skips entirely if the table is
    non-empty), this utility is safe to run on a populated production
    database to add new event batches without touching existing rows.

Usage:
    python -m src.ingestion.ingest_new_events

ETHICS considerations:
    * Existing rows are NEVER updated here. Use specific amendment scripts
      for event corrections — this tool only INSERTs missing events.
    * Same ETHICS-007/008 guarantees as seed_events_database():
      - event_type NOT softened (GENOCIDE, COLONIAL_VIOLENCE, etc.)
      - main_actor preserved as provided (explicit "chi ha fatto cosa")
      - known_silence + silence_reason preserved verbatim
      - entity_links resolved via name_original ground truth; missing refs
        are logged but never block the insert (an event may legitimately
        reference entities not yet in the DB).
"""

from __future__ import annotations

import io
import logging
import sys

# Windows cp1252 stdout fix for non-latin event names
if sys.platform == "win32" and isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except AttributeError:
        pass

from src.db.database import SessionLocal
from src.db.models import EventEntityLink, EventSource, GeoEntity, HistoricalEvent
from src.db.seed import load_all_events

logger = logging.getLogger(__name__)


def ingest_missing_events() -> dict:
    """Insert events whose (name_original, year) tuple is not in the DB yet.

    Returns:
        dict with keys {inserted, skipped_existing, total_in_json,
        unresolved_entity_links}.
    """
    db = SessionLocal()
    try:
        existing_keys = {
            (row.name_original, row.year)
            for row in db.query(HistoricalEvent.name_original, HistoricalEvent.year).all()
        }
        logger.info("Eventi esistenti in DB: %d", len(existing_keys))

        all_events = load_all_events()
        logger.info("Eventi nei JSON: %d", len(all_events))

        # Map name_original → entity_id per resolvere i link entity-side.
        entity_map = {e.name_original: e.id for e in db.query(GeoEntity).all()}

        inserted = 0
        skipped = 0
        missing_refs: list[str] = []

        for ev_data in all_events:
            name = ev_data.get("name_original", "")
            year = ev_data.get("year")
            if not name or year is None:
                continue
            if (name, year) in existing_keys:
                skipped += 1
                continue

            event = HistoricalEvent(
                name_original=ev_data["name_original"],
                name_original_lang=ev_data["name_original_lang"],
                event_type=ev_data["event_type"],
                year=ev_data["year"],
                year_end=ev_data.get("year_end"),
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
                if entity_id is None:
                    # ETHICS: un evento può legittimamente referenziare
                    # entità non (ancora) nel DB; log + skip del singolo link.
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
            "Ingest eventi completato: %d inseriti, %d già esistenti saltati, %d link non risolti.",
            inserted,
            skipped,
            len(missing_refs),
        )
        if missing_refs:
            for ref in missing_refs[:10]:
                logger.debug("link evento→entita mancante: %s", ref)

        return {
            "inserted": inserted,
            "skipped_existing": skipped,
            "total_in_json": len(all_events),
            "unresolved_entity_links": len(missing_refs),
        }

    except Exception:
        db.rollback()
        logger.error("Errore durante ingest eventi", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    stats = ingest_missing_events()
    print("\nIngest eventi stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
