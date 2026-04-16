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

from sqlalchemy import Boolean, CheckConstraint, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.db.enums import (  # noqa: F401
    ChainType,
    CityType,
    EntityStatus,
    EventRole,
    EventType,
    RouteType,
    SourceType,
    TransitionType,
)


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


# ─── v6.4: Cities + Trade Routes ─────────────────────────────────────────────


class HistoricalCity(Base):
    """Città storica — centro urbano discreto con vita propria.

    Distinta dalla `capital_*` su GeoEntity per tre ragioni:
        1. Le città sopravvivono alle entità (Roma come capitale romana,
           bizantina, poi del Papato — una città, più entità).
        2. Molte città importanti NON sono capitali (Samarcanda come
           trade-hub, Timbuctù come centro accademico).
        3. Le città sono nodi di `TradeRoute` — m:n sulle rotte, non
           limitate all'entità a cui appartengono politicamente.

    ETHICS-001 analogy: `name_original` è il nome nella lingua locale /
    del momento di fondazione, non il nome imposto dai conquistatori.
    Varianti coloniali vanno in `name_variants`.

    ETHICS-009 (nuovo, v6.4): una città può essere stata "rinominata per
    cancellazione culturale" (Constantinople → Istanbul, Königsberg →
    Kaliningrad, Lvov/Lviv/Lemberg/Lwów). Il campo `ethical_notes`
    deve esplicitare il contesto del renaming, non nasconderlo.
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

    # Coordinate del centro storico della città (non dell'area urbana moderna).
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    # Fondazione / abbandono. NULL = ancora esistente o ignoto.
    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    abandoned_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Funzione dominante. Se ambigua o multipla → MULTI_PURPOSE.
    city_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default=CityType.MULTI_PURPOSE.value
    )

    # Popolazione stimata al picco (informativa, per ordinamento).
    population_peak: Mapped[int | None] = mapped_column(Integer, nullable=True)
    population_peak_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Entità politica di appartenenza "principale" — opzionale, perché
    # le città pre-statali (Çatalhöyük) non hanno stato di riferimento.
    entity_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("geo_entities.id"), nullable=True
    )

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EntityStatus.CONFIRMED.value
    )

    # ETHICS-009: spiegazione del renaming / cancellazione culturale.
    ethical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Sources come JSON string (lista di dict {citation, url, source_type}).
    # JSON scelto invece di tabella separata per semplicità: le città hanno
    # tipicamente 1-3 fonti, non decine come le entità.
    sources: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Name variants come JSON — per "Constantinople" / "Istanbul" entrambi.
    name_variants: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relazioni.
    entity: Mapped[GeoEntity | None] = relationship("GeoEntity")
    route_links: Mapped[list[RouteCityLink]] = relationship(
        "RouteCityLink", back_populates="city", cascade="all, delete-orphan"
    )


class TradeRoute(Base):
    """Rotta commerciale storica.

    ETHICS-010 (nuovo, v6.4): se una rotta trafficava esseri umani
    schiavizzati (Trans-Atlantic slave trade, Trans-Saharan slave trade,
    Indian Ocean slave trade), `commodities` DEVE includere il marker
    `"humans_enslaved"` e `ethical_notes` DEVE esplicitare scala
    (milioni di persone), periodo, main_actors (compagnie, stati).
    NON "merce generica" o "prodotti vari".

    La rotta è una linea/polilinea in GeoJSON nel campo `geometry_geojson`,
    con waypoints elencati come città in `route_city_links`. Se i waypoints
    sono ignoti/molteplici, lasciare la relazione vuota e tenere solo la
    polilinea approssimata.
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

    # Periodo di attività. NULL = ignoto.
    start_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Geometria: LineString o MultiLineString in GeoJSON.
    geometry_geojson: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Commodities come JSON array di strings. ETHICS-010: include
    # "humans_enslaved" per le rotte schiaviste.
    commodities: Mapped[str | None] = mapped_column(Text, nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Se la rotta includeva schiavismo (denormalizzato per query/filter).
    # ETHICS-010: flag esplicito evita che un fruitore debba parsare
    # commodities per sapere se la rotta è eticamente "pesante".
    involves_slavery: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.6)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EntityStatus.CONFIRMED.value
    )

    # ETHICS-010: note etiche (scala, main_actors, nomi alternativi imposti
    # dai colonizzatori). Obbligatorio se involves_slavery=True.
    ethical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    sources: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relazione m:n via RouteCityLink (ordine dei waypoints conservato).
    city_links: Mapped[list[RouteCityLink]] = relationship(
        "RouteCityLink", back_populates="route", cascade="all, delete-orphan",
        order_by="RouteCityLink.sequence_order",
    )


