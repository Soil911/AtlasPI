"""Test per content expansion v6.13.0 — Persian / Indian subcontinent.

Verifica:
- 4 nuove entita' (Achaemenid, Delhi Sultanate, Mughal, Pakistan)
- 2 nuove catene (Persian deep trunk, Indian medieval trunk)
- 8 nuovi eventi (Gaugamela, Hormozdgan, al-Qadisiyyah, etc.)
- Integrita' dei link catena-entita'
- Qualita' dei metadati etici
"""

import json

import pytest

from src.db.database import SessionLocal
from src.db.models import (
    ChainLink,
    DynastyChain,
    GeoEntity,
    HistoricalEvent,
    NameVariant,
    Source,
    TerritoryChange,
)


@pytest.fixture()
def db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


# ─── Nuove entita' ────────────────────────────────────────────────────

class TestNewEntities:
    """Verifica le 4 nuove entita' v6.13.0."""

    def test_total_entities_at_least_850(self, db):
        assert db.query(GeoEntity).count() >= 850

    def test_achaemenid_exists(self, db):
        e = db.query(GeoEntity).filter(
            GeoEntity.name_original == "\u0647\u062e\u0627\u0645\u0646\u0634\u06cc\u0627\u0646"
        ).first()
        assert e is not None, "Achaemenid Empire not found"
        assert e.entity_type == "empire"
        assert e.year_start == -550
        assert e.year_end == -330
        assert e.capital_name == "Persepolis"
        # v6.30: confidence may be slightly lowered if aourednik fuzzy-matching
        # produced a simplified boundary. 0.7+ is still well-sourced.
        assert e.confidence_score >= 0.7

    def test_delhi_sultanate_exists(self, db):
        e = db.query(GeoEntity).filter(
            GeoEntity.name_original == "\u0633\u0644\u0637\u0646\u062a \u062f\u06c1\u0644\u06cc"
        ).first()
        assert e is not None, "Delhi Sultanate not found"
        assert e.entity_type == "sultanate"
        assert e.year_start == 1206
        assert e.year_end == 1526

    def test_mughal_exists(self, db):
        e = db.query(GeoEntity).filter(
            GeoEntity.name_original == "\u0633\u0644\u0637\u0646\u062a \u0645\u063a\u0644\u06cc\u06c1"
        ).first()
        assert e is not None, "Mughal Empire not found"
        assert e.entity_type == "empire"
        assert e.year_start == 1526
        assert e.year_end == 1857

    def test_pakistan_exists(self, db):
        e = db.query(GeoEntity).filter(
            GeoEntity.name_original == "\u0627\u0633\u0644\u0627\u0645\u06cc \u062c\u0645\u06c1\u0648\u0631\u06cc\u06c2 \u067e\u0627\u06a9\u0633\u062a\u0627\u0646"
        ).first()
        assert e is not None, "Pakistan not found"
        assert e.entity_type == "republic"
        assert e.year_start == 1947
        assert e.year_end is None  # ongoing

    def test_new_entities_have_boundary_geojson(self, db):
        """Tutte le nuove entita' devono avere confini GeoJSON.

        v6.30: accept both Polygon and MultiPolygon (aourednik provides
        MultiPolygon for territorially complex empires like Achaemenid).
        """
        names = [
            "\u0647\u062e\u0627\u0645\u0646\u0634\u06cc\u0627\u0646",
            "\u0633\u0644\u0637\u0646\u062a \u062f\u06c1\u0644\u06cc",
            "\u0633\u0644\u0637\u0646\u062a \u0645\u063a\u0644\u06cc\u06c1",
            "\u0627\u0633\u0644\u0627\u0645\u06cc \u062c\u0645\u06c1\u0648\u0631\u06cc\u06c2 \u067e\u0627\u06a9\u0633\u062a\u0627\u0646",
        ]
        for name in names:
            e = db.query(GeoEntity).filter(GeoEntity.name_original == name).first()
            assert e is not None, f"Entity {name} not found"
            assert e.boundary_geojson is not None, f"No boundary for {name}"
            geo = json.loads(e.boundary_geojson)
            assert geo["type"] in ("Polygon", "MultiPolygon")
            # For Polygon: check the outer ring
            # For MultiPolygon: check total vertices across all polygons
            if geo["type"] == "Polygon":
                vertex_count = len(geo["coordinates"][0])
            else:
                vertex_count = sum(
                    len(poly[0]) for poly in geo["coordinates"]
                )
            assert vertex_count >= 10

    def test_new_entities_have_ethical_notes(self, db):
        """ETHICS: ogni nuova entita' deve avere ethical_notes."""
        names = [
            "\u0647\u062e\u0627\u0645\u0646\u0634\u06cc\u0627\u0646",
            "\u0633\u0644\u0637\u0646\u062a \u062f\u06c1\u0644\u06cc",
            "\u0633\u0644\u0637\u0646\u062a \u0645\u063a\u0644\u06cc\u06c1",
            "\u0627\u0633\u0644\u0627\u0645\u06cc \u062c\u0645\u06c1\u0648\u0631\u06cc\u06c2 \u067e\u0627\u06a9\u0633\u062a\u0627\u0646",
        ]
        for name in names:
            e = db.query(GeoEntity).filter(GeoEntity.name_original == name).first()
            assert e.ethical_notes, f"No ethical_notes for {name}"
            assert len(e.ethical_notes) > 100, f"Ethical notes too brief for {name}"


