"""external_source_records polymorphic mirror table (ADR-010 / audit R8).

Revision ID: 020_external_source_records
Revises: 019_boundary_geom_postgis
Create Date: 2026-05-13

Aggiunge una tabella polymorphic `external_source_records` che mirrora
le citazioni serializzate come JSON-blob su 6 tabelle:
HistoricalCity, TradeRoute, DynastyChain, ArchaeologicalSite,
HistoricalRuler, HistoricalLanguage.

Il JSON resta canonico. Questa tabella e' un mirror queryable popolato
via scripts/sync_source_records.py (manual run).

Schema:
  - id            SERIAL PK
  - parent_type   VARCHAR(50)   NOT NULL  ('city'|'route'|'chain'|'site'|'ruler'|'language')
  - parent_id     INTEGER       NOT NULL
  - citation      VARCHAR(1000) NOT NULL
  - url           VARCHAR(2000) NULL
  - source_type   VARCHAR(30)   NOT NULL DEFAULT 'secondary'
  - created_at    VARCHAR(50)   NOT NULL  (ISO 8601)
  - UNIQUE(parent_type, parent_id, citation)

Indici:
  - ix_source_records_parent          (parent_type, parent_id)
  - ix_source_records_citation        (citation)
  - ix_source_records_source_type     (source_type)

Compatibile con PostgreSQL e SQLite. Idempotente (IF NOT EXISTS).

ETHICS-005-analogy: il source_type mantiene la tassonomia (primary /
secondary / academic / oral_tradition / archaeological / indirect_reference)
per non degradare le fonti non-occidentali (oral_tradition,
archaeological — vedi ETHICS-008).
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "020_external_source_records"
down_revision: str | None = "019_boundary_geom_postgis"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "external_source_records",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("parent_type", sa.String(50), nullable=False),
        sa.Column("parent_id", sa.Integer, nullable=False),
        sa.Column("citation", sa.String(1000), nullable=False),
        sa.Column("url", sa.String(2000), nullable=True),
        sa.Column("source_type", sa.String(30), nullable=False, server_default="secondary"),
        sa.Column("created_at", sa.String(50), nullable=False),
        sa.UniqueConstraint(
            "parent_type", "parent_id", "citation",
            name="uq_source_records_parent_citation",
        ),
        if_not_exists=True,
    )

    op.create_index(
        "ix_source_records_parent",
        "external_source_records",
        ["parent_type", "parent_id"],
        if_not_exists=True,
    )
    op.create_index(
        "ix_source_records_citation",
        "external_source_records",
        ["citation"],
        if_not_exists=True,
    )
    op.create_index(
        "ix_source_records_source_type",
        "external_source_records",
        ["source_type"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("ix_source_records_source_type", table_name="external_source_records", if_exists=True)
    op.drop_index("ix_source_records_citation", table_name="external_source_records", if_exists=True)
    op.drop_index("ix_source_records_parent", table_name="external_source_records", if_exists=True)
    op.drop_table("external_source_records", if_exists=True)
