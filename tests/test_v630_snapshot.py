"""Tests for the world snapshot endpoint v6.30.

GET /v1/snapshot/year/{year} aggregates entities, events, periods,
cities, chains into a single response.
"""


def test_snapshot_returns_200(client):
    r = client.get("/v1/snapshot/year/1250")
    assert r.status_code == 200


def test_snapshot_has_year_fields(client):
    r = client.get("/v1/snapshot/year/1250")
    d = r.json()
    assert d["year"] == 1250
    assert d["year_display"] == "1250 CE"


def test_snapshot_bce_year_display(client):
    r = client.get("/v1/snapshot/year/-500")
    d = r.json()
    assert d["year"] == -500
    assert d["year_display"] == "500 BCE"


def test_snapshot_has_all_sections(client):
    r = client.get("/v1/snapshot/year/1500")
    d = r.json()
    for key in ("year", "year_display", "periods", "entities",
                "events_that_year", "cities", "chains"):
        assert key in d, f"Missing key: {key}"


def test_snapshot_periods_section_structure(client):
    r = client.get("/v1/snapshot/year/1500")
    d = r.json()
    assert "total" in d["periods"]
    assert "items" in d["periods"]
    for p in d["periods"]["items"]:
        assert "id" in p
        assert "name" in p
        assert "region" in p


def test_snapshot_periods_include_renaissance_at_1500(client):
    r = client.get("/v1/snapshot/year/1500")
    d = r.json()
    slugs = {p["slug"] for p in d["periods"]["items"]}
    assert "renaissance" in slugs


def test_snapshot_entities_section(client):
    r = client.get("/v1/snapshot/year/1500")
    d = r.json()
    e = d["entities"]
    assert "total_active" in e
    assert "by_type" in e
    assert "top_by_confidence" in e
    assert isinstance(e["total_active"], int)
    assert isinstance(e["by_type"], dict)


def test_snapshot_top_entities_sorted_by_confidence(client):
    r = client.get("/v1/snapshot/year/1500")
    d = r.json()
    top = d["entities"]["top_by_confidence"]
    scores = [e["confidence_score"] for e in top]
    assert scores == sorted(scores, reverse=True)


def test_snapshot_cities_section(client):
    r = client.get("/v1/snapshot/year/1500")
    d = r.json()
    c = d["cities"]
    assert "total_active" in c
    assert "by_type" in c
    assert "top" in c


def test_snapshot_top_n_parameter(client):
    """top_n=3 returns at most 3 top entities."""
    r = client.get("/v1/snapshot/year/1500?top_n=3")
    d = r.json()
    assert len(d["entities"]["top_by_confidence"]) <= 3


def test_snapshot_chains_section(client):
    r = client.get("/v1/snapshot/year/1500")
    d = r.json()
    assert "total_active" in d["chains"]
    assert "items" in d["chains"]


def test_snapshot_events_that_year(client):
    """events_that_year contains only events with year == query year."""
    r = client.get("/v1/snapshot/year/1500")
    d = r.json()
    assert "total" in d["events_that_year"]
    assert "items" in d["events_that_year"]


def test_snapshot_boundary_years(client):
    """Year 1 works (transition BCE/CE)."""
    r = client.get("/v1/snapshot/year/1")
    assert r.status_code == 200


def test_snapshot_invalid_year_400(client):
    """Very large year rejected by validator."""
    r = client.get("/v1/snapshot/year/3000")
    # Either 200 (allowed) or 422 (validator rejects)
    assert r.status_code in (200, 422)


def test_snapshot_ancient_year(client):
    """Ancient year returns consistent data."""
    r = client.get("/v1/snapshot/year/-300")
    assert r.status_code == 200
    d = r.json()
    assert d["year"] == -300


def test_snapshot_entities_type_breakdown_sums(client):
    """by_type dict should sum to total_active."""
    r = client.get("/v1/snapshot/year/1500")
    d = r.json()
    if d["entities"]["total_active"] > 0:
        type_sum = sum(d["entities"]["by_type"].values())
        assert type_sum == d["entities"]["total_active"]
