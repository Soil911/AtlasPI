"""Schemi Pydantic per le risposte API — vedi ADR-002."""

from pydantic import BaseModel


class NameVariantResponse(BaseModel):
    name: str
    lang: str
    period_start: int | None = None
    period_end: int | None = None
    context: str | None = None
    source: str | None = None

    model_config = {"from_attributes": True}


class TerritoryChangeResponse(BaseModel):
    year: int
    region: str
    change_type: str
    description: str | None = None
    population_affected: int | None = None
    confidence_score: float

    model_config = {"from_attributes": True}


class SourceResponse(BaseModel):
    citation: str
    url: str | None = None
    source_type: str

    model_config = {"from_attributes": True}


class CapitalResponse(BaseModel):
    name: str
    lat: float
    lon: float


class EntityResponse(BaseModel):
    """Risposta completa per una singola entità — formato da ADR-002."""

    id: int
    entity_type: str
    year_start: int
    year_end: int | None = None
    name_original: str
    name_original_lang: str
    name_variants: list[NameVariantResponse] = []
    capital: CapitalResponse | None = None
    boundary_geojson: dict | None = None
    confidence_score: float
    status: str
    territory_changes: list[TerritoryChangeResponse] = []
    sources: list[SourceResponse] = []
    ethical_notes: str | None = None

    model_config = {"from_attributes": True}


class EntityListResponse(BaseModel):
    count: int
    entities: list[EntityResponse]


class HealthResponse(BaseModel):
    status: str
    version: str
    entity_count: int
