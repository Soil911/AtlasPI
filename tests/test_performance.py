"""Test di performance — tempi di risposta."""

import time


class TestResponseTimes:
    def test_health_under_100ms(self, client):
        start = time.perf_counter()
        r = client.get("/health")
        elapsed = (time.perf_counter() - start) * 1000
        assert r.status_code == 200
        assert elapsed < 100, f"Health check troppo lento: {elapsed:.0f}ms"

    def test_entity_list_under_300ms(self, client):
        start = time.perf_counter()
        r = client.get("/v1/entities?limit=20")
        elapsed = (time.perf_counter() - start) * 1000
        assert r.status_code == 200
        assert elapsed < 300, f"Entity list troppo lento: {elapsed:.0f}ms"

    def test_entity_detail_under_200ms(self, client):
        eid = client.get("/v1/entities?limit=1").json()["entities"][0]["id"]
        start = time.perf_counter()
        r = client.get(f"/v1/entities/{eid}")
        elapsed = (time.perf_counter() - start) * 1000
        assert r.status_code == 200
        assert elapsed < 200, f"Entity detail troppo lento: {elapsed:.0f}ms"

    def test_search_under_300ms(self, client):
        start = time.perf_counter()
        r = client.get("/v1/search?q=empire")
        elapsed = (time.perf_counter() - start) * 1000
        assert r.status_code == 200
        assert elapsed < 300, f"Search troppo lento: {elapsed:.0f}ms"

    def test_stats_under_200ms(self, client):
        start = time.perf_counter()
        r = client.get("/v1/stats")
        elapsed = (time.perf_counter() - start) * 1000
        assert r.status_code == 200
        assert elapsed < 200, f"Stats troppo lento: {elapsed:.0f}ms"

    def test_geojson_export_under_500ms(self, client):
        start = time.perf_counter()
        r = client.get("/v1/export/geojson")
        elapsed = (time.perf_counter() - start) * 1000
        assert r.status_code == 200
        assert elapsed < 500, f"GeoJSON export troppo lento: {elapsed:.0f}ms"

    def test_contemporaries_under_300ms(self, client):
        eid = client.get("/v1/entities?limit=1").json()["entities"][0]["id"]
        start = time.perf_counter()
        r = client.get(f"/v1/entities/{eid}/contemporaries")
        elapsed = (time.perf_counter() - start) * 1000
        assert r.status_code == 200
        assert elapsed < 300, f"Contemporaries troppo lento: {elapsed:.0f}ms"
