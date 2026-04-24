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
    op.create_index(
        INDEX_NAME,
        "geo_entities",
        ["status", "year_start", "year_end"],
        unique=False,
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index(INDEX_NAME, table_name="geo_entities")
