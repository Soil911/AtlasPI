"""Models: HistoricalPeriod (epochs / eras / periodizations).

Sub-module di src.db.models (split v6.96.0 / audit R7).

ETHICS: le periodizzazioni sono costrutti storiografici, non fatti
oggettivi. Ogni periodo dichiara region + historiographic_note +
confidence_score.
"""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


class HistoricalPeriod(Base):
    """Structured historical period / epoch.

    Esempi:
      * "Bronze Age" (global, 3300-1200 BCE)
      * "Classical Antiquity" (Mediterranean, 8th c. BCE - 5th c. CE)
      * "Edo Period" (Japan, 1603-1868)
      * "Warring States Period" (China, -475 - -221)

    ETHICS: la stessa epoca puo' avere definizioni diverse per regioni
    diverse (es. "Middle Ages" in Europa vs "Heian Period" in Giappone).
    """

    __tablename__ = "historical_periods"
    __table_args__ = (
        Index("ix_periods_year_range", "year_start", "year_end"),
        Index("ix_periods_region", "region"),
        Index("ix_periods_period_type", "period_type"),
        Index("ix_periods_slug", "slug"),
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_periods_confidence_range",
        ),
        CheckConstraint(
            "year_end IS NULL OR year_end >= year_start",
            name="ck_periods_year_order",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    name_lang: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    # URL-friendly unique slug.
    slug: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    # Native-language name (es. "江戸時代" per Edo Period).
    name_native: Mapped[str | None] = mapped_column(String(200), nullable=True)
    name_native_lang: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Period type: age / era / period / dynasty / epoch.
    period_type: Mapped[str] = mapped_column(String(50), nullable=False, default="period")

    # Region scope: "global", "europe", "asia_east", "asia_south",
    # "mesoamerica", "near_east", "africa", "oceania", "americas".
    region: Mapped[str] = mapped_column(String(50), nullable=False, default="global")

    year_start: Mapped[int] = mapped_column(Integer, nullable=False)
    year_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    # ETHICS: periodization disputes go here.
    historiographic_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Alternative names / competing periodizations: JSON list.
    alternative_names: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="confirmed")

    sources: Mapped[str | None] = mapped_column(Text, nullable=True)
