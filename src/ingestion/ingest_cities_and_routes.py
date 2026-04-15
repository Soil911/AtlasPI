"""Idempotent ingestion of historical cities and trade routes.

Reads all JSON files in ``data/cities/`` and ``data/routes/`` and inserts
only those that aren't already present.

Dedup keys:
    * HistoricalCity: (name_original, founded_year) — a city with the same
      name and the same founding year is considered the same city.
    * TradeRoute: (name_original, start_year) — same logic.

Entity resolution:
    * City.entity_name_original → GeoEntity.id via a name_original lookup.
      Missing refs are logged but don't block the insert (cities may
      legitimately exist without a parent entity in the DB, e.g.
      stateless or pre-statal cities).
    * Route.waypoint_city_names → HistoricalCity.id via lookup. Cities
      ingested in this same run are visible to the route resolver because
      we flush() between the two passes.

ETHICS-010 sanity:
    A route with ``involves_slavery=True`` MUST have "humans_enslaved"
    in commodities (or a name_variant like "humans-enslaved" — accepted).
    We don't raise on violations but log WARNING so the operator sees
    the mismatch. The CI test suite enforces this invariant strictly.

Usage:
    python -m src.ingestion.ingest_cities_and_routes
"""

from __future__ import annotations

import io
import json
import logging
import sys
from pathlib import Path
from typing import Any

# Windows cp1252 stdout fix for non-latin names
if sys.platform == "win32" and isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except AttributeError:
        pass

from src.config import DATA_DIR
from src.db.database import SessionLocal
from src.db.models import GeoEntity, HistoricalCity, RouteCityLink, TradeRoute

logger = logging.getLogger(__name__)


CITIES_DIR = Path(DATA_DIR) / "cities"
ROUTES_DIR = Path(DATA_DIR) / "routes"


def _load_json_dir(dir_path: Path) -> list[dict[str, Any]]:
    """Load & concatenate all *.json files in a directory."""
    if not dir_path.exists():
        return []
    out: list[dict[str, Any]] = []
    for fp in sorted(dir_path.glob("*.json")):
        try:
            with fp.open(encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, list):
                out.extend(data)
            else:
                logger.warning("File %s non è una lista JSON, skip.", fp)
        except Exception as exc:
            logger.error("Errore lettura %s: %s", fp, exc)
    return out


def ingest_cities() -> dict[str, Any]:
    """Insert cities whose (name_original, founded_year) aren't in DB.

    Returns a dict with {inserted, skipped_existing, total_in_json,
    unresolved_entity_refs}.
    """
    db = SessionLocal()
    try:
        existing = {
            (c.name_original, c.founded_year)
            for c in db.query(
                HistoricalCity.name_original, HistoricalCity.founded_year
            ).all()
        }

        all_cities = _load_json_dir(CITIES_DIR)
        logger.info("Città nei JSON: %d", len(all_cities))

        entity_map = {e.name_original: e.id for e in db.query(GeoEntity).all()}

        inserted = 0
        skipped = 0
        unresolved: list[str] = []

        for c_data in all_cities:
            name = c_data.get("name_original")
            founded = c_data.get("founded_year")
            if not name:
                continue
            if (name, founded) in existing:
                skipped += 1
                continue

            ent_name = c_data.get("entity_name_original")
            entity_id = entity_map.get(ent_name) if ent_name else None
            if ent_name and entity_id is None:
                unresolved.append(f"city={name} → entity={ent_name}")

            city = HistoricalCity(
                name_original=name,
                name_original_lang=c_data.get("name_original_lang", "en"),
                latitude=float(c_data["latitude"]),
                longitude=float(c_data["longitude"]),
                founded_year=founded,
                abandoned_year=c_data.get("abandoned_year"),
                city_type=c_data.get("city_type", "MULTI_PURPOSE"),
                population_peak=c_data.get("population_peak"),
                population_peak_year=c_data.get("population_peak_year"),
                entity_id=entity_id,
                confidence_score=c_data.get("confidence_score", 0.7),
                status=c_data.get("status", "confirmed"),
                ethical_notes=c_data.get("ethical_notes"),
                sources=(
                    json.dumps(c_data["sources"], ensure_ascii=False)
                    if c_data.get("sources")
                    else None
                ),
                name_variants=(
                    json.dumps(c_data["name_variants"], ensure_ascii=False)
                    if c_data.get("name_variants")
                    else None
                ),
            )
            db.add(city)
            inserted += 1

        db.commit()
        logger.info(
            "Ingest città: %d inserite, %d saltate, %d entity-refs non risolti",
            inserted, skipped, len(unresolved),
        )
        if unresolved:
            for ref in unresolved[:10]:
                logger.debug(" unresolved: %s", ref)

        return {
            "inserted": inserted,
            "skipped_existing": skipped,
            "total_in_json": len(all_cities),
            "unresolved_entity_refs": len(unresolved),
        }
    finally:
        db.close()


