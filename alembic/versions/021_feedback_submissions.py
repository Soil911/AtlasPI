"""feedback_submissions table — Phase G1.

Revision ID: 021_feedback_submissions
Revises: 020_external_source_records
Create Date: 2026-05-28

Aggiunge la tabella `feedback_submissions` per raccogliere feedback da:
- Umani (UI widget bottone "Segnala")
- Agenti AI (via MCP tool `atlaspi_submit_feedback`)
- Bot programmatici (via POST /v1/feedback REST)

ETHICS-FEEDBACK: il feedback NON modifica direttamente i dati del DB.
Va sempre prima in stato `pending` e richiede review umana o
auto-acceptance se reputation submitter >= 0.9 + sono richieste solo
metadata-level fix (typo, ISBN, formattazione).

Per i feedback su contenuti storici (year_end, boundary, conquista vs
succession, ecc.) la review umana è SEMPRE richiesta — sono decisioni
con impatto etico (vedi CLAUDE.md "Governance etica durante lo sviluppo").

Schema:
  - id                          SERIAL PK
  - created_at                  VARCHAR(50) NOT NULL  (ISO 8601)

  Cosa:
  - entity_id                   INT NULL    FK geo_entities (CASCADE NULL on delete)
  - event_id                    INT NULL    FK historical_events
  - city_id                     INT NULL    FK historical_cities
  - field_name                  VARCHAR(64) NULL   ('year_end', 'boundary_geojson', etc.)
  - category                    VARCHAR(40) NOT NULL  (vedi enum sotto)

  Chi:
  - submitter_type              VARCHAR(20) NOT NULL  ('human'|'ai_agent'|'bot'|'anonymous')
  - submitter_id                VARCHAR(256) NULL    (email | agent name | UA hash)
  - submitter_reputation        FLOAT NOT NULL DEFAULT 0.0   (0.0-1.0)

  Contenuto:
  - current_value               TEXT NULL    (snapshot stato attuale)
  - suggested_value             TEXT NULL    (correzione proposta)
  - citation                    TEXT NULL    (riferimento bibliografico)
  - reasoning                   TEXT NULL    (spiegazione)
  - confidence                  FLOAT NULL   (0.0-1.0 self-reported)

  Triage:
  - status                      VARCHAR(20) NOT NULL DEFAULT 'pending'
                                ('pending'|'under_review'|'accepted'|'rejected'|
                                 'duplicate'|'ethics_escalated')
  - reviewed_by                 VARCHAR(256) NULL
  - reviewed_at                 VARCHAR(50) NULL
  - review_notes                TEXT NULL

  Outcome:
  - applied_at                  VARCHAR(50) NULL
  - applied_in_version          VARCHAR(32) NULL    ('6.99.75', ecc.)

  Anti-spam / rate-limiting:
  - client_ip_hash              VARCHAR(64) NULL    (sha256 dell'IP — privacy)
  - user_agent                  VARCHAR(500) NULL

Indici:
  - ix_feedback_status                    (status)
  - ix_feedback_entity                    (entity_id)
  - ix_feedback_category                  (category)
  - ix_feedback_submitter_type            (submitter_type)
  - ix_feedback_created                   (created_at)

Cosa NON c'è (a posta):
- DELETE on FK cascade — vogliamo preservare il feedback anche se l'entità
  viene rinominata o splittata. ID nullable invece.
- Reputation history table — la metto solo se serve nel G2.
- Voting up/down — può venire dopo se utile.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "021_feedback_submissions"
down_revision: str | None = "020_external_source_records"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "feedback_submissions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.String(50), nullable=False),
        # Cosa
        sa.Column("entity_id", sa.Integer, nullable=True),
        sa.Column("event_id", sa.Integer, nullable=True),
        sa.Column("city_id", sa.Integer, nullable=True),
        sa.Column("field_name", sa.String(64), nullable=True),
        sa.Column("category", sa.String(40), nullable=False),
        # Chi
        sa.Column("submitter_type", sa.String(20), nullable=False),
        sa.Column("submitter_id", sa.String(256), nullable=True),
        sa.Column("submitter_reputation", sa.Float, nullable=False, server_default="0.0"),
        # Contenuto
        sa.Column("current_value", sa.Text, nullable=True),
        sa.Column("suggested_value", sa.Text, nullable=True),
        sa.Column("citation", sa.Text, nullable=True),
        sa.Column("reasoning", sa.Text, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        # Triage
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reviewed_by", sa.String(256), nullable=True),
        sa.Column("reviewed_at", sa.String(50), nullable=True),
        sa.Column("review_notes", sa.Text, nullable=True),
        # Outcome
        sa.Column("applied_at", sa.String(50), nullable=True),
        sa.Column("applied_in_version", sa.String(32), nullable=True),
        # Anti-spam
        sa.Column("client_ip_hash", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        if_not_exists=True,
    )

    op.create_index(
        "ix_feedback_status",
        "feedback_submissions",
        ["status"],
        if_not_exists=True,
    )
    op.create_index(
        "ix_feedback_entity",
        "feedback_submissions",
        ["entity_id"],
        if_not_exists=True,
    )
    op.create_index(
        "ix_feedback_category",
        "feedback_submissions",
        ["category"],
        if_not_exists=True,
    )
    op.create_index(
        "ix_feedback_submitter_type",
        "feedback_submissions",
        ["submitter_type"],
        if_not_exists=True,
    )
    op.create_index(
        "ix_feedback_created",
        "feedback_submissions",
        ["created_at"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("ix_feedback_created", table_name="feedback_submissions", if_exists=True)
    op.drop_index("ix_feedback_submitter_type", table_name="feedback_submissions", if_exists=True)
    op.drop_index("ix_feedback_category", table_name="feedback_submissions", if_exists=True)
    op.drop_index("ix_feedback_entity", table_name="feedback_submissions", if_exists=True)
    op.drop_index("ix_feedback_status", table_name="feedback_submissions", if_exists=True)
    op.drop_table("feedback_submissions", if_exists=True)
