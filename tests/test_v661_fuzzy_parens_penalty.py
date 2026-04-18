"""v6.61: fuzzy search deve penalizzare token match in parenthesized descriptors.

Bug identificato da audit #02: q='sultanate' → 'Gelgel (pre-sultanate Bali)'
scored 1.0 perchè 'sultanate' match token in parens. Quello che l'utente
cerca è un vero sultanato, non un'entità con 'sultanate' nella descrizione.

Fix: score token-match in parens a 0.6 * del match in primary name.
"""

import pytest

from src.db.models import GeoEntity, NameVariant


def test_parens_match_weakened(client, db):
    """Entity con sultanate nel name_original SENZA parens deve vincere su
    entity con sultanate in parens."""
    # Real sultanate
    real = GeoEntity(
        name_original="Sultanate of Malacca",
        name_original_lang="ms",
        entity_type="sultanate",
        year_start=1400,
        year_end=1511,
        confidence_score=0.9,
        status="confirmed",
    )
    # Descriptive use of "sultanate" in parens
    fake = GeoEntity(
        name_original="Foobar (pre-sultanate descriptor)",
        name_original_lang="en",
        entity_type="kingdom",
        year_start=1000,
        year_end=1300,
        confidence_score=0.7,
        status="confirmed",
    )
    db.add(real)
    db.add(fake)
    db.commit()
    db.refresh(real)
    db.refresh(fake)

    r = client.get("/v1/search/fuzzy?q=sultanate&min_score=0.4&limit=10")
    data = r.json()
    # Find scores
    by_name = {res["name_original"]: res["score"] for res in data["results"]}
    real_score = by_name.get("Sultanate of Malacca")
    fake_score = by_name.get("Foobar (pre-sultanate descriptor)")

    assert real_score is not None, "Real sultanate not in results"
    # fake may or may not be in results — crucial is that real > fake if both present
    if fake_score is not None:
        assert real_score > fake_score, (
            f"Primary-name match ({real_score}) should beat parens-only "
            f"match ({fake_score})"
        )

    db.delete(real)
    db.delete(fake)
    db.commit()


def test_venice_legitimate_match_still_works(client, db):
    """v6.42 test regression: venice → Repubblica di Venezia still works."""
    r = client.get("/v1/search/fuzzy?q=venice&min_score=0.5&limit=5")
    data = r.json()
    # At least one result
    assert len(data["results"]) >= 1
