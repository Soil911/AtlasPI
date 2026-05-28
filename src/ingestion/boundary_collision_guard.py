"""Boundary collision guard — detect polygon collisions among historical entities.

v6.99.79 (Phase H boundary review follow-up): after fixing ~250 polygon collisions
caused by aourednik + natural_earth fuzzy-matching errors (entities sharing
"super-group" cultural-linguistic polygons), this guard runs at boot to detect
NEW collisions that would indicate a regression in the matching pipeline.

ETHICS-006: collision detection is informational, not corrective. The guard
LOGS suspect collisions but does NOT auto-rewrite polygons — that risks
destroying legitimate same-state entities (e.g. duplicates that need merge,
or culturally-consolidated polygons that are intentionally shared).

What is a "suspect collision"?
  Two or more entities with byte-identical boundary_geom areas (to 4 decimal
  places of deg²). Specifically:
    - Different name_original (excluding pure transliteration variants)
    - Or different year_start range (more than 200 years apart)
    - Or same boundary_aourednik_name (super-group matching error)
  Threshold for alarm: > MAX_ALLOWED_COLLISIONS pairs.

What is NOT a suspect collision (legitimate sharing):
  - Genuine duplicates flagged for merge (Bohemia Czech + Bohemia Danish)
  - Same culture across periods (Ancestral Puebloans + Pueblo)
  - Federations with member entities (e.g., Hanseatic League with member cities)
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# Threshold: more than N suspect collision groups triggers a WARNING in logs.
# Calibrated against post-Phase-H state (40 minor collisions remaining,
# mostly known duplicates). A jump to >60 indicates a regression.
MAX_ALLOWED_COLLISION_GROUPS = 60

# Threshold for individual group size: groups with >= N members are SUSPICIOUS
# even if total count is OK (e.g., 1 group of 10 entities is a big problem).
MAX_GROUP_SIZE_BEFORE_ALARM = 4


def detect_boundary_collisions() -> dict[str, Any]:
    """Detect entities sharing identical boundary_geom areas.

    Returns dict with:
      - total_groups: int, number of distinct collision groups (area buckets)
      - total_entities: int, number of entities involved in any collision
      - big_groups: list of dicts, groups with >= MAX_GROUP_SIZE_BEFORE_ALARM members
      - super_group_alerts: list of dicts, entities sharing same
        boundary_aourednik_name (likely fuzzy-match regression)
      - status: "ok" | "warning" | "alarm"
    """
    from sqlalchemy import text

    from src.db.database import SessionLocal, is_postgres

    if not is_postgres:
        return {"status": "skip", "reason": "non-postgres dialect"}

    db = SessionLocal()
    try:
        # Detect collisions: entities with identical boundary_geom area (to 4 dp)
        collisions = db.execute(
            text(
                """
                SELECT
                  ROUND(ST_Area(boundary_geom)::numeric, 4) AS area_bucket,
                  COUNT(*) AS n,
                  array_agg(id ORDER BY id) AS ids,
                  array_agg(name_original ORDER BY id) AS names,
                  array_agg(boundary_aourednik_name ORDER BY id) AS aour_names,
                  array_agg(year_start ORDER BY id) AS years
                FROM geo_entities
                WHERE boundary_geom IS NOT NULL
                  AND boundary_source IN ('aourednik', 'natural_earth')
                GROUP BY area_bucket
                HAVING COUNT(*) >= 2
                ORDER BY n DESC, area_bucket DESC
                """
            )
        ).all()

        total_groups = len(collisions)
        total_entities = sum(row.n for row in collisions)
        big_groups: list[dict[str, Any]] = []
        super_group_alerts: list[dict[str, Any]] = []

        for row in collisions:
            # Big groups: 4+ entities sharing polygon = strong fuzzy-match suspect
            if row.n >= MAX_GROUP_SIZE_BEFORE_ALARM:
                big_groups.append(
                    {
                        "area_deg2": float(row.area_bucket),
                        "n_entities": row.n,
                        "ids": list(row.ids),
                        "names": list(row.names),
                    }
                )

            # Super-group alert: if all entities share same aourednik_name AND
            # are not pure transliteration duplicates → strong regression
            # signal. We detect by looking for matching aour_names with
            # diverse year_start (>200 years apart).
            aour_set = {n for n in row.aour_names if n}
            if len(aour_set) == 1 and aour_set != {None}:
                # All entities share same aourednik_name
                year_min = min(row.years)
                year_max = max(row.years)
                if year_max - year_min > 200:
                    # Entities span >200 years = likely different polities
                    super_group_alerts.append(
                        {
                            "boundary_aourednik_name": next(iter(aour_set)),
                            "n_entities": row.n,
                            "year_range": (year_min, year_max),
                            "ids": list(row.ids),
                            "names": list(row.names),
                        }
                    )

        # Determine status
        if total_groups > MAX_ALLOWED_COLLISION_GROUPS or super_group_alerts:
            status = "alarm"
        elif big_groups:
            status = "warning"
        else:
            status = "ok"

        result = {
            "total_groups": total_groups,
            "total_entities": total_entities,
            "big_groups_count": len(big_groups),
            "super_group_alert_count": len(super_group_alerts),
            "big_groups": big_groups[:5],  # cap details to first 5 for log
            "super_group_alerts": super_group_alerts[:5],
            "status": status,
        }

        # Log according to status
        if status == "alarm":
            logger.warning(
                "Boundary collision ALARM: %d groups (%d entities), %d big groups, "
                "%d super-group alerts — likely fuzzy-match regression in "
                "ingestion pipeline. See big_groups / super_group_alerts in result. "
                "Run docs/boundary-review-v6.99.79/phase1_screening_report.md "
                "analyzer for full investigation.",
                total_groups,
                total_entities,
                len(big_groups),
                len(super_group_alerts),
            )
            for alert in super_group_alerts[:3]:
                logger.warning(
                    "  SUPER-GROUP: '%s' shared by %d entities (years %d-%d): %s",
                    alert["boundary_aourednik_name"],
                    alert["n_entities"],
                    alert["year_range"][0],
                    alert["year_range"][1],
                    ", ".join(alert["names"][:5]),
                )
        elif status == "warning":
            logger.warning(
                "Boundary collisions: %d groups (%d entities), %d big groups — "
                "expected post-Phase-H baseline. Monitor for growth.",
                total_groups,
                total_entities,
                len(big_groups),
            )
        else:
            logger.debug(
                "Boundary collisions: %d groups (%d entities) — within baseline.",
                total_groups,
                total_entities,
            )

        return result
    finally:
        db.close()
