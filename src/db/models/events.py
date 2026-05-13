"""Models: HistoricalEvent + junctions (entity link + source).

Sub-module di src.db.models (split v6.96.0 / audit R7).

ETHICS-007: terminologia accademica (GENOCIDE, COLONIAL_VIOLENCE, ecc.)
non viene sostituita da eufemismi.
ETHICS-008: eventi silenziati dalle fonti del potere dominante hanno
known_silence=True + silence_reason.
"""

from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.db.enums import EntityStatus, EventRole, SourceType  # noqa: F401
from src.db.models.entities import GeoEntity  # noqa: F401 — relationship target


class HistoricalEvent(Base):
    """Evento storico discreto (battaglia, trattato, epidemia, ecc.).

    ETHICS-007: ogni evento espone chi ha fatto cosa a chi
    (main_actor + event_entity_links.role) con voce attiva.
    ETHICS-008: eventi documentati solo da oralità / archeologia hanno
    known_silence=True + silence_reason.
    """

    __tablename__ = "historical_events"
    __table_args__ = (
        Index("ix_historical_events_year", "year"),
        Index("ix_historical_events_event_type", "event_type"),
        Index("ix_historical_events_status", "status"),
        Index("ix_historical_events_confidence", "confidence_score"),
        Index("ix_historical_events_known_silence", "known_silence"),
        # v6.14: composite index for "on this day" queries.
        Index("ix_historical_events_month_day", "month", "day"),
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_events_confidence_range",
        ),
        CheckConstraint(
            "casualties_low IS NULL OR casualties_high IS NULL OR casualties_low <= casualties_high",
            name="ck_events_casualties_range",
        ),
        # v6.14: date precision constraints.
        CheckConstraint(
            "month IS NULL OR (month >= 1 AND month <= 12)",
            name="ck_events_month_range",
        ),
        CheckConstraint(
            "day IS NULL OR (day >= 1 AND day <= 31)",
            name="ck_events_day_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ETHICS-001 analogy: il nome primario è quello originale/locale.
    name_original: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    name_original_lang: Mapped[str] = mapped_column(String(10), nullable=False)

    # ETHICS-007: EventType enum, no euphemism.
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)

    year: Mapped[int] = mapped_column(Integer, nullable=False)
    year_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # v6.14: date precision layer (sub-annuale opzionale).
    month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # ETHICS: per BCE, date_precision + calendar_note esplicitano che si
    # usa il prolettico gregoriano e il calendario originale è diverso.
    date_precision: Mapped[str | None] = mapped_column(String(20), nullable=True)
    iso_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    calendar_note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    location_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_lon: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ETHICS-007: esplicita CHI ha fatto l'evento.
    main_actor: Mapped[str | None] = mapped_column(String(500), nullable=True)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    # ETHICS-007: range vittime con citazione della stima.
    casualties_low: Mapped[int | None] = mapped_column(Integer, nullable=True)
    casualties_high: Mapped[int | None] = mapped_column(Integer, nullable=True)
    casualties_source: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=EntityStatus.CONFIRMED.value)

    # ETHICS-008: silenzi delle fonti come fatto di prima classe.
    known_silence: Mapped[bool] = mapped_column(nullable=False, default=False)
    silence_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    ethical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    entity_links: Mapped[list[EventEntityLink]] = relationship(
        "EventEntityLink", back_populates="event", cascade="all, delete-orphan"
    )
    sources: Mapped[list[EventSource]] = relationship(
        "EventSource", back_populates="event", cascade="all, delete-orphan"
    )


class EventEntityLink(Base):
    """Junction many-to-many evento ↔ entità con ruolo esplicito.

    ETHICS-007: il ruolo (MAIN_ACTOR / VICTIM / PARTICIPANT / AFFECTED /
    WITNESS / FOUNDED / DISSOLVED) rende leggibile dalla macchina CHI ha
    fatto cosa a CHI.
    """

    __tablename__ = "event_entity_links"
    __table_args__ = (
        Index("ix_event_entity_links_event_id", "event_id"),
        Index("ix_event_entity_links_entity_id", "entity_id"),
        Index("ix_event_entity_links_role", "role"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("historical_events.id"), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("geo_entities.id"), nullable=False)

    # ETHICS-007: ruolo esplicito; default AFFECTED perché è il più neutrale.
    role: Mapped[str] = mapped_column(String(30), nullable=False, default=EventRole.AFFECTED.value)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    event: Mapped[HistoricalEvent] = relationship("HistoricalEvent", back_populates="entity_links")
    entity: Mapped[GeoEntity] = relationship("GeoEntity")


class EventSource(Base):
    """Fonte bibliografica per un evento.

    ETHICS-008: SourceType accetta oral_tradition e archaeological come
    evidence di pari dignità ad academic.
    """

    __tablename__ = "event_sources"
    __table_args__ = (
        Index("ix_event_sources_event_id", "event_id"),
        Index("ix_event_sources_source_type", "source_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("historical_events.id"), nullable=False)

    citation: Mapped[str] = mapped_column(String(1000), nullable=False)
    url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False, default=SourceType.SECONDARY.value)

    event: Mapped[HistoricalEvent] = relationship("HistoricalEvent", back_populates="sources")