# ─── Varianti di nome ─────────────────────────────────────────────────

class TestNameVariants:
    """Verifica varianti di nome per le nuove entita'."""

    def test_achaemenid_has_english_variant(self, db):
        e = db.query(GeoEntity).filter(
            GeoEntity.name_original == "\u0647\u062e\u0627\u0645\u0646\u0634\u06cc\u0627\u0646"
        ).first()
        variants = {v.name for v in e.name_variants}
        assert "Achaemenid Empire" in variants

    def test_delhi_sultanate_has_english_variant(self, db):
        e = db.query(GeoEntity).filter(
            GeoEntity.name_original == "\u0633\u0644\u0637\u0646\u062a \u062f\u06c1\u0644\u06cc"
        ).first()
        variants = {v.name for v in e.name_variants}
        assert "Delhi Sultanate" in variants

    def test_mughal_has_multiple_variants(self, db):
        e = db.query(GeoEntity).filter(
            GeoEntity.name_original == "\u0633\u0644\u0637\u0646\u062a \u0645\u063a\u0644\u06cc\u06c1"
        ).first()
        assert len(e.name_variants) >= 3

    def test_pakistan_has_english_variant(self, db):
        e = db.query(GeoEntity).filter(
            GeoEntity.name_original == "\u0627\u0633\u0644\u0627\u0645\u06cc \u062c\u0645\u06c1\u0648\u0631\u06cc\u06c2 \u067e\u0627\u06a9\u0633\u062a\u0627\u0646"
        ).first()
        variants = {v.name for v in e.name_variants}
        assert "Islamic Republic of Pakistan" in variants


# ─── Territory changes ─────────────────────────────────────────────────

class TestTerritoryChanges:
    """Verifica territory changes delle nuove entita'."""

    def test_achaemenid_has_changes(self, db):
        e = db.query(GeoEntity).filter(
            GeoEntity.name_original == "\u0647\u062e\u0627\u0645\u0646\u0634\u06cc\u0627\u0646"
        ).first()
        assert len(e.territory_changes) >= 3
        # Conquest of Babylonia
        years = {tc.year for tc in e.territory_changes}
        assert -539 in years, "Missing conquest of Babylon"

    def test_mughal_has_changes(self, db):
        e = db.query(GeoEntity).filter(
            GeoEntity.name_original == "\u0633\u0644\u0637\u0646\u062a \u0645\u063a\u0644\u06cc\u06c1"
        ).first()
        assert len(e.territory_changes) >= 4
        years = {tc.year for tc in e.territory_changes}
        assert 1526 in years, "Missing Panipat formation"
        assert 1857 in years, "Missing 1857 dissolution"

    def test_delhi_sultanate_has_timur_sack(self, db):
        e = db.query(GeoEntity).filter(
            GeoEntity.name_original == "\u0633\u0644\u0637\u0646\u062a \u062f\u06c1\u0644\u06cc"
        ).first()
        years = {tc.year for tc in e.territory_changes}
        assert 1398 in years, "Missing Timur's sack of Delhi"


# ─── Catene (chains) ──────────────────────────────────────────────────

