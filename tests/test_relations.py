"""Test per endpoint relazioni tra entità."""


class TestContemporaries:
    def _first_id(self, client):
        return client.get("/v1/entities?limit=1").json()["entities"][0]["id"]

    def test_returns_contemporaries(self, client):
        eid = self._first_id(client)
        r = client.get(f"/v1/entities/{eid}/contemporaries")
        assert r.status_code == 200
        d = r.json()
        assert d["entity_id"] == eid
        assert d["count"] > 0
        assert len(d["contemporaries"]) > 0

    def test_contemporaries_have_overlap(self, client):
        eid = self._first_id(client)
        r = client.get(f"/v1/entities/{eid}/contemporaries")
        for c in r.json()["contemporaries"]:
            assert "overlap_start" in c
            assert "overlap_end" in c

    def test_not_found(self, client):
        r = client.get("/v1/entities/99999/contemporaries")
        assert r.status_code == 404


class TestRelated:
    def _first_id(self, client):
        return client.get("/v1/entities?limit=1").json()["entities"][0]["id"]

    def test_returns_related(self, client):
        eid = self._first_id(client)
        r = client.get(f"/v1/entities/{eid}/related")
        assert r.status_code == 200
        d = r.json()
        assert "same_type" in d
        assert "temporal_overlap" in d

    def test_not_found(self, client):
        r = client.get("/v1/entities/99999/related")
        assert r.status_code == 404


class TestCompare:
    def _two_ids(self, client):
        entities = client.get("/v1/entities?limit=2").json()["entities"]
        return entities[0]["id"], entities[1]["id"]

    def test_compare_returns_both_entities(self, client):
        id1, id2 = self._two_ids(client)
        r = client.get(f"/v1/compare/{id1}/{id2}")
        assert r.status_code == 200
        d = r.json()
        assert d["entity_a"]["id"] == id1
        assert d["entity_b"]["id"] == id2
        assert "comparison" in d

    def test_compare_has_overlap(self, client):
        id1, id2 = self._two_ids(client)
        r = client.get(f"/v1/compare/{id1}/{id2}")
        d = r.json()
        cmp = d["comparison"]
        assert "temporal_overlap_years" in cmp
        assert "same_type" in cmp
        assert "confidence_diff" in cmp

    def test_compare_has_duration(self, client):
        id1, id2 = self._two_ids(client)
        r = client.get(f"/v1/compare/{id1}/{id2}")
        d = r.json()
        assert d["entity_a"]["duration_years"] > 0
        assert d["entity_b"]["duration_years"] > 0

    def test_compare_not_found(self, client):
        r = client.get("/v1/compare/99999/99998")
        assert r.status_code == 404
