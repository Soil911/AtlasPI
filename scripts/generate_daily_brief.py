#!/usr/bin/env python3
"""Generate a Markdown daily brief for AtlasPI.

Queries the database directly (no HTTP calls needed) and prints
a Markdown report to stdout. Can be piped to a file or email.

Usage:
    python scripts/generate_daily_brief.py
    python scripts/generate_daily_brief.py > briefs/2026-04-16.md
"""

from __future__ import annotations

import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, distinct, or_

from src.db.database import SessionLocal
from src.db.models import (
    ApiRequestLog,
    ChainLink,
    DynastyChain,
    GeoEntity,
    HistoricalCity,
    HistoricalEvent,
    TradeRoute,
)


# ── Internal IPs (same as admin_insights) ──────────────────────────
INTERNAL_IPS = frozenset({
    "127.0.0.1", "::1", "77.81.229.242",
    "172.17.0.1", "172.18.0.1", "10.0.0.1",
})


def _classify_ua(ua: str | None) -> str:
    if not ua:
        return "unknown"
    ua_lower = ua.lower()
    bot_keywords = ("bot", "crawl", "spider", "curl", "wget", "python-",
                    "go-http", "postman", "scrapy", "headless", "gptbot",
                    "claudebot", "anthropic")
    if any(k in ua_lower for k in bot_keywords):
        return "bot"
    browser_keywords = ("mozilla", "chrome", "safari", "firefox", "edge")
    if any(k in ua_lower for k in browser_keywords):
        return "browser"
    return "api_client"


