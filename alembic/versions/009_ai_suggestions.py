"""Create ai_suggestions table for the Co-Founder Dashboard.

Revision ID: 009_ai_suggestions
Revises: 008_date_precision
Create Date: 2026-04-16

v6.16 AI Co-Founder Dashboard — persistent table for AI-generated
suggestions. The analysis agent populates rows; the founder reviews
them via the /admin/brief dashboard.

ETHICS: suggestions are purely about data coverage and quality. They
do NOT prescribe a specific cultural or political perspective.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "009_ai_suggestions"
down_revision: Union[str, None] = "008_date_precision"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_suggestions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("detail_json", sa.Text(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("source", sa.String(length=20), nullable=False, server_default="auto"),
        sa.Column("created_at", sa.String(length=50), nullable=False),
        sa.Column("reviewed_at", sa.String(length=50), nullable=True),
        sa.Column("review_note", sa.Text(), nullable=True),
    )
    op.create_index("ix_ai_suggestions_status", "ai_suggestions", ["status"])
    op.create_index("ix_ai_suggestions_priority", "ai_suggestions", ["priority"])
    op.create_index("ix_ai_suggestions_category", "ai_suggestions", ["category"])
    op.create_index("ix_ai_suggestions_created", "ai_suggestions", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_ai_suggestions_created", "ai_suggestions")
    op.drop_index("ix_ai_suggestions_category", "ai_suggestions")
    op.drop_index("ix_ai_suggestions_priority", "ai_suggestions")
    op.drop_index("ix_ai_suggestions_status", "ai_suggestions")
    op.drop_table("ai_suggestions")
