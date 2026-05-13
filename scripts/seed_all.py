"""Orchestrator unico per il seed di AtlasPI — v6.95.0 (audit R3).

Esegue in sequenza tutti gli step di seed/ingestion che oggi girano
in `src/main.py::lifespan` quando `AUTO_SEED=true`. Lo scopo e' avere
un punto di esecuzione esplicito per:

- Re-seed dopo un wipe del DB (alembic downgrade -1 → upgrade head).
- Re-build boundary post-aggiornamento di data/raw/.
- Test in ambienti dove `AUTO_SEED=false` (config piu' sicura per prod
  post primo boot).

Uso:

    # Tutti gli step (entita' + eventi + periodi + siti + lingue + chains +
    # update boundaries con force=True)
    docker exec cra-atlaspi python -m scripts.seed_all

    # Solo seed entita' (skip update_all_boundaries lento)
    docker exec cra-atlaspi python -m scripts.seed_all --skip-boundaries

    # Solo update boundary (re-extract da Natural Earth/aourednik)
    docker exec cra-atlaspi python -m scripts.seed_all --only=boundaries

    # Sequenza piena con force re-extract di boundary
    docker exec cra-atlaspi python -m scripts.seed_all --force-boundaries

Idempotenza:
Tutti gli step interni sono idempotenti (skip-when-populated). Lo
script puo' essere lanciato n volte senza effetti collaterali.

Failure mode:
Ogni step e' in try/except. Un errore in un seed step viene loggato
ma non interrompe gli altri. Exit code 1 alla fine se almeno un step
ha fallito.

ETHICS: lo script non altera i dati esistenti, solo aggiunge mancanti.
Per modifica/cancellazione usa script SQL dedicati in scripts/.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time


def _step(name: str, fn, *args, **kwargs) -> bool:
    """Esegui uno step con timing + log + try/except. Ritorna True se ok."""
    log = logging.getLogger(__name__)
    log.info("=== Step: %s ===", name)
    start = time.perf_counter()
    try:
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start
        log.info("Step '%s' completato in %.2fs (result=%r)", name, elapsed, result)
        return True
    except Exception:
        elapsed = time.perf_counter() - start
        log.exception("Step '%s' fallito dopo %.2fs", name, elapsed)
        return False


def run_all(
    skip_boundaries: bool = False,
    only: str | None = None,
    force_boundaries: bool = False,
) -> int:
    """Esegui tutti gli step. Ritorna 0 se ok, 1 se almeno uno e' fallito."""
    from src.db.seed import (
        seed_database,
        seed_events_database,
        seed_periods_database,
        sync_new_periods,
    )
    from src.ingestion.boundary_guards import run_boundary_guards_at_boot
    from src.ingestion.ensure_aourednik_data import ensure_aourednik
    from src.ingestion.ingest_chains import ingest_chains
    from src.ingestion.ingest_languages import ingest_languages
    from src.ingestion.ingest_sites import ingest_sites
    from src.ingestion.update_boundaries import update_all_boundaries

    failures: list[str] = []

    def maybe_run(label: str, fn, *args, **kwargs) -> None:
        if only and only != label:
            return
        if only and only == "boundaries" and label != "boundaries":
            return
        ok = _step(label, fn, *args, **kwargs)
        if not ok:
            failures.append(label)

    # Ordine logico: prima entita' (chiave per tutto il resto), poi
    # le risorse che referenziano entita' (events/sites/languages/chains),
    # infine boundary che richiedono entita' presenti.
    maybe_run("ensure_aourednik_data", ensure_aourednik)
    maybe_run("seed_entities", seed_database)
    maybe_run("seed_events", seed_events_database)
    maybe_run("seed_periods", seed_periods_database)
    maybe_run("sync_periods", sync_new_periods)
    maybe_run("ingest_sites", ingest_sites)
    maybe_run("ingest_languages", ingest_languages)
    maybe_run("ingest_chains", ingest_chains)

    if not skip_boundaries:
        maybe_run("update_boundaries", update_all_boundaries, force=force_boundaries)

    # Boundary guards al boot (idempotenti) — sempre safe.
    maybe_run("boundary_guards", run_boundary_guards_at_boot)

    if failures:
        logging.getLogger(__name__).error(
            "Seed completato con %d errori: %s", len(failures), ", ".join(failures)
        )
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Orchestratore unico per il seed di AtlasPI (audit R3 v6.95.0)"
    )
    parser.add_argument(
        "--skip-boundaries",
        action="store_true",
        help="Salta update_all_boundaries (file I/O su Natural Earth/aourednik).",
    )
    parser.add_argument(
        "--force-boundaries",
        action="store_true",
        help="Forza re-extraction boundary (bypass skip-if-80%%-populated).",
    )
    parser.add_argument(
        "--only",
        choices=[
            "entities", "events", "periods", "sites", "languages",
            "chains", "boundaries", "guards",
        ],
        default=None,
        help="Esegui solo lo step specificato.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    return run_all(
        skip_boundaries=args.skip_boundaries,
        only=args.only,
        force_boundaries=args.force_boundaries,
    )


if __name__ == "__main__":
    sys.exit(main())
