"""AtlasPI agent: Claude con tool access che chiamano AtlasPI REST API.

Simuliamo MCP tools come function definitions Anthropic. Ogni tool_use chiamato
dal model viene eseguito come HTTP call verso https://atlaspi.cra-srl.com/v1/*,
il risultato viene restituito come tool_result. Il loop continua finché il
model dà una text response finale.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

import requests
from anthropic import Anthropic


ATLASPI_BASE = os.environ.get("ATLASPI_BASE_URL", "https://atlaspi.cra-srl.com")

SYSTEM_PROMPT = (
    "You are a rigorous historian. AtlasPI provides lookup tools for "
    "structured historical data (entities, rulers, events, snapshots).\n\n"
    "Rules:\n"
    "1. Use the tools when a factual question benefits from a structured "
    "lookup: capital of a polity at a given year, ruler list, events around "
    "a date, list of polities active in a snapshot year, fuzzy entity name "
    "search.\n"
    "2. When a tool returns empty, partial, or no relevant result, "
    "EXPLICITLY acknowledge it and answer from your training knowledge "
    "with appropriate hedging. Example: 'AtlasPI has limited ruler data "
    "for this period; from my training knowledge, [Ruler X] is well-"
    "documented as ruling [years].'\n"
    "3. Do NOT claim 'according to AtlasPI...' unless you actually called "
    "the tool and got a result. If you answer from training, say 'from my "
    "training' or omit attribution rather than fabricating one.\n"
    "4. Cite AtlasPI entity IDs only when you used tool data for that "
    "specific fact (format: [AtlasPI:123]).\n"
    "5. Be precise with dates, names, places. Include dynasty/ruler name "
    "when the question asks about a specific period.\n"
    "6. Respond in the same language as the question.\n"
    "7. Be concise: 2-4 sentences typical.\n\n"
    "v7.1 prompt revision (post benchmark v7.0): superiority claims about "
    "AtlasPI removed because they caused hallucinations when tools were "
    "unavailable. The agent is now neutral about source authority and "
    "explicit about deferring to training when tools are silent."
)

# Tool definitions — equivalenti a MCP tools di AtlasPI
TOOLS = [
    {
        "name": "search_entities",
        "description": (
            "Fuzzy search over AtlasPI entities by name. Returns list of "
            "candidates with id, name_original, year_start, year_end, "
            "entity_type. Use this to find entity IDs from a text query "
            "like 'Ottoman Empire' or 'Bisanzio'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Name or partial name"},
                "limit": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_entity",
        "description": (
            "Get full details of an AtlasPI entity by ID. Includes "
            "name_original, name_variants (other languages), year_start/end, "
            "capital, capital_history (timeline of multiple capitals if "
            "polity long-duration), entity_type, confidence_score, "
            "ethical_notes, wikidata_qid, sources."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "integer", "description": "AtlasPI entity ID"},
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "get_snapshot_year",
        "description": (
            "Return world snapshot at a given year: list of entities "
            "active (year_start <= year <= year_end). Useful for questions "
            "like 'who controlled X in year Y'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Year (negative = BCE)"},
            },
            "required": ["year"],
        },
    },
    {
        "name": "get_rulers",
        "description": (
            "List rulers of an entity: name, reign_start, reign_end, title. "
            "Use for questions about who governed X in year Y."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "integer"},
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "get_events_at",
        "description": (
            "List historical events near a year or at a specific date. "
            "Useful for questions about what happened in year X or when "
            "did event Y occur."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer"},
                "month": {"type": "integer", "minimum": 1, "maximum": 12},
                "day": {"type": "integer", "minimum": 1, "maximum": 31},
            },
            "required": ["year"],
        },
    },
    # v7.1 NEW TOOLS (3 added per ADR-007 implementation item #2)
    {
        "name": "get_rulers_at_year",
        "description": (
            "List rulers active in a specific year, optionally filtered by region. "
            "Returns rulers whose reign overlaps the year. Use this for questions "
            "like 'who was emperor of Y in 1400' or 'who ruled the Silk Road in 750 CE'. "
            "More direct than get_rulers(entity_id) when you don't yet know the entity."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Year (negative = BCE)"},
                "region": {"type": "string", "description": "Optional region filter (e.g. 'Europe', 'Middle East', 'East Asia')"},
            },
            "required": ["year"],
        },
    },
    {
        "name": "get_events_by_entity",
        "description": (
            "List historical events associated with a specific AtlasPI entity. "
            "Returns up to 30 events sorted by year. Use this when you have an "
            "entity_id (from search_entities or get_entity) and want to know its "
            "key events: foundations, battles, treaties, dissolutions, succession events. "
            "Different from get_events_at which filters by year, not entity."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "integer", "description": "AtlasPI entity ID"},
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "get_languages_at_year_region",
        "description": (
            "List historical languages active at a year, optionally filtered by region. "
            "Returns language records with iso_code, family, script, geographic center. "
            "Use this for questions about what language was spoken at place X in year Y, "
            "or which language family dominated a region. AtlasPI has 29 languages "
            "(Mesoamerican, Semitic, Indo-European, Sino-Tibetan, etc.); coverage is "
            "stronger on classical/medieval than modern."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Year for language activity"},
                "region": {"type": "string", "description": "Optional region filter"},
            },
            "required": ["year"],
        },
    },
]


def _execute_tool(name: str, inp: dict) -> Any:
    """Esegue un tool call come HTTP request a AtlasPI."""
    try:
        if name == "search_entities":
            r = requests.get(
                f"{ATLASPI_BASE}/v1/search/fuzzy",
                params={"q": inp["query"], "limit": inp.get("limit", 5)},
                timeout=15,
            )
            r.raise_for_status()
            data = r.json()
            results = data.get("results", [])
            return [
                {
                    "id": x.get("id"),
                    "name_original": x.get("name_original"),
                    "entity_type": x.get("entity_type"),
                    "year_start": x.get("year_start"),
                    "year_end": x.get("year_end"),
                    "score": x.get("score"),
                }
                for x in results
            ]

        if name == "get_entity":
            r = requests.get(
                f"{ATLASPI_BASE}/v1/entities/{inp['entity_id']}",
                timeout=15,
            )
            if r.status_code == 404:
                return {"error": "entity not found"}
            r.raise_for_status()
            d = r.json()
            # Slim payload: omit boundary_geojson (huge) + sources
            d.pop("boundary_geojson", None)
            d.pop("territory_changes", None)
            return d

        if name == "get_snapshot_year":
            r = requests.get(
                f"{ATLASPI_BASE}/v1/snapshot/year/{inp['year']}",
                params={"limit": 50},
                timeout=20,
            )
            r.raise_for_status()
            d = r.json()
            # v6.92: /v1/snapshot/year/{year} restituisce `entities` come DICT
            # con chiavi: total_active, by_type, top_by_confidence (list).
            # Usiamo top_by_confidence come lista entity principale.
            entities_block = d.get("entities", {}) or {}
            if isinstance(entities_block, list):
                # backward compat se endpoint cambiasse a list
                entity_list = entities_block
            else:
                entity_list = entities_block.get("top_by_confidence", [])
            total = entities_block.get("total_active", len(entity_list)) if isinstance(entities_block, dict) else len(entity_list)
            # Slim payload: keep only key fields
            slim = [
                {
                    "id": e.get("id"),
                    "name": e.get("name") or e.get("name_original"),
                    "type": e.get("entity_type"),
                    "range": f"{e.get('year_start')}–{e.get('year_end') or '?'}",
                    "confidence": e.get("confidence_score"),
                }
                for e in entity_list[:30]
            ]
            by_type = entities_block.get("by_type", {}) if isinstance(entities_block, dict) else {}
            return {
                "year": inp["year"],
                "total_active": total,
                "top_by_confidence": slim,
                "by_type_count": by_type,
            }

        if name == "get_rulers":
            r = requests.get(
                f"{ATLASPI_BASE}/v1/rulers",
                params={"entity_id": inp["entity_id"], "limit": 30},
                timeout=15,
            )
            r.raise_for_status()
            d = r.json()
            rulers = d.get("rulers", [])
            return [
                {
                    "id": x.get("id"),
                    "name": x.get("name_original"),
                    "title": x.get("title"),
                    "reign_start": x.get("reign_start"),
                    "reign_end": x.get("reign_end"),
                }
                for x in rulers
            ]

        if name == "get_events_at":
            year = inp["year"]
            month = inp.get("month")
            day = inp.get("day")
            if month and day:
                url = f"{ATLASPI_BASE}/v1/events/at-date/{year:04d}-{month:02d}-{day:02d}"
                r = requests.get(url, timeout=15)
            else:
                r = requests.get(
                    f"{ATLASPI_BASE}/v1/events",
                    params={"year": year, "limit": 20},
                    timeout=15,
                )
            r.raise_for_status()
            d = r.json()
            events = d.get("events", [])
            return [
                {
                    "name": e.get("name_original"),
                    "year": e.get("year"),
                    "type": e.get("event_type"),
                    "location": e.get("location_name"),
                    "casualties": e.get("casualties_high") or e.get("casualties_low"),
                }
                for e in events[:15]
            ]

        # v7.1 NEW TOOLS (per ADR-007 #2)
        if name == "get_rulers_at_year":
            params = {"year": inp["year"], "limit": 20}
            if inp.get("region"):
                params["region"] = inp["region"]
            r = requests.get(f"{ATLASPI_BASE}/v1/rulers", params=params, timeout=15)
            r.raise_for_status()
            d = r.json()
            rulers = d.get("rulers", [])
            return [
                {
                    "id": x.get("id"),
                    "name": x.get("name_original"),
                    "title": x.get("title"),
                    "dynasty": x.get("dynasty"),
                    "reign_start": x.get("reign_start"),
                    "reign_end": x.get("reign_end"),
                    "entity_id": x.get("entity_id"),
                    "entity_name": x.get("entity_name_fallback"),
                    "region": x.get("region"),
                }
                for x in rulers[:15]
            ]

        if name == "get_events_by_entity":
            r = requests.get(
                f"{ATLASPI_BASE}/v1/events",
                params={"entity_id": inp["entity_id"], "limit": 30},
                timeout=15,
            )
            r.raise_for_status()
            d = r.json()
            events = d.get("events", [])
            # Sort by year ascending
            events.sort(key=lambda e: e.get("year") or 0)
            return [
                {
                    "id": e.get("id"),
                    "name": e.get("name_original"),
                    "year": e.get("year"),
                    "year_end": e.get("year_end"),
                    "type": e.get("event_type"),
                    "location": e.get("location_name"),
                    "main_actor": e.get("main_actor"),
                    "casualties": e.get("casualties_high") or e.get("casualties_low"),
                }
                for e in events[:20]
            ]

        if name == "get_languages_at_year_region":
            params = {"year": inp["year"], "limit": 30}
            if inp.get("region"):
                params["region"] = inp["region"]
            r = requests.get(f"{ATLASPI_BASE}/v1/languages", params=params, timeout=15)
            r.raise_for_status()
            d = r.json()
            langs = d.get("languages", [])
            return [
                {
                    "id": l.get("id"),
                    "name": l.get("name_original"),
                    "iso_code": l.get("iso_code"),
                    "family": l.get("family"),
                    "script": l.get("script"),
                    "region_name": l.get("region_name"),
                    "period_start": l.get("period_start"),
                    "period_end": l.get("period_end"),
                    "vitality": l.get("vitality_status"),
                }
                for l in langs[:20]
            ]

        return {"error": f"unknown tool: {name}"}

    except requests.HTTPError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:200]}"}


class AtlasPIAgent:
    def __init__(self, model: str = "claude-sonnet-4-5-20250929", max_tokens: int = 1200, max_tool_iterations: int = 8):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model
        self.max_tokens = max_tokens
        self.max_tool_iterations = max_tool_iterations

    def answer(self, question: str) -> dict:
        start = time.monotonic()
        messages = [{"role": "user", "content": question}]
        tool_calls_log: list[dict] = []
        tokens_in_total = 0
        tokens_out_total = 0

        for iteration in range(self.max_tool_iterations):
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )
            tokens_in_total += resp.usage.input_tokens
            tokens_out_total += resp.usage.output_tokens

            if resp.stop_reason == "end_turn":
                text_parts = [b.text for b in resp.content if b.type == "text"]
                answer_text = "\n".join(text_parts).strip()
                return {
                    "condition": "atlaspi",
                    "model": self.model,
                    "response": answer_text,
                    "latency_ms": round((time.monotonic() - start) * 1000.0, 1),
                    "tokens_in": tokens_in_total,
                    "tokens_out": tokens_out_total,
                    "stop_reason": resp.stop_reason,
                    "tool_calls_count": len(tool_calls_log),
                    "tool_calls": tool_calls_log,
                    "iterations": iteration + 1,
                }

            if resp.stop_reason == "tool_use":
                # Append assistant message (with tool_use blocks)
                messages.append({"role": "assistant", "content": resp.content})
                # Process every tool_use
                tool_results = []
                for block in resp.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        result = _execute_tool(tool_name, tool_input)
                        tool_calls_log.append({
                            "tool": tool_name,
                            "input": tool_input,
                            "output_summary": str(result)[:300],
                        })
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False),
                        })
                messages.append({"role": "user", "content": tool_results})
                continue

            # Unexpected stop_reason
            text_parts = [b.text for b in resp.content if b.type == "text"]
            return {
                "condition": "atlaspi",
                "model": self.model,
                "response": "\n".join(text_parts).strip() or f"[unexpected stop_reason: {resp.stop_reason}]",
                "latency_ms": round((time.monotonic() - start) * 1000.0, 1),
                "tokens_in": tokens_in_total,
                "tokens_out": tokens_out_total,
                "stop_reason": resp.stop_reason,
                "tool_calls_count": len(tool_calls_log),
                "tool_calls": tool_calls_log,
                "iterations": iteration + 1,
            }

        # Hit max_tool_iterations
        return {
            "condition": "atlaspi",
            "model": self.model,
            "response": "[max tool iterations reached]",
            "latency_ms": round((time.monotonic() - start) * 1000.0, 1),
            "tokens_in": tokens_in_total,
            "tokens_out": tokens_out_total,
            "stop_reason": "max_iterations",
            "tool_calls_count": len(tool_calls_log),
            "tool_calls": tool_calls_log,
            "iterations": self.max_tool_iterations,
        }
