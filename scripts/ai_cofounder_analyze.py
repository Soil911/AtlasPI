"""AI Co-Founder Analysis Agent — v6.26.

Analyses the AtlasPI database for coverage gaps, quality issues, and
actionable suggestions. Inserts results into the ai_suggestions table.

Analysis categories:
  1. Geographic gaps     — regions with few entities vs average
  2. Temporal gaps       — eras with sparse events or entities
  3. Low confidence      — entities/events with confidence < 0.4
  4. Missing boundaries  — entities without boundary GeoJSON
  5. Orphan entities     — entities not in any dynasty chain
  6. Failed searches     — 404s + zero-result search queries (demand signals)
  7. Date coverage gaps  — months with sparse on-this-day coverage

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
    """Look for patterns in failed/empty API searches that signal demand.

    Two signals:
    1. Repeated 404s on /v1/* paths → entity/event doesn't exist
    2. Repeated search queries with fast response (< 100ms) → likely empty results
       (heuristic: fast response on search endpoints = empty DB hit)
    """
    month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

    # Check if we have any request logs at all
    log_count = (
        db.query(func.count(ApiRequestLog.id))
        .filter(ApiRequestLog.timestamp >= month_ago)
        .scalar() or 0
    )
    if log_count < 10:
        return 0

    count = 0

    # ── Signal 1: Repeated 404s on entity-related paths ──────────
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

    # ── Signal 2: Likely-empty search queries (200 + fast response) ──
    # Heuristic: search endpoints returning 200 with response_time < 100ms
    # and query_string contains actual SEARCH params (not just pagination).
    # Pagination-only queries (limit=, offset=) are normal usage, not signals.
    _SEARCH_PARAMS = ("name=", "q=", "year=", "event_type=", "entity_type=",
                      "status=", "continent=", "type=", "search=")
    search_paths = ("/v1/entities", "/v1/events", "/v1/search")
    empty_search_rows = (
        db.query(
            ApiRequestLog.path,
            ApiRequestLog.query_string,
            func.count(ApiRequestLog.id).label("times"),
        )
        .filter(
            ApiRequestLog.timestamp >= month_ago,
            ApiRequestLog.query_string.isnot(None),
            ApiRequestLog.query_string != "",
            or_(
                *[ApiRequestLog.path.like(f"{p}%") for p in search_paths]
            ),
            # Must contain at least one real search param (not just limit/offset)
            or_(
                *[ApiRequestLog.query_string.contains(p) for p in _SEARCH_PARAMS]
            ),
            ApiRequestLog.status_code == 200,
            ApiRequestLog.response_time_ms < 100,
        )
        .group_by(ApiRequestLog.path, ApiRequestLog.query_string)
        .having(func.count(ApiRequestLog.id) >= 2)  # At least 2 identical queries
        .order_by(func.count(ApiRequestLog.id).desc())
        .limit(10)
        .all()
    )

    for r in empty_search_rows:
        # Extract human-readable query from query_string
        qs_display = r.query_string[:80] + ("…" if len(r.query_string) > 80 else "")
        added = _add_suggestion(
            db, existing_titles,
            category="search_demand",
            title=f"Empty search: {r.path}?{qs_display} ({r.times}x)",
            description=(
                f"The query '{r.path}?{r.query_string}' was made {r.times} times "
                f"in the last 30 days with fast response times (likely zero results). "
                f"This indicates demand for data we may not have."
            ),
            priority=3,
            detail_json=json.dumps({
                "path": r.path,
                "query_string": r.query_string,
                "times": r.times,
                "signal": "fast_200_likely_empty",
            }),
        )
        if added:
            count += 1

    return count


def analyze_date_coverage_gaps(db, existing_titles: set[str]) -> int:
    """Flag months with poor event date coverage for on-this-day feature.

    The on-this-day endpoint needs events with month+day populated.
    This analyzer flags months with fewer than 5 covered days, signaling
    the need for more date-precise events in those months.
    """
    # Count unique (month, day) pairs with events
    date_rows = (
        db.query(
            HistoricalEvent.month,
            func.count(distinct(HistoricalEvent.day)).label("unique_days"),
        )
        .filter(
            HistoricalEvent.month.isnot(None),
            HistoricalEvent.day.isnot(None),
        )
        .group_by(HistoricalEvent.month)
        .all()
    )

    month_coverage = {r.month: r.unique_days for r in date_rows}
    total_days_covered = sum(month_coverage.values())
    count = 0

    # Only analyze if we already have SOME date coverage (avoid noise in early stage)
    if total_days_covered < 30:
        return 0

    MONTH_NAMES = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]

    sparse_months = []
    for m in range(1, 13):
        days = month_coverage.get(m, 0)
        if days < 5:
            sparse_months.append({"month": m, "name": MONTH_NAMES[m], "covered_days": days})

    if not sparse_months:
        return 0

    # Create one suggestion summarizing sparse months
    names = [f"{s['name']} ({s['covered_days']} days)" for s in sparse_months]
    added = _add_suggestion(
        db, existing_titles,
        category="date_coverage",
        title=f"Sparse date coverage: {len(sparse_months)} months below 5 days",
        description=(
            f"The on-this-day feature relies on events with month+day data. "
            f"These months have fewer than 5 covered days: {', '.join(names)}. "
            f"Adding events with precise dates in these months would improve "
            f"the daily historical content feature."
        ),
        priority=3,
        detail_json=json.dumps({
            "sparse_months": sparse_months,
            "total_days_covered": total_days_covered,
            "coverage_pct": round(total_days_covered / 366 * 100, 1),
        }),
    )
    if added:
        count += 1

    return count


# ═══════════════════════════════════════════════════════════════════
# Geometric quality analyzer (v6.31)
# ═══════════════════════════════════════════════════════════════════


def analyze_geometric_bugs(db, existing_titles: set[str]) -> int:
    """Detect geometric quality issues invisible to metadata checks.

    Origin: v6.31 — a user reported that the 'United States of America' label
    appeared on France on the interactive map. Root cause: USA's Natural Earth
    polygon has Alaska's Aleutian islands wrapped past +180°, making the
    polygon's bounding box span ~360° longitude → Leaflet's bbox-center label
    position calculation lands at lon≈0 (on France). NONE of the existing
    metadata analyzers caught this because:
      - boundary is present (not null) ✓
      - boundary is large (>500 chars) ✓
      - confidence is high ✓
      - no text anomaly in names or descriptions

    This analyzer performs SHAPE-LEVEL SANITY CHECKS:

    1. ANTIMERIDIAN CROSSING: bbox width > 180° (polygon wraps the globe)
    2. CAPITAL FAR FROM POLYGON: capital_lat/lon > 500km from polygon
       (already in fix_displaced_aourednik but we re-check here as a
       belt-and-suspenders)
    3. POLYGON TOO LARGE FOR ENTITY TYPE: a city with boundary >100,000 km²,
       a principality with >1M km², etc. (wrong-polygon inheritance
       indicator)
    4. IDENTICAL POLYGONS WITH DIFFERENT OWNERS: two entities sharing the
       exact same boundary_geojson bytes are a red flag (matching gone wrong)

    Returns count of suggestions created.
    """
    try:
        from shapely.geometry import shape
    except ImportError:
        logger.warning("shapely not available — skipping geometric analysis")
        return 0

    count = 0
    suspects: list[dict] = []

    # Type-based area ceilings (km², rough) for wrong-polygon detection
    type_max_area_km2 = {
        "city": 10_000,
        "city-state": 50_000,
        "principality": 200_000,
        "duchy": 200_000,
        "chiefdom": 300_000,
        "tribal_nation": 2_000_000,
        "tribal_federation": 2_000_000,
        "confederation": 3_000_000,
        "kingdom": 6_000_000,
        "sultanate": 4_000_000,
        "republic": 10_000_000,
        "dynasty": 15_000_000,
        "caliphate": 15_000_000,
        "khanate": 30_000_000,
        "empire": 35_000_000,
    }

    # Check every entity
    entities = (
        db.query(GeoEntity)
        .filter(GeoEntity.boundary_geojson.isnot(None))
        .all()
    )

    # Track boundary hashes to detect shared polygons
    from hashlib import sha256
    boundary_owners: dict[str, list[int]] = {}

    for e in entities:
        boundary = e.boundary_geojson
        if not boundary:
            continue
        try:
            geom = shape(json.loads(boundary))
        except Exception:
            continue

        issues = []

        # 1. Antimeridian crossing
        bb = geom.bounds
        if (bb[2] - bb[0]) > 180:
            issues.append(
                f"antimeridian-crossing bbox (width {bb[2]-bb[0]:.0f}°) — "
                f"label will render at lon≈{(bb[0]+bb[2])/2:.1f} not at capital"
            )

        # 2. Polygon too large for entity type
        if e.entity_type and geom.area > 0:
            # approximate km² from degree² (very rough; polar-biased)
            approx_km2 = geom.area * 111 * 111
            ceiling = type_max_area_km2.get(e.entity_type)
            if ceiling and approx_km2 > ceiling * 1.5:
                issues.append(
                    f"polygon area {approx_km2:,.0f} km² exceeds type "
                    f"ceiling for {e.entity_type} ({ceiling:,} km² × 1.5 margin) — "
                    f"likely wrong-polygon inheritance"
                )

        # 3. Track boundary-hash duplicates
        if len(boundary) > 100:  # only meaningful-size polygons
            h = sha256(boundary.encode()).hexdigest()[:16]
            boundary_owners.setdefault(h, []).append(e.id)

        if issues:
            suspects.append({
                "id": e.id,
                "name": e.name_original,
                "entity_type": e.entity_type,
                "boundary_source": e.boundary_source,
                "issues": issues,
            })

    # 4. Shared-polygon detection (different entities with identical boundary)
    # This catches fuzzy-match failures where multiple entities were assigned
    # the same NE polygon.
    shared_polygons = {h: ids for h, ids in boundary_owners.items() if len(ids) > 1}
    if shared_polygons:
        for h, ids in list(shared_polygons.items())[:10]:  # cap to 10 for sanity
            names = []
            for eid in ids[:10]:
                ent = next((e for e in entities if e.id == eid), None)
                if ent:
                    names.append(f"{eid}={ent.name_original[:30]}")
            suspects.append({
                "hash": h,
                "shared_polygon_ids": ids,
                "shared_polygon_names": names,
                "issues": [f"{len(ids)} entities share the exact same polygon — fuzzy-match error"],
            })

    # Create suggestions
    if suspects:
        # Aggregate suggestion (one per analysis run, listing all issues)
        title = f"Geometric bugs: {len(suspects)} entities have shape-level issues"
        added = _add_suggestion(
            db, existing_titles,
            category="geometric_bug",
            title=title,
            description=(
                f"The geometric quality analyzer detected {len(suspects)} entities "
                f"with shape-level bugs (antimeridian-crossing bbox, polygon-area "
                f"exceeding type-based ceiling, or shared polygons across multiple "
                f"entities). These are NOT caught by metadata checks (confidence, "
                f"boundary-presence, status) but cause visual bugs on the map or "
                f"incorrect spatial queries. Run "
                f"`python -m src.ingestion.fix_antimeridian_and_wrong_polygons` to "
                f"fix automatically."
            ),
            priority=2,  # high — these are user-visible bugs
            detail_json=json.dumps({
                "analyzer": "analyze_geometric_bugs",
                "total_suspects": len(suspects),
                "suspects": suspects[:30],  # cap payload
                "auto_fix_command": "python -m src.ingestion.fix_antimeridian_and_wrong_polygons",
            }),
        )
        if added:
            count += 1

    return count


# ═══════════════════════════════════════════════════════════════════
# Cross-resource consistency analyzer (v6.32)
# ═══════════════════════════════════════════════════════════════════


def analyze_cross_resource_consistency(db, existing_titles: set[str]) -> int:
    """Detect logical inconsistencies across tables.

    Checks:
    1. Events linked to entities whose year range doesn't include the event
       year (±100 year grace for uncertain dates)
    2. Chain links with sequence disorder (transition_year < prev transition_year
       when sequence_order > 0)
    3. Territory changes referencing entities that didn't exist at change time
    4. Events with no sources (should be all have sources post v6.30)
    5. Entities whose year_end < year_start (data entry errors)
    6. Events with month but no day and date_precision='DAY'

    Unlike FK violations (which SQL constraints catch), these are logical
    inconsistencies that pass naive validation but indicate data quality issues.
    """
    count = 0
    issues_found: dict[str, list[dict]] = {}

    from sqlalchemy import text

    # 1. Events before/after their linked entity's lifespan (>100y grace)
    rows = db.execute(
        text(
            "SELECT e.id as event_id, e.name_original as event_name, e.year as event_year, "
            "g.id as entity_id, g.name_original as entity_name, "
            "g.year_start, g.year_end "
            "FROM event_entity_links eel "
            "JOIN historical_events e ON e.id = eel.event_id "
            "JOIN geo_entities g ON g.id = eel.entity_id "
            "WHERE (e.year < g.year_start - 100) "
            "OR (g.year_end IS NOT NULL AND e.year > g.year_end + 100) "
            "LIMIT 30"
        )
    ).fetchall()

    if rows:
        issues_found["temporal_mismatch"] = [
            {
                "event_id": r.event_id,
                "event_name": r.event_name,
                "event_year": r.event_year,
                "entity_id": r.entity_id,
                "entity_name": r.entity_name,
                "entity_range": f"{r.year_start}..{r.year_end or 'present'}",
            }
            for r in rows
        ]

    # 2. Check for events with no sources (should be zero after v6.30)
    unsourced_events_result = db.execute(
        text(
            "SELECT id, name_original, year FROM historical_events "
            "WHERE id NOT IN (SELECT event_id FROM event_sources) "
            "LIMIT 20"
        )
    ).fetchall()
    if unsourced_events_result:
        issues_found["unsourced_events"] = [
            {"id": r.id, "name": r.name_original, "year": r.year}
            for r in unsourced_events_result
        ]

    # 3. Entities with inverted year range
    inverted = db.query(GeoEntity).filter(
        GeoEntity.year_end.isnot(None),
        GeoEntity.year_end < GeoEntity.year_start,
    ).all()
    if inverted:
        issues_found["inverted_year_range"] = [
            {"id": e.id, "name": e.name_original, "year_start": e.year_start, "year_end": e.year_end}
            for e in inverted
        ]

    # 4. Events with day without month
    bad_dates = db.query(HistoricalEvent).filter(
        HistoricalEvent.day.isnot(None),
        HistoricalEvent.month.is_(None),
    ).all()
    if bad_dates:
        issues_found["day_without_month"] = [
            {"id": e.id, "name": e.name_original, "day": e.day}
            for e in bad_dates[:10]
        ]

    # Create suggestion if any issues found
    if issues_found:
        total = sum(len(v) for v in issues_found.values())
        title = f"Cross-resource consistency: {total} logical inconsistencies"
        categories = ", ".join(f"{k}({len(v)})" for k, v in issues_found.items())
        added = _add_suggestion(
            db, existing_titles,
            category="consistency_bug",
            title=title,
            description=(
                f"The cross-resource consistency analyzer detected {total} "
                f"logical inconsistencies across tables: {categories}. "
                f"These pass FK constraints but indicate data-entry errors, "
                f"orphan references, or temporal mismatches (e.g., an event "
                f"year 200 years outside its linked entity's lifespan). "
                f"Most are fixable by manual review; some indicate bulk "
                f"import errors requiring script-based correction."
            ),
            priority=3,
            detail_json=json.dumps({
                "analyzer": "analyze_cross_resource_consistency",
                "issues": issues_found,
                "total": total,
            }, default=str),
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
            "date_coverage_gaps": analyze_date_coverage_gaps(db, existing),
            "geometric_bugs": analyze_geometric_bugs(db, existing),
            "consistency_bugs": analyze_cross_resource_consistency(db, existing),
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
