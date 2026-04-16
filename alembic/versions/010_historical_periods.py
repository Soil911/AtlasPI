"""Create historical_periods table for structured historical epochs.

Revision ID: 010_historical_periods
Revises: 009_ai_suggestions
Create Date: 2026-04-16

v6.27 Historical Periods — structured epochs/ages like Bronze Age,
Classical Antiquity, Edo Period, etc. Queryable by year, region,
and period_type.

ETHICS: periodizations are historiographic constructs, not objective
facts. The `region` field ensures Eurocentric periodizations don't
apply globally (e.g., "Middle Ages" is Europe-specific). The
`historiographic_note` field captures scholarly debates.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "010_historical_periods"
down_revision: Union[str, None] = "009_ai_suggestions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "historical_periods",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("name_lang", sa.String(length=10), nullable=False, server_default="en"),
        sa.Column("slug", sa.String(length=200), nullable=False, unique=True),
        sa.Column("name_native", sa.String(length=200), nullable=True),
        sa.Column("name_native_lang", sa.String(length=10), nullable=True),
        sa.Column("period_type", sa.String(length=50), nullable=False, server_default="period"),
        sa.Column("region", sa.String(length=50), nullable=False, server_default="global"),
        sa.Column("year_start", sa.Integer(), nullable=False),
        sa.Column("year_end", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("historiographic_note", sa.Text(), nullable=True),
        sa.Column("alternative_names", sa.Text(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.8"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="confirmed"),
        sa.Column("sources", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_periods_confidence_range",
        ),
        sa.CheckConstraint(
            "year_end IS NULL OR year_end >= year_start",
            name="ck_periods_year_order",
        ),
    )
    op.create_index("ix_periods_name", "historical_periods", ["name"])
    op.create_index("ix_periods_year_range", "historical_periods", ["year_start", "year_end"])
    op.create_index("ix_periods_region", "historical_periods", ["region"])
    op.create_index("ix_periods_period_type", "historical_periods", ["period_type"])
    op.create_index("ix_periods_slug", "historical_periods", ["slug"])


def downgrade() -> None:
    op.drop_index("ix_periods_slug", "historical_periods")
    op.drop_index("ix_periods_period_type", "historical_periods")
    op.drop_index("ix_periods_region", "historical_periods")
    op.drop_index("ix_periods_year_range", "historical_periods")
    op.drop_index("ix_periods_name", "historical_periods")
    op.drop_table("historical_periods")
