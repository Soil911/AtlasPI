"""Add capital_history table — audit v4 Round 13.

Revision ID: 016_capital_history
Revises: 015_wikidata_qid
Create Date: 2026-04-19

v6.84 — Capital history table per polities long-duration con capitali multiple.

Pattern emerso da audit v2 + v4: entità come Ottoman (Söğüt → Bursa → Edirne →
Istanbul), Mughal (Agra → Delhi), Ming (Nanjing → Beijing), Song (Kaifeng →
Lin'an), Solomonic Ethiopia (Tegulet → corte itinerante → Gondar → Addis
Abeba) hanno avuto multiple capitali nel tempo. Il campo strutturato
`capital_name/lat/lon` espone solo UNA capitale (la "iconica"), creando
anacronismi quando un agente AI chiede "capital of X in year Y".

Schema:
- entity_id: FK a geo_entities (CASCADE delete)
- name: nome della capitale
- lat, lon: coordinate
- year_start, year_end: periodo in cui questa città è capitale (year_end
  NULL = ancora capitale o ultima capitale)
- ordering: int per sorting (utile quando year ranges si sovrappongono,
  es. capitali estive/invernali)
- notes: opzionale (es. "capitale di estate", "sede corte itinerante")

ETHICS-001: i nomi capital seguono ETHICS-001 (lingua locale primary).
ETHICS-002: per polities con corte mobile (Mali, Solomonic Ethiopia
medieval) si può usare nome="court itinerant" + lat/lon NULL.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "016_capital_history"
down_revision: Union[str, None] = "015_wikidata_qid"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "capital_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lon", sa.Float(), nullable=True),
        sa.Column("year_start", sa.Integer(), nullable=False),
        sa.Column("year_end", sa.Integer(), nullable=True),
        sa.Column("ordering", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["entity_id"], ["geo_entities.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_capital_history_entity_id",
        "capital_history",
        ["entity_id"],
    )
    op.create_index(
        "ix_capital_history_year_range",
        "capital_history",
        ["year_start", "year_end"],
    )


def downgrade() -> None:
    op.drop_index("ix_capital_history_year_range", table_name="capital_history")
    op.drop_index("ix_capital_history_entity_id", table_name="capital_history")
    op.drop_table("capital_history")
