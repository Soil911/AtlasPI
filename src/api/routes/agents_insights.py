"""Endpoint /agents/insights — Phase G3 Agent Telemetry.

Pivot di `api_request_logs` filtrato per AI agents/bots.

Espone pattern di utilizzo degli agenti AI (Claude, GPT, Gemini, Perplexity,
bot di indicizzazione, ecc.) per capire COSA cercano nel database, da DOVE
arrivano, e dove ci sono ZERO-RESULT queries (= cosa manca).

Non aggiunge tabelle nuove — riusa `api_request_logs` (schema R10).

GET /agents/insights/overview     — dashboard summary
GET /agents/insights/by-family    — breakdown per AI agent family
GET /agents/insights/top-queries  — top query patterns
GET /agents/insights/zero-results — queries che hanno restituito 0 (gap analysis)

Endpoint pubblici (no auth) — trasparenza completa sui pattern di accesso AI.
"""

from __future__ import annotations

import datetime
import logging

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import ApiRequestLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents/insights", tags=["agents"])


# ─── User-agent classification ──────────────────────────────────────

# AI agent / bot patterns. Ordered: most specific first.
# Tuple: (lowercase substring, family_label, family_category)
_AI_AGENT_PATTERNS: list[tuple[str, str, str]] = [
    # Anthropic ecosystem
    ("claudebot", "ClaudeBot", "anthropic"),
    ("anthropic-ai", "Anthropic", "anthropic"),
    ("claude-web", "Claude.ai", "anthropic"),
    ("atlaspi-mcp", "AtlasPI-MCP", "anthropic_mcp"),
    # OpenAI ecosystem
    ("gptbot", "OpenAI GPTBot", "openai"),
    ("chatgpt-user", "ChatGPT-User", "openai"),
    ("oai-searchbot", "OpenAI SearchBot", "openai"),
    # Perplexity
    ("perplexitybot", "PerplexityBot", "perplexity"),
    ("perplexity-user", "Perplexity-User", "perplexity"),
    # Google
    ("googlebot", "GoogleBot", "google"),
    ("google-extended", "Google-Extended", "google"),
    ("bard", "Google Bard", "google"),
    # Microsoft
    ("bingbot", "BingBot", "microsoft"),
    ("copilotbot", "CopilotBot", "microsoft"),
    # Other search/index
    ("duckduckbot", "DuckDuckBot", "other_search"),
    ("baiduspider", "Baidu", "other_search"),
    ("yandexbot", "YandexBot", "other_search"),
    ("petalbot", "PetalBot", "other_search"),
    # Common Crawl / archives
    ("ccbot", "Common Crawl", "archive"),
    ("archive.org_bot", "Internet Archive", "archive"),
    ("ia_archiver", "Internet Archive", "archive"),
    # Social media previewers
    ("facebookexternalhit", "Facebook", "social_preview"),
    ("twitterbot", "Twitter/X", "social_preview"),
    ("linkedinbot", "LinkedIn", "social_preview"),
    ("slackbot", "Slack", "social_preview"),
    ("discordbot", "Discord", "social_preview"),
    ("telegrambot", "Telegram", "social_preview"),
    # SEO crawlers
    ("semrushbot", "SemrushBot", "seo"),
    ("ahrefsbot", "AhrefsBot", "seo"),
    ("mj12bot", "Majestic", "seo"),
    ("dotbot", "Moz DotBot", "seo"),
    # Generic
    ("python-requests", "Python requests", "programmatic"),
    ("httpx", "Python httpx", "programmatic"),
    ("aiohttp", "Python aiohttp", "programmatic"),
    ("curl/", "curl", "programmatic"),
    ("wget", "wget", "programmatic"),
    ("node-fetch", "Node.js fetch", "programmatic"),
    ("axios", "Axios", "programmatic"),
    ("go-http", "Go HTTP", "programmatic"),
    ("okhttp", "OkHttp", "programmatic"),
    ("bot/", "Generic Bot", "generic_bot"),
    ("crawler", "Generic Crawler", "generic_bot"),
    ("spider", "Generic Spider", "generic_bot"),
]


def classify_user_agent(ua: str | None) -> tuple[str, str] | tuple[None, None]:
    """Classifica UA. Ritorna (family_label, category) o (None, None) se non match."""
    if not ua:
        return None, None
    ua_lower = ua.lower()
    for needle, label, category in _AI_AGENT_PATTERNS:
        if needle in ua_lower:
            return label, category
    return None, None


