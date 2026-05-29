"""Wave 2.3 (audit API #2): tutti gli errori HTTP usano l'envelope canonico.

Prima del fix i ~58 `raise HTTPException` (es. /v1/periods/by-slug/{slug})
bypassavano l'envelope {"error":{code,message,request_id}} restituendo il
default FastAPI {"detail": ...}, quindi due 404 da endpoint fratelli avevano
forma JSON diversa. Ora un handler StarletteHTTPException li normalizza,
preservando gli header dell'eccezione (es. WWW-Authenticate dell'auth admin).
"""


def test_raw_httpexception_404_uses_canonical_envelope(client):
    # /v1/periods/by-slug/{slug} con slug inesistente → raw HTTPException(404).
    r = client.get("/v1/periods/by-slug/__nonexistent_slug__")
    assert r.status_code == 404
    body = r.json()
    assert "error" in body, f"manca envelope canonico: {body}"
    assert body["error"]["code"] == "NOT_FOUND"
    assert "request_id" in body["error"]
    assert "detail" in body  # legacy flat preservato


def test_typed_and_raw_404_have_identical_envelope_shape(client):
    raw = client.get("/v1/periods/by-slug/__nonexistent_slug__").json()
    typed = client.get("/v1/entities/99999999").json()
    # Stesso involucro: un agent che legge response.error.code funziona su entrambi.
    assert set(raw.keys()) == set(typed.keys())
    assert raw["error"].keys() >= {"code", "message", "request_id"}
    assert typed["error"].keys() >= {"code", "message", "request_id"}


def test_admin_401_still_has_www_authenticate(unauth_client):
    # Regressione critica: il nuovo handler NON deve perdere WWW-Authenticate
    # (verify_admin lo imposta per far comparire il prompt del browser).
    r = unauth_client.get("/admin/cache-stats")
    assert r.status_code == 401
    header_keys = {k.lower() for k in r.headers.keys()}
    assert "www-authenticate" in header_keys
    # 401 ora mappa a UNAUTHORIZED nell'envelope canonico.
    assert r.json()["error"]["code"] == "UNAUTHORIZED"
