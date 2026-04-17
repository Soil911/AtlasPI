"""Analytics dashboard per AtlasPI — v6.49 ridisegnata.

GET /admin/analytics       — pagina HTML con dashboard interattiva
GET /admin/analytics/data  — dati JSON grezzi per il dashboard

v6.49 change:
- Rimosso Top IPs dalla dashboard (privacy + poco utile)
- Aggiunta classificazione user-agent: human / agent / bot / unknown
- Aggiunta device detection: desktop / mobile / tablet / server / bot
- Aggiunta endpoint category breakdown (entities / events / geo_query / etc)
- Recent Requests ora mostra `Client Type` + `Device` invece dell'IP
"""

import logging
import re

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import ApiRequestLog

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin"])


# ─── Classificazione user-agent (v6.49) ──────────────────────────

# Pattern matching ordered: bots most specific first.
# Second tuple element is a human-readable label for display.
_BOT_PATTERNS: list[tuple[str, str]] = [
    ("googlebot", "GoogleBot"),
    ("bingbot", "BingBot"),
    ("duckduckbot", "DuckDuckBot"),
    ("baiduspider", "Baidu"),
    ("yandexbot", "YandexBot"),
    ("facebookexternalhit", "Facebook"),
    ("twitterbot", "Twitter/X"),
    ("linkedinbot", "LinkedIn"),
    ("slackbot", "Slack"),
    ("discordbot", "Discord"),
    ("telegrambot", "Telegram"),
    ("applebot", "Apple"),
    ("claudebot", "ClaudeBot"),
    ("anthropic-ai", "Anthropic"),
    ("gptbot", "OpenAI GPTBot"),
    ("chatgpt-user", "ChatGPT-User"),
    ("perplexitybot", "PerplexityBot"),
    ("petal", "PetalBot"),
    ("semrushbot", "SemrushBot"),
    ("ahrefsbot", "AhrefsBot"),
    ("mj12bot", "Majestic"),
    ("dotbot", "Moz DotBot"),
    ("archive.org_bot", "Internet Archive"),
    ("ia_archiver", "Internet Archive"),
    ("bot/", "Generic Bot"),
    ("crawler", "Generic Crawler"),
    ("spider", "Generic Spider"),
]

# Programmatic / SDK clients — "agent" type.
_AGENT_PATTERNS: list[tuple[str, str]] = [
    ("atlaspi-mcp", "AtlasPI MCP"),
    ("atlaspi-client", "AtlasPI SDK"),
    ("atlaspi-client-js", "AtlasPI JS SDK"),
    ("python-requests", "Python requests"),
    ("httpx", "Python httpx"),
    ("aiohttp", "Python aiohttp"),
    ("urllib", "Python urllib"),
    ("node-fetch", "Node.js fetch"),
    ("axios", "Axios"),
    ("undici", "Node.js undici"),
    ("curl/", "curl"),
    ("wget", "wget"),
    ("go-http", "Go HTTP"),
    ("okhttp", "OkHttp"),
    ("java/", "Java HTTP"),
    ("apache-httpclient", "Apache HttpClient"),
    ("insomnia", "Insomnia"),
    ("postman", "Postman"),
    ("thunder client", "Thunder Client"),
    ("paw/", "Paw"),
    ("httpie", "HTTPie"),
    ("ruby", "Ruby HTTP"),
    ("php", "PHP curl"),
]

_MOBILE_PATTERNS = ("iphone", "android", "mobile", "windows phone", "blackberry")
_TABLET_PATTERNS = ("ipad", "tablet")


