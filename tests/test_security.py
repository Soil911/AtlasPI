"""Test di sicurezza: CORS, headers, rate limiting."""


class TestSecurityHeaders:
    def test_x_content_type_options(self, client):
        r = client.get("/health")
        assert r.headers.get("x-content-type-options") == "nosniff"

    def test_x_frame_options(self, client):
        r = client.get("/health")
        assert r.headers.get("x-frame-options") == "DENY"

    def test_request_id_present(self, client):
        r = client.get("/health")
        assert "x-request-id" in r.headers
        assert len(r.headers["x-request-id"]) > 0


class TestCORS:
    def test_cors_preflight(self, client):
        r = client.options(
            "/health",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert r.status_code == 200


class TestErrorResponses:
    def test_404_is_structured(self, client):
        r = client.get("/v1/entities/99999")
        assert r.status_code == 404
        d = r.json()
        assert "error" in d
        assert "detail" in d
        assert "request_id" in d

    def test_422_on_bad_input(self, client):
        r = client.get("/v1/entity?year=notanumber")
        assert r.status_code == 422
