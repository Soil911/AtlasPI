"""Fix boundary_geom GiST index — name collision 004 vs 019 (Wave 2.1 / audit).

Revision ID: 022_fix_boundary_geom_gist_index
Revises: 021_feedback_submissions
Create Date: 2026-05-29

Contesto (audit Wave 2, finding DB #5 — verificato in produzione 2026-05-29):

La migration 004_postgis_indexes crea `ix_geo_entities_boundary_geom` come
EXPRESSION index su `ST_GeomFromGeoJSON(boundary_geojson)` (usato da
_where_was_postgis). La migration 019_boundary_geom_postgis tentava di creare
un indice OMONIMO sulla COLONNA `boundary_geom`, ma `CREATE INDEX IF NOT EXISTS`
con nome già occupato → no-op silenzioso. Risultato in prod: la colonna
boundary_geom è SENZA indice GiST, quindi _apply_bbox_filter
(ST_Intersects(boundary_geom, ...)) e _apply_contains_filter
(ST_Contains(boundary_geom, ...)) in src/api/routes/_entities_helpers.py girano
in sequential scan — l'esatto O(n) che ADR-009 voleva eliminare.

Snapshot indici prod PRIMA del fix:
  ix_geo_entities_boundary_geom       GIST (st_geomfromgeojson(boundary_geojson))  [004, expression — TENERE]
  ix_geo_entities_boundary_geom_temp  GIST (st_geomfromgeojson(boundary_geojson))  [duplicato one-off — DROP]
  (nessun indice sulla colonna boundary_geom)

Fix:
  1. CREATE INDEX ix_geo_entities_boundary_geom_gist su GIST(boundary_geom) — nome distinto.
  2. DROP ix_geo_entities_boundary_geom_temp — duplicato ridondante dell'expression
     index (residuo di scripts/sites_fk_backfill_v2.sql, mai referenziato in query).
  3. ix_geo_entities_boundary_geom (004, expression) resta INTATTO — serve a
     _where_was_postgis (ST_Contains(ST_GeomFromGeoJSON(boundary_geojson), ...)).

Solo PostgreSQL. SQLite (dev/test) → no-op. Idempotente (IF NOT EXISTS / IF EXISTS).
CREATE INDEX non-CONCURRENTLY: gira nella transazione Alembic e su ~1038 righe il
build è sub-secondo, lock trascurabile.

ADR-009: nessun cambio di semantica. boundary_geojson resta source-of-truth;
boundary_geom + il suo indice sono solo acceleratori spaziali interni.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "022_fix_boundary_geom_gist_index"
down_revision: str | None = "021_feedback_submissions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _is_postgres() -> bool:
    bind = op.get_bind()
    return bind.dialect.name == "postgresql"


def upgrade() -> None:
    if not _is_postgres():
        # SQLite dev/test: niente PostGIS, niente da indicizzare.
        return

    # 1. Indice GiST sulla COLONNA boundary_geom (nome distinto da 004).
    #    Questo è ciò che 019 voleva creare e che le query bbox/contains
    #    (ST_Intersects/ST_Contains su boundary_geom) richiedono.
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_geo_entities_boundary_geom_gist
            ON geo_entities
            USING GIST (boundary_geom)
        """
    )

    # 2. Rimuovi il duplicato ridondante dell'expression index (residuo
    #    di scripts/sites_fk_backfill_v2.sql). Identico per definizione a
    #    ix_geo_entities_boundary_geom → solo spreco di spazio e write-cost.
    op.execute("DROP INDEX IF EXISTS ix_geo_entities_boundary_geom_temp")

    # NB: ix_geo_entities_boundary_geom (004, expression su
    #     ST_GeomFromGeoJSON(boundary_geojson)) NON va droppato: è usato da
    #     _where_was_postgis. Resta invariato.

    # 3. ANALYZE così il planner aggiorna subito le statistiche e usa il
    #    nuovo indice senza attendere l'autovacuum (cross-check GPT-5.5).
    #    ANALYZE è ammesso dentro la transazione Alembic (a differenza di VACUUM).
    op.execute("ANALYZE geo_entities")


def downgrade() -> None:
    if not _is_postgres():
        return

    # Rimuovi solo l'indice colonna creato qui. Il _temp era spazzatura
    # (duplicato) e non viene ricreato di proposito.
    op.execute("DROP INDEX IF EXISTS ix_geo_entities_boundary_geom_gist")