# ─── Path classification ────────────────────────────────────────────

_PATH_QUERY_TYPES: list[tuple[str, str]] = [
    ("/v1/entity", "entity_search"),
    ("/v1/entities", "entity_listing"),
    ("/v1/events/on-this-day", "on_this_day"),
    ("/v1/events", "events"),
    ("/v1/snapshot", "snapshot"),
    ("/v1/nearby", "spatial_proximity"),
    ("/v1/periods", "periods"),
    ("/v1/cities", "cities"),
    ("/v1/sites", "archaeological_sites"),
    ("/v1/rulers", "rulers"),
    ("/v1/languages", "languages"),
    ("/v1/routes", "trade_routes"),
    ("/v1/chains", "dynasty_chains"),
    ("/v1/search", "search"),
    ("/v1/feedback", "feedback"),
    ("/v1/compare", "comparison"),
    ("/v1/timeline", "timeline"),
    ("/v1/export", "export"),
    ("/v1/stats", "stats"),
    ("/openapi.json", "openapi_spec"),
    ("/.well-known/mcp.json", "mcp_discovery"),
    ("/llms.txt", "llms_txt"),
    ("/docs", "swagger_docs"),
]


def classify_path(path: str) -> str:
    """Mappa path API a categoria di query."""
    for prefix, category in _PATH_QUERY_TYPES:
        if path.startswith(prefix):
            return category
    return "other"


# ─── Schemas ────────────────────────────────────────────────────────


class AgentOverview(BaseModel):
    total_requests: int
    distinct_agents: int
    total_ai_agent_requests: int
    by_category: dict[str, int]
    last_24h_ai_requests: int
    last_7d_ai_requests: int
    most_active_family: str | None


class FamilyRow(BaseModel):
    family: str
    category: str
    request_count: int
    unique_paths: int
    last_seen: str | None


class TopQueryRow(BaseModel):
    path: str
    query_type: str
    request_count: int
    distinct_agents: int
    sample_params: list[str] = []


class ZeroResultRow(BaseModel):
    path: str
    query_string: str | None
    status_code: int
    count: int
    last_seen: str | None


# ─── Endpoints ──────────────────────────────────────────────────────


@router.get(
    "/overview",
    response_model=AgentOverview,
    summary="AI agent traffic overview",
)
def overview(db: Session = Depends(get_db)) -> AgentOverview:
    # Counters
    total = db.query(func.count(ApiRequestLog.id)).scalar() or 0
    distinct_agents = db.query(func.count(func.distinct(ApiRequestLog.user_agent))).scalar() or 0

    # Aggregate AI agent / bot
    all_logs = db.query(ApiRequestLog.user_agent).all()
    ai_total = 0
    by_cat: dict[str, int] = {}
    fam_counter: dict[str, int] = {}
    for (ua,) in all_logs:
        family, cat = classify_user_agent(ua)
        if family:
            ai_total += 1
            by_cat[cat] = by_cat.get(cat, 0) + 1
            fam_counter[family] = fam_counter.get(family, 0) + 1

    most_active = max(fam_counter, key=fam_counter.get) if fam_counter else None

    # 24h / 7d windows
    now = datetime.datetime.utcnow()
    th_24h = (now - datetime.timedelta(hours=24)).isoformat()
    th_7d = (now - datetime.timedelta(days=7)).isoformat()
    last_24h_logs = (
        db.query(ApiRequestLog.user_agent)
        .filter(ApiRequestLog.timestamp >= th_24h)
        .all()
    )
    last_24h_ai = sum(1 for (ua,) in last_24h_logs if classify_user_agent(ua)[0])
    last_7d_logs = (
        db.query(ApiRequestLog.user_agent)
        .filter(ApiRequestLog.timestamp >= th_7d)
        .all()
    )
    last_7d_ai = sum(1 for (ua,) in last_7d_logs if classify_user_agent(ua)[0])

    return AgentOverview(
        total_requests=total,
        distinct_agents=distinct_agents,
        total_ai_agent_requests=ai_total,
        by_category=by_cat,
        last_24h_ai_requests=last_24h_ai,
        last_7d_ai_requests=last_7d_ai,
        most_active_family=most_active,
    )


