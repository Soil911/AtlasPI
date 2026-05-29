"""Wave 2.5 (audit API #1): gli endpoint headline per agent AI espongono uno
schema OpenAPI reale, e response_model NON elimina campi (modelli mirror-esatti).

Prima, ~88% delle route mostravano `schema: {}` in /openapi.json → un agent non
poteva conoscere la forma della risposta. Ora /v1/entities/light, /v1/entities/batch
e /v1/events sono tipizzati. I test "keeps_all_keys" sono la rete anti-regressione:
se un modello mirror dimenticasse una chiave, response_model la droppererebbe e
qui fallirebbe.
"""

LIGHT_ENTITY_KEYS = {
    "id", "name_original", "name_original_lang", "entity_type", "year_start",
    "year_end", "capital_name", "capital_lat", "capital_lon",
    "confidence_score", "status", "continent",
}
EVENT_SUMMARY_KEYS = {
    "id", "name_original", "name_original_lang", "event_type", "year", "year_end",
    "month", "day", "date_precision", "iso_date", "location_name", "location_lat",
    "location_lon", "main_actor", "status", "confidence_score", "known_silence",
}


def test_openapi_documents_headline_response_schemas(client):
    spec = client.get("/openapi.json").json()
    paths = spec["paths"]
    for path in ["/v1/entities/light", "/v1/entities/batch", "/v1/events"]:
        schema = paths[path]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
        assert schema and schema != {}, f"{path}: schema OpenAPI vuoto (agent non può tipizzare)"
        assert "$ref" in schema or "properties" in schema, f"{path}: schema non strutturato: {schema}"


def test_light_response_keeps_all_keys(client):
    body = client.get("/v1/entities/light").json()
    assert {"total", "count", "entities"} <= set(body.keys())
    if body["entities"]:
        missing = LIGHT_ENTITY_KEYS - set(body["entities"][0].keys())
        assert not missing, f"response_model ha droppato chiavi da /light: {missing}"


def test_events_response_keeps_all_keys(client):
    body = client.get("/v1/events?limit=1").json()
    assert {"total", "limit", "offset", "events"} <= set(body.keys())
    if body["events"]:
        missing = EVENT_SUMMARY_KEYS - set(body["events"][0].keys())
        assert not missing, f"response_model ha droppato chiavi da /v1/events: {missing}"


def test_batch_response_shape_and_inner_entity(client):
    body = client.get("/v1/entities/batch?ids=1,2").json()
    assert {"requested", "found", "not_found", "entities"} <= set(body.keys())
    assert isinstance(body["not_found"], list)
    if body["entities"]:
        # le entities interne riusano EntityResponse → devono mantenere i campi core
        core = {"id", "name_original", "entity_type", "confidence_score", "status", "sources"}
        missing = core - set(body["entities"][0].keys())
        assert not missing, f"batch: EntityResponse ha droppato campi core: {missing}"
