"""Agent-compat routes from AI Co-Founder traffic-pattern suggestions #78-81 (v6.99.97).

External clients repeatedly hit the wrong paths (404 in prod over 30d):
  * /v1/models (10x) — a client treating AtlasPI as an OpenAI-style LLM endpoint.
  * /v1/atlaspi/{cities,events,export/geojson} (6x each) — wrong doubled prefix.

These routes turn those 404s into helpful responses, improving agent usability.
"""
from __future__ import annotations


def test_v1_models_returns_helpful_openai_shaped_stub(client):
    """/v1/models must 200 with an OpenAI-shaped empty list + a pointer to the
    real API, so LLM clients probing it don't crash on a 404."""
    r = client.get("/v1/models")
    assert r.status_code == 200
    body = r.json()
    assert body["object"] == "list"
    assert body["data"] == []
    assert "/v1/entities" in body.get("note", "") or "llms.txt" in body.get("note", "")
    assert "/v1/entities" in body.get("resources", [])


def test_v1_atlaspi_prefix_redirects_preserving_query(client):
    """/v1/atlaspi/{rest} → 308 → /v1/{rest}, query string preserved."""
    r = client.get("/v1/atlaspi/cities?limit=5", follow_redirects=False)
    assert r.status_code == 308
    assert r.headers["location"] == "/v1/cities?limit=5"


def test_v1_atlaspi_nested_path_redirects(client):
    """Covers the nested export path from suggestion #81."""
    r = client.get("/v1/atlaspi/export/geojson?year=1500", follow_redirects=False)
    assert r.status_code == 308
    assert r.headers["location"] == "/v1/export/geojson?year=1500"


def test_v1_atlaspi_redirect_target_is_valid(client):
    """Following the redirect lands on a working canonical endpoint."""
    r = client.get("/v1/atlaspi/cities?limit=1")  # TestClient follows redirects
    assert r.status_code == 200
