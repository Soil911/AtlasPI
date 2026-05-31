"""CI-only PostGIS boundary-collision fence — Wave 2 audit #7.

Runs the REAL boundary collision guard (``detect_boundary_collisions``, which
needs ``ST_Area(boundary_geom)`` and so only works on PostGIS) against a fresh
seed of ``data/entities/*.json``. This is the authoritative half of the fence:
it proves that an empty-DB deploy — the exact thing that used to regress Phase H
— produces 0 super-group collisions on the same Postgres+PostGIS stack as prod.

The fast half (``tests/test_boundary_collisions_json_audit.py``) runs on SQLite
in the normal ``test`` job; this one runs in the ``postgres-migrations`` job
after ``alembic upgrade head``.

NOT a pytest test (on purpose): ``tests/conftest.py`` forces
``DATABASE_URL=sqlite``, where ST_Area is a no-op. Skips (exit 0) if DATABASE_URL
is not PostgreSQL.

Steps: seed entities from JSON -> backfill boundary_geom from boundary_geojson
(same expression as migration 019 / the boot guard) -> run the guard -> fail if
any super-group alert or if the collision-group count exceeds the baseline.
"""
import os
import sys

os.environ.setdefault("AUTO_SEED", "false")
os.environ.setdefault("REDIS_URL", "")
os.environ.setdefault("ATLASPI_ADMIN_TOKEN", "ci-collision-check")

from sqlalchemy import text  # noqa: E402

from src.db.database import SessionLocal, is_postgres  # noqa: E402

if not is_postgres:
    print("SKIP: DATABASE_URL non è PostgreSQL — il collision fence richiede PostGIS.")
    sys.exit(0)

from src.db.models import GeoEntity  # noqa: E402
from src.db.seed import seed_database  # noqa: E402
from src.ingestion.boundary_collision_guard import (  # noqa: E402
    MAX_ALLOWED_COLLISION_GROUPS,
    detect_boundary_collisions,
)


def main() -> int:
    # Fresh seed from the JSON source of truth (no-op if already populated).
    seed_database()

    db = SessionLocal()
    try:
        n = db.query(GeoEntity).count()
        # Backfill boundary_geom from boundary_geojson exactly like migration 019
        # / the boot guard (seed only writes boundary_geojson text).
        db.execute(
            text(
                "UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract("
                "ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3)) "
                "WHERE boundary_geojson IS NOT NULL AND boundary_geom IS NULL"
            )
        )
        db.commit()
        geom_n = db.execute(
            text("SELECT count(*) FROM geo_entities WHERE boundary_geom IS NOT NULL")
        ).scalar()
    finally:
        db.close()

    print(f"Seeded {n} entities, {geom_n} with boundary_geom.")

    result = detect_boundary_collisions()
    if result.get("status") == "skip":
        print(f"SKIP: {result.get('reason')}")
        return 0

    alerts = result.get("super_group_alerts", [])
    total_groups = result.get("total_groups", 0)
    print(
        f"Collision audit: total_groups={total_groups} "
        f"big_groups={result.get('big_groups_count', 0)} "
        f"super_group_alerts={result.get('super_group_alert_count', 0)}"
    )

    errors = []
    if alerts:
        errors.append(f"{len(alerts)} super-group polygon collision(s) — Phase H regression:")
        for a in alerts[:8]:
            errors.append(
                f"  • '{a['boundary_aourednik_name']}' x{a['n_entities']} "
                f"(years {a['year_range'][0]}..{a['year_range'][1]}): {', '.join(a['names'][:5])}"
            )
    if total_groups > MAX_ALLOWED_COLLISION_GROUPS:
        errors.append(
            f"collision-group count {total_groups} exceeds baseline "
            f"{MAX_ALLOWED_COLLISION_GROUPS} — likely ingestion regression."
        )

    if errors:
        print("\nPostGIS COLLISION FENCE FAILED (audit #7):")
        for e in errors:
            print("  -", e)
        print("\nFix: backport per-entity boundaries / reject the super-group label.")
        return 1

    print("PostGIS collision fence PASSED — fresh JSON seed has 0 super-group collisions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
