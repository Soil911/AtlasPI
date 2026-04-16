"""Test per v6.14.0 — Date Precision Layer.

Verifica:
- DatePrecision enum
- Nuove colonne su HistoricalEvent e TerritoryChange
- Filtri month/day su GET /v1/events
- Endpoint GET /v1/events/on-this-day/{mm_dd}
- Endpoint GET /v1/events/at-date/{date_str}
- Backward compatibility (eventi senza month/day)
- Constraint validation (month/day fuori range)
- Script extract_date_from_description()
"""

import pytest
from sqlalchemy.exc import IntegrityError

from src.db.enums import DatePrecision
from src.db.models import HistoricalEvent, TerritoryChange


# ─── DatePrecision Enum ────────────────────────────────────────────────────


class TestDatePrecisionEnum:
    def test_enum_has_six_values(self):
        values = [e.value for e in DatePrecision]
        assert len(values) == 6
        assert "DAY" in values
        assert "MONTH" in values
        assert "SEASON" in values
        assert "YEAR" in values
        assert "DECADE" in values
        assert "CENTURY" in values

    def test_enum_is_str(self):
        assert isinstance(DatePrecision.DAY, str)
        assert DatePrecision.DAY == "DAY"


# ─── Model columns ────────────────────────────────────────────────────────


class TestModelColumns:
    def test_event_has_date_precision_columns(self, db):
        """HistoricalEvent has the 5 new nullable columns."""
        event = db.query(HistoricalEvent).first()
        assert event is not None
        # All new columns should exist (may be None on old data).
        assert hasattr(event, "month")
        assert hasattr(event, "day")
        assert hasattr(event, "date_precision")
        assert hasattr(event, "iso_date")
        assert hasattr(event, "calendar_note")

    def test_territory_change_has_date_precision_columns(self, db):
        """TerritoryChange has the 5 new nullable columns."""
        tc = db.query(TerritoryChange).first()
        if tc is None:
            pytest.skip("No territory changes in test DB")
        assert hasattr(tc, "month")
        assert hasattr(tc, "day")
        assert hasattr(tc, "date_precision")
        assert hasattr(tc, "iso_date")
        assert hasattr(tc, "calendar_note")

    def test_event_roundtrip_with_full_date(self, db):
        """Can create an event with all date precision fields."""
        event = HistoricalEvent(
            name_original="Test Date Precision Event",
            name_original_lang="en",
            event_type="BATTLE",
            year=1789,
            month=7,
            day=14,
            date_precision="DAY",
            iso_date="1789-07-14",
            calendar_note=None,
            description="Test event for date precision.",
            confidence_score=0.9,
            status="confirmed",
        )
        db.add(event)
        db.flush()

        loaded = db.query(HistoricalEvent).filter(
            HistoricalEvent.name_original == "Test Date Precision Event"
        ).first()
        assert loaded is not None
        assert loaded.month == 7
        assert loaded.day == 14
        assert loaded.date_precision == "DAY"
        assert loaded.iso_date == "1789-07-14"
        assert loaded.calendar_note is None

        # Cleanup.
        db.delete(loaded)
        db.flush()

    def test_event_nullable_month_day(self, db):
        """Events without month/day work fine (backward compatible)."""
        event = HistoricalEvent(
            name_original="Test No Date Event",
            name_original_lang="en",
            event_type="OTHER",
            year=1500,
            description="No sub-annual date.",
            confidence_score=0.5,
            status="confirmed",
        )
        db.add(event)
        db.flush()

        loaded = db.query(HistoricalEvent).filter(
            HistoricalEvent.name_original == "Test No Date Event"
        ).first()
        assert loaded.month is None
        assert loaded.day is None
        assert loaded.date_precision is None

        db.delete(loaded)
        db.flush()


# ─── Check constraints ────────────────────────────────────────────────────


class TestConstraints:
    def test_month_13_rejected(self, db):
        """Month=13 should violate the check constraint."""
        event = HistoricalEvent(
            name_original="Bad Month Event",
            name_original_lang="en",
            event_type="OTHER",
            year=2000,
            month=13,
            description="Invalid month.",
            confidence_score=0.5,
        )
        db.add(event)
        with pytest.raises(IntegrityError):
            db.flush()
        db.rollback()

    def test_day_32_rejected(self, db):
        """Day=32 should violate the check constraint."""
        event = HistoricalEvent(
            name_original="Bad Day Event",
            name_original_lang="en",
            event_type="OTHER",
            year=2000,
            day=32,
            description="Invalid day.",
            confidence_score=0.5,
        )
        db.add(event)
        with pytest.raises(IntegrityError):
            db.flush()
        db.rollback()

    def test_month_0_rejected(self, db):
        """Month=0 should violate the check constraint."""
        event = HistoricalEvent(
            name_original="Zero Month Event",
            name_original_lang="en",
            event_type="OTHER",
            year=2000,
            month=0,
            description="Invalid zero month.",
            confidence_score=0.5,
        )
        db.add(event)
        with pytest.raises(IntegrityError):
            db.flush()
        db.rollback()


# ─── API: list_events with month/day filters ──────────────────────────────


