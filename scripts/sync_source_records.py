"""Sync external_source_records dal JSON di 6 tabelle (ADR-010 / audit R8).

Popola la tabella `external_source_records` (mirror queryable) parsando
i campi JSON `sources` di:

- historical_cities         → parent_type='city'
- trade_routes              → parent_type='route'
- dynasty_chains            → parent_type='chain'
- archaeological_sites      → parent_type='site'
- historical_rulers         → parent_type='ruler'
- historical_languages      → parent_type='language'

Idempotente:
- UPSERT su (parent_type, parent_id, citation) — duplicati skippati.
- `--rebuild` cancella tutti i records di un parent_type prima di
  ri-inserire (utile dopo modifica massiva del dataset).

Uso:

    docker exec cra-atlaspi python -m scripts.sync_source_records
    docker exec cra-atlaspi python -m scripts.sync_source_records --only cities
    docker exec cra-atlaspi python -m scripts.sync_source_records --dry-run
    docker exec cra-atlaspi python -m scripts.sync_source_records --rebuild

ETHICS-005-analogy: source_type ammette oral_tradition + archaeological
come evidence di pari dignità ad academic (ETHICS-008).
ETHICS-001: la citation viene preservata nella forma originale dal JSON
(non normalizzata) — gestione di "Cambridge Histories" vs "The Cambridge
History" affidata a post-processing query LIKE.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import UTC, datetime

logger = logging.getLogger(__name__)


# Mapping parent_type → (model class, json field name)
PARENT_TYPE_MAP = {
    "city": ("HistoricalCity", "sources"),
    "route": ("TradeRoute", "sources"),
    "chain": ("DynastyChain", "sources"),
    "site": ("ArchaeologicalSite", "sources"),
    "ruler": ("HistoricalRuler", "sources"),
    "language": ("HistoricalLanguage", "sources"),
}


def _parse_sources_json(raw: str | None) -> list[dict]:
    """Parse JSON-blob sources field.

    Ritorna sempre una lista di dict con almeno `citation` key. Skip
    silenzioso su JSON malformato o entries senza citation.
    """
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []

    if not isinstance(data, list):
        return []

    parsed: list[dict] = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        citation = entry.get("citation", "").strip()
        if not citation:
            continue
        parsed.append({
            "citation": citation[:1000],  # cap at column max
            "url": (entry.get("url") or "").strip()[:2000] or None,
            "source_type": entry.get("source_type", "secondary"),
        })
    return parsed


def sync_parent_type(
    parent_type: str,
    *,
    rebuild: bool = False,
    dry_run: bool = False,
) -> int:
    """Sync external_source_records per un parent_type.

    Returns: numero di records inseriti.
    """
    if parent_type not in PARENT_TYPE_MAP:
        raise ValueError(f"parent_type '{parent_type}' non supportato")

    model_name, json_field = PARENT_TYPE_MAP[parent_type]

    from sqlalchemy import text

    from src.db import models
    from src.db.database import SessionLocal

    model_cls = getattr(models, model_name)

    db = SessionLocal()
    try:
        if rebuild and not dry_run:
            deleted = db.execute(
                text("DELETE FROM external_source_records WHERE parent_type = :pt"),
                {"pt": parent_type},
            ).rowcount or 0
            db.commit()
            logger.info("rebuild %s: %d records esistenti cancellati", parent_type, deleted)

        records = db.query(model_cls).all()
        total_parsed = 0
        total_inserted = 0
        skipped_dup = 0
        now_iso = datetime.now(UTC).isoformat()

        for record in records:
            raw = getattr(record, json_field, None)
            sources = _parse_sources_json(raw)
            if not sources:
                continue
            total_parsed += len(sources)

            for src in sources:
                if dry_run:
                    total_inserted += 1
                    continue

                # UPSERT via INSERT ... ON CONFLICT (Postgres) o INSERT OR IGNORE (SQLite).
                # Per portabilita', usiamo SELECT + INSERT idempotente.
                existing = db.execute(
                    text("""
                        SELECT id FROM external_source_records
                        WHERE parent_type = :pt AND parent_id = :pid AND citation = :cit
                    """),
                    {"pt": parent_type, "pid": record.id, "cit": src["citation"]},
                ).first()
                if existing:
                    skipped_dup += 1
                    continue

                db.execute(
                    text("""
                        INSERT INTO external_source_records
                            (parent_type, parent_id, citation, url, source_type, created_at)
                        VALUES (:pt, :pid, :cit, :url, :st, :ts)
                    """),
                    {
                        "pt": parent_type,
                        "pid": record.id,
                        "cit": src["citation"],
                        "url": src["url"],
                        "st": src["source_type"],
                        "ts": now_iso,
                    },
                )
                total_inserted += 1

        if not dry_run:
            db.commit()

        logger.info(
            "%s%s: %d records parsed, %d inserted, %d skipped (already present)",
            "[DRY-RUN] " if dry_run else "",
            parent_type,
            total_parsed,
            total_inserted,
            skipped_dup,
        )
        return total_inserted
    finally:
        db.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sync external_source_records dal JSON-blob sources (ADR-010)"
    )
    parser.add_argument(
        "--only",
        choices=list(PARENT_TYPE_MAP.keys()),
        default=None,
        help="Esegui solo per il parent_type specificato.",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Cancella records esistenti per ogni parent_type prima del re-insert.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Conta inserts senza scrivere al DB.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    parent_types = [args.only] if args.only else list(PARENT_TYPE_MAP.keys())

    start = time.perf_counter()
    total_inserted = 0
    for pt in parent_types:
        try:
            inserted = sync_parent_type(pt, rebuild=args.rebuild, dry_run=args.dry_run)
            total_inserted += inserted
        except Exception:
            logger.exception("Sync %s failed", pt)
            return 1

    elapsed = time.perf_counter() - start
    print(
        f"deleted+inserted_total={total_inserted} types={len(parent_types)} "
        f"elapsed={elapsed:.2f}s dry_run={args.dry_run} rebuild={args.rebuild}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
