"""Agent-UX v6.99.109: zero-result hint, boundary_reference_year, event summary.

# Origine: audit agent-consumer 2026-07-02 — tre attriti reali per gli agenti:
# (1) zero-result senza retry-path → l'agente abbandona invece di provare fuzzy;
# (2) boundary statico silenziosamente anacronistico → serve flag machine-readable;
# (3) on-this-day/liste eventi senza descrizione → N+1 fetch di detail.
"""


class TestZeroResultHint:
    def test_v1_entity_zero_result_has_hint(self, client):
        r = client.get("/v1/entity", params={"name": "Xyzzy Nonexistent Empire"})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0
        assert data["hint"] and "/v1/search/fuzzy" in data["hint"]

    def test_v1_entity_with_results_has_no_hint(self, client):
        r = client.get("/v1/entity", params={"name": "Kush"})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] > 0
        assert data.get("hint") is None

    def test_v1_entities_zero_result_has_hint(self, client):
        r = client.get("/v1/entities", params={"search": "Xyzzy Nonexistent"})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0
        assert data["hint"] and "/v1/search/fuzzy" in data["hint"]

    def test_v1_search_zero_result_has_hint(self, client):
        r = client.get("/v1/search", params={"q": "XyzzyNonexistent"})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0
        assert data["hint"] and "/v1/search/fuzzy" in data["hint"]

    def test_hint_urlencodes_query(self, client):
        r = client.get("/v1/search", params={"q": "does not exist ürk"})
        assert r.status_code == 200
        hint = r.json()["hint"]
        assert " ürk" not in hint  # spazio e non-ASCII devono essere percent-encoded
        assert "does%20not%20exist" in hint


class TestBoundaryReferenceYear:
    def test_field_present_in_entity_detail(self, client):
        r = client.get("/v1/entities/1", params={"exclude_geometry": "true"})
        assert r.status_code == 200
        assert "boundary_reference_year" in r.json()

    def test_matches_aourednik_year_when_present(self, client, db):
        from src.db.models import GeoEntity

        ent = (
            db.query(GeoEntity)
            .filter(GeoEntity.boundary_aourednik_year.isnot(None))
            .first()
        )
        if ent is None:
            import pytest

            pytest.skip("nessuna entità aourednik nel seed di test")
        r = client.get(f"/v1/entities/{ent.id}", params={"exclude_geometry": "true"})
        assert r.json()["boundary_reference_year"] == ent.boundary_aourednik_year


class TestEventSummaryDescription:
    def test_on_this_day_includes_description_short(self, client):
        r = client.get("/v1/events/date-coverage")
        assert r.status_code == 200
        covered = r.json().get("covered_dates") or []
        if not covered:
            import pytest

            pytest.skip("nessuna data coperta nel seed di test")
        mm_dd = covered[0] if isinstance(covered[0], str) else covered[0].get("date")
        r2 = client.get(f"/v1/events/on-this-day/{mm_dd}")
        assert r2.status_code == 200
        events = r2.json()["events"]
        assert events, "data coperta senza eventi?"
        ev = events[0]
        assert "description_short" in ev
        if ev["description_short"]:
            assert len(ev["description_short"]) <= 280