class TestListEventsFilters:
    def _seed_dated_event(self, db, name, year, month, day, precision="DAY"):
        """Helper: insert a dated event for filter tests."""
        iso = f"{year:04d}-{month:02d}-{day:02d}"
        event = HistoricalEvent(
            name_original=name,
            name_original_lang="en",
            event_type="BATTLE",
            year=year,
            month=month,
            day=day,
            date_precision=precision,
            iso_date=iso,
            description=f"Test event {name}.",
            confidence_score=0.9,
            status="confirmed",
        )
        db.add(event)
        db.commit()
        return event

    def test_filter_by_month(self, client, db):
        """GET /v1/events?month=3 returns only March events."""
        self._seed_dated_event(db, "_test_march_event", 1800, 3, 15)
        r = client.get("/v1/events", params={"month": 3})
        assert r.status_code == 200
        data = r.json()
        for ev in data["events"]:
            assert ev["month"] == 3

        # Cleanup.
        db.query(HistoricalEvent).filter(
            HistoricalEvent.name_original == "_test_march_event"
        ).delete()
        db.commit()

    def test_filter_by_month_and_day(self, client, db):
        """GET /v1/events?month=7&day=14 returns only July 14 events."""
        self._seed_dated_event(db, "_test_july14_event", 1789, 7, 14)
        r = client.get("/v1/events", params={"month": 7, "day": 14})
        assert r.status_code == 200
        data = r.json()
        for ev in data["events"]:
            assert ev["month"] == 7
            assert ev["day"] == 14

        db.query(HistoricalEvent).filter(
            HistoricalEvent.name_original == "_test_july14_event"
        ).delete()
        db.commit()

    def test_event_summary_includes_date_fields(self, client, db):
        """Event summary in list response includes month, day, date_precision, iso_date."""
        self._seed_dated_event(db, "_test_summary_fields", 1600, 10, 21)
        r = client.get("/v1/events", params={"month": 10, "day": 21})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1
        ev = data["events"][0]
        assert "month" in ev
        assert "day" in ev
        assert "date_precision" in ev
        assert "iso_date" in ev

        db.query(HistoricalEvent).filter(
            HistoricalEvent.name_original == "_test_summary_fields"
        ).delete()
        db.commit()


# ─── API: on-this-day endpoint ─────────────────────────────────────────────


class TestOnThisDay:
    def test_on_this_day_returns_events(self, client, db):
        """GET /v1/events/on-this-day/07-14 returns matching events."""
        # Seed a known event.
        ev = HistoricalEvent(
            name_original="_test_bastille_otd",
            name_original_lang="fr",
            event_type="REVOLUTION",
            year=1789,
            month=7,
            day=14,
            date_precision="DAY",
            iso_date="1789-07-14",
            description="Storming of the Bastille on 14 July 1789.",
            confidence_score=0.95,
            status="confirmed",
        )
        db.add(ev)
        db.commit()

        r = client.get("/v1/events/on-this-day/07-14")
        assert r.status_code == 200
        data = r.json()
        assert data["month"] == 7
        assert data["day"] == 14
        assert data["total"] >= 1
        names = [e["name_original"] for e in data["events"]]
        assert "_test_bastille_otd" in names

        db.query(HistoricalEvent).filter(
            HistoricalEvent.name_original == "_test_bastille_otd"
        ).delete()
        db.commit()

    def test_on_this_day_empty_returns_empty_list(self, client):
        """A date with no events returns empty list, not 404."""
        r = client.get("/v1/events/on-this-day/02-29")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 0  # may be 0

    def test_on_this_day_invalid_month_422(self, client):
        """Month 13 returns 422."""
        r = client.get("/v1/events/on-this-day/13-01")
        assert r.status_code == 422

    def test_on_this_day_invalid_day_422(self, client):
        """Day 32 returns 422."""
        r = client.get("/v1/events/on-this-day/01-32")
        assert r.status_code == 422

    def test_on_this_day_bad_format_422(self, client):
        """Bad format returns 422."""
        r = client.get("/v1/events/on-this-day/7-14")
        assert r.status_code == 422


# ─── API: at-date endpoint ─────────────────────────────────────────────────


