"""Test per gli endpoint delle entit\u00e0."""


class TestListEntities:
    def test_returns_entities(self, client):
        r = client.get("/v1/entities")
        assert r.status_code == 200
        d = r.json()
        assert d["count"] >= 50
        assert len(d["entities"]) <= d["limit"]

    def test_pagination_default(self, client):
        r = client.get("/v1/entities")
        d = r.json()
        assert d["limit"] == 20
        assert d["offset"] == 0

    def test_pagination_custom(self, client):
        r = client.get("/v1/entities?limit=3&offset=0")
        d = r.json()
        assert len(d["entities"]) == 3
        assert d["limit"] == 3

    def test_pagination_offset(self, client):
        r1 = client.get("/v1/entities?limit=5&offset=0")
        r2 = client.get("/v1/entities?limit=5&offset=5")
        ids1 = {e["id"] for e in r1.json()["entities"]}
        ids2 = {e["id"] for e in r2.json()["entities"]}
        assert ids1.isdisjoint(ids2)

    def test_has_cache_header(self, client):
        r = client.get("/v1/entities")
        assert "cache-control" in r.headers


class TestGetEntity:
    def _first_id(self, client):
        """Ottiene il primo ID disponibile."""
        r = client.get("/v1/entities?limit=1")
        return r.json()["entities"][0]["id"]

    def test_by_id(self, client):
        eid = self._first_id(client)
        r = client.get(f"/v1/entities/{eid}")
        assert r.status_code == 200
        assert r.json()["id"] == eid

    def test_not_found(self, client):
        r = client.get("/v1/entities/99999")
        assert r.status_code == 404
        d = r.json()
        assert d["error"] is True

    def test_has_all_fields(self, client):
        eid = self._first_id(client)
        r = client.get(f"/v1/entities/{eid}")
        e = r.json()
        required = ["name_original", "name_original_lang", "confidence_score",
                     "status", "name_variants", "sources", "territory_changes",
                     "entity_type", "year_start"]
        for field in required:
            assert field in e, f"Campo mancante: {field}"


class TestQueryEntity:
    def test_by_name(self, client):
        r = client.get("/v1/entity?name=Imperium")
        assert r.status_code == 200
        assert r.json()["count"] >= 1

    def test_by_name_variant(self, client):
        """Cercare per variante (es. 'Ottoman') deve trovare l'entit\u00e0."""
        r = client.get("/v1/entity?name=Ottoman")
        assert r.json()["count"] >= 1

    def test_by_year(self, client):
        r = client.get("/v1/entity?year=100")
        d = r.json()
        for e in d["entities"]:
            assert e["year_start"] <= 100

    def test_by_status(self, client):
        r = client.get("/v1/entity?status=disputed")
        d = r.json()
        for e in d["entities"]:
            assert e["status"] == "disputed"

    def test_combined_filters(self, client):
        r = client.get("/v1/entity?year=2020&status=disputed")
        d = r.json()
        assert d["count"] >= 1
        for e in d["entities"]:
            assert e["status"] == "disputed"
            assert e["year_start"] <= 2020
