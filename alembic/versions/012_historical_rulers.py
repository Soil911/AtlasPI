"""Create historical_rulers table for emperors/kings/sultans biographies.

Revision ID: 012_historical_rulers
Revises: 011_archaeological_sites
Create Date: 2026-04-17

v6.38 Historical Rulers — structured biographies of historical sovereigns.
Distinct from HistoricalEvent (event records) and GeoEntity (state records).

ETHICS-001: name_original in native script; ETHICS-002: violence explicit.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "012_historical_rulers"
down_revision: Union[str, None] = "011_archaeological_sites"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "historical_rulers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name_original", sa.String(length=500), nullable=False),
        sa.Column("name_original_lang", sa.String(length=10), nullable=False),
        sa.Column("name_regnal", sa.String(length=500), nullable=True),
        sa.Column("birth_year", sa.Integer(), nullable=True),
        sa.Column("death_year", sa.Integer(), nullable=True),
        sa.Column("reign_start", sa.Integer(), nullable=True),
        sa.Column("reign_end", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.Integer(), sa.ForeignKey("geo_entities.id"), nullable=True),
        sa.Column("entity_name_fallback", sa.String(length=500), nullable=True),
        sa.Column("region", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("dynasty", sa.String(length=200), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.7"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="confirmed"),
        sa.Column("ethical_notes", sa.Text(), nullable=True),
        sa.Column("sources", sa.Text(), nullable=True),
        sa.Column("name_variants", sa.Text(), nullable=True),
        sa.Column("notable_events", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_rulers_confidence_range",
        ),
        sa.CheckConstraint(
            "birth_year IS NULL OR death_year IS NULL OR birth_year <= death_year",
            name="ck_rulers_birth_before_death",
        ),
        sa.CheckConstraint(
            "reign_start IS NULL OR reign_end IS NULL OR reign_start <= reign_end",
            name="ck_rulers_reign_order",
        ),
    )
    op.create_index("ix_rulers_name", "historical_rulers", ["name_original"])
    op.create_index("ix_rulers_entity_id", "historical_rulers", ["entity_id"])
    op.create_index("ix_rulers_reign", "historical_rulers", ["reign_start", "reign_end"])
    op.create_index("ix_rulers_region", "historical_rulers", ["region"])


def downgrade() -> None:
    op.drop_index("ix_rulers_region", "historical_rulers")
    op.drop_index("ix_rulers_reign", "historical_rulers")
    op.drop_index("ix_rulers_entity_id", "historical_rulers")
    op.drop_index("ix_rulers_name", "historical_rulers")
    op.drop_table("historical_rulers")
