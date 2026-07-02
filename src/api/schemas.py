"""Schemi Pydantic per le risposte API — vedi ADR-002."""

from pydantic import BaseModel, Field


class NameVariantResponse(BaseModel):
    """Variante di nome con contesto storico (ETHICS-001)."""
    name: str = Field(description="Nome nella lingua indicata")
    lang: str = Field(description="Codice lingua ISO 639-1")
    period_start: int | None = Field(None, description="Anno inizio uso (negativo = a.C.)")
    period_end: int | None = Field(None, description="Anno fine uso")
    context: str | None = Field(None, description="Contesto storico-politico del nome")
    source: str | None = Field(None, description="Fonte bibliografica")

    model_config = {"from_attributes": True}


class TerritoryChangeResponse(BaseModel):
    """Cambio territoriale con tipo esplicito (ETHICS-002)."""
    year: int = Field(description="Anno del cambio (negativo = a.C.)")
    region: str = Field(description="Regione coinvolta")
    change_type: str = Field(description="Tipo: CONQUEST_MILITARY, TREATY, COLONIZATION, etc.")
    description: str | None = Field(None, description="Descrizione del cambio")
    population_affected: int | None = Field(None, description="Stima popolazione colpita")
    confidence_score: float = Field(description="Affidabilità dato 0.0-1.0")

    model_config = {"from_attributes": True}


class SourceResponse(BaseModel):
    """Fonte bibliografica tracciabile."""
    citation: str = Field(description="Citazione bibliografica")
    url: str | None = Field(None, description="URL della fonte")
    source_type: str = Field(description="Tipo: primary, secondary, academic")

    model_config = {"from_attributes": True}


class CapitalResponse(BaseModel):
    """Capitale dell'entità."""
    name: str
    lat: float
    lon: float


class CapitalHistoryResponse(BaseModel):
    """Capitale storica con range temporale (v6.87 — ADR-004).

    Per polities long-duration con capitali multiple (Ottoman, HRE, Mughal,
    Ming, Song, Solomonic Ethiopia, ecc.). Permette query 'capital of X
    in year Y' senza anacronismo.

    `lat/lon` può essere null per polities con corte itinerante.
    `year_end` null = capitale attuale o ultima.
    `ordering` per casi sovrapposti (es. dual monarchy Wien+Budapest).
    """
    name: str = Field(description="Nome della capitale (lingua locale, ETHICS-001)")
    lat: float | None = Field(None, description="Latitudine (null per corte itinerante)")
    lon: float | None = Field(None, description="Longitudine")
    year_start: int = Field(description="Anno inizio periodo come capitale")
    year_end: int | None = Field(None, description="Anno fine (null = ultima/attuale)")
    ordering: int = Field(default=0, description="Sort secondario per periodi sovrapposti")
    notes: str | None = Field(None, description="Spiegazione del ruolo")

    model_config = {"from_attributes": True}


