"""Boundary guards eseguiti al boot — facade unica.

v6.93.0 (audit R12): consolidamento dei boundary-fix script che girano
ad ogni startup del container. Prima del refactor `src/main.py::lifespan`
chiamava 2 funzioni separate da 2 moduli diversi, con error-handling
duplicato. Ora c'e' un unico entry point `run_boundary_guards_at_boot()`
che orchestra tutto con summary log finale.

Guards attivi al boot (in ordine):

1. `fix_displaced_aourednik` (ETHICS-006 follow-up)
   Cancella boundary aourednik con displacement >1500km dalla capitale
   (es. Pacific polity matchata fuzzy ad un poligono Indian Ocean).
   Idempotente — solo entita' con displacement effettivo vengono toccate.

2. `fix_antimeridian_and_wrong_polygons` (v6.31)
   - Reset wrong-country polygons (es. tribu' Native che ereditavano
     interi USA, USSR che ereditava Russia moderna).
   - Clip antimeridian-crossing polygons (bbox >360° → label rendering
     in luoghi assurdi).

I file legacy `fix_bad_boundaries_v671/v672/v673.py` NON vengono piu'
chiamati al boot — restano per uso CLI manuale / audit history. La
loro logica e' gia' stata applicata storicamente e i dati corretti
sono in seed.

ETHICS-006: questi guard sono "seconda linea di difesa" — il fix
principale e' nel matcher (`boundary_match.py`), questi prendono solo
quello che sfugge. Vedi `tests/test_ethics_006_audit.py` per la
guardia CI.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def sync_boundary_geom_from_geojson() -> int:
    """Backfill incrementale di `boundary_geom` da `boundary_geojson`.

    v6.94.0 (audit R1 / ADR-009): la colonna PostGIS `boundary_geom`
    deve restare sincrona con `boundary_geojson` quando l'ingestion
    pipeline aggiorna una boundary. Strategy: chiamato al boot,
    aggiorna righe con `boundary_geojson NOT NULL AND boundary_geom IS NULL`.

    Solo PostgreSQL — su SQLite e' un no-op (colonna non esiste).

    Idempotente: zero righe modificate se tutto sincrono. Sicuro
    chiamare ad ogni boot.

    Returns: numero di righe aggiornate.
    """
    from sqlalchemy import text

    from src.db.database import SessionLocal, is_postgres

    if not is_postgres:
        return 0

    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                UPDATE geo_entities
                SET boundary_geom = ST_Multi(
                    ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson))
                )
                WHERE boundary_geojson IS NOT NULL
                  AND boundary_geojson != ''
                  AND boundary_geom IS NULL
                  AND ST_IsValid(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)))
            """)
        )
        db.commit()
        return result.rowcount or 0
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def run_boundary_guards_at_boot() -> dict[str, Any]:
    """Esegui tutti i boundary guards in sequenza con summary unificato.

    Returns: dict con statistiche aggregate per logging:
        {
            "displaced_fixed": int,        # da fix_displaced_aourednik
            "wrong_polygon_fixed": int,    # da fix_antimeridian_and_wrong_polygons
            "antimeridian_clipped": int,   # da fix_antimeridian_and_wrong_polygons
            "geom_synced": int,            # da sync_boundary_geom_from_geojson (R1)
            "errors": list[str],           # eventuali messaggi di errore (no raise)
        }

    NON solleva eccezioni — ogni guard ha il proprio try/except interno
    e collega gli errori nel dict. Il lifespan continua con `pass` su
    errore — il servizio resta up anche con guard parziale.
    """
    stats: dict[str, Any] = {
        "displaced_fixed": 0,
        "wrong_polygon_fixed": 0,
        "antimeridian_clipped": 0,
        "geom_synced": 0,
        "errors": [],
    }

    # ── Guard 1: displaced aourednik (ETHICS-006) ──────────────────
    try:
        from src.ingestion.fix_displaced_aourednik import fix_displaced
        disp_result = fix_displaced(dry_run=False)
        stats["displaced_fixed"] = disp_result.get("fixed", 0)
    except Exception as exc:
        msg = f"fix_displaced_aourednik failed: {exc!r}"
        logger.warning(msg, exc_info=True)
        stats["errors"].append(msg)

    # ── Guard 2: antimeridian + wrong-country polygons (v6.31) ─────
    try:
        from src.ingestion.fix_antimeridian_and_wrong_polygons import fix_all
        am_result = fix_all(dry_run=False)
        stats["wrong_polygon_fixed"] = am_result.get("wrong_polygon_fixed", 0)
        stats["antimeridian_clipped"] = am_result.get("antimeridian_clipped", 0)
    except Exception as exc:
        msg = f"fix_antimeridian_and_wrong_polygons failed: {exc!r}"
        logger.warning(msg, exc_info=True)
        stats["errors"].append(msg)

    # ── Guard 3: sync boundary_geom from boundary_geojson (R1) ─────
    # IMPORTANTE: deve girare DOPO i guard 1-2 perche' quelli possono
    # modificare boundary_geojson (rollback a circle, antimeridian clip).
    # Il sync ripopola boundary_geom solo dove e' NULL.
    try:
        synced = sync_boundary_geom_from_geojson()
        stats["geom_synced"] = synced
    except Exception as exc:
        msg = f"sync_boundary_geom_from_geojson failed: {exc!r}"
        logger.warning(msg, exc_info=True)
        stats["errors"].append(msg)

    # ── Summary log unificato ─────────────────────────────────────
    total_fixed = (
        stats["displaced_fixed"]
        + stats["wrong_polygon_fixed"]
        + stats["antimeridian_clipped"]
    )
    if total_fixed > 0 or stats["geom_synced"] > 0:
        logger.warning(
            "Boundary guards al boot: %d displaced rollback + %d wrong-polygon reset + "
            "%d antimeridian clipped + %d geom synced",
            stats["displaced_fixed"],
            stats["wrong_polygon_fixed"],
            stats["antimeridian_clipped"],
            stats["geom_synced"],
        )
    elif stats["errors"]:
        logger.warning("Boundary guards al boot: %d errori, vedi log", len(stats["errors"]))
    else:
        logger.debug("Boundary guards al boot: nessuna correzione necessaria (dataset pulito)")

    return stats
