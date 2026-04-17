"""Fix antimeridian-crossing boundaries + entities with wrong-country polygons.

Two distinct bugs identified v6.30.x:

1. WRONG-COUNTRY POLYGONS: several Native American confederations (Cherokee,
   Seminole, Oceti Sakowin) and the USSR inherited the entire USA/Russia
   natural_earth polygon via boundary matching. Their actual territorial
   extent was much smaller / different. Fix: reset to approximate_generated
   capital-based circle sized per historical extent.

2. ANTIMERIDIAN CROSSING: boundaries with real +/-180° crossing (USA
   Aleutians, Russian Kamchatka, Fiji, NZ Ngati Toa generated circle) have
   bounding boxes spanning ~360° → Leaflet bbox-center labels appear in
   absurd locations (France, Gulf of Guinea, Atlantic). Fix: clip or split
   polygons so bbox stays within a reasonable longitude range.

Run:
    python -m src.ingestion.fix_antimeridian_and_wrong_polygons
    python -m src.ingestion.fix_antimeridian_and_wrong_polygons --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import math

from shapely.geometry import MultiPolygon, Polygon, mapping, shape

from src.db.database import SessionLocal
from src.db.models import GeoEntity

logger = logging.getLogger(__name__)


# ─── Fix 1: Wrong-country polygon inheritance ──────────────────────────────

# Entities that inherited a too-large national polygon. Each gets reset to
# approximate_generated with a capital-based circle of appropriate radius.
WRONG_POLYGON_FIXES = {
    218: {  # Cherokee (ᏣᎳᎩ)
        "name": "Cherokee",
        "radius_km": 300,  # Southern Appalachian region
        "note": "Cherokee territory was in the southern Appalachians (modern NC, TN, GA, SC, AL) — ~150-200k km², not the entire USA.",
    },
    545: {  # Seminole / Ikaniuksalgi
        "name": "Seminole",
        "radius_km": 200,  # Florida peninsula
        "note": "Seminole homeland was Florida — ~170k km², not the entire USA.",
    },
    727: {  # Oceti Sakowin
        "name": "Oceti Sakowin (Great Sioux Nation)",
        "radius_km": 700,  # Great Plains
        "note": "Oceti Sakowin (Dakota/Lakota/Nakota) territory spanned the Great Plains — ~1.5M km², not the entire USA.",
    },
    230: {  # USSR
        "name": "USSR",
        "radius_km": 2500,  # approximate radius for USSR extent — spans from Kaliningrad to Kamchatka
        "note": "Soviet Union spanned 22.4M km² including Caucasus, Central Asia, Ukraine, Baltics — NOT just modern Russian Federation. Reverted from Russia-only polygon.",
    },
}


def _generate_circle(lat: float, lon: float, radius_km: float, num_points: int = 48) -> dict:
    """Circle polygon, clipped to prevent antimeridian crossing."""
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * max(0.1, math.cos(math.radians(lat))))

    # Clip lon_delta to prevent wrap
    max_safe_delta = 179.0 - abs(lon)
    if lon_delta > max_safe_delta and max_safe_delta > 10:
        lon_delta = max_safe_delta

    coords = []
    for i in range(num_points):
        theta = 2 * math.pi * i / num_points
        x = lon + lon_delta * math.cos(theta)
        y = lat + lat_delta * math.sin(theta)
        # Clamp to valid lon range
        if x > 180:
            x = 180
        if x < -180:
            x = -180
        if y > 85:
            y = 85
        if y < -85:
            y = -85
        coords.append([x, y])
    coords.append(coords[0])  # close ring

    return {"type": "Polygon", "coordinates": [coords]}


# ─── Fix 2: Antimeridian-crossing boundary normalization ──────────────────


def _normalize_antimeridian(geom: dict, lat: float | None, lon: float | None) -> dict | None:
    """For MultiPolygons that cross the antimeridian, keep only polygons
    near the entity's capital. Discards far-flung pieces (e.g. Alaska's
    Aleutian islands > +170° when the capital is in continental US).

    Returns None if no meaningful fix is possible.
    """
    if lat is None or lon is None:
        return None

    g = shape(geom)
    if g.geom_type != "MultiPolygon":
        return None

    # Check actual bbox
    bb = g.bounds
    if (bb[2] - bb[0]) < 180:
        return None  # no antimeridian issue

    # Keep polygons whose own bbox is within ±170° of capital_lon
    # (i.e., don't take Aleutians wrapped to +179 if capital is at -77)
    kept_polys = []
    for p in g.geoms:
        pbb = p.bounds
        # A polygon is "far" if its center is more than 170° from capital_lon
        pcenter_lon = (pbb[0] + pbb[2]) / 2
        # Compute great-circle-ish longitude distance
        dist_lon = abs(pcenter_lon - lon)
        if dist_lon > 180:
            dist_lon = 360 - dist_lon
        if dist_lon <= 160:  # within 160 degrees of capital
            kept_polys.append(p)

    if not kept_polys:
        return None

    if len(kept_polys) == 1:
        new_geom = kept_polys[0]
        # ensure it's still a Polygon/MultiPolygon
        if new_geom.geom_type == "Polygon":
            return mapping(new_geom)
        return mapping(MultiPolygon([new_geom]))

    new_geom = MultiPolygon(kept_polys)
    return mapping(new_geom)


# ─── Orchestrator ─────────────────────────────────────────────────────────


def fix_all(dry_run: bool = False) -> dict:
    db = SessionLocal()
    stats = {
        "wrong_polygon_fixed": 0,
        "antimeridian_clipped": 0,
        "errors": 0,
        "details": [],
    }

    try:
        # Fix 1: reset wrong-polygon inheritors
        for eid, cfg in WRONG_POLYGON_FIXES.items():
            e = db.query(GeoEntity).filter(GeoEntity.id == eid).first()
            if e is None or e.capital_lat is None or e.capital_lon is None:
                continue
            new_polygon = _generate_circle(e.capital_lat, e.capital_lon, cfg["radius_km"])
            e.boundary_geojson = json.dumps(new_polygon)
            e.boundary_source = "approximate_generated"
            e.boundary_aourednik_name = None
            e.boundary_aourednik_year = None
            e.boundary_aourednik_precision = None
            e.boundary_ne_iso_a3 = None
            # cap confidence
            if e.confidence_score > 0.5:
                e.confidence_score = 0.5
            # append note
            note = (
                f"[v6.31-wrong-polygon-reset] {cfg['note']} "
                f"Boundary reset to approximate circle ({cfg['radius_km']}km radius) "
                f"around capital coordinates. Previous boundary was an over-reach "
                f"of national (USA/RUS) polygon via faulty name/ISO matching."
            )
            existing = e.ethical_notes or ""
            if "[v6.31-wrong-polygon-reset]" not in existing:
                e.ethical_notes = (existing + "\n\n" if existing else "") + note
            stats["wrong_polygon_fixed"] += 1
            stats["details"].append(f"WRONG-POLYGON id={eid} {cfg['name']}")
            logger.info("Reset wrong-polygon entity %d (%s)", eid, cfg["name"])

        # Fix 2: antimeridian clipping for remaining entities
        suspects = db.query(GeoEntity).filter(
            GeoEntity.boundary_geojson.isnot(None)
        ).all()

        for e in suspects:
            if e.id in WRONG_POLYGON_FIXES:
                continue  # already handled
            try:
                geom_obj = json.loads(e.boundary_geojson)
                g = shape(geom_obj)
                bb = g.bounds
                if (bb[2] - bb[0]) < 180:
                    continue
                # Antimeridian crossing detected
                new_geom = _normalize_antimeridian(geom_obj, e.capital_lat, e.capital_lon)
                if new_geom is None:
                    # If we can't fix via clipping, regenerate as capital circle
                    if e.capital_lat is not None and e.capital_lon is not None:
                        # Use entity_type-based radius
                        type_radius = {
                            "empire": 500, "republic": 500, "kingdom": 200,
                            "sultanate": 200, "khanate": 300, "confederation": 250,
                            "chiefdom": 100, "dynasty": 200, "principality": 80,
                            "duchy": 60, "city-state": 20, "city": 10,
                        }
                        radius = type_radius.get(e.entity_type, 200)
                        new_geom = _generate_circle(e.capital_lat, e.capital_lon, radius)
                        e.boundary_source = "approximate_generated"
                        e.boundary_aourednik_name = None
                        e.boundary_aourednik_year = None
                        e.boundary_aourednik_precision = None
                        e.boundary_ne_iso_a3 = None

                e.boundary_geojson = json.dumps(new_geom)
                # keep boundary_source unless we regenerated
                note = (
                    "[v6.31-antimeridian-fix] Boundary clipped to remove "
                    "antimeridian-crossing polygons (Aleutians, Kamchatka tip, "
                    "Fiji eastern pieces, etc.). Main landmass preserved; "
                    "bbox now reasonable for map label rendering."
                )
                existing = e.ethical_notes or ""
                if "[v6.31-antimeridian-fix]" not in existing:
                    e.ethical_notes = (existing + "\n\n" if existing else "") + note
                stats["antimeridian_clipped"] += 1
                stats["details"].append(f"ANTIMERIDIAN id={e.id} {e.name_original}")
            except Exception as exc:
                logger.warning("Error processing entity %d: %s", e.id, exc)
                stats["errors"] += 1

        if dry_run:
            db.rollback()
        else:
            db.commit()

        return stats
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    stats = fix_all(dry_run=args.dry_run)
    print("\n=== Antimeridian & wrong-polygon fix stats ===")
    print(f"  wrong_polygon_fixed:    {stats['wrong_polygon_fixed']}")
    print(f"  antimeridian_clipped:   {stats['antimeridian_clipped']}")
    print(f"  errors:                 {stats['errors']}")
    print()
    for d in stats["details"]:
        print(f"  {d}")
    if args.dry_run:
        print("\n(dry-run — no DB changes)")


if __name__ == "__main__":
    main()
