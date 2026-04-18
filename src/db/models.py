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
    DatePrecision,
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

    # v6.69 audit v4 Fase A: Wikidata Q-ID di riferimento (bootstrap via
    # scripts/wikidata_bootstrap.py con score ≥ 0.85).
    # ETHICS: il Q-ID serve per cross-reference/drift detection, non come
    # fonte autoritativa. Wikidata può avere bias occidentali/convention diverse
    # — le discrepanze vanno valutate manualmente (vedi Fase B drift report).
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
    # ─── v6.14: date precision layer ─────────────────────────────────────
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

    # ─── v6.14: date precision layer ─────────────────────────────────────
    # Granularità sub-annuale opzionale. month/day nullable — se NULL,
    # l'evento ha solo precisione annuale (backward-compatible).
    month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # ETHICS: per BCE, date_precision + calendar_note esplicitano
    # che si usa il prolettico gregoriano e il calendario originale è diverso.
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

    timestamp: Mapped[str] = mapped_column(String(50), nullable=False)  # ISO 8601
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    path: Mapped[str] = mapped_column(String(2000), nullable=False)
    query_string: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_time_ms: Mapped[float] = mapped_column(Float, nullable=False)

    client_ip: Mapped[str] = mapped_column(String(45), nullable=False)  # IPv6 max 45 chars
    user_agent: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    referer: Mapped[str | None] = mapped_column(String(2000), nullable=True)


# ─── v6.16: AI Co-Founder Dashboard ─────────────────────────────────


class AiSuggestion(Base):
    """AI-generated suggestion for the co-founder dashboard.

    The AI analysis agent populates this table with actionable suggestions
    (geographic gaps, temporal gaps, low-confidence entities, missing chains,
    etc.). The founder reviews and accepts/rejects/implements each suggestion
    via the /admin/brief dashboard.

    ETHICS: suggestions about adding entities or events must NOT bias the
    dataset toward any particular cultural perspective. Geographic and
    temporal gaps are identified objectively by comparing coverage across
    ALL regions and eras equally.
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


# ─── v6.27: Historical Periods (Epochs) ─────────────────────────────


class HistoricalPeriod(Base):
    """Structured historical period / epoch.

    Esempi:
      * "Bronze Age" (global, 3300-1200 BCE)
      * "Classical Antiquity" (Mediterranean, 8th c. BCE - 5th c. CE)
      * "Medieval Period" (Europe, 500-1500)
      * "Edo Period" (Japan, 1603-1868)
      * "Warring States Period" (China, -475 - -221)

    ETHICS: le periodizzazioni sono costrutti storiografici, non fatti
    oggettivi. Ogni periodo dichiara `region` (non globale di default),
    `historiographic_note` con le controversie, e `confidence_score`.
    La stessa epoca puo' avere definizioni diverse per regioni diverse
    (es. "Middle Ages" in Europa vs "Heian Period" in Giappone).
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

    # ETHICS: primary name is the commonly accepted English historiographic
    # name for searchability; original_name_native preserves local form.
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    name_lang: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    # URL-friendly unique slug (e.g., "bronze-age", "edo-period")
    slug: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    # Native-language name if different (e.g., "江戸時代" for Edo Period)
    name_native: Mapped[str | None] = mapped_column(String(200), nullable=True)
    name_native_lang: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Period type: age (prehistoric), era (classical), period (specific),
    # dynasty (rule-based), epoch (scientific). Used for filtering.
    period_type: Mapped[str] = mapped_column(String(50), nullable=False, default="period")

    # Region scope: "global", "europe", "asia_east", "asia_south", "mesoamerica",
    # "near_east", "africa", "oceania", "americas", etc. "global" for planet-wide
    # periods (e.g., Bronze Age broadly).
    region: Mapped[str] = mapped_column(String(50), nullable=False, default="global")

    year_start: Mapped[int] = mapped_column(Integer, nullable=False)
    year_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    # ETHICS: periodization disputes go here. "The term 'Dark Ages' is now
    # contested in scholarship; this period uses the neutral 'Early Medieval
    # Period'. For the Islamic Golden Age perspective see ..."
    historiographic_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Alternative names / competing periodizations: JSON list of dicts
    # [{"name": "Dark Ages", "context": "older historiography, now contested"}]
    alternative_names: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    # confirmed (well-established), debated (boundaries contested),
    # deprecated (older term superseded)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="confirmed")

    # JSON array of source citations
    sources: Mapped[str | None] = mapped_column(Text, nullable=True)


