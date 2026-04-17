"""v6.42: tests per /v1/search/fuzzy — token-level matching.

Problema identificato: 'venice' non matchava 'Repubblica di Venezia'
perché SequenceMatcher a livello char su stringhe lunghezza diversa
ritorna ratio basso (~0.3). Fix: tokenize e compute max per-token
similarity — 'venice' vs 'venezia' ~0.77.
"""


def test_fuzzy_venice_finds_venezia(client, db):
    """v6.42 core test: 'venice' deve trovare 'Repubblica di Venezia'."""
    from src.db.models import GeoEntity, NameVariant
    entity = GeoEntity(
        name_original="Repubblica di Venezia",
        name_original_lang="it",
        entity_type="republic",
        year_start=697,
        year_end=1797,
        confidence_score=0.95,
        status="confirmed",
    )
    entity.name_variants.append(
        NameVariant(name="Venezia", lang="it", context="short form")
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)

    r = client.get("/v1/search/fuzzy?q=venice&min_score=0.4")
    assert r.status_code == 200
    data = r.json()
    names = [res["name_original"] for res in data["results"]]
    assert "Repubblica di Venezia" in names, f"not found in {names}"

    db.delete(entity)
    db.commit()


def test_fuzzy_florence_finds_firenze(client, db):
    """Tokenize aiuta anche 'florence' → 'Repubblica di Firenze' via token 'firenze'."""
    from src.db.models import GeoEntity, NameVariant
    entity = GeoEntity(
        name_original="Repubblica di Firenze",
        name_original_lang="it",
        entity_type="republic",
        year_start=1115,
        year_end=1569,
        confidence_score=0.9,
        status="confirmed",
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)

    r = client.get("/v1/search/fuzzy?q=florence&min_score=0.35")
    names = [res["name_original"] for res in r.json()["results"]]
    # 'florence' vs 'firenze' — SequenceMatcher ratio ~0.57, con bonuses > 0.6
    assert "Repubblica di Firenze" in names, f"not found in {names}"

    db.delete(entity)
    db.commit()


def test_fuzzy_byzantine_finds_bisanzio(client, db):
    """Query 'bisanzio' deve trovare 'Byzantine Empire' via token match."""
    from src.db.models import GeoEntity, NameVariant
    entity = GeoEntity(
        name_original="Bisanzio",
        name_original_lang="it",
        entity_type="empire",
        year_start=330,
        year_end=1453,
        confidence_score=0.95,
        status="confirmed",
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)

    # Query con typo/abbrev tollerato
    r = client.get("/v1/search/fuzzy?q=bizantino&min_score=0.3&limit=20")
    names = [res["name_original"] for res in r.json()["results"]]
    # 'bizantino' vs 'bisanzio' tokenized — ratio token-level alto
    assert "Bisanzio" in names, f"not found in {names}"

    db.delete(entity)
    db.commit()


def test_fuzzy_still_respects_min_score(client):
    """Query random 'zzzxyz' non deve matchare niente."""
    r = client.get("/v1/search/fuzzy?q=zzzxyz123&min_score=0.5")
    assert r.status_code == 200
    assert r.json()["count"] == 0
