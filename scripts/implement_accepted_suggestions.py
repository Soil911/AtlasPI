"""Auto-implementation of accepted AI suggestions — v6.28.

Clirim's vision (paraphrased):
  "L'analisi agente interno propone, io entro il pomeriggio vedo le proposte,
   ne accetto 2 e vanno in pending. Alla prossima esecuzione del claude code
   programmato queste vengono implementate e finiscono in implemented."

This script closes the loop: fetches accepted suggestions, dispatches each
to a category-specific handler, and updates status accordingly.

Not all categories are fully auto-implementable:
- `missing_boundaries` → auto-run boundary updater, count successes (AUTOMATED)
- `quality` (boundaries variant) → same as above                (AUTOMATED)
- `low_confidence` → auto-boost entities that have ≥3 sources   (AUTOMATED)
- `geographic_gap` / `temporal_gap` → generate briefing MD file (BRIEFING)
- `missing_chain` / `traffic_pattern` / `search_demand` → briefing (BRIEFING)
- `date_coverage` → briefing                                     (BRIEFING)

Handler outcomes:
- "implemented": suggestion marked as implemented (automation succeeded)
- "briefing": a markdown briefing written to data/briefings/; suggestion
  stays in "accepted" state for human/Claude Code execution
- "failed": handler errored; suggestion stays "accepted" with note

Usage:
    python -m scripts.implement_accepted_suggestions
    curl -X POST https://atlaspi.cra-srl.com/admin/ai/implement-accepted
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

# Ensure project root is on sys.path so `src.*` imports work.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.db.database import SessionLocal
from src.db.models import AiSuggestion, GeoEntity, Source

logger = logging.getLogger(__name__)

BRIEFINGS_DIR = _PROJECT_ROOT / "data" / "briefings"


# ═══════════════════════════════════════════════════════════════════
# Handler outcome type
# ═══════════════════════════════════════════════════════════════════


def _outcome(status: str, summary: str, **extra: Any) -> dict[str, Any]:
    """Build a structured outcome dict. Status in {implemented, briefing, failed}."""
    return {"status": status, "summary": summary, **extra}


# ═══════════════════════════════════════════════════════════════════
# Automated handlers
# ═══════════════════════════════════════════════════════════════════


def handle_missing_boundaries(sug: AiSuggestion, db: Session) -> dict[str, Any]:
    """Attempt to auto-add boundaries via the existing boundary updater.

    The updater uses Natural Earth + aourednik data. If any of the entities
    in detail_json receive a boundary, we mark as implemented.
    """
    try:
        details = json.loads(sug.detail_json) if sug.detail_json else []
    except json.JSONDecodeError:
        return _outcome("failed", "detail_json malformed — cannot parse entity list")

    entity_ids = [d["id"] for d in details if isinstance(d, dict) and "id" in d]
    if not entity_ids:
        return _outcome("failed", "No entity IDs in detail_json")

    # Count entities without boundaries BEFORE
    before_missing = db.query(GeoEntity).filter(
        GeoEntity.id.in_(entity_ids),
        or_(
            GeoEntity.boundary_geojson.is_(None),
            GeoEntity.boundary_geojson == "",
        ),
    ).count()

    # Run the existing boundary updater (works by name_original match)
    try:
        from src.ingestion.update_boundaries import update_all_boundaries
        # Note: update_all_boundaries operates on ALL entities matching its
        # extraction dataset. It's idempotent — entities already having
        # boundaries are refreshed (not double-added).
        update_all_boundaries()
    except Exception as exc:
        logger.warning("update_all_boundaries failed: %s", exc)
        return _outcome("failed", f"Boundary updater error: {exc}")

    # Count after
    db.expire_all()  # Refresh session after the updater's separate session
    after_missing = db.query(GeoEntity).filter(
        GeoEntity.id.in_(entity_ids),
        or_(
            GeoEntity.boundary_geojson.is_(None),
            GeoEntity.boundary_geojson == "",
        ),
    ).count()

    added = before_missing - after_missing
    if added > 0:
        return _outcome(
            "implemented",
            f"Auto-matched boundaries for {added}/{len(entity_ids)} entities",
            entities_affected=entity_ids,
            added_count=added,
        )
    else:
        return _outcome(
            "briefing",
            f"No boundary auto-match possible for {len(entity_ids)} entities — manual work needed",
            entities_affected=entity_ids,
        )


def handle_low_confidence(sug: AiSuggestion, db: Session) -> dict[str, Any]:
    """Auto-boost confidence for entities that have accumulated ≥3 sources.

    Rationale: if a low-confidence entity has been verified by multiple
    sources since the suggestion was created, its confidence should reflect
    that. This is a safe, evidence-based automation.
    """
    try:
        details = json.loads(sug.detail_json) if sug.detail_json else []
    except json.JSONDecodeError:
        return _outcome("failed", "detail_json malformed")

    if not isinstance(details, list):
        return _outcome("failed", "detail_json is not a list")

    entity_ids = [d["id"] for d in details if isinstance(d, dict) and "id" in d]
    if not entity_ids:
        return _outcome("failed", "No entity IDs in detail_json")

    boosted: list[dict] = []
    for eid in entity_ids:
        ent = db.query(GeoEntity).filter(GeoEntity.id == eid).first()
        if ent is None:
            continue
        # Count sources for this entity
        source_count = db.query(Source).filter(Source.entity_id == eid).count()
        # Boost if ≥3 sources AND current confidence still low
        if source_count >= 3 and ent.confidence_score < 0.6:
            old = ent.confidence_score
            new = min(0.6, 0.3 + 0.1 * source_count)  # 3 sources -> 0.6, caps
            ent.confidence_score = new
            boosted.append({
                "id": eid,
                "name": ent.name_original,
                "old_confidence": old,
                "new_confidence": new,
                "sources": source_count,
            })

    if boosted:
        return _outcome(
            "implemented",
            f"Boosted confidence on {len(boosted)} entities (≥3 sources each)",
            boosted=boosted,
        )
    else:
        return _outcome(
            "briefing",
            f"No entities qualify for auto-boost (need ≥3 sources). {len(entity_ids)} still low-confidence.",
            entities_checked=entity_ids,
        )


# ═══════════════════════════════════════════════════════════════════
# Briefing handler (for non-automatable categories)
# ═══════════════════════════════════════════════════════════════════


def _generate_briefing(sug: AiSuggestion) -> Path:
    """Write a markdown briefing for human/Claude Code to act on."""
    BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    fname = f"suggestion_{sug.id:04d}_{sug.category}_{timestamp}.md"
    path = BRIEFINGS_DIR / fname

    try:
        detail_parsed = json.loads(sug.detail_json) if sug.detail_json else None
    except json.JSONDecodeError:
        detail_parsed = None

    content = f"""# AtlasPI Implementation Briefing

