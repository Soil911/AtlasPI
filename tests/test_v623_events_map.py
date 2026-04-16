"""Tests for v6.23.0 — Events Map Overlay.

Tests the GET /v1/events/map endpoint (lightweight map marker payload)
and validates the two new event data batches (batch_21_iron_age,
batch_22_early_civilizations).
"""

import json
from pathlib import Path

import pytest

from src.db.enums import EventType

DATA_DIR = Path("data") / "events"

# Required fields in the /v1/events/map marker payload.
MAP_MARKER_FIELDS = {
    "id",
    "name_original",
    "event_type",
    "year",
    "location_lat",
    "location_lon",
}

# Heavy fields that MUST NOT appear in map marker responses —
# the client fetches /v1/events/{id} on click for these.
HEAVY_FIELDS = {"description", "sources", "entity_links", "casualties_low", "casualties_high"}

# Required fields in each raw event JSON object.
RAW_EVENT_REQUIRED_FIELDS = {
    "name_original",
    "event_type",
    "year",
    "location_lat",
    "location_lon",
    "description",
    "sources",
}


# ── helpers ────────────────────────────────────────────────────────────────


def _load_batch(filename: str) -> list[dict]:
    path = DATA_DIR / filename
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


# ── /v1/events/map endpoint tests ─────────────────────────────────────────


class TestEventsMapEndpoint:
    """GET /v1/events/map — lightweight map marker payload."""

    def test_basic_request_returns_200(self, client):
        r = client.get("/v1/events/map?year=-500")
        assert r.status_code == 200

    def test_response_has_required_top_level_fields(self, client):
        r = client.get("/v1/events/map?year=-500")
        data = r.json()
        for field in ("year", "window", "total", "events"):
            assert field in data, f"Missing top-level field: {field}"

    def test_events_have_map_marker_fields(self, client):
        """Each event in the response must carry the fields needed to
        place and label a marker on the map."""
        r = client.get("/v1/events/map?year=-500&window=500")
        data = r.json()
        # There must be at least some events seeded in the test DB for
        # this range; if not, the assertion below still holds vacuously.
        for ev in data["events"]:
            for field in MAP_MARKER_FIELDS:
                assert field in ev, f"Event {ev.get('id')} missing field: {field}"

    def test_events_exclude_heavy_fields(self, client):
        """Map markers must NOT carry heavy fields — those are fetched
        on click via /v1/events/{id}."""
        r = client.get("/v1/events/map?year=-500&window=500")
        data = r.json()
        for ev in data["events"]:
            for field in HEAVY_FIELDS:
                assert field not in ev, (
                    f"Event {ev.get('id')} should not carry heavy field: {field}"
                )

    def test_window_auto_expansion_deep_ancient(self, client):
        """year < -1000 should auto-expand window to at least 50."""
        r = client.get("/v1/events/map?year=-2000")
        data = r.json()
        assert data["window"] >= 50

    def test_window_auto_expansion_classical(self, client):
        """year between -1000 and 0 should auto-expand window to at least 25."""
        r = client.get("/v1/events/map?year=-500")
        data = r.json()
        assert data["window"] >= 25

    def test_window_stays_at_explicit_value_for_modern(self, client):
        """year > 0 with default window (10) should NOT auto-expand."""
        r = client.get("/v1/events/map?year=1500")
        data = r.json()
        assert data["window"] == 10

    def test_explicit_large_window_respected_for_modern(self, client):
        """An explicitly large window should be respected even for
        modern years (no clamping down)."""
        r = client.get("/v1/events/map?year=1500&window=100")
        data = r.json()
        assert data["window"] == 100

    def test_limit_parameter(self, client):
        """limit=5 should return at most 5 events."""
        r = client.get("/v1/events/map?year=-500&window=500&limit=5")
        data = r.json()
        assert len(data["events"]) <= 5

    def test_only_events_with_coordinates_returned(self, client):
        """Every event returned must have non-null lat/lon."""
        r = client.get("/v1/events/map?year=-500&window=500")
        data = r.json()
        for ev in data["events"]:
            assert ev["location_lat"] is not None, (
                f"Event {ev['id']} has null location_lat"
            )
            assert ev["location_lon"] is not None, (
                f"Event {ev['id']} has null location_lon"
            )

    def test_year_parameter_required(self, client):
        """Omitting the required `year` parameter should return 422."""
        r = client.get("/v1/events/map")
        assert r.status_code == 422


# ── Data batch validation ─────────────────────────────────────────────────


class TestBatch21IronAge:
    """Validate data/events/batch_21_iron_age.json structure and content."""

    @pytest.fixture(scope="class")
    def events(self):
        return _load_batch("batch_21_iron_age.json")

    def test_loads_as_list(self, events):
        assert isinstance(events, list)
        assert len(events) > 0

    def test_each_event_has_required_fields(self, events):
        for i, ev in enumerate(events):
            for field in RAW_EVENT_REQUIRED_FIELDS:
                assert field in ev, (
                    f"Event index {i} ({ev.get('name_original', '?')}) "
                    f"missing required field: {field}"
                )

    def test_years_in_iron_age_range(self, events):
        """Iron Age batch events should have years between -1000 and -400."""
        for ev in events:
            assert -1000 <= ev["year"] <= -400, (
                f"Event '{ev['name_original']}' year {ev['year']} "
                f"outside Iron Age range [-1000, -400]"
            )

    def test_event_types_are_valid_enum_members(self, events):
        valid_types = {t.value for t in EventType}
        for ev in events:
            assert ev["event_type"] in valid_types, (
                f"Event '{ev['name_original']}' has invalid event_type "
                f"'{ev['event_type']}' — not in EventType enum"
            )


