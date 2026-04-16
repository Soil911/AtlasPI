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

import math
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


async def _h_similar(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.similar(
        int(args["entity_id"]),
        limit=int(args.get("limit", 10)),
        min_score=float(args.get("min_score", 0.3)),
    )


async def _h_stats(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.stats()


# -- v6.3 events ---------------------------------------------------


async def _h_list_events(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.list_events(
        year_min=args.get("year_min"),
        year_max=args.get("year_max"),
        event_type=args.get("event_type"),
        status=args.get("status"),
        known_silence=args.get("known_silence"),
        limit=args.get("limit"),
        offset=args.get("offset"),
    )


async def _h_get_event(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.get_event(int(args["event_id"]))


async def _h_events_for_entity(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.events_for_entity(
        int(args["entity_id"]),
        role=args.get("role"),
    )


# -- v6.23 events for map + on this day ----------------------------


async def _h_events_for_map(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.events_for_map(
        year=int(args["year"]),
        window=args.get("window"),
        limit=args.get("limit"),
    )


async def _h_on_this_day(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.on_this_day(str(args["mm_dd"]))


# -- v6.4 cities & routes ------------------------------------------


async def _h_list_cities(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.list_cities(
        year=args.get("year"),
        city_type=args.get("city_type"),
        entity_id=args.get("entity_id"),
        bbox=args.get("bbox"),
        status=args.get("status"),
        limit=args.get("limit"),
        offset=args.get("offset"),
    )


async def _h_get_city(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.get_city(int(args["city_id"]))


async def _h_list_routes(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.list_routes(
        year=args.get("year"),
        route_type=args.get("route_type"),
        involves_slavery=args.get("involves_slavery"),
        status=args.get("status"),
        limit=args.get("limit"),
        offset=args.get("offset"),
    )


async def _h_get_route(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.get_route(int(args["route_id"]))


# -- v6.5 chains ---------------------------------------------------


async def _h_list_chains(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.list_chains(
        chain_type=args.get("chain_type"),
        region=args.get("region"),
        year=args.get("year"),
        status=args.get("status"),
        limit=args.get("limit"),
        offset=args.get("offset"),
    )


async def _h_get_chain(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.get_chain(int(args["chain_id"]))


async def _h_predecessors(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.entity_predecessors(int(args["entity_id"]))


async def _h_successors(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    return await client.entity_successors(int(args["entity_id"]))


# -- composite ---------------------------------------------------


async def _h_full_timeline_for_entity(
    client: AtlasPIClient, args: dict[str, Any]
) -> Any:
    """Restituisce la timeline unificata (eventi + territory + catene) di un'entità."""
    return await client.full_timeline(
        int(args["entity_id"]),
        include_entity_links=args.get("include_entity_links"),
    )


async def _h_fuzzy_search(client: AtlasPIClient, args: dict[str, Any]) -> Any:
    """Ricerca approssimata cross-script sui nomi delle entità."""
    return await client.fuzzy_search(
        str(args["q"]),
        limit=args.get("limit"),
        min_score=args.get("min_score"),
    )


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distanza geodetica (km) tra due coppie di coordinate (WGS84)."""
    r = 6371.0  # raggio medio della Terra in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


async def _h_nearest_historical_city(
    client: AtlasPIClient, args: dict[str, Any]
) -> Any:
    """Trova le città storiche più vicine a una coppia di coordinate.

    Composizione client-side: non esiste un endpoint /v1/cities/nearest.
    Scarica fino a ``max_candidates`` città (filtrate per anno e tipo se
    specificati), calcola la distanza haversine in Python, ordina per
    distanza crescente e ritorna le prime ``limit``.
    """
    lat = float(args["lat"])
    lon = float(args["lon"])
    year = args.get("year")
    city_type = args.get("city_type")
    limit = int(args.get("limit", 5) or 5)
    max_candidates = int(args.get("max_candidates", 500) or 500)

    payload = await client.nearest_historical_city(
        lat=lat,
        lon=lon,
        year=year,
        city_type=city_type,
        limit=limit,
        max_candidates=max_candidates,
    )

    results: list[dict[str, Any]] = []
    for city in payload.get("cities", []):
        if not isinstance(city, dict):
            continue
        c_lat = city.get("lat") or city.get("latitude")
        c_lon = city.get("lon") or city.get("longitude")
        if c_lat is None or c_lon is None:
            continue
        try:
            dist = _haversine_km(lat, lon, float(c_lat), float(c_lon))
        except (TypeError, ValueError):
            continue
        results.append(
            {
                "id": city.get("id"),
                "name_original": city.get("name_original"),
                "name_original_lang": city.get("name_original_lang"),
                "city_type": city.get("city_type"),
                "lat": float(c_lat),
                "lon": float(c_lon),
                "year_founded": city.get("year_founded"),
                "year_abandoned": city.get("year_abandoned"),
                "status": city.get("status"),
                "distance_km": round(dist, 2),
            }
        )

    results.sort(key=lambda r: r["distance_km"])
    top = results[:limit]

    return {
        "query": {
            "lat": lat,
            "lon": lon,
            "year": year,
            "city_type": city_type,
            "limit": limit,
        },
        "candidates_considered": payload.get("candidates_considered", len(results)),
        "count": len(top),
        "cities": top,
    }


async def _h_what_changed_between(
    client: AtlasPIClient, args: dict[str, Any]
) -> Any:
    """Diff macro-storico fra due snapshot del mondo.

    Combina ``snapshot(year1)`` e ``snapshot(year2)``, poi lista:
      * ``appeared``   — entità attive a year2 ma non a year1
      * ``disappeared``— entità attive a year1 ma non a year2
      * ``persisted``  — entità attive in entrambe (id list, non full payload)

    È una composizione client-side: non corrisponde a un endpoint server.
    """
    year1 = int(args["year1"])
    year2 = int(args["year2"])
    if year1 == year2:
        raise ValueError("year1 and year2 must be different")

    type_filter = args.get("type")
    continent_filter = args.get("continent")

    snap1 = await client.snapshot(year1, type=type_filter, continent=continent_filter)
    snap2 = await client.snapshot(year2, type=type_filter, continent=continent_filter)

    def _id_name(entities: list[dict[str, Any]]) -> dict[int, str]:
        return {
            int(e["id"]): e.get("name_original", "")
            for e in entities
            if isinstance(e, dict) and "id" in e
        }

    ids1 = _id_name(snap1.get("entities", []))
    ids2 = _id_name(snap2.get("entities", []))
    set1 = set(ids1.keys())
    set2 = set(ids2.keys())

    appeared = [{"id": i, "name_original": ids2[i]} for i in sorted(set2 - set1)]
    disappeared = [{"id": i, "name_original": ids1[i]} for i in sorted(set1 - set2)]
    persisted_ids = sorted(set1 & set2)

    return {
        "year1": year1,
        "year2": year2,
        "filter": {"type": type_filter, "continent": continent_filter},
        "count": {
            "appeared": len(appeared),
            "disappeared": len(disappeared),
            "persisted": len(persisted_ids),
            "year1_total": len(set1),
            "year2_total": len(set2),
        },
        "appeared": appeared,
        "disappeared": disappeared,
        "persisted_ids": persisted_ids,
    }


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
        name="find_similar_entities",
        description=(
            "Trova entita' storiche simili a quella specificata, ordinate per "
            "punteggio di similarita' (0.0-1.0). Il punteggio considera: tipo di "
            "entita' (35%), sovrapposizione temporale (30%), durata simile (15%), "
            "confidence simile (10%), stesso status (10%). "
            "Usa questo tool quando l'utente chiede 'quali imperi erano simili a "
            "Roma?' o 'trova stati paragonabili al Sacro Romano Impero' o "
            "'suggerisci paralleli storici per l'Impero Mongolo'. "
            "Il risultato include id, nome, tipo, periodo e punteggio per ogni "
            "entita' simile."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "ID dell'entita' di riferimento.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                    "description": "Numero massimo di risultati.",
                },
                "min_score": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.3,
                    "description": "Punteggio minimo di similarita'.",
                },
            },
            "required": ["entity_id"],
            "additionalProperties": False,
        },
        handler=_h_similar,
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
    # ─── v6.3 events ────────────────────────────────────────────────
    ToolDefinition(
        name="search_events",
        description=(
            "Cerca eventi storici con filtri su anno, tipo, status e silenzio "
            "documentato. ETHICS-007: i tipi usano termini espliciti — GENOCIDE, "
            "COLONIAL_VIOLENCE, ETHNIC_CLEANSING, MASSACRE, DEPORTATION — senza "
            "eufemismi. Per domande tipo 'quali genocidi sono registrati nel XX "
            "secolo?' (event_type='GENOCIDE', year_min=1900, year_max=2000). "
            "ETHICS-008: known_silence=true filtra eventi storicamente insabbiati "
            "(es. genocidio armeno nella storiografia turca)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "year_min": {
                    **_YEAR_SCHEMA,
                    "description": _YEAR_SCHEMA["description"]
                    + " Limite inferiore (incluso).",
                },
                "year_max": {
                    **_YEAR_SCHEMA,
                    "description": _YEAR_SCHEMA["description"]
                    + " Limite superiore (incluso).",
                },
                "event_type": {
                    "type": "string",
                    "description": (
                        "Tipo di evento (EventType). Esempi: BATTLE, SIEGE, "
                        "TREATY, REBELLION, REVOLUTION, CONQUEST, "
                        "COLONIAL_VIOLENCE, GENOCIDE, ETHNIC_CLEANSING, "
                        "MASSACRE, DEPORTATION, FAMINE, EPIDEMIC, EARTHQUAKE, "
                        "VOLCANIC_ERUPTION, TSUNAMI, FLOOD, DROUGHT, FIRE, "
                        "EXPLORATION, TRADE_AGREEMENT, RELIGIOUS_EVENT, "
                        "INTELLECTUAL_EVENT, TECHNOLOGICAL_EVENT."
                    ),
                },
                "status": _STATUS_SCHEMA,
                "known_silence": {
                    "type": "boolean",
                    "description": (
                        "ETHICS-008: true = solo eventi con documentazione "
                        "contemporanea insabbiata/cancellata."
                    ),
                },
                "limit": {
                    "type": "integer", "minimum": 1, "maximum": 500,
                    "description": "Numero massimo di risultati (default: 50).",
                },
                "offset": {"type": "integer", "minimum": 0},
            },
            "additionalProperties": False,
        },
        handler=_h_list_events,
    ),
    ToolDefinition(
        name="get_event",
        description=(
            "Dettaglio completo di un evento storico dato il suo id: tipo, "
            "anno, descrizione, entità coinvolte con ruolo esplicito "
            "(MAIN_ACTOR, VICTIM, PARTICIPANT, AFFECTED, WITNESS, FOUNDED, "
            "DISSOLVED), fonti con page/confidence, ethical_notes. "
            "ETHICS-007: il main_actor è sempre presente — la voce attiva "
            "('chi ha fatto cosa a chi') è obbligatoria per eventi di violenza."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "event_id": {"type": "integer", "minimum": 1},
            },
            "required": ["event_id"],
            "additionalProperties": False,
        },
        handler=_h_get_event,
    ),
    ToolDefinition(
        name="events_for_entity",
        description=(
            "Restituisce tutti gli eventi storici in cui una data entità compare "
            "(fondazione, conquiste, eventi subiti, dissoluzione). Filtro "
            "opzionale su role (MAIN_ACTOR, VICTIM, ecc.). Usa questo tool "
            "dopo get_entity/search_entities per ricostruire la storia "
            "eventuale di una specifica entità (es. 'quali eventi ha subito "
            "l'Impero Ottomano?'). Distingue tra ruoli attivi (conquiste "
            "operate) e subiti (conquiste ricevute, genocidi, colonizzazioni)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "entity_id": {"type": "integer", "minimum": 1},
                "role": {
                    "type": "string",
                    "description": (
                        "Ruolo dell'entità nell'evento. Esempi: MAIN_ACTOR, "
                        "VICTIM, PARTICIPANT, AFFECTED, WITNESS, FOUNDED, "
                        "DISSOLVED."
                    ),
                },
            },
            "required": ["entity_id"],
            "additionalProperties": False,
        },
        handler=_h_events_for_entity,
    ),
    # ─── v6.23 events for map + on this day ───────────────────────
    ToolDefinition(
        name="events_for_map",
        description=(
            "Recupera gli eventi storici geolocalizzati attorno a un dato anno, "
            "ottimizzato per la visualizzazione su mappa. Restituisce un payload "
            "leggero (10 campi per evento) con solo eventi che hanno coordinate. "
            "La finestra temporale si auto-espande per epoche antiche: ±50 anni "
            "per anni < -1000 a.C., ±25 per il periodo classico, ±10 per l'età "
            "moderna. Usa questo tool quando l'utente chiede 'cosa è successo "
            "vicino a [luogo] nel [anno]?' o per popolare una visualizzazione "
            "mappa con eventi. Non include description/sources — usa get_event "
            "per i dettagli di un singolo evento."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "year": _YEAR_SCHEMA,
                "window": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 500,
                    "description": (
                        "Semi-ampiezza della finestra temporale in anni "
                        "(default: 10, auto-espansa per epoche antiche)."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 500,
                    "description": "Numero massimo di eventi (default: 200).",
                },
            },
            "required": ["year"],
            "additionalProperties": False,
        },
        handler=_h_events_for_map,
    ),
    ToolDefinition(
        name="on_this_day",
        description=(
            "Restituisce gli eventi storici avvenuti in una specifica data "
            "del calendario (mese e giorno), attraverso tutti gli anni nel "
            "dataset. Formato: MM-DD (es. '07-04' per il 4 luglio, '10-12' "
            "per il 12 ottobre). Utile per curiosità storiche, efemeridi, "
            "quiz, contenuti 'accadde oggi'. Esempio: on_this_day('10-12') "
            "potrebbe restituire lo sbarco di Colombo (1492) e il giorno "
            "della scoperta del Nuovo Mondo."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "mm_dd": {
                    "type": "string",
                    "pattern": r"^\d{2}-\d{2}$",
                    "description": (
                        "Data nel formato MM-DD (es. '12-25' per Natale, "
                        "'07-14' per il 14 luglio). Il mese è 01-12, il "
                        "giorno 01-31."
                    ),
                },
            },
            "required": ["mm_dd"],
            "additionalProperties": False,
        },
        handler=_h_on_this_day,
    ),
    # ─── v6.4 cities ────────────────────────────────────────────────
    ToolDefinition(
        name="search_cities",
        description=(
            "Cerca città storiche con filtri su anno di attività, tipo "
            "funzionale (CAPITAL, TRADE_HUB, RELIGIOUS_CENTER, FORTRESS, "
            "PORT, ACADEMIC_CENTER, INDUSTRIAL_CENTER, MULTI_PURPOSE), "
            "entità politica di appartenenza, bbox geografica. Una città è "
            "separata dalla capital_* di GeoEntity perché può sopravvivere "
            "più entità politiche (es. Costantinopoli/Istanbul attraversa "
            "Bizantino → Ottomano → Repubblica di Turchia)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "year": {
                    **_YEAR_SCHEMA,
                    "description": _YEAR_SCHEMA["description"]
                    + " Città attiva in quell'anno.",
                },
                "city_type": {
                    "type": "string",
                    "description": (
                        "CAPITAL / TRADE_HUB / RELIGIOUS_CENTER / FORTRESS / "
                        "PORT / ACADEMIC_CENTER / INDUSTRIAL_CENTER / "
                        "MULTI_PURPOSE / OTHER."
                    ),
                },
                "entity_id": {
                    "type": "integer", "minimum": 1,
                    "description": "ID dell'entità politica di appartenenza.",
                },
                "bbox": {
                    "type": "string",
                    "description": (
                        "Bounding box geografica. Formato CSV: "
                        "min_lon,min_lat,max_lon,max_lat"
                    ),
                },
                "status": _STATUS_SCHEMA,
                "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                "offset": {"type": "integer", "minimum": 0},
            },
            "additionalProperties": False,
        },
        handler=_h_list_cities,
    ),
    ToolDefinition(
        name="get_city",
        description=(
            "Dettaglio di una città storica: nome originale, varianti "
            "linguistiche e storiche (ETHICS-009: rename coloniali/imperiali "
            "documentati — es. Konstantinoupolis → Istanbul, Königsberg → "
            "Kaliningrad, Tenochtitlan → Ciudad de México, Calcutta → "
            "Kolkata), coordinate, tipo, population_peak, fonti, entità "
            "politica corrente. Usa dopo search_cities per approfondire."
        ),
        input_schema={
            "type": "object",
            "properties": {"city_id": {"type": "integer", "minimum": 1}},
            "required": ["city_id"],
            "additionalProperties": False,
        },
        handler=_h_get_city,
    ),
    # ─── v6.4 routes ────────────────────────────────────────────────
    ToolDefinition(
        name="search_routes",
        description=(
            "Cerca rotte commerciali storiche con filtri su anno di attività, "
            "tipo geografico (LAND, SEA, RIVER, CARAVAN, MIXED) e "
            "involves_slavery. ETHICS-010: involves_slavery=true restituisce "
            "le rotte che trafficavano esseri umani schiavizzati come merce "
            "primaria (Trans-Atlantic, Trans-Saharan Slave, Indian Ocean Slave "
            "Route). Il flag è esplicito perché la distinzione è eticamente "
            "rilevante. Nota: 'Silk Road' è attribuzione 1877 di Richthofen, "
            "non un'auto-designazione delle carovane storiche."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "year": {
                    **_YEAR_SCHEMA,
                    "description": _YEAR_SCHEMA["description"]
                    + " Rotta attiva in quell'anno.",
                },
                "route_type": {
                    "type": "string",
                    "enum": ["LAND", "SEA", "RIVER", "CARAVAN", "MIXED"],
                    "description": (
                        "LAND=terrestre ordinaria; CARAVAN=carovane con "
                        "caravanserragli; SEA=marittima; RIVER=fluviale; "
                        "MIXED=intermodale."
                    ),
                },
                "involves_slavery": {
                    "type": "boolean",
                    "description": (
                        "ETHICS-010: true = rotte che trafficavano esseri "
                        "umani schiavizzati come merce primaria."
                    ),
                },
                "status": _STATUS_SCHEMA,
                "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                "offset": {"type": "integer", "minimum": 0},
            },
            "additionalProperties": False,
        },
        handler=_h_list_routes,
    ),
    ToolDefinition(
        name="get_route",
        description=(
            "Dettaglio di una rotta commerciale: nome originale, tipo "
            "geografico, intervallo temporale, waypoints (città attraversate "
            "in ordine) con coordinate, commodities principali, flag "
            "involves_slavery, geometry_geojson per visualizzazione, "
            "ethical_notes dettagliate. ETHICS-010: le rotte della tratta "
            "atlantica documentano le stime di Middle Passage (~1.8M morti "
            "su 12.5M embarcati)."
        ),
        input_schema={
            "type": "object",
            "properties": {"route_id": {"type": "integer", "minimum": 1}},
            "required": ["route_id"],
            "additionalProperties": False,
        },
        handler=_h_get_route,
    ),
    # ─── v6.5 chains ────────────────────────────────────────────────
    ToolDefinition(
        name="search_chains",
        description=(
            "Cerca catene successorie/dinastiche/coloniali con filtri su "
            "chain_type (DYNASTY / SUCCESSION / RESTORATION / COLONIAL / "
            "IDEOLOGICAL / OTHER), region, year (almeno un'entità della "
            "catena attiva in quell'anno), status. ETHICS-002: ogni link "
            "ha transition_type esplicito (CONQUEST / REVOLUTION / REFORM / "
            "SUCCESSION / DECOLONIZATION / PARTITION / UNIFICATION / "
            "DISSOLUTION / ANNEXATION) — non esiste 'succession' generico che "
            "maschera violenze. ETHICS-003: chain_type=IDEOLOGICAL (es. "
            "Sacrum Imperium Romanum → Deutsches Kaiserreich → Deutsches "
            "Reich) porta avvertimento che la continuità self-proclaimed "
            "non implica legittimità."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "chain_type": {
                    "type": "string",
                    "enum": [
                        "DYNASTY", "SUCCESSION", "RESTORATION",
                        "COLONIAL", "IDEOLOGICAL", "OTHER",
                    ],
                },
                "region": {
                    "type": "string",
                    "description": (
                        "Substring case-insensitive sulla regione "
                        "(es. 'Mediterranean', 'East Asia')."
                    ),
                },
                "year": {
                    **_YEAR_SCHEMA,
                    "description": _YEAR_SCHEMA["description"]
                    + " Almeno un'entità della catena attiva in quell'anno.",
                },
                "status": _STATUS_SCHEMA,
                "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                "offset": {"type": "integer", "minimum": 0},
            },
            "additionalProperties": False,
        },
        handler=_h_list_chains,
    ),
    ToolDefinition(
        name="get_chain",
        description=(
            "Dettaglio di una catena successoria con tutti i link in ordine "
            "cronologico. Ogni link ha sequence_order, entità di riferimento, "
            "transition_year, transition_type (ETHICS-002: esplicito, no "
            "eufemismi), is_violent, description e ethical_notes specifiche "
            "per la singola transizione. Usa dopo search_chains."
        ),
        input_schema={
            "type": "object",
            "properties": {"chain_id": {"type": "integer", "minimum": 1}},
            "required": ["chain_id"],
            "additionalProperties": False,
        },
        handler=_h_get_chain,
    ),
    ToolDefinition(
        name="entity_predecessors",
        description=(
            "Restituisce le catene in cui l'entità data ha un predecessore "
            "(sequence_order > 0), insieme al predecessore immediato, "
            "transition_year, transition_type, is_violent e ethical_notes "
            "della transizione CHE HA PORTATO A questa entità. Usa per "
            "domande tipo 'che entità ha preceduto la Repubblica di "
            "Turchia?' (→ Ottoman Empire, transition 1923 REVOLUTION)."
        ),
        input_schema={
            "type": "object",
            "properties": {"entity_id": {"type": "integer", "minimum": 1}},
            "required": ["entity_id"],
            "additionalProperties": False,
        },
        handler=_h_predecessors,
    ),
    ToolDefinition(
        name="entity_successors",
        description=(
            "Restituisce le catene in cui l'entità data ha un successore, "
            "insieme al successore immediato, transition_year, "
            "transition_type, is_violent e ethical_notes della transizione "
            "CHE HA PORTATO DA questa entità all'entità successiva. Usa per "
            "domande tipo 'cosa è venuto dopo Tawantinsuyu?' (→ Viceroyalty "
            "of Peru, transition 1542 CONQUEST)."
        ),
        input_schema={
            "type": "object",
            "properties": {"entity_id": {"type": "integer", "minimum": 1}},
            "required": ["entity_id"],
            "additionalProperties": False,
        },
        handler=_h_successors,
    ),
    # ─── v6.7 unified timeline + fuzzy search ───────────────────────
    ToolDefinition(
        name="full_timeline_for_entity",
        description=(
            "Restituisce la timeline unificata di un'entità: eventi storici "
            "(via EventEntityLink), cambi territoriali e transizioni di "
            "catene successorie (predecessori + successori) in un unico "
            "stream ordinato cronologicamente. Ogni voce ha un campo "
            "discriminatore 'kind' fra 'event', 'territory_change' e "
            "'chain_transition'. Usa questo tool invece di chiamare "
            "get_evolution + events_for_entity + entity_predecessors + "
            "entity_successors separatamente quando l'utente chiede la "
            "storia completa di un'entità (es. 'raccontami tutta la storia "
            "dell'Impero Romano d'Oriente'). Ritorna counts per ogni kind "
            "piu' lo stream unificato."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "ID dell'entità di cui ricostruire la timeline completa.",
                },
                "include_entity_links": {
                    "type": "boolean",
                    "description": (
                        "Se true (default), include nei risultati i link "
                        "EventEntityLink per ogni evento (ruolo dell'entità: "
                        "MAIN_ACTOR, VICTIM, ecc.). Se false, ritorna solo "
                        "i metadati base degli eventi."
                    ),
                },
            },
            "required": ["entity_id"],
            "additionalProperties": False,
        },
        handler=_h_full_timeline_for_entity,
    ),
    ToolDefinition(
        name="fuzzy_search",
        description=(
            "Ricerca approssimata (fuzzy) sui nomi delle entità storiche — "
            "tollera errori di spelling, trascrizioni diverse e script "
            "differenti. Usa difflib.SequenceMatcher a livello di caratteri "
            "Unicode, quindi funziona anche cross-script (latino, cirillico, "
            "arabo, cinese, devanagari, ecc.). Esempio: q='safavid' trova "
            "'دولت صفویه' (script arabo), q='Constantinople' trova "
            "'Κωνσταντινούπολις' (script greco). Preferisci questo tool "
            "quando search_entities non trova risultati per via di "
            "translitterazione non standard o spelling approssimativo."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 200,
                    "description": (
                        "Query di ricerca. Può essere in qualsiasi script; "
                        "l'algoritmo confronta char-by-char quindi è "
                        "robusto anche a omissioni e refusi."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "description": "Numero massimo di risultati (default: 20).",
                },
                "min_score": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": (
                        "Soglia minima di similarità (0.0-1.0, default 0.4). "
                        "Valori bassi (<0.4) producono match rumorosi; "
                        "valori alti (>0.7) richiedono match quasi esatti."
                    ),
                },
            },
            "required": ["q"],
            "additionalProperties": False,
        },
        handler=_h_fuzzy_search,
    ),
    ToolDefinition(
        name="nearest_historical_city",
        description=(
            "Trova le città storiche più vicine a una coppia di coordinate "
            "(latitudine, longitudine), opzionalmente filtrate per anno di "
            "attività e tipo (CAPITAL, TRADE_HUB, ecc.). Calcola la "
            "distanza haversine client-side e ordina per distanza "
            "crescente. Usa per domande tipo 'che città c'erano vicino a "
            "41.9, 12.5 nel 100 d.C.?' (città vicino Roma) o 'qual è il "
            "trade hub più vicino a Venezia nel 1400?'. Nota: questo tool "
            "trova CITTÀ storiche (dataset separato da GeoEntity) — per "
            "capitali di imperi/regni usa nearby_entities."
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
                "year": {
                    **_YEAR_SCHEMA,
                    "description": _YEAR_SCHEMA["description"]
                    + " Filtra città attive (year_founded <= anno <= year_abandoned).",
                },
                "city_type": {
                    "type": "string",
                    "description": (
                        "CAPITAL / TRADE_HUB / RELIGIOUS_CENTER / FORTRESS / "
                        "PORT / ACADEMIC_CENTER / INDUSTRIAL_CENTER / "
                        "MULTI_PURPOSE / OTHER."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "description": "Numero massimo di città da ritornare (default: 5).",
                },
                "max_candidates": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 1000,
                    "description": (
                        "Numero massimo di candidati da scaricare prima "
                        "del sort client-side (default: 500)."
                    ),
                },
            },
            "required": ["lat", "lon"],
            "additionalProperties": False,
        },
        handler=_h_nearest_historical_city,
    ),
    # ─── composite tools ────────────────────────────────────────────
    ToolDefinition(
        name="what_changed_between",
        description=(
            "Diff macro-storico del mondo tra due anni: ritorna le entità "
            "apparse fra year1 e year2, quelle scomparse, e gli id di quelle "
            "persistenti. Opzionalmente filtra per tipo o continente. Usa "
            "per domande tipo 'cosa è cambiato nel Mediterraneo tra il 300 "
            "a.C. e il 100 d.C.?' o 'quali imperi sono apparsi tra il 1800 "
            "e il 1900 in Africa?'. È composizione client-side di due "
            "snapshot — più economico di due chiamate separate se servono "
            "solo id+nomi."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "year1": _YEAR_SCHEMA,
                "year2": _YEAR_SCHEMA,
                "type": _TYPE_SCHEMA,
                "continent": _CONTINENT_SCHEMA,
            },
            "required": ["year1", "year2"],
            "additionalProperties": False,
        },
        handler=_h_what_changed_between,
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
