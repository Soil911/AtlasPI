"""Initial schema — all tables for AtlasPI v5.8.0.

Revision ID: 001_initial
Revises: None
Create Date: 2026-04-12

Creates:
- geo_entities: entita' geopolitiche storiche con coordinate e confini
- name_variants: varianti di nome multilingua (ETHICS-001)
- territory_changes: cambi territoriali con tipo esplicito (ETHICS-002)
- sources: fonti bibliografiche

Compatibile con SQLite (dev) e PostgreSQL (prod).
Usa batch mode su SQLite per ALTER TABLE.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- geo_entities ---
    op.create_table(
        "geo_entities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name_original", sa.String(length=500), nullable=False),
        sa.Column("name_original_lang", sa.String(length=10), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("year_start", sa.Integer(), nullable=False),
        sa.Column("year_end", sa.Integer(), nullable=True),
        sa.Column("capital_name", sa.String(length=500), nullable=True),
        sa.Column("capital_lat", sa.Float(), nullable=True),
        sa.Column("capital_lon", sa.Float(), nullable=True),
        sa.Column("boundary_geojson", sa.Text(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("ethical_notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_confidence_range",
        ),
    )
    op.create_index("ix_geo_entities_name_original", "geo_entities", ["name_original"])
    op.create_index("ix_geo_entities_year_range", "geo_entities", ["year_start", "year_end"])
    op.create_index("ix_geo_entities_status", "geo_entities", ["status"])
    op.create_index("ix_geo_entities_entity_type", "geo_entities", ["entity_type"])
    op.create_index("ix_geo_entities_confidence", "geo_entities", ["confidence_score"])

    # --- name_variants ---
    op.create_table(
        "name_variants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("lang", sa.String(length=10), nullable=False),
        sa.Column("period_start", sa.Integer(), nullable=True),
        sa.Column("period_end", sa.Integer(), nullable=True),
        sa.Column("context", sa.String(length=500), nullable=True),
        sa.Column("source", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["entity_id"], ["geo_entities.id"]),
    )
    op.create_index("ix_name_variants_name", "name_variants", ["name"])
    op.create_index("ix_name_variants_lang", "name_variants", ["lang"])
    op.create_index("ix_name_variants_entity_id", "name_variants", ["entity_id"])

    # --- territory_changes ---
    op.create_table(
        "territory_changes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("region", sa.String(length=500), nullable=False),
        sa.Column("change_type", sa.String(length=30), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("population_affected", sa.Integer(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["entity_id"], ["geo_entities.id"]),
    )
    op.create_index("ix_territory_changes_entity_id", "territory_changes", ["entity_id"])
    op.create_index("ix_territory_changes_year", "territory_changes", ["year"])
    op.create_index("ix_territory_changes_change_type", "territory_changes", ["change_type"])

    # --- sources ---
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("citation", sa.String(length=1000), nullable=False),
        sa.Column("url", sa.String(length=2000), nullable=True),
        sa.Column("source_type", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["entity_id"], ["geo_entities.id"]),
    )
    op.create_index("ix_sources_entity_id", "sources", ["entity_id"])
    op.create_index("ix_sources_source_type", "sources", ["source_type"])


def downgrade() -> None:
    op.drop_table("sources")
    op.drop_table("territory_changes")
    op.drop_table("name_variants")
    op.drop_table("geo_entities")
