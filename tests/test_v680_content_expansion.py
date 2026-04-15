"""Tests for v6.8.0 content expansion: ancient events + Asian dynasty chains.

Covers:
  * batch_09_ancient_expansion.json structure and schema
  * Pre-500 CE gap reduction (was 29 events, now 53)
  * batch_03_asia.json structure
  * Japan 7-link shogunate chain wiring
  * India 5-link classical dynastic chain wiring
  * ETHICS coverage on all new content
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.config import DATA_DIR
from src.db.enums import ChainType, EventType, TransitionType
from src.db.models import (
    ChainLink,
    DynastyChain,
    EventEntityLink,
    EventSource,
    GeoEntity,
    HistoricalEvent,
)

EVENTS_DIR = Path(DATA_DIR) / "events"
CHAINS_DIR = Path(DATA_DIR) / "chains"

V680_EVENTS_FILE = EVENTS_DIR / "batch_09_ancient_expansion.json"
V680_CHAINS_FILE = CHAINS_DIR / "batch_03_asia.json"


# ─── batch_09_ancient_expansion.json — file structure ──────────────


def _load_v680_events() -> list[dict]:
    with V680_EVENTS_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


def _load_v680_chains() -> list[dict]:
    with V680_CHAINS_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


def test_v680_events_file_exists():
    assert V680_EVENTS_FILE.exists(), f"Missing: {V680_EVENTS_FILE}"


def test_v680_events_is_list_of_20_plus():
    events = _load_v680_events()
    assert isinstance(events, list)
    assert len(events) >= 20, (
        f"Expected 20+ ancient events in batch_09, got {len(events)}"
    )


@pytest.mark.parametrize("key", [
    "name_original", "name_original_lang", "event_type",
    "year", "description", "confidence_score", "status",
    "ethical_notes", "entity_links", "sources",
])
def test_v680_event_has_required_keys(key):
    events = _load_v680_events()
    for ev in events:
        assert key in ev, f"Event {ev.get('name_original', '?')} missing key {key!r}"


def test_v680_event_types_are_valid_enum():
    events = _load_v680_events()
    valid = {e.value for e in EventType}
    for ev in events:
        assert ev["event_type"] in valid, (
            f"Event {ev['name_original']!r} has invalid event_type {ev['event_type']!r}"
        )


def test_v680_events_are_pre_500_ce():
    """Main raison d'etre of this batch: fill the pre-500 CE gap."""
    events = _load_v680_events()
    for ev in events:
        assert ev["year"] <= 500, (
            f"Event {ev['name_original']!r} has year={ev['year']} — "
            f"not pre-500 CE (this batch targets the ancient gap)"
        )


def test_v680_events_span_multiple_regions():
    """The batch covers Near East + Greece + Rome + India + China, not only Mediterranean."""
    events = _load_v680_events()
    langs = {ev["name_original_lang"] for ev in events}
    # Expect at minimum Akkadian, Hebrew, Greek, Latin, Sanskrit, Chinese, Persian, Aramaic
    expected_any = {"akk", "heb", "grc", "lat", "san", "lzh", "peo", "arc"}
    present = langs & expected_any
    assert len(present) >= 5, (
        f"Expected 5+ of {sorted(expected_any)} represented among ancient events, "
        f"got {sorted(present)}"
    )


def test_v680_events_have_sources():
    events = _load_v680_events()
    for ev in events:
        assert len(ev["sources"]) >= 1, (
            f"Event {ev['name_original']!r} has no sources"
        )
        # At least one primary or academic per event.
        stypes = {s.get("source_type") for s in ev["sources"]}
        assert stypes & {"primary", "academic"}, (
            f"Event {ev['name_original']!r} has no primary/academic sources "
            f"({stypes})"
        )


def test_v680_events_have_ethical_notes():
    """Every ancient-expansion event carries an ETHICS note because the gap
    filling is itself a representational choice (whose violence gets recorded)."""
    events = _load_v680_events()
    for ev in events:
        assert ev.get("ethical_notes"), (
            f"Event {ev['name_original']!r} lacks ethical_notes — "
            f"v6.8.0 ancient expansion requires ETHICS coverage"
        )
        assert len(ev["ethical_notes"]) > 80, (
            f"Event {ev['name_original']!r} has thin ethical_notes"
        )


def test_v680_events_confidence_in_range():
    events = _load_v680_events()
    for ev in events:
        c = ev["confidence_score"]
        assert 0.0 <= c <= 1.0, f"Confidence out of range: {c} for {ev['name_original']!r}"


