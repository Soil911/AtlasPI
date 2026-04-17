"""v6.49: tests per analytics redesign — user-agent classification + endpoint category."""

import pytest

from src.api.routes.analytics import classify_user_agent, classify_endpoint


# ─── classify_user_agent ────────────────────────────────────────

def test_ua_empty():
    r = classify_user_agent("")
    assert r["client_type"] == "unknown"
    assert r["device"] == "unknown"


def test_ua_none():
    r = classify_user_agent(None)
    assert r["client_type"] == "unknown"


def test_ua_chrome_desktop():
    r = classify_user_agent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    assert r["client_type"] == "human"
    assert r["device"] == "desktop"
    assert r["label"] == "Chrome"


def test_ua_chrome_mobile():
    r = classify_user_agent(
        "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    )
    assert r["client_type"] == "human"
    assert r["device"] == "mobile"


def test_ua_safari_iphone():
    r = classify_user_agent(
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    )
    assert r["client_type"] == "human"
    assert r["device"] == "mobile"


def test_ua_ipad():
    r = classify_user_agent("Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) Safari/604.1")
    assert r["device"] == "tablet"


def test_ua_firefox():
    r = classify_user_agent("Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0")
    assert r["label"] == "Firefox"
    assert r["device"] == "desktop"


def test_ua_curl():
    r = classify_user_agent("curl/8.4.0")
    assert r["client_type"] == "agent"
    assert r["device"] == "server"
    assert r["label"] == "curl"


def test_ua_python_requests():
    r = classify_user_agent("python-requests/2.31.0")
    assert r["client_type"] == "agent"
    assert r["device"] == "server"


def test_ua_atlaspi_mcp():
    r = classify_user_agent("atlaspi-mcp/0.8.0 (+https://github.com/Soil911/AtlasPI)")
    assert r["client_type"] == "agent"
    assert r["label"] == "AtlasPI MCP"


def test_ua_googlebot():
    r = classify_user_agent("Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)")
    assert r["client_type"] == "bot"
    assert r["device"] == "bot"
    assert r["label"] == "GoogleBot"


def test_ua_chatgpt():
    r = classify_user_agent("Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot")
    assert r["client_type"] == "bot"
    assert r["label"] == "ChatGPT-User"


def test_ua_claudebot():
    r = classify_user_agent("Mozilla/5.0 (compatible; ClaudeBot/1.0; +claudebot@anthropic.com)")
    assert r["client_type"] == "bot"
    assert r["label"] == "ClaudeBot"


def test_ua_httpx():
    r = classify_user_agent("python-httpx/0.27.0")
    assert r["client_type"] == "agent"


# ─── classify_endpoint ─────────────────────────────────────────

def test_category_entities():
    assert classify_endpoint("/v1/entities") == "entities"
    assert classify_endpoint("/v1/entities/42") == "entities"
    assert classify_endpoint("/v1/entities/batch?ids=1,2,3") == "entities"
    assert classify_endpoint("/v1/entities/light") == "entities"


def test_category_events():
    assert classify_endpoint("/v1/events") == "events"
    assert classify_endpoint("/v1/events/on-this-day/07-14") == "events"


def test_category_sites_rulers_languages():
    assert classify_endpoint("/v1/sites") == "sites"
    assert classify_endpoint("/v1/sites/nearby") == "sites"
    assert classify_endpoint("/v1/rulers/at-year/1250") == "rulers"
    assert classify_endpoint("/v1/languages/at-year/0") == "languages"


def test_category_geo_query():
    assert classify_endpoint("/v1/where-was") == "geo_query"
    assert classify_endpoint("/v1/nearby") == "geo_query"
    assert classify_endpoint("/v1/snapshot/1250") == "geo_query"


def test_category_render_export():
    assert classify_endpoint("/v1/render/snapshot/1250.png") == "render"
    assert classify_endpoint("/v1/export/sites.geojson") == "export"


def test_category_health():
    assert classify_endpoint("/health") == "health"
    assert classify_endpoint("/metrics") == "health"


def test_category_admin():
    assert classify_endpoint("/admin/analytics") == "admin"


def test_category_other():
    assert classify_endpoint("/some-random-path") == "other"


# ─── Endpoint /admin/analytics/data ────────────────────────────

def test_analytics_data_endpoint(client):
    r = client.get("/admin/analytics/data")
    assert r.status_code == 200
    data = r.json()
    # v6.49 schema
    assert "summary" in data
    assert "unique_visitors" in data["summary"]
    assert "by_category" in data
    assert "by_client_type" in data
    assert "by_device" in data
    assert "top_clients" in data
    # v6.49: IPs removed from top-level
    assert "top_ips" not in data


def test_analytics_dashboard_html(client):
    r = client.get("/admin/analytics")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    body = r.text
    # v6.49: new sections present
    assert "By Client Type" in body
    assert "By Device" in body
    assert "By Endpoint Category" in body
    # v6.49: no more "Top IPs" section in dashboard
    assert "Top 20 IPs" not in body
