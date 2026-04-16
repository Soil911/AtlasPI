"""Add api_request_logs table for analytics.

Revision ID: 007_api_request_logs
Revises: 006_dynasty_chains
Create Date: 2026-04-16

v6.12 API analytics — logs every API request (path, method, status,
response_time_ms, client_ip, user_agent) for the /admin/analytics dashboard.

Tutto additivo. Rollback: drop api_request_logs.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "007_api_request_logs"
down_revision: Union[str, None] = "006_dynasty_chains"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─── api_request_logs ────────────────────────────────────────────────
    op.create_table(
        "api_request_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("timestamp", sa.String(length=30), nullable=False),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("path", sa.String(length=2000), nullable=False),
        sa.Column("query_string", sa.String(length=2000), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("response_time_ms", sa.Float(), nullable=False),
        sa.Column("client_ip", sa.String(length=45), nullable=False),
        sa.Column("user_agent", sa.String(length=1000), nullable=True),
        sa.Column("referer", sa.String(length=2000), nullable=True),
    )
    op.create_index("ix_api_logs_timestamp", "api_request_logs", ["timestamp"])
    op.create_index("ix_api_logs_path", "api_request_logs", ["path"])
    op.create_index("ix_api_logs_client_ip", "api_request_logs", ["client_ip"])
    op.create_index("ix_api_logs_status_code", "api_request_logs", ["status_code"])


def downgrade() -> None:
    op.drop_table("api_request_logs")
