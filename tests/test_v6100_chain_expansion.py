"""Tests for v6.10.0 chain expansion: Islamic central lands + Korean trunk.

Covers:
  * batch_05_islamic_central_lands.json structure and schema
  * batch_06_korea.json structure
  * 5-link Islamic caliphate chain (Rashidun → Ottoman)
  * 5-link Korean chain (Silla → ROK)
  * ETHICS coverage on both chains (Karbala, Banquet of Abu Futrus,
    1258 Baghdad, 1517 Cairo, Jeju massacre, comfort women, etc.)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.config import DATA_DIR
from src.db.enums import ChainType, TransitionType
from src.db.models import ChainLink, DynastyChain

CHAINS_DIR = Path(DATA_DIR) / "chains"

V6100_ISLAMIC_FILE = CHAINS_DIR / "batch_05_islamic_central_lands.json"
V6100_KOREA_FILE = CHAINS_DIR / "batch_06_korea.json"


def _load_islamic() -> list[dict]:
    with V6100_ISLAMIC_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


def _load_korea() -> list[dict]:
    with V6100_KOREA_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


# ─── file existence + structural tests ─────────────────────────────


def test_v6100_islamic_file_exists():
    assert V6100_ISLAMIC_FILE.exists(), f"Missing: {V6100_ISLAMIC_FILE}"


def test_v6100_korea_file_exists():
    assert V6100_KOREA_FILE.exists(), f"Missing: {V6100_KOREA_FILE}"


def test_v6100_islamic_single_chain():
    chains = _load_islamic()
    assert isinstance(chains, list)
    assert len(chains) == 1


def test_v6100_korea_single_chain():
    chains = _load_korea()
    assert isinstance(chains, list)
    assert len(chains) == 1


@pytest.mark.parametrize("key", [
    "name", "name_lang", "chain_type", "region",
    "description", "confidence_score", "ethical_notes", "links", "sources",
])
def test_v6100_islamic_required_keys(key):
    chain = _load_islamic()[0]
    assert key in chain, f"Islamic chain missing key {key!r}"


@pytest.mark.parametrize("key", [
    "name", "name_lang", "chain_type", "region",
    "description", "confidence_score", "ethical_notes", "links", "sources",
])
def test_v6100_korea_required_keys(key):
    chain = _load_korea()[0]
    assert key in chain, f"Korea chain missing key {key!r}"


def test_v6100_islamic_chain_type_valid():
    valid = {e.value for e in ChainType}
    assert _load_islamic()[0]["chain_type"] in valid


def test_v6100_korea_chain_type_valid():
    valid = {e.value for e in ChainType}
    assert _load_korea()[0]["chain_type"] in valid


def test_v6100_islamic_transitions_valid():
    valid = {e.value for e in TransitionType}
    for link in _load_islamic()[0]["links"]:
        tt = link.get("transition_type")
        if tt is None:
            continue
        assert tt in valid, f"Invalid Islamic transition_type: {tt!r}"


def test_v6100_korea_transitions_valid():
    valid = {e.value for e in TransitionType}
    for link in _load_korea()[0]["links"]:
        tt = link.get("transition_type")
        if tt is None:
            continue
        assert tt in valid, f"Invalid Korea transition_type: {tt!r}"


# ─── link counts + endpoints ───────────────────────────────────────


def test_v6100_islamic_has_5_links():
    chain = _load_islamic()[0]
    assert len(chain["links"]) == 5, (
        f"Expected 5-link Islamic caliphate chain "
        f"(Rashidun → Umayyad → Abbasid → Mamluk → Ottoman), "
        f"got {len(chain['links'])}"
    )


def test_v6100_islamic_endpoints():
    chain = _load_islamic()[0]
    assert chain["links"][0]["entity_name"] == "الخلافة الراشدة"
    assert chain["links"][-1]["entity_name"] == "Osmanlı İmparatorluğu"


def test_v6100_korea_has_5_links():
    chain = _load_korea()[0]
    assert len(chain["links"]) == 5, (
        f"Expected 5-link Korea chain (Silla → Unified Silla → Goryeo "
        f"→ Joseon → ROK), got {len(chain['links'])}"
    )


def test_v6100_korea_endpoints():
    chain = _load_korea()[0]
    assert chain["links"][0]["entity_name"] == "신라"
    assert chain["links"][-1]["entity_name"] == "대한민국"


# ─── ETHICS-specific tests ─────────────────────────────────────────


def test_v6100_islamic_abbasid_is_revolution_not_succession():
    """ETHICS: Abbasid Revolution of 750 ended with the Banquet of Abu Futrus —
    cannot be euphemised as SUCCESSION."""
    chain = _load_islamic()[0]
    abbasid = next(l for l in chain["links"] if l["entity_name"] == "الخلافة العباسية")
    assert abbasid["transition_type"] == "REVOLUTION"
    assert abbasid["is_violent"] is True
    enote = abbasid.get("ethical_notes") or ""
    # Must mention Abu Futrus, Umayyad extermination, or Abd al-Rahman I escape.
    assert any(kw in enote for kw in ("Abu Futrus", "Umayyad", "Abd al-Rahman", "Banquet")), (
        f"Abbasid link ethical_notes must mention Abu Futrus / Umayyad massacre; "
        f"got: {enote[:200]}"
    )


def test_v6100_islamic_umayyad_is_conquest_and_mentions_karbala():
    """ETHICS: First Fitna → Umayyad transition must flag Ali's assassination
    and Karbala (foundational trauma of Shia Islam)."""
    chain = _load_islamic()[0]
    umayyad = next(l for l in chain["links"] if l["entity_name"] == "الدولة الأموية")
    assert umayyad["transition_type"] == "CONQUEST"
    assert umayyad["is_violent"] is True
    enote = umayyad.get("ethical_notes") or ""
    assert any(kw in enote for kw in ("Karbala", "Husayn", "Ashura")), (
        f"Umayyad link ethical_notes must mention Karbala / Husayn / Ashura; "
        f"got: {enote[:200]}"
    )


def test_v6100_islamic_mamluk_mentions_baghdad_sack():
    """ETHICS: 1258 Mongol sack of Baghdad must be flagged in the Mamluk link."""
    chain = _load_islamic()[0]
    mamluk = next(l for l in chain["links"] if l["entity_name"] == "سلطنة المماليك")
    assert mamluk["transition_type"] == "CONQUEST"
    enote = (mamluk.get("ethical_notes") or "") + (mamluk.get("description") or "")
    assert any(kw in enote for kw in ("Hulagu", "Baghdad", "1258", "Musta'sim")), (
        f"Mamluk link must mention Hulagu / Baghdad / 1258 / al-Musta'sim sack; "
        f"got: {enote[:300]}"
    )


def test_v6100_islamic_ottoman_mentions_caliphal_transfer_or_abolition():
    """ETHICS: Ottoman link must flag either 1517 caliphal transfer OR
    1924 Atatürk abolition — both are contested historiographical claims."""
    chain = _load_islamic()[0]
    ott = next(l for l in chain["links"] if l["entity_name"] == "Osmanlı İmparatorluğu")
    enote = (ott.get("ethical_notes") or "") + (ott.get("description") or "")
    assert any(kw in enote for kw in ("al-Mutawakkil", "Atatürk", "1924", "Abdulhamid")), (
        f"Ottoman link must mention caliphal transfer mechanics or 1924 abolition; "
        f"got: {enote[:300]}"
    )


def test_v6100_korea_jeju_massacre_flagged():
    """ETHICS: Jeju 4·3 massacre (~30,000 dead) must be flagged in the partition
    link — officially acknowledged only in 2003."""
    chain = _load_korea()[0]
    rok = next(l for l in chain["links"] if l["entity_name"] == "대한민국")
    assert rok["transition_type"] == "PARTITION"
    assert rok["is_violent"] is True
    enote = (rok.get("ethical_notes") or "") + (rok.get("description") or "")
    assert any(kw in enote for kw in ("Jeju", "제주", "4·3", "Gwangju")), (
        f"ROK link must mention Jeju massacre or Gwangju; "
        f"got: {enote[:300]}"
    )


def test_v6100_korea_colonial_period_acknowledged():
    """ETHICS: the Joseon (1897 end) → ROK (1948 start) gap is 51 years;
    the chain MUST acknowledge Korean Empire + Japanese colonial period."""
    chain = _load_korea()[0]
    enote = chain["ethical_notes"]
    assert "Korean Empire" in enote or "대한제국" in enote or "1897" in enote, (
        "Korea chain ethical_notes must flag the Korean Empire gap"
    )
    assert any(kw in enote for kw in ("colonial", "Japanese", "comfort", "1910")), (
        "Korea chain ethical_notes must flag the 1910-1945 Japanese colonial period"
    )


def test_v6100_korea_goryeo_mentions_mongol_invasions():
    """ETHICS: the Goryeo link spans 1231-1259 Mongol invasions which killed
    hundreds of thousands — must be flagged in the link."""
    chain = _load_korea()[0]
    goryeo = next(l for l in chain["links"] if l["entity_name"] == "고려")
    enote = (goryeo.get("ethical_notes") or "") + (goryeo.get("description") or "")
    assert any(kw in enote for kw in ("Mongol", "gongnyeo", "Khitan", "Tripitaka")), (
        f"Goryeo link must mention Mongol invasions; got: {enote[:300]}"
    )


def test_v6100_both_chains_have_thick_ethical_notes():
    for chain in _load_islamic() + _load_korea():
        assert len(chain["ethical_notes"]) > 400, (
            f"Chain {chain['name']!r} has thin ethical_notes "
            f"({len(chain['ethical_notes'])} chars)"
        )


# ─── DB-layer ──────────────────────────────────────────────────────


def test_v6100_islamic_chain_in_db(db):
    ch = db.query(DynastyChain).filter(
        DynastyChain.name.like("Islamic central lands%")
    ).first()
    if ch is None:
        pytest.skip("Islamic chain not yet ingested in test DB")
    links = db.query(ChainLink).filter_by(chain_id=ch.id).all()
    assert len(links) == 5


def test_v6100_korea_chain_in_db(db):
    ch = db.query(DynastyChain).filter(
        DynastyChain.name.like("Korean state forms%")
    ).first()
    if ch is None:
        pytest.skip("Korea chain not yet ingested in test DB")
    links = db.query(ChainLink).filter_by(chain_id=ch.id).all()
    assert len(links) == 5


def test_v6100_total_chain_count_grew(db):
    """Before v6.10.0: 12 chains on disk. After: 14.

    DB check is soft — test fixture does not run ingest_chains.
    """
    chain_files = sorted(CHAINS_DIR.glob("batch_*.json"))
    total = 0
    for fp in chain_files:
        with fp.open(encoding="utf-8") as fh:
            total += len(json.load(fh))
    assert total >= 14, (
        f"Total chains on disk {total} — expected 14+ after v6.10.0"
    )

    count = db.query(DynastyChain).count()
    if count >= 12:
        # Full ingest ran → both v6.10.0 chains must be present.
        assert count >= 14, f"Chain ingest landed {count} — expected 14+"
