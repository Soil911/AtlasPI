"""Modelli ORM per AtlasPI.

ETHICS: Ogni modello riflette le decisioni etiche documentate in docs/ethics/.
I nomi usano name_original come campo primario (ETHICS-001).
I cambi territoriali richiedono change_type esplicito (ETHICS-002).
I territori contestati hanno status 'disputed' (ETHICS-003).

Compatibilita' database:
- Tutti i tipi sono compatibili con SQLite e PostgreSQL.
- String senza lunghezza esplicita: VARCHAR senza limite (SQLite ignora, PostgreSQL usa TEXT).
- String(N): VARCHAR(N) su entrambi.
- boundary_geojson e' Text per ora; in futuro sara' PostGIS Geometry (ADR-001).
"""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.db.enums import EntityStatus, EventRole, EventType, SourceType  # noqa: F401


class GeoEntity(Base):
    """Entità geopolitica storica."""

    __tablename__ = "geo_entities"
    __table_args__ = (
        Index("ix_geo_entities_year_range", "year_start", "year_end"),
        Index("ix_geo_entities_status", "status"),
        Index("ix_geo_entities_entity_type", "entity_type"),
        Index("ix_geo_entities_confidence", "confidence_score"),
        CheckConstraint("confidence_score >= 0.0 AND confidence_score <= 1.0", name="ck_confidence_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ETHICS: il nome primario è quello originale/locale (ETHICS-001)
    name_original: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    name_original_lang: Mapped[str] = mapped_column(String(10), nullable=False)

    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    year_start: Mapped[int] = mapped_column(Integer, nullable=False)
    year_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    capital_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    capital_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    capital_lon: Mapped[float | None] = mapped_column(Float, nullable=True)

    # PostGIS-ready: questo campo e' Text (JSON serializzato) per compatibilita' SQLite.
    # In produzione PostgreSQL+PostGIS, sara' migrato a una colonna Geometry(MULTIPOLYGON, 4326).
    # La migrazione aggiungera' un indice spaziale GiST sulla colonna Geometry.
    # Vedi ADR-001 per il piano di migrazione PostGIS.
    boundary_geojson: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ETHICS-005: il campo boundary_source documenta la tier di origine del
    # poligono (historical_map / natural_earth / aourednik / academic_source /
    # approximate_generated). Un utente accademico DEVE poter distinguere un
    # confine reale da uno generato senza aprire il boundary_geojson.
    # Migration 002_boundary_provenance.
    boundary_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Tracciamento aourednik per riproducibilita' scientifica (ETHICS-005 §3.2).
    boundary_aourednik_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    boundary_aourednik_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    boundary_aourednik_precision: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Tracciamento Natural Earth: ISO_A3 del paese matchato.
    boundary_ne_iso_a3: Mapped[str | None] = mapped_column(String(3), nullable=True)

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    # ETHICS: i territori contestati devono avere status='disputed' (ETHICS-003)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=EntityStatus.CONFIRMED.value)

    ethical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    name_variants: Mapped[list[NameVariant]] = relationship(
        "NameVariant", back_populates="entity", cascade="all, delete-orphan"
    )
    territory_changes: Mapped[list[TerritoryChange]] = relationship(
        "TerritoryChange", back_populates="entity", cascade="all, delete-orphan"
    )
    sources: Mapped[list[Source]] = relationship(
        "Source", back_populates="entity", cascade="all, delete-orphan"
    )


class NameVariant(Base):
    """Variante di nome per un'entità — vedi ETHICS-001."""

    __tablename__ = "name_variants"
    __table_args__ = (
        Index("ix_name_variants_name", "name"),
        Index("ix_name_variants_lang", "lang"),
        Index("ix_name_variants_entity_id", "entity_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("geo_entities.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    lang: Mapped[str] = mapped_column(String(10), nullable=False)
    period_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    period_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    context: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source: Mapped[str | None] = mapped_column(String(500), nullable=True)

    entity: Mapped[GeoEntity] = relationship("GeoEntity", back_populates="name_variants")


class TerritoryChange(Base):
    """Cambio territoriale con tipo esplicito — vedi ETHICS-002.

    ETHICS: ogni cambio territoriale deve avere change_type esplicito.
    Non usare linguaggio che minimizza conquiste violente.
    """

    __tablename__ = "territory_changes"
    __table_args__ = (
        Index("ix_territory_changes_entity_id", "entity_id"),
        Index("ix_territory_changes_year", "year"),
        Index("ix_territory_changes_change_type", "change_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("geo_entities.id"), nullable=False)

    year: Mapped[int] = mapped_column(Integer, nullable=False)
    region: Mapped[str] = mapped_column(String(500), nullable=False)
    # ETHICS: tipi definiti in ETHICS-002 — vedi src/db/enums.py
    change_type: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    population_affected: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    entity: Mapped[GeoEntity] = relationship("GeoEntity", back_populates="territory_changes")


class Source(Base):
    """Fonte bibliografica per un'entità."""

    __tablename__ = "sources"
    __table_args__ = (
        Index("ix_sources_entity_id", "entity_id"),
        Index("ix_sources_source_type", "source_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("geo_entities.id"), nullable=False)

    citation: Mapped[str] = mapped_column(String(1000), nullable=False)
    url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False, default=SourceType.SECONDARY.value)

    entity: Mapped[GeoEntity] = relationship("GeoEntity", back_populates="sources")


# ─── v6.3: Eventi storici — ETHICS-007 + ETHICS-008 ──────────────────────────


class HistoricalEvent(Base):
    """Evento storico discreto (battaglia, trattato, epidemia, ecc.).

    ETHICS-007: ogni evento deve esporre chi ha fatto cosa a chi
    (main_actor + event_entity_links.role) con voce attiva nelle
    descrizioni. Terminologia accademica (GENOCIDE, COLONIAL_VIOLENCE)
    NON viene sostituita da eufemismi.

    ETHICS-008: eventi non documentati dalle fonti del potere dominante
    ma noti da oralità / archeologia / fonti post-hoc sono rappresentati
    esplicitamente con `known_silence = True` + `silence_reason`.
    """

    __tablename__ = "historical_events"
    __table_args__ = (
        Index("ix_historical_events_year", "year"),
        Index("ix_historical_events_event_type", "event_type"),
        Index("ix_historical_events_status", "status"),
        Index("ix_historical_events_confidence", "confidence_score"),
        Index("ix_historical_events_known_silence", "known_silence"),
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_events_confidence_range",
        ),
        CheckConstraint(
            "casualties_low IS NULL OR casualties_high IS NULL OR casualties_low <= casualties_high",
            name="ck_events_casualties_range",
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

    # Relazioni.
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
    # Note etiche per questo specifico link (utile se il ruolo è ambiguo
    # o contestato — es. Tlaxcaltec in 1521 erano MAIN_ACTOR o AFFECTED?).
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    event: Mapped[HistoricalEvent] = relationship("HistoricalEvent", back_populates="entity_links")
    entity: Mapped[GeoEntity] = relationship("GeoEntity")


class EventSource(Base):
    """Fonte bibliografica per un evento.

    ETHICS-008: SourceType accetta oral_tradition e archaeological
    come evidence di pari dignità ad academic.
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