# ─── v6.37: Archaeological Sites (UNESCO + ruins + monuments) ──────────


class ArchaeologicalSite(Base):
    """Sito archeologico / culturale discreto con coordinate puntuali.

    Distinto da `HistoricalCity` (centro urbano con vita politica) e da
    `GeoEntity` (stato/regno con boundary). Un sito e' un luogo materiale:
    Pompeii, Stonehenge, Chichen Itza, Angkor Wat, Petra, Uluru, ecc.

    Design choices:
      * Coordinate puntuali (lat/lon), non polygon. Se serve area
        approssimata si puo' derivare da siti UNESCO con buffer radius.
      * `date_start` / `date_end` sono periodi di costruzione/uso attestato,
        NON fondazione dell'entita' politica (es. Pompeii date_start = -600
        VIII sec a.C.? o prima insediamento Osco-Sannita? usiamo la prima
        evidenza archeologica documentata)
      * `entity_id` e' nullable: molti siti pre-datano o sopravvivono
        qualsiasi entita' politica single (es. Gobekli Tepe, Stonehenge)
      * `unesco_id` e' lo "Ref ID" del sito UNESCO (es. "757" per Pompei)

    ETHICS-005-analogy: confidence_score riflette la qualita' dell'evidenza
    archeologica, non un giudizio politico. Siti con datazione controversa
    (es. Gobekli Tepe) hanno status='uncertain' e ethical_notes esplicita.

    ETHICS-009-analogy: i siti storici spesso hanno DUE nomi — quello
    originale/indigeno e quello coloniale. `name_original` = quello
    primario-culturale (Uluru, non "Ayers Rock"). `name_variants` JSON
    array contiene altre forme con context.
    """

    __tablename__ = "archaeological_sites"
    __table_args__ = (
        Index("ix_arch_sites_name", "name_original"),
        Index("ix_arch_sites_entity_id", "entity_id"),
        Index("ix_arch_sites_years", "date_start", "date_end"),
        Index("ix_arch_sites_site_type", "site_type"),
        Index("ix_arch_sites_unesco", "unesco_id"),
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_arch_sites_confidence_range",
        ),
        CheckConstraint(
            "latitude >= -90.0 AND latitude <= 90.0",
            name="ck_arch_sites_lat_range",
        ),
        CheckConstraint(
            "longitude >= -180.0 AND longitude <= 180.0",
            name="ck_arch_sites_lon_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ETHICS-001: nome originale/locale come chiave primaria.
    name_original: Mapped[str] = mapped_column(String(500), nullable=False)
    name_original_lang: Mapped[str] = mapped_column(String(10), nullable=False)

    # Coordinate puntuali WGS84 del centro del sito.
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    # Periodo di costruzione / uso attestato. NULL se ignoto.
    date_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Tipo dominante (vedi src/db/enums.py SiteType).
    site_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="ruins"
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # UNESCO World Heritage Site ID (es. "757" per Pompei area); NULL se non UNESCO.
    unesco_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Anno di inscrizione UNESCO.
    unesco_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Entita' politica di appartenenza principale (pre-classico se necessario).
    # NULL per siti pre-statali (Gobekli Tepe, Stonehenge).
    entity_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("geo_entities.id"), nullable=True
    )

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    # confirmed / uncertain / disputed — con uncertain di default se
    # datazione ancora dibattuta o sito contestato
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EntityStatus.CONFIRMED.value
    )

    # ETHICS-009-analogy: colonial renaming (Uluru/Ayers Rock,
    # Chiang Mai/Lanna), ritorni/rivendicazioni indigene, danneggiamenti
    # storici (Bamiyan Buddhas, Palmyra).
    ethical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON-serialized (stesso pattern di HistoricalCity):
    # [{"citation": "...", "url": "...", "source_type": "academic"}]
    sources: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON: [{"name": "Ayers Rock", "lang": "en", "context": "colonial"}]
    name_variants: Mapped[str | None] = mapped_column(Text, nullable=True)

    entity: Mapped[GeoEntity | None] = relationship("GeoEntity")


