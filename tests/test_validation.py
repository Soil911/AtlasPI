"""Test edge cases e validazione input."""


class TestInputValidation:
    def test_year_too_low(self, client):
        r = client.get("/v1/entity?year=-5000")
        assert r.status_code == 422

    def test_year_too_high(self, client):
        r = client.get("/v1/entity?year=3000")
        assert r.status_code == 422

    def test_name_too_long(self, client):
        r = client.get(f"/v1/entity?name={'x' * 201}")
        assert r.status_code == 422

    def test_invalid_status(self, client):
        r = client.get("/v1/entity?status=invalid")
        assert r.status_code == 422

    def test_limit_too_high(self, client):
        r = client.get("/v1/entities?limit=500")
        assert r.status_code == 422

    def test_negative_offset(self, client):
        r = client.get("/v1/entities?offset=-1")
        assert r.status_code == 422


class TestEdgeCases:
    def test_negative_year_query(self, client):
        """Anno negativo (a.C.) deve funzionare."""
        r = client.get("/v1/entity?year=-400")
        assert r.status_code == 200

    def test_empty_results(self, client):
        r = client.get("/v1/entity?name=INESISTENTE_ZZZZZ")
        assert r.status_code == 200
        assert r.json()["count"] == 0
        assert r.json()["entities"] == []

    def test_unicode_search(self, client):
        """Ricerca con caratteri Unicode deve funzionare."""
        r = client.get("/v1/entity?name=\u0130stanbul")
        assert r.status_code == 200

    def test_arabic_search(self, client):
        r = client.get("/v1/entity?name=\u0641\u0644\u0633\u0637\u064a\u0646")
        assert r.status_code == 200

    def test_pagination_beyond_results(self, client):
        r = client.get("/v1/entities?offset=9999")
        assert r.status_code == 200
        assert r.json()["entities"] == []

    def test_year_boundary_negative(self, client):
        """Anno -657 (fondazione di Bisanzio) deve trovare Istanbul."""
        r = client.get("/v1/entity?year=-657&limit=100")
        assert r.status_code == 200
        names = [e["name_original"] for e in r.json()["entities"]]
        assert "\u0130stanbul" in names
