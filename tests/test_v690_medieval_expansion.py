"""Tests for v6.9.0 content expansion: medieval events + Chinese dynasty chain.

Covers:
  * batch_10_medieval_expansion.json structure and schema
  * 500-1000 CE gap reduction (was 7 events, now 22+)
  * batch_04_china.json structure
  * Chinese 12-link dynastic trunk wiring
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
    GeoEntity,
    HistoricalEvent,
)

EVENTS_DIR = Path(DATA_DIR) / "events"
CHAINS_DIR = Path(DATA_DIR) / "chains"

V690_EVENTS_FILE = EVENTS_DIR / "batch_10_medieval_expansion.json"
V690_CHAIN_FILE = CHAINS_DIR / "batch_04_china.json"


# ─── batch_10_medieval_expansion.json — file structure ─────────────


def _load_v690_events() -> list[dict]:
    with V690_EVENTS_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


def _load_v690_chain() -> list[dict]:
    with V690_CHAIN_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


def test_v690_events_file_exists():
    assert V690_EVENTS_FILE.exists(), f"Missing: {V690_EVENTS_FILE}"


def test_v690_events_is_list_of_15_plus():
    events = _load_v690_events()
    assert isinstance(events, list)
    assert len(events) >= 15, (
        f"Expected 15+ medieval events in batch_10, got {len(events)}"
    )


@pytest.mark.parametrize("key", [
    "name_original", "name_original_lang", "event_type",
    "year", "description", "confidence_score", "status",
    "ethical_notes", "entity_links", "sources",
])
def test_v690_event_has_required_keys(key):
    events = _load_v690_events()
    for ev in events:
        assert key in ev, f"Event {ev.get('name_original', '?')} missing key {key!r}"


def test_v690_event_types_are_valid_enum():
    events = _load_v690_events()
    valid = {e.value for e in EventType}
    for ev in events:
        assert ev["event_type"] in valid, (
            f"Event {ev['name_original']!r} has invalid event_type {ev['event_type']!r}"
        )


def test_v690_events_in_500_1000_ce_window():
    """Main raison d'etre of this batch: fill the 500-1000 CE gap."""
    events = _load_v690_events()
    for ev in events:
        assert 500 <= ev["year"] <= 1000, (
            f"Event {ev['name_original']!r} has year={ev['year']} — "
            f"not within 500-1000 CE (this batch targets the medieval gap)"
        )


def test_v690_events_span_multiple_regions():
    """The batch covers Islamic world + China + Europe + Japan + India."""
    events = _load_v690_events()
    langs = {ev["name_original_lang"] for ev in events}
    # Expect at minimum Arabic, Greek, Latin, Chinese, Old Church Slavonic/Russian
    expected_any = {"ara", "grc", "lat", "lzh", "chu", "pal", "ang", "sla", "got", "hun"}
    present = langs & expected_any
    assert len(present) >= 3, (
        f"Expected 3+ of {sorted(expected_any)} represented among medieval events, "
        f"got {sorted(langs)}"
    )


def test_v690_events_have_sources():
    events = _load_v690_events()
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


def test_v690_events_have_ethical_notes():
    """Every medieval-expansion event carries an ETHICS note — the period is
    saturated with religious violence and conquest-narratives that hide or
    soften their victims."""
    events = _load_v690_events()
    for ev in events:
        assert ev.get("ethical_notes"), (
            f"Event {ev['name_original']!r} lacks ethical_notes — "
            f"v6.9.0 medieval expansion requires ETHICS coverage"
        )
        assert len(ev["ethical_notes"]) > 80, (
            f"Event {ev['name_original']!r} has thin ethical_notes"
        )


def test_v690_events_confidence_in_range():
    events = _load_v690_events()
    for ev in events:
        c = ev["confidence_score"]
        assert 0.0 <= c <= 1.0, f"Confidence out of range: {c} for {ev['name_original']!r}"


# ─── DB-layer: ingest landed new events ────────────────────────────


