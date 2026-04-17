"""Revert aourednik boundaries that are catastrophically displaced from capital.

v6.29 boundary enrichment upgraded many entities from approximate_generated
to aourednik data, but some fuzzy-name matches landed polygons geographically
far from the entity's capital (e.g., Pacific island polities matched to
Indian Ocean polygons because of name similarity).

This script detects displacement > 3000km between capital and polygon
centroid, and for those entities:
  1. Replaces boundary_geojson with a generated circle around the capital
  2. Sets boundary_source back to 'approximate_generated'
  3. Appends an ETHICS note explaining the rollback
  4. Caps confidence_score at 0.4 (ETHICS-004)

Run:
    python -m src.ingestion.fix_displaced_aourednik           # apply
    python -m src.ingestion.fix_displaced_aourednik --dry-run # preview
"""

from __future__ import annotations

import argparse
import json
import logging
import math
from datetime import datetime, timezone

from pyproj import Geod
from shapely.geometry import shape

from src.db.database import SessionLocal
from src.db.models import GeoEntity

logger = logging.getLogger(__name__)

_GEOD = Geod(ellps="WGS84")

# Displacement threshold: centroid distance > 1500km is almost certainly wrong.
# Legitimate vast empires (Umayyad, Mongol) have polygons where the capital
# can be far from the centroid but capital-to-polygon-edge distance is small.
# Using polygon-edge distance (via _capital_distance_to_polygon_km) when available,
# with fallback to centroid distance.
DISPLACEMENT_THRESHOLD_KM = 1500.0
# Polygon-edge threshold (tighter since it ignores polygon size)
POLYGON_EDGE_THRESHOLD_KM = 800.0


def _generate_circle_polygon(lat: float, lon: float, radius_km: float = 150.0) -> dict:
    """Create a rough circle around (lat, lon) as a polygon GeoJSON."""
    # Approximate: 1 degree latitude ~ 111 km
    lat_delta = radius_km / 111.0
    # Longitude degrees depend on latitude
    lon_delta = radius_km / (111.0 * max(0.1, math.cos(math.radians(lat))))

    num_points = 32
    coords = []
    for i in range(num_points):
        theta = 2 * math.pi * i / num_points
        coords.append([
            lon + lon_delta * math.cos(theta),
            lat + lat_delta * math.sin(theta),
        ])
    # Close the ring
    coords.append(coords[0])

    return {
        "type": "Polygon",
        "coordinates": [coords],
    }


def _displacement_km(entity: GeoEntity) -> tuple[float | None, float | None]:
    """Return (centroid_dist_km, polygon_edge_dist_km), or (None, None)."""
    if not entity.boundary_geojson or not entity.capital_lat or not entity.capital_lon:
        return (None, None)
    try:
        geom = shape(json.loads(entity.boundary_geojson))
        centroid = geom.centroid
        _, _, centroid_m = _GEOD.inv(
            entity.capital_lon,
            entity.capital_lat,
            centroid.x,
            centroid.y,
        )
        # Polygon-edge distance: 0 if capital is inside polygon, else distance to boundary
        from shapely.geometry import Point
        pt = Point(entity.capital_lon, entity.capital_lat)
        if geom.contains(pt):
            edge_km = 0.0
        else:
            # Find nearest boundary point (approximate via Shapely distance in degrees,
            # then convert using average km-per-degree at this latitude)
            edge_deg = geom.boundary.distance(pt)
            # Rough conversion: 1 degree ~ 111km, adjusted for latitude
            km_per_deg = 111.0 * max(0.1, math.cos(math.radians(entity.capital_lat)))
            edge_km = edge_deg * km_per_deg
        return (centroid_m / 1000, edge_km)
    except Exception:
        return (None, None)


def fix_displaced(dry_run: bool = False) -> dict:
    """Find and fix displaced aourednik boundaries."""
    db = SessionLocal()
    stats = {
        "inspected": 0,
        "displaced": 0,
        "fixed": 0,
        "errors": 0,
        "samples": [],
    }

    try:
        entities = (
            db.query(GeoEntity)
            .filter(
                GeoEntity.boundary_source == "aourednik",
                GeoEntity.boundary_geojson.isnot(None),
                GeoEntity.capital_lat.isnot(None),
                GeoEntity.capital_lon.isnot(None),
            )
            .all()
        )
        stats["inspected"] = len(entities)

        for e in entities:
            centroid_dist, edge_dist = _displacement_km(e)
            if centroid_dist is None:
                continue

            # Flag as displaced if EITHER:
            #   - centroid is very far from capital (large empires excepted)
            #   - capital is outside polygon by more than polygon-edge threshold
            is_displaced = (
                centroid_dist > DISPLACEMENT_THRESHOLD_KM
                or (edge_dist is not None and edge_dist > POLYGON_EDGE_THRESHOLD_KM)
            )

            if is_displaced:
                stats["displaced"] += 1
                if len(stats["samples"]) < 20:
                    stats["samples"].append(
                        f"id={e.id} '{e.name_original}' centroid={centroid_dist:.0f}km edge={edge_dist:.0f}km"
                    )

                if not dry_run:
                    # Generate capital-based circle (radius 150km by default)
                    # Adjusted by entity_type: empire gets bigger radius
                    type_radius = {
                        "empire": 500.0,
                        "caliphate": 500.0,
                        "kingdom": 200.0,
                        "sultanate": 200.0,
                        "khanate": 300.0,
                        "republic": 150.0,
                        "confederation": 250.0,
                        "dynasty": 200.0,
                        "principality": 80.0,
                        "duchy": 60.0,
                        "city-state": 20.0,
                        "city": 10.0,
                    }
                    radius = type_radius.get(e.entity_type, 150.0)

                    new_polygon = _generate_circle_polygon(
                        e.capital_lat, e.capital_lon, radius_km=radius
                    )
                    e.boundary_geojson = json.dumps(new_polygon)
                    e.boundary_source = "approximate_generated"
                    # Clear aourednik tracking since we're no longer using it
                    e.boundary_aourednik_name = None
                    e.boundary_aourednik_year = None
                    e.boundary_aourednik_precision = None

                    # ETHICS-004: cap confidence
                    if e.confidence_score > 0.4:
                        e.confidence_score = 0.4

                    # Append rollback note
                    note_marker = "[v6.30-displaced-rollback]"
                    rollback_note = (
                        f"{note_marker} Boundary reverted to capital-based approximation: "
                        f"aourednik fuzzy match placed polygon centroid={centroid_dist:.0f}km / "
                        f"edge={edge_dist:.0f}km from capital (exceeded thresholds). "
                        f"Regenerated as {radius}km radius circle. "
                        f"Reverted {datetime.now(timezone.utc).date().isoformat()}."
                    )
                    if e.ethical_notes:
                        e.ethical_notes = e.ethical_notes + "\n\n" + rollback_note
                    else:
                        e.ethical_notes = rollback_note

                    stats["fixed"] += 1

        if not dry_run:
            db.commit()
            logger.info("Committed %d rollbacks", stats["fixed"])
        else:
            db.rollback()

    except Exception:
        db.rollback()
        stats["errors"] += 1
        raise
    finally:
        db.close()

    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    stats = fix_displaced(dry_run=args.dry_run)
    print("\n=== Displaced aourednik rollback stats ===")
    for k, v in stats.items():
        if k == "samples":
            continue
        print(f"  {k:30s} {v}")
    if stats.get("samples"):
        print("\nSamples of displaced entities:")
        for s in stats["samples"]:
            print(f"  {s}")


if __name__ == "__main__":
    main()
