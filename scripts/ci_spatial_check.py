"""CI-only PostGIS spatial check — audit Wave 2, finding #6.

Esercita il path spaziale REALE dell'app (`ST_Intersects(boundary_geom, envelope)`
in `_apply_bbox_filter`) contro PostGIS vero, via l'endpoint pubblico
`/v1/entities?bbox=`. La suite pytest gira su SQLite (dove `contains`/`bbox`
sono no-op), quindi questa classe di bug — incluso il difetto dell'indice GiST
di Wave 2.1 — non era catturabile. Questo script colma il buco.

NON è un test pytest (di proposito): così `tests/conftest.py`, che forza
`DATABASE_URL=sqlite`, non viene caricato. Gira in CI nel job postgres dopo
`alembic upgrade head`. Skippa (exit 0) se DATABASE_URL non è PostgreSQL.

Strategia: inserisce 2 entità con polygon noto (un quadrato sull'Europa, uno sul
Giappone) SENZA capitale (così il match passa SOLO per boundary_geom, non per il
fallback capital-point), fa il backfill di boundary_geom come la migration 019,
poi verifica che una bbox europea restituisca l'entità Europa e NON quella
Giappone. Pulisce sempre le 2 entità di test.
"""
import json
import os
import sys

# Disabilita dipendenze non necessarie prima di importare l'app.
os.environ.setdefault("AUTO_SEED", "false")
os.environ.setdefault("REDIS_URL", "")
os.environ.setdefault("ATLASPI_ADMIN_TOKEN", "ci-spatial-check")

from sqlalchemy import text  # noqa: E402

from src.db.database import SessionLocal, is_postgres  # noqa: E402

if not is_postgres:
    print("SKIP: DATABASE_URL non è PostgreSQL — lo spatial check richiede PostGIS.")
    sys.exit(0)

from fastapi.testclient import TestClient  # noqa: E402

from src.db.models import GeoEntity  # noqa: E402
from src.main import app  # noqa: E402

EUROPE = {"type": "Polygon", "coordinates": [[[0, 45], [5, 45], [5, 50], [0, 50], [0, 45]]]}
JAPAN = {"type": "Polygon", "coordinates": [[[135, 35], [140, 35], [140, 40], [135, 40], [135, 35]]]}
NAMES = ("__ci_spatial_europe__", "__ci_spatial_japan__")


def main() -> int:
    db = SessionLocal()
    errors: list[str] = []
    try:
        # Cleanup difensivo di eventuali run precedenti.
        db.query(GeoEntity).filter(GeoEntity.name_original.in_(NAMES)).delete(synchronize_session=False)
        db.commit()

        for name, geom in ((NAMES[0], EUROPE), (NAMES[1], JAPAN)):
            db.add(GeoEntity(
                name_original=name, name_original_lang="en", entity_type="kingdom",
                year_start=1000, confidence_score=0.9, status="confirmed",
                boundary_geojson=json.dumps(geom),
            ))  # capital_* lasciati NULL di proposito → match solo via boundary_geom
        db.commit()

        # Backfill boundary_geom come la migration 019 / il boot guard.
        db.execute(text(
            "UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract("
            "ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3)) "
            "WHERE name_original IN (:a, :b)"
        ), {"a": NAMES[0], "b": NAMES[1]})
        db.commit()

        ids = {
            e.name_original: e.id
            for e in db.query(GeoEntity).filter(GeoEntity.name_original.in_(NAMES)).all()
        }
        if len(ids) != 2:
            print(f"FAIL: setup — attese 2 entità, trovate {len(ids)}")
            return 1

        client = TestClient(app)  # niente `with` → nessun lifespan (no re-seed/migrate)
        # bbox europea: deve includere Europa, escludere Giappone.
        r = client.get("/v1/entities?bbox=-1,44,6,51&limit=500&exclude_geometry=true")
        if r.status_code != 200:
            print(f"FAIL: /v1/entities?bbox= → {r.status_code}: {r.text[:200]}")
            return 1
        got = {e["id"] for e in r.json().get("entities", [])}
        europe_in = ids[NAMES[0]] in got
        japan_in = ids[NAMES[1]] in got
        print(f"bbox(Europe) → europe_in={europe_in} japan_in={japan_in}")
        if not europe_in:
            errors.append("entità Europa NON restituita da una bbox europea (ST_Intersects rotto o boundary_geom non indicizzato/popolato)")
        if japan_in:
            errors.append("entità Giappone restituita da una bbox europea (filtro spaziale errato)")
    finally:
        db.query(GeoEntity).filter(GeoEntity.name_original.in_(NAMES)).delete(synchronize_session=False)
        db.commit()
        db.close()

    if errors:
        print("PostGIS SPATIAL CHECK FAILED:")
        for e in errors:
            print("  -", e)
        return 1
    print("PostGIS spatial check PASSED — ST_Intersects(boundary_geom) funziona via /v1/entities?bbox=")
    return 0


if __name__ == "__main__":
    sys.exit(main())
