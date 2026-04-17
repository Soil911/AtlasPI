"""AI Co-Founder Dashboard — v6.16 + v6.25 + v6.28.

GET  /admin/brief                         — HTML dashboard page
GET  /admin/ai/suggestions                — list suggestions (filterable)
POST /admin/ai/suggestions/{id}/accept    — accept a suggestion
POST /admin/ai/suggestions/{id}/reject    — reject a suggestion
POST /admin/ai/suggestions/{id}/implement — mark as implemented
POST /admin/ai/analyze                    — trigger analysis + generate suggestions
POST /admin/ai/implement-accepted         — auto-implement accepted suggestions (v6.28)
GET  /admin/ai/status                     — dashboard summary counts
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import AiSuggestion

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin"])

STATIC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "static"


# ═══════════════════════════════════════════════════════════════════
# 1. HTML Dashboard
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/admin/brief",
    summary="AI Co-Founder Dashboard (HTML)",
    description="Pagina HTML con dashboard interattiva per il co-founder.",
    include_in_schema=False,
)
async def cofounder_brief():
    """Serve the Co-Founder Brief dashboard HTML page."""
    brief_path = STATIC_DIR / "admin" / "brief.html"
    if brief_path.exists():
        return FileResponse(brief_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Dashboard file not found")


# ═══════════════════════════════════════════════════════════════════
# 2. Suggestions CRUD
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/admin/ai/suggestions",
    summary="List AI suggestions",
    description="Lista suggerimenti AI con filtro opzionale per status.",
    include_in_schema=False,
)
def list_suggestions(
    status: str | None = Query(None, description="Filter by status: pending, accepted, rejected, implemented"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Return suggestions ordered by priority (critical first), then created_at desc."""
    q = db.query(AiSuggestion)

    if status:
        q = q.filter(AiSuggestion.status == status)

    total = q.count()

    items = (
        q.order_by(AiSuggestion.priority.asc(), AiSuggestion.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return JSONResponse(content={
        "total": total,
        "offset": offset,
        "limit": limit,
        "suggestions": [
            {
                "id": s.id,
                "category": s.category,
                "title": s.title,
                "description": s.description,
                "detail_json": s.detail_json,
                "priority": s.priority,
                "status": s.status,
                "source": s.source,
                "created_at": s.created_at,
                "reviewed_at": s.reviewed_at,
                "review_note": s.review_note,
            }
            for s in items
        ],
    })


def _update_suggestion_status(db: Session, suggestion_id: int, new_status: str, note: str | None = None):
    """Helper: update suggestion status and reviewed_at timestamp."""
    suggestion = db.query(AiSuggestion).filter(AiSuggestion.id == suggestion_id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail=f"Suggestion {suggestion_id} not found")

    suggestion.status = new_status
    suggestion.reviewed_at = datetime.now(timezone.utc).isoformat()
    if note is not None:
        suggestion.review_note = note
    db.commit()
    db.refresh(suggestion)

    return JSONResponse(content={
        "id": suggestion.id,
        "status": suggestion.status,
        "reviewed_at": suggestion.reviewed_at,
        "review_note": suggestion.review_note,
    })


@router.post(
    "/admin/ai/suggestions/{suggestion_id}/accept",
    summary="Accept an AI suggestion",
    include_in_schema=False,
)
def accept_suggestion(
    suggestion_id: int,
    note: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """Mark a suggestion as accepted."""
    return _update_suggestion_status(db, suggestion_id, "accepted", note)


@router.post(
    "/admin/ai/suggestions/{suggestion_id}/reject",
    summary="Reject an AI suggestion",
    include_in_schema=False,
)
def reject_suggestion(
    suggestion_id: int,
    note: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """Mark a suggestion as rejected."""
    return _update_suggestion_status(db, suggestion_id, "rejected", note)


@router.post(
    "/admin/ai/suggestions/{suggestion_id}/implement",
    summary="Mark an AI suggestion as implemented (manual override)",
    description=(
        "Marks a suggestion's status as 'implemented' — manual override "
        "used when a human or Claude Code has completed the work outside "
        "the automated pipeline. Normal workflow: accept → daily cron "
        "runs /admin/ai/implement-accepted → handler executes → status "
        "flips automatically. Use this endpoint only when you've done the "
        "work yourself and want to close the loop manually."
    ),
    include_in_schema=False,
)
def implement_suggestion(
    suggestion_id: int,
    note: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """Mark a suggestion as implemented. Does NOT run the handler.

    The actual handler execution happens via `/admin/ai/implement-accepted`
    (batch endpoint, normally called by daily cron). This endpoint is for
    the case where YOU have already done the work manually and just want
    to close out the suggestion.
    """
    return _update_suggestion_status(db, suggestion_id, "implemented", note)


# ═══════════════════════════════════════════════════════════════════
# 3. Trigger Analysis
# ═══════════════════════════════════════════════════════════════════

@router.post(
    "/admin/ai/analyze",
    summary="Run AI analysis and generate suggestions",
    description=(
        "Triggers the full AI co-founder analysis pipeline: geographic gaps, "
        "temporal gaps, low confidence entities, missing boundaries, orphan "
        "entities, failed search patterns (404s + zero-result queries), and "
        "date coverage gaps (on-this-day feature). New suggestions are created "
        "in 'pending' status. Existing pending/accepted suggestions are "
        "not duplicated."
    ),
    include_in_schema=False,
)
def trigger_analysis(db: Session = Depends(get_db)):
    """Run AI analysis pipeline and return summary."""
    from scripts.ai_cofounder_analyze import run_analysis

    try:
        results = run_analysis(db=db)
    except Exception as e:
        logger.error("AI analysis failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

    return JSONResponse(content=results)


# ═══════════════════════════════════════════════════════════════════
# 4. Auto-implementation of accepted suggestions (v6.28 GAMECHANGER)
# ═══════════════════════════════════════════════════════════════════


@router.post(
    "/admin/ai/implement-accepted",
    summary="Auto-implement all accepted AI suggestions",
    description=(
        "Closes the feedback loop: fetches all accepted suggestions, "
        "dispatches each to a category-specific handler, and updates "
        "status to 'implemented' when automation succeeds. Categories "
        "that can't be auto-implemented generate a markdown briefing "
        "in data/briefings/ for manual/Claude Code follow-up.\n\n"
        "Automated handlers:\n"
        "- missing_boundaries → runs Natural Earth boundary matcher\n"
        "- low_confidence → boosts confidence on entities with ≥3 sources\n"
        "- quality (boundary variant) → same as missing_boundaries\n\n"
        "All other categories generate a briefing (status stays 'accepted')."
    ),
    include_in_schema=False,
)
def trigger_implementation(db: Session = Depends(get_db)):
    """Run the auto-implementation pipeline and return summary."""
    from scripts.implement_accepted_suggestions import implement_accepted

    try:
        summary = implement_accepted(db=db)
    except Exception as e:
        logger.error("Auto-implementation failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Implementation failed: {e}")

    return JSONResponse(content=summary)


# ═══════════════════════════════════════════════════════════════════
# 5. Status Summary
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/admin/ai/status",
    summary="AI dashboard status summary",
    include_in_schema=False,
)
def ai_status(db: Session = Depends(get_db)):
    """Return counts by status and last analysis timestamp."""
    rows = (
        db.query(AiSuggestion.status, func.count(AiSuggestion.id))
        .group_by(AiSuggestion.status)
        .all()
    )
    counts = {r[0]: r[1] for r in rows}

    last_created = (
        db.query(func.max(AiSuggestion.created_at))
        .filter(AiSuggestion.source == "auto")
        .scalar()
    )

    pending = counts.get("pending", 0)
    total = sum(counts.values())

    # Health summary: green if no pending critical/high, yellow if pending exist, red if critical
    critical_pending = (
        db.query(func.count(AiSuggestion.id))
        .filter(AiSuggestion.status == "pending", AiSuggestion.priority <= 2)
        .scalar() or 0
    )

    if critical_pending > 0:
        health = "issues_found"
    elif pending > 0:
        health = "needs_attention"
    else:
        health = "all_good"

    return JSONResponse(content={
        "last_analysis_time": last_created,
        "pending_count": pending,
        "accepted_count": counts.get("accepted", 0),
        "rejected_count": counts.get("rejected", 0),
        "implemented_count": counts.get("implemented", 0),
        "total_count": total,
        "health_summary": health,
    })
