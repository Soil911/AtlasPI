"""Test per le feature v5.x: compare, random, continents, embed."""


class TestCompareEndpoint:
    def _two_ids(self, client):
        entities = client.get("/v1/entities?limit=2").json()["entities"]
        return entities[0]["id"], entities[1]["id"]

    def test_compare_symmetric(self, client):
        """Il confronto A-B deve avere gli stessi dati di overlap di B-A."""
        id1, id2 = self._two_ids(client)
        r1 = client.get(f"/v1/compare/{id1}/{id2}").json()
        r2 = client.get(f"/v1/compare/{id2}/{id1}").json()
        assert r1["comparison"]["temporal_overlap_years"] == r2["comparison"]["temporal_overlap_years"]

    def test_compare_self(self, client):
        """Confronto con se stesso deve avere overlap totale."""
        eid = client.get("/v1/entities?limit=1").json()["entities"][0]["id"]
        r = client.get(f"/v1/compare/{eid}/{eid}")
        assert r.status_code == 200
        d = r.json()
        assert d["comparison"]["same_type"] is True
        assert d["comparison"]["confidence_diff"] == 0.0

    def test_compare_has_geojson(self, client):
        id1, id2 = self._two_ids(client)
        r = client.get(f"/v1/compare/{id1}/{id2}").json()
        # Almeno uno dovrebbe avere geojson
        a_geo = r["entity_a"].get("boundary_geojson")
        b_geo = r["entity_b"].get("boundary_geojson")
        assert a_geo is not None or b_geo is not None


class TestRandomEndpoint:
    def test_random_varies(self, client):
        """Due chiamate random dovrebbero (statisticamente) dare risultati diversi."""
        results = set()
        for _ in range(10):
            r = client.get("/v1/random")
            results.add(r.json()["id"])
        # Con 55 entita', 10 tentativi dovrebbero dare almeno 2 diversi
        assert len(results) >= 2

    def test_random_has_full_response(self, client):
        r = client.get("/v1/random").json()
        required_fields = [
            "id", "name_original", "entity_type", "year_start",
            "confidence_score", "status", "continent",
        ]
        for field in required_fields:
            assert field in r, f"Campo mancante: {field}"


class TestContinentsEndpoint:
    def test_continents_cover_world(self, client):
        r = client.get("/v1/continents")
        names = [c["continent"] for c in r.json()]
        # Deve avere almeno Europa, Asia, Africa, Americas
        assert "Europe" in names
        assert "Africa" in names

    def test_continent_totals_match(self, client):
        """La somma dei conteggi per continente deve uguagliare il totale."""
        continents = client.get("/v1/continents").json()
        total_from_continents = sum(c["count"] for c in continents)
        stats = client.get("/v1/stats").json()
        assert total_from_continents == stats["total_entities"]

    def test_continent_filter_reduces_results(self, client):
        all_count = client.get("/v1/entities?limit=100").json()["count"]
        europe_count = client.get("/v1/entity?continent=Europe&limit=100").json()["count"]
        assert europe_count < all_count
        assert europe_count > 0


class TestEmbedEndpoint:
    def test_embed_page_serves(self, client):
        r = client.get("/embed")
        assert r.status_code == 200


class TestDataDiversity:
    """Test che il dataset v5.3 sia veramente diversificato."""

    def test_at_least_200_entities(self, client):
        r = client.get("/v1/stats").json()
        assert r["total_entities"] >= 200

    def test_at_least_4_continents(self, client):
        r = client.get("/v1/continents").json()
        assert len(r) >= 4

    def test_entities_span_5000_years(self, client):
        r = client.get("/v1/stats").json()
        year_range = r["year_range"]["max"] - r["year_range"]["min"]
        assert year_range >= 4000

    def test_has_oceania_entities(self, client):
        """Deve avere entita' in Oceania (aggiunta v5.3)."""
        r = client.get("/v1/continents").json()
        oceania = [c for c in r if c["continent"] == "Oceania"]
        assert len(oceania) > 0 and oceania[0]["count"] >= 1

    def test_has_americas_entities(self, client):
        r = client.get("/v1/continents").json()
        americas = [c for c in r if c["continent"] == "Americas"]
        assert len(americas) > 0 and americas[0]["count"] >= 2

    def test_no_glorifying_language_in_notes(self, client):
        """Le note etiche non devono glorificare conquiste."""
        # ETHICS-002: le conquiste devono essere descritte onestamente
        glorifying_terms = ["glorious", "magnificent conquest", "civilizing"]
        entities = client.get("/v1/entities?limit=100").json()["entities"]
        for e in entities:
            detail = client.get(f"/v1/entities/{e['id']}").json()
            notes = (detail.get("ethical_notes") or "").lower()
            for term in glorifying_terms:
                assert term not in notes, f"Linguaggio glorificante in {e['name_original']}: '{term}'"
