"""Schemi Pydantic per le risposte API — vedi ADR-002."""

from pydantic import BaseModel, Field


class NameVariantResponse(BaseModel):
    """Name variant with historical context (ETHICS-001)."""
    name: str = Field(description="Name in the indicated language")
    lang: str = Field(description="ISO 639-1 language code")
    period_start: int | None = Field(None, description="Year usage began (negative = BCE)")
    period_end: int | None = Field(None, description="Year usage ended")
    context: str | None = Field(None, description="Historical-political context of the name")
    source: str | None = Field(None, description="Bibliographic source")

    model_config = {"from_attributes": True}


class TerritoryChangeResponse(BaseModel):
    """Territorial change with explicit change type (ETHICS-002)."""
    year: int = Field(description="Year of the change (negative = BCE)")
    region: str = Field(description="Region involved")
    change_type: str = Field(description="Type: CONQUEST_MILITARY, TREATY, COLONIZATION, etc.")
    description: str | None = Field(None, description="Description of the change")
    population_affected: int | None = Field(None, description="Estimated population affected")
    confidence_score: float = Field(description="Data reliability 0.0-1.0")

    model_config = {"from_attributes": True}


class SourceResponse(BaseModel):
    """Traceable bibliographic source."""
    citation: str = Field(description="Bibliographic citation")
    url: str | None = Field(None, description="Source URL")
    source_type: str = Field(description="Type: primary, secondary, academic")

    model_config = {"from_attributes": True}


class CapitalResponse(BaseModel):
    """Capital of the entity."""
    name: str
    lat: float
    lon: float


class CapitalHistoryResponse(BaseModel):
    """Historical capital with temporal range (v6.87 — ADR-004).

    For long-duration polities with multiple capitals (Ottoman, HRE, Mughal,
    Ming, Song, Solomonic Ethiopia, etc.). Enables 'capital of X in year Y'
    queries without anachronism.

    `lat/lon` may be null for polities with an itinerant court.
    `year_end` null = current or last capital.
    `ordering` for overlapping cases (e.g. dual monarchy Wien+Budapest).
    """
    name: str = Field(description="Name of the capital (local language, ETHICS-001)")
    lat: float | None = Field(None, description="Latitude (null for itinerant court)")
    lon: float | None = Field(None, description="Longitude")
    year_start: int = Field(description="Year the period as capital began")
    year_end: int | None = Field(None, description="End year (null = last/current)")
    ordering: int = Field(default=0, description="Secondary sort for overlapping periods")
    notes: str | None = Field(None, description="Explanation of the role")

    model_config = {"from_attributes": True}


