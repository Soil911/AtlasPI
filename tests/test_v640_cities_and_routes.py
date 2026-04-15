"""Test per /v1/cities + /v1/routes (v6.4.0).

Questi test fabbricano dati di fixture direttamente nel DB (NON dipendono
dai batch JSON ingesti dagli agenti di seed) così coprono la logica
endpoint/modello a prescindere dalla presenza di dati di produzione.

Aree coperte:
    * List + filtri (year, type, entity_id, bbox, involves_slavery)
    * Detail + 404
    * ETHICS-009: name_variants su città rinominate
    * ETHICS-010: routes con "humans_enslaved" e involves_slavery=True
    * OpenAPI documentation
"""

from __future__ import annotations

import json

import pytest

from src.db.models import HistoricalCity, RouteCityLink, TradeRoute


@pytest.fixture
def seeded_cities_and_routes(db):
    """Crea un minimo set di città e rotte per i test.

    Function-scoped (vincolato dallo scope del fixture `db` di conftest.py).
    Il pattern check-existing rende la fixture idempotente, quindi chiamate
    multiple nello stesso DB non creano duplicati.
    """
    # Evita duplicati se il modulo è ri-eseguito nella stessa sessione.
    existing = {c.name_original for c in db.query(HistoricalCity).all()}

    cities_data = [
        dict(
            name_original="Kōnstantinoupolis",
            name_original_lang="el",
            latitude=41.0082, longitude=28.9784,
            founded_year=330, abandoned_year=None,
            city_type="CAPITAL",
            population_peak=500000, population_peak_year=500,
            confidence_score=0.95,
            ethical_notes=(
                "Renamed Istanbul after Ottoman conquest 1453. The Hagia "
                "Sophia was converted to a mosque; much of the Greek "
                "Christian identity was systematically transformed."
            ),
            name_variants=json.dumps([
                {"name": "Istanbul", "lang": "tr", "period_start": 1453,
                 "period_end": None, "context": "Ottoman name imposed after conquest"},
                {"name": "Byzantium", "lang": "la", "period_start": -657,
                 "period_end": 330, "context": "Pre-Christian name"},
            ]),
            sources=json.dumps([
                {"citation": "Oxford Dictionary of Byzantium", "url": None,
                 "source_type": "academic"}
            ]),
        ),
        dict(
            name_original="Samarqand",
            name_original_lang="fa",
            latitude=39.6548, longitude=66.9597,
            founded_year=-700, abandoned_year=None,
            city_type="TRADE_HUB",
            population_peak=200000, population_peak_year=1370,
            confidence_score=0.9,
            ethical_notes=None,
            sources=None, name_variants=None,
        ),
        dict(
            name_original="Tenōchtitlan",
            name_original_lang="nah",
            latitude=19.4326, longitude=-99.1332,
            founded_year=1325, abandoned_year=1521,
            city_type="CAPITAL",
            population_peak=200000, population_peak_year=1500,
            confidence_score=0.9,
            ethical_notes=(
                "Destroyed by Hernán Cortés 1521. Templo Mayor deliberately "
                "demolished; Catedral Metropolitana built on top as act of "
                "cultural erasure. Population collapsed ~200k → few thousand "
                "after smallpox + conquest."
            ),
            name_variants=json.dumps([
                {"name": "Mexico City", "lang": "es", "period_start": 1521,
                 "period_end": None, "context": "Imposed after Spanish conquest"}
            ]),
            sources=None,
        ),
        # Tiny test city for bbox filter edge cases
        dict(
            name_original="TestCity-South",
            name_original_lang="en",
            latitude=-45.0, longitude=-70.0,
            founded_year=1800, abandoned_year=None,
            city_type="OTHER",
            population_peak=None, population_peak_year=None,
            confidence_score=0.5,
            ethical_notes=None, sources=None, name_variants=None,
        ),
    ]

    for cd in cities_data:
        if cd["name_original"] in existing:
            continue
        db.add(HistoricalCity(**cd))
    db.commit()

    # Rotte: una non-schiavista, una schiavista (ETHICS-010), una con
    # waypoint che punta alle città appena create.
    existing_routes = {r.name_original for r in db.query(TradeRoute).all()}

    routes_data = [
        dict(
            name_original="Silk Road",
            name_original_lang="en",
            route_type="CARAVAN",
            start_year=-130, end_year=1453,
            geometry_geojson=json.dumps({
                "type": "LineString",
                "coordinates": [
                    [108.94, 34.34], [94.66, 40.14],  # Chang'an → Dunhuang
                    [66.96, 39.65],                    # Samarqand
                    [28.98, 41.01],                    # Kōnstantinoupolis
                ]
            }),
            commodities=json.dumps(["silk", "porcelain", "paper-technology"]),
            description="Chang'an → Kōnstantinoupolis overland network.",
            involves_slavery=False,
            confidence_score=0.85,
            ethical_notes=(
                "'Silk Road' is a 19th-c. German neologism (Richthofen 1877); "
                "the historical network was not called that by its users."
            ),
            sources=json.dumps([
                {"citation": "Hansen, V. 'The Silk Road: A New History'",
                 "url": None, "source_type": "academic"}
            ]),
        ),
        dict(
            name_original="Trans-Atlantic Slave Trade",
            name_original_lang="en",
            route_type="SEA",
            start_year=1500, end_year=1866,
            geometry_geojson=json.dumps({
                "type": "MultiLineString",
                "coordinates": [
                    [[7.34, 4.85], [-38.50, -12.97]],   # Bonny → Salvador
                    [[8.77, -8.81], [-76.61, 17.99]],   # Luanda → Jamaica
                ]
            }),
            commodities=json.dumps(["humans_enslaved", "sugar", "cotton", "tobacco"]),
            description="Atlantic passage trafficking ~12.5M enslaved Africans.",
            involves_slavery=True,
            confidence_score=0.95,
            ethical_notes=(
                "~12.5 million humans kidnapped and trafficked Africa→Americas; "
                "~2 million died in the Middle Passage. Main actors: Portuguese, "
                "British, Dutch, French, Spanish, US merchants; Royal African "
                "Company; Companhia do Grão-Pará. Foundation of Atlantic "
                "capitalism; demographic devastation of African societies."
            ),
            sources=json.dumps([
                {"citation": "Eltis, D. 'Trans-Atlantic Slave Trade Database'",
                 "url": "https://slavevoyages.org", "source_type": "academic"}
            ]),
        ),
    ]

    for rd in routes_data:
        if rd["name_original"] in existing_routes:
            continue
        route = TradeRoute(**rd)
        db.add(route)
        db.flush()  # get route.id

        # Aggiungi waypoints per Silk Road che toccano le nostre città.
        if rd["name_original"] == "Silk Road":
            for i, cname in enumerate(["Samarqand", "Kōnstantinoupolis"]):
                city = db.query(HistoricalCity).filter_by(name_original=cname).first()
                if city is None:
                    continue
                db.add(RouteCityLink(
                    route_id=route.id, city_id=city.id,
                    sequence_order=i, is_terminal=(i == 1),
                ))

    db.commit()
    yield


