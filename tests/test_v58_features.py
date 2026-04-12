"""Test per le nuove funzionalita' v5.8: filtered random, aggregation, data expansion."""


class TestFilteredRandom:
    """Test per /v1/random con filtri opzionali."""

    def test_random_no_filters(self, client):
        """Random senza filtri funziona."""
        r = client.get("/v1/random")
        assert r.status_code == 200
        d = r.json()
        assert "id" in d
        assert "name_original" in d

    def test_random_filter_by_type(self, client):
        """Random filtrato per tipo restituisce il tipo corretto."""
        r = client.get("/v1/random?type=empire")
        assert r.status_code == 200
        d = r.json()
        assert d["entity_type"] == "empire"

    def test_random_filter_by_year(self, client):
        """Random filtrato per anno restituisce entita' attiva in quell'anno."""
        r = client.get("/v1/random?year=1500")
        assert r.status_code == 200
        d = r.json()
        assert d["year_start"] <= 1500
        assert d["year_end"] is None or d["year_end"] >= 1500

    def test_random_filter_by_status(self, client):
        """Random filtrato per status restituisce lo status corretto."""
        r = client.get("/v1/random?status=confirmed")
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "confirmed"

    def test_random_filter_combined(self, client):
        """Random con filtri multipli funziona."""
        r = client.get("/v1/random?type=empire&year=1500")
        assert r.status_code == 200
        d = r.json()
        assert d["entity_type"] == "empire"
        assert d["year_start"] <= 1500

    def test_random_no_match_returns_404(self, client):
        """Random con filtri impossibili da' 404."""
        r = client.get("/v1/random?type=nonexistent_type_xyz")
        assert r.status_code == 404

    def test_random_no_cache_header(self, client):
        """Random ha Cache-Control: no-cache."""
        r = client.get("/v1/random")
        assert "no-cache" in r.headers.get("cache-control", "")


class TestAggregation:
    """Test per /v1/aggregation — statistiche aggregate."""

    def test_aggregation_returns_200(self, client):
        """L'endpoint aggregation risponde."""
        r = client.get("/v1/aggregation")
        assert r.status_code == 200

    def test_aggregation_has_all_sections(self, client):
        """La risposta contiene tutte le sezioni."""
        d = client.get("/v1/aggregation").json()
        assert "by_century" in d
        assert "by_type" in d
        assert "by_continent" in d
        assert "by_status" in d
        assert "total" in d
        assert "time_span" in d

    def test_aggregation_total_matches_stats(self, client):
        """Il totale aggregation corrisponde a /v1/stats."""
        agg = client.get("/v1/aggregation").json()
        stats = client.get("/v1/stats").json()
        assert agg["total"] == stats["total_entities"]

    def test_aggregation_by_type_sum_matches_total(self, client):
        """La somma per tipo corrisponde al totale."""
        d = client.get("/v1/aggregation").json()
        type_sum = sum(item["count"] for item in d["by_type"])
        assert type_sum == d["total"]

    def test_aggregation_by_continent_sum_matches_total(self, client):
        """La somma per continente corrisponde al totale."""
        d = client.get("/v1/aggregation").json()
        continent_sum = sum(item["count"] for item in d["by_continent"])
        assert continent_sum == d["total"]

    def test_aggregation_by_status_sum_matches_total(self, client):
        """La somma per status corrisponde al totale."""
        d = client.get("/v1/aggregation").json()
        status_sum = sum(item["count"] for item in d["by_status"])
        assert status_sum == d["total"]

    def test_aggregation_centuries_ordered(self, client):
        """I secoli sono in ordine cronologico (a.C. prima)."""
        d = client.get("/v1/aggregation").json()
        centuries = d["by_century"]
        assert len(centuries) > 0
        # a.C. entries should come before d.C. entries
        bc_indices = [i for i, c in enumerate(centuries) if "a.C." in c["century"]]
        ad_indices = [i for i, c in enumerate(centuries) if "a.C." not in c["century"]]
        if bc_indices and ad_indices:
            assert max(bc_indices) < min(ad_indices)

    def test_aggregation_time_span(self, client):
        """Il time_span ha earliest e latest sensati."""
        d = client.get("/v1/aggregation").json()
        assert d["time_span"]["earliest"] < 0  # almeno un'entita' a.C.
        assert d["time_span"]["latest"] > 1500  # almeno un'entita' moderna

    def test_aggregation_cache_header(self, client):
        """Aggregation ha Cache-Control con max-age."""
        r = client.get("/v1/aggregation")
        assert "max-age" in r.headers.get("cache-control", "")


class TestDataExpansion:
    """Test per l'espansione del dataset v5.8."""

    def test_entity_count_above_650(self, client):
        """Il dataset ha almeno 650 entita'."""
        r = client.get("/v1/stats")
        assert r.json()["total_entities"] >= 650

    def test_multiple_entity_types(self, client):
        """Ci sono almeno 10 tipi di entita'."""
        r = client.get("/v1/types")
        assert len(r.json()) >= 10

    def test_multiple_continents(self, client):
        """Ci sono almeno 5 continenti rappresentati."""
        r = client.get("/v1/continents")
        assert len(r.json()) >= 5

    def test_no_duplicate_names(self, client):
        """Non ci sono nomi duplicati nel dataset."""
        r = client.get("/v1/entities?limit=100&offset=0")
        names = set()
        entities = r.json()["entities"]
        for e in entities:
            assert e["name_original"] not in names, f"Duplicato: {e['name_original']}"
            names.add(e["name_original"])


class TestEvolutionForTimeline:
    """Test che l'evolution endpoint fornisce dati per il canvas timeline."""

    def test_evolution_has_timeline_data(self, client):
        """L'evolution ha dati per la timeline canvas."""
        r = client.get("/v1/entities/1/evolution")
        d = r.json()
        assert "timeline" in d
        assert "year_start" in d
        assert "duration_years" in d

    def test_evolution_changes_have_year(self, client):
        """Ogni cambiamento ha un anno per il posizionamento sul canvas."""
        r = client.get("/v1/entities/1/evolution")
        d = r.json()
        for tc in d["timeline"]:
            assert "year" in tc
            assert isinstance(tc["year"], int)

    def test_evolution_changes_have_type(self, client):
        """Ogni cambiamento ha un tipo per il colore sul canvas."""
        r = client.get("/v1/entities/1/evolution")
        d = r.json()
        for tc in d["timeline"]:
            assert "change_type" in tc
            assert isinstance(tc["change_type"], str)
            assert len(tc["change_type"]) > 0
