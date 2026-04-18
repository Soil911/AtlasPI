"""v6.57: fix status coherence — entities/events con confidence < 0.5
e status='confirmed' dovrebbero essere 'uncertain'.

Audit report: research_output/audit/01_data_quality_ethics.md ha
identificato 55 entities + 2 events con questo pattern.

Usage:
    python -m scripts.fix_status_coherence --dry-run
    python -m scripts.fix_status_coherence
"""

from __future__ import annotations

import argparse
import datetime
import io
import logging
import sys


def _apply_windows_stdout_fix():
    if sys.platform == "win32" and isinstance(sys.stdout, io.TextIOWrapper):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        except AttributeError:
            pass


from src.db.database import SessionLocal
from src.db.models import GeoEntity, HistoricalEvent

logger = logging.getLogger(__name__)


def fix_status_coherence(dry_run: bool = False) -> dict:
    """Update status to 'uncertain' for records with confidence < 0.5 but
    currently status='confirmed'."""
    db = SessionLocal()
    stats = {"entities_fixed": 0, "events_fixed": 0}
    try:
        # Entities
        ent_q = db.query(GeoEntity).filter(
            GeoEntity.confidence_score < 0.5,
            GeoEntity.status == "confirmed",
        )
        entities_to_fix = ent_q.all()
        stats["entities_fixed"] = len(entities_to_fix)
        for e in entities_to_fix:
            logger.info(
                "entity/%d %r conf=%.2f confirmed → uncertain",
                e.id, e.name_original[:50], e.confidence_score,
            )
            if not dry_run:
                e.status = "uncertain"

        # Events
        evt_q = db.query(HistoricalEvent).filter(
            HistoricalEvent.confidence_score < 0.5,
            HistoricalEvent.status == "confirmed",
        )
        events_to_fix = evt_q.all()
        stats["events_fixed"] = len(events_to_fix)
        for ev in events_to_fix:
            logger.info(
                "event/%d %r conf=%.2f confirmed → uncertain",
                ev.id, ev.name_original[:50], ev.confidence_score,
            )
            if not dry_run:
                ev.status = "uncertain"

        if not dry_run:
            db.commit()
            # Audit log append
            from pathlib import Path
            audit = Path(__file__).resolve().parent.parent / "data_patch_audit.log"
            with audit.open("a", encoding="utf-8") as f:
                now = datetime.datetime.now(datetime.timezone.utc).isoformat()
                f.write(
                    f"{now} | bulk-status-coherence | "
                    f"entities_fixed={stats['entities_fixed']}, "
                    f"events_fixed={stats['events_fixed']} | "
                    f"applied_by: cli\n"
                )

        return stats
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    _apply_windows_stdout_fix()
    parser = argparse.ArgumentParser(description="Fix status coherence for low-confidence records")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    stats = fix_status_coherence(dry_run=args.dry_run)
    print("\n=== Status coherence fix ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    if args.dry_run:
        print("(DRY RUN — no writes)")


if __name__ == "__main__":
    main()
