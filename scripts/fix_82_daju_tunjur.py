"""Close AI Co-Founder suggestion #82: Daju (1032) & Tunjur (1033) shared an
identical Darfur boundary AND capital.

Two distinct, successive Darfur sultanates were collapsed onto one byte-identical
hand-drawn polygon + the same capital (14.14, 23.7) — false precision implying
they occupied the exact same territory. Per ETHICS-014 an auto-fix (capital
circle) was declined because a circle around the SAME capital would still be
identical. The honest fix needs DISTINCT, sourced centres:

  * Daju  (~1200-1400): southern Jebel Marra (sultan Ahmed el-Daj moved the
    capital to Jebel Marra ~1100). O'Fahey & Spaulding, Kingdoms of the Sudan.
  * Tunjur (~1400-1640): northern Darfur — capital Uri, then Ain Farah (Furnung
    Hills, ~130 km NW of El Fasher). O'Fahey, The Darfur Sultanate.

So each gets a distinct capital-centred approximate_circle (honest: we know
approximate centres, not exact documented borders). boundary_source becomes
approximate_circle; aourednik provenance cleared. Identical GeoJSON written to
the JSON source AND emitted in the prod SQL (deterministic generator), keeping
source == prod.

Usage:
    python -m scripts.fix_82_daju_tunjur --dry-run
    python -m scripts.fix_82_daju_tunjur
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTITIES_DIR = ROOT / "data" / "entities"
SQL_OUT = ROOT / "data" / "fixes" / "fix_82_daju_tunjur.sql"

# (prod id, JSON name_original, capital_lat, capital_lon, radius_km)
TARGETS = [
    (1032, "سلطنة الداجو", 12.7, 24.2, 120),   # Daju — southern Jebel Marra
    (1033, "التنجر", 14.5, 24.4, 120),         # Tunjur — Ain Farah, northern Darfur
]


def circle(lat: float, lon: float, km: float, n: int = 36) -> dict:
    """Approximate geodesic circle as a GeoJSON MultiPolygon (equirectangular;
    fine for an explicitly-approximate capital circle). Deterministic."""
    dlat = km / 111.32
    dlon = km / (111.32 * math.cos(math.radians(lat)))
    ring = []
    for i in range(n):
        a = 2 * math.pi * i / n
        ring.append([round(lon + dlon * math.cos(a), 5), round(lat + dlat * math.sin(a), 5)])
    ring.append(ring[0])
    return {"type": "MultiPolygon", "coordinates": [[ring]]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Close suggestion #82 (Daju/Tunjur distinct geometry).")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass

    geoms = {eid: (name, lat, lon, circle(lat, lon, km)) for eid, name, lat, lon, km in TARGETS}
    name_to_eid = {name: eid for eid, name, *_ in TARGETS}

    # --- JSON
    files = sorted(p for p in ENTITIES_DIR.glob("*.json") if not p.name.endswith(".bak"))
    changed, applied = set(), set()
    parsed = {}
    for p in files:
        data = json.load(open(p, encoding="utf-8"))
        parsed[p] = data
        for ent in data:
            eid = name_to_eid.get(ent.get("name_original"))
            if eid is None:
                continue
            _name, lat, lon, geom = geoms[eid]
            ent["capital_lat"] = lat
            ent["capital_lon"] = lon
            ent["boundary_geojson"] = geom
            ent["boundary_source"] = "approximate_circle"
            ent["boundary_aourednik_name"] = None
            ent["boundary_aourednik_year"] = None
            ent["boundary_aourednik_precision"] = None
            ent["boundary_ne_iso_a3"] = None
            applied.add(ent["name_original"])
            changed.add(p)

    missing = set(name_to_eid) - applied
    if missing:
        print("ERROR: not found in JSON:", missing)
        return 2

    # --- prod SQL (idempotent)
    lines = [
        "-- Close suggestion #82: distinct Daju/Tunjur geometry. Idempotent.",
        "BEGIN;",
    ]
    for eid, (_name, lat, lon, geom) in geoms.items():
        gj = json.dumps(geom).replace("'", "''")
        lines.append(
            f"UPDATE geo_entities SET capital_lat={lat}, capital_lon={lon}, "
            f"boundary_geojson='{gj}', "
            f"boundary_geom=ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON('{gj}')),3)), "
            f"boundary_source='approximate_circle', boundary_aourednik_name=NULL, "
            f"boundary_aourednik_year=NULL, boundary_aourednik_precision=NULL, boundary_ne_iso_a3=NULL "
            f"WHERE id={eid};"
        )
    lines.append("SELECT id, name_original, capital_lat, capital_lon, boundary_source, "
                 "md5(boundary_geojson) AS geom_md5 FROM geo_entities WHERE id IN (1032,1033) ORDER BY id;")
    lines.append("COMMIT;")
    sql = "\n".join(lines) + "\n"

    print("Daju circle @ (12.7,24.2), Tunjur circle @ (14.5,24.4) — distinct.")
    print(f"JSON entities updated: {sorted(applied)} in {len(changed)} files.")

    if args.dry_run:
        print("DRY-RUN: no writes.")
        return 0

    for p in changed:
        text = json.dumps(parsed[p], ensure_ascii=False, indent=2).replace("\n", "\r\n")
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
    with open(SQL_OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write(sql)
    print(f"Wrote {len(changed)} JSON files + {SQL_OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