**Suggestion ID**: {sug.id}
**Category**: `{sug.category}`
**Priority**: {sug.priority} (1=critical, 5=info)
**Created**: {sug.created_at}
**Accepted**: {sug.reviewed_at}

## Title

{sug.title}

## Description

{sug.description}

## Review note

{sug.review_note or "(no review note)"}

## Detail payload

```json
{json.dumps(detail_parsed, indent=2, ensure_ascii=False) if detail_parsed else sug.detail_json or "(empty)"}
```

## Implementation guidance

This suggestion requires human or Claude Code intervention — it cannot be
fully automated. Typical approaches:

- **geographic_gap**: research historical entities in the named region and
  add them to `data/entities/batch_XX.json` with sources and ETHICS notes.
- **temporal_gap**: research events from the named era and add them to
  `data/events/batch_XX.json` with verified dates.
- **missing_chain**: identify orphan entities and link them into existing
  or new dynasty chains in `data/chains/`.
- **traffic_pattern** (404): investigate the repeated path — either add the
  missing entity/event, or document why the path is invalid.
- **search_demand** (empty search): check what users searched for, decide
  whether to add the missing data.
- **date_coverage**: add date-precise events in the months with sparse coverage.

After implementation, mark the suggestion as implemented via:

```bash
curl -X POST "https://atlaspi.cra-srl.com/admin/ai/suggestions/{sug.id}/implement" \\
  -G --data-urlencode "note=Implemented on $(date +%Y-%m-%d)"
```
"""
    path.write_text(content, encoding="utf-8")
    return path


def handle_briefing(sug: AiSuggestion, db: Session) -> dict[str, Any]:
    """Generate a markdown briefing for non-automatable categories."""
    try:
        path = _generate_briefing(sug)
        # Prefer a relative path if the briefing is under PROJECT_ROOT,
        # otherwise return the absolute path (test/tmp directories).
        try:
            path_str = str(path.relative_to(_PROJECT_ROOT))
        except ValueError:
            path_str = str(path)
        return _outcome(
            "briefing",
            f"Briefing generated: {path.name}",
            briefing_path=path_str,
        )
    except Exception as exc:
        logger.exception("Briefing generation failed")
        return _outcome("failed", f"Briefing generation error: {exc}")


def handle_geometric_bug(sug: AiSuggestion, db: Session) -> dict[str, Any]:
    """Auto-fix geometric bugs (antimeridian-crossing, wrong-polygon inheritance).

    Delegates to fix_antimeridian_and_wrong_polygons which handles both:
    - USA/Russia/Fiji antimeridian polygon clipping
    - Wrong-country polygon inheritance (Cherokee, Seminole, etc.)
    """
    try:
        from src.ingestion.fix_antimeridian_and_wrong_polygons import fix_all
        # Use module-level SessionLocal since fix_all opens its own session
        stats = fix_all(dry_run=False)
        total = stats.get("wrong_polygon_fixed", 0) + stats.get("antimeridian_clipped", 0)
        if total > 0:
            return _outcome(
                "implemented",
                f"Fixed {stats['wrong_polygon_fixed']} wrong-polygon + "
                f"{stats['antimeridian_clipped']} antimeridian-crossing boundaries",
                details=stats.get("details", []),
            )
        else:
            return _outcome(
                "briefing",
                "No geometric bugs currently detected — suggestion may be stale; "
                "mark as implemented manually after visual verification",
            )
    except Exception as exc:
        logger.exception("Geometric bug auto-fix failed")
        return _outcome("failed", f"Geometric fix error: {exc}")


# ═══════════════════════════════════════════════════════════════════
# Handler registry
# ═══════════════════════════════════════════════════════════════════


HANDLERS: dict[str, Callable[[AiSuggestion, Session], dict[str, Any]]] = {
    # Automated (category -> specific handler)
    "missing_boundaries": handle_missing_boundaries,
    "low_confidence": handle_low_confidence,
    "geometric_bug": handle_geometric_bug,  # v6.31
    # "quality" is a catch-all; route to missing_boundaries when the
    # description matches the boundary pattern, else briefing.
}


def _dispatch(sug: AiSuggestion, db: Session) -> dict[str, Any]:
    """Route a suggestion to its handler (or briefing fallback)."""
    # Quality category: check if it's a boundary issue
    if sug.category == "quality" and "boundar" in sug.title.lower():
        return handle_missing_boundaries(sug, db)

    handler = HANDLERS.get(sug.category, handle_briefing)
    return handler(sug, db)


# ═══════════════════════════════════════════════════════════════════
# Orchestrator
# ═══════════════════════════════════════════════════════════════════


def implement_accepted(db: Session | None = None) -> dict[str, Any]:
    """Fetch all accepted suggestions, dispatch handlers, update statuses.

    Returns a summary dict with counts per outcome + per-suggestion details.
    """
    own_session = db is None
    if own_session:
        db = SessionLocal()

    summary: dict[str, Any] = {
        "processed": 0,
        "implemented": 0,
        "briefing": 0,
        "failed": 0,
        "results": [],
    }

    try:
        accepted = (
            db.query(AiSuggestion)
            .filter(AiSuggestion.status == "accepted")
            .order_by(AiSuggestion.priority, AiSuggestion.created_at)
            .all()
        )

        for sug in accepted:
            outcome = _dispatch(sug, db)
            summary["processed"] += 1
            summary[outcome["status"]] = summary.get(outcome["status"], 0) + 1

            # If implemented, flip status
            if outcome["status"] == "implemented":
                sug.status = "implemented"
                sug.reviewed_at = datetime.now(timezone.utc).isoformat()
                existing_note = sug.review_note or ""
                sug.review_note = (
                    existing_note + f"\nAuto-implemented: {outcome['summary']}"
                ).strip()

            summary["results"].append({
                "id": sug.id,
                "category": sug.category,
                "title": sug.title,
                "outcome": outcome["status"],
                "summary": outcome["summary"],
            })

        db.commit()
        return summary
    except Exception:
        db.rollback()
        raise
    finally:
        if own_session:
            db.close()


def main():
    """CLI entry point."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger.info("Running accepted-suggestion implementation pipeline...")

    summary = implement_accepted()

    logger.info(
        "Processed %d | implemented: %d | briefing: %d | failed: %d",
        summary["processed"],
        summary.get("implemented", 0),
        summary.get("briefing", 0),
        summary.get("failed", 0),
    )
    for r in summary["results"]:
        logger.info(
            "  [%s] #%d %s: %s",
            r["outcome"],
            r["id"],
            r["category"],
            r["summary"][:100],
        )

    return summary


if __name__ == "__main__":
    main()
