"""Add historical_cities + trade_routes + route_city_links tables.

Revision ID: 005_cities_and_routes
Revises: 004_postgis_indexes
Create Date: 2026-04-15

v6.4 Cities + Trade Routes layer — ETHICS-009 (city renaming) +
ETHICS-010 (slave trade commodity explicitness).

Creates three new tables:
  * historical_cities   — centri urbani storici discreti, con propria vita
                          (founded_year, abandoned_year) indipendente dalle
                          entità politiche che li hanno controllati.
  * trade_routes        — rotte commerciali storiche (Silk Road, Trans-
                          Saharan, Trans-Atlantic, Amber, Incense…) con
                          geometria GeoJSON e commodities JSON array.
  * route_city_links    — junction m:n route ↔ city con sequence_order
                          per conservare l'ordine dei waypoints.

Tutti additivi. GeoEntity esistente toccata solo come target di FK
opzionale (historical_cities.entity_id → geo_entities.id).

PostGIS (prod): analogamente a 004, aggiunge indici GiST funzionali su:
  * ST_MakePoint(longitude, latitude)::geography (per /v1/cities?near=…)
  * ST_GeomFromGeoJSON(geometry_geojson) (per /v1/routes?bbox=…)
SQLite (dev): skippa silenziosamente.

Rollback: drop tables in ordine inverso di FK (links → routes/cities).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "005_cities_and_routes"
down_revision: Union[str, None] = "004_postgis_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_postgres() -> bool:
    bind = op.get_bind()
    return bind.dialect.name == "postgresql"


def upgrade() -> None:
    # ─── historical_cities ───────────────────────────────────────────────
    op.create_table(
        "historical_cities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name_original", sa.String(length=500), nullable=False),
        sa.Column("name_original_lang", sa.String(length=10), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("founded_year", sa.Integer(), nullable=True),
        sa.Column("abandoned_year", sa.Integer(), nullable=True),
        sa.Column(
            "city_type", sa.String(length=30), nullable=False,
            server_default="MULTI_PURPOSE",
        ),
        sa.Column("population_peak", sa.Integer(), nullable=True),
        sa.Column("population_peak_year", sa.Integer(), nullable=True),
        sa.Column(
            "entity_id", sa.Integer(),
            sa.ForeignKey("geo_entities.id"), nullable=True,
        ),
        sa.Column(
            "confidence_score", sa.Float(), nullable=False, server_default="0.7",
        ),
        sa.Column(
            "status", sa.String(length=20), nullable=False,
            server_default="confirmed",
        ),
        sa.Column("ethical_notes", sa.Text(), nullable=True),
        sa.Column("sources", sa.Text(), nullable=True),
        sa.Column("name_variants", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_cities_confidence_range",
        ),
        sa.CheckConstraint(
            "population_peak IS NULL OR population_peak >= 0",
            name="ck_cities_population_nonneg",
        ),
    )
    op.create_index(
        "ix_historical_cities_name", "historical_cities", ["name_original"]
    )
    op.create_index(
        "ix_historical_cities_years", "historical_cities",
        ["founded_year", "abandoned_year"],
    )
    op.create_index(
        "ix_historical_cities_city_type", "historical_cities", ["city_type"]
    )
    op.create_index(
        "ix_historical_cities_entity_id", "historical_cities", ["entity_id"]
    )
    op.create_index(
        "ix_historical_cities_confidence", "historical_cities", ["confidence_score"]
    )

    # ─── trade_routes ────────────────────────────────────────────────────
    op.create_table(
        "trade_routes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name_original", sa.String(length=500), nullable=False),
        sa.Column("name_original_lang", sa.String(length=10), nullable=False),
        sa.Column("route_type", sa.String(length=20), nullable=False),
        sa.Column("start_year", sa.Integer(), nullable=True),
        sa.Column("end_year", sa.Integer(), nullable=True),
        sa.Column("geometry_geojson", sa.Text(), nullable=True),
        sa.Column("commodities", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "involves_slavery", sa.Boolean(), nullable=False, server_default=sa.false(),
        ),
        sa.Column(
            "confidence_score", sa.Float(), nullable=False, server_default="0.6",
        ),
        sa.Column(
            "status", sa.String(length=20), nullable=False,
            server_default="confirmed",
        ),
        sa.Column("ethical_notes", sa.Text(), nullable=True),
        sa.Column("sources", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_routes_confidence_range",
        ),
    )
    op.create_index("ix_trade_routes_name", "trade_routes", ["name_original"])
    op.create_index(
        "ix_trade_routes_years", "trade_routes", ["start_year", "end_year"]
    )
    op.create_index(
        "ix_trade_routes_route_type", "trade_routes", ["route_type"]
    )
    op.create_index(
        "ix_trade_routes_confidence", "trade_routes", ["confidence_score"]
    )

    # ─── route_city_links (junction) ─────────────────────────────────────
    op.create_table(
        "route_city_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "route_id", sa.Integer(),
            sa.ForeignKey("trade_routes.id"), nullable=False,
        ),
        sa.Column(
            "city_id", sa.Integer(),
            sa.ForeignKey("historical_cities.id"), nullable=False,
        ),
        sa.Column("sequence_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "is_terminal", sa.Boolean(), nullable=False, server_default=sa.false(),
        ),
    )
    op.create_index(
        "ix_route_city_links_route_id", "route_city_links", ["route_id"]
    )
    op.create_index(
        "ix_route_city_links_city_id", "route_city_links", ["city_id"]
    )
    op.create_index(
        "ix_route_city_links_sequence", "route_city_links",
        ["route_id", "sequence_order"],
    )

    # ─── PostGIS spatial indexes (prod only) ─────────────────────────────
    if _is_postgres():
        # Città: punto singolo, indice geography per /v1/cities?near= (ST_DWithin).
        op.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_historical_cities_point_geog
                ON historical_cities
                USING GIST (
                    (ST_MakePoint(longitude, latitude)::geography)
                )
            """
        )
        # Rotte: LineString/MultiLineString, indice geometry per /v1/routes?bbox=.
        op.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_trade_routes_geom
                ON trade_routes
                USING GIST (
                    ST_GeomFromGeoJSON(geometry_geojson)
                )
                WHERE geometry_geojson IS NOT NULL
            """
        )


def downgrade() -> None:
    if _is_postgres():
        op.execute("DROP INDEX IF EXISTS ix_trade_routes_geom")
        op.execute("DROP INDEX IF EXISTS ix_historical_cities_point_geog")

    op.drop_table("route_city_links")
    op.drop_table("trade_routes")
    op.drop_table("historical_cities")