class TestAtDate:
    def test_at_date_ce(self, client, db):
        """GET /v1/events/at-date/1789-07-14 returns matching events."""
        ev = HistoricalEvent(
            name_original="_test_bastille_atdate",
            name_original_lang="fr",
            event_type="REVOLUTION",
            year=1789,
            month=7,
            day=14,
            date_precision="DAY",
            iso_date="1789-07-14",
            description="Storming of the Bastille.",
            confidence_score=0.95,
            status="confirmed",
        )
        db.add(ev)
        db.commit()

        r = client.get("/v1/events/at-date/1789-07-14")
        assert r.status_code == 200
        data = r.json()
        assert data["date"] == "1789-07-14"
        assert data["year"] == 1789
        assert data["month"] == 7
        assert data["day"] == 14
        assert data["total"] >= 1

        db.query(HistoricalEvent).filter(
            HistoricalEvent.name_original == "_test_bastille_atdate"
        ).delete()
        db.commit()

    def test_at_date_bce(self, client, db):
        """GET /v1/events/at-date/-0331-10-01 works for BCE dates."""
        ev = HistoricalEvent(
            name_original="_test_gaugamela_atdate",
            name_original_lang="grc",
            event_type="BATTLE",
            year=-331,
            month=10,
            day=1,
            date_precision="DAY",
            iso_date="-0331-10-01",
            calendar_note="Proleptic Gregorian; original calendar uncertain",
            description="Battle of Gaugamela on 1 October 331 BCE.",
            confidence_score=0.85,
            status="confirmed",
        )
        db.add(ev)
        db.commit()

        r = client.get("/v1/events/at-date/-0331-10-01")
        assert r.status_code == 200
        data = r.json()
        assert data["year"] == -331
        assert data["total"] >= 1

        db.query(HistoricalEvent).filter(
            HistoricalEvent.name_original == "_test_gaugamela_atdate"
        ).delete()
        db.commit()

    def test_at_date_empty_returns_empty_list(self, client):
        """A date with no events returns empty list, not 404."""
        r = client.get("/v1/events/at-date/0001-01-01")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 0

    def test_at_date_bad_format_422(self, client):
        """Bad format returns 422."""
        r = client.get("/v1/events/at-date/14-07-1789")
        assert r.status_code == 422


# ─── API: event detail includes new fields ─────────────────────────────────


class TestEventDetail:
    def test_event_detail_has_calendar_note(self, client, db):
        """GET /v1/events/{id} includes calendar_note in response."""
        ev = HistoricalEvent(
            name_original="_test_detail_calnote",
            name_original_lang="en",
            event_type="BATTLE",
            year=-490,
            month=9,
            day=12,
            date_precision="DAY",
            iso_date="-0490-09-12",
            calendar_note="Proleptic Gregorian; original calendar uncertain",
            description="Battle of Marathon, September 490 BCE.",
            confidence_score=0.8,
            status="confirmed",
        )
        db.add(ev)
        db.commit()

        r = client.get(f"/v1/events/{ev.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["month"] == 9
        assert data["day"] == 12
        assert data["date_precision"] == "DAY"
        assert data["iso_date"] == "-0490-09-12"
        assert "calendar_note" in data
        assert "Proleptic Gregorian" in data["calendar_note"]

        db.query(HistoricalEvent).filter(
            HistoricalEvent.name_original == "_test_detail_calnote"
        ).delete()
        db.commit()


# ─── Backward compatibility ────────────────────────────────────────────────


class TestBackwardCompatibility:
    def test_old_events_still_work(self, client):
        """Events without month/day still return correctly."""
        r = client.get("/v1/events", params={"limit": 5})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1
        # month/day fields present (even if None).
        ev = data["events"][0]
        assert "month" in ev
        assert "day" in ev

    def test_list_events_without_filters_unchanged(self, client):
        """GET /v1/events with no month/day filters returns all events."""
        r = client.get("/v1/events")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 50  # we have 275+ events


# ─── Date extraction script ───────────────────────────────────────────────


class TestDateExtraction:
    def test_extract_dmy_pattern(self):
        from scripts.populate_date_fields import extract_date_from_description
        result = extract_date_from_description(
            "On 14 July 1789, the Bastille was stormed.", 1789
        )
        assert result is not None
        assert result["month"] == 7
        assert result["day"] == 14
        assert result["date_precision"] == "DAY"
        assert result["iso_date"] == "1789-07-14"

    def test_extract_mdy_pattern(self):
        from scripts.populate_date_fields import extract_date_from_description
        result = extract_date_from_description(
            "October 1, 331 BCE saw the Battle of Gaugamela.", -331
        )
        assert result is not None
        assert result["month"] == 10
        assert result["day"] == 1
        assert result["date_precision"] == "DAY"
        assert result["iso_date"] == "-0331-10-01"
        assert "Proleptic Gregorian" in result["calendar_note"]

    def test_extract_no_match_returns_none(self):
        from scripts.populate_date_fields import extract_date_from_description
        result = extract_date_from_description(
            "A great battle occurred in antiquity.", -500
        )
        assert result is None

    def test_extract_year_mismatch_skipped(self):
        """If extracted year doesn't match event year, skip it."""
        from scripts.populate_date_fields import extract_date_from_description
        result = extract_date_from_description(
            "On 14 July 1789, something happened.", 1800  # wrong year
        )
        assert result is None

    def test_extract_julian_calendar_note(self):
        """Pre-1582 CE dates get Julian calendar note."""
        from scripts.populate_date_fields import extract_date_from_description
        result = extract_date_from_description(
            "On 29 May 1453, Constantinople fell.", 1453
        )
        assert result is not None
        assert result["calendar_note"] == "Julian calendar; Gregorian equivalent may differ"

    def test_extract_post_1582_no_calendar_note(self):
        """Post-1582 dates have no calendar note."""
        from scripts.populate_date_fields import extract_date_from_description
        result = extract_date_from_description(
            "On 14 July 1789, the Bastille was stormed.", 1789
        )
        assert result is not None
        assert result["calendar_note"] is None
