"""Models: HistoricalRuler (imperatori, re, sultani, khagan, presidenti, ...).

Sub-module di src.db.models (split v6.96.0 / audit R7).

ETHICS-001: nome primario in lingua/script originale del sovrano
(武曌, Александр II). Forme latinizzate in name_variants.
ETHICS-002: violenza, genocidi, schiavitù vanno esplicitati nelle
ethical_notes — niente eufemismi.
"""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.db.enums import EntityStatus  # noqa: F401
from src.db.models.entities import GeoEntity  # noqa: F401 — relationship target


class HistoricalRuler(Base):
    """Capi storici: imperatori, re, sultani, khagan, presidenti, dittatori."""

    __tablename__ = "historical_rulers"
    __table_args__ = (
        Index("ix_rulers_name", "name_original"),
        Index("ix_rulers_entity_id", "entity_id"),
        Index("ix_rulers_reign", "reign_start", "reign_end"),
        Index("ix_rulers_region", "region"),
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_rulers_confidence_range",
        ),
        CheckConstraint(
            "birth_year IS NULL OR death_year IS NULL OR birth_year <= death_year",
            name="ck_rulers_birth_before_death",
        ),
        CheckConstraint(
            "reign_start IS NULL OR reign_end IS NULL OR reign_start <= reign_end",
            name="ck_rulers_reign_order",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_original: Mapped[str] = mapped_column(String(500), nullable=False)
    name_original_lang: Mapped[str] = mapped_column(String(10), nullable=False)
    name_regnal: Mapped[str | None] = mapped_column(String(500), nullable=True)

    birth_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    death_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reign_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reign_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    title: Mapped[str] = mapped_column(String(100), nullable=False)

    entity_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("geo_entities.id"), nullable=True
    )
    entity_name_fallback: Mapped[str | None] = mapped_column(String(500), nullable=True)

    region: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    dynasty: Mapped[str | None] = mapped_column(String(200), nullable=True)

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EntityStatus.CONFIRMED.value
    )

    ethical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sources: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    name_variants: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    notable_events: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array

    entity: Mapped[GeoEntity | None] = relationship("GeoEntity")