class EntityResponse(BaseModel):
    """Risposta completa per una singola entità — formato da ADR-002."""
    id: int
    entity_type: str = Field(description="Tipo: empire, kingdom, city-state, colony, disputed_territory")
    year_start: int = Field(description="Anno inizio (negativo = a.C.)")
    year_end: int | None = Field(None, description="Anno fine (null = ancora esistente)")
    name_original: str = Field(description="Nome nella lingua originale/locale (ETHICS-001)")
    name_original_lang: str = Field(description="Codice lingua ISO 639-1")
    name_variants: list[NameVariantResponse] = Field(default_factory=list, description="Nomi in altre lingue con contesto")
    capital: CapitalResponse | None = None
    boundary_geojson: dict | None = Field(None, description="Confini GeoJSON (Polygon o MultiPolygon)")
    # ETHICS-005: la tier di provenienza del confine. Permette al consumatore
    # di distinguere un poligono reale da uno generato senza ispezionare il
    # geojson. Valori: historical_map, natural_earth, aourednik,
    # academic_source, approximate_generated, approximate_circle (cerchio sulla
    # capitale, Phase H — ETHICS-012), historical_approximation (poligono storico
    # disegnato a mano).
    boundary_source: str | None = Field(
        None,
        description=(
            "Tier di provenienza del confine (ETHICS-005): historical_map, "
            "natural_earth, aourednik, academic_source, approximate_generated, "
            "approximate_circle, historical_approximation"
        ),
    )
    boundary_aourednik_name: str | None = Field(
        None,
        description="Nome esatto della feature matchata in aourednik/historical-basemaps (riproducibilita' scientifica)",
    )
    boundary_aourednik_year: int | None = Field(
        None,
        description="Anno dello snapshot aourednik usato (uno dei 53 disponibili, -123000..2010)",
    )
    # v6.99.109 (agent-UX): flag machine-readable dell'anacronismo potenziale.
    boundary_reference_year: int | None = Field(
        None,
        description=(
            "Anno di riferimento del polygon. Il boundary è UNO snapshot STATICO "
            "per l'intero lifespan dell'entità: interrogando un anno diverso da "
            "questo, i confini mostrati possono essere anacronistici (es. Mughal "
            "alla massima estensione ~1700 anche per query sul 1550). NULL = anno "
            "di riferimento non noto (approssimazione generica). Oggi coincide con "
            "boundary_aourednik_year quando la provenienza è aourednik."
        ),
    )
    boundary_aourednik_precision: int | None = Field(
        None,
        description="Precisione BORDERPRECISION dell'upstream aourednik (README historical-basemaps): 1=approssimato, 2=moderatamente preciso, 3=determinato da legge internazionale. Il valore 0 e' un edge-case legacy (4 feature upstream). Converte in confidence via PRECISION_CONFIDENCE (3->0.85, 2->0.70, 1->0.55, 0->0.45).",
    )
    boundary_ne_iso_a3: str | None = Field(
        None,
        description="ISO_A3 del paese Natural Earth quando il match passa per NE",
    )
    confidence_score: float = Field(description="Affidabilità complessiva 0.0-1.0")
    status: str = Field(description="confirmed, uncertain, o disputed")
    territory_changes: list[TerritoryChangeResponse] = Field(default_factory=list, description="Cambi territoriali (ETHICS-002)")
    sources: list[SourceResponse] = Field(default_factory=list, description="Fonti bibliografiche")
    ethical_notes: str | None = Field(None, description="Note sulla governance etica del dato")
    continent: str | None = Field(None, description="Continente derivato dalle coordinate della capitale")
    # v6.69: Wikidata Q-ID per cross-reference (audit v4 Fase A).
    # ETHICS: identificatore di riferimento esterno, non fonte autoritativa —
    # usato per drift detection sistematico contro Wikidata.
    wikidata_qid: str | None = Field(
        None,
        description="Wikidata Q-ID di riferimento (formato 'Q12345'). Null se nessun match high-confidence è stato trovato (audit v4, v6.69).",
    )
    # v6.87 ADR-004: capital history per polities con capitali multiple.
    capital_history: list[CapitalHistoryResponse] = Field(
        default_factory=list,
        description="Cronologia capitali per polities long-duration (ADR-004). Vuoto se l'entity ha solo `capital` singola. Ordinato per year_start ASC, poi ordering.",
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "entity_type": "empire",
                "year_start": -27,
                "year_end": 476,
                "name_original": "Imperium Romanum",
                "name_original_lang": "la",
                "confidence_score": 0.90,
                "status": "confirmed",
                "capital": {"name": "Roma", "lat": 41.9028, "lon": 12.4964},
                "boundary_source": "natural_earth",
                "boundary_ne_iso_a3": "ITA",
                "boundary_aourednik_name": None,
                "boundary_aourednik_year": None,
                "boundary_aourednik_precision": None,
                "continent": "Europe",
                "wikidata_qid": "Q2277",
            }
        },
    }


