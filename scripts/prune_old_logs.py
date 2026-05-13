"""Retention policy per api_request_logs — v6.92.3 (audit R10).

Cancella record di `api_request_logs` piu' vecchi di N giorni
(default 90). La tabella ha gia' osservato 90k righe in 30 giorni
(CHANGELOG v6.32), quindi senza retention cresce a milioni nell'anno.

Uso standalone (dal container o cron host):

    docker exec cra-atlaspi python -m scripts.prune_old_logs --days 90 --dry-run
    docker exec cra-atlaspi python -m scripts.prune_old_logs --days 90

Anche chiamato idempotentemente al boot di src/main.py via Redis lock
24h. Vedi src.main.lifespan + src.maintenance.maybe_prune_old_logs.

Output: stampa numero di righe cancellate + timing su stdout. Exit 0
se OK, 1 se errore.

ETHICS / data retention:
- I log contengono solo richieste API (path, IP, user-agent, status,
  timing). NON dati personali in senso GDPR (no nomi, email, payload
  body), ma IP e' considerato PII in alcune giurisdizioni.
- 90 giorni e' uno standard ragionevole per analytics ops senza
  cumulare PII oltre il necessario.
- Per audit forense vero, le entries Sentry conservano gli errori
  comunque (sample 0.1 per traces).
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime, timedelta, timezone


def prune_old_logs(days: int = 90, dry_run: bool = False) -> int:
    """Cancella api_request_logs.timestamp < (now - days).

    Returns: numero di righe cancellate (0 se dry-run).
    Raises: qualunque errore DB risale al chiamante.

    Nota: timestamp e' String ISO 8601 (vedi src/db/models.py:ApiRequestLog).
    Confronto lessicografico = confronto cronologico per ISO 8601 UTC.
    """
    # Import locale per evitare overhead se il module viene importato
    # solo per type-hint o documentazione.
    from sqlalchemy import text

    from src.db.database import SessionLocal

    cutoff_dt = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_iso = cutoff_dt.isoformat()

    logger = logging.getLogger(__name__)

    start = time.perf_counter()
    db = SessionLocal()
    try:
        # Count prima per visibilita' (utile in dry-run + sanity check).
        n_to_delete = db.execute(
            text("SELECT COUNT(*) FROM api_request_logs WHERE timestamp < :cutoff"),
            {"cutoff": cutoff_iso},
        ).scalar() or 0

        if n_to_delete == 0:
            logger.info("Nessun log piu' vecchio di %d giorni — nulla da cancellare", days)
            return 0

        if dry_run:
            logger.info(
                "[DRY-RUN] Cancellerei %d righe di api_request_logs piu' vecchie di %s",
                n_to_delete, cutoff_iso,
            )
            return 0

        result = db.execute(
            text("DELETE FROM api_request_logs WHERE timestamp < :cutoff"),
            {"cutoff": cutoff_iso},
        )
        db.commit()
        elapsed_ms = (time.perf_counter() - start) * 1000
        deleted = result.rowcount or n_to_delete
        logger.info(
            "Pruned %d righe di api_request_logs piu' vecchie di %d giorni in %.0fms",
            deleted, days, elapsed_ms,
        )
        return deleted
    finally:
        db.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prune api_request_logs older than N days")
    parser.add_argument("--days", type=int, default=90,
                        help="Retention in giorni (default 90)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Conta cosa cancellerei senza eseguire DELETE")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    try:
        deleted = prune_old_logs(days=args.days, dry_run=args.dry_run)
    except Exception:
        logging.exception("Errore durante prune_old_logs")
        return 1

    print(f"deleted={deleted} days={args.days} dry_run={args.dry_run}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