def classify_user_agent(ua: str | None) -> dict:
    """Classify user-agent string into structured dict.

    Returns:
        {
          "client_type": "human" | "agent" | "bot" | "unknown",
          "device":      "desktop" | "mobile" | "tablet" | "server" | "bot" | "unknown",
          "label":       short human-readable name (browser/tool/bot name)
        }
    """
    if not ua:
        return {"client_type": "unknown", "device": "unknown", "label": "(empty)"}
    ua_lower = ua.lower()

    # Bots first (most specific patterns)
    for key, label in _BOT_PATTERNS:
        if key in ua_lower:
            return {"client_type": "bot", "device": "bot", "label": label}

    # Programmatic clients
    for key, label in _AGENT_PATTERNS:
        if key in ua_lower:
            return {"client_type": "agent", "device": "server", "label": label}

    # Human browser: device detection
    device = "desktop"
    if any(p in ua_lower for p in _TABLET_PATTERNS):
        device = "tablet"
    elif any(p in ua_lower for p in _MOBILE_PATTERNS):
        device = "mobile"

    # Browser family
    if "edg/" in ua_lower or "edge/" in ua_lower:
        label = "Edge"
    elif "opr/" in ua_lower or "opera" in ua_lower:
        label = "Opera"
    elif "firefox" in ua_lower:
        label = "Firefox"
    elif "chromium" in ua_lower:
        label = "Chromium"
    elif "chrome" in ua_lower:
        label = "Chrome"
    elif "safari" in ua_lower:
        label = "Safari"
    else:
        label = "Other browser"

    return {"client_type": "human", "device": device, "label": label}


# ─── Classificazione endpoint path (v6.49) ──────────────────────

_ENDPOINT_CATEGORIES: list[tuple[str, str]] = [
    ("/v1/entities/batch", "entities"),
    ("/v1/entities/light", "entities"),
    ("/v1/entities", "entities"),
    ("/v1/entity", "entities"),
    ("/v1/events", "events"),
    ("/v1/sites", "sites"),
    ("/v1/rulers", "rulers"),
    ("/v1/languages", "languages"),
    ("/v1/periods", "periods"),
    ("/v1/cities", "cities_routes_chains"),
    ("/v1/routes", "cities_routes_chains"),
    ("/v1/chains", "cities_routes_chains"),
    ("/v1/search", "search"),
    ("/v1/where-was", "geo_query"),
    ("/v1/nearby", "geo_query"),
    ("/v1/snapshot", "geo_query"),
    ("/v1/random", "geo_query"),
    ("/v1/render", "render"),
    ("/v1/export", "export"),
    ("/v1/compare", "compare"),
    ("/v1/timeline", "timeline"),
    ("/v1/stats", "stats"),
    ("/v1/types", "stats"),
    ("/v1/continents", "stats"),
    ("/v1/aggregation", "stats"),
    ("/v1/widgets", "widgets"),
    ("/v1/docs", "docs"),
    ("/admin", "admin"),
    ("/health", "health"),
    ("/metrics", "health"),
    ("/static", "static"),
    ("/", "landing"),
]


def classify_endpoint(path: str) -> str:
    """Map path to category. First match wins."""
    if not path:
        return "other"
    for prefix, cat in _ENDPOINT_CATEGORIES:
        if path == prefix or path.startswith(prefix + "/") or path.startswith(prefix + "?"):
            return cat
    return "other"


# ─── JSON data endpoint ─────────────────────────────────────────


