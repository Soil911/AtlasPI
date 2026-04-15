"""Test per /v1/chains + /v1/entities/{id}/predecessors|successors (v6.5.0).

I test fabbricano fixture entità + chain in DB così coprono la logica
endpoint a prescindere dalla presenza di dati di produzione.

Aree coperte:
    * Chain list + filter (chain_type, region, year)
    * Chain detail con links ordinati
    * 404 su chain inesistente
    * predecessors / successors per entità
    * ETHICS-002: transition_type esposto correttamente sui link
    * /v1/chains/types — enum coverage
    * OpenAPI documentation
"""

from __future__ import annotations

import json

import pytest

from src.db.models import ChainLink, DynastyChain, GeoEntity


@pytest.fixture
def seeded_chain(db):
    """Crea una catena di test: Roman Republic → Roman Empire → Byzantine.

    Function-scoped (vincolato dallo scope del fixture `db` di conftest).
    Idempotente via check-existing.
    """
    # Verifica entità di test, creale se assenti.
    existing_entities = {
        e.name_original for e in db.query(GeoEntity).all()
    }

    test_entities = [
        dict(
            name_original="TEST_Roman_Republic",
            name_original_lang="la",
            entity_type="republic",
            year_start=-509, year_end=-27,
            confidence_score=0.95,
            ethical_notes=None,
        ),
        dict(
            name_original="TEST_Roman_Empire",
            name_original_lang="la",
            entity_type="empire",
            year_start=-27, year_end=476,
            confidence_score=0.95,
            ethical_notes=None,
        ),
        dict(
            name_original="TEST_Byzantine_Empire",
            name_original_lang="el",
            entity_type="empire",
            year_start=330, year_end=1453,
            confidence_score=0.95,
            ethical_notes=None,
        ),
    ]
    for ed in test_entities:
        if ed["name_original"] not in existing_entities:
            db.add(GeoEntity(**ed))
    db.commit()

    # Recupera gli ID per i link.
    e_rep = db.query(GeoEntity).filter_by(name_original="TEST_Roman_Republic").first()
    e_emp = db.query(GeoEntity).filter_by(name_original="TEST_Roman_Empire").first()
    e_byz = db.query(GeoEntity).filter_by(name_original="TEST_Byzantine_Empire").first()

    # Verifica chain di test.
    existing_chains = {c.name for c in db.query(DynastyChain).all()}

    chain_name = "TEST_Roman_Power_Center"
    if chain_name not in existing_chains:
        chain = DynastyChain(
            name=chain_name,
            name_lang="en",
            chain_type="SUCCESSION",
            region="Mediterranean",
            description=(
                "Power center evolution from Roman Republic to Byzantine Empire."
            ),
            confidence_score=0.9,
            ethical_notes=(
                "The Byzantine continuity from Western Rome is contested: "
                "Byzantines called themselves Romans (Ῥωμαῖοι), but Western "
                "European historiography traditionally treats 476 as a rupture."
            ),
            sources=json.dumps([
                {"citation": "Cambridge Ancient History vol. X-XIV",
                 "url": None, "source_type": "academic"},
            ]),
        )
        db.add(chain)
        db.flush()

        # Link 0: Roman Republic (no predecessor).
        db.add(ChainLink(
            chain_id=chain.id, entity_id=e_rep.id,
            sequence_order=0,
            transition_year=None, transition_type=None, is_violent=False,
        ))
        # Link 1: Roman Empire (Augustus 27 BCE — REFORM, formally not a conquest).
        db.add(ChainLink(
            chain_id=chain.id, entity_id=e_emp.id,
            sequence_order=1,
            transition_year=-27,
            transition_type="REFORM",
            is_violent=False,
            description="Augustus assumes principate after civil wars.",
            ethical_notes=(
                "Formally a 'restoration of the republic' but de facto "
                "monarchical reform. The 'res publica restituta' framing "
                "is itself a piece of imperial propaganda."
            ),
        ))
        # Link 2: Byzantine (330 CE — Constantine moves capital, REFORM).
        db.add(ChainLink(
            chain_id=chain.id, entity_id=e_byz.id,
            sequence_order=2,
            transition_year=330,
            transition_type="REFORM",
            is_violent=False,
            description="Constantine refounds Byzantium as Constantinople.",
        ))

    db.commit()
    yield


# ─── CHAINS LIST ────────────────────────────────────────────────────────


def test_chains_list_returns_chains(client, seeded_chain):
    r = client.get("/v1/chains?limit=100")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    names = {c["name"] for c in body["chains"]}
    assert "TEST_Roman_Power_Center" in names


def test_chains_filter_by_type(client, seeded_chain):
    r = client.get("/v1/chains?chain_type=SUCCESSION&limit=50")
    assert r.status_code == 200
    for c in r.json()["chains"]:
        assert c["chain_type"] == "SUCCESSION"


def test_chains_filter_by_region(client, seeded_chain):
    r = client.get("/v1/chains?region=mediterranean&limit=50")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1


