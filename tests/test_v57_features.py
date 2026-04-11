"""Test per le nuove funzionalita' v5.7: evolution, capital markers, API improvements."""


class TestEvolutionEndpoint:
    """Test per /v1/entities/{id}/evolution — cronologia entita'."""

    def test_evolution_returns_timeline(self, client):
        """L'endpoint restituisce una cronologia."""
        r = client.get("/v1/entities/1/evolution")
        assert r.status_code == 200
        d = r.json()
        assert "timeline" in d
        assert "duration_years" in d
        assert "summary" in d

    def test_evolution_sorted_by_year(self, client):
        """I cambiamenti sono ordinati per anno."""
        r = client.get("/v1/entities/1/evolution")
        d = r.json()
        if len(d["timeline"]) >= 2:
            years = [tc["year"] for tc in d["timeline"]]
            assert years == sorted(years)

    def test_evolution_has_summary(self, client):
        """Il sommario contiene espansioni e contrazioni."""
        r = client.get("/v1/entities/1/evolution")
        d = r.json()
        assert "expansion_events" in d["summary"]
        assert "contraction_events" in d["summary"]
        assert "sources_count" in d["summary"]
        assert "name_variants_count" in d["summary"]

    def test_evolution_not_found(self, client):
        """Entita' inesistente da' 404."""
        r = client.get("/v1/entities/99999/evolution")
        assert r.status_code == 404

    def test_evolution_has_entity_info(self, client):
        """La risposta include info base dell'entita'."""
        r = client.get("/v1/entities/1/evolution")
        d = r.json()
        assert "entity_id" in d
        assert "name_original" in d
        assert "entity_type" in d
        assert "year_start" in d

    def test_evolution_timeline_fields(self, client):
        """Ogni evento nella timeline ha i campi richiesti."""
        r = client.get("/v1/entities/1/evolution")
        d = r.json()
        for tc in d["timeline"]:
            assert "year" in tc
            assert "change_type" in tc
            assert "region" in tc
            assert "confidence_score" in tc


class TestCapitalData:
    """Test che le entita' hanno dati sulla capitale per i marker."""

    def test_most_entities_have_capital(self, client):
        """Almeno 95% delle entita' ha coordinate della capitale."""
        r = client.get("/v1/entities?limit=100&offset=0")
        d = r.json()
        with_capital = sum(1 for e in d["entities"] if e.get("capital"))
        assert with_capital / len(d["entities"]) >= 0.90

    def test_capital_has_coordinates(self, client):
        """Ogni capitale ha lat e lon."""
        r = client.get("/v1/entities?limit=50")
        d = r.json()
        for e in d["entities"]:
            if e.get("capital"):
                assert "lat" in e["capital"]
                assert "lon" in e["capital"]
                assert -90 <= e["capital"]["lat"] <= 90
                assert -180 <= e["capital"]["lon"] <= 180


class TestDataQualityExpanded:
    """Test di qualita' dei dati con il dataset espanso."""

    def test_at_least_600_entities(self, client):
        """Il dataset contiene almeno 600 entita'."""
        r = client.get("/v1/stats")
        d = r.json()
        assert d["total_entities"] >= 600

    def test_at_least_1800_sources(self, client):
        """Il dataset contiene almeno 1800 fonti."""
        r = client.get("/v1/stats")
        d = r.json()
        assert d["total_sources"] >= 1800

    def test_at_least_6_continents(self, client):
        """Almeno 6 regioni rappresentate."""
        r = client.get("/v1/continents")
        d = r.json()
        assert len(d) >= 5

    def test_types_diversity(self, client):
        """Almeno 10 tipi di entita' diversi."""
        r = client.get("/v1/types")
        d = r.json()
        assert len(d) >= 10

    def test_avg_confidence_reasonable(self, client):
        """Confidence media tra 0.5 e 0.9."""
        r = client.get("/v1/stats")
        d = r.json()
        assert 0.5 <= d["avg_confidence"] <= 0.9

    def test_disputed_entities_exist(self, client):
        """Esistono entita' contestate (ETHICS-003)."""
        r = client.get("/v1/stats")
        d = r.json()
        assert d["disputed_count"] >= 5

    def test_snapshot_1500_has_many_entities(self, client):
        """Il 1500 d.C. ha almeno 50 entita' attive."""
        r = client.get("/v1/snapshot/1500")
        d = r.json()
        assert d["count"] >= 50

    def test_ancient_entities_exist(self, client):
        """Entita' antiche (prima del 1000 a.C.) esistono."""
        r = client.get("/v1/entity?year=-1000&limit=10")
        d = r.json()
        assert d["count"] >= 1

    def test_modern_entities_exist(self, client):
        """Entita' moderne (dopo 2000) esistono."""
        r = client.get("/v1/entity?year=2024&limit=10")
        d = r.json()
        assert d["count"] >= 1


class TestCacheHeaders:
    """Test per i cache headers."""

    def test_entity_has_cache_header(self, client):
        """Le risposte hanno Cache-Control."""
        r = client.get("/v1/entities/1")
        assert "cache-control" in r.headers
        assert "max-age" in r.headers["cache-control"]

    def test_random_has_no_cache(self, client):
        """L'endpoint random non deve essere cachato."""
        r = client.get("/v1/random")
        assert "no-cache" in r.headers.get("cache-control", "")