# ─── v6.38: Historical Rulers ───────────────────────────────────────────


class HistoricalRuler(Base):
    """Capi storici: imperatori, re, sultani, khagan, presidenti, dittatori.

    ETHICS-001: nome primario e' quello originale nella lingua/script
    del sovrano (武曌, Александр II). Forme latinizzate in name_variants.

    ETHICS-002: violenza, genocidi, schiavitu' vanno esplicitati nelle
    ethical_notes — niente eufemismi.
    """

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


# ─── v6.44: Historical Languages ────────────────────────────────────────


class HistoricalLanguage(Base):
    """Lingua storica geocoded — area geografica d'uso + periodo.

    Distinta da `GeoEntity` (stato politico) e `HistoricalCity` (urban
    center). Una lingua puo' coprire multiple entita' politiche
    (latino sotto Roma e sotto Bizantino) e sopravvivere oltre la
    fine di uno stato (greco post-conquista romana).

    ETHICS: languages endangered / extinct flaggate. Quando c'e' colonial
    imposition (es. Nahuatl soppresso da spagnolo, aborigeni AU da inglese),
    ethical_notes esplicita il processo.

    Design choices:
      * Geocoding: center point + region_name (string). Polygon optional
        (pochi casi ben delimitati - es. dialetti chiaramente confinati).
      * period_start/end: prima attestazione scritta → ultimo parlante
        native (o 'living' status). Per lingue ricostruite (PIE),
        confidence_score < 0.5 e status='uncertain'.
    """

    __tablename__ = "historical_languages"
    __table_args__ = (
        Index("ix_lang_name", "name_original"),
        Index("ix_lang_period", "period_start", "period_end"),
        Index("ix_lang_region", "region_name"),
        Index("ix_lang_family", "family"),
        Index("ix_lang_iso", "iso_code"),
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_lang_confidence_range",
        ),
        CheckConstraint(
            "center_lat IS NULL OR (center_lat >= -90.0 AND center_lat <= 90.0)",
            name="ck_lang_lat_range",
        ),
        CheckConstraint(
            "center_lon IS NULL OR (center_lon >= -180.0 AND center_lon <= 180.0)",
            name="ck_lang_lon_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_original: Mapped[str] = mapped_column(String(200), nullable=False)
    name_original_lang: Mapped[str] = mapped_column(String(10), nullable=False)

    # ISO 639-3 (3-letter) dove disponibile. Es. "lat" (latino), "grc" (ancient greek).
    iso_code: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Language family (Indo-European, Afro-Asiatic, Sino-Tibetan, Austronesian, ecc.)
    family: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Script(s) storicamente usati (latin, greek, cuneiform, hieroglyphic, ecc.)
    script: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Geocoding approssimato — center point dell'area storica principale.
    center_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    center_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    region_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # Period: prima attestazione → ultimo parlante native (None = ancora parlata)
    period_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    period_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Status vita: living, endangered, extinct, reconstructed, classical (dead-but-literary).
    vitality_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="extinct"
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EntityStatus.CONFIRMED.value
    )

    # ETHICS: soppressioni coloniali, repressioni linguistiche, revival
    # movements (Welsh, Maori, Cornish, Hebrew).
    ethical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON array: fonti accademiche (Ethnologue, Glottolog, academic corpora).
    sources: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON array: varianti nome (scientific/colonial).
    name_variants: Mapped[str | None] = mapped_column(Text, nullable=True)


# ─── v6.53: Known Dev IPs (for analytics filter) ──────────────────────


class KnownDevIp(Base):
    """IP marcati come 'dev' dall'admin — esclusi dalla dashboard analytics
    external-only. Popolato via `POST /admin/dev-ips/mark-current` (user-facing).

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
