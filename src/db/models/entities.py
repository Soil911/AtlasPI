"""Models: GeoEntity + dirette dipendenti (capital, name variants, territory changes, sources).

Sub-module di src.db.models (split v6.96.0 / audit R7).

ETHICS-001: i nomi usano name_original come campo primario.
ETHICS-002: i cambi territoriali richiedono change_type esplicito.
ETHICS-003: i territori contestati hanno status='disputed'.
ETHICS-005: boundary_source documenta la provenance (audit v6.1).
"""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Float, ForeignKey, Index, Integer, String, Text, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.db.enums import EntityStatus, SourceType  # noqa: F401


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

    # boundary_geojson: Text (JSON serializzato), canonico per response.
    # boundary_geom (non mappato qui — vedi ADR-009): colonna PostGIS
    # materializzata via Alembic 019, usata per query spaziali indicizzate.
    boundary_geojson: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ETHICS-005: provenance del polygon. Migration 002_boundary_provenance.
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

    # v6.69 audit v4 Fase A: Wikidata Q-ID di riferimento.
    # ETHICS: il Q-ID serve per cross-reference/drift detection, non come
    # fonte autoritativa.
    wikidata_qid: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)

    name_variants: Mapped[list[NameVariant]] = relationship(
        "NameVariant", back_populates="entity", cascade="all, delete-orphan"
    )
    territory_changes: Mapped[list[TerritoryChange]] = relationship(
        "TerritoryChange", back_populates="entity", cascade="all, delete-orphan"
    )
    sources: Mapped[list[Source]] = relationship(
        "Source", back_populates="entity", cascade="all, delete-orphan"
    )
    capital_history: Mapped[list[CapitalHistory]] = relationship(
        "CapitalHistory", back_populates="entity", cascade="all, delete-orphan",
        order_by="CapitalHistory.year_start"
    )


# ETHICS-013 (principio 3 — trasparenza dell'incertezza): un'entità con
# confidence_score < 0.5 NON può essere status='confirmed'. Sarebbe un "dato
# certo inventato" — esattamente ciò che CLAUDE.md dichiara peggiore
# dell'incertezza onesta. Forziamo 'confirmed' → 'uncertain' a livello dato,
# così seed/ingest/patch e ogni futuro write-path ORM non possono far divergere
# confidence e status (audit Wave 2 #4/#9: derive_status era codice morto, mai
# chiamato). Lo status 'disputed' resta RISERVATO ai territori contestati
# (ETHICS-003, cap ≤0.7) e non viene mai sovrascritto qui.
# Vedi docs/ethics/ETHICS-013-confidence-status-coherence.md.
def _coerce_low_confidence_status(mapper, connection, target: GeoEntity) -> None:
    if (
        target.confidence_score is not None
        and target.confidence_score < 0.5
        and target.status == EntityStatus.CONFIRMED.value
    ):
        target.status = EntityStatus.UNCERTAIN.value


event.listen(GeoEntity, "before_insert", _coerce_low_confidence_status)
event.listen(GeoEntity, "before_update", _coerce_low_confidence_status)


class CapitalHistory(Base):
    """Storia delle capitali per polities long-duration (audit v4 Round 13, ADR-004).

    Pattern: entità come Ottoman, Mughal, Ming, Song, Solomonic Ethiopia
    hanno avuto capitali multiple. Il campo `geo_entities.capital_*`
    espone solo UNA capitale (la "iconica"); questa tabella documenta
    la cronologia completa.

    ETHICS-001: nomi capital nella lingua locale.
    ETHICS-002: per polities con corte mobile, name='court itinerant' + lat/lon NULL.
    """

    __tablename__ = "capital_history"
    __table_args__ = (
        Index("ix_capital_history_entity_id", "entity_id"),
        Index("ix_capital_history_year_range", "year_start", "year_end"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("geo_entities.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    year_start: Mapped[int] = mapped_column(Integer, nullable=False)
    year_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ordering: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    entity: Mapped[GeoEntity] = relationship("GeoEntity", back_populates="capital_history")


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
        # v6.14: date precision constraints.
        CheckConstraint(
            "month IS NULL OR (month >= 1 AND month <= 12)",
            name="ck_tc_month_range",
        ),
        CheckConstraint(
            "day IS NULL OR (day >= 1 AND day <= 31)",
            name="ck_tc_day_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("geo_entities.id"), nullable=False)

    year: Mapped[int] = mapped_column(Integer, nullable=False)
    # v6.14: date precision layer
    month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date_precision: Mapped[str | None] = mapped_column(String(20), nullable=True)
    iso_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    calendar_note: Mapped[str | None] = mapped_column(String(500), nullable=True)

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