@router.get(
    "/admin/analytics/data",
    summary="Dati analytics grezzi (JSON)",
    description="Statistiche aggregate sulle richieste API (v6.49: senza IP).",
    include_in_schema=False,
)
def analytics_data(db: Session = Depends(get_db)):
    """Dati grezzi per la dashboard analytics — v6.49 redesign."""

    # ── Summary ──────────────────────────────────────────────────
    total_requests = db.query(func.count(ApiRequestLog.id)).scalar() or 0
    unique_ips = db.query(func.count(func.distinct(ApiRequestLog.client_ip))).scalar() or 0
    avg_response_time = db.query(func.avg(ApiRequestLog.response_time_ms)).scalar()
    avg_response_time = round(avg_response_time, 2) if avg_response_time else 0.0
    first_request = db.query(func.min(ApiRequestLog.timestamp)).scalar()
    last_request = db.query(func.max(ApiRequestLog.timestamp)).scalar()

    summary = {
        "total_requests": total_requests,
        "unique_visitors": unique_ips,  # Renamed: privacy-neutral label
        "avg_response_time_ms": avg_response_time,
        "first_request": first_request,
        "last_request": last_request,
    }

    # ── Requests per day (last 30) ───────────────────────────────
    date_col = func.substr(ApiRequestLog.timestamp, 1, 10).label("date")
    rpd_rows = (
        db.query(date_col, func.count(ApiRequestLog.id).label("count"))
        .group_by(date_col)
        .order_by(desc(date_col))
        .limit(30)
        .all()
    )
    requests_per_day = [{"date": r.date, "count": r.count} for r in rpd_rows]

    # ── Top 20 endpoints ─────────────────────────────────────────
    te_rows = (
        db.query(
            ApiRequestLog.path,
            func.count(ApiRequestLog.id).label("count"),
            func.avg(ApiRequestLog.response_time_ms).label("avg_ms"),
        )
        .group_by(ApiRequestLog.path)
        .order_by(desc("count"))
        .limit(20)
        .all()
    )
    top_endpoints = [
        {"path": r.path, "count": r.count, "avg_ms": round(r.avg_ms, 2) if r.avg_ms else 0.0}
        for r in te_rows
    ]

    # ── v6.49: Breakdown per endpoint CATEGORY ──────────────────
    # Aggregate all paths by category in application code (cheap enough for ~tens of K rows).
    all_path_counts = (
        db.query(ApiRequestLog.path, func.count(ApiRequestLog.id).label("count"))
        .group_by(ApiRequestLog.path)
        .all()
    )
    category_counts: dict[str, int] = {}
    for row in all_path_counts:
        cat = classify_endpoint(row.path)
        category_counts[cat] = category_counts.get(cat, 0) + row.count
    by_category = [
        {"category": k, "count": v}
        for k, v in sorted(category_counts.items(), key=lambda kv: -kv[1])
    ]

    # ── v6.49: Breakdown per client_type + device (via user_agent classification) ──
    ua_rows = (
        db.query(
            ApiRequestLog.user_agent,
            func.count(ApiRequestLog.id).label("count"),
        )
        .group_by(ApiRequestLog.user_agent)
        .all()
    )
    client_type_counts: dict[str, int] = {"human": 0, "agent": 0, "bot": 0, "unknown": 0}
    device_counts: dict[str, int] = {
        "desktop": 0, "mobile": 0, "tablet": 0, "server": 0, "bot": 0, "unknown": 0,
    }
    label_counts: dict[str, int] = {}
    for row in ua_rows:
        cls = classify_user_agent(row.user_agent)
        client_type_counts[cls["client_type"]] = client_type_counts.get(cls["client_type"], 0) + row.count
        device_counts[cls["device"]] = device_counts.get(cls["device"], 0) + row.count
        label_counts[cls["label"]] = label_counts.get(cls["label"], 0) + row.count

    by_client_type = [{"type": k, "count": v} for k, v in client_type_counts.items() if v > 0]
    by_client_type.sort(key=lambda kv: -kv["count"])
    by_device = [{"device": k, "count": v} for k, v in device_counts.items() if v > 0]
    by_device.sort(key=lambda kv: -kv["count"])

    # Top 15 semantic labels (Chrome / curl / GoogleBot / etc)
    top_clients = sorted(
        [{"label": k, "count": v} for k, v in label_counts.items()],
        key=lambda kv: -kv["count"],
    )[:15]

    # ── Recent 50 requests (v6.49: senza IP, con classification) ──
    rr_rows = (
        db.query(ApiRequestLog)
        .order_by(desc(ApiRequestLog.id))
        .limit(50)
        .all()
    )
    recent_requests = []
    for r in rr_rows:
        cls = classify_user_agent(r.user_agent)
        recent_requests.append({
            "timestamp": r.timestamp,
            "method": r.method,
            "path": r.path,
            "category": classify_endpoint(r.path),
            "status_code": r.status_code,
            "response_time_ms": round(r.response_time_ms, 2),
            "client_type": cls["client_type"],
            "device": cls["device"],
            "client_label": cls["label"],
        })

    return JSONResponse(content={
        "summary": summary,
        "requests_per_day": requests_per_day,
        "top_endpoints": top_endpoints,
        "by_category": by_category,
        "by_client_type": by_client_type,
        "by_device": by_device,
        "top_clients": top_clients,
        "recent_requests": recent_requests,
    })


# ─── HTML dashboard page ───────────────────────────────────────────

DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AtlasPI Analytics Dashboard</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    background: #1a1a2e; color: #e0e0e0; padding: 20px; line-height: 1.5;
  }
  h1 { color: #e94560; font-size: 1.8rem; margin-bottom: 6px; }
  .subtitle { color: #888; font-size: 0.85rem; margin-bottom: 24px; }

  /* Summary cards */
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 28px; }
  .card {
    background: #16213e; border-radius: 10px; padding: 20px;
    border-left: 4px solid #e94560;
  }
  .card .label { font-size: 0.75rem; text-transform: uppercase; color: #888; letter-spacing: 0.5px; }
  .card .value { font-size: 1.8rem; font-weight: 700; color: #fff; margin-top: 4px; }

  /* Chart */
  .chart-container {
    background: #16213e; border-radius: 10px; padding: 20px; margin-bottom: 28px;
  }
  .chart-container h2 { color: #e94560; font-size: 1.1rem; margin-bottom: 12px; }
  canvas { width: 100% !important; height: 220px; display: block; }

  /* Horizontal breakdown bars */
  .breakdown-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 16px; margin-bottom: 28px;
  }
  .breakdown {
    background: #16213e; border-radius: 10px; padding: 20px;
  }
  .breakdown h2 { color: #e94560; font-size: 1.05rem; margin-bottom: 12px; }
  .bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
  .bar-row .name {
    flex: 0 0 120px; font-size: 0.85rem;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  .bar-row .bar-wrap { flex: 1; height: 14px; background: #0f1e35; border-radius: 3px; position: relative; }
  .bar-row .bar { height: 100%; border-radius: 3px; }
  .bar-row .count { flex: 0 0 60px; text-align: right; font-size: 0.8rem; color: #aaa; font-family: 'Consolas', monospace; }

  .bar-human { background: #4caf50; }
  .bar-agent { background: #58a6ff; }
  .bar-bot { background: #ff9800; }
  .bar-unknown { background: #666; }

  .bar-desktop { background: #58a6ff; }
  .bar-mobile { background: #4caf50; }
  .bar-tablet { background: #9c27b0; }
  .bar-server { background: #ff9800; }
  .bar-bot2 { background: #f85149; }

  .bar-cat { background: #e94560; }

  /* Tables */
  .table-section { margin-bottom: 28px; }
  .table-section h2 { color: #e94560; font-size: 1.1rem; margin-bottom: 10px; }
  .table-wrap { overflow-x: auto; border-radius: 10px; background: #16213e; }
  table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
  thead th {
    background: #0f3460; color: #e94560; padding: 10px 12px;
    text-align: left; font-weight: 600; white-space: nowrap;
    position: sticky; top: 0;
  }
  tbody td { padding: 8px 12px; border-top: 1px solid #1a1a2e; }
  tbody tr:hover { background: #1a2744; }
  .mono { font-family: 'Consolas', 'Monaco', monospace; font-size: 0.8rem; }
  .status-2 { color: #4caf50; }
  .status-3 { color: #ff9800; }
  .status-4 { color: #e94560; }
  .status-5 { color: #f44336; }
  .truncate { max-width: 360px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .right { text-align: right; }
  .pill {
    display: inline-block; padding: 2px 8px; border-radius: 10px;
    font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
  }
  .pill-human { background: #1e3c22; color: #4caf50; }
  .pill-agent { background: #1e2a45; color: #58a6ff; }
  .pill-bot { background: #3c2b12; color: #ff9800; }
  .pill-unknown { background: #2a2a2a; color: #888; }

  /* Loading / error */
  #loading { text-align: center; padding: 60px 0; color: #888; }
  #error { text-align: center; padding: 40px 0; color: #e94560; display: none; }

  /* Responsive */
  @media (max-width: 600px) {
    body { padding: 12px; }
    h1 { font-size: 1.3rem; }
    .card .value { font-size: 1.3rem; }
    table { font-size: 0.75rem; }
    thead th, tbody td { padding: 6px 8px; }
    .bar-row .name { flex: 0 0 90px; }
  }
</style>
</head>
<body>

<h1>AtlasPI Analytics Dashboard</h1>
<p class="subtitle">v6.49 — traffic semantics (no raw IPs) &middot; auto-refresh 60s &middot; <span id="last-update">loading...</span></p>

<div id="loading">Loading analytics data...</div>
<div id="error">Failed to load analytics data. Retrying...</div>

<div id="dashboard" style="display:none;">

  <!-- Summary cards -->
  <div class="cards">
    <div class="card"><div class="label">Total Requests</div><div class="value" id="s-total">-</div></div>
    <div class="card"><div class="label">Unique Visitors</div><div class="value" id="s-visitors">-</div></div>
    <div class="card"><div class="label">Top Category</div><div class="value" id="s-topcat" style="font-size:1.1rem;">-</div></div>
    <div class="card"><div class="label">Avg Response Time</div><div class="value" id="s-avg">-</div></div>
  </div>

  <!-- Chart -->
  <div class="chart-container">
    <h2>Requests per Day (last 30 days)</h2>
    <canvas id="chart"></canvas>
  </div>

  <!-- Breakdowns: who / device / what -->
  <div class="breakdown-grid">
    <div class="breakdown">
      <h2>By Client Type (human / agent / bot)</h2>
      <div id="bd-client"></div>
    </div>
    <div class="breakdown">
      <h2>By Device</h2>
      <div id="bd-device"></div>
    </div>
    <div class="breakdown">
      <h2>By Endpoint Category</h2>
      <div id="bd-cat"></div>
    </div>
  </div>

  <!-- Top endpoints -->
  <div class="table-section">
    <h2>Top 20 Endpoints</h2>
    <div class="table-wrap"><table>
      <thead><tr><th>#</th><th>Path</th><th class="right">Count</th><th class="right">Avg ms</th></tr></thead>
      <tbody id="t-endpoints"></tbody>
    </table></div>
  </div>

  <!-- Top Clients (semantic labels — browsers/sdks/bots) -->
  <div class="table-section">
    <h2>Top Clients</h2>
    <div class="table-wrap"><table>
      <thead><tr><th>#</th><th>Client</th><th class="right">Count</th></tr></thead>
      <tbody id="t-clients"></tbody>
    </table></div>
  </div>

  <!-- Recent requests (no IPs — client_type + device instead) -->
  <div class="table-section">
    <h2>Recent 50 Requests</h2>
    <div class="table-wrap" style="max-height:480px; overflow-y:auto;"><table>
      <thead><tr>
        <th>Time</th><th>Method</th><th>Path</th>
        <th>Category</th><th>Who</th><th>Device</th>
        <th class="right">Status</th><th class="right">ms</th>
      </tr></thead>
      <tbody id="t-recent"></tbody>
    </table></div>
  </div>

</div>

<script>
function fmt(n) { return n >= 1000 ? (n/1000).toFixed(1) + 'k' : String(n); }
function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function statusClass(c) { return 'status-' + String(c)[0]; }

function drawChart(canvas, data) {
  const items = data.slice().reverse();
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx.scale(dpr, dpr);
  const W = rect.width, H = rect.height;
  const pad = {top: 10, right: 10, bottom: 40, left: 50};
  const cW = W - pad.left - pad.right;
  const cH = H - pad.top - pad.bottom;

  if (!items.length) {
    ctx.fillStyle = '#888'; ctx.font = '14px sans-serif'; ctx.textAlign = 'center';
    ctx.fillText('No data yet', W/2, H/2);
    return;
  }

  const maxVal = Math.max(...items.map(d => d.count), 1);
  const barW = Math.max(2, (cW / items.length) - 2);

  ctx.strokeStyle = '#1a2744'; ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pad.top + cH - (cH * i / 4);
    ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(W - pad.right, y); ctx.stroke();
    ctx.fillStyle = '#666'; ctx.font = '11px sans-serif'; ctx.textAlign = 'right';
    ctx.fillText(fmt(Math.round(maxVal * i / 4)), pad.left - 6, y + 4);
  }

  items.forEach((d, i) => {
    const x = pad.left + (cW / items.length) * i + 1;
    const barH = (d.count / maxVal) * cH;
    const y = pad.top + cH - barH;
    ctx.fillStyle = '#e94560';
    ctx.fillRect(x, y, barW, barH);
    const step = items.length <= 10 ? 1 : items.length <= 20 ? 2 : 3;
    if (i % step === 0) {
      ctx.save();
      ctx.translate(x + barW/2, pad.top + cH + 6);
      ctx.rotate(-Math.PI / 4);
      ctx.fillStyle = '#888'; ctx.font = '10px sans-serif'; ctx.textAlign = 'right';
      ctx.fillText(d.date.slice(5), 0, 0);
      ctx.restore();
    }
  });
}

function renderBarBreakdown(targetId, items, nameKey, colorClassFn) {
  const tgt = document.getElementById(targetId);
  if (!tgt) return;
  const max = Math.max(...items.map(i => i.count), 1);
  tgt.innerHTML = items.map(item => {
    const pct = (item.count / max) * 100;
    const name = item[nameKey] || '-';
    const colorClass = colorClassFn(name);
    return '<div class="bar-row">' +
      '<div class="name" title="' + esc(name) + '">' + esc(name) + '</div>' +
      '<div class="bar-wrap"><div class="bar ' + colorClass + '" style="width:' + pct + '%"></div></div>' +
      '<div class="count">' + fmt(item.count) + '</div>' +
    '</div>';
  }).join('');
}

function pillFor(clientType) {
  return '<span class="pill pill-' + clientType + '">' + clientType + '</span>';
}

async function load() {
  try {
    const res = await fetch('/admin/analytics/data');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const d = await res.json();

    document.getElementById('loading').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';

    // Summary
    document.getElementById('s-total').textContent = fmt(d.summary.total_requests);
    document.getElementById('s-visitors').textContent = fmt(d.summary.unique_visitors);
    document.getElementById('s-avg').textContent = d.summary.avg_response_time_ms + ' ms';
    document.getElementById('s-topcat').textContent = d.by_category.length ? d.by_category[0].category : '-';

    // Chart
    drawChart(document.getElementById('chart'), d.requests_per_day);
    window._lastData = d.requests_per_day;

    // Breakdowns
    renderBarBreakdown('bd-client', d.by_client_type, 'type', name => 'bar-' + name);
    renderBarBreakdown('bd-device', d.by_device, 'device', name => {
      return name === 'bot' ? 'bar-bot2' : 'bar-' + name;
    });
    renderBarBreakdown('bd-cat', d.by_category, 'category', () => 'bar-cat');

    // Top endpoints
    document.getElementById('t-endpoints').innerHTML = d.top_endpoints.map((r, i) =>
      '<tr><td>' + (i+1) + '</td><td class="mono">' + esc(r.path) + '</td><td class="right">' + r.count + '</td><td class="right">' + r.avg_ms + '</td></tr>'
    ).join('');

    // Top Clients
    document.getElementById('t-clients').innerHTML = d.top_clients.map((r, i) =>
      '<tr><td>' + (i+1) + '</td><td>' + esc(r.label) + '</td><td class="right">' + fmt(r.count) + '</td></tr>'
    ).join('');

    // Recent requests (no IPs)
    document.getElementById('t-recent').innerHTML = d.recent_requests.map(r =>
      '<tr>' +
        '<td class="mono" style="white-space:nowrap;">' + esc(r.timestamp) + '</td>' +
        '<td>' + esc(r.method) + '</td>' +
        '<td class="mono truncate" title="' + esc(r.path) + '">' + esc(r.path) + '</td>' +
        '<td>' + esc(r.category) + '</td>' +
        '<td>' + pillFor(r.client_type) + ' <small style="color:#888">' + esc(r.client_label) + '</small></td>' +
        '<td>' + esc(r.device) + '</td>' +
        '<td class="right ' + statusClass(r.status_code) + '">' + r.status_code + '</td>' +
        '<td class="right">' + r.response_time_ms + '</td>' +
      '</tr>'
    ).join('');

    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
  } catch (e) {
    console.error('Analytics load error:', e);
    document.getElementById('loading').style.display = 'none';
    document.getElementById('error').style.display = 'block';
  }
}

load();
setInterval(load, 60000);

window.addEventListener('resize', () => {
  const canvas = document.getElementById('chart');
  if (canvas && window._lastData) drawChart(canvas, window._lastData);
});
</script>
</body>
</html>
"""


@router.get(
    "/admin/analytics",
    response_class=HTMLResponse,
    summary="Dashboard analytics (HTML)",
    description="Pagina HTML con dashboard analytics interattiva (v6.49 ridisegnata).",
    include_in_schema=False,
)
def analytics_dashboard():
    """Serve la pagina HTML della dashboard analytics."""
    return HTMLResponse(content=DASHBOARD_HTML)
