"""Apply the displacement fix to entity JSON files directly.

This ensures the batch JSON files are the source of truth — subsequent
seeds will not reintroduce displaced boundaries. Run once to heal the
committed data; subsequent runs are idempotent (no-op).

Run:
    python -m scripts.fix_displaced_in_json
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

# Ensure project root on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from pyproj import Geod
from shapely.geometry import Point, shape

_GEOD = Geod(ellps="WGS84")
ENTITIES_DIR = _PROJECT_ROOT / "data" / "entities"

CENTROID_THRESHOLD_KM = 1500.0
EDGE_THRESHOLD_KM = 800.0


def _generate_circle(lat: float, lon: float, radius_km: float) -> dict:
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * max(0.1, math.cos(math.radians(lat))))
    num_points = 32
    coords = []
    for i in range(num_points):
        theta = 2 * math.pi * i / num_points
        coords.append([
            lon + lon_delta * math.cos(theta),
            lat + lat_delta * math.sin(theta),
        ])
    coords.append(coords[0])
    return {"type": "Polygon", "coordinates": [coords]}


TYPE_RADIUS_KM = {
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
    "tribal_nation": 150.0,
    "tribal_federation": 150.0,
    "chiefdom": 100.0,
    "federation": 200.0,
    "colony": 300.0,
    "cultural_region": 300.0,
    "civilization": 400.0,
    "disputed_territory": 100.0,
}


def compute_displacement(entity: dict) -> tuple[float, float] | None:
    """Return (centroid_km, edge_km) or None if not applicable."""
    if entity.get("boundary_source") != "aourednik":
        return None
    boundary = entity.get("boundary_geojson")
    if not boundary:
        return None
    lat, lon = entity.get("capital_lat"), entity.get("capital_lon")
    if lat is None or lon is None:
        return None

    try:
        geom = shape(boundary) if isinstance(boundary, dict) else shape(json.loads(boundary))
        centroid = geom.centroid
        _, _, centroid_m = _GEOD.inv(lon, lat, centroid.x, centroid.y)
        pt = Point(lon, lat)
        if geom.contains(pt):
            edge_km = 0.0
        else:
            edge_deg = geom.boundary.distance(pt)
            km_per_deg = 111.0 * max(0.1, math.cos(math.radians(lat)))
            edge_km = edge_deg * km_per_deg
        return (centroid_m / 1000, edge_km)
    except Exception:
        return None


def fix_file(filepath: Path) -> tuple[int, int]:
    """Apply displacement fix to one JSON file. Returns (changed, inspected)."""
    with filepath.open(encoding="utf-8") as f:
        entities = json.load(f)

    changed = 0
    for e in entities:
        disp = compute_displacement(e)
        if disp is None:
            continue
        centroid_km, edge_km = disp
        if centroid_km <= CENTROID_THRESHOLD_KM and edge_km <= EDGE_THRESHOLD_KM:
            continue

        # Displaced — rewrite
        etype = e.get("entity_type", "kingdom")
        radius = TYPE_RADIUS_KM.get(etype, 150.0)
        lat, lon = e["capital_lat"], e["capital_lon"]
        e["boundary_geojson"] = _generate_circle(lat, lon, radius)
        e["boundary_source"] = "approximate_generated"
        # Clear tracking fields
        for k in ("boundary_aourednik_name", "boundary_aourednik_year", "boundary_aourednik_precision"):
            e.pop(k, None)
        # Cap confidence
        if e.get("confidence_score", 0.5) > 0.4:
            e["confidence_score"] = 0.4
        # Append ETHICS note
        note_marker = "[v6.30-displaced-rollback]"
        rollback_note = (
            f"{note_marker} Boundary reverted to capital-based approximation: "
            f"aourednik fuzzy match placed polygon centroid={centroid_km:.0f}km / "
            f"edge={edge_km:.0f}km from capital (exceeded thresholds). "
            f"Regenerated as {radius}km radius circle."
        )
        existing_notes = e.get("ethical_notes", "")
        if existing_notes:
            if note_marker not in existing_notes:
                e["ethical_notes"] = existing_notes + "\n\n" + rollback_note
        else:
            e["ethical_notes"] = rollback_note
        changed += 1

    if changed > 0:
        with filepath.open("w", encoding="utf-8") as f:
            json.dump(entities, f, ensure_ascii=False, indent=2)

    return (changed, len(entities))


def main():
    print(f"Fixing displaced aourednik entities in {ENTITIES_DIR}...")
    total_changed = 0
    total_inspected = 0
    for fp in sorted(ENTITIES_DIR.glob("batch_*.json")):
        if fp.name.endswith(".bak"):
            continue
        changed, inspected = fix_file(fp)
        total_changed += changed
        total_inspected += inspected
        if changed > 0:
            print(f"  {fp.name}: fixed {changed}/{inspected}")

    print(f"\nTotal: fixed {total_changed} of {total_inspected} entities")


if __name__ == "__main__":
    main()