def test_chains_filter_by_year(client, seeded_chain):
    # 200 CE: Roman Empire active (in our test chain).
    r = client.get("/v1/chains?year=200&limit=50")
    assert r.status_code == 200
    names = {c["name"] for c in r.json()["chains"]}
    assert "TEST_Roman_Power_Center" in names


# ─── CHAIN DETAIL ──────────────────────────────────────────────────────


def test_chain_detail_includes_ordered_links(client, db, seeded_chain):
    chain = db.query(DynastyChain).filter_by(name="TEST_Roman_Power_Center").first()
    r = client.get(f"/v1/chains/{chain.id}")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "TEST_Roman_Power_Center"
    assert len(body["links"]) == 3
    # Verifica ordine cronologico.
    seqs = [l["sequence_order"] for l in body["links"]]
    assert seqs == sorted(seqs)
    # ETHICS-002: transition_type esposto.
    assert body["links"][0]["transition_type"] is None  # first link, no predecessor
    assert body["links"][1]["transition_type"] == "REFORM"
    assert body["links"][2]["transition_type"] == "REFORM"


def test_chain_detail_includes_ethical_notes(client, db, seeded_chain):
    chain = db.query(DynastyChain).filter_by(name="TEST_Roman_Power_Center").first()
    r = client.get(f"/v1/chains/{chain.id}")
    body = r.json()
    assert body["ethical_notes"] is not None
    assert "contested" in body["ethical_notes"].lower() or "byzantine" in body["ethical_notes"].lower()


def test_chain_detail_404(client, seeded_chain):
    r = client.get("/v1/chains/99999999")
    assert r.status_code == 404


def test_chain_types_endpoint(client):
    r = client.get("/v1/chains/types")
    assert r.status_code == 200
    body = r.json()
    chain_types = {t["type"] for t in body["chain_types"]}
    assert {"DYNASTY", "SUCCESSION", "RESTORATION", "COLONIAL", "IDEOLOGICAL"} <= chain_types
    transition_types = {t["type"] for t in body["transition_types"]}
    assert {"CONQUEST", "REFORM", "SUCCESSION", "DECOLONIZATION"} <= transition_types


# ─── PREDECESSORS / SUCCESSORS ─────────────────────────────────────────


def test_entity_predecessors(client, db, seeded_chain):
    # Roman Empire (sequence 1) ha Roman Republic come predecessor.
    e_emp = db.query(GeoEntity).filter_by(name_original="TEST_Roman_Empire").first()
    r = client.get(f"/v1/entities/{e_emp.id}/predecessors")
    assert r.status_code == 200
    body = r.json()
    assert body["entity_name"] == "TEST_Roman_Empire"
    assert len(body["predecessors"]) >= 1
    pred = body["predecessors"][0]
    assert pred["predecessor_entity_name"] == "TEST_Roman_Republic"
    assert pred["transition_type"] == "REFORM"
    assert pred["transition_year"] == -27


def test_entity_successors(client, db, seeded_chain):
    # Roman Republic (sequence 0) ha Roman Empire come successor.
    e_rep = db.query(GeoEntity).filter_by(name_original="TEST_Roman_Republic").first()
    r = client.get(f"/v1/entities/{e_rep.id}/successors")
    assert r.status_code == 200
    body = r.json()
    assert body["entity_name"] == "TEST_Roman_Republic"
    assert len(body["successors"]) >= 1
    succ = body["successors"][0]
    assert succ["successor_entity_name"] == "TEST_Roman_Empire"
    assert succ["transition_type"] == "REFORM"


def test_entity_predecessors_first_link_empty(client, db, seeded_chain):
    # Roman Republic è sequence 0 in tutte le sue catene → no predecessors.
    e_rep = db.query(GeoEntity).filter_by(name_original="TEST_Roman_Republic").first()
    r = client.get(f"/v1/entities/{e_rep.id}/predecessors")
    assert r.status_code == 200
    body = r.json()
    assert body["predecessors"] == []


def test_entity_successors_last_link_empty(client, db, seeded_chain):
    # Byzantine (sequence 2, l'ultimo) → no successors nella nostra chain.
    e_byz = db.query(GeoEntity).filter_by(name_original="TEST_Byzantine_Empire").first()
    r = client.get(f"/v1/entities/{e_byz.id}/successors")
    assert r.status_code == 200
    body = r.json()
    assert body["successors"] == []


def test_entity_predecessors_404(client, seeded_chain):
    r = client.get("/v1/entities/99999999/predecessors")
    assert r.status_code == 404


def test_entity_successors_404(client, seeded_chain):
    r = client.get("/v1/entities/99999999/successors")
    assert r.status_code == 404


# ─── OPENAPI ────────────────────────────────────────────────────────────


def test_chains_in_openapi(client):
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    assert "/v1/chains" in paths
    assert "/v1/chains/{chain_id}" in paths
    assert "/v1/chains/types" in paths
    assert "/v1/entities/{entity_id}/predecessors" in paths
    assert "/v1/entities/{entity_id}/successors" in paths
    chain_list_params = {p["name"] for p in paths["/v1/chains"]["get"]["parameters"]}
    assert "chain_type" in chain_list_params
    assert "year" in chain_list_params
    assert "region" in chain_list_params
