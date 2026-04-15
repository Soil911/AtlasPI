"""Add PostGIS GiST indexes for spatial query performance.

Revision ID: 004_postgis_indexes
Revises: 003_historical_events
Create Date: 2026-04-15

v6.3.2 PostGIS deep work — indici spaziali per /v1/nearby + /v1/entities bbox.

Aggiunge tre indici per accelerare le query spaziali in produzione:

  1. **`ix_geo_entities_capital_geog`** — indice GiST funzionale su
     `ST_MakePoint(capital_lon, capital_lat)::geography`. Rende
     `ST_DWithin()` su capitali sub-millisecondo invece di full-scan.

  2. **`ix_geo_entities_boundary_geom`** — indice GiST su
     `ST_GeomFromGeoJSON(boundary_geojson)` per accelerare
     `ST_Intersects()` su bbox query (`/v1/entities?bbox=...`).
     Espressione filtrata su WHERE boundary_geojson IS NOT NULL per
     evitare di indicizzare NULL.

  3. **`ix_event_links_entity_year`** — composite (entity_id, year) tramite
     join historical_events.year, accelera /v1/entities/{id}/events.
     (Non spaziale ma frequente.) Rimosso: la struttura attuale del JSON
     non rende facile materializzare year in event_entity_links senza
     denormalizzazione. Skippato in v6.3.2 — riconsidereremo se
     /v1/entities/{id}/events mostra latenze problematiche.

ETHICS-006: nessun impatto sulla guardia capital-in-polygon. Gli indici
sono solo acceleratori di query, non modificano la semantica.

Compatibile con:
  * PostgreSQL + PostGIS (prod) — gli indici vengono creati
  * SQLite (dev) — gli indici vengono SKIPPATI silenziosamente.
    SQLite non ha PostGIS quindi non c'è nulla da indicizzare.
"""

from typing import Sequence, Union

from alembic import op


revision: str = "004_postgis_indexes"
down_revision: Union[str, None] = "003_historical_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_postgres() -> bool:
    """Check whether the current Alembic context is running on PostgreSQL.

    SQLite (dev) non supporta CREATE INDEX su funzioni PostGIS, quindi
    saltiamo silenziosamente. PostGIS deep work è strettamente prod-only.
    """
    bind = op.get_bind()
    return bind.dialect.name == "postgresql"


def upgrade() -> None:
    if not _is_postgres():
        # SQLite dev: nulla da fare. Niente PostGIS, niente indici GiST.
        return

    # ─── 1. GiST su capital point (geography) ──────────────────────────
    # Accelera /v1/nearby (ST_DWithin su capital_lat/lon).
    # Espressione = ST_MakePoint(lon, lat)::geography.
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_geo_entities_capital_geog
            ON geo_entities
            USING GIST (
                (ST_MakePoint(capital_lon, capital_lat)::geography)
            )
            WHERE capital_lat IS NOT NULL AND capital_lon IS NOT NULL
        """
    )

    # ─── 2. GiST su boundary GeoJSON ──────────────────────────────────
    # Accelera /v1/entities con filtro bbox via ST_Intersects.
    # boundary_geojson è TEXT contenente GeoJSON; ST_GeomFromGeoJSON()
    # lo materializza in geometria PostGIS al volo.
    #
    # NB: questo è un EXPRESSION INDEX. La query DEVE usare la stessa
    # espressione `ST_GeomFromGeoJSON(boundary_geojson)` perché PostgreSQL
    # possa usare l'indice. Vedi src/api/routes/entities.py per l'uso.
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_geo_entities_boundary_geom
            ON geo_entities
            USING GIST (
                ST_GeomFromGeoJSON(boundary_geojson)
            )
            WHERE boundary_geojson IS NOT NULL
        """
    )


def downgrade() -> None:
    if not _is_postgres():
        return
    op.execute("DROP INDEX IF EXISTS ix_geo_entities_boundary_geom")
    op.execute("DROP INDEX IF EXISTS ix_geo_entities_capital_geog")
