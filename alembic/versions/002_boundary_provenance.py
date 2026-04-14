"""Add boundary provenance columns to geo_entities.

Revision ID: 002_boundary_provenance
Revises: 001_initial
Create Date: 2026-04-14

Adds five nullable columns that document the provenance of each boundary
polygon (ETHICS-005 §2.3):

- boundary_source: enum-like string (historical_map / natural_earth /
  aourednik / academic_source / approximate_generated)
- boundary_aourednik_name: exact feature name from the matched aourednik
  world_*.geojson (reproducibility)
- boundary_aourednik_year: snapshot year used for the match
- boundary_aourednik_precision: 0 (capital-in-polygon) / 1 (fuzzy name) /
  2 (exact name)
- boundary_ne_iso_a3: Natural Earth ISO_A3 code when matched via NE

All columns are nullable — the migration is purely additive. Data
backfill happens via `src.ingestion.sync_boundaries_from_json`
after this migration is applied.

Compatible with SQLite (dev) and PostgreSQL (prod). Uses batch mode on
SQLite so ALTER TABLE ADD COLUMN respects any CHECK constraints.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_boundary_provenance"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("geo_entities") as batch_op:
        batch_op.add_column(sa.Column("boundary_source", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("boundary_aourednik_name", sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column("boundary_aourednik_year", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("boundary_aourednik_precision", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("boundary_ne_iso_a3", sa.String(length=3), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("geo_entities") as batch_op:
        batch_op.drop_column("boundary_ne_iso_a3")
        batch_op.drop_column("boundary_aourednik_precision")
        batch_op.drop_column("boundary_aourednik_year")
        batch_op.drop_column("boundary_aourednik_name")
        batch_op.drop_column("boundary_source")