class TestNewChains:
    """Verifica le 2 nuove catene v6.13.0."""

    def test_total_chains_at_least_19(self, db):
        assert db.query(DynastyChain).count() >= 19

    def test_persian_deep_trunk_exists(self, db):
        chain = db.query(DynastyChain).filter(
            DynastyChain.name.like("%Iranian state-formation trunk%")
        ).first()
        assert chain is not None, "Persian deep trunk chain not found"
        assert chain.chain_type == "SUCCESSION"
        links = db.query(ChainLink).filter(ChainLink.chain_id == chain.id).all()
        assert len(links) == 6, f"Expected 6 links, got {len(links)}"

    def test_persian_chain_starts_with_achaemenid(self, db):
        chain = db.query(DynastyChain).filter(
            DynastyChain.name.like("%Iranian state-formation trunk%")
        ).first()
        first_link = db.query(ChainLink).filter(
            ChainLink.chain_id == chain.id,
            ChainLink.sequence_order == 0,
        ).first()
        entity = db.query(GeoEntity).filter(GeoEntity.id == first_link.entity_id).first()
        assert entity.name_original == "\u0647\u062e\u0627\u0645\u0646\u0634\u06cc\u0627\u0646"

    def test_persian_chain_ends_with_islamic_republic(self, db):
        chain = db.query(DynastyChain).filter(
            DynastyChain.name.like("%Iranian state-formation trunk%")
        ).first()
        last_link = db.query(ChainLink).filter(
            ChainLink.chain_id == chain.id,
            ChainLink.sequence_order == 5,
        ).first()
        entity = db.query(GeoEntity).filter(GeoEntity.id == last_link.entity_id).first()
        assert entity.name_original == "\u062c\u0645\u0647\u0648\u0631\u06cc \u0627\u0633\u0644\u0627\u0645\u06cc \u0627\u06cc\u0631\u0627\u0646"

    def test_indian_medieval_trunk_exists(self, db):
        chain = db.query(DynastyChain).filter(
            DynastyChain.name.like("%Indian subcontinent paramount%")
        ).first()
        assert chain is not None, "Indian medieval trunk chain not found"
        assert chain.chain_type == "SUCCESSION"
        links = db.query(ChainLink).filter(ChainLink.chain_id == chain.id).all()
        assert len(links) == 4, f"Expected 4 links, got {len(links)}"

    def test_indian_chain_has_mughal_to_raj_transition(self, db):
        chain = db.query(DynastyChain).filter(
            DynastyChain.name.like("%Indian subcontinent paramount%")
        ).first()
        # Mughal is link 1 (seq_order 1), British Raj is link 2 (seq_order 2)
        raj_link = db.query(ChainLink).filter(
            ChainLink.chain_id == chain.id,
            ChainLink.sequence_order == 2,
        ).first()
        assert raj_link.transition_year == 1858
        assert raj_link.transition_type == "CONQUEST"
        assert raj_link.is_violent is True

    def test_indian_chain_ends_with_decolonization(self, db):
        chain = db.query(DynastyChain).filter(
            DynastyChain.name.like("%Indian subcontinent paramount%")
        ).first()
        last_link = db.query(ChainLink).filter(
            ChainLink.chain_id == chain.id,
            ChainLink.sequence_order == 3,
        ).first()
        assert last_link.transition_year == 1947
        assert last_link.transition_type == "DECOLONIZATION"

    def test_chain_ethical_notes_present(self, db):
        """ETHICS: both new chains must have substantive ethical_notes."""
        for pattern in ["%Iranian state-formation%", "%Indian subcontinent%"]:
            chain = db.query(DynastyChain).filter(
                DynastyChain.name.like(pattern)
            ).first()
            assert chain.ethical_notes, f"No ethical_notes on chain {chain.name[:40]}"
            assert len(chain.ethical_notes) > 100


# ─── Nuovi eventi ─────────────────────────────────────────────────────

