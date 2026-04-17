"""Create known_dev_ips table — marker per dev IPs da filtrare nell'analytics.

Revision ID: 014_known_dev_ips
Revises: 013_historical_languages
Create Date: 2026-04-17

v6.53 — admin self-service marking per escludere IP dev dalla dashboard
external-only. UI: button "Mark my IP as dev" nella dashboard.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "014_known_dev_ips"
down_revision: Union[str, None] = "013_historical_languages"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "known_dev_ips",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ip", sa.String(length=45), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=True),
        sa.Column("marked_at", sa.String(length=50), nullable=False),
    )
    op.create_index("ix_dev_ips_ip", "known_dev_ips", ["ip"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_dev_ips_ip", "known_dev_ips")
    op.drop_table("known_dev_ips")