class RouteCityLink(Base):
    """Junction m:n rotta ↔ città con ordinamento dei waypoints.

    sequence_order = 0 è l'origine; l'ultima sequence è la destinazione.
    Terminale = is_terminal=True marca origine e destinazione esplicitamente
    (utile per filtrare "rotte che partono da Canton").
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
    city: Mapped["HistoricalCity"] = relationship("HistoricalCity", back_populates="route_links")


# ─── v6.5: Dynasty / Succession Chains ─────────────────────────────────────


class DynastyChain(Base):
    """Catena successoria che lega più entità geopolitiche.

    Esempi:
      * "Roman Power Center" (SUCCESSION): Roma Repubblica → Impero
        Romano → Impero Romano d'Occidente → Regno d'Italia Ostrogoto
        → Esarcato di Ravenna → ...
      * "Chinese Imperial Dynasties" (DYNASTY): Han → Tang → Song → Yuan
        → Ming → Qing → Repubblica
      * "Inca → Peruvian Republic" (COLONIAL): Tawantinsuyu → Vicereame
        del Perù → Repubblica del Perù

    ETHICS-002 / ETHICS-003: ogni link nella catena ha un transition_type
    esplicito (CONQUEST, SUCCESSION, DECOLONIZATION, ecc.) — non si
    riducono violenze a "successione" generica. Le catene IDEOLOGICAL
    (es. "Holy Roman Empire → German Empire → Third Reich") portano
    avvertimento esplicito che la self-proclaimed continuità ≠ legittimità.
    """

    __tablename__ = "dynasty_chains"
    __table_args__ = (
        Index("ix_dynasty_chains_name", "name"),
        Index("ix_dynasty_chains_chain_type", "chain_type"),
        Index("ix_dynasty_chains_region", "region"),
        Index("ix_dynasty_chains_status", "status"),
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_chains_confidence_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    name_lang: Mapped[str] = mapped_column(String(10), nullable=False, default="en")

    # ChainType enum (DYNASTY / SUCCESSION / RESTORATION / COLONIAL /
    # IDEOLOGICAL / OTHER).
    chain_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # Macro-area geografica della catena (descrittiva, non normativa).
    region: Mapped[str | None] = mapped_column(String(200), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EntityStatus.CONFIRMED.value
    )

    # ETHICS: avvertimenti su self-proclaimed continuità (German Reich),
    # cancellazioni culturali (Tenochtitlan→Mexico City), nature contestate
    # delle continuità (URSS → Federazione Russa: continuità giuridica
    # parziale).
    ethical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    sources: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array

    # Link ordinati alle entità della catena.
    links: Mapped[list[ChainLink]] = relationship(
        "ChainLink", back_populates="chain", cascade="all, delete-orphan",
        order_by="ChainLink.sequence_order",
    )


class ChainLink(Base):
    """Link tra una DynastyChain e una GeoEntity, con tipo di transizione.

    sequence_order = 0 è l'entità più antica della catena. Ogni link ha
    transition_type che descrive COME questa entità è subentrata alla
    precedente (CONQUEST, REFORM, SUCCESSION, DECOLONIZATION, ecc.). La
    PRIMA entità della catena (sequence_order=0) ha transition_type=NULL
    perché non c'è predecessore nella catena.
    """

    __tablename__ = "chain_links"
    __table_args__ = (
        Index("ix_chain_links_chain_id", "chain_id"),
        Index("ix_chain_links_entity_id", "entity_id"),
        Index("ix_chain_links_sequence", "chain_id", "sequence_order"),
        Index("ix_chain_links_transition_type", "transition_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chain_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dynasty_chains.id"), nullable=False
    )
    entity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("geo_entities.id"), nullable=False
    )

    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Anno della transizione DAL predecessore A questa entità.
    # NULL per il primo link della catena.
    transition_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # TransitionType enum (CONQUEST / SUCCESSION / DECOLONIZATION / ecc.).
    # NULL solo per il primo link della catena (no predecessore).
    transition_type: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # ETHICS-002: era violenta? Se transition_type=CONQUEST è True per
    # default; per altri tipi può essere overridden esplicitamente
    # (es. una "PARTITION" formalmente legale ma con violenze associate).
    is_violent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Note etiche specifiche al link (es. dispute sulla legittimità
    # della successione, cancellazione di documentazione, ecc.).
    ethical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    chain: Mapped[DynastyChain] = relationship("DynastyChain", back_populates="links")
    entity: Mapped[GeoEntity] = relationship("GeoEntity")


# ─── v6.12: API Analytics ─────────────────────────────────────────────


class ApiRequestLog(Base):
    """Log entry for every API request. Used by /admin/analytics dashboard.

    Only logs API paths (/v1/*, /health, /admin/*) — static file requests
    are excluded by the middleware to keep the table lean.
    """

    __tablename__ = "api_request_logs"
    __table_args__ = (
        Index("ix_api_logs_timestamp", "timestamp"),
        Index("ix_api_logs_path", "path"),
        Index("ix_api_logs_client_ip", "client_ip"),
        Index("ix_api_logs_status_code", "status_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    timestamp: Mapped[str] = mapped_column(String(30), nullable=False)  # ISO 8601
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    path: Mapped[str] = mapped_column(String(2000), nullable=False)
    query_string: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_time_ms: Mapped[float] = mapped_column(Float, nullable=False)

    client_ip: Mapped[str] = mapped_column(String(45), nullable=False)  # IPv6 max 45 chars
    user_agent: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    referer: Mapped[str | None] = mapped_column(String(2000), nullable=True)
