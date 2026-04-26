"""Add pg_trgm extension + GIN trigram indexes for /v1/search/fuzzy.

Revision ID: 018_pg_trgm_fuzzy_search
Revises: 017_composite_index_entities
Create Date: 2026-04-26

Performance fix for AI Co-Founder suggestion #70: /v1/search/fuzzy averaging
909ms (max 1421ms) over 175 req/day. Root cause: O(n) Python SequenceMatcher
scan over all ~1038 entities + variants on every query.

Fix: PostgreSQL `pg_trgm` extension provides trigram similarity at the index
level. GIN trigram indexes on `geo_entities.name_original` and
`name_variants.name` let the planner pre-filter candidates with a single
index scan. The existing Python scoring (ETHICS-001 bonuses, parens
weighting, token-prefix bonus) is applied to the candidate set only,
preserving ranking semantics while eliminating the linear scan.

Note: in production l'extension `pg_trgm` e i due indici GIN risultano gia'
creati out-of-band (probabilmente in una sessione manuale precedente).
La migration usa CREATE EXTENSION IF NOT EXISTS / CREATE INDEX IF NOT EXISTS
con gli stessi nomi presenti in `pg_indexes` (ix_geo_entities_name_trgm,
ix_name_variants_name_trgm) → idempotente. Su un DB nuovo o senza pg_trgm
l'effetto e' completo; su prod la migration e' un no-op che pero' allinea
lo schema-as-code allo stato reale.

Compatibile con:
  * PostgreSQL (prod) — extension + indici creati o gia' presenti.
  * SQLite (dev/test) — saltato. Il fallback Python full-scan resta in uso.

ETHICS-001: l'indice e' solo un acceleratore di candidate filtering. Il
bonus +0.10 per match sul name_original e' preservato nel re-rank Python a
valle del filter.
"""

from typing import Sequence, Union

from alembic import op


revision: str = "018_pg_trgm_fuzzy_search"
down_revision: Union[str, None] = "017_composite_index_entities"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_postgres() -> bool:
    bind = op.get_bind()
    return bind.dialect.name == "postgresql"


def upgrade() -> None:
    if not _is_postgres():
        return

    # pg_trgm e' bundled con PostgreSQL — non serve installare nulla.
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # I nomi degli indici corrispondono a quelli gia' creati out-of-band
    # in produzione (vedi pg_indexes), quindi IF NOT EXISTS lo rende un
    # no-op pulito.
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_geo_entities_name_trgm
            ON geo_entities
            USING gin (name_original gin_trgm_ops)
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_name_variants_name_trgm
            ON name_variants
            USING gin (name gin_trgm_ops)
        """
    )


def downgrade() -> None:
    if not _is_postgres():
        return
    op.execute("DROP INDEX IF EXISTS ix_name_variants_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_geo_entities_name_trgm")
    # Lascia stare l'extension — potrebbe essere usata da altre cose.