class PaginatedEntityResponse(BaseModel):
    """Risposta paginata per liste di entità.

    v6.66 FIX 4: include sia `total` (standard) sia `count` (legacy).
    `count` è deprecato ma restituito per retro-compatibilità per 1-2 release.
    """
    total: int = Field(description="Numero totale di risultati che matchano i filtri (prima di limit/offset)")
    count: int = Field(description="DEPRECATED (v6.66) — alias di `total`. Sarà rimosso in v6.68.")
    limit: int = Field(description="Limite per pagina")
    offset: int = Field(description="Offset corrente")
    entities: list[EntityResponse]
    # v6.99.109 (agent-UX): con 0 risultati, indica il retry-path invece di
    # un dead-end silenzioso (gli agenti abbandonavano dopo il primo 0-result).
    hint: str | None = Field(
        None,
        description="Presente solo con total=0 su ricerche per nome: suggerisce il retry via /v1/search/fuzzy",
    )


# ─── Wave 2.5 (audit API #1): response_model per gli endpoint headline ──────
# Modelli MIRROR-ESATTI dei dict restituiti dagli handler (stesse chiavi),
# campi Optional/permissivi così response_model NON elimina campi né solleva
# 500 su validazione. Scopo: l'OpenAPI spec espone schemi reali (non `{}`) sugli
# endpoint che gli agent AI usano per primi (/light, /batch, /events).


class LightEntityResponse(BaseModel):
    """Entità in forma leggera (senza boundary_geojson) — vedi /v1/entities/light."""
    id: int
    name_original: str | None = None
    name_original_lang: str | None = None
    entity_type: str | None = None
    year_start: int | None = None
    year_end: int | None = None
    capital_name: str | None = None
    capital_lat: float | None = None
    capital_lon: float | None = None
    confidence_score: float | None = None
    status: str | None = None
    continent: str | None = Field(None, description="Continente derivato dalle coordinate capitale")

    model_config = {"from_attributes": True}


class LightListResponse(BaseModel):
    """Risposta di /v1/entities/light — bootstrap mappa / overview agent."""
    total: int
    count: int = Field(description="DEPRECATED — alias di total (retro-compat)")
    entities: list[LightEntityResponse]


class BatchResponse(BaseModel):
    """Risposta di /v1/entities/batch — fetch multiplo per ID in un round-trip."""
    requested: int
    found: int
    not_found: list[int] = Field(default_factory=list)
    entities: list[EntityResponse]


class EventSummaryResponse(BaseModel):
    """Evento storico in forma compatta (liste) — mirror di _event_summary."""
    id: int
    name_original: str | None = None
    name_original_lang: str | None = None
    event_type: str | None = None
    year: int | None = None
    year_end: int | None = None
    month: int | None = None
    day: int | None = None
    date_precision: str | None = None
    iso_date: str | None = None
    location_name: str | None = None
    location_lat: float | None = None
    location_lon: float | None = None
    main_actor: str | None = None
    status: str | None = None
    confidence_score: float | None = None
    known_silence: bool | None = None

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    """Risposta di /v1/events (list)."""
    total: int
    limit: int
    offset: int
    events: list[EventSummaryResponse]


class HealthResponse(BaseModel):
    """Stato di salute del servizio."""
    status: str = Field(description="'ok' | 'degraded' | 'down'")
    version: str
    environment: str = Field(default="unknown", description="development, staging, production")
    database: str = Field(description="Tipo e stato del database")
    entity_count: int
    uptime_seconds: float = Field(default=0.0, description="Secondi dall'avvio del processo")
    check_duration_ms: float = Field(default=0.0, description="Tempo speso in questo health check")
    sentry_active: bool = Field(default=False, description="Se Sentry sta catturando errori")
    checks: dict[str, str] = Field(
        default_factory=dict,
        description="Esito delle sotto-verifiche (database, seed, rate_limit, ...)",
    )
