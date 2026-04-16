"""Tests for the entity similarity endpoint — v6.24.0.

GET /v1/entities/{id}/similar — finds entities similar to a given one
based on type, temporal overlap, duration, confidence, and status.
"""


class TestSimilarityEndpoint:
    """GET /v1/entities/{id}/similar"""

    def test_returns_200(self, client):
        r = client.get("/v1/entities/1/similar")
        assert r.status_code == 200

    def test_response_structure(self, client):
        r = client.get("/v1/entities/1/similar")
        data = r.json()
        assert "entity_id" in data
        assert "entity_name" in data
        assert "similar" in data
        assert isinstance(data["similar"], list)

    def test_similar_entities_have_required_fields(self, client):
        r = client.get("/v1/entities/1/similar?limit=5")
        data = r.json()
        required_fields = {
            "id", "name_original", "entity_type", "year_start",
            "year_end", "similarity_score",
        }
        for s in data["similar"]:
            for field in required_fields:
                assert field in s, f"Missing field: {field}"

    def test_similarity_scores_sorted_descending(self, client):
        r = client.get("/v1/entities/1/similar?limit=20")
        scores = [s["similarity_score"] for s in r.json()["similar"]]
        assert scores == sorted(scores, reverse=True)

    def test_similarity_scores_between_0_and_1(self, client):
        r = client.get("/v1/entities/1/similar?limit=20")
        for s in r.json()["similar"]:
            assert 0.0 <= s["similarity_score"] <= 1.0

    def test_excludes_self(self, client):
        r = client.get("/v1/entities/1/similar")
        ids = [s["id"] for s in r.json()["similar"]]
        assert 1 not in ids

    def test_limit_parameter(self, client):
        r = client.get("/v1/entities/1/similar?limit=3")
        assert len(r.json()["similar"]) <= 3

    def test_min_score_filter(self, client):
        r = client.get("/v1/entities/1/similar?min_score=0.8")
        for s in r.json()["similar"]:
            assert s["similarity_score"] >= 0.8

    def test_nonexistent_entity_returns_404(self, client):
        r = client.get("/v1/entities/99999/similar")
        assert r.status_code == 404

    def test_total_similar_count(self, client):
        r = client.get("/v1/entities/1/similar?limit=5")
        data = r.json()
        assert "total_similar" in data
        assert data["total_similar"] >= len(data["similar"])
