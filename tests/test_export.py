"""Test per gli endpoint di esportazione."""

import json


class TestGeoJsonExport:
    def test_returns_feature_collection(self, client):
        r = client.get("/v1/export/geojson")
        assert r.status_code == 200
        d = json.loads(r.content)
        assert d["type"] == "FeatureCollection"
        assert len(d["features"]) >= 35

    def test_has_correct_content_type(self, client):
        r = client.get("/v1/export/geojson")
        assert "geo+json" in r.headers["content-type"]

    def test_filter_by_year(self, client):
        r = client.get("/v1/export/geojson?year=1500")
        d = json.loads(r.content)
        for feat in d["features"]:
            assert feat["properties"]["year_start"] <= 1500

    def test_features_have_properties(self, client):
        r = client.get("/v1/export/geojson")
        d = json.loads(r.content)
        feat = d["features"][0]
        assert "name_original" in feat["properties"]
        assert "confidence_score" in feat["properties"]
        assert "status" in feat["properties"]


class TestCsvExport:
    def test_returns_csv(self, client):
        r = client.get("/v1/export/csv")
        assert r.status_code == 200
        assert "text/csv" in r.headers["content-type"]

    def test_has_header_row(self, client):
        r = client.get("/v1/export/csv")
        lines = r.content.decode("utf-8").strip().split("\\n")
        assert "name_original" in lines[0]


class TestTimeline:
    def test_returns_timeline(self, client):
        r = client.get("/v1/export/timeline")
        assert r.status_code == 200
        d = r.json()
        assert d["count"] >= 35
        assert d["min_year"] < 0
        assert "items" in d

    def test_items_have_required_fields(self, client):
        r = client.get("/v1/export/timeline")
        item = r.json()["items"][0]
        for field in ["id", "name", "type", "start", "status", "confidence"]:
            assert field in item