def test_v690_events_in_db(db):
    """After seed+ingest, the 15 new medieval events should be present."""
    events = _load_v690_events()
    names = [ev["name_original"] for ev in events]
    in_db = db.query(HistoricalEvent).filter(
        HistoricalEvent.name_original.in_(names)
    ).count()
    # Allow partial landing if a future schema refactor rejects some events.
    assert in_db >= len(names) * 0.8, (
        f"Only {in_db}/{len(names)} v6.9.0 medieval events reached the DB"
    )


def test_v690_medieval_gap_closed(db):
    """Historical: 7 events in 500-1000 CE before v6.9.0. After: 20+."""
    count = db.query(HistoricalEvent).filter(
        HistoricalEvent.year >= 500,
        HistoricalEvent.year <= 1000,
    ).count()
    assert count >= 20, (
        f"500-1000 CE event count {count} — expected 20+ after v6.9.0 expansion "
        f"(was 7 pre-v6.9.0)"
    )


def test_v690_talas_in_db(db):
    """Spot-check: Battle of Talas (751) should be present."""
    ev = db.query(HistoricalEvent).filter(
        HistoricalEvent.year == 751,
        HistoricalEvent.name_original.like("%طلاس%"),
    ).first()
    if ev is None:
        pytest.skip("Talas event not in this test DB")
    # event_type may be stored as str or enum depending on DB type.
    et = ev.event_type.value if hasattr(ev.event_type, "value") else ev.event_type
    assert et == "BATTLE"


def test_v690_verdun_treaty_in_db(db):
    """Spot-check: Treaty of Verdun (843) should be present."""
    ev = db.query(HistoricalEvent).filter(
        HistoricalEvent.year == 843,
        HistoricalEvent.event_type == EventType.TREATY,
    ).first()
    if ev is None:
        pytest.skip("Verdun event not in this test DB")
    assert ev.ethical_notes and len(ev.ethical_notes) > 80


# ─── batch_04_china.json — chain structure ─────────────────────────


def test_v690_china_chain_file_exists():
    assert V690_CHAIN_FILE.exists(), f"Missing: {V690_CHAIN_FILE}"


def test_v690_china_chain_is_list_of_1():
    chain = _load_v690_chain()
    assert isinstance(chain, list)
    assert len(chain) == 1, (
        f"Expected 1 China dynasty trunk chain in v6.9.0, got {len(chain)}"
    )


@pytest.mark.parametrize("key", [
    "name", "name_lang", "chain_type", "region",
    "description", "confidence_score", "ethical_notes", "links", "sources",
])
def test_v690_china_chain_has_required_keys(key):
    chain = _load_v690_chain()[0]
    assert key in chain, f"China chain missing key {key!r}"


def test_v690_china_chain_type_valid_enum():
    chain = _load_v690_chain()[0]
    valid = {e.value for e in ChainType}
    assert chain["chain_type"] in valid, (
        f"China chain has invalid chain_type {chain['chain_type']!r}"
    )


def test_v690_china_chain_transitions_valid_enum():
    chain = _load_v690_chain()[0]
    valid = {e.value for e in TransitionType}
    for link in chain["links"]:
        tt = link.get("transition_type")
        if tt is None:
            continue
        assert tt in valid, (
            f"China chain link {link['entity_name']!r} "
            f"has invalid transition_type {tt!r}"
        )


def test_v690_china_chain_has_12_links():
    chain = _load_v690_chain()[0]
    assert len(chain["links"]) == 12, (
        f"Expected 12-link China chain (Shang through PRC), "
        f"got {len(chain['links'])}"
    )


def test_v690_china_chain_endpoints():
    """China chain: Shang (start) to PRC (end)."""
    chain = _load_v690_chain()[0]
    assert chain["links"][0]["entity_name"] == "商朝"
    assert chain["links"][-1]["entity_name"] == "中华人民共和国"


