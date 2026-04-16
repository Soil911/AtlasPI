"""Populate date precision fields on existing HistoricalEvent rows.

v6.14 — Extracts month/day from event descriptions using regex patterns,
cross-validates against event.year, and sets date_precision / iso_date /
calendar_note accordingly.

Safe to run multiple times: only updates rows where date_precision is NULL.

Usage:
    python -m scripts.populate_date_fields          # dry-run (default)
    python -m scripts.populate_date_fields --apply  # write to DB

ETHICS: for BCE dates, calendar_note is set to explain proleptic Gregorian
usage. The original calendar (Julian, Egyptian, Chinese lunisolar, etc.)
is acknowledged as uncertain.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys

logger = logging.getLogger(__name__)

# ─── Date extraction patterns ──────────────────────────────────────────────

MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

# "On 14 July 1789" / "On 1 October 331 BCE" / "on 28 August 476"
_PATTERN_DMY = re.compile(
    r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\s+(\d{1,4})\s*(BCE|BC|CE|AD|a\.C\.|d\.C\.)?",
    re.IGNORECASE,
)

# "July 14, 1789" / "October 1, 331 BCE"
_PATTERN_MDY = re.compile(
    r"\b(January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\s+(\d{1,2}),?\s+(\d{1,4})\s*(BCE|BC|CE|AD|a\.C\.|d\.C\.)?",
    re.IGNORECASE,
)

# Month-only: "In October 331 BCE" / "In July 1789"
_PATTERN_MY = re.compile(
    r"\b(?:in|during|by)\s+(January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\s+(\d{1,4})\s*(BCE|BC|CE|AD|a\.C\.|d\.C\.)?",
    re.IGNORECASE,
)

# Season patterns: "in the summer of 410" / "during spring 1453"
_PATTERN_SEASON = re.compile(
    r"\b(?:in the\s+)?(spring|summer|autumn|fall|winter)\s+(?:of\s+)?(\d{1,4})\s*(BCE|BC|CE|AD)?",
    re.IGNORECASE,
)


def _is_bce(era_str: str | None) -> bool:
    """Return True if the era indicator means BCE."""
    if not era_str:
        return False
    return era_str.upper() in ("BCE", "BC", "A.C.")


def _compute_iso_date(year: int, month: int | None, day: int | None) -> str:
    """Compute ISO-like date string, supporting negative years for BCE.

    Examples: "1789-07-14", "-0331-10-01", "0476-08-00" (day unknown).
    """
    if year < 0:
        y_str = f"-{abs(year):04d}"
    else:
        y_str = f"{year:04d}"
    m_str = f"{month:02d}" if month else "00"
    d_str = f"{day:02d}" if day else "00"
    return f"{y_str}-{m_str}-{d_str}"


def extract_date_from_description(
    description: str, event_year: int
) -> dict | None:
    """Try to extract month/day from an event description.

    Cross-validates extracted year against event_year to avoid false positives.

    Returns dict with keys: month, day, date_precision, iso_date, calendar_note
    or None if no date found.
    """
    # Try day-month-year patterns first (most precise).
    for pattern, group_order in [
        (_PATTERN_DMY, "dmy"),
        (_PATTERN_MDY, "mdy"),
    ]:
        match = pattern.search(description)
        if match:
            if group_order == "dmy":
                day_s, month_s, year_s, era = match.groups()
            else:
                month_s, day_s, year_s, era = match.groups()

            extracted_year = int(year_s)
            if _is_bce(era):
                extracted_year = -extracted_year

            # Cross-validate: extracted year must match event_year.
            if extracted_year != event_year:
                continue

            m = MONTH_MAP.get(month_s.lower())
            d = int(day_s)
            if m and 1 <= d <= 31:
                cal_note = None
                if event_year < 0:
                    cal_note = "Proleptic Gregorian; original calendar uncertain"
                elif event_year < 1582:
                    cal_note = "Julian calendar; Gregorian equivalent may differ"

                return {
                    "month": m,
                    "day": d,
                    "date_precision": "DAY",
                    "iso_date": _compute_iso_date(event_year, m, d),
                    "calendar_note": cal_note,
                }

    # Try month-year only.
    match = _PATTERN_MY.search(description)
    if match:
        month_s, year_s, era = match.groups()
        extracted_year = int(year_s)
        if _is_bce(era):
            extracted_year = -extracted_year
        if extracted_year == event_year:
            m = MONTH_MAP.get(month_s.lower())
            if m:
                cal_note = None
                if event_year < 0:
                    cal_note = "Proleptic Gregorian; original calendar uncertain"
                elif event_year < 1582:
                    cal_note = "Julian calendar; Gregorian equivalent may differ"

                return {
                    "month": m,
                    "day": None,
                    "date_precision": "MONTH",
                    "iso_date": _compute_iso_date(event_year, m, None),
                    "calendar_note": cal_note,
                }

    # Try season patterns.
    match = _PATTERN_SEASON.search(description)
    if match:
        _season, year_s, era = match.groups()
        extracted_year = int(year_s)
        if _is_bce(era):
            extracted_year = -extracted_year
        if extracted_year == event_year:
            cal_note = None
            if event_year < 0:
                cal_note = "Proleptic Gregorian; original calendar uncertain"
            return {
                "month": None,
                "day": None,
                "date_precision": "SEASON",
                "iso_date": _compute_iso_date(event_year, None, None),
                "calendar_note": cal_note,
            }

    # No match — default to YEAR precision.
    return None


def populate_date_fields(apply: bool = False) -> dict:
    """Scan all events, extract dates, optionally write to DB.

    Returns stats dict.
    """
    from src.db.database import SessionLocal
    from src.db.models import HistoricalEvent

    db = SessionLocal()
    try:
        # Only process events without date_precision (not yet populated).
        events = (
            db.query(HistoricalEvent)
            .filter(HistoricalEvent.date_precision.is_(None))
            .all()
        )

        stats = {"total": len(events), "day": 0, "month": 0, "season": 0, "year": 0}

        for event in events:
            result = extract_date_from_description(event.description, event.year)

            if result:
                precision = result["date_precision"]
                if apply:
                    event.month = result["month"]
                    event.day = result["day"]
                    event.date_precision = result["date_precision"]
                    event.iso_date = result["iso_date"]
                    event.calendar_note = result["calendar_note"]
                stats[precision.lower()] += 1
                logger.info(
                    "[%s] %s (%d) → %s %s",
                    precision,
                    event.name_original,
                    event.year,
                    result.get("iso_date", ""),
                    "(dry-run)" if not apply else "",
                )
            else:
                # No sub-annual date found — mark as YEAR precision.
                if apply:
                    event.date_precision = "YEAR"
                stats["year"] += 1

        if apply:
            db.commit()
            logger.info("Date fields populated and committed.")
        else:
            logger.info("Dry-run complete. Use --apply to write changes.")

        return stats

    except Exception:
        db.rollback()
        logger.error("Error populating date fields", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="Populate date precision fields on events")
    parser.add_argument("--apply", action="store_true", help="Write changes to DB (default: dry-run)")
    args = parser.parse_args()

    stats = populate_date_fields(apply=args.apply)
    print("\nDate population stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
