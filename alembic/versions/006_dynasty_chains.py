"""Add dynasty_chains + chain_links tables.

Revision ID: 006_dynasty_chains
Revises: 005_cities_and_routes
Create Date: 2026-04-15

v6.5 DynastyChain layer — relazioni successorie tra entità geopolitiche
con transition_type esplicito (CONQUEST / SUCCESSION / DECOLONIZATION).

Crea due tabelle:
  * dynasty_chains  — catena successoria (es. "Roman Power Center",
                      "Chinese Imperial Dynasties", "Inca → Peru").
  * chain_links     — junction chain ↔ geo_entity con sequence_order +
                      transition_year + transition_type + is_violent.

Tutto additivo. geo_entities toccata solo come target di FK in chain_links.

ETHICS-002/003 enforcement: il transition_type rende esplicito CHE COSA è
successo tra entità (CONQUEST violenta vs SUCCESSION dinastica vs
DECOLONIZATION). Niente "transition" generico che maschera violenze.

Rollback: drop chain_links → dynasty_chains.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "006_dynasty_chains"
down_revision: Union[str, None] = "005_cities_and_routes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─── dynasty_chains ──────────────────────────────────────────────────
    op.create_table(
        "dynasty_chains",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("name_lang", sa.String(length=10), nullable=False, server_default="en"),
        sa.Column("chain_type", sa.String(length=20), nullable=False),
        sa.Column("region", sa.String(length=200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "confidence_score", sa.Float(), nullable=False, server_default="0.7"
        ),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="confirmed"
        ),
        sa.Column("ethical_notes", sa.Text(), nullable=True),
        sa.Column("sources", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_chains_confidence_range",
        ),
    )
    op.create_index("ix_dynasty_chains_name", "dynasty_chains", ["name"])
    op.create_index(
        "ix_dynasty_chains_chain_type", "dynasty_chains", ["chain_type"]
    )
    op.create_index("ix_dynasty_chains_region", "dynasty_chains", ["region"])
    op.create_index("ix_dynasty_chains_status", "dynasty_chains", ["status"])

    # ─── chain_links (junction) ──────────────────────────────────────────
    op.create_table(
        "chain_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "chain_id", sa.Integer(),
            sa.ForeignKey("dynasty_chains.id"), nullable=False,
        ),
        sa.Column(
            "entity_id", sa.Integer(),
            sa.ForeignKey("geo_entities.id"), nullable=False,
        ),
        sa.Column("sequence_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("transition_year", sa.Integer(), nullable=True),
        sa.Column("transition_type", sa.String(length=30), nullable=True),
        sa.Column(
            "is_violent", sa.Boolean(), nullable=False, server_default=sa.false(),
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("ethical_notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_chain_links_chain_id", "chain_links", ["chain_id"])
    op.create_index("ix_chain_links_entity_id", "chain_links", ["entity_id"])
    op.create_index(
        "ix_chain_links_sequence", "chain_links",
        ["chain_id", "sequence_order"],
    )
    op.create_index(
        "ix_chain_links_transition_type", "chain_links", ["transition_type"]
    )


def downgrade() -> None:
    op.drop_table("chain_links")
    op.drop_table("dynasty_chains")
