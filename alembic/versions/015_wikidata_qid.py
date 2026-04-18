"""Add wikidata_qid column to geo_entities — audit v4 Fase A.

Revision ID: 015_wikidata_qid
Revises: 014_known_dev_ips
Create Date: 2026-04-18

v6.69 — cross-reference sistematico con Wikidata.

Aggiunge `geo_entities.wikidata_qid` (nullable) + indice per lookup rapido.
Lo schema Q-ID ha formato "Q123456" (lunghezza max osservata 8 cifre; 20 char
dà margine abbondante). Il campo è popolato via `scripts/wikidata_bootstrap.py`
con confidence ≥ 0.85. Le entità senza match sicuro restano NULL.

ETHICS: il Q-ID è un identificatore esterno di riferimento, non un'autorità.
AtlasPI non adotta automaticamente i dati Wikidata — il Q-ID serve a
confronto/drift detection (fase B) + tracciabilità. Le discrepanze vanno
valutate caso per caso (vedi docs/audit/FASE_A_B_HANDOFF.md).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "015_wikidata_qid"
down_revision: Union[str, None] = "014_known_dev_ips"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "geo_entities",
        sa.Column("wikidata_qid", sa.String(length=20), nullable=True),
    )
    op.create_index(
        "ix_geo_entities_wikidata_qid",
        "geo_entities",
        ["wikidata_qid"],
    )


def downgrade() -> None:
    op.drop_index("ix_geo_entities_wikidata_qid", table_name="geo_entities")
    op.drop_column("geo_entities", "wikidata_qid")
