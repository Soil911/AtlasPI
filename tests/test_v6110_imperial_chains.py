"""Tests for v6.11.0 imperial-continuity chains and events.

Covers:
  * batch_07_western_roman_continuity.json (Imperium Romanum → Regnum Francorum →
    Imperium Francorum → Sacrum Imperium Romanum → Deutsches Kaiserreich →
    Deutsches Reich) — the 6-link Western Roman imperial-continuity IDEOLOGICAL chain.
  * batch_08_eastern_roman_continuity.json (Imperium Romanum → Βασιλεία Ῥωμαίων)
    — 2-link Byzantine SUCCESSION chain, ending at the 1453 Ottoman conquest.
  * batch_09_mongol_yuan.json (Yekhe Mongol Ulus → Yuan → Northern Yuan) —
    3-link Mongol DYNASTY chain tracking East-Asian branch to 1635.
  * batch_11_imperial_chain_events.json — 11 events anchoring the above chains
    (800 Charlemagne coronation, 962 Otto I, 1204 Sack of Constantinople, 1206
    Kurultai, 1241 Mohi, 1260 Ain Jalut, 1271 Yuan founding, 1368 Ming expulsion,
    1453 Fall of Constantinople, 1806 HRE dissolution, 1871 Versailles).

ETHICS coverage:
  * Western chain must flag Third Reich + genocides as documentary not endorsed.
  * Byzantine chain must flag 1204 sack + 1453 conquest accurately.
  * Mongol chain must flag 20-60M conquest deaths + Zunghar genocide pointer.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.config import DATA_DIR
from src.db.enums import ChainType, EventType, TransitionType
from src.db.models import ChainLink, DynastyChain, HistoricalEvent

CHAINS_DIR = Path(DATA_DIR) / "chains"
EVENTS_DIR = Path(DATA_DIR) / "events"

V6110_WESTERN_FILE = CHAINS_DIR / "batch_07_western_roman_continuity.json"
V6110_BYZANTINE_FILE = CHAINS_DIR / "batch_08_eastern_roman_continuity.json"
V6110_MONGOL_FILE = CHAINS_DIR / "batch_09_mongol_yuan.json"
V6110_EVENTS_FILE = EVENTS_DIR / "batch_11_imperial_chain_events.json"


def _load(fp: Path) -> list[dict]:
    with fp.open(encoding="utf-8") as fh:
        return json.load(fh)


def _load_western() -> list[dict]:
    return _load(V6110_WESTERN_FILE)


def _load_byzantine() -> list[dict]:
    return _load(V6110_BYZANTINE_FILE)


def _load_mongol() -> list[dict]:
    return _load(V6110_MONGOL_FILE)


def _load_events() -> list[dict]:
    return _load(V6110_EVENTS_FILE)


# ─── file existence ────────────────────────────────────────────────


def test_v6110_western_file_exists():
    assert V6110_WESTERN_FILE.exists(), f"Missing: {V6110_WESTERN_FILE}"


def test_v6110_byzantine_file_exists():
    assert V6110_BYZANTINE_FILE.exists(), f"Missing: {V6110_BYZANTINE_FILE}"


def test_v6110_mongol_file_exists():
    assert V6110_MONGOL_FILE.exists(), f"Missing: {V6110_MONGOL_FILE}"


def test_v6110_events_file_exists():
    assert V6110_EVENTS_FILE.exists(), f"Missing: {V6110_EVENTS_FILE}"


# ─── structural: required keys on each chain ───────────────────────


@pytest.mark.parametrize("loader", [_load_western, _load_byzantine, _load_mongol])
@pytest.mark.parametrize("key", [
    "name", "name_lang", "chain_type", "region",
    "description", "confidence_score", "ethical_notes", "links", "sources",
])
def test_v6110_chain_required_keys(loader, key):
    chains = loader()
    assert len(chains) == 1
    assert key in chains[0], f"Missing key {key!r} in {loader.__name__}"


# ─── chain-type + transitions valid enum values ────────────────────


def test_v6110_western_chain_is_ideological():
    """Mixed Merovingian/Carolingian/HRE/Wilhelmine/Nazi links cannot be a
    legal-succession DYNASTY — must be IDEOLOGICAL."""
    chain = _load_western()[0]
    assert chain["chain_type"] == "IDEOLOGICAL"
    assert ChainType.IDEOLOGICAL.value == "IDEOLOGICAL"


def test_v6110_byzantine_chain_is_succession():
    chain = _load_byzantine()[0]
    assert chain["chain_type"] == "SUCCESSION"


def test_v6110_mongol_chain_is_dynasty():
    chain = _load_mongol()[0]
    assert chain["chain_type"] == "DYNASTY"


@pytest.mark.parametrize("loader", [_load_western, _load_byzantine, _load_mongol])
def test_v6110_chain_transitions_are_valid_enum(loader):
    valid = {e.value for e in TransitionType}
    for link in loader()[0]["links"]:
        tt = link.get("transition_type")
        if tt is None:
            continue
        assert tt in valid, f"Invalid transition_type: {tt!r}"


# ─── link counts + endpoints ───────────────────────────────────────


def test_v6110_western_has_6_links():
    chain = _load_western()[0]
    assert len(chain["links"]) == 6


def test_v6110_western_endpoints():
    chain = _load_western()[0]
    assert chain["links"][0]["entity_name"] == "Imperium Romanum"
    assert chain["links"][-1]["entity_name"] == "Deutsches Reich"


def test_v6110_byzantine_has_2_links():
    chain = _load_byzantine()[0]
    assert len(chain["links"]) == 2


def test_v6110_byzantine_endpoints():
    chain = _load_byzantine()[0]
    assert chain["links"][0]["entity_name"] == "Imperium Romanum"
    assert chain["links"][-1]["entity_name"] == "Βασιλεία Ῥωμαίων"


def test_v6110_mongol_has_3_links():
    chain = _load_mongol()[0]
    assert len(chain["links"]) == 3


def test_v6110_mongol_endpoints():
    chain = _load_mongol()[0]
    assert chain["links"][0]["entity_name"] == "ᠶᠡᠬᠡ ᠮᠣᠩᠭᠣᠯ ᠤᠯᠤᠰ"
    assert chain["links"][-1]["entity_name"] == "北元"


# ─── ETHICS invariants ─────────────────────────────────────────────


def test_v6110_western_third_reich_flagged_as_documentary():
    """ETHICS: the Deutsches Reich (1933-1945) link must be labelled REVOLUTION
    and the chain-level ethical_notes must explicitly describe the Nazi regime
    as a rupture claiming the continuity — not an endorsement of the claim."""
    chain = _load_western()[0]
    third = next(l for l in chain["links"] if l["entity_name"] == "Deutsches Reich")
    assert third["transition_type"] == "REVOLUTION"
    assert third["is_violent"] is True
    enote = third.get("ethical_notes") or ""
    # Must mention Holocaust numbers + civilian victim categories.
    assert any(kw in enote for kw in ("Holocaust", "6 million", "Jewish")), (
        f"Third Reich link must explicitly flag the Holocaust; got: {enote[:300]}"
    )
    # Chain-level note must contextualise the inclusion.
    chain_enote = chain["ethical_notes"]
    assert any(kw in chain_enote for kw in ("documentary", "appropriation", "perverting", "endorsement")), (
        "Chain ethical_notes must explain WHY Third Reich is included "
        "(documentary necessity, not legitimation)"
    )


def test_v6110_western_kaiserreich_flags_herero_nama_genocide():
    """ETHICS: the 1904-1908 Herero and Nama genocide (formally recognised
    by Germany in 2021) must be in the Kaiserreich link."""
    chain = _load_western()[0]
    kaiser = next(l for l in chain["links"] if l["entity_name"] == "Deutsches Kaiserreich")
    enote = (kaiser.get("ethical_notes") or "") + (kaiser.get("description") or "")
    assert any(kw in enote for kw in ("Herero", "Nama", "Trotha", "Shark Island")), (
        f"Kaiserreich link must flag the Herero/Nama genocide; got: {enote[:400]}"
    )


def test_v6110_western_carolingian_flags_verden_massacre():
    """ETHICS: Charlemagne's 800 coronation and reign must not silence the
    Saxon Wars, including the 782 Massacre of Verden (~4,500 beheaded)."""
    chain = _load_western()[0]
    carol = next(l for l in chain["links"] if l["entity_name"] == "Imperium Francorum")
    enote = (carol.get("ethical_notes") or "") + (carol.get("description") or "")
    assert any(kw in enote for kw in ("Verden", "Saxon", "forced conversion", "capitulatio")), (
        f"Carolingian link must flag Saxon Wars or Verden Massacre; got: {enote[:400]}"
    )


def test_v6110_byzantine_1204_sack_flagged():
    """ETHICS: the Byzantine chain must flag the 1204 Fourth Crusade sack
    even though it is not a link (it is a 57-year interruption)."""
    chain = _load_byzantine()[0]
    byz_link = next(l for l in chain["links"] if l["entity_name"] == "Βασιλεία Ῥωμαίων")
    enote = (byz_link.get("ethical_notes") or "") + (byz_link.get("description") or "")
    assert any(kw in enote for kw in ("1204", "Fourth Crusade", "Latin")), (
        f"Byzantine link must flag 1204 sack; got: {enote[:400]}"
    )


def test_v6110_byzantine_basil_bulgaroktonos_flagged():
    """ETHICS: Basil II's 1014 blinding of 14,000 Bulgarian prisoners at
    Kleidion (earning him 'Bulgar-Slayer') must not be whitewashed."""
    chain = _load_byzantine()[0]
    byz_link = next(l for l in chain["links"] if l["entity_name"] == "Βασιλεία Ῥωμαίων")
    enote = (byz_link.get("ethical_notes") or "") + (byz_link.get("description") or "")
    assert any(kw in enote for kw in ("Kleidion", "Bulgar", "Βουλγαροκτόνος", "14,000", "blinding")), (
        f"Byzantine link must flag Basil II's 1014 atrocity; got: {enote[:500]}"
    )


def test_v6110_mongol_conquest_mortality_flagged():
    """ETHICS: the Mongol chain must flag the 20-60M conquest death range."""
    chain = _load_mongol()[0]
    enote = chain["ethical_notes"]
    assert any(kw in enote for kw in ("20-60", "40 million", "60 million", "20–60", "Merv")), (
        f"Mongol chain must flag conquest mortality range; got: {enote[:500]}"
    )


def test_v6110_mongol_zunghar_pointer_present():
    """ETHICS: the Northern Yuan link ends with 1635 Qing submission, and the
    companion Zunghar genocide (1755-1758) must be pointed to even though it
    is on the Qing link of batch_04."""
    chain = _load_mongol()[0]
    # Can be in chain-level or link-level notes
    text = chain["ethical_notes"]
    for link in chain["links"]:
        text += (link.get("ethical_notes") or "") + (link.get("description") or "")
    assert any(kw in text for kw in ("Zunghar", "Dzungar", "1755", "1758")), (
        f"Mongol chain must point to the Zunghar genocide; got chunk: {text[:500]}"
    )


def test_v6110_mongol_yuan_caste_system_flagged():
    """ETHICS: the Yuan four-caste system (Mongol/Semu/Han/Nanren) must be
    flagged in the Yuan link — it's the structural mechanism the Ming would
    later weaponise as ethnic grievance."""
    chain = _load_mongol()[0]
    yuan = next(l for l in chain["links"] if l["entity_name"] == "元朝")
    enote = (yuan.get("ethical_notes") or "") + (yuan.get("description") or "")
    assert any(kw in enote for kw in ("four-caste", "Semu", "Han", "Nanren")), (
        f"Yuan link must flag the four-caste system; got: {enote[:400]}"
    )


# ─── ethical_notes thickness ───────────────────────────────────────


def test_v6110_western_ethical_notes_thick():
    chain = _load_western()[0]
    assert len(chain["ethical_notes"]) > 800, (
        f"Western chain note too thin: {len(chain['ethical_notes'])} chars"
    )


def test_v6110_byzantine_ethical_notes_thick():
    chain = _load_byzantine()[0]
    assert len(chain["ethical_notes"]) > 600


def test_v6110_mongol_ethical_notes_thick():
    chain = _load_mongol()[0]
    assert len(chain["ethical_notes"]) > 800


# ─── events batch_11 structural ────────────────────────────────────


def test_v6110_events_count():
    events = _load_events()
    # 9 net-new events after removing 2 duplicates (Karoli Magni 800 and
    # Alosis 1453 already in earlier batches). Total DB events post-ingest: 259.
    assert len(events) == 9, f"Expected 9 events, got {len(events)}"


def test_v6110_events_year_span():
    events = _load_events()
    years = [e["year"] for e in events]
    # Span the imperial-chain era: 962 Otto I to 1871 Versailles
    assert min(years) <= 962
    assert max(years) >= 1871


@pytest.mark.parametrize("key", [
    "name_original", "name_original_lang", "event_type", "year",
    "location_name", "location_lat", "location_lon", "main_actor",
    "description", "confidence_score", "status", "ethical_notes",
    "entity_links", "sources",
])
def test_v6110_event_has_required_keys(key):
    for ev in _load_events():
        assert key in ev, f"Event {ev.get('name_original')!r} missing {key!r}"


def test_v6110_events_types_valid_enum():
    valid = {e.value for e in EventType}
    for ev in _load_events():
        assert ev["event_type"] in valid, (
            f"Event {ev['name_original']} has invalid type {ev['event_type']!r}"
        )


def test_v6110_events_have_ethical_notes():
    for ev in _load_events():
        enote = ev.get("ethical_notes") or ""
        assert len(enote) > 80, (
            f"Event {ev['name_original']} has thin ethical_notes: "
            f"{len(enote)} chars"
        )


def test_v6110_events_have_primary_and_academic_sources():
    for ev in _load_events():
        src_types = {s["source_type"] for s in ev["sources"]}
        assert "primary" in src_types, (
            f"Event {ev['name_original']} lacks primary source"
        )
        assert "academic" in src_types, (
            f"Event {ev['name_original']} lacks academic source"
        )


# ─── event-specific ETHICS invariants ──────────────────────────────


def test_v6110_event_1453_fall_of_constantinople_in_db(db):
    """1453 Fall of Constantinople is in batch_01_core.json (already in DB,
    stored as SIEGE event-type there); batch_11's duplicate was removed during
    v6.11.0 ingest. This test verifies the event exists as a valid EventType
    and that v6.11.0 ingestion did not create a second 1453 Constantinople
    record."""
    evs = db.query(HistoricalEvent).filter(HistoricalEvent.year == 1453).all()
    if not evs:
        pytest.skip("1453 event not yet in DB")
    cpl = [e for e in evs if "Κωνσταντινουπόλεως" in e.name_original]
    if not cpl:
        pytest.skip("Fall of Constantinople not found by expected name")
    # No duplicate: exactly one row for the Constantinople fall.
    assert len(cpl) == 1, f"Duplicate 1453 Constantinople events: {[e.name_original for e in cpl]}"
    et = cpl[0].event_type.value if hasattr(cpl[0].event_type, "value") else cpl[0].event_type
    # Accept either SIEGE (batch_01) or CONQUEST (alternate framing).
    assert et in {"SIEGE", "CONQUEST"}, f"Unexpected 1453 event type: {et!r}"


def test_v6110_event_1204_fourth_crusade():
    events = _load_events()
    ev = next(e for e in events if e["year"] == 1204)
    assert ev["event_type"] == "MASSACRE"
    # The Fourth Crusade's diversion was driven by Venetian fleet-pricing pressure
    text = (ev.get("description") or "") + (ev.get("ethical_notes") or "")
    assert any(kw in text for kw in ("Venice", "Venetian", "Dandolo", "1201")), (
        f"1204 event must flag Venetian role; got: {text[:500]}"
    )


def test_v6110_event_ain_jalut_1260_flagged_as_contingent():
    events = _load_events()
    ev = next(e for e in events if e["year"] == 1260 and "جالوت" in e["name_original"])
    assert ev["event_type"] == "BATTLE"
    text = (ev.get("ethical_notes") or "")
    assert any(kw in text for kw in ("Möngke", "contingent", "Amitai", "retrospective")), (
        f"Ain Jalut event must contextualise the 'saved Islam' framing; got: {text[:400]}"
    )


def test_v6110_event_1206_kurultai():
    events = _load_events()
    ev = next(e for e in events if e["year"] == 1206)
    assert ev["event_type"] == "FOUNDING_STATE"
    # Must acknowledge 20-60M downstream mortality
    text = (ev.get("ethical_notes") or "")
    assert any(kw in text for kw in ("20", "60 million", "Merv", "60-year", "catastrophic")), (
        f"1206 kurultai event must acknowledge downstream conquest mortality; got: {text[:400]}"
    )


def test_v6110_event_1871_versailles_humiliation_logic():
    events = _load_events()
    ev = next(e for e in events if e["year"] == 1871)
    text = (ev.get("description") or "") + (ev.get("ethical_notes") or "")
    assert any(kw in text for kw in ("humiliation", "inverted", "Louis XIV", "1919", "1940")), (
        f"1871 event must expose the humiliation-ceremony logic; got: {text[:400]}"
    )


# ─── DB layer (soft) ───────────────────────────────────────────────


def test_v6110_western_chain_in_db(db):
    ch = db.query(DynastyChain).filter(
        DynastyChain.name.like("Western Roman imperial%")
    ).first()
    if ch is None:
        pytest.skip("Western chain not yet ingested in test DB")
    links = db.query(ChainLink).filter_by(chain_id=ch.id).all()
    assert len(links) == 6


def test_v6110_byzantine_chain_in_db(db):
    ch = db.query(DynastyChain).filter(
        DynastyChain.name.like("Eastern Roman (Byzantine)%")
    ).first()
    if ch is None:
        pytest.skip("Byzantine chain not yet ingested in test DB")
    links = db.query(ChainLink).filter_by(chain_id=ch.id).all()
    assert len(links) == 2


def test_v6110_mongol_chain_in_db(db):
    ch = db.query(DynastyChain).filter(
        DynastyChain.name.like("Mongol Empire Yuan branch%")
    ).first()
    if ch is None:
        pytest.skip("Mongol chain not yet ingested in test DB")
    links = db.query(ChainLink).filter_by(chain_id=ch.id).all()
    assert len(links) == 3


def test_v6110_total_chain_count_grew(db):
    """After v6.11.0 there should be 17 chains on disk (14 from v6.10.0 + 3)."""
    total = 0
    for fp in sorted(CHAINS_DIR.glob("batch_*.json")):
        with fp.open(encoding="utf-8") as fh:
            total += len(json.load(fh))
    assert total >= 17, f"Total chains on disk {total} — expected 17+ after v6.11.0"

    db_count = db.query(DynastyChain).count()
    if db_count >= 14:
        assert db_count >= 17, f"Chain ingest landed {db_count} — expected 17+"


def test_v6110_1206_event_in_db(db):
    """Spot-check: Mongol 1206 kurultai founding event is ingested."""
    ev = db.query(HistoricalEvent).filter(
        HistoricalEvent.year == 1206,
    ).first()
    if ev is None:
        pytest.skip("1206 event not yet ingested")
    et = ev.event_type.value if hasattr(ev.event_type, "value") else ev.event_type
    assert et == "FOUNDING_STATE"
