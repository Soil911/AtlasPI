"""Test per le nuove funzionalita' v5.6: nearby, snapshot, autocomplete."""


class TestNearbyEndpoint:
    """Test per /v1/nearby — ricerca per prossimita' geografica."""

    def test_nearby_finds_rome(self, client):
        """Cercando vicino a Roma si trova l'Impero Romano."""
        r = client.get("/v1/nearby?lat=41.9&lon=12.5&year=100&limit=5")
        assert r.status_code == 200
        d = r.json()
        assert d["count"] >= 1
        names = [e["name_original"] for e in d["entities"]]
        assert any("Roman" in n or "Romanum" in n for n in names)

    def test_nearby_returns_distance(self, client):
        """Ogni risultato include distanza in km."""
        r = client.get("/v1/nearby?lat=41.9&lon=12.5&radius=2000&limit=5")
        assert r.status_code == 200
        for e in r.json()["entities"]:
            assert "distance_km" in e
            assert isinstance(e["distance_km"], (int, float))
            assert e["distance_km"] >= 0

    def test_nearby_respects_radius(self, client):
        """Con raggio piccolo, meno risultati."""
        r_small = client.get("/v1/nearby?lat=41.9&lon=12.5&radius=10&limit=50")
        r_big = client.get("/v1/nearby?lat=41.9&lon=12.5&radius=2000&limit=50")
        assert r_small.json()["count"] <= r_big.json()["count"]

    def test_nearby_respects_year_filter(self, client):
        """Filtrando per anno esclude entita' non attive."""
        r = client.get("/v1/nearby?lat=41.9&lon=12.5&year=2024&radius=500&limit=20")
        assert r.status_code == 200
        for e in r.json()["entities"]:
            assert e["year_start"] <= 2024

    def test_nearby_sorted_by_distance(self, client):
        """I risultati sono ordinati per distanza crescente."""
        r = client.get("/v1/nearby?lat=30.0&lon=31.0&radius=3000&limit=20")
        assert r.status_code == 200
        distances = [e["distance_km"] for e in r.json()["entities"]]
        assert distances == sorted(distances)

    def test_nearby_invalid_coordinates(self, client):
        """Coordinate fuori range danno errore 422."""
        r = client.get("/v1/nearby?lat=100&lon=12.5")
        assert r.status_code == 422

    def test_nearby_includes_continent(self, client):
        """Ogni risultato include il continente."""
        r = client.get("/v1/nearby?lat=35.0&lon=139.0&radius=2000&limit=5")
        assert r.status_code == 200
        for e in r.json()["entities"]:
            assert "continent" in e

    def test_nearby_query_echoed(self, client):
        """La risposta include i parametri di query."""
        r = client.get("/v1/nearby?lat=41.9&lon=12.5&radius=100&year=500")
        d = r.json()
        assert d["query"]["lat"] == 41.9
        assert d["query"]["lon"] == 12.5
        assert d["query"]["radius_km"] == 100.0
        assert d["query"]["year"] == 500


class TestSnapshotEndpoint:
    """Test per /v1/snapshot/{year} — stato del mondo in un anno."""

    def test_snapshot_returns_entities(self, client):
        """Snapshot per un anno storico restituisce entita'."""
        r = client.get("/v1/snapshot/1500")
        assert r.status_code == 200
        d = r.json()
        assert d["year"] == 1500
        assert d["count"] >= 50
        assert len(d["entities"]) == d["count"]

    def test_snapshot_summary(self, client):
        """La risposta include sommario per tipo, continente, status."""
        r = client.get("/v1/snapshot/1500")
        d = r.json()
        assert "summary" in d
        assert "types" in d["summary"]
        assert "continents" in d["summary"]
        assert "statuses" in d["summary"]

    def test_snapshot_entities_active_in_year(self, client):
        """Tutte le entita' erano attive nell'anno richiesto."""
        r = client.get("/v1/snapshot/500")
        for e in r.json()["entities"]:
            assert e["year_start"] <= 500
            if e["year_end"] is not None:
                assert e["year_end"] >= 500

    def test_snapshot_ancient_year(self, client):
        """Snapshot per anno antico funziona."""
        r = client.get("/v1/snapshot/-3000")
        assert r.status_code == 200
        d = r.json()
        assert d["year"] == -3000
        assert d["count"] >= 1

    def test_snapshot_modern(self, client):
        """Snapshot per anno moderno restituisce molte entita'."""
        r = client.get("/v1/snapshot/2020")
        assert r.status_code == 200
        assert r.json()["count"] >= 10

    def test_snapshot_filter_by_type(self, client):
        """Si puo' filtrare per tipo."""
        r = client.get("/v1/snapshot/1500?type=empire")
        assert r.status_code == 200
        for e in r.json()["entities"]:
            assert e["entity_type"] == "empire"

    def test_snapshot_filter_by_continent(self, client):
        """Si puo' filtrare per continente."""
        r = client.get("/v1/snapshot/1500?continent=Europe")
        assert r.status_code == 200
        for e in r.json()["entities"]:
            assert e["continent"] == "Europe"

    def test_snapshot_invalid_year(self, client):
        """Anno fuori range restituisce errore."""
        r = client.get("/v1/snapshot/-5000")
        assert r.status_code == 400

    def test_snapshot_empty_year(self, client):
        """Anno molto antico puo' avere zero risultati."""
        r = client.get("/v1/snapshot/-4499")
        assert r.status_code == 200
        # potrebbe avere 0 o pochi risultati


class TestSearchAutocomplete:
    """Test per /v1/search — usato dall'autocomplete frontend."""

    def test_search_returns_results(self, client):
        """La ricerca base trova risultati."""
        r = client.get("/v1/search?q=Roman")
        assert r.status_code == 200
        d = r.json()
        assert d["count"] >= 1

    def test_search_by_variant(self, client):
        """La ricerca trova varianti di nome."""
        r = client.get("/v1/search?q=Ottoman")
        assert r.status_code == 200
        assert r.json()["count"] >= 1

    def test_search_limit(self, client):
        """Il parametro limit viene rispettato."""
        r = client.get("/v1/search?q=empire&limit=3")
        assert r.status_code == 200
        assert len(r.json()["results"]) <= 3

    def test_search_returns_lightweight(self, client):
        """I risultati non includono GeoJSON (leggeri)."""
        r = client.get("/v1/search?q=Roman")
        for res in r.json()["results"]:
            assert "boundary_geojson" not in res
            assert "id" in res
            assert "name_original" in res
            assert "entity_type" in res

    def test_search_unicode(self, client):
        """La ricerca funziona con caratteri Unicode."""
        r = client.get("/v1/search?q=%CE%91%CE%B8")  # Αθ (Athen)
        assert r.status_code == 200

    def test_search_empty_query(self, client):
        """Query vuota restituisce errore."""
        r = client.get("/v1/search?q=")
        assert r.status_code == 422