class TestNewEvents:
    """Verifica i nuovi eventi v6.13.0."""

    def test_total_events_at_least_267(self, db):
        assert db.query(HistoricalEvent).count() >= 267

    def test_gaugamela_exists(self, db):
        e = db.query(HistoricalEvent).filter(
            HistoricalEvent.year == -331,
            HistoricalEvent.event_type == "BATTLE",
        ).first()
        assert e is not None, "Battle of Gaugamela not found"
        assert e.location_name is not None
        assert "Gaugamela" in e.location_name or "Mosul" in e.location_name

    def test_hormozdgan_exists(self, db):
        e = db.query(HistoricalEvent).filter(
            HistoricalEvent.year == 224,
            HistoricalEvent.event_type == "BATTLE",
        ).first()
        assert e is not None, "Battle of Hormozdgan not found"

    def test_al_qadisiyyah_exists(self, db):
        e = db.query(HistoricalEvent).filter(
            HistoricalEvent.year == 636,
            HistoricalEvent.event_type == "CONQUEST",
        ).first()
        assert e is not None, "Battle of al-Qadisiyyah not found"

    def test_third_panipat_exists(self, db):
        e = db.query(HistoricalEvent).filter(
            HistoricalEvent.year == 1761,
            HistoricalEvent.event_type == "BATTLE",
        ).first()
        assert e is not None, "Third Battle of Panipat not found"

    def test_jallianwala_bagh_exists(self, db):
        e = db.query(HistoricalEvent).filter(
            HistoricalEvent.year == 1919,
            HistoricalEvent.event_type == "MASSACRE",
        ).first()
        assert e is not None, "Jallianwala Bagh massacre not found"
        assert e.casualties_low is not None
        assert e.casualties_low >= 300

    def test_iranian_revolution_exists(self, db):
        e = db.query(HistoricalEvent).filter(
            HistoricalEvent.year == 1979,
            HistoricalEvent.event_type == "REVOLUTION",
        ).first()
        assert e is not None, "Iranian Revolution not found"

    def test_events_have_ethical_notes(self, db):
        """ETHICS: tutti i nuovi eventi devono avere ethical_notes."""
        for year in [-331, 224, 636, 1565, 1761, 1919, 1979]:
            e = db.query(HistoricalEvent).filter(
                HistoricalEvent.year == year,
            ).first()
            if e:
                assert e.ethical_notes, f"No ethical_notes on event year={year}"

    def test_delhi_durbar_during_famine(self, db):
        """ETHICS: il Delhi Durbar 1877 deve menzionare la carestia."""
        e = db.query(HistoricalEvent).filter(
            HistoricalEvent.year == 1877,
            HistoricalEvent.event_type == "CORONATION",
        ).first()
        assert e is not None, "Delhi Durbar 1877 not found"
        assert "famine" in e.ethical_notes.lower() or "carestia" in e.ethical_notes.lower()


# ─── Alembic migration files ──────────────────────────────────────────

class TestDataFiles:
    """Verifica che i file JSON delle nuove entita' esistano."""

    def test_batch_25_exists(self):
        import os
        assert os.path.exists("data/entities/batch_25_persian_iranian_entities.json")

    def test_batch_26_exists(self):
        import os
        assert os.path.exists("data/entities/batch_26_indian_subcontinent_entities.json")

    def test_persian_chain_file_exists(self):
        import os
        assert os.path.exists("data/chains/batch_10_persian_deep_trunk.json")

    def test_indian_chain_file_exists(self):
        import os
        assert os.path.exists("data/chains/batch_11_indian_medieval_trunk.json")

    def test_events_file_exists(self):
        import os
        assert os.path.exists("data/events/batch_12_persian_indian_events.json")

    def test_json_files_valid(self):
        """Verifica che tutti i nuovi file JSON siano validi."""
        import json
        files = [
            "data/entities/batch_25_persian_iranian_entities.json",
            "data/entities/batch_26_indian_subcontinent_entities.json",
            "data/chains/batch_10_persian_deep_trunk.json",
            "data/chains/batch_11_indian_medieval_trunk.json",
            "data/events/batch_12_persian_indian_events.json",
        ]
        for f in files:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
            assert isinstance(data, list), f"{f} is not a JSON array"
            assert len(data) >= 1, f"{f} is empty"


# ─── API endpoint verification ─────────────────────────────────────────

class TestAPIEndpoints:
    """Verifica che le nuove entita' siano accessibili via API."""

    def test_achaemenid_in_search(self, client):
        r = client.get("/v1/entities?search=Achaemenid")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] >= 1

    def test_mughal_in_search(self, client):
        r = client.get("/v1/entities?search=Mughal")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] >= 1

    def test_chains_endpoint_includes_new(self, client):
        r = client.get("/v1/chains")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 19

    def test_stats_reflects_850_plus(self, client):
        r = client.get("/v1/stats")
        assert r.status_code == 200
        data = r.json()
        assert data["total_entities"] >= 850
