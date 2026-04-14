"""Definizioni dei tools MCP esposti da atlaspi-mcp.

Ogni tool e' una struct con:
- ``name``     : identificatore snake_case (cosa l'agente chiama)
- ``description``: testo verboso che spiega *quando* usare il tool
  (e' quello che il modello legge per decidere)
- ``input_schema``: JSON Schema dei parametri di input
- ``handler``  : coroutine ``(client, args) -> dict`` che chiama l'API

I tools sono pensati per la *retrieval-augmented* di domande storiche
geografiche: l'agente puo' combinarli per costruire risposte ricche
(es. snapshot + nearby + evolution).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from atlaspi_mcp.client import AtlasPIClient

# Tipo del callable handler di un tool MCP.
ToolHandler = Callable[[AtlasPIClient, dict[str, Any]], Awaitable[Any]]


@dataclass(frozen=True)
class ToolDefinition:
    """Definizione dichiarativa di un tool MCP."""

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: ToolHandler


# ------------------------------------------------------------------ #
# Sotto-schemi riusabili                                              #
# ------------------------------------------------------------------ #

_YEAR_SCHEMA: dict[str, Any] = {
    "type": "integer",
    "minimum": -4500,
    "maximum": 2100,
    "description": (
        "Anno (intero). Anni negativi rappresentano date a.C. "
        "Esempi: -300 = 300 a.C., 476 = 476 d.C."
    ),
}

_STATUS_SCHEMA: dict[str, Any] = {
    "type": "string",
    "enum": ["confirmed", "uncertain", "disputed"],
    "description": (
        "Livello di certezza storica del record. 'disputed' indica voci "
        "con confidence_score basso o controverse fra storici."
    ),
}

_CONTINENT_SCHEMA: dict[str, Any] = {
    "type": "string",
    "description": (
        "Continente o macro-regione. Valori comuni: Europe, Asia, Africa, "
        "Americas, Middle East, Oceania."
    ),
}

_TYPE_SCHEMA: dict[str, Any] = {
    "type": "string",
    "description": (
        "Tipo di entita' geopolitica. Esempi: empire, kingdom, republic, "
        "city-state, sultanate, caliphate, khanate, dynasty, principality, "
        "confederation, federation, duchy, colony, disputed_territory, city."
    ),
}


# ------------------------------------------------------------------ #
# Handler                                                              #
# ------------------------------------------------------------------ #

async def _h_search_entities(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.search_entities(
        name=args.get("name"),
        year=args.get("year"),
        type=args.get("type"),
        continent=args.get("continent"),
        status=args.get("status"),
        sort=args.get("sort"),
        order=args.get("order"),
        limit=args.get("limit"),
        offset=args.get("offset"),
    )


async def _h_get_entity(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.get_entity(int(args["entity_id"]))


async def _h_snapshot(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.snapshot(
        int(args["year"]),
        type=args.get("type"),
        continent=args.get("continent"),
    )


async def _h_nearby(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.nearby(
        lat=float(args["lat"]),
        lon=float(args["lon"]),
        radius=args.get("radius"),
        year=args.get("year"),
        limit=args.get("limit"),
    )


async def _h_compare(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.compare(int(args["id1"]), int(args["id2"]))


async def _h_random(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.random(
        type=args.get("type"),
        year=args.get("year"),
        status=args.get("status"),
        continent=args.get("continent"),
    )


async def _h_evolution(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.evolution(int(args["entity_id"]))


async def _h_stats(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.stats()


# ------------------------------------------------------------------ #
# Definizioni tools                                                    #
# ------------------------------------------------------------------ #

TOOLS: list[ToolDefinition] = [
    ToolDefinition(
        name="search_entities",
        description=(
            "Cerca entita' geopolitiche storiche nel database AtlasPI applicando "
            "filtri combinabili su nome, anno, tipo, continente e status. "
            "Usa questo tool quando l'utente chiede di trovare imperi, regni, "
            "repubbliche, citta'-stato, sultanati, ducati, ecc. con criteri "
            "specifici (es: 'tutti gli imperi attivi nel 100 a.C. in Asia'). "
            "Ritorna un elenco paginato con id, nome originale, lingua, intervallo "
            "temporale, capitale e geometria GeoJSON. Per dettagli completi su una "
            "singola entita', usa get_entity con l'id ottenuto qui."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": (
                        "Nome (anche parziale) dell'entita'. Cerca sia nel nome "
                        "originale che nelle varianti linguistiche."
                    ),
                    "maxLength": 200,
                },
                "year": {
                    **_YEAR_SCHEMA,
                    "description": _YEAR_SCHEMA["description"]
                    + " Filtra entita' attive in quest'anno.",
                },
                "type": _TYPE_SCHEMA,
                "continent": _CONTINENT_SCHEMA,
                "status": _STATUS_SCHEMA,
                "sort": {
                    "type": "string",
                    "enum": ["name", "year_start", "year_end", "confidence"],
                    "description": "Campo di ordinamento dei risultati.",
                },
                "order": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "Direzione di ordinamento (default: asc).",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Numero massimo di risultati (default: 20).",
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Offset per paginazione (default: 0).",
                },
            },
            "additionalProperties": False,
        },
        handler=_h_search_entities,
    ),
    ToolDefinition(
        name="get_entity",
        description=(
            "Recupera il dettaglio completo di una entita' storica dato il suo id "
            "numerico. Ritorna nome originale e lingua, varianti linguistiche con "
            "fonti, capitale (nome + coordinate), confine GeoJSON, intervallo "
            "temporale, confidence_score, fonti citate e metadati storici. "
            "Usa questo tool dopo search_entities o snapshot_at_year per "
            "approfondire una specifica entita'."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "ID numerico dell'entita' nel database AtlasPI.",
                },
            },
            "required": ["entity_id"],
            "additionalProperties": False,
        },
        handler=_h_get_entity,
    ),
    ToolDefinition(
        name="snapshot_at_year",
        description=(
            "Restituisce uno snapshot del mondo in un dato anno: tutte le entita' "
            "geopolitiche attive in quell'anno (year_start <= anno <= year_end), "
            "con possibilita' di filtrare per tipo o continente. "
            "Usa questo tool per domande del tipo 'che mappa politica c'era nel "
            "300 a.C.?' o 'quali regni esistevano in Africa nel 1500?'. "
            "Ricorda: gli anni negativi sono a.C."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "year": _YEAR_SCHEMA,
                "type": _TYPE_SCHEMA,
                "continent": _CONTINENT_SCHEMA,
            },
            "required": ["year"],
            "additionalProperties": False,
        },
        handler=_h_snapshot,
    ),
    ToolDefinition(
        name="nearby_entities",
        description=(
            "Trova le entita' geopolitiche piu' vicine a una coppia di coordinate "
            "(latitudine, longitudine) attive in un dato anno. Ordina per distanza "
            "geodetica dalla capitale dell'entita'. "
            "Usa questo tool per domande del tipo 'cosa c'era vicino a "
            "lat 41.9, lon 12.5 nel 100 d.C.?' (cioe' Roma) o 'quali entita' "
            "circondavano queste coordinate nel medioevo?'."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "lat": {
                    "type": "number",
                    "minimum": -90,
                    "maximum": 90,
                    "description": "Latitudine in gradi decimali (WGS84).",
                },
                "lon": {
                    "type": "number",
                    "minimum": -180,
                    "maximum": 180,
                    "description": "Longitudine in gradi decimali (WGS84).",
                },
                "radius": {
                    "type": "number",
                    "minimum": 1,
                    "maximum": 20000,
                    "description": (
                        "Raggio di ricerca in chilometri (default: 500). "
                        "Aumenta per regioni a bassa densita' di entita'."
                    ),
                },
                "year": {
                    **_YEAR_SCHEMA,
                    "description": _YEAR_SCHEMA["description"]
                    + " Se omesso, considera tutte le epoche.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "description": "Numero massimo di entita' da ritornare (default: 10).",
                },
            },
            "required": ["lat", "lon"],
            "additionalProperties": False,
        },
        handler=_h_nearby,
    ),
    ToolDefinition(
        name="compare_entities",
        description=(
            "Confronta due entita' storiche dato il loro id numerico. Ritorna un "
            "report strutturato con sovrapposizione temporale, differenze di "
            "estensione territoriale, diversita' di status, capitali e fonti. "
            "Utile per domande comparative tipo 'paragona Roma Repubblicana e "
            "Impero Bizantino' o 'che differenze ci sono tra il Sacro Romano "
            "Impero e l'Impero Carolingio?'."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "id1": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "ID della prima entita'.",
                },
                "id2": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "ID della seconda entita'.",
                },
            },
            "required": ["id1", "id2"],
            "additionalProperties": False,
        },
        handler=_h_compare,
    ),
    ToolDefinition(
        name="random_entity",
        description=(
            "Restituisce una entita' storica casuale, opzionalmente filtrata per "
            "tipo, anno, continente o status. Pensato per esplorazione, "
            "suggerimenti, generazione di curiosita' storiche o per permettere "
            "all'agente di proporre 'lo sapevi che...' contestuali. "
            "Esempio: random_entity(type='khanate', continent='Asia') ritorna un "
            "khanato asiatico a caso."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "type": _TYPE_SCHEMA,
                "year": _YEAR_SCHEMA,
                "status": _STATUS_SCHEMA,
                "continent": _CONTINENT_SCHEMA,
            },
            "additionalProperties": False,
        },
        handler=_h_random,
    ),
    ToolDefinition(
        name="get_evolution",
        description=(
            "Restituisce la timeline dei cambi territoriali di una entita': "
            "annessioni, perdite di territorio, cambi di capitale, transizioni di "
            "regime, eventi di scissione o unificazione. Ogni evento ha anno, "
            "descrizione, fonte e (quando disponibile) acquisition_method per "
            "documentare se un territorio fu acquisito per conquista, "
            "matrimonio dinastico, trattato, ecc. "
            "Importante per ricostruire l'arco storico di un'entita' nel tempo."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "ID dell'entita' di cui ricostruire l'evoluzione.",
                },
            },
            "required": ["entity_id"],
            "additionalProperties": False,
        },
        handler=_h_evolution,
    ),
    ToolDefinition(
        name="dataset_stats",
        description=(
            "Restituisce statistiche aggregate del dataset AtlasPI: numero totale "
            "di entita', breakdown per tipo, distribuzione per status (confirmed / "
            "uncertain / disputed), distribuzione per continente, intervallo "
            "temporale coperto (year_range), confidence_score medio, numero totale "
            "di fonti citate e di cambi territoriali. "
            "Utile come tool di scoperta iniziale per capire la copertura del "
            "dataset prima di formulare query specifiche."
        ),
        input_schema={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        handler=_h_stats,
    ),
]


def get_tools() -> list[ToolDefinition]:
    """Ritorna l'elenco completo dei tools MCP esposti."""
    return list(TOOLS)


def get_tool(name: str) -> ToolDefinition:
    """Cerca un tool per nome.

    Solleva ``KeyError`` se il nome non corrisponde ad alcun tool.
    """
    for tool in TOOLS:
        if tool.name == name:
            return tool
    raise KeyError(f"Unknown tool: {name!r}")