# ─── CITIES LIST ────────────────────────────────────────────────────────


def test_cities_list_returns_cities(client, seeded_cities_and_routes):
    r = client.get("/v1/cities?limit=100")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 3
    names = {c["name_original"] for c in body["cities"]}
    assert {"Kōnstantinoupolis", "Samarqand", "Tenōchtitlan"} <= names


def test_cities_filter_by_type(client, seeded_cities_and_routes):
    r = client.get("/v1/cities?city_type=CAPITAL&limit=50")
    assert r.status_code == 200
    for c in r.json()["cities"]:
        assert c["city_type"] == "CAPITAL"


def test_cities_filter_by_year_excludes_abandoned(client, seeded_cities_and_routes):
    # Year 1600: Tenōchtitlan abandoned 1521 should NOT appear.
    # Kōnstantinoupolis founded 330, still around: should appear.
    r = client.get("/v1/cities?year=1600&limit=50")
    assert r.status_code == 200
    names = {c["name_original"] for c in r.json()["cities"]}
    assert "Kōnstantinoupolis" in names
    assert "Tenōchtitlan" not in names


def test_cities_filter_by_year_includes_active(client, seeded_cities_and_routes):
    # Year 1500: Tenōchtitlan still exists (founded 1325, abandoned 1521).
    r = client.get("/v1/cities?year=1500&limit=50")
    assert r.status_code == 200
    names = {c["name_original"] for c in r.json()["cities"]}
    assert "Tenōchtitlan" in names


def test_cities_bbox_filter(client, seeded_cities_and_routes):
    # Bbox Bosphorus area — should include Kōnstantinoupolis (41, 29).
    r = client.get("/v1/cities?bbox=28,40,30,42&limit=50")
    assert r.status_code == 200
    names = {c["name_original"] for c in r.json()["cities"]}
    assert "Kōnstantinoupolis" in names
    assert "Tenōchtitlan" not in names
    assert "TestCity-South" not in names


def test_cities_bbox_invalid_returns_422(client, seeded_cities_and_routes):
    r = client.get("/v1/cities?bbox=not-a-bbox")
    assert r.status_code == 422
    r = client.get("/v1/cities?bbox=1,2,3")
    assert r.status_code == 422
    r = client.get("/v1/cities?bbox=10,10,0,20")  # min>max
    assert r.status_code == 422


# ─── CITIES DETAIL ──────────────────────────────────────────────────────


def test_city_detail_includes_name_variants(client, db, seeded_cities_and_routes):
    """ETHICS-009: name_variants devono essere esposti nel detail."""
    city = db.query(HistoricalCity).filter_by(name_original="Kōnstantinoupolis").first()
    r = client.get(f"/v1/cities/{city.id}")
    assert r.status_code == 200
    body = r.json()
    assert body["name_original"] == "Kōnstantinoupolis"
    assert body["ethical_notes"] is not None
    assert "Istanbul" in body["ethical_notes"] or "Ottoman" in body["ethical_notes"]
    variants = {v["name"] for v in body["name_variants"]}
    assert "Istanbul" in variants