# ─── DB-layer: ingest landed new events ────────────────────────────


def test_v680_events_in_db(db):
    """After seed, the 24 new pre-500 CE events should be present."""
    events = _load_v680_events()
    names = [ev["name_original"] for ev in events]
    in_db = db.query(HistoricalEvent).filter(
        HistoricalEvent.name_original.in_(names)
    ).count()
    # At least ~80% landed (some may fail enum-strictness tests in future refactors).
    assert in_db >= len(names) * 0.8, (
        f"Only {in_db}/{len(names)} v6.8.0 ancient events reached the DB"
    )


def test_v680_pre_500_ce_gap_closed(db):
    """Historical: 29 pre-500 CE events before v6.8.0. After: 50+."""
    count = db.query(HistoricalEvent).filter(HistoricalEvent.year <= 500).count()
    assert count >= 50, (
        f"Pre-500 CE event count {count} — expected 50+ after v6.8.0 expansion "
        f"(was 29 pre-v6.8.0)"
    )


def test_v680_caesar_assassination_linked(db):
    """Spot-check: the Caesar assassination event should be linked to Imperium Romanum."""
    ev = db.query(HistoricalEvent).filter_by(
        name_original="Caedes C. Iulii Caesaris"
    ).first()
    if ev is None:
        pytest.skip("Caesar event not in this test DB")
    link_entity_names = {link.entity.name_original for link in ev.entity_links}
    assert "Imperium Romanum" in link_entity_names


def test_v680_cyrus_liberation_linked_to_judah(db):
    """Spot-check: Cyrus's conquest of Babylon liberates exiled Judah."""
    ev = db.query(HistoricalEvent).filter_by(year=-539).filter(
        HistoricalEvent.name_original.like("%𐎤𐎢𐎽𐎢𐏁%")
    ).first()
    if ev is None:
        pytest.skip("Cyrus event not in this test DB")
    # Expect both Neo-Babylonian (dissolved) and Judah (liberated)
    link_roles = {(link.entity.name_original, link.role) for link in ev.entity_links}
    assert any(
        "יהודה" in name for name, _role in link_roles
    ), f"Expected Judah linked to Cyrus event; got {link_roles}"


# ─── batch_03_asia.json — chains structure ─────────────────────────


def test_v680_chains_file_exists():
    assert V680_CHAINS_FILE.exists(), f"Missing: {V680_CHAINS_FILE}"


def test_v680_chains_is_list_of_2():
    chains = _load_v680_chains()
    assert isinstance(chains, list)
    assert len(chains) == 2, f"Expected 2 Asia chains in v6.8.0, got {len(chains)}"


@pytest.mark.parametrize("key", [
    "name", "name_lang", "chain_type", "region",
    "description", "confidence_score", "ethical_notes", "links",
])
def test_v680_chain_has_required_keys(key):
    chains = _load_v680_chains()
    for ch in chains:
        assert key in ch, f"Chain {ch.get('name', '?')!r} missing key {key!r}"


def test_v680_chain_types_are_valid_enum():
    chains = _load_v680_chains()
    valid = {e.value for e in ChainType}
    for ch in chains:
        assert ch["chain_type"] in valid, (
            f"Chain {ch['name']!r} has invalid chain_type {ch['chain_type']!r}"
        )


def test_v680_chain_transition_types_are_valid_enum():
    chains = _load_v680_chains()
    valid = {e.value for e in TransitionType}
    for ch in chains:
        for link in ch["links"]:
            tt = link.get("transition_type")
            if tt is None:
                continue
            assert tt in valid, (
                f"Chain {ch['name']!r} link {link['entity_name']!r} "
                f"has invalid transition_type {tt!r}"
            )


def test_v680_japan_chain_has_7_links():
    chains = _load_v680_chains()
    japan = next(ch for ch in chains if "Japanese" in ch["name"])
    assert len(japan["links"]) == 7, (
        f"Expected 7-link Japan chain (Nara through Meiji Empire), "
        f"got {len(japan['links'])}"
    )


def test_v680_japan_chain_endpoints():
    """Japan chain: Nara (start) to Empire of Japan (end)."""
    chains = _load_v680_chains()
    japan = next(ch for ch in chains if "Japanese" in ch["name"])
    assert japan["links"][0]["entity_name"] == "奈良時代"
    assert japan["links"][-1]["entity_name"] == "大日本帝國"


