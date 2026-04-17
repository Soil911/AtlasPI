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
    # v6.32 additions based on /admin/ai/analyze findings:
    452: {  # 太平天國 (Taiping Heavenly Kingdom)
        "name": "Taiping Heavenly Kingdom",
        "radius_km": 600,  # controlled parts of southern China, Nanjing as capital
        "note": "Taiping Heavenly Kingdom (1851-1864) controlled parts of south-central China around Nanjing — estimated peak ~1M km², NOT the entire Chinese polygon (11M km²). Reverted.",
    },
    542: {  # Quilombos (confederation)
        "name": "Quilombos",
        "radius_km": 400,  # Palmares quilombo was in Alagoas/Pernambuco
        "note": "Quilombos were maroon communities of escaped slaves in Brazilian interior, the largest (Palmares) spanning ~350km in Alagoas/Pernambuco ~1600-1694. Never a unified 8.7M km² confederation. Reverted from Brazil polygon.",
    },
    326: {  # Cumans / Kipchaks
        "name": "Kipchak-Cuman confederation",
        "radius_km": 1000,  # Kazakh steppe — no single capital for nomads
        "fallback_lat": 47.0,  # Approximate center of Kazakh-Ukrainian steppe
        "fallback_lon": 60.0,
        "note": "Kipchak-Cuman confederation of nomadic tribes spanning Central Asian steppes (~3-4M km² Kazakh to Ukrainian steppe). Nomadic — no fixed capital. Approximated as 1000km circle centered on steppe midpoint. Reverted from 9.4M km² polygon.",
    },
    651: {  # Duché de Normandie
        "name": "Duchy of Normandy",
        "radius_km": 90,  # Normandy ~30k km²
        "note": "Duchy of Normandy was the historical region of Normandy (~30,000 km²), not much of NE France as the aourednik polygon suggests. Reverted.",
    },
    566: {  # Dugelezh Breizh (Duchy of Brittany)
        "name": "Duchy of Brittany",
        "radius_km": 90,  # Brittany ~30k km²
        "note": "Duchy of Brittany (Dugelezh Breizh) was the peninsula region ~30,000 km². Reverted from oversized polygon.",
    },
    580: {  # Kurfurstentum Sachsen
        "name": "Electorate of Saxony",
        "radius_km": 100,
        "note": "Electorate of Saxony was a relatively small HRE state centered on Dresden/Wittenberg ~50-100k km², not a Germany-wide region. Reverted from shared default polygon.",
    },
    581: {  # Kurfurstentum Pfalz
        "name": "Electorate of the Palatinate",
        "radius_km": 80,
        "note": "Electorate of the Palatinate was a relatively small HRE state ~20-50k km². Reverted from shared default polygon.",
    },
    587: {  # Herzogtum Wurttemberg
        "name": "Duchy of Württemberg",
        "radius_km": 80,
        "note": "Duchy of Württemberg was ~19,500 km² (Swabian region, modern Baden-Württemberg). Reverted from oversized polygon.",
    },
    655: {  # Hertugdømmet Slesvig
        "name": "Duchy of Schleswig",
        "radius_km": 80,
        "note": "Duchy of Schleswig was ~9,300 km² between Denmark and Holstein. Reverted from oversized polygon.",
    },
    538: {  # Avakuarusu (Guarani confederation)
        "name": "Avakuarusu / Guarani confederation",
        "radius_km": 800,  # Guarani lands span Paraguay, parts of Brazil, Argentina
        "note": "Avakuarusu (Guarani confederation) traditional lands spanned parts of modern Paraguay, southern Brazil, northeastern Argentina — estimated ~2M km², not the 5M km² polygon that overreaches into the Amazon. Reverted.",
    },
    779: {  # Lenapehoking
        "name": "Lenapehoking",
        "radius_km": 400,
        "note": "Lenapehoking (Lenape homeland) covered the Delaware River watershed including parts of modern NY, NJ, PA, DE, MD — approximately 100-150k km², not 4.6M. Reverted.",
    },
    773: {  # Coosa chiefdom
        "name": "Coosa paramount chiefdom",
        "radius_km": 250,
        "note": "Coosa paramount chiefdom covered much of modern northern Georgia, eastern Tennessee, northern Alabama ~100-200k km², not 500k+ km². Reverted.",
    },
    667: {  # Raska
        "name": "Grand Principality of Rascia",
        "radius_km": 150,
        "note": "Grand Principality of Rascia (Raška) was the medieval Serbian polity centered on modern Raška district, ~50-80k km² not 357k. Reverted.",
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
    in the same hemisphere as the capital. Discards far-flung pieces
    (Alaska Aleutians in the eastern hemisphere when capital is US mainland,
    Kamchatka wrapping for Russia, etc.)

    Strategy: keep polygons whose NON-WRAPPED longitude distance from capital
    is less than 90°. For continental states, this keeps the main landmass
    and drops antimeridian-crossing island chains. For genuinely bi-hemispheric
    entities (Fiji, Kiribati), the capital's hemisphere wins.

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

    # Keep polygons whose own bbox is on the SAME SIDE of antimeridian
    # as capital_lon. For USA cap=-77: keep polys entirely in lon<0.
    # For Russia cap=+37: keep polys with lon<=180 (so Kamchatka stays,
    # but we drop any wrap-around slivers).
    kept_polys = []
    for p in g.geoms:
        pbb = p.bounds
        # Reject polygon if it crosses antimeridian (both < -170 AND > 170)
        if pbb[0] < -170 and pbb[2] > 170:
            continue  # polygon itself crosses AM — skip
        # Use NON-WRAPPED longitude distance
        pcenter_lon = (pbb[0] + pbb[2]) / 2
        non_wrap_dist = abs(pcenter_lon - lon)
        # Use WRAPPED distance too, but prefer same-hemisphere
        if non_wrap_dist <= 90:
            kept_polys.append(p)
            continue
        # Tiny polygons within 150° are also kept (tiny islands near
        # the capital even if across antimeridian)
        if p.area < 0.5 and non_wrap_dist <= 150:
            kept_polys.append(p)

    if not kept_polys:
        return None

    if len(kept_polys) == 1:
        new_geom = kept_polys[0]
        if new_geom.geom_type == "Polygon":
            return mapping(new_geom)
        return mapping(MultiPolygon([new_geom]))

    new_geom = MultiPolygon(kept_polys)
    # Verify the result no longer crosses antimeridian
    nb = new_geom.bounds
    if (nb[2] - nb[0]) > 180:
        # Still problematic — find the largest single polygon, use that
        largest = max(kept_polys, key=lambda p: p.area)
        return mapping(largest if largest.geom_type != "Polygon" else largest)
    return mapping(new_geom)


# ─── Orchestrator ─────────────────────────────────────────────────────────


# Type-based CONSERVATIVE area ceilings (km²). Entities with polygon area
# exceeding `ceiling × AUTO_FIX_FACTOR` get auto-reset. Uses higher margin
# than the analyzer (which flags at 1.5×) to avoid false positives on
# legitimately-large entities (empires, trans-continental republics, etc.)
TYPE_MAX_AREA_KM2 = {
    "city": 10_000,
    "city-state": 50_000,
    "principality": 300_000,
    "duchy": 300_000,
    "chiefdom": 500_000,
    "tribal_nation": 2_000_000,
    "tribal_federation": 2_000_000,
    "confederation": 4_000_000,
    "kingdom": 8_000_000,
    "sultanate": 5_000_000,
    "republic": 15_000_000,
    "dynasty": 20_000_000,
    "caliphate": 20_000_000,
    "khanate": 40_000_000,
    "empire": 40_000_000,
}

# Fix oversized polygons if they exceed ceiling × this factor.
# Stricter factor for small entity types (higher risk of wrong-polygon inheritance)
AUTO_FIX_OVERSIZE_FACTOR = 3.0
AUTO_FIX_OVERSIZE_FACTOR_STRICT = 2.5  # for small types that rarely legitimately exceed ceiling

STRICT_TYPES = {"city", "city-state", "principality", "duchy", "chiefdom",
                "dynasty", "kingdom", "sultanate", "caliphate"}

# Radius (km) to use when regenerating a capital-based circle for an
# oversized polygon that we can't match to a better source.
TYPE_RESET_RADIUS_KM = {
    "city": 10,
    "city-state": 30,
    "principality": 80,
    "duchy": 100,
    "chiefdom": 150,
    "tribal_nation": 250,
    "tribal_federation": 250,
    "confederation": 400,
    "kingdom": 500,
    "sultanate": 400,
    "republic": 800,
    "dynasty": 700,
    "caliphate": 800,
    "khanate": 1000,
    "empire": 1200,
}


def _polygon_area_km2(geom) -> float:
    """Rough km² from shapely geometry (degree area × 111² — not great at poles, fine for sanity)."""
    return geom.area * 111 * 111


def fix_all(dry_run: bool = False) -> dict:
    db = SessionLocal()
    stats = {
        "wrong_polygon_fixed": 0,
        "antimeridian_clipped": 0,
        "oversized_reset": 0,
        "errors": 0,
        "details": [],
    }

    try:
        # Fix 1: reset wrong-polygon inheritors
        for eid, cfg in WRONG_POLYGON_FIXES.items():
            e = db.query(GeoEntity).filter(GeoEntity.id == eid).first()
            if e is None:
                continue
            # Use fallback coords if entity has no capital (e.g., nomadic peoples)
            cap_lat = e.capital_lat if e.capital_lat is not None else cfg.get("fallback_lat")
            cap_lon = e.capital_lon if e.capital_lon is not None else cfg.get("fallback_lon")
            if cap_lat is None or cap_lon is None:
                continue  # Still no coords — can't generate circle
            # If we used fallback, persist to entity for future use
            if e.capital_lat is None:
                e.capital_lat = cap_lat
                e.capital_lon = cap_lon
            new_polygon = _generate_circle(cap_lat, cap_lon, cfg["radius_km"])
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

                # Fix 3: oversized polygon for entity type (generic wrong-polygon)
                # A polygon area >> type ceiling is a strong signal of
                # fuzzy-match error (city-state with empire-sized polygon, etc.)
                type_ceiling = TYPE_MAX_AREA_KM2.get(e.entity_type)
                if type_ceiling and e.capital_lat is not None and e.capital_lon is not None:
                    try:
                        area_km2 = _polygon_area_km2(g)
                        # Stricter threshold for small/medieval types (duchy, principality, etc.)
                        # which rarely legitimately exceed their ceiling
                        factor = (
                            AUTO_FIX_OVERSIZE_FACTOR_STRICT
                            if e.entity_type in STRICT_TYPES
                            else AUTO_FIX_OVERSIZE_FACTOR
                        )
                        if area_km2 > type_ceiling * factor:
                            # Regenerate as type-sized capital circle
                            radius = TYPE_RESET_RADIUS_KM.get(e.entity_type, 200)
                            new_polygon = _generate_circle(e.capital_lat, e.capital_lon, radius)
                            e.boundary_geojson = json.dumps(new_polygon)
                            e.boundary_source = "approximate_generated"
                            e.boundary_aourednik_name = None
                            e.boundary_aourednik_year = None
                            e.boundary_aourednik_precision = None
                            e.boundary_ne_iso_a3 = None
                            if e.confidence_score > 0.5:
                                e.confidence_score = 0.5
                            note = (
                                f"[v6.31-oversize-reset] Boundary area was "
                                f"{area_km2:,.0f} km², exceeding {e.entity_type} "
                                f"ceiling ({type_ceiling:,} km²) by "
                                f"{area_km2/type_ceiling:.1f}×. Reset to capital-based "
                                f"circle ({radius}km radius) — likely wrong-polygon "
                                f"inheritance via fuzzy name matching. Manual review "
                                f"recommended if the entity's true extent is known."
                            )
                            existing = e.ethical_notes or ""
                            if "[v6.31-oversize-reset]" not in existing:
                                e.ethical_notes = (existing + "\n\n" if existing else "") + note
                            stats["oversized_reset"] += 1
                            stats["details"].append(
                                f"OVERSIZE id={e.id} {e.name_original[:30]} "
                                f"{area_km2:,.0f}km² > {type_ceiling:,}km² ({e.entity_type})"
                            )
                            continue  # don't also run antimeridian check
                    except Exception as ex:
                        logger.debug("Area check failed for %d: %s", e.id, ex)

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
