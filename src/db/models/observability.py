"""Models: ApiRequestLog + AiSuggestion + KnownDevIp (observability / analytics).

Sub-module di src.db.models (split v6.96.0 / audit R7).

Queste tabelle NON sono parte del dataset storico — sono telemetria
operativa per dashboard analytics + AI co-founder. Sono separate dalle
entità di dominio per chiarezza concettuale.
"""

from __future__ import annotations

from sqlalchemy import Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


class ApiRequestLog(Base):
    """Log entry for every API request. Used by /admin/analytics dashboard.

    Only logs API paths (/v1/*, /health, /admin/*) — static file requests
    are excluded by the middleware to keep the table lean.

    v6.92.3 (audit R10): retention 90 giorni via scripts/prune_old_logs.py +
    src/main.py::_maybe_prune_logs_locked() (Redis lock 24h).
    """

    __tablename__ = "api_request_logs"
    __table_args__ = (
        Index("ix_api_logs_timestamp", "timestamp"),
        Index("ix_api_logs_path", "path"),
        Index("ix_api_logs_client_ip", "client_ip"),
        Index("ix_api_logs_status_code", "status_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    timestamp: Mapped[str] = mapped_column(String(50), nullable=False)  # ISO 8601
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    path: Mapped[str] = mapped_column(String(2000), nullable=False)
    query_string: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_time_ms: Mapped[float] = mapped_column(Float, nullable=False)

    client_ip: Mapped[str] = mapped_column(String(45), nullable=False)  # IPv6 max 45 chars
    user_agent: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    referer: Mapped[str | None] = mapped_column(String(2000), nullable=True)


class AiSuggestion(Base):
    """AI-generated suggestion for the co-founder dashboard.

    L'AI analysis agent popola questa tabella con suggerimenti
    actionable (geographic gaps, temporal gaps, low-confidence entities,
    missing chains, ecc.).

    ETHICS: suggestions about adding entities or events must NOT bias
    the dataset toward any particular cultural perspective.
    """

    __tablename__ = "ai_suggestions"
    __table_args__ = (
        Index("ix_ai_suggestions_status", "status"),
        Index("ix_ai_suggestions_priority", "priority"),
        Index("ix_ai_suggestions_category", "category"),
        Index("ix_ai_suggestions_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Category: geographic_gap, temporal_gap, quality, traffic_pattern,
    # missing_entity, missing_chain, low_confidence
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    detail_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 1=critical, 2=high, 3=medium, 4=low, 5=info
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    # pending, accepted, rejected, implemented
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    # auto (from analysis agent), manual (from human)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="auto")

    created_at: Mapped[str] = mapped_column(String(50), nullable=False)
    reviewed_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class KnownDevIp(Base):
    """IP marcati come 'dev' dall'admin — esclusi dalla dashboard analytics
    external-only. Popolato via `POST /admin/dev-ips/mark-current`.

    Semplice table — nessuna FK, nessun vincolo, solo IP univoci.
    """

    __tablename__ = "known_dev_ips"
    __table_args__ = (
        Index("ix_dev_ips_ip", "ip", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ip: Mapped[str] = mapped_column(String(45), nullable=False)  # IPv6 max 45
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    marked_at: Mapped[str] = mapped_column(String(50), nullable=False)  # ISO 8601
