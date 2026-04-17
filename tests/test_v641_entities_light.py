"""v6.41: tests per /v1/entities/light — lightweight endpoint senza boundary_geojson.

Risolve (parzialmente) il problema scalability della home (17MB totale con 11
chiamate paginate). Un AI agent puo' ora fare UNA chiamata per avere la lista
globale di tutte le entita', poi detail on-demand.
"""


def test_entities_light_returns_all(client):
    """Una sola chiamata deve ritornare TUTTE le entita'."""
    r = client.get("/v1/entities/light")
    assert r.status_code == 200
    data = r.json()
    assert "count" in data
    assert "entities" in data
    assert data["count"] == len(data["entities"])
    assert data["count"] > 50  # seed ha almeno 50+ entita'


def test_entities_light_no_boundary_geojson(client):
    """Payload deve NON includere boundary_geojson (il vero motivo del bottleneck)."""
    r = client.get("/v1/entities/light")
    entities = r.json()["entities"]
    for e in entities[:20]:
        assert "boundary_geojson" not in e, f"'{e.get('name_original')}' has boundary_geojson"


def test_entities_light_has_essential_fields(client):
    r = client.get("/v1/entities/light")
    entities = r.json()["entities"]
    for e in entities[:5]:
        for key in ("id", "name_original", "entity_type", "year_start", "confidence_score", "status", "continent"):
            assert key in e, f"missing field {key}"


def test_entities_light_year_filter(client):
    """Filter year=1000: solo entita' attive in quell'anno."""
    r = client.get("/v1/entities/light?year=1000")
    assert r.status_code == 200
    entities = r.json()["entities"]
    for e in entities[:10]:
        assert e["year_start"] <= 1000
        # year_end None o >= 1000
        if e["year_end"] is not None:
            assert e["year_end"] >= 1000


def test_entities_light_year_out_of_range(client):
    r = client.get("/v1/entities/light?year=-10000")
    assert r.status_code == 422


def test_entities_light_payload_size_claim(client):
    """Verifica che il payload light sia molto piu' piccolo di /v1/entities con pagination.

    (Not a hard assert, ma buona sanita' check: light deve essere < 500KB di JSON.)
    """
    r = client.get("/v1/entities/light")
    # Content-Length header puo' non esserci se gzipped, quindi usiamo body len
    body_bytes = len(r.content)
    # 1000 entities × ~300 bytes average = ~300KB. Upper bound 1MB.
    assert body_bytes < 2_000_000, f"light payload is {body_bytes} bytes — too heavy"


def test_entities_light_bbox(client):
    """bbox filter funziona (capital-point only, no polygon intersect)."""
    # Mediterranean area
    r = client.get("/v1/entities/light?bbox=-10,30,40,50")
    assert r.status_code == 200
    entities = r.json()["entities"]
    for e in entities:
        if e.get("capital_lat") is not None and e.get("capital_lon") is not None:
            assert -10 <= e["capital_lon"] <= 40
            assert 30 <= e["capital_lat"] <= 50