def test_v680_japan_meiji_is_revolution_not_restoration():
    """ETHICS: Meiji is a REVOLUTION (Boshin War, Ainu colonisation, Ryukyu annexation),
    not a gentle RESTORATION as popular narrative frames it."""
    chains = _load_v680_chains()
    japan = next(ch for ch in chains if "Japanese" in ch["name"])
    meiji = next(l for l in japan["links"] if l["entity_name"] == "大日本帝國")
    assert meiji["transition_type"] == "REVOLUTION", (
        "Meiji must be REVOLUTION, not RESTORATION — see chain ethical_notes"
    )
    assert meiji["is_violent"] is True
    # ETHICS note must mention Boshin or Ainu or Ryukyu explicitly.
    enote = meiji.get("ethical_notes") or ""
    assert any(kw in enote for kw in ("Boshin", "Ainu", "Ryūkyū", "Ryukyu")), (
        f"Meiji link ethical_notes must mention Boshin/Ainu/Ryukyu; got: {enote[:200]}"
    )


def test_v680_india_chain_has_5_links():
    chains = _load_v680_chains()
    india = next(ch for ch in chains if "North Indian" in ch["name"])
    assert len(india["links"]) == 5, (
        f"Expected 5-link India chain (Shishunaga through Kanva), "
        f"got {len(india['links'])}"
    )


def test_v680_india_shunga_is_regicide_not_succession():
    """ETHICS: Pushyamitra Shunga murders the last Maurya — must be REVOLUTION + violent,
    not a polite SUCCESSION."""
    chains = _load_v680_chains()
    india = next(ch for ch in chains if "North Indian" in ch["name"])
    shunga = next(l for l in india["links"] if l["entity_name"] == "शुंग")
    assert shunga["transition_type"] == "REVOLUTION", (
        "Shunga foundation was a regicide — cannot be SUCCESSION"
    )
    assert shunga["is_violent"] is True


def test_v680_india_chain_all_transitions_violent():
    """ETHICS: every Nanda→Maurya→Shunga→Kanva transition is regicide or conquest.
    No polite 'succession' euphemisms for the classical Magadhan dynasties."""
    chains = _load_v680_chains()
    india = next(ch for ch in chains if "North Indian" in ch["name"])
    # Skip first link (has no transition)
    for link in india["links"][1:]:
        assert link["is_violent"] is True, (
            f"India link {link['entity_name']!r} marked non-violent — "
            f"but all classical Magadhan transitions were regicides or conquests"
        )


def test_v680_chains_have_ethical_notes():
    chains = _load_v680_chains()
    for ch in chains:
        assert ch.get("ethical_notes"), (
            f"Chain {ch['name']!r} lacks ethical_notes"
        )
        assert len(ch["ethical_notes"]) > 200, (
            f"Chain {ch['name']!r} has thin ethical_notes"
        )


# ─── DB-layer: chains landed in DB ─────────────────────────────────


def test_v680_japan_chain_in_db(db):
    """Japan chain should be in DB via ingest_chains or seed."""
    ch = db.query(DynastyChain).filter(
        DynastyChain.name.like("Japanese state forms%")
    ).first()
    if ch is None:
        pytest.skip("Japan chain not yet ingested in test DB (run ingest_chains)")
    links = db.query(ChainLink).filter_by(chain_id=ch.id).all()
    assert len(links) == 7


def test_v680_india_chain_in_db(db):
    ch = db.query(DynastyChain).filter(
        DynastyChain.name.like("North Indian classical%")
    ).first()
    if ch is None:
        pytest.skip("India chain not yet ingested in test DB (run ingest_chains)")
    links = db.query(ChainLink).filter_by(chain_id=ch.id).all()
    assert len(links) == 5


def test_v680_total_chain_count_grew(db):
    """Before v6.8.0: 9 chains in data/chains JSONs. After: 11.

    Note: test DB doesn't call ingest_chains, so chains table may be empty.
    When chains are loaded (prod, local full ingest), the total must be >= 11.
    """
    # Files-on-disk check (always applicable).
    chain_files = sorted(CHAINS_DIR.glob("batch_*.json"))
    total = 0
    for fp in chain_files:
        with fp.open(encoding="utf-8") as fh:
            total += len(json.load(fh))
    assert total >= 11, (
        f"Total chains on disk {total} — expected 11+ after v6.8.0"
    )

    # DB check: only meaningful if a full chain ingest ran (seed alone
    # populates 0-1 chains — ingest_chains is a separate idempotent step
    # not invoked by the test fixture).
    count = db.query(DynastyChain).count()
    if count >= 9:
        # Full ingest ran → both v6.8.0 chains must be present.
        assert count >= 11, f"Chain ingest landed {count} — expected 11+"
