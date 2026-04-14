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
    # academic_source, approximate_generated.
    boundary_source: str | None = Field(
        None,
        description="Tier di provenienza del confine (ETHICS-005): historical_map, natural_earth, aourednik, academic_source, approximate_generated",
    )
    boundary_aourednik_name: str | None = Field(
        None,
        description="Nome esatto della feature matchata in aourednik/historical-basemaps (riproducibilita' scientifica)",
    )
    boundary_aourednik_year: int | None = Field(
        None,
        description="Anno dello snapshot aourednik usato (uno dei 53 disponibili, -123000..2010)",
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
            }
        },
    }


class PaginatedEntityResponse(BaseModel):
    """Risposta paginata per liste di entità."""
    count: int = Field(description="Numero totale di risultati")
    limit: int = Field(description="Limite per pagina")
    offset: int = Field(description="Offset corrente")
    entities: list[EntityResponse]


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
