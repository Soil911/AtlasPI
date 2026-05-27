"""Models: FeedbackSubmission (Phase G1).

Tabella per raccogliere feedback su entita'/eventi/citta' da:
- Umani (UI widget)
- Agenti AI (via MCP tool)
- Bot programmatici (via REST API)

ETHICS-FEEDBACK: il feedback NON modifica direttamente i dati. Va in
stato `pending` e richiede review umana (o auto-acceptance solo per
metadata-fix se submitter ha reputation >= 0.9).

Per i feedback su contenuti storici (year_end, boundary, conquista vs
succession, ecc.) la review umana e' SEMPRE richiesta — sono decisioni
con impatto etico (CLAUDE.md: "Governance etica durante lo sviluppo").
"""

from __future__ import annotations

from sqlalchemy import Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base

# Categorie di feedback supportate (string enum applicato a livello applicativo,
# non DB enum per portabilita' SQLite/PG).
FEEDBACK_CATEGORIES = {
    "incorrect_data",      # campo X ha valore sbagliato
    "missing_source",      # entita' ha bisogno di una citation
    "bias_report",          # rappresentazione biasata (ETHICS concern)
    "boundary_dispute",    # il polygon e' impreciso
    "missing_entity",      # entita' che dovrebbe esserci non c'e'
    "translation_error",   # nome variant errato/mancante
    "ethics_concern",       # ETHICS-violation potenziale
    "other",               # cattura-tutto, da triagare
}

FEEDBACK_STATUSES = {
    "pending",
    "under_review",
    "accepted",
    "rejected",
    "duplicate",
    "ethics_escalated",
}

SUBMITTER_TYPES = {
    "human",
    "ai_agent",
    "bot",
    "anonymous",
}


class FeedbackSubmission(Base):
    """Feedback record per una entita'/evento/citta'.

    Vedi alembic/versions/021_feedback_submissions.py per schema completo.
    """

    __tablename__ = "feedback_submissions"
    __table_args__ = (
        Index("ix_feedback_status", "status"),
        Index("ix_feedback_entity", "entity_id"),
        Index("ix_feedback_category", "category"),
        Index("ix_feedback_submitter_type", "submitter_type"),
        Index("ix_feedback_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[str] = mapped_column(String(50), nullable=False)

    # Cosa (almeno uno tra entity_id / event_id / city_id dovrebbe essere settato,
    # ma non e' enforced a livello DB — la categoria 'missing_entity' puo' avere tutti null)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    event_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    city_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    field_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    category: Mapped[str] = mapped_column(String(40), nullable=False)

    # Chi
    submitter_type: Mapped[str] = mapped_column(String(20), nullable=False)
    submitter_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    submitter_reputation: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Contenuto
    current_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    citation: Mapped[str | None] = mapped_column(Text, nullable=True)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Triage
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    reviewed_by: Mapped[str | None] = mapped_column(String(256), nullable=True)
    reviewed_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Outcome
    applied_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    applied_in_version: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Anti-spam (hash IP per privacy)
    client_ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    def to_public_dict(self) -> dict:
        """Serializza in dict per API response (esclude PII)."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "entity_id": self.entity_id,
            "event_id": self.event_id,
            "city_id": self.city_id,
            "field_name": self.field_name,
            "category": self.category,
            "submitter_type": self.submitter_type,
            # submitter_id mostrato solo se non e' un email/PII
            "submitter_id": self._safe_submitter_id(),
            "submitter_reputation": round(self.submitter_reputation, 2),
            "current_value": self.current_value,
            "suggested_value": self.suggested_value,
            "citation": self.citation,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "status": self.status,
            "reviewed_at": self.reviewed_at,
            "review_notes": self.review_notes,
            "applied_at": self.applied_at,
            "applied_in_version": self.applied_in_version,
        }

    def _safe_submitter_id(self) -> str | None:
        """Maschera email/PII; mostra solo agent names o handle pubblici."""
        if not self.submitter_id:
            return None
        # Se sembra email, mostra solo dominio
        if "@" in self.submitter_id and "." in self.submitter_id:
            domain = self.submitter_id.rsplit("@", 1)[1]
            return f"***@{domain}"
        return self.submitter_id