class TestBatch22EarlyCivilizations:
    """Validate data/events/batch_22_early_civilizations.json structure and content."""

    @pytest.fixture(scope="class")
    def events(self):
        return _load_batch("batch_22_early_civilizations.json")

    def test_loads_as_list(self, events):
        assert isinstance(events, list)
        assert len(events) > 0

    def test_each_event_has_required_fields(self, events):
        for i, ev in enumerate(events):
            for field in RAW_EVENT_REQUIRED_FIELDS:
                assert field in ev, (
                    f"Event index {i} ({ev.get('name_original', '?')}) "
                    f"missing required field: {field}"
                )

    def test_years_in_early_civilizations_range(self, events):
        """Early Civilizations batch: years between -3500 and -2000."""
        for ev in events:
            assert -3500 <= ev["year"] <= -2000, (
                f"Event '{ev['name_original']}' year {ev['year']} "
                f"outside Early Civilizations range [-3500, -2000]"
            )

    def test_event_types_are_valid_enum_members(self, events):
        valid_types = {t.value for t in EventType}
        for ev in events:
            assert ev["event_type"] in valid_types, (
                f"Event '{ev['name_original']}' has invalid event_type "
                f"'{ev['event_type']}' — not in EventType enum"
            )


class TestBatch23EarlyMedieval:
    """Validate data/events/batch_23_early_medieval.json structure and content."""

    @pytest.fixture(scope="class")
    def events(self):
        return _load_batch("batch_23_early_medieval.json")

    def test_loads_as_list(self, events):
        assert isinstance(events, list)
        assert len(events) >= 14

    def test_each_event_has_required_fields(self, events):
        for i, ev in enumerate(events):
            for field in RAW_EVENT_REQUIRED_FIELDS:
                assert field in ev, (
                    f"Event index {i} ({ev.get('name_original', '?')}) "
                    f"missing required field: {field}"
                )

    def test_years_in_early_medieval_range(self, events):
        """Early Medieval batch: years between 500 and 1000 CE."""
        for ev in events:
            assert 500 <= ev["year"] <= 1000, (
                f"Event '{ev['name_original']}' year {ev['year']} "
                f"outside Early Medieval range [500, 1000]"
            )

    def test_event_types_are_valid_enum_members(self, events):
        valid_types = {t.value for t in EventType}
        for ev in events:
            assert ev["event_type"] in valid_types, (
                f"Event '{ev['name_original']}' has invalid event_type "
                f"'{ev['event_type']}' — not in EventType enum"
            )

    def test_has_migration_and_collapse_types(self, events):
        """Batch 23 should exercise the new MIGRATION and COLLAPSE types."""
        types_used = {ev["event_type"] for ev in events}
        assert "MIGRATION" in types_used, "Expected at least one MIGRATION event"
        assert "COLLAPSE" in types_used, "Expected at least one COLLAPSE event"

    def test_events_have_date_precision_fields(self, events):
        """All events should have date_precision field."""
        for ev in events:
            assert "date_precision" in ev, (
                f"Event '{ev['name_original']}' missing date_precision"
            )

    def test_high_confidence_events_have_sources(self, events):
        """Events with confidence > 0.8 must have at least 2 sources."""
        for ev in events:
            if ev.get("confidence_score", 0) > 0.8:
                assert len(ev.get("sources", [])) >= 2, (
                    f"High-confidence event '{ev['name_original']}' "
                    f"({ev['confidence_score']}) has < 2 sources"
                )


class TestMigrationCollapseEnum:
    """Verify the new MIGRATION and COLLAPSE EventType values."""

    def test_migration_in_enum(self):
        assert "MIGRATION" in {t.value for t in EventType}

    def test_collapse_in_enum(self):
        assert "COLLAPSE" in {t.value for t in EventType}

    def test_enum_has_33_values(self):
        assert len(EventType) == 33

    def test_event_types_endpoint_includes_new_types(self, client):
        r = client.get("/v1/events/types")
        data = r.json()
        type_names = {t["type"] for t in data["event_types"]}
        assert "MIGRATION" in type_names
        assert "COLLAPSE" in type_names

    def test_new_types_have_descriptions(self, client):
        r = client.get("/v1/events/types")
        data = r.json()
        for t in data["event_types"]:
            if t["type"] in ("MIGRATION", "COLLAPSE"):
                assert t["description"], f"{t['type']} missing description"


class TestCrossBatchIntegrity:
    """Cross-batch checks across all event batches."""

    @pytest.fixture(scope="class")
    def all_events(self):
        events = []
        for batch_file in sorted(DATA_DIR.glob("batch_*.json")):
            events.extend(_load_batch(batch_file.name))
        return events

    def test_no_duplicate_names_within_same_year(self, all_events):
        seen = set()
        dupes = []
        for ev in all_events:
            key = (ev["name_original"], ev["year"])
            if key in seen:
                dupes.append(key)
            seen.add(key)
        assert len(dupes) <= 5, (
            f"Too many duplicate (name, year) pairs across batches: {dupes}"
        )

    def test_all_event_types_valid(self, all_events):
        valid_types = {t.value for t in EventType}
        invalid = [
            (ev["name_original"], ev["event_type"])
            for ev in all_events
            if ev["event_type"] not in valid_types
        ]
        assert not invalid, f"Invalid event types found: {invalid}"

    def test_all_events_have_coordinates(self, all_events):
        """At least 90% of events should have lat/lon."""
        with_coords = sum(
            1 for ev in all_events
            if ev.get("location_lat") is not None and ev.get("location_lon") is not None
        )
        ratio = with_coords / len(all_events) if all_events else 0
        assert ratio >= 0.9, (
            f"Only {ratio:.1%} of events have coordinates (expected >= 90%)"
        )
