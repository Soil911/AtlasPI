"""Drop known_dev_ips — dashboard analytics interna rimossa (v6.99.115).

Revision ID: 023_drop_known_dev_ips
Revises: 022_fix_boundary_geom_gist_index
Create Date: 2026-07-03

Contesto: la dashboard analytics interna (/admin/analytics + /admin/dev-ips)
è stata rimossa in favore di Matomo self-hosted (stats.cra-srl.com, siteId 2,
cookieless). La tabella known_dev_ips serviva SOLO al filtro external-only di
quella dashboard (v6.52/v6.53) — nessun altro consumatore (verificato:
apply_external_filter viveva in analytics.py, rimosso nello stesso commit).
La telemetria API (api_request_logs) NON è toccata: alimenta l'AI Co-Founder
(analyzer failed_searches) e gli agent-insights.

Il downgrade ricrea la tabella vuota (i contenuti erano pochi IP di sviluppo,
non dati storici — perderli è accettabile e documentato).
"""

import sqlalchemy as sa

from alembic import op

revision = "023_drop_known_dev_ips"
down_revision = "022_fix_boundary_geom_gist_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS known_dev_ips")


def downgrade() -> None:
    op.create_table(
        "known_dev_ips",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ip", sa.String(45), nullable=False),
        sa.Column("label", sa.String(200), nullable=True),
        sa.Column("marked_at", sa.String(50), nullable=False),
    )
    op.create_index("ix_dev_ips_ip", "known_dev_ips", ["ip"], unique=True)