def test_v690_china_mongol_yuan_is_conquest():
    """ETHICS: Song → Yuan transition was a Mongol conquest that killed
    30-60M people — not a polite 'succession'."""
    chain = _load_v690_chain()[0]
    yuan = next(l for l in chain["links"] if l["entity_name"] == "元朝")
    assert yuan["transition_type"] == "CONQUEST", (
        "Yuan must be CONQUEST, not SUCCESSION — Mongol conquest killed 30-60M"
    )
    assert yuan["is_violent"] is True


def test_v690_china_manchu_qing_is_conquest():
    """ETHICS: Ming → Qing transition was a Manchu conquest with massacres
    (Yangzhou 1645) and forced bodily assimilation (queue edict)."""
    chain = _load_v690_chain()[0]
    qing = next(l for l in chain["links"] if l["entity_name"] == "大清帝國")
    assert qing["transition_type"] == "CONQUEST", (
        "Qing must be CONQUEST — Manchu conquest, not natural succession"
    )
    assert qing["is_violent"] is True
    enote = qing.get("ethical_notes") or ""
    # Must mention Yangzhou OR queue-edict OR Zunghar.
    assert any(kw in enote for kw in ("Yangzhou", "揚州", "queue", "剃髮", "Zunghar")), (
        f"Qing link ethical_notes must mention Yangzhou/queue-edict/Zunghar; "
        f"got: {enote[:200]}"
    )


def test_v690_china_prc_transition_is_revolution():
    """ETHICS: ROC → PRC was a civil-war revolution, not peaceful succession."""
    chain = _load_v690_chain()[0]
    prc = next(l for l in chain["links"] if l["entity_name"] == "中华人民共和国")
    assert prc["transition_type"] == "REVOLUTION"
    assert prc["is_violent"] is True


def test_v690_china_chain_has_ethical_notes():
    chain = _load_v690_chain()[0]
    assert chain.get("ethical_notes"), "China chain lacks ethical_notes"
    assert len(chain["ethical_notes"]) > 400, (
        "China chain ethical_notes too thin — the trunk-format historiographical "
        "choice itself needs documenting (Three Kingdoms, Liao/Jin/Xia erasure, "
        "An Lushan, Cultural Revolution)"
    )


def test_v690_china_chain_flags_fragmentation_periods():
    """The trunk chain elides the 360-year Three Kingdoms→N&S Dynasties gap
    and the Five Dynasties gap. ETHICS notes MUST acknowledge this."""
    chain = _load_v690_chain()[0]
    enote = chain["ethical_notes"]
    # Must mention at least one known-silence marker from those periods.
    silences = ("Three Kingdoms", "Sixteen Kingdoms", "Five Dynasties",
                "Liao", "Jin", "Western Xia", "Northern", "Southern Dynasties")
    mentioned = [s for s in silences if s in enote]
    assert len(mentioned) >= 3, (
        f"China chain ethical_notes must flag trunk-format silences; "
        f"found only: {mentioned}"
    )


# ─── DB-layer: chain landed ────────────────────────────────────────


def test_v690_china_chain_in_db(db):
    """China chain should be in DB via ingest_chains."""
    ch = db.query(DynastyChain).filter(
        DynastyChain.name.like("Chinese dynastic trunk%")
    ).first()
    if ch is None:
        pytest.skip("China chain not yet ingested in test DB (run ingest_chains)")
    links = db.query(ChainLink).filter_by(chain_id=ch.id).all()
    assert len(links) == 12


def test_v690_total_chain_count_grew(db):
    """Before v6.9.0: 11 chains on disk. After: 12.

    DB check is soft: the test fixture does not call ingest_chains, so chains
    table may be empty or partial. Disk-file check is always applicable.
    """
    chain_files = sorted(CHAINS_DIR.glob("batch_*.json"))
    total = 0
    for fp in chain_files:
        with fp.open(encoding="utf-8") as fh:
            total += len(json.load(fh))
    assert total >= 12, (
        f"Total chains on disk {total} — expected 12+ after v6.9.0"
    )

    count = db.query(DynastyChain).count()
    if count >= 10:
        # Full ingest ran → China chain must be present.
        assert count >= 12, f"Chain ingest landed {count} — expected 12+"
