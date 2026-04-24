"""Add composite index on geo_entities(status, year_start, year_end).

Revision ID: 017_composite_index_entities
Revises: 016_capital_history
Create Date: 2026-04-24

Performance fix for suggestion #68: /v1/entities slow on unfiltered queries.

The existing indexes are:
  - ix_geo_entities_year_range: (year_start, year_end)
  - ix_geo_entities_status: (status)

A composite (status, year_start, year_end) index lets the planner satisfy the
most common query pattern — "active non-deprecated entities in a year range" —
with a single index scan instead of two separate index lookups merged via bitmap.

Specifically: list_entities always filters status != 'deprecated', then
optionally filters by year_start <= year AND (year_end IS NULL OR year_end >= year).
The composite index covers both predicates in order.

CONCURRENTLY creation: PostgreSQL only. Alembic does not support CONCURRENTLY
natively, so we use op.execute() with the raw DDL. The migration is not
transactional for this index (CREATE INDEX CONCURRENTLY cannot run in a txn).
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "017_composite_index_entities"
down_revision = "016_capital_history"
branch_labels = None
depends_on = None

INDEX_NAME = "ix_geo_entities_status_year_composite"


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        # CONCURRENTLY avoids table lock during index build on production.
        # Must be run outside of a transaction — Alembic wraps in BEGIN by default,
        # so we close the transaction first.
        op.execute("COMMIT")
        op.execute(
            f"CREATE INDEX CONCURRENTLY IF NOT EXISTS {INDEX_NAME} "
            f"ON geo_entities (status, year_start, year_end)"
        )
    else:
        # SQLite / other: plain index (no CONCURRENTLY support needed)
        op.create_index(
            INDEX_NAME,
            "geo_entities",
            ["status", "year_start", "year_end"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        op.execute(f"DROP INDEX IF EXISTS {INDEX_NAME}")
    else:
        op.drop_index(INDEX_NAME, table_name="geo_entities")
