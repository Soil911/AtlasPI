"""AI Co-Founder Analysis Agent — v6.16.

Analyses the AtlasPI database for coverage gaps, quality issues, and
actionable suggestions. Inserts results into the ai_suggestions table.

SMART noise reduction: if everything is fine, this script says "all good"
and creates NO suggestions. Only genuinely actionable items are flagged.

Usage:
    python -m scripts.ai_cofounder_analyze

ETHICS: suggestions about adding entities or events must NOT bias the
dataset toward any particular cultural perspective. Geographic and
temporal gaps are identified by comparing coverage across ALL regions
and eras equally.
"""

from __future__ import annotations

import json
import logging
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ensure project root is on sys.path so `src.*` imports work.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from sqlalchemy import distinct, func, or_

from src.db.database import SessionLocal
from src.db.models import (
    AiSuggestion,
    ApiRequestLog,
    ChainLink,
    DynastyChain,
    GeoEntity,
    HistoricalEvent,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ─── Helper: continent from coordinates ──────────────────────────
def _lat_to_continent(lat: float | None, lon: float | None) -> str:
    if lat is None or lon is None:
        return "Unknown"
    if lat > 35 and lon > -30 and lon < 60:
        return "Europe"
    if lon >= 100 and lon < 180:
        return "Asia (East/Southeast)"
    if lat > 12 and lon >= 60 and lon < 100:
        return "Asia (Central/South)"
    if lat <= 12 and lon >= 60 and lon < 100:
        return "Asia (Central/South)"
    if lat < 35 and lon >= -20 and lon < 55:
        return "Africa / Middle East"
    if lat > 15 and lon >= -170 and lon < -30:
        return "Americas (North)"
    if lat <= 15 and lon >= -170 and lon < -30:
        return "Americas (South/Central)"
    if lat < -10 and lon >= 100:
        return "Oceania"
    if lon >= 25 and lon < 60 and lat > 10 and lat <= 45:
        return "Africa / Middle East"
    return "Other"


def _year_to_era(year: int) -> str:
    if year < -3000:
        return "Pre-3000 BCE"
    if year < -1000:
        return "3000-1000 BCE"
    if year < -500:
        return "1000-500 BCE"
    if year < 0:
        return "500-1 BCE"
    if year < 500:
        return "1-500 CE"
    if year < 1000:
        return "500-1000 CE"
    if year < 1500:
        return "1000-1500 CE"
    if year < 1800:
        return "1500-1800 CE"
    if year < 1900:
        return "1800-1900 CE"
    if year < 2000:
        return "1900-2000 CE"
    return "2000-present"


_ERA_ORDER = [
    "Pre-3000 BCE", "3000-1000 BCE", "1000-500 BCE", "500-1 BCE",
    "1-500 CE", "500-1000 CE", "1000-1500 CE", "1500-1800 CE",
    "1800-1900 CE", "1900-2000 CE", "2000-present",
]


def _existing_pending_titles(db) -> set[str]:
    """Get titles of suggestions that are already pending or accepted (dedup)."""
    rows = (
        db.query(AiSuggestion.title)
        .filter(AiSuggestion.status.in_(["pending", "accepted"]))
        .all()
    )
    return {r[0] for r in rows}


def _add_suggestion(
    db,
    existing_titles: set[str],
    category: str,
    title: str,
    description: str,
    priority: int = 3,
    detail_json: str | None = None,
) -> bool:
    """Insert a suggestion if it doesn't already exist in pending/accepted state."""
    if title in existing_titles:
        return False

    db.add(AiSuggestion(
        category=category,
        title=title,
        description=description,
        detail_json=detail_json,
        priority=priority,
        status="pending",
        source="auto",
        created_at=datetime.now(timezone.utc).isoformat(),
    ))
    existing_titles.add(title)
    return True


# ═══════════════════════════════════════════════════════════════════
# Analysis functions
# ═══════════════════════════════════════════════════════════════════


def analyze_geographic_gaps(db, existing_titles: set[str]) -> int:
    """Flag regions with significantly fewer entities than average."""
    entities = db.query(GeoEntity.capital_lat, GeoEntity.capital_lon).all()
    region_counts: dict[str, int] = Counter()
    for e in entities:
        region_counts[_lat_to_continent(e.capital_lat, e.capital_lon)] += 1

    avg = sum(region_counts.values()) / max(len(region_counts), 1)
    count = 0

    for region, n in sorted(region_counts.items(), key=lambda x: x[1]):
        # Only flag if significantly below average (< 40% of avg) and
        # has fewer than 20 entities — don't create noise for "Other" etc.
        if n < avg * 0.4 and region not in ("Unknown", "Other") and n < 50:
            priority = 2 if n < 10 else 3
            added = _add_suggestion(
                db, existing_titles,
                category="geographic_gap",
                title=f"Geographic gap: {region} ({n} entities)",
                description=f"The region '{region}' has only {n} entities, while the average across regions is {avg:.0f}. Consider adding more historical entities from this area to improve coverage balance.",
                priority=priority,
                detail_json=json.dumps({"region": region, "count": n, "average": round(avg)}),
            )
            if added:
                count += 1

    return count


def analyze_temporal_gaps(db, existing_titles: set[str]) -> int:
    """Flag eras with zero or very few events/entities."""
    event_years = db.query(HistoricalEvent.year).all()
    era_events: dict[str, int] = Counter()
    for (y,) in event_years:
        era_events[_year_to_era(y)] += 1

    entity_years = db.query(GeoEntity.year_start).all()
    era_entities: dict[str, int] = Counter()
    for (y,) in entity_years:
        era_entities[_year_to_era(y)] += 1

    avg_events = sum(era_events.values()) / max(len(_ERA_ORDER), 1)
    count = 0

    for era in _ERA_ORDER:
        ev = era_events.get(era, 0)
        en = era_entities.get(era, 0)
        # Only flag truly empty eras or those with very few events (< 30% avg)
        if ev == 0 and en > 0:
            added = _add_suggestion(
                db, existing_titles,
                category="temporal_gap",
                title=f"Zero events in era: {era}",
                description=f"There are {en} entities starting in {era} but zero events. Adding key events from this period would improve temporal coverage.",
                priority=2,
                detail_json=json.dumps({"era": era, "events": ev, "entities": en}),
            )
            if added:
                count += 1
        elif ev < avg_events * 0.3 and ev < 10 and en > 5:
            added = _add_suggestion(
                db, existing_titles,
                category="temporal_gap",
                title=f"Sparse events in era: {era} ({ev} events)",
                description=f"The era '{era}' has only {ev} events (avg is {avg_events:.0f}). Consider adding key historical events from this period.",
                priority=3,
                detail_json=json.dumps({"era": era, "events": ev, "entities": en, "average": round(avg_events)}),
            )
            if added:
                count += 1

    return count


def analyze_low_confidence(db, existing_titles: set[str]) -> int:
    """Flag entities and events with very low confidence scores."""
    low_entities = (
        db.query(GeoEntity.id, GeoEntity.name_original, GeoEntity.confidence_score)
        .filter(GeoEntity.confidence_score < 0.4)
        .order_by(GeoEntity.confidence_score)
        .limit(10)
        .all()
    )

    count = 0
    if len(low_entities) >= 3:
        names = [f"{e.name_original} ({e.confidence_score:.1f})" for e in low_entities[:5]]
        added = _add_suggestion(
            db, existing_titles,
            category="low_confidence",
            title=f"{len(low_entities)} entities with confidence < 0.4",
            description=f"These entities have low confidence scores and may benefit from additional source verification: {', '.join(names)}.",
            priority=4,
            detail_json=json.dumps([
                {"id": e.id, "name": e.name_original, "score": e.confidence_score}
                for e in low_entities
            ]),
        )
        if added:
            count += 1

    low_events = (
        db.query(HistoricalEvent.id, HistoricalEvent.name_original, HistoricalEvent.confidence_score)
        .filter(HistoricalEvent.confidence_score < 0.4)
        .order_by(HistoricalEvent.confidence_score)
        .limit(10)
        .all()
    )

    if len(low_events) >= 3:
        names = [f"{e.name_original} ({e.confidence_score:.1f})" for e in low_events[:5]]
        added = _add_suggestion(
            db, existing_titles,
            category="low_confidence",
            title=f"{len(low_events)} events with confidence < 0.4",
            description=f"These events have low confidence scores: {', '.join(names)}. Consider adding more sources.",
            priority=4,
            detail_json=json.dumps([
                {"id": e.id, "name": e.name_original, "score": e.confidence_score}
                for e in low_events
            ]),
        )
        if added:
            count += 1

    return count


def analyze_missing_boundaries(db, existing_titles: set[str]) -> int:
    """Flag entities that have no boundary GeoJSON."""
    no_boundary = (
        db.query(GeoEntity.id, GeoEntity.name_original, GeoEntity.entity_type)
        .filter(or_(
            GeoEntity.boundary_geojson.is_(None),
            GeoEntity.boundary_geojson == "",
        ))
        .all()
    )

    if len(no_boundary) == 0:
        return 0

    # Don't flag if there are very few (< 3) — noise threshold
    if len(no_boundary) < 3:
        return 0

    names = [e.name_original for e in no_boundary[:5]]
    more = f" and {len(no_boundary) - 5} more" if len(no_boundary) > 5 else ""
    added = _add_suggestion(
        db, existing_titles,
        category="quality",
        title=f"{len(no_boundary)} entities without boundaries",
        description=f"These entities lack boundary GeoJSON data: {', '.join(names)}{more}. Adding boundaries would improve map visualization and spatial queries.",
        priority=3,
        detail_json=json.dumps([
            {"id": e.id, "name": e.name_original, "type": e.entity_type}
            for e in no_boundary[:20]
        ]),
    )
    return 1 if added else 0


def analyze_orphan_entities(db, existing_titles: set[str]) -> int:
    """Flag entities not linked to any dynasty/succession chain."""
    entity_ids_in_chains = set(
        r[0] for r in db.query(distinct(ChainLink.entity_id)).all()
    )
    total = db.query(func.count(GeoEntity.id)).scalar() or 0

    if total == 0:
        return 0

    orphan_count = total - len(entity_ids_in_chains)
    pct = (orphan_count / total) * 100

    # Only flag if orphan percentage is high AND more than 50% orphans
    # (chain coverage is naturally low in early development)
    if pct < 85:
        return 0

    added = _add_suggestion(
        db, existing_titles,
        category="missing_chain",
        title=f"{orphan_count} entities not in any chain ({pct:.0f}%)",
        description=f"Out of {total} entities, {orphan_count} ({pct:.0f}%) are not linked to any dynasty/succession chain. Adding more chains would improve historical continuity and discoverability.",
        priority=5,
        detail_json=json.dumps({"orphan_count": orphan_count, "total": total, "percentage": round(pct, 1)}),
    )
    return 1 if added else 0


def analyze_failed_searches(db, existing_titles: set[str]) -> int:
    """Look for patterns in failed/empty API searches that signal demand."""
    month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

    # Check if we have any request logs at all
    log_count = (
        db.query(func.count(ApiRequestLog.id))
        .filter(ApiRequestLog.timestamp >= month_ago)
        .scalar() or 0
    )
    if log_count < 10:
        return 0

    # Look for 404s on entity-related paths
    not_found_rows = (
        db.query(
            ApiRequestLog.path,
            func.count(ApiRequestLog.id).label("times"),
        )
        .filter(
            ApiRequestLog.timestamp >= month_ago,
            ApiRequestLog.status_code == 404,
            ApiRequestLog.path.like("/v1/%"),
        )
        .group_by(ApiRequestLog.path)
        .order_by(func.count(ApiRequestLog.id).desc())
        .limit(10)
        .all()
    )

    count = 0
    for r in not_found_rows:
        if r.times >= 3:  # Only if queried multiple times
            added = _add_suggestion(
                db, existing_titles,
                category="traffic_pattern",
                title=f"Repeated 404: {r.path} ({r.times}x)",
                description=f"The path '{r.path}' returned 404 {r.times} times in the last 30 days. This may indicate user demand for data we don't have.",
                priority=3,
                detail_json=json.dumps({"path": r.path, "times": r.times}),
            )
            if added:
                count += 1

    return count


# ═══════════════════════════════════════════════════════════════════
# Main runner
# ═══════════════════════════════════════════════════════════════════


def run_analysis(db=None) -> dict:
    """Run all analysis functions and return summary.

    Accepts an optional db session for testing; creates its own if None.
    """
    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        existing = _existing_pending_titles(db)

        results = {
            "geographic_gaps": analyze_geographic_gaps(db, existing),
            "temporal_gaps": analyze_temporal_gaps(db, existing),
            "low_confidence": analyze_low_confidence(db, existing),
            "missing_boundaries": analyze_missing_boundaries(db, existing),
            "orphan_entities": analyze_orphan_entities(db, existing),
            "failed_searches": analyze_failed_searches(db, existing),
        }

        db.commit()

        total_new = sum(results.values())
        results["total_new_suggestions"] = total_new

        return results
    except Exception:
        db.rollback()
        raise
    finally:
        if own_session:
            db.close()


def main():
    """CLI entry point."""
    logger.info("AtlasPI AI Co-Founder Analysis starting...")

    results = run_analysis()

    total = results["total_new_suggestions"]
    if total == 0:
        logger.info("All good! No new suggestions generated.")
    else:
        logger.info("Generated %d new suggestions:", total)
        for k, v in results.items():
            if k != "total_new_suggestions" and v > 0:
                logger.info("  %s: %d", k, v)

    logger.info("Analysis complete.")
    return results


if __name__ == "__main__":
    main()