@router.get(
    "/by-family",
    response_model=list[FamilyRow],
    summary="Breakdown by AI agent family",
)
def by_family(
    days: int = Query(30, ge=1, le=365, description="Time window in days"),
    db: Session = Depends(get_db),
) -> list[FamilyRow]:
    threshold = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).isoformat()
    rows = (
        db.query(
            ApiRequestLog.user_agent,
            ApiRequestLog.path,
            ApiRequestLog.timestamp,
        )
        .filter(ApiRequestLog.timestamp >= threshold)
        .all()
    )

    # Aggregate per family
    families: dict[str, dict] = {}
    for ua, path, ts in rows:
        family, cat = classify_user_agent(ua)
        if not family:
            continue
        if family not in families:
            families[family] = {
                "family": family,
                "category": cat,
                "request_count": 0,
                "paths": set(),
                "last_seen": ts,
            }
        families[family]["request_count"] += 1
        families[family]["paths"].add(path)
        if ts > families[family]["last_seen"]:
            families[family]["last_seen"] = ts

    return sorted(
        [
            FamilyRow(
                family=v["family"],
                category=v["category"],
                request_count=v["request_count"],
                unique_paths=len(v["paths"]),
                last_seen=v["last_seen"],
            )
            for v in families.values()
        ],
        key=lambda r: r.request_count,
        reverse=True,
    )


@router.get(
    "/top-queries",
    response_model=list[TopQueryRow],
    summary="Top query patterns from AI agents",
)
def top_queries(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[TopQueryRow]:
    threshold = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).isoformat()
    rows = (
        db.query(
            ApiRequestLog.path,
            ApiRequestLog.query_string,
            ApiRequestLog.user_agent,
        )
        .filter(ApiRequestLog.timestamp >= threshold)
        .filter(ApiRequestLog.status_code < 500)
        .all()
    )

    by_path: dict[str, dict] = {}
    for path, qs, ua in rows:
        family, cat = classify_user_agent(ua)
        if not family:
            continue
        # Normalizza path: trasforma /v1/entities/123 -> /v1/entities/{id}
        norm = _normalize_path(path)
        if norm not in by_path:
            by_path[norm] = {
                "path": norm,
                "query_type": classify_path(norm),
                "request_count": 0,
                "agents": set(),
                "params": [],
            }
        by_path[norm]["request_count"] += 1
        by_path[norm]["agents"].add(family)
        if qs and len(by_path[norm]["params"]) < 5:
            by_path[norm]["params"].append(qs[:100])

    sorted_rows = sorted(by_path.values(), key=lambda v: v["request_count"], reverse=True)
    return [
        TopQueryRow(
            path=v["path"],
            query_type=v["query_type"],
            request_count=v["request_count"],
            distinct_agents=len(v["agents"]),
            sample_params=v["params"],
        )
        for v in sorted_rows[:limit]
    ]


@router.get(
    "/zero-results",
    response_model=list[ZeroResultRow],
    summary="Queries that returned 404 / 0 results (gap analysis)",
)
def zero_results(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[ZeroResultRow]:
    threshold = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).isoformat()
    rows = (
        db.query(
            ApiRequestLog.path,
            ApiRequestLog.query_string,
            ApiRequestLog.status_code,
            func.count(ApiRequestLog.id).label("c"),
            func.max(ApiRequestLog.timestamp).label("last_ts"),
        )
        .filter(ApiRequestLog.timestamp >= threshold)
        .filter(ApiRequestLog.status_code == 404)
        .group_by(ApiRequestLog.path, ApiRequestLog.query_string, ApiRequestLog.status_code)
        .order_by(desc("c"))
        .limit(limit)
        .all()
    )
    return [
        ZeroResultRow(
            path=r.path,
            query_string=r.query_string,
            status_code=r.status_code,
            count=r.c,
            last_seen=r.last_ts,
        )
        for r in rows
    ]


# ─── Helpers ────────────────────────────────────────────────────────


def _normalize_path(path: str) -> str:
    """Trasforma /v1/entities/123 -> /v1/entities/{id} per aggregation."""
    parts = path.split("/")
    out = []
    for p in parts:
        if p.isdigit():
            out.append("{id}")
        else:
            out.append(p)
    return "/".join(out)
