"""Traffic-fix #1: /v1/entity/{id} (singolare) → 308 → /v1/entities/{id} (plurale).

Osservato in prod (2026-05-31): agent AI che, trovato funzionante /v1/entity?name=,
deducono /v1/entity/{id} per il dettaglio e prendono 404. Il redirect 308 canonico
elimina questi fallimenti, preservando query string e sotto-route, senza toccare
l'endpoint di ricerca /v1/entity.
"""


def test_singular_id_redirects_to_plural(client):
    r = client.get("/v1/entity/1", follow_redirects=False)
    assert r.status_code == 308
    assert r.headers["location"] == "/v1/entities/1"


def test_singular_id_followed_returns_entity(client):
    r = client.get("/v1/entity/1")  # segue il redirect
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_singular_subpath_redirects(client):
    r = client.get("/v1/entity/1/timeline", follow_redirects=False)
    assert r.status_code == 308
    assert r.headers["location"] == "/v1/entities/1/timeline"


def test_redirect_preserves_query_string(client):
    r = client.get("/v1/entity/1/evolution?direction=forward", follow_redirects=False)
    assert r.status_code == 308
    assert r.headers["location"] == "/v1/entities/1/evolution?direction=forward"


def test_search_endpoint_singular_still_works(client):
    # /v1/entity (senza sotto-path) DEVE restare l'endpoint di ricerca.
    r = client.get("/v1/entity?limit=5")
    assert r.status_code == 200
    assert "entities" in r.json()
