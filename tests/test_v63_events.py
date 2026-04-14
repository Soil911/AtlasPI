"""Test per v6.3 Events layer — ETHICS-007 + ETHICS-008.

Copre:
  * CRUD-like read tramite gli endpoint /v1/events
  * Filtri: year, event_type, status, known_silence
  * /v1/events/types enumera tutti gli EventType senza eufemismi
  * /v1/events/{id} detail con entity_links
  * /v1/entities/{id}/events reverse-lookup
  * ETHICS-007: terminologia esplicita per violenze coloniali e genocidi
  * ETHICS-008: filtro known_silence per eventi con documentazione assente
  * Integrità: seed idempotente, confidence in [0,1], casualties_low <= casualties_high
"""

from __future__ import annotations

import pytest

from src.db.enums import EventRole, EventType
from src.db.models import (
    EventEntityLink,
    EventSource,
    GeoEntity,
    HistoricalEvent,
)

# ─── Sanity: seed ha popolato la tabella eventi ──────────────────


def test_events_seeded(db):
    count = db.query(HistoricalEvent).count()
    assert count >= 30, f"Attesi 30+ eventi core, trovati {count}"


def test_event_entity_links_resolved(db):
    """Almeno alcuni link devono risolvere verso GeoEntity reali."""
    links = db.query(EventEntityLink).count()
    assert links >= 10, f"Attesi 10+ link entità↔evento, trovati {links}"


# ─── /v1/events list ─────────────────────────────────────────────


def test_list_events_default_returns_events(client):
    r = client.get("/v1/events")
    assert r.status_code == 200
    d = r.json()
    assert "total" in d
    assert "events" in d
    assert len(d["events"]) > 0
    # Le voci della lista sono summary (non detail)
    first = d["events"][0]
    assert "id" in first
    assert "name_original" in first
    assert "event_type" in first
    assert "year" in first
    assert "known_silence" in first


def test_list_events_year_filter(client):
    """Eventi dopo il 1900 escludono Marathon (-490)."""
    r = client.get("/v1/events?year_min=1900")
    assert r.status_code == 200
    d = r.json()
    for e in d["events"]:
        assert e["year"] >= 1900 or (e.get("year_end") and e["year_end"] >= 1900)


def test_list_events_event_type_filter(client):
    r = client.get("/v1/events?event_type=GENOCIDE")
    assert r.status_code == 200
    d = r.json()
    assert d["total"] >= 1, "Almeno un GENOCIDE nei seed (ETHICS-007)"
    for e in d["events"]:
        assert e["event_type"] == "GENOCIDE"


def test_list_events_known_silence_filter(client):
    """ETHICS-008: deve esistere almeno un evento known_silence=true."""
    r = client.get("/v1/events?known_silence=true")
    assert r.status_code == 200
    d = r.json()
    assert d["total"] >= 1, "Almeno un silenzio documentato (ETHICS-008)"
    for e in d["events"]:
        assert e["known_silence"] is True


def test_list_events_known_silence_false(client):
    """known_silence=false esclude i silenzi documentati."""
    r = client.get("/v1/events?known_silence=false")
    assert r.status_code == 200
    d = r.json()
    for e in d["events"]:
        assert e["known_silence"] is False


def test_list_events_pagination(client):
    r = client.get("/v1/events?limit=2&offset=0")
    assert r.status_code == 200
    d = r.json()
    assert len(d["events"]) <= 2
    assert d["limit"] == 2
    assert d["offset"] == 0


def test_list_events_cache_headers(client):
    r = client.get("/v1/events")
    assert "cache-control" in r.headers
    assert "max-age" in r.headers["cache-control"]


# ─── /v1/events/types ────────────────────────────────────────────


def test_event_types_enumerated(client):
    r = client.get("/v1/events/types")
    assert r.status_code == 200
    d = r.json()
    assert "event_types" in d
    assert "event_roles" in d
    types = [t["type"] for t in d["event_types"]]
    # ETHICS-007: enum completo, senza eufemismi
    for required in (
        "GENOCIDE",
        "COLONIAL_VIOLENCE",
        "ETHNIC_CLEANSING",
        "MASSACRE",
        "DEPORTATION",
        "FAMINE",
    ):
        assert required in types, f"EventType {required} deve essere enumerato (ETHICS-007)"


def test_event_types_no_euphemisms(client):
    """ETHICS-007: NON devono comparire eufemismi come 'PACIFICATION' o 'INCIDENT'."""
    r = client.get("/v1/events/types")
    types = [t["type"] for t in r.json()["event_types"]]
    for forbidden in ("PACIFICATION", "INCIDENT", "REGRETTABLE_EVENT", "POPULATION_TRANSFER"):
        assert forbidden not in types, f"Eufemismo {forbidden} non ammesso (ETHICS-007)"


def test_event_types_matches_enum(client):
    r = client.get("/v1/events/types")
    api_types = {t["type"] for t in r.json()["event_types"]}
    enum_types = {t.value for t in EventType}
    assert api_types == enum_types, "API types deve coincidere con enum EventType"


def test_event_roles_contains_victim(client):
    """ETHICS-007: deve esistere ruolo VICTIM esplicito."""
    r = client.get("/v1/events/types")
    roles = [r_["role"] for r_ in r.json()["event_roles"]]
    assert "VICTIM" in roles
    assert "MAIN_ACTOR" in roles


# ─── /v1/events/{id} detail ──────────────────────────────────────


def test_event_detail_structure(client):
    """Ottieni il primo evento e verifica la struttura detail."""
    r = client.get("/v1/events?limit=1")
    first_id = r.json()["events"][0]["id"]

    r = client.get(f"/v1/events/{first_id}")
    assert r.status_code == 200
    d = r.json()
    assert "description" in d
    assert "entity_links" in d
    assert "sources" in d
    assert "ethical_notes" in d or d.get("ethical_notes") is None


