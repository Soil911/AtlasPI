"""Models: HistoricalCity + TradeRoute + RouteCityLink (places ≠ stati politici).

Sub-module di src.db.models (split v6.96.0 / audit R7).

ETHICS-009: rinominazioni coloniali documentate, non nascoste.
ETHICS-010: rotte schiaviste flaggate con involves_slavery=True.
"""

from __future__ import annotations

from sqlalchemy import Boolean, CheckConstraint, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.db.enums import CityType, EntityStatus  # noqa: F401
from src.db.models.entities import GeoEntity  # noqa: F401 — relationship target


class HistoricalCity(Base):
    """Città storica — centro urbano discreto con vita propria.

    Distinta dalla `capital_*` su GeoEntity perché:
        1. Le città sopravvivono alle entità (Roma come capitale romana,
           bizantina, poi del Papato — una città, più entità).
        2. Molte città importanti NON sono capitali (Samarcanda come
           trade-hub, Timbuctù come centro accademico).
        3. Le città sono nodi di `TradeRoute` — m:n sulle rotte.

    ETHICS-001 analogy: `name_original` è il nome locale.
    ETHICS-009: rinominazioni coloniali (Constantinople → Istanbul,
    Königsberg → Kaliningrad) sono documentate in `ethical_notes`,
    non nascoste.
    """

    __tablename__ = "historical_cities"
    __table_args__ = (
        Index("ix_historical_cities_name", "name_original"),
        Index("ix_historical_cities_years", "founded_year", "abandoned_year"),
        Index("ix_historical_cities_city_type", "city_type"),
        Index("ix_historical_cities_entity_id", "entity_id"),
        Index("ix_historical_cities_confidence", "confidence_score"),
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_cities_confidence_range",
        ),
        CheckConstraint(
            "population_peak IS NULL OR population_peak >= 0",
            name="ck_cities_population_nonneg",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ETHICS-001: nome originale/locale come chiave.
    name_original: Mapped[str] = mapped_column(String(500), nullable=False)
    name_original_lang: Mapped[str] = mapped_column(String(10), nullable=False)

    # Coordinate del centro storico della città.
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    abandoned_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Funzione dominante. Se ambigua o multipla → MULTI_PURPOSE.
    city_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default=CityType.MULTI_PURPOSE.value
    )

    population_peak: Mapped[int | None] = mapped_column(Integer, nullable=True)
    population_peak_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Entità politica di appartenenza "principale" — nullable per città
    # pre-statali (Çatalhöyük).
    entity_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("geo_entities.id"), nullable=True
    )

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EntityStatus.CONFIRMED.value
    )

    # ETHICS-009: spiegazione del renaming / cancellazione culturale.
    ethical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Sources come JSON string. Vedi audit R8 (post v6.96) per migrazione
    # a tabella source_records relazionale.
    sources: Mapped[str | None] = mapped_column(Text, nullable=True)
    name_variants: Mapped[str | None] = mapped_column(Text, nullable=True)

    entity: Mapped[GeoEntity | None] = relationship("GeoEntity")
    route_links: Mapped[list[RouteCityLink]] = relationship(
        "RouteCityLink", back_populates="city", cascade="all, delete-orphan"
    )


class TradeRoute(Base):
    """Rotta commerciale storica.

    ETHICS-010: rotte di esseri umani schiavizzati flaggate con
    involves_slavery=True + commodities include "humans_enslaved" +
    ethical_notes con scala/periodo/main_actors.
    """

    __tablename__ = "trade_routes"
    __table_args__ = (
        Index("ix_trade_routes_name", "name_original"),
        Index("ix_trade_routes_years", "start_year", "end_year"),
        Index("ix_trade_routes_route_type", "route_type"),
        Index("ix_trade_routes_confidence", "confidence_score"),
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_routes_confidence_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name_original: Mapped[str] = mapped_column(String(500), nullable=False)
    name_original_lang: Mapped[str] = mapped_column(String(10), nullable=False)

    route_type: Mapped[str] = mapped_column(String(20), nullable=False)

    start_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Geometria: LineString o MultiLineString in GeoJSON.
    geometry_geojson: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Commodities come JSON array di strings. ETHICS-010: include
    # "humans_enslaved" per le rotte schiaviste.
    commodities: Mapped[str | None] = mapped_column(Text, nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ETHICS-010: flag esplicito (denormalizzato) per query/filter.
    involves_slavery: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.6)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EntityStatus.CONFIRMED.value
    )

    # ETHICS-010: note etiche obbligatorie se involves_slavery=True.
    ethical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    sources: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relazione m:n via RouteCityLink (ordine waypoints conservato).
    city_links: Mapped[list[RouteCityLink]] = relationship(
        "RouteCityLink", back_populates="route", cascade="all, delete-orphan",
        order_by="RouteCityLink.sequence_order",
    )


class RouteCityLink(Base):
    """Junction m:n rotta ↔ città con ordinamento dei waypoints.

    sequence_order = 0 è l'origine; l'ultima sequence è la destinazione.
    is_terminal=True marca origine/destinazione esplicitamente.
    """

    __tablename__ = "route_city_links"
    __table_args__ = (
        Index("ix_route_city_links_route_id", "route_id"),
        Index("ix_route_city_links_city_id", "city_id"),
        Index("ix_route_city_links_sequence", "route_id", "sequence_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("trade_routes.id"), nullable=False
    )
    city_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("historical_cities.id"), nullable=False
    )

    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_terminal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    route: Mapped[TradeRoute] = relationship("TradeRoute", back_populates="city_links")
    city: Mapped[HistoricalCity] = relationship("HistoricalCity", back_populates="route_links")
