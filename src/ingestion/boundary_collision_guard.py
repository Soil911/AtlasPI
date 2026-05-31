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


# ─── PostGIS-free variant (Wave 2 #7) ──────────────────────────────────────
# The query above needs PostGIS (ST_Area on boundary_geom), so it only runs in
# the Postgres CI job. The SQLite test suite — which runs on every PR — gets the
# same fence via this pure-Python detector that works directly on the JSON
# source (data/entities/*.json), i.e. exactly the artifact a fresh seed loads.
#
# Difference vs the PostGIS version: instead of bucketing by ST_Area (equal area
# ≈ same polygon), we bucket by the sha256 of the canonical geometry — i.e.
# *byte-identical* polygons. This is the precise signature of the Phase H
# super-group bug, where the fuzzy matcher literally assigned the SAME upstream
# polygon to several historically-distinct entities. The two detectors agree on
# super-group alerts (the hard fence); the JSON one is strictly stricter on
# bucketing, so its group COUNT is not compared against the loose 60 threshold.

# Year span beyond which entities sharing one aourednik label are almost
# certainly different polities (matches the >200y test in the PostGIS query).
SUPER_GROUP_YEAR_SPAN = 200

# Sources produced by the fuzzy matcher — the only ones that can carry the
# super-group regression. Curated circles / hand-drawn polygons / Natural-Earth
# modern shapes are out of scope (a shared circle is impossible; see ETHICS-012).
_FUZZY_SOURCES = ("aourednik", "natural_earth")


def _canonical_geom_key(geom: Any) -> str | None:
    """Stable hash of a GeoJSON geometry, robust to key order and fp jitter.

    Coordinates are rounded to 6 dp (~0.1 m) before hashing so that two
    geometries that differ only by float-serialisation noise still collide —
    we want to catch *the same polygon assigned twice*, not formatting.
    """
    import hashlib

    if not isinstance(geom, dict) or "coordinates" not in geom:
        return None

    def _round(c: Any) -> Any:
        if isinstance(c, list):
            if c and isinstance(c[0], (int, float)):
                return [round(float(v), 6) for v in c]
            return [_round(x) for x in c]
        return c

    import json as _json

    payload = _json.dumps(
        {"type": geom.get("type"), "coordinates": _round(geom.get("coordinates"))},
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def detect_json_boundary_collisions(entities: list[dict]) -> dict[str, Any]:
    """PostGIS-free super-group collision detector over JSON entity dicts.

    Args:
        entities: list of entity dicts as produced by
            ``src.db.seed.load_all_entities`` (each with ``boundary_geojson`` as
            a dict, ``boundary_source``, ``boundary_aourednik_name``,
            ``year_start``, ``name_original``).

    Returns the same shape as :func:`detect_boundary_collisions` minus the
    Postgres-only ``status`` heuristics: ``super_group_alerts`` and
    ``big_groups`` are the actionable signals for the CI fence.
    """
    buckets: dict[str, list[dict]] = {}
    for ent in entities:
        if ent.get("boundary_source") not in _FUZZY_SOURCES:
            continue
        key = _canonical_geom_key(ent.get("boundary_geojson"))
        if key is None:
            continue
        buckets.setdefault(key, []).append(ent)

    super_group_alerts: list[dict[str, Any]] = []
    big_groups: list[dict[str, Any]] = []

    for members in buckets.values():
        if len(members) < 2:
            continue

        # Big group: 4+ fuzzy entities sharing one byte-identical polygon.
        if len(members) >= MAX_GROUP_SIZE_BEFORE_ALARM:
            big_groups.append(
                {
                    "n_entities": len(members),
                    "names": [m.get("name_original") for m in members],
                }
            )

        # Super-group: same aourednik label spanning > SUPER_GROUP_YEAR_SPAN.
        by_label: dict[str, list[int]] = {}
        names_by_label: dict[str, list[str]] = {}
        for m in members:
            label = m.get("boundary_aourednik_name")
            if not label:
                continue
            yr = m.get("year_start")
            if yr is None:
                continue
            by_label.setdefault(label, []).append(yr)
            names_by_label.setdefault(label, []).append(m.get("name_original"))
        for label, years in by_label.items():
            if len(years) >= 2 and (max(years) - min(years)) > SUPER_GROUP_YEAR_SPAN:
                super_group_alerts.append(
                    {
                        "boundary_aourednik_name": label,
                        "n_entities": len(years),
                        "year_range": (min(years), max(years)),
                        "names": names_by_label[label],
                    }
                )

    return {
        "total_groups": sum(1 for m in buckets.values() if len(m) >= 2),
        "super_group_alerts": super_group_alerts,
        "super_group_alert_count": len(super_group_alerts),
        "big_groups": big_groups,
        "big_groups_count": len(big_groups),
        "status": "alarm" if (super_group_alerts or big_groups) else "ok",
    }
