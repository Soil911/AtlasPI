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
        # v6.92.1: origin deve essere nella whitelist CORS (v6.66.0 audit
        # security ha tolto il default `*`). Usiamo il dominio pubblico
        # canonico — vedi src/config.py::_CORS_DEFAULT.
        r = client.options(
            "/health",
            headers={
                "Origin": "https://atlaspi.it",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert r.status_code == 200

    def test_cors_preflight_unknown_origin_rejected(self, client):
        # Origin non in whitelist: Starlette CORSMiddleware risponde 400
        # al preflight (non manda Access-Control-Allow-Origin).
        r = client.options(
            "/health",
            headers={
                "Origin": "http://evil.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert r.status_code == 400


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