def ingest_routes() -> dict[str, Any]:
    """Insert routes whose (name_original, start_year) aren't in DB.

    Routes are ingested AFTER cities so that waypoint_city_names can be
    resolved via lookup on the (now-populated) HistoricalCity table.
    """
    db = SessionLocal()
    try:
        existing = {
            (r.name_original, r.start_year)
            for r in db.query(
                TradeRoute.name_original, TradeRoute.start_year
            ).all()
        }

        all_routes = _load_json_dir(ROUTES_DIR)
        logger.info("Rotte nei JSON: %d", len(all_routes))

        city_map = {c.name_original: c.id for c in db.query(HistoricalCity).all()}

        inserted = 0
        skipped = 0
        unresolved_waypoints: list[str] = []
        slavery_flag_mismatches: list[str] = []

        for r_data in all_routes:
            name = r_data.get("name_original")
            start = r_data.get("start_year")
            if not name:
                continue
            if (name, start) in existing:
                skipped += 1
                continue

            commodities = r_data.get("commodities") or []
            involves_slavery = bool(r_data.get("involves_slavery", False))

            # ETHICS-010 sanity: if flagged involves_slavery, commodities
            # should contain "humans_enslaved".
            if involves_slavery and "humans_enslaved" not in commodities:
                slavery_flag_mismatches.append(
                    f"route={name} has involves_slavery=True but 'humans_enslaved' not in commodities"
                )
            # Inverse: if "humans_enslaved" present but flag False, also log.
            if "humans_enslaved" in commodities and not involves_slavery:
                slavery_flag_mismatches.append(
                    f"route={name} has 'humans_enslaved' commodity but involves_slavery=False"
                )

            geometry_val = r_data.get("geometry_geojson")
            if isinstance(geometry_val, (dict, list)):
                geometry_str = json.dumps(geometry_val, ensure_ascii=False)
            elif isinstance(geometry_val, str):
                geometry_str = geometry_val
            else:
                geometry_str = None

            route = TradeRoute(
                name_original=name,
                name_original_lang=r_data.get("name_original_lang", "en"),
                route_type=r_data["route_type"],
                start_year=start,
                end_year=r_data.get("end_year"),
                geometry_geojson=geometry_str,
                commodities=(
                    json.dumps(commodities, ensure_ascii=False) if commodities else None
                ),
                description=r_data.get("description"),
                involves_slavery=involves_slavery,
                confidence_score=r_data.get("confidence_score", 0.6),
                status=r_data.get("status", "confirmed"),
                ethical_notes=r_data.get("ethical_notes"),
                sources=(
                    json.dumps(r_data["sources"], ensure_ascii=False)
                    if r_data.get("sources")
                    else None
                ),
            )

            # Resolve waypoints.
            waypoints = r_data.get("waypoint_city_names") or []
            for i, city_name in enumerate(waypoints):
                city_id = city_map.get(city_name)
                if city_id is None:
                    unresolved_waypoints.append(f"{name}[{i}] → {city_name}")
                    continue
                route.city_links.append(
                    RouteCityLink(
                        city_id=city_id,
                        sequence_order=i,
                        is_terminal=(i == 0 or i == len(waypoints) - 1),
                    )
                )

            db.add(route)
            inserted += 1

        db.commit()
        logger.info(
            "Ingest rotte: %d inserite, %d saltate, %d waypoints non risolti, %d slavery-flag mismatches",
            inserted, skipped, len(unresolved_waypoints), len(slavery_flag_mismatches),
        )
        if unresolved_waypoints:
            for ref in unresolved_waypoints[:10]:
                logger.debug(" unresolved waypoint: %s", ref)
        if slavery_flag_mismatches:
            for m in slavery_flag_mismatches:
                logger.warning(" ETHICS-010 mismatch: %s", m)

        return {
            "inserted": inserted,
            "skipped_existing": skipped,
            "total_in_json": len(all_routes),
            "unresolved_waypoints": len(unresolved_waypoints),
            "slavery_flag_mismatches": len(slavery_flag_mismatches),
        }
    finally:
        db.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    c_res = ingest_cities()
    r_res = ingest_routes()
    print("=== Cities ingest ===")
    print(json.dumps(c_res, indent=2))
    print("=== Routes ingest ===")
    print(json.dumps(r_res, indent=2))


if __name__ == "__main__":
    main()
