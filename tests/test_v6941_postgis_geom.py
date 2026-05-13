"""Test per audit R1 (ADR-009): PostGIS boundary_geom column + endpoint switch.

I test verificano:
  * Validazione parametri ?contains=lat,lon (422 su formato sbagliato).
  * Endpoint /v1/entities?contains= ritorna 200 con shape attesa.
  * SQLite dev: ?contains= ritorna sempre lista vuota (feature PostGIS-only,
    documentata cosi' in OpenAPI).
  * /v1/entities?bbox= continua a funzionare dopo lo switch a boundary_geom
    reference.

Su PostgreSQL+PostGIS (CI postgres-migrations o prod) il filtro contains
e' funzionale e usa l'indice GiST. I test pgsql-funzionali sono affidati
al CI postgres-migrations job (alembic upgrade head + import sanity) +
verifica manuale in prod.
"""


class TestContainsValidation:
    def test_contains_invalid_format_no_comma(self, client):
        r = client.get("/v1/entities?contains=invalid")
        assert r.status_code == 422

    def test_contains_invalid_format_three_values(self, client):
        r = client.get("/v1/entities?contains=1,2,3")
        assert r.status_code == 422

    def test_contains_lat_out_of_range(self, client):
        r = client.get("/v1/entities?contains=91.0,12.5")
        assert r.status_code == 422

    def test_contains_lon_out_of_range(self, client):
        r = client.get("/v1/entities?contains=41.9,181.0")
        assert r.status_code == 422

    def test_contains_non_numeric(self, client):
        r = client.get("/v1/entities?contains=foo,bar")
        assert r.status_code == 422


class TestContainsHappy:
    def test_contains_valid_coordinates_returns_200(self, client):
        # Roma (Italia centrale). Su SQLite ritorna lista vuota (no PostGIS).
        # Su Postgres ritorna entita' con boundary_geom che contiene il punto.
        r = client.get("/v1/entities?contains=41.9,12.5")
        assert r.status_code == 200
        d = r.json()
        assert "entities" in d
        assert "total" in d
        assert isinstance(d["entities"], list)

    def test_contains_combined_with_year(self, client):
        # Combina spatial + temporal filter
        r = client.get("/v1/entities?contains=41.9,12.5&year=100")
        assert r.status_code == 200

    def test_contains_sqlite_returns_empty(self, client):
        """v6.94.1 ADR-009: SQLite dev no PostGIS support → filter False."""
        # NB: in CI con postgres-migrations questo test salterebbe il check
        # finale (PostGIS attivo). Qui assumo conftest fissa SQLite.
        r = client.get("/v1/entities?contains=41.9,12.5&limit=5")
        d = r.json()
        # SQLite path: q.filter(False) → entities sempre vuoto
        # NB: se in futuro il test runtime e' Postgres, modificare assertion.
        assert d["entities"] == []


class TestBboxStillWorks:
    """Regression check: lo switch da ST_GeomFromGeoJSON a boundary_geom
    deve mantenere la response shape e i count di /v1/entities?bbox=."""

    def test_bbox_empty_response_shape(self, client):
        # Bbox a -90,-180,-89,-179 (Antartide remoto) — nessuna entita'.
        r = client.get("/v1/entities?bbox=-180,-90,-179,-89")
        assert r.status_code == 200
        d = r.json()
        assert "total" in d
        assert "entities" in d

    def test_bbox_global_no_filter_lost(self, client):
        # bbox -180,-90,180,90 = mondo. Su SQLite filtra solo capital-point.
        # Su Postgres usa ST_Intersects(boundary_geom, envelope).
        # Total dovrebbe essere > 100 (la maggior parte delle entita' ha
        # capital o boundary nell'envelope mondiale).
        r = client.get("/v1/entities?bbox=-180,-90,180,90&limit=10")
        assert r.status_code == 200
        d = r.json()
        # Almeno 10 entita' nell'envelope mondiale (sanity check)
        assert d["total"] >= 10