class EntityResponse(BaseModel):
    """Full response for a single entity — format per ADR-002."""
    id: int
    entity_type: str = Field(description="Type: empire, kingdom, city-state, colony, disputed_territory")
    year_start: int = Field(description="Start year (negative = BCE)")
    year_end: int | None = Field(None, description="End year (null = still existing)")
    name_original: str = Field(description="Name in the original/local language (ETHICS-001)")
    name_original_lang: str = Field(description="ISO 639-1 language code")
    name_variants: list[NameVariantResponse] = Field(default_factory=list, description="Names in other languages with context")
    capital: CapitalResponse | None = None
    boundary_geojson: dict | None = Field(None, description="GeoJSON boundaries (Polygon or MultiPolygon)")
    # ETHICS-005: la tier di provenienza del confine. Permette al consumatore
    # di distinguere un poligono reale da uno generato senza ispezionare il
    # geojson. Valori: historical_map, natural_earth, aourednik,
    # academic_source, approximate_generated, approximate_circle (cerchio sulla
    # capitale, Phase H — ETHICS-012), historical_approximation (poligono storico
    # disegnato a mano).
    boundary_source: str | None = Field(
        None,
        description=(
            "Boundary provenance tier (ETHICS-005): historical_map, "
            "natural_earth, aourednik, academic_source, approximate_generated, "
            "approximate_circle, historical_approximation"
        ),
    )
    boundary_aourednik_name: str | None = Field(
        None,
        description="Exact name of the matched feature in aourednik/historical-basemaps (scientific reproducibility)",
    )
    boundary_aourednik_year: int | None = Field(
        None,
        description="Year of the aourednik snapshot used (one of the 53 available, -123000..2010)",
    )
    # v6.99.109 (agent-UX): flag machine-readable dell'anacronismo potenziale.
    boundary_reference_year: int | None = Field(
        None,
        description=(
            "Reference year of the polygon. The boundary is ONE STATIC snapshot "
            "for the entity's entire lifespan: when querying a year other than "
            "this one, the boundaries shown may be anachronistic (e.g. Mughal "
            "at maximum extent ~1700 even for queries about 1550). NULL = reference "
            "year unknown (generic approximation). Currently coincides with "
            "boundary_aourednik_year when the provenance is aourednik."
        ),
    )
    boundary_aourednik_precision: int | None = Field(
        None,
        description="BORDERPRECISION value from the aourednik upstream (historical-basemaps README): 1=approximate, 2=moderately precise, 3=determined by international law. Value 0 is a legacy edge-case (4 upstream features). Converts to confidence via PRECISION_CONFIDENCE (3->0.85, 2->0.70, 1->0.55, 0->0.45).",
    )
    boundary_ne_iso_a3: str | None = Field(
        None,
        description="ISO_A3 of the Natural Earth country when the match goes through NE",
    )
    confidence_score: float = Field(description="Overall reliability 0.0-1.0")
    status: str = Field(description="confirmed, uncertain, or disputed")
    territory_changes: list[TerritoryChangeResponse] = Field(default_factory=list, description="Territorial changes (ETHICS-002)")
    sources: list[SourceResponse] = Field(default_factory=list, description="Bibliographic sources")
    ethical_notes: str | None = Field(None, description="Notes on the ethical governance of the data")
    continent: str | None = Field(None, description="Continent derived from the capital's coordinates")
    # v6.69: Wikidata Q-ID per cross-reference (audit v4 Fase A).
    # ETHICS: identificatore di riferimento esterno, non fonte autoritativa —
    # usato per drift detection sistematico contro Wikidata.
    wikidata_qid: str | None = Field(
        None,
        description="Reference Wikidata Q-ID (format 'Q12345'). Null if no high-confidence match was found (audit v4, v6.69).",
    )
    # v6.87 ADR-004: capital history per polities con capitali multiple.
    capital_history: list[CapitalHistoryResponse] = Field(
        default_factory=list,
        description="Capital history for long-duration polities (ADR-004). Empty if the entity only has a single `capital`. Sorted by year_start ASC, then ordering.",
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
    """Paginated response for entity lists.

    v6.66 FIX 4: includes both `total` (standard) and `count` (legacy).
    `count` is deprecated but returned for backward compatibility for 1-2 releases.
    """
    total: int = Field(description="Total number of results matching the filters (before limit/offset)")
    count: int = Field(description="DEPRECATED (v6.66) — alias of `total`. Will be removed in v6.68.")
    limit: int = Field(description="Per-page limit")
    offset: int = Field(description="Current offset")
    entities: list[EntityResponse]
    # v6.99.109 (agent-UX): con 0 risultati, indica il retry-path invece di
    # un dead-end silenzioso (gli agenti abbandonavano dopo il primo 0-result).
    hint: str | None = Field(
        None,
        description="Present only when total=0 on name searches: suggests retrying via /v1/search/fuzzy",
    )


# ─── Wave 2.5 (audit API #1): response_model per gli endpoint headline ──────
# Modelli MIRROR-ESATTI dei dict restituiti dagli handler (stesse chiavi),
# campi Optional/permissivi così response_model NON elimina campi né solleva
# 500 su validazione. Scopo: l'OpenAPI spec espone schemi reali (non `{}`) sugli
# endpoint che gli agent AI usano per primi (/light, /batch, /events).


class LightEntityResponse(BaseModel):
    """Lightweight entity (without boundary_geojson) — see /v1/entities/light."""
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
    continent: str | None = Field(None, description="Continent derived from the capital coordinates")

    model_config = {"from_attributes": True}


class LightListResponse(BaseModel):
    """Response of /v1/entities/light — map bootstrap / agent overview."""
    total: int
    count: int = Field(description="DEPRECATED — alias of total (backward compat)")
    entities: list[LightEntityResponse]


class BatchResponse(BaseModel):
    """Response of /v1/entities/batch — multi-ID fetch in one round-trip."""
    requested: int
    found: int
    not_found: list[int] = Field(default_factory=list)
    entities: list[EntityResponse]


class EventSummaryResponse(BaseModel):
    """Historical event in compact form (lists) — mirrors _event_summary."""
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
    """Response of /v1/events (list)."""
    total: int
    limit: int
    offset: int
    events: list[EventSummaryResponse]


class HealthResponse(BaseModel):
    """Service health status."""
    status: str = Field(description="'ok' | 'degraded' | 'down'")
    version: str
    environment: str = Field(default="unknown", description="development, staging, production")
    database: str = Field(description="Database type and status")
    entity_count: int
    uptime_seconds: float = Field(default=0.0, description="Seconds since process start")
    check_duration_ms: float = Field(default=0.0, description="Time spent in this health check")
    sentry_active: bool = Field(default=False, description="Whether Sentry is capturing errors")
    checks: dict[str, str] = Field(
        default_factory=dict,
        description="Result of the sub-checks (database, seed, rate_limit, ...)",
    )
