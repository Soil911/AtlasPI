"""Add historical_events + event_entity_links + event_sources tables.

Revision ID: 003_historical_events
Revises: 002_boundary_provenance
Create Date: 2026-04-15

v6.3 Events layer — ETHICS-007 + ETHICS-008.

Creates three new tables:
  * historical_events     — eventi storici discreti (battaglie, trattati,
                            epidemie, genocidi, eruzioni, carestie, ecc.)
  * event_entity_links    — junction many-to-many evento ↔ entità con
                            ruolo esplicito (MAIN_ACTOR, VICTIM, ecc.)
  * event_sources         — citazioni bibliografiche per eventi

Tutti i campi sono additivi; GeoEntity esistente non viene toccata.

Compatible con SQLite (dev) e PostgreSQL (prod).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003_historical_events"
down_revision: Union[str, None] = "002_boundary_provenance"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─── historical_events ───────────────────────────────────────────────
    op.create_table(
        "historical_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name_original", sa.String(length=500), nullable=False),
        sa.Column("name_original_lang", sa.String(length=10), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("year_end", sa.Integer(), nullable=True),
        sa.Column("location_name", sa.String(length=500), nullable=True),
        sa.Column("location_lat", sa.Float(), nullable=True),
        sa.Column("location_lon", sa.Float(), nullable=True),
        sa.Column("main_actor", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("casualties_low", sa.Integer(), nullable=True),
        sa.Column("casualties_high", sa.Integer(), nullable=True),
        sa.Column("casualties_source", sa.String(length=1000), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="confirmed"),
        sa.Column("known_silence", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("silence_reason", sa.Text(), nullable=True),
        sa.Column("ethical_notes", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_events_confidence_range",
        ),
        sa.CheckConstraint(
            "casualties_low IS NULL OR casualties_high IS NULL "
            "OR casualties_low <= casualties_high",
            name="ck_events_casualties_range",
        ),
    )
    op.create_index("ix_historical_events_name_original", "historical_events", ["name_original"])
    op.create_index("ix_historical_events_year", "historical_events", ["year"])
    op.create_index("ix_historical_events_event_type", "historical_events", ["event_type"])
    op.create_index("ix_historical_events_status", "historical_events", ["status"])
    op.create_index("ix_historical_events_confidence", "historical_events", ["confidence_score"])
    op.create_index("ix_historical_events_known_silence", "historical_events", ["known_silence"])

    # ─── event_entity_links ───────────────────────────────────────────────
    op.create_table(
        "event_entity_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("historical_events.id"), nullable=False),
        sa.Column("entity_id", sa.Integer(), sa.ForeignKey("geo_entities.id"), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False, server_default="AFFECTED"),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_event_entity_links_event_id", "event_entity_links", ["event_id"])
    op.create_index("ix_event_entity_links_entity_id", "event_entity_links", ["entity_id"])
    op.create_index("ix_event_entity_links_role", "event_entity_links", ["role"])

    # ─── event_sources ────────────────────────────────────────────────────
    op.create_table(
        "event_sources",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("historical_events.id"), nullable=False),
        sa.Column("citation", sa.String(length=1000), nullable=False),
        sa.Column("url", sa.String(length=2000), nullable=True),
        sa.Column("source_type", sa.String(length=30), nullable=False, server_default="secondary"),
    )
    op.create_index("ix_event_sources_event_id", "event_sources", ["event_id"])
    op.create_index("ix_event_sources_source_type", "event_sources", ["source_type"])


def downgrade() -> None:
    op.drop_index("ix_event_sources_source_type", table_name="event_sources")
    op.drop_index("ix_event_sources_event_id", table_name="event_sources")
    op.drop_table("event_sources")

    op.drop_index("ix_event_entity_links_role", table_name="event_entity_links")
    op.drop_index("ix_event_entity_links_entity_id", table_name="event_entity_links")
    op.drop_index("ix_event_entity_links_event_id", table_name="event_entity_links")
    op.drop_table("event_entity_links")

    op.drop_index("ix_historical_events_known_silence", table_name="historical_events")
    op.drop_index("ix_historical_events_confidence", table_name="historical_events")
    op.drop_index("ix_historical_events_status", table_name="historical_events")
    op.drop_index("ix_historical_events_event_type", table_name="historical_events")
    op.drop_index("ix_historical_events_year", table_name="historical_events")
    op.drop_index("ix_historical_events_name_original", table_name="historical_events")
    op.drop_table("historical_events")
