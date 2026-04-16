"""Add date precision columns to historical_events and territory_changes.

Revision ID: 008_date_precision
Revises: 007_api_request_logs
Create Date: 2026-04-16

v6.14 Date Precision Layer — adds sub-annual granularity (month, day,
date_precision, iso_date, calendar_note) to both historical_events and
territory_changes tables. All columns nullable for backward compatibility.

ETHICS: calendar_note field lets us declare when a date uses proleptic
Gregorian and the original calendar was different (Julian, Islamic,
Chinese lunisolar, etc.).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "008_date_precision"
down_revision: Union[str, None] = "007_api_request_logs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─── historical_events: 5 new columns ───────────────────────────────
    op.add_column("historical_events", sa.Column("month", sa.Integer(), nullable=True))
    op.add_column("historical_events", sa.Column("day", sa.Integer(), nullable=True))
    op.add_column("historical_events", sa.Column("date_precision", sa.String(length=20), nullable=True))
    op.add_column("historical_events", sa.Column("iso_date", sa.String(length=20), nullable=True))
    op.add_column("historical_events", sa.Column("calendar_note", sa.String(length=500), nullable=True))

    # Composite index for "on this day" queries.
    op.create_index("ix_historical_events_month_day", "historical_events", ["month", "day"])

    # Check constraints.
    op.create_check_constraint("ck_events_month_range", "historical_events",
                               "month IS NULL OR (month >= 1 AND month <= 12)")
    op.create_check_constraint("ck_events_day_range", "historical_events",
                               "day IS NULL OR (day >= 1 AND day <= 31)")

    # ─── territory_changes: 5 new columns ───────────────────────────────
    op.add_column("territory_changes", sa.Column("month", sa.Integer(), nullable=True))
    op.add_column("territory_changes", sa.Column("day", sa.Integer(), nullable=True))
    op.add_column("territory_changes", sa.Column("date_precision", sa.String(length=20), nullable=True))
    op.add_column("territory_changes", sa.Column("iso_date", sa.String(length=20), nullable=True))
    op.add_column("territory_changes", sa.Column("calendar_note", sa.String(length=500), nullable=True))

    # Check constraints.
    op.create_check_constraint("ck_tc_month_range", "territory_changes",
                               "month IS NULL OR (month >= 1 AND month <= 12)")
    op.create_check_constraint("ck_tc_day_range", "territory_changes",
                               "day IS NULL OR (day >= 1 AND day <= 31)")


def downgrade() -> None:
    # ─── territory_changes ──────────────────────────────────────────────
    op.drop_constraint("ck_tc_day_range", "territory_changes", type_="check")
    op.drop_constraint("ck_tc_month_range", "territory_changes", type_="check")
    op.drop_column("territory_changes", "calendar_note")
    op.drop_column("territory_changes", "iso_date")
    op.drop_column("territory_changes", "date_precision")
    op.drop_column("territory_changes", "day")
    op.drop_column("territory_changes", "month")

    # ─── historical_events ──────────────────────────────────────────────
    op.drop_constraint("ck_events_day_range", "historical_events", type_="check")
    op.drop_constraint("ck_events_month_range", "historical_events", type_="check")
    op.drop_index("ix_historical_events_month_day", "historical_events")
    op.drop_column("historical_events", "calendar_note")
    op.drop_column("historical_events", "iso_date")
    op.drop_column("historical_events", "date_precision")
    op.drop_column("historical_events", "day")
    op.drop_column("historical_events", "month")