def test_city_detail_404(client, seeded_cities_and_routes):
    r = client.get("/v1/cities/99999999")
    assert r.status_code == 404


def test_city_types_endpoint(client):
    r = client.get("/v1/cities/types")
    assert r.status_code == 200
    types = {t["type"] for t in r.json()["city_types"]}
    assert {"CAPITAL", "TRADE_HUB", "RELIGIOUS_CENTER", "FORTRESS", "PORT"} <= types


# ─── ROUTES LIST ────────────────────────────────────────────────────────


def test_routes_list_returns_routes(client, seeded_cities_and_routes):
    r = client.get("/v1/routes?limit=100")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 2
    names = {r_["name_original"] for r_ in body["routes"]}
    assert {"Silk Road", "Trans-Atlantic Slave Trade"} <= names


def test_routes_filter_by_type(client, seeded_cities_and_routes):
    r = client.get("/v1/routes?route_type=SEA&limit=50")
    assert r.status_code == 200
    for rt in r.json()["routes"]:
        assert rt["route_type"] == "SEA"


def test_routes_filter_involves_slavery_true(client, seeded_cities_and_routes):
    """ETHICS-010: filtro esplicito delle rotte schiaviste."""
    r = client.get("/v1/routes?involves_slavery=true&limit=50")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    for rt in body["routes"]:
        assert rt["involves_slavery"] is True
        assert "humans_enslaved" in rt["commodities"]


def test_routes_filter_involves_slavery_false(client, seeded_cities_and_routes):
    """Solo non-schiaviste quando involves_slavery=false."""
    r = client.get("/v1/routes?involves_slavery=false&limit=50")
    assert r.status_code == 200
    for rt in r.json()["routes"]:
        assert rt["involves_slavery"] is False


def test_routes_filter_by_year(client, seeded_cities_and_routes):
    # 1700: Trans-Atlantic active (1500-1866); Silk Road declined (-130 to 1453).
    r = client.get("/v1/routes?year=1700&limit=50")
    assert r.status_code == 200
    names = {rt["name_original"] for rt in r.json()["routes"]}
    assert "Trans-Atlantic Slave Trade" in names
    assert "Silk Road" not in names


# ─── ROUTES DETAIL ──────────────────────────────────────────────────────


def test_route_detail_includes_geometry_and_waypoints(
    client, db, seeded_cities_and_routes
):
    r_id = db.query(TradeRoute).filter_by(name_original="Silk Road").first().id
    resp = client.get(f"/v1/routes/{r_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["geometry"]["type"] == "LineString"
    assert len(body["geometry"]["coordinates"]) > 0
    waypoint_cities = {w["city_name"] for w in body["waypoints"]}
    assert "Kōnstantinoupolis" in waypoint_cities
    assert "Samarqand" in waypoint_cities


def test_route_detail_slave_trade_ethics(client, db, seeded_cities_and_routes):
    """ETHICS-010: la Trans-Atlantic route DEVE avere ethical_notes sostanziose."""
    r_id = (
        db.query(TradeRoute)
        .filter_by(name_original="Trans-Atlantic Slave Trade")
        .first().id
    )
    resp = client.get(f"/v1/routes/{r_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["involves_slavery"] is True
    assert "humans_enslaved" in body["commodities"]
    notes = body["ethical_notes"] or ""
    # Scala menzionata esplicitamente (milioni)
    assert "million" in notes.lower() or "12.5" in notes
    # Middle Passage mortality menzionata
    assert "Middle Passage" in notes or "middle passage" in notes.lower()


def test_route_detail_404(client, seeded_cities_and_routes):
    r = client.get("/v1/routes/99999999")
    assert r.status_code == 404


def test_route_types_endpoint(client):
    r = client.get("/v1/routes/types")
    assert r.status_code == 200
    types = {t["type"] for t in r.json()["route_types"]}
    assert {"LAND", "SEA", "RIVER", "CARAVAN", "MIXED"} == types


# ─── OPENAPI ────────────────────────────────────────────────────────────


def test_cities_and_routes_in_openapi(client):
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    assert "/v1/cities" in paths
    assert "/v1/cities/{city_id}" in paths
    assert "/v1/cities/types" in paths
    assert "/v1/routes" in paths
    assert "/v1/routes/{route_id}" in paths
    assert "/v1/routes/types" in paths
    # Check critical query params documented.
    city_list_params = {p["name"] for p in paths["/v1/cities"]["get"]["parameters"]}
    assert "bbox" in city_list_params
    assert "year" in city_list_params
    assert "city_type" in city_list_params
    route_list_params = {p["name"] for p in paths["/v1/routes"]["get"]["parameters"]}
    assert "involves_slavery" in route_list_params
    assert "year" in route_list_params
