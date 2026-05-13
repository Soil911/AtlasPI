"""Add boundary_geom PostGIS column + GiST index + backfill (ADR-009 / audit R1).

Revision ID: 019_boundary_geom_postgis
Revises: 018_pg_trgm_fuzzy_search
Create Date: 2026-05-13

Aggiunge una colonna PostGIS `boundary_geom GEOMETRY(MultiPolygon, 4326)`
affianco a `boundary_geojson Text`. Vedi ADR-009 per il rationale completo.

Cosa fa la migration (solo PostgreSQL):

1. `CREATE EXTENSION IF NOT EXISTS postgis` (no-op se gia' presente, e
   sui container postgis/postgis:16-3.4 lo e').
2. `ALTER TABLE geo_entities ADD COLUMN IF NOT EXISTS boundary_geom ...`
3. `CREATE INDEX IF NOT EXISTS ix_geo_entities_boundary_geom ... USING GIST`
4. Backfill: `UPDATE geo_entities SET boundary_geom = ST_Multi(ST_GeomFromGeoJSON(boundary_geojson))`
   - Solo per righe con boundary_geojson valido + ST_IsValid del polygon
   - ST_Multi() wrappa Polygon in MultiPolygon (la colonna e' MultiPolygon)
   - Skip righe con boundary_geom gia' settato (idempotente)

Compatibile con:
  * PostgreSQL (prod, CI postgres-migrations) — completo
  * SQLite (dev/test) — no-op (la colonna non viene mai creata in dev)

Idempotenza:
  La migration usa IF NOT EXISTS ovunque. Pero' il backfill UPDATE puo'
  generare WARN su row con geojson malformato — non e' un fail, e'
  visibile nei log. Riesecuzione produce zero righe aggiornate (WHERE
  boundary_geom IS NULL).

ETHICS-005: la colonna boundary_geom NON sostituisce boundary_geojson
come source-of-truth. boundary_geojson resta il campo canonico
serializzato in /v1/entities response. boundary_geom e' solo un indice
spaziale interno.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "019_boundary_geom_postgis"
down_revision: str | None = "018_pg_trgm_fuzzy_search"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _is_postgres() -> bool:
    bind = op.get_bind()
    return bind.dialect.name == "postgresql"


def upgrade() -> None:
    if not _is_postgres():
        return

    # 1. PostGIS extension (no-op su container postgis/postgis:*).
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # 2. Add column boundary_geom (idempotente con IF NOT EXISTS).
    op.execute(
        """
        ALTER TABLE geo_entities
        ADD COLUMN IF NOT EXISTS boundary_geom geometry(MultiPolygon, 4326)
        """
    )

    # 3. GiST index per spatial queries (ST_Within, ST_Intersects, ST_DWithin).
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_geo_entities_boundary_geom
            ON geo_entities
            USING GIST(boundary_geom)
        """
    )

    # 4. Backfill: popola boundary_geom da boundary_geojson.
    #    - Solo righe con boundary_geom NULL (idempotente).
    #    - Filtro ST_IsValid sul polygon parsato per skippare malformed.
    #    - ST_MakeValid recovery: tentativo di self-intersect repair prima di skip.
    #    - ST_Multi: wrap Polygon → MultiPolygon (la colonna e' MultiPolygon).
    op.execute(
        """
        UPDATE geo_entities
        SET boundary_geom = ST_Multi(
            ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson))
        )
        WHERE boundary_geom IS NULL
          AND boundary_geojson IS NOT NULL
          AND boundary_geojson != ''
          AND boundary_geojson NOT LIKE '%null%'
          AND ST_IsValid(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)))
        """
    )


def downgrade() -> None:
    if not _is_postgres():
        return

    op.execute("DROP INDEX IF EXISTS ix_geo_entities_boundary_geom")
    op.execute("ALTER TABLE geo_entities DROP COLUMN IF EXISTS boundary_geom")
    # Lascia stare l'extension postgis — usata da altre future colonne.