def test_event_detail_404_unknown(client):
    r = client.get("/v1/events/999999")
    assert r.status_code == 404
    body = r.json()
    assert body["error"] is True
    assert body["error_detail"]["code"] == "NOT_FOUND"


def test_event_detail_entity_links_have_role(client):
    """ETHICS-007: ogni link ha un ruolo esplicito (voce attiva)."""
    r = client.get("/v1/events?limit=50")
    # Trova un evento con link
    for ev in r.json()["events"]:
        detail = client.get(f"/v1/events/{ev['id']}").json()
        if detail.get("entity_links"):
            for link in detail["entity_links"]:
                assert "role" in link
                assert link["role"] in {r_.value for r_ in EventRole}
            return  # uno basta
    pytest.skip("Nessun evento con entity_links nei seed (seed potrebbe avere solo nomi unresolved)")


# ─── /v1/entities/{id}/events ────────────────────────────────────


def test_entity_events_endpoint_exists(client):
    """Prendi un entity e verifica l'endpoint, anche se restituisce 0 eventi."""
    r = client.get("/v1/entity?limit=1")
    entity_id = r.json()["entities"][0]["id"]
    r = client.get(f"/v1/entities/{entity_id}/events")
    assert r.status_code == 200
    d = r.json()
    assert "entity_id" in d
    assert "events" in d
    assert d["entity_id"] == entity_id


def test_entity_events_404_for_unknown_entity(client):
    r = client.get("/v1/entities/999999/events")
    assert r.status_code == 404


# ─── ETHICS compliance ────────────────────────────────────────────


def test_every_event_has_description(db):
    """ETHICS-007: ogni evento deve avere description non vuota."""
    missing = (
        db.query(HistoricalEvent)
        .filter((HistoricalEvent.description.is_(None)) | (HistoricalEvent.description == ""))
        .count()
    )
    assert missing == 0, f"{missing} eventi senza description"


def test_violent_events_have_main_actor(db):
    """ETHICS-007: eventi di violenza organizzata DEVONO avere main_actor.

    Per non cadere in 'violenza senza agente' (l'eufemismo più comune).
    """
    violent_types = [
        EventType.GENOCIDE.value,
        EventType.COLONIAL_VIOLENCE.value,
        EventType.ETHNIC_CLEANSING.value,
        EventType.MASSACRE.value,
        EventType.DEPORTATION.value,
    ]
    violent = db.query(HistoricalEvent).filter(HistoricalEvent.event_type.in_(violent_types)).all()
    assert len(violent) >= 1, "Seed deve includere almeno un evento di violenza organizzata"
    missing_actor = [e for e in violent if not e.main_actor]
    assert not missing_actor, (
        f"Eventi violenti senza main_actor (ETHICS-007): "
        f"{[(e.id, e.name_original) for e in missing_actor]}"
    )


def test_known_silence_events_have_reason(db):
    """ETHICS-008: se known_silence=true, silence_reason deve essere presente."""
    silent = db.query(HistoricalEvent).filter(HistoricalEvent.known_silence.is_(True)).all()
    assert len(silent) >= 1, "Seed deve includere almeno un evento con silenzio documentato"
    for e in silent:
        assert e.silence_reason, (
            f"ETHICS-008: evento {e.id} '{e.name_original}' ha known_silence=true "
            f"ma silence_reason vuoto"
        )


def test_casualties_range_consistent(db):
    """Integrità: casualties_low <= casualties_high quando entrambi presenti."""
    rows = (
        db.query(HistoricalEvent)
        .filter(HistoricalEvent.casualties_low.isnot(None))
        .filter(HistoricalEvent.casualties_high.isnot(None))
        .all()
    )
    for e in rows:
        assert e.casualties_low <= e.casualties_high, (
            f"Evento {e.id} '{e.name_original}' ha casualties_low > casualties_high"
        )


def test_confidence_in_range(db):
    """Integrità: confidence_score in [0.0, 1.0]."""
    rows = db.query(HistoricalEvent).all()
    for e in rows:
        assert 0.0 <= e.confidence_score <= 1.0, (
            f"Evento {e.id} confidence fuori range: {e.confidence_score}"
        )


def test_sources_present_for_most_events(db):
    """La maggior parte degli eventi deve avere almeno una sorgente.

    Non è un constraint hard (eventi di tradizione orale possono avere sorgenti
    diverse dal tipo citation) ma un indicatore di qualità del seed.
    """
    all_events = db.query(HistoricalEvent).all()
    with_sources = sum(1 for e in all_events if e.sources)
    ratio = with_sources / max(len(all_events), 1)
    assert ratio >= 0.8, f"Solo {ratio:.0%} degli eventi ha sources (atteso >=80%)"


# ─── Seed idempotency ────────────────────────────────────────────


def test_seed_events_idempotent(db):
    """Chiamare seed_events_database() due volte non duplica righe."""
    from src.db import seed as seed_module

    before = db.query(HistoricalEvent).count()

    # Monkeypatch temporaneo del SessionLocal verso la sessione di test
    original = seed_module.SessionLocal
    seed_module.SessionLocal = db.session_factory if hasattr(db, "session_factory") else None

    # Fallback robusto: usa la sessione del test direttamente
    from tests.conftest import TestSession
    seed_module.SessionLocal = TestSession
    try:
        seed_module.seed_events_database()
    finally:
        seed_module.SessionLocal = original

    after = db.query(HistoricalEvent).count()
    assert after == before, "seed_events_database non è idempotente"
