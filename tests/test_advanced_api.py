"""Test per le funzionalita' API avanzate v2.2."""


class TestSorting:
    def test_sort_by_name(self, client):
        r = client.get("/v1/entities?sort=name&order=asc&limit=5")
        assert r.status_code == 200
        names = [e["name_original"] for e in r.json()["entities"]]
        assert names == sorted(names)

    def test_sort_by_confidence_desc(self, client):
        r = client.get("/v1/entities?sort=confidence&order=desc&limit=5")
        assert r.status_code == 200
        scores = [e["confidence_score"] for e in r.json()["entities"]]
        assert scores == sorted(scores, reverse=True)

    def test_sort_by_year(self, client):
        r = client.get("/v1/entities?sort=year_start&order=asc&limit=5")
        assert r.status_code == 200
        years = [e["year_start"] for e in r.json()["entities"]]
        assert years == sorted(years)


class TestTypeFilter:
    def test_filter_by_empire(self, client):
        r = client.get("/v1/entity?type=empire")
        assert r.status_code == 200
        for e in r.json()["entities"]:
            assert e["entity_type"] == "empire"

    def test_filter_by_disputed_territory(self, client):
        r = client.get("/v1/entity?type=disputed_territory")
        assert r.status_code == 200
        assert r.json()["count"] >= 2

    def test_combined_type_and_year(self, client):
        r = client.get("/v1/entity?type=empire&year=1500")
        assert r.status_code == 200
        for e in r.json()["entities"]:
            assert e["entity_type"] == "empire"
            assert e["year_start"] <= 1500


class TestSearch:
    def test_search_basic(self, client):
        r = client.get("/v1/search?q=Roma")
        assert r.status_code == 200
        assert r.json()["count"] >= 1

    def test_search_returns_light_results(self, client):
        r = client.get("/v1/search?q=Ottoman")
        d = r.json()
        assert d["count"] >= 1
        # Verifica che NON ci sia boundary_geojson (risultati leggeri)
        result = d["results"][0]
        assert "boundary_geojson" not in result
        assert "name_original" in result

    def test_search_min_length(self, client):
        r = client.get("/v1/search?q=")
        assert r.status_code == 422


class TestTypes:
    def test_list_types(self, client):
        r = client.get("/v1/types")
        assert r.status_code == 200
        types = r.json()
        assert len(types) >= 3
        assert all("type" in t and "count" in t for t in types)

    def test_empire_is_most_common(self, client):
        r = client.get("/v1/types")
        types = r.json()
        # L'empire dovrebbe essere il tipo piu' comune
        assert types[0]["type"] == "empire"


class TestContinents:
    def test_list_continents(self, client):
        r = client.get("/v1/continents")
        assert r.status_code == 200
        continents = r.json()
        assert len(continents) >= 3
        assert all("continent" in c and "count" in c for c in continents)

    def test_has_multiple_regions(self, client):
        r = client.get("/v1/continents")
        names = [c["continent"] for c in r.json()]
        assert "Europe" in names
        assert "Asia" in names or "Middle East" in names

    def test_continent_filter(self, client):
        r = client.get("/v1/entity?continent=Europe")
        assert r.status_code == 200
        for e in r.json()["entities"]:
            assert e.get("continent") == "Europe"

    def test_entity_has_continent(self, client):
        r = client.get("/v1/entities?limit=1")
        e = r.json()["entities"][0]
        assert "continent" in e
        assert e["continent"] is not None


class TestStats:
    def test_stats_response(self, client):
        r = client.get("/v1/stats")
        assert r.status_code == 200
        d = r.json()
        assert d["total_entities"] >= 35
        assert d["disputed_count"] >= 5
        assert d["total_sources"] > 0
        assert d["total_territory_changes"] > 0
        assert 0.0 < d["avg_confidence"] < 1.0
        assert d["year_range"]["min"] < 0  # abbiamo entita' a.C.

    def test_stats_has_continents(self, client):
        r = client.get("/v1/stats")
        d = r.json()
        assert "continents" in d
        assert len(d["continents"]) >= 3
