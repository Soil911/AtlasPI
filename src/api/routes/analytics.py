"""Analytics dashboard per AtlasPI.

GET /admin/analytics       — pagina HTML con dashboard interattiva
GET /admin/analytics/data  — dati JSON grezzi per il dashboard
"""

import logging

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import ApiRequestLog

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin"])


# ─── JSON data endpoint ────────────────────────────────────────────


@router.get(
    "/admin/analytics/data",
    summary="Dati analytics grezzi (JSON)",
    description="Ritorna statistiche aggregate sulle richieste API.",
    include_in_schema=False,
)
def analytics_data(db: Session = Depends(get_db)):
    """Dati grezzi per la dashboard analytics."""

    # ── Summary ──────────────────────────────────────────────────
    total_requests = db.query(func.count(ApiRequestLog.id)).scalar() or 0
    unique_ips = db.query(func.count(func.distinct(ApiRequestLog.client_ip))).scalar() or 0
    avg_response_time = db.query(func.avg(ApiRequestLog.response_time_ms)).scalar()
    avg_response_time = round(avg_response_time, 2) if avg_response_time else 0.0
    first_request = db.query(func.min(ApiRequestLog.timestamp)).scalar()
    last_request = db.query(func.max(ApiRequestLog.timestamp)).scalar()

    summary = {
        "total_requests": total_requests,
        "unique_ips": unique_ips,
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

    # ── Top 20 IPs ───────────────────────────────────────────────
    ti_rows = (
        db.query(
            ApiRequestLog.client_ip,
            func.count(ApiRequestLog.id).label("count"),
            func.max(ApiRequestLog.timestamp).label("last_seen"),
        )
        .group_by(ApiRequestLog.client_ip)
        .order_by(desc("count"))
        .limit(20)
        .all()
    )
    top_ips = [
        {"ip": r.client_ip, "count": r.count, "last_seen": r.last_seen}
        for r in ti_rows
    ]

    # ── Top 15 user agents ───────────────────────────────────────
    ua_rows = (
        db.query(
            ApiRequestLog.user_agent,
            func.count(ApiRequestLog.id).label("count"),
        )
        .group_by(ApiRequestLog.user_agent)
        .order_by(desc("count"))
        .limit(15)
        .all()
    )
    top_user_agents = [
        {"user_agent": r.user_agent or "Unknown", "count": r.count}
        for r in ua_rows
    ]

    # ── Recent 50 requests ───────────────────────────────────────
    rr_rows = (
        db.query(ApiRequestLog)
        .order_by(desc(ApiRequestLog.id))
        .limit(50)
        .all()
    )
    recent_requests = [
        {
            "timestamp": r.timestamp,
            "method": r.method,
            "path": r.path,
            "status_code": r.status_code,
            "response_time_ms": round(r.response_time_ms, 2),
            "client_ip": r.client_ip,
        }
        for r in rr_rows
    ]

    return JSONResponse(content={
        "summary": summary,
        "requests_per_day": requests_per_day,
        "top_endpoints": top_endpoints,
        "top_ips": top_ips,
        "top_user_agents": top_user_agents,
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

  /* ── Summary cards ────────────────────────────────────── */
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 28px; }
  .card {
    background: #16213e; border-radius: 10px; padding: 20px;
    border-left: 4px solid #e94560;
  }
  .card .label { font-size: 0.75rem; text-transform: uppercase; color: #888; letter-spacing: 0.5px; }
  .card .value { font-size: 1.8rem; font-weight: 700; color: #fff; margin-top: 4px; }

  /* ── Chart ─────────────────────────────────────────────── */
  .chart-container {
    background: #16213e; border-radius: 10px; padding: 20px; margin-bottom: 28px;
  }
  .chart-container h2 { color: #e94560; font-size: 1.1rem; margin-bottom: 12px; }
  canvas { width: 100% !important; height: 220px; display: block; }

  /* ── Tables ────────────────────────────────────────────── */
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

  /* ── Loading / error ──────────────────────────────────── */
  #loading { text-align: center; padding: 60px 0; color: #888; }
  #error { text-align: center; padding: 40px 0; color: #e94560; display: none; }

  /* ── Responsive ───────────────────────────────────────── */
  @media (max-width: 600px) {
    body { padding: 12px; }
    h1 { font-size: 1.3rem; }
    .card .value { font-size: 1.3rem; }
    table { font-size: 0.75rem; }
    thead th, tbody td { padding: 6px 8px; }
  }
</style>
</head>
<body>

<h1>AtlasPI Analytics Dashboard</h1>
<p class="subtitle">Auto-refresh every 60s &mdash; <span id="last-update">loading...</span></p>

<div id="loading">Loading analytics data...</div>
<div id="error">Failed to load analytics data. Retrying...</div>

<div id="dashboard" style="display:none;">

  <!-- Summary cards -->
  <div class="cards">
    <div class="card"><div class="label">Total Requests</div><div class="value" id="s-total">-</div></div>
    <div class="card"><div class="label">Unique IPs</div><div class="value" id="s-ips">-</div></div>
    <div class="card"><div class="label">Top Endpoint</div><div class="value" id="s-top" style="font-size:1rem;">-</div></div>
    <div class="card"><div class="label">Avg Response Time</div><div class="value" id="s-avg">-</div></div>
  </div>

  <!-- Chart -->
  <div class="chart-container">
    <h2>Requests per Day (last 30 days)</h2>
    <canvas id="chart"></canvas>
  </div>

  <!-- Top endpoints -->
  <div class="table-section">
    <h2>Top 20 Endpoints</h2>
    <div class="table-wrap"><table>
      <thead><tr><th>#</th><th>Path</th><th class="right">Count</th><th class="right">Avg ms</th></tr></thead>
      <tbody id="t-endpoints"></tbody>
    </table></div>
  </div>

  <!-- Top IPs -->
  <div class="table-section">
    <h2>Top 20 IPs</h2>
    <div class="table-wrap"><table>
      <thead><tr><th>#</th><th>IP</th><th class="right">Count</th><th>Last Seen</th></tr></thead>
      <tbody id="t-ips"></tbody>
    </table></div>
  </div>

  <!-- Top User Agents -->
  <div class="table-section">
    <h2>Top User Agents</h2>
    <div class="table-wrap"><table>
      <thead><tr><th>#</th><th>User Agent</th><th class="right">Count</th></tr></thead>
      <tbody id="t-ua"></tbody>
    </table></div>
  </div>

  <!-- Recent requests -->
  <div class="table-section">
    <h2>Recent 50 Requests</h2>
    <div class="table-wrap" style="max-height:480px; overflow-y:auto;"><table>
      <thead><tr><th>Time</th><th>Method</th><th>Path</th><th class="right">Status</th><th class="right">ms</th><th>IP</th></tr></thead>
      <tbody id="t-recent"></tbody>
    </table></div>
  </div>

</div>

<script>
function fmt(n) { return n >= 1000 ? (n/1000).toFixed(1) + 'k' : String(n); }
function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function statusClass(c) { return 'status-' + String(c)[0]; }

function drawChart(canvas, data) {
  // data = [{date, count}, ...] already sorted desc; reverse for chronological
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
    ctx.fillStyle = '#888';
    ctx.font = '14px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('No data yet', W/2, H/2);
    return;
  }

  const maxVal = Math.max(...items.map(d => d.count), 1);
  const barW = Math.max(2, (cW / items.length) - 2);

  // Grid lines
  ctx.strokeStyle = '#1a2744';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pad.top + cH - (cH * i / 4);
    ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(W - pad.right, y); ctx.stroke();
    ctx.fillStyle = '#666'; ctx.font = '11px sans-serif'; ctx.textAlign = 'right';
    ctx.fillText(fmt(Math.round(maxVal * i / 4)), pad.left - 6, y + 4);
  }

  // Bars
  items.forEach((d, i) => {
    const x = pad.left + (cW / items.length) * i + 1;
    const barH = (d.count / maxVal) * cH;
    const y = pad.top + cH - barH;
    ctx.fillStyle = '#e94560';
    ctx.fillRect(x, y, barW, barH);

    // Date label (show every few bars to avoid clutter)
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
    document.getElementById('s-ips').textContent = fmt(d.summary.unique_ips);
    document.getElementById('s-avg').textContent = d.summary.avg_response_time_ms + ' ms';
    document.getElementById('s-top').textContent = d.top_endpoints.length ? d.top_endpoints[0].path : '-';

    // Chart
    drawChart(document.getElementById('chart'), d.requests_per_day);

    // Top endpoints
    document.getElementById('t-endpoints').innerHTML = d.top_endpoints.map((r, i) =>
      '<tr><td>' + (i+1) + '</td><td class="mono">' + esc(r.path) + '</td><td class="right">' + r.count + '</td><td class="right">' + r.avg_ms + '</td></tr>'
    ).join('');

    // Top IPs
    document.getElementById('t-ips').innerHTML = d.top_ips.map((r, i) =>
      '<tr><td>' + (i+1) + '</td><td class="mono">' + esc(r.ip) + '</td><td class="right">' + r.count + '</td><td>' + esc(r.last_seen||'') + '</td></tr>'
    ).join('');

    // User agents
    document.getElementById('t-ua').innerHTML = d.top_user_agents.map((r, i) =>
      '<tr><td>' + (i+1) + '</td><td class="truncate" title="' + esc(r.user_agent) + '">' + esc(r.user_agent.length > 80 ? r.user_agent.slice(0,80) + '...' : r.user_agent) + '</td><td class="right">' + r.count + '</td></tr>'
    ).join('');

    // Recent requests
    document.getElementById('t-recent').innerHTML = d.recent_requests.map(r =>
      '<tr><td class="mono" style="white-space:nowrap;">' + esc(r.timestamp) + '</td><td>' + esc(r.method) + '</td><td class="mono">' + esc(r.path) + '</td><td class="right ' + statusClass(r.status_code) + '">' + r.status_code + '</td><td class="right">' + r.response_time_ms + '</td><td class="mono">' + esc(r.client_ip) + '</td></tr>'
    ).join('');

    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
  } catch (e) {
    console.error('Analytics load error:', e);
    document.getElementById('loading').style.display = 'none';
    document.getElementById('error').style.display = 'block';
  }
}

// Initial load + auto-refresh every 60s
load();
setInterval(load, 60000);

// Redraw chart on resize
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
    description="Pagina HTML con dashboard analytics interattiva.",
    include_in_schema=False,
)
def analytics_dashboard():
    """Serve la pagina HTML della dashboard analytics."""
    return HTMLResponse(content=DASHBOARD_HTML)
