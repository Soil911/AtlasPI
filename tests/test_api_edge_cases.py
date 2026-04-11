"""Test edge cases aggiuntivi per v5.4."""


class TestSearchEdgeCases:
    def test_search_with_special_chars(self, client):
        r = client.get("/v1/search?q=%C3%87a%C4%9F")  # encoded chars
        assert r.status_code == 200

    def test_search_with_spaces(self, client):
        r = client.get("/v1/search?q=Impero Romano")
        assert r.status_code == 200

    def test_search_single_char(self, client):
        r = client.get("/v1/search?q=A")
        assert r.status_code == 200
        assert r.json()["count"] >= 1

    def test_search_max_results(self, client):
        r = client.get("/v1/search?q=a&limit=50")
        assert r.status_code == 200
        assert r.json()["count"] <= 50


class TestPaginationEdgeCases:
    def test_offset_equals_total(self, client):
        total = client.get("/v1/entities?limit=1").json()["count"]
        r = client.get(f"/v1/entities?offset={total}&limit=10")
        assert r.status_code == 200
        assert len(r.json()["entities"]) == 0

    def test_limit_1(self, client):
        r = client.get("/v1/entities?limit=1")
        assert r.status_code == 200
        assert len(r.json()["entities"]) == 1

    def test_page_consistency(self, client):
        """Pagine successive non devono avere overlap."""
        page1 = client.get("/v1/entities?limit=5&offset=0").json()["entities"]
        page2 = client.get("/v1/entities?limit=5&offset=5").json()["entities"]
        ids1 = {e["id"] for e in page1}
        ids2 = {e["id"] for e in page2}
        assert ids1.isdisjoint(ids2), "Le pagine hanno entita' duplicate"


class TestSortingEdgeCases:
    def test_sort_with_type_filter(self, client):
        r = client.get("/v1/entity?type=empire&sort=year_start&order=asc&limit=50")
        assert r.status_code == 200
        years = [e["year_start"] for e in r.json()["entities"]]
        assert years == sorted(years)

    def test_sort_desc(self, client):
        r = client.get("/v1/entities?sort=confidence&order=desc&limit=5")
        scores = [e["confidence_score"] for e in r.json()["entities"]]
        assert scores == sorted(scores, reverse=True)

    def test_sort_by_year_end(self, client):
        r = client.get("/v1/entities?sort=year_end&order=asc&limit=50")
        assert r.status_code == 200


class TestExportEdgeCases:
    def test_geojson_with_year_filter(self, client):
        r = client.get("/v1/export/geojson?year=1500")
        assert r.status_code == 200
        d = r.json()
        for f in d["features"]:
            assert f["properties"]["year_start"] <= 1500

    def test_csv_has_all_columns(self, client):
        r = client.get("/v1/export/csv")
        lines = r.text.strip().split('\n')
        header = lines[0]
        required = ["id", "name_original", "entity_type", "year_start", "status", "confidence_score"]
        for col in required:
            assert col in header

    def test_timeline_sorted(self, client):
        r = client.get("/v1/export/timeline")
        d = r.json()
        assert d["min_year"] <= d["max_year"]
        assert d["count"] >= 50


class TestPerformanceV5:
    def test_compare_under_500ms(self, client):
        import time
        ids = [e["id"] for e in client.get("/v1/entities?limit=2").json()["entities"]]
        start = time.time()
        client.get(f"/v1/compare/{ids[0]}/{ids[1]}")
        assert time.time() - start < 0.5

    def test_random_under_200ms(self, client):
        import time
        start = time.time()
        client.get("/v1/random")
        assert time.time() - start < 0.2

    def test_continents_under_200ms(self, client):
        import time
        start = time.time()
        client.get("/v1/continents")
        assert time.time() - start < 0.2
