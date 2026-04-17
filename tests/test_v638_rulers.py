"""v6.38: tests per HistoricalRuler model + /v1/rulers endpoint family."""

import json

import pytest

from src.db.models import HistoricalRuler


# ─── Helpers ─────────────────────────────────────────────────────────

def _insert_test_ruler(
    db,
    name: str = "Wu Zetian",
    name_lang: str = "zh",
    title: str = "empress regnant",
    region: str = "East Asia",
    reign_start: int | None = 690,
    reign_end: int | None = 705,
    birth_year: int | None = 624,
    death_year: int | None = 705,
    entity_name_fallback: str | None = None,
    entity_id: int | None = None,
) -> HistoricalRuler:
    ruler = HistoricalRuler(
        name_original=name,
        name_original_lang=name_lang,
        title=title,
        region=region,
        reign_start=reign_start,
        reign_end=reign_end,
        birth_year=birth_year,
        death_year=death_year,
        entity_name_fallback=entity_name_fallback,
        entity_id=entity_id,
        confidence_score=0.9,
        status="confirmed",
    )
    db.add(ruler)
    db.commit()
    db.refresh(ruler)
    return ruler


def _cleanup(db):
    db.query(HistoricalRuler).delete()
    db.commit()


# ─── Model tests ─────────────────────────────────────────────────────

def test_insert_ruler_roundtrip(db):
    _cleanup(db)
    r = _insert_test_ruler(db, name="Ashoka", name_lang="sa", title="emperor", region="South Asia", reign_start=-268, reign_end=-232)
    assert r.id is not None
    assert r.name_original == "Ashoka"
    _cleanup(db)


def test_birth_before_death_constraint(db):
    """DB check should fail if birth_year > death_year."""
    _cleanup(db)
    with pytest.raises(Exception):
        db.add(HistoricalRuler(
            name_original="Bad",
            name_original_lang="en",
            title="king",
            region="Europe",
            birth_year=1700,
            death_year=1500,  # INVALID
            confidence_score=0.5,
            status="confirmed",
        ))
        db.commit()
    db.rollback()
    _cleanup(db)


def test_reign_order_constraint(db):
    _cleanup(db)
    with pytest.raises(Exception):
        db.add(HistoricalRuler(
            name_original="BadReign",
            name_original_lang="en",
            title="king",
            region="Europe",
            reign_start=1700,
            reign_end=1600,  # INVALID
            confidence_score=0.5,
            status="confirmed",
        ))
        db.commit()
    db.rollback()
    _cleanup(db)


# ─── API endpoint tests ──────────────────────────────────────────────

def test_list_rulers_empty(client, db):
    _cleanup(db)
    r = client.get("/v1/rulers")
    assert r.status_code == 200
    assert r.json()["total"] == 0


def test_list_rulers_with_filter(client, db):
    _cleanup(db)
    _insert_test_ruler(db, name="Wu Zetian", region="East Asia")
    _insert_test_ruler(db, name="Ashoka", region="South Asia", reign_start=-268, reign_end=-232)
    r = client.get("/v1/rulers?region=East+Asia")
    names = [x["name_original"] for x in r.json()["rulers"]]
    assert "Wu Zetian" in names
    assert "Ashoka" not in names
    _cleanup(db)


def test_rulers_at_year(client, db):
    """v6.38: rulers at year — core feature for 'chi regnava nel 700?'"""
    _cleanup(db)
    _insert_test_ruler(db, name="Wu Zetian", reign_start=690, reign_end=705)
    _insert_test_ruler(db, name="Charlemagne", region="Europe", reign_start=768, reign_end=814, birth_year=748, death_year=814)
    r = client.get("/v1/rulers/at-year/700")
    names = [x["name_original"] for x in r.json()["rulers"]]
    assert "Wu Zetian" in names
    assert "Charlemagne" not in names

    r = client.get("/v1/rulers/at-year/800")
    names = [x["name_original"] for x in r.json()["rulers"]]
    assert "Charlemagne" in names
    assert "Wu Zetian" not in names
    _cleanup(db)


def test_rulers_at_year_invalid(client):
    r = client.get("/v1/rulers/at-year/9999")
    assert r.status_code == 400


def test_get_ruler_detail_404(client):
    r = client.get("/v1/rulers/999999")
    assert r.status_code == 404


def test_ruler_with_ethical_notes(client, db):
    """ETHICS-002: violence documented explicitly."""
    _cleanup(db)
    ruler = HistoricalRuler(
        name_original="Leopoldo II",
        name_original_lang="nl",
        title="king",
        region="Europe",
        birth_year=1835,
        death_year=1909,
        reign_start=1865,
        reign_end=1909,
        entity_name_fallback="Belgium / Congo Free State",
        confidence_score=0.98,
        status="confirmed",
        ethical_notes="ETHICS-007: Congo Free State (1885-1908) personal colony responsible for ~10 million Congolese deaths through forced rubber labor, mutilations (hand-cutting policy), famines. Re-labeled by historians as 'Congo genocide' (Hochschild 1998). Despite this, Belgian state monuments remain contested.",
        sources=json.dumps([
            {"citation": "Hochschild, A. (1998). King Leopold's Ghost.", "source_type": "academic"},
        ], ensure_ascii=False),
    )
    db.add(ruler)
    db.commit()
    db.refresh(ruler)
    r = client.get(f"/v1/rulers/{ruler.id}")
    data = r.json()
    assert "Congo genocide" in data["ethical_notes"]
    assert len(data["sources"]) == 1
    _cleanup(db)


def test_ruler_native_script_preserved(client, db):
    """ETHICS-001: name_original in native script."""
    _cleanup(db)
    ruler = HistoricalRuler(
        name_original="武曌",
        name_original_lang="zh",
        name_regnal="則天皇帝",
        title="empress regnant",
        region="East Asia",
        reign_start=690,
        reign_end=705,
        birth_year=624,
        death_year=705,
        confidence_score=0.95,
        status="confirmed",
        name_variants=json.dumps([
            {"name": "Wu Zetian", "lang": "en", "context": "standard pinyin"},
            {"name": "武后", "lang": "zh", "context": "alt. Empress Wu"},
        ], ensure_ascii=False),
    )
    db.add(ruler)
    db.commit()
    db.refresh(ruler)
    r = client.get(f"/v1/rulers/{ruler.id}")
    data = r.json()
    assert data["name_original"] == "武曌"
    assert data["name_regnal"] == "則天皇帝"
    assert data["name_variants"][0]["name"] == "Wu Zetian"
    _cleanup(db)
