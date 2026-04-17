"""Create historical_languages table — geocoded language records.

Revision ID: 013_historical_languages
Revises: 012_historical_rulers
Create Date: 2026-04-17

v6.44 Historical Languages — tracks languages as geocoded records with
period of use. Distinct from GeoEntity (political state) and
HistoricalCity (urban center) — languages cross political boundaries.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "013_historical_languages"
down_revision: Union[str, None] = "012_historical_rulers"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "historical_languages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name_original", sa.String(length=200), nullable=False),
        sa.Column("name_original_lang", sa.String(length=10), nullable=False),
        sa.Column("iso_code", sa.String(length=10), nullable=True),
        sa.Column("family", sa.String(length=100), nullable=True),
        sa.Column("script", sa.String(length=100), nullable=True),
        sa.Column("center_lat", sa.Float(), nullable=True),
        sa.Column("center_lon", sa.Float(), nullable=True),
        sa.Column("region_name", sa.String(length=200), nullable=False),
        sa.Column("period_start", sa.Integer(), nullable=True),
        sa.Column("period_end", sa.Integer(), nullable=True),
        sa.Column("vitality_status", sa.String(length=30), nullable=False, server_default="extinct"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.7"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="confirmed"),
        sa.Column("ethical_notes", sa.Text(), nullable=True),
        sa.Column("sources", sa.Text(), nullable=True),
        sa.Column("name_variants", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_lang_confidence_range",
        ),
        sa.CheckConstraint(
            "center_lat IS NULL OR (center_lat >= -90.0 AND center_lat <= 90.0)",
            name="ck_lang_lat_range",
        ),
        sa.CheckConstraint(
            "center_lon IS NULL OR (center_lon >= -180.0 AND center_lon <= 180.0)",
            name="ck_lang_lon_range",
        ),
    )
    op.create_index("ix_lang_name", "historical_languages", ["name_original"])
    op.create_index("ix_lang_period", "historical_languages", ["period_start", "period_end"])
    op.create_index("ix_lang_region", "historical_languages", ["region_name"])
    op.create_index("ix_lang_family", "historical_languages", ["family"])
    op.create_index("ix_lang_iso", "historical_languages", ["iso_code"])


def downgrade() -> None:
    op.drop_index("ix_lang_iso", "historical_languages")
    op.drop_index("ix_lang_family", "historical_languages")
    op.drop_index("ix_lang_region", "historical_languages")
    op.drop_index("ix_lang_period", "historical_languages")
    op.drop_index("ix_lang_name", "historical_languages")
    op.drop_table("historical_languages")
