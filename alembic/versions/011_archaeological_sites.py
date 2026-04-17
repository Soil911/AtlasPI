"""Create archaeological_sites table for UNESCO/ruins/monuments.

Revision ID: 011_archaeological_sites
Revises: 010_historical_periods
Create Date: 2026-04-17

v6.37 Archaeological Sites — point-located material sites (Pompeii,
Stonehenge, Chichen Itza, Angkor Wat, Petra, Uluru, ecc.). Distinct
from GeoEntity (political state with boundary) and HistoricalCity
(urban center with political life).

ETHICS: nome originale primario (Uluru, non "Ayers Rock"). Nomi
coloniali in name_variants con context. unesco_id e unesco_year
esplicitano UNESCO tier.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "011_archaeological_sites"
down_revision: Union[str, None] = "010_historical_periods"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "archaeological_sites",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name_original", sa.String(length=500), nullable=False),
        sa.Column("name_original_lang", sa.String(length=10), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("date_start", sa.Integer(), nullable=True),
        sa.Column("date_end", sa.Integer(), nullable=True),
        sa.Column("site_type", sa.String(length=50), nullable=False, server_default="ruins"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("unesco_id", sa.String(length=50), nullable=True),
        sa.Column("unesco_year", sa.Integer(), nullable=True),
        sa.Column("entity_id", sa.Integer(), sa.ForeignKey("geo_entities.id"), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.7"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="confirmed"),
        sa.Column("ethical_notes", sa.Text(), nullable=True),
        sa.Column("sources", sa.Text(), nullable=True),
        sa.Column("name_variants", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_arch_sites_confidence_range",
        ),
        sa.CheckConstraint(
            "latitude >= -90.0 AND latitude <= 90.0",
            name="ck_arch_sites_lat_range",
        ),
        sa.CheckConstraint(
            "longitude >= -180.0 AND longitude <= 180.0",
            name="ck_arch_sites_lon_range",
        ),
    )
    op.create_index("ix_arch_sites_name", "archaeological_sites", ["name_original"])
    op.create_index("ix_arch_sites_entity_id", "archaeological_sites", ["entity_id"])
    op.create_index("ix_arch_sites_years", "archaeological_sites", ["date_start", "date_end"])
    op.create_index("ix_arch_sites_site_type", "archaeological_sites", ["site_type"])
    op.create_index("ix_arch_sites_unesco", "archaeological_sites", ["unesco_id"])


def downgrade() -> None:
    op.drop_index("ix_arch_sites_unesco", "archaeological_sites")
    op.drop_index("ix_arch_sites_site_type", "archaeological_sites")
    op.drop_index("ix_arch_sites_years", "archaeological_sites")
    op.drop_index("ix_arch_sites_entity_id", "archaeological_sites")
    op.drop_index("ix_arch_sites_name", "archaeological_sites")
    op.drop_table("archaeological_sites")