def generate_brief() -> str:
    """Generate the daily brief as a Markdown string."""
    db = SessionLocal()
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    yesterday = (now - timedelta(days=1)).isoformat()
    week_ago = (now - timedelta(days=7)).isoformat()
    month_ago = (now - timedelta(days=30)).isoformat()

    lines: list[str] = []
    lines.append(f"# AtlasPI Daily Brief - {today}\n")
    lines.append(f"Generated at {now.strftime('%H:%M UTC')}\n")

    # ── 1. Dataset overview ───────────────────────────────────
    total_entities = db.query(func.count(GeoEntity.id)).scalar() or 0
    total_events = db.query(func.count(HistoricalEvent.id)).scalar() or 0
    total_chains = db.query(func.count(DynastyChain.id)).scalar() or 0
    total_cities = db.query(func.count(HistoricalCity.id)).scalar() or 0
    total_routes = db.query(func.count(TradeRoute.id)).scalar() or 0

    lines.append("## Dataset overview\n")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Entities | {total_entities} |")
    lines.append(f"| Events | {total_events} |")
    lines.append(f"| Dynasty chains | {total_chains} |")
    lines.append(f"| Cities | {total_cities} |")
    lines.append(f"| Trade routes | {total_routes} |")
    lines.append("")

    # ── 2. Traffic highlights ─────────────────────────────────
    total_all = db.query(func.count(ApiRequestLog.id)).scalar() or 0
    total_24h = (
        db.query(func.count(ApiRequestLog.id))
        .filter(ApiRequestLog.timestamp >= yesterday)
        .scalar() or 0
    )
    total_7d = (
        db.query(func.count(ApiRequestLog.id))
        .filter(ApiRequestLog.timestamp >= week_ago)
        .scalar() or 0
    )
    avg_ms = db.query(func.avg(ApiRequestLog.response_time_ms)).scalar()
    avg_ms = round(avg_ms, 1) if avg_ms else 0

    lines.append("## Traffic highlights\n")
    lines.append(f"- **Last 24h**: {total_24h} requests")
    lines.append(f"- **Last 7d**: {total_7d} requests")
    lines.append(f"- **All time**: {total_all} requests")
    lines.append(f"- **Avg response**: {avg_ms} ms")
    lines.append("")

    # ── 3. External visitors ──────────────────────────────────
    ext_rows = (
        db.query(
            ApiRequestLog.client_ip,
            func.count(ApiRequestLog.id).label("hits"),
            func.max(ApiRequestLog.timestamp).label("last_seen"),
        )
        .filter(ApiRequestLog.timestamp >= week_ago)
        .group_by(ApiRequestLog.client_ip)
        .order_by(func.count(ApiRequestLog.id).desc())
        .all()
    )
    external = [r for r in ext_rows if r.client_ip not in INTERNAL_IPS]

    if external:
        lines.append("## External visitors (last 7d)\n")
        lines.append("| IP | Hits | Last seen |")
        lines.append("|----|------|-----------|")
        for r in external[:10]:
            lines.append(f"| `{r.client_ip}` | {r.hits} | {r.last_seen} |")
        if len(external) > 10:
            lines.append(f"\n*... and {len(external) - 10} more*")
        lines.append("")

    # ── 4. Top searches ───────────────────────────────────────
    search_rows = (
        db.query(
            ApiRequestLog.path,
            ApiRequestLog.query_string,
            func.count(ApiRequestLog.id).label("times"),
        )
        .filter(
            ApiRequestLog.timestamp >= week_ago,
            ApiRequestLog.query_string.isnot(None),
            ApiRequestLog.query_string != "",
        )
        .group_by(ApiRequestLog.path, ApiRequestLog.query_string)
        .order_by(func.count(ApiRequestLog.id).desc())
        .limit(10)
        .all()
    )
    if search_rows:
        lines.append("## Top searches (last 7d)\n")
        lines.append("| Path | Query | Times |")
        lines.append("|------|-------|-------|")
        for r in search_rows:
            q = r.query_string[:60] + "..." if len(r.query_string or "") > 60 else r.query_string
            lines.append(f"| `{r.path}` | `{q}` | {r.times} |")
        lines.append("")

    # ── 5. Quality score ──────────────────────────────────────
    entities_data = db.query(
        GeoEntity.confidence_score, GeoEntity.boundary_geojson,
    ).all()
    avg_conf = sum(e.confidence_score for e in entities_data) / len(entities_data) if entities_data else 0
    with_boundary = sum(1 for e in entities_data if e.boundary_geojson)
    boundary_pct = round(with_boundary / len(entities_data) * 100, 1) if entities_data else 0

    entity_ids_in_chains = set(
        r[0] for r in db.query(distinct(ChainLink.entity_id)).all()
    )
    chain_pct = round(len(entity_ids_in_chains) / total_entities * 100, 1) if total_entities else 0

    lines.append("## Data quality\n")
    lines.append(f"- **Avg confidence**: {round(avg_conf, 3)}")
    lines.append(f"- **Boundary coverage**: {boundary_pct}% ({with_boundary}/{len(entities_data)})")
    lines.append(f"- **Chain coverage**: {chain_pct}% ({len(entity_ids_in_chains)}/{total_entities})")
    lines.append("")

    # ── 6. Top 5 suggestions ─────────────────────────────────
    lines.append("## Top suggestions\n")

    # Low confidence
    low_conf = (
        db.query(GeoEntity.name_original, GeoEntity.confidence_score)
        .filter(GeoEntity.confidence_score < 0.5)
        .order_by(GeoEntity.confidence_score)
        .limit(3)
        .all()
    )
    if low_conf:
        lines.append("**Low confidence entities to review:**")
        for e in low_conf:
            lines.append(f"- {e.name_original} (score: {e.confidence_score})")
        lines.append("")

    # No boundary
    no_boundary = (
        db.query(GeoEntity.name_original)
        .filter(or_(
            GeoEntity.boundary_geojson.is_(None),
            GeoEntity.boundary_geojson == "",
        ))
        .limit(5)
        .all()
    )
    if no_boundary:
        lines.append("**Entities missing boundaries:**")
        for (name,) in no_boundary:
            lines.append(f"- {name}")
        lines.append("")

    # Orphan entities
    orphan_count = total_entities - len(entity_ids_in_chains)
    if orphan_count > 0:
        lines.append(f"**Orphan entities** (not in any chain): {orphan_count}")
        lines.append("")

    lines.append("---\n")
    lines.append("*Generated by AtlasPI AI Co-Founder Intelligence Layer (v6.15)*")

    db.close()
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_brief())
