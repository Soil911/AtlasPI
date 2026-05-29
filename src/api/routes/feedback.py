"""Endpoint feedback — Phase G1.

Raccoglie correzioni, segnalazioni e proposte da umani + agenti AI + bot.

POST /v1/feedback          — submit feedback (rate-limited)
GET  /v1/feedback          — lista pubblica trasparente (paginated)
GET  /v1/feedback/{id}     — dettaglio singolo
GET  /v1/feedback/stats    — aggregate counters per status/category

ETHICS-FEEDBACK: tutti i feedback vanno in stato `pending`. NON modificano
i dati direttamente. Per contenuti storici (campi entity year_*, boundary,
acquisition_method, ecc.) la review umana e' SEMPRE richiesta — sono
decisioni con impatto etico (CLAUDE.md, ETHICS-001-010).

Trasparenza: gli endpoint GET sono pubblici, senza auth, cosi' anche bot
e altri agenti possono leggere il feedback pendente per cross-validation.

PATCH /v1/feedback/{id} richiede auth admin (header X-Admin-Token).
"""

from __future__ import annotations

import datetime
import hashlib
import hmac
import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import (
    FeedbackSubmission,
    GeoEntity,
    HistoricalCity,
    HistoricalEvent,
)
from src.db.models.feedback import (
    FEEDBACK_CATEGORIES,
    FEEDBACK_STATUSES,
    SUBMITTER_TYPES,
)

# Max length per text fields — GPT-5.5 review: prevent abuse/DoS via huge payloads
MAX_CITATION_LEN = 2000
MAX_VALUE_LEN = 4000
MAX_REASONING_LEN = 4000

# Per default, GET /v1/feedback (senza filtro) mostra solo questi status
# per evitare che spam/rejected siano pubblicamente visibili.
DEFAULT_VISIBLE_STATUSES = {"pending", "under_review", "accepted"}

# Domini email accademici trusted (reputation iniziale 0.4 invece di 0.0)
TRUSTED_ACADEMIC_DOMAINS = {
    ".edu", ".ac.uk", ".ac.it", ".ac.jp", ".ac.za", ".edu.au", ".edu.cn",
    ".uni-muenchen.de", ".uni-leipzig.de", ".uni-bonn.de", ".uni-koeln.de",
    ".unibo.it", ".unimi.it", ".uniroma1.it", ".uniroma3.it", ".unipd.it",
    ".sorbonne-universite.fr", ".u-bordeaux.fr", ".univ-paris1.fr",
    ".cnrs.fr", ".inria.fr",  # CNRS, INRIA research orgs
    ".mpg.de",  # Max Planck
    ".cam.ac.uk", ".ox.ac.uk", ".harvard.edu", ".mit.edu", ".stanford.edu",
    ".yale.edu", ".princeton.edu", ".columbia.edu", ".berkeley.edu",
    ".chicago.edu", ".jhu.edu",  # Johns Hopkins
    ".si.edu",  # Smithsonian
}


def _compute_reputation_for_email(email: str) -> float:
    """Calcola reputation iniziale basata su dominio email.

    - Trusted academic (.edu, etc.): 0.4 (skip-the-queue ma comunque review)
    - Email standard: 0.1
    - No email: 0.0
    """
    if not email or "@" not in email:
        return 0.0
    domain = email.rsplit("@", 1)[1].lower()
    for trusted in TRUSTED_ACADEMIC_DOMAINS:
        if domain.endswith(trusted):
            return 0.4
    return 0.1


def _lookup_reputation(db: Session, submitter_id: str | None) -> float:
    """Calcola reputation cumulative basata su feedback accettati passati.

    Formula: base + 0.05 per ogni feedback accettato dello stesso submitter_id,
    capped a 1.0. + bonus accademico iniziale.

    NB: questo NON e' un mechanism anti-Sybil — submitter_id puo' essere
    cambiato. Usa solo come segnale soft per prioritizzare la review queue.
    """
    if not submitter_id:
        return 0.0
    base = _compute_reputation_for_email(submitter_id)
    accepted = (
        db.query(func.count(FeedbackSubmission.id))
        .filter(FeedbackSubmission.submitter_id == submitter_id)
        .filter(FeedbackSubmission.status == "accepted")
        .scalar()
        or 0
    )
    rep = min(base + 0.05 * accepted, 1.0)
    return round(rep, 3)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/feedback", tags=["feedback"])


# ─── Schemas ────────────────────────────────────────────────────────


class FeedbackSubmitRequest(BaseModel):
    """Schema per POST /v1/feedback."""

    entity_id: int | None = Field(None, description="ID entita' (geo_entities)")
    event_id: int | None = Field(None, description="ID evento (historical_events)")
    city_id: int | None = Field(None, description="ID citta' (historical_cities)")
    field_name: str | None = Field(
        None,
        max_length=64,
        description="Campo specifico (es. 'year_end', 'boundary_geojson')",
    )

    category: str = Field(
        ...,
        description=f"Categoria. Uno di: {sorted(FEEDBACK_CATEGORIES)}",
    )

    submitter_type: str = Field(
        ...,
        description=f"Tipo submitter. Uno di: {sorted(SUBMITTER_TYPES)}",
    )
    submitter_id: str | None = Field(
        None,
        max_length=256,
        description="Email umano | nome agente AI | handle pubblico",
    )

    current_value: str | None = Field(
        None,
        max_length=MAX_VALUE_LEN,
        description=f"Valore attuale (snapshot). Max {MAX_VALUE_LEN} chars.",
    )
    suggested_value: str | None = Field(
        None,
        max_length=MAX_VALUE_LEN,
        description=f"Valore corretto proposto. Max {MAX_VALUE_LEN} chars.",
    )
    citation: str | None = Field(
        None,
        max_length=MAX_CITATION_LEN,
        description=f"Riferimento bibliografico/accademico. Max {MAX_CITATION_LEN} chars.",
    )
    reasoning: str | None = Field(
        None,
        max_length=MAX_REASONING_LEN,
        description=f"Spiegazione breve (1-3 frasi). Max {MAX_REASONING_LEN} chars.",
    )
    confidence: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Self-reported confidence (0.0-1.0)",
    )

    @field_validator("category")
    @classmethod
    def _validate_category(cls, v: str) -> str:
        if v not in FEEDBACK_CATEGORIES:
            raise ValueError(
                f"Invalid category {v!r}. Allowed: {sorted(FEEDBACK_CATEGORIES)}"
            )
        return v

    @field_validator("submitter_type")
    @classmethod
    def _validate_submitter_type(cls, v: str) -> str:
        if v not in SUBMITTER_TYPES:
            raise ValueError(
                f"Invalid submitter_type {v!r}. Allowed: {sorted(SUBMITTER_TYPES)}"
            )
        return v


class FeedbackResponse(BaseModel):
    """Schema response per GET /v1/feedback/{id}."""

    id: int
    created_at: str
    entity_id: int | None
    event_id: int | None
    city_id: int | None
    field_name: str | None
    category: str
    submitter_type: str
    submitter_id: str | None
    submitter_reputation: float
    current_value: str | None
    suggested_value: str | None
    citation: str | None
    reasoning: str | None
    confidence: float | None
    status: str
    reviewed_at: str | None
    review_notes: str | None
    applied_at: str | None
    applied_in_version: str | None


class FeedbackListResponse(BaseModel):
    total: int
    count: int
    offset: int
    limit: int
    items: list[FeedbackResponse]


class FeedbackStatsResponse(BaseModel):
    total: int
    by_status: dict[str, int]
    by_category: dict[str, int]
    by_submitter_type: dict[str, int]
    last_24h: int
    last_7d: int


class FeedbackReviewRequest(BaseModel):
    """Schema per PATCH /v1/feedback/{id} (admin)."""

    status: str = Field(...)
    review_notes: str | None = None
    applied_in_version: str | None = None

    @field_validator("status")
    @classmethod
    def _validate_status(cls, v: str) -> str:
        if v not in FEEDBACK_STATUSES:
            raise ValueError(
                f"Invalid status {v!r}. Allowed: {sorted(FEEDBACK_STATUSES)}"
            )
        return v


# ─── Helpers ────────────────────────────────────────────────────────


def _hash_ip(ip: str) -> str:
    """SHA-256 hash IP — per privacy, manteniamo solo il digest."""
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()


def _check_admin_token(request: Request) -> bool:
    """Verifica header X-Admin-Token contro env var ATLASPI_ADMIN_TOKEN.

    Se ATLASPI_ADMIN_TOKEN non e' settata o e' vuota, NESSUNO puo' fare
    PATCH (failsafe — meglio bloccato che aperto).

    Usa `hmac.compare_digest` per protezione timing-attack (GPT-5.5 review).
    """
    expected = os.getenv("ATLASPI_ADMIN_TOKEN", "").strip()
    if not expected:
        return False
    provided = request.headers.get("X-Admin-Token", "")
    if not provided:
        return False
    # constant-time comparison
    return hmac.compare_digest(provided.encode("utf-8"), expected.encode("utf-8"))


# ─── Endpoints ──────────────────────────────────────────────────────


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=201,
    summary="Submit feedback su entita'/evento/citta'",
    description=(
        "Sottometti una correzione, segnalazione di fonte mancante, "
        "boundary dispute, bias report, ecc. \n\n"
        "Tutti i feedback vanno in stato `pending`. La review umana e' "
        "richiesta per contenuti storici (ETHICS).\n\n"
        "**Rate limit**: 5/min per IP anonimo, 30/min per submitter "
        "identificato (con submitter_id non-vuoto).\n\n"
        "Endpoint pubblico, no auth richiesta."
    ),
)
def submit_feedback(
    payload: FeedbackSubmitRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    # Validazione cross-field: per categorie che richiedono un target,
    # almeno uno tra entity_id/event_id/city_id deve essere settato.
    requires_target = payload.category in {
        "incorrect_data",
        "missing_source",
        "boundary_dispute",
        "translation_error",
        "ethics_concern",
    }
    has_target = any([payload.entity_id, payload.event_id, payload.city_id])
    if requires_target and not has_target:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Category {payload.category!r} requires at least one of "
                "entity_id, event_id, city_id"
            ),
        )

    # Se entity_id/event_id/city_id forniti, verifica che esistano (no dangling refs).
    # GPT-5.5 review #4: also validate event_id/city_id consistency.
    if payload.entity_id is not None:
        exists = db.query(GeoEntity.id).filter(GeoEntity.id == payload.entity_id).first()
        if not exists:
            raise HTTPException(
                status_code=404,
                detail=f"entity_id {payload.entity_id} not found",
            )
    if payload.event_id is not None:
        exists = db.query(HistoricalEvent.id).filter(HistoricalEvent.id == payload.event_id).first()
        if not exists:
            raise HTTPException(
                status_code=404,
                detail=f"event_id {payload.event_id} not found",
            )
    if payload.city_id is not None:
        exists = db.query(HistoricalCity.id).filter(HistoricalCity.id == payload.city_id).first()
        if not exists:
            raise HTTPException(
                status_code=404,
                detail=f"city_id {payload.city_id} not found",
            )

    # IP hashing per privacy + anti-spam
    client_ip = request.client.host if request.client else "unknown"
    ip_hash = _hash_ip(client_ip)
    user_agent = request.headers.get("user-agent", "")[:500]

    now_iso = datetime.datetime.utcnow().isoformat() + "Z"

    # G2: compute reputation based on past accepted feedback + email domain
    reputation = _lookup_reputation(db, payload.submitter_id)

    fb = FeedbackSubmission(
        created_at=now_iso,
        entity_id=payload.entity_id,
        event_id=payload.event_id,
        city_id=payload.city_id,
        field_name=payload.field_name,
        category=payload.category,
        submitter_type=payload.submitter_type,
        submitter_id=payload.submitter_id,
        submitter_reputation=reputation,
        current_value=payload.current_value,
        suggested_value=payload.suggested_value,
        citation=payload.citation,
        reasoning=payload.reasoning,
        confidence=payload.confidence,
        status="pending",
        client_ip_hash=ip_hash,
        user_agent=user_agent,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)

    logger.info(
        "feedback submitted: id=%d category=%s entity_id=%s submitter_type=%s",
        fb.id, fb.category, fb.entity_id, fb.submitter_type,
    )

    return FeedbackResponse(**fb.to_public_dict())


@router.get(
    "",
    response_model=FeedbackListResponse,
    summary="Lista pubblica feedback (trasparenza)",
    description=(
        "Filtri opzionali per status/category/entity_id/submitter_type. "
        "Pubblicamente accessibile per permettere ad agenti AI di leggere "
        "il feedback pending e fare cross-validation."
    ),
)
def list_feedback(
    status: str | None = Query(
        None,
        description=(
            "Filtra per status. Se omesso, mostra solo pending/under_review/"
            "accepted (rejected/duplicate visibili solo con filter esplicito)."
        ),
    ),
    category: str | None = Query(None, description="Filtra per categoria"),
    entity_id: int | None = Query(None, description="Filtra per entity_id"),
    submitter_type: str | None = Query(None, description="Filtra per submitter_type"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> FeedbackListResponse:
    q = db.query(FeedbackSubmission)

    # GPT-5.5 review #5: hide rejected/duplicate by default (anti-spam visibility)
    if status:
        q = q.filter(FeedbackSubmission.status == status)
    else:
        q = q.filter(FeedbackSubmission.status.in_(DEFAULT_VISIBLE_STATUSES))
    if category:
        q = q.filter(FeedbackSubmission.category == category)
    if entity_id is not None:
        q = q.filter(FeedbackSubmission.entity_id == entity_id)
    if submitter_type:
        q = q.filter(FeedbackSubmission.submitter_type == submitter_type)

    total = q.count()
    items = (
        q.order_by(desc(FeedbackSubmission.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return FeedbackListResponse(
        total=total,
        count=len(items),
        offset=offset,
        limit=limit,
        items=[FeedbackResponse(**fb.to_public_dict()) for fb in items],
    )


@router.get(
    "/stats",
    response_model=FeedbackStatsResponse,
    summary="Aggregate statistics per status/category",
)
def feedback_stats(db: Session = Depends(get_db)) -> FeedbackStatsResponse:
    total = db.query(FeedbackSubmission).count()

    by_status_q = (
        db.query(FeedbackSubmission.status, func.count(FeedbackSubmission.id))
        .group_by(FeedbackSubmission.status)
        .all()
    )
    by_status = {s: c for s, c in by_status_q}

    by_category_q = (
        db.query(FeedbackSubmission.category, func.count(FeedbackSubmission.id))
        .group_by(FeedbackSubmission.category)
        .all()
    )
    by_category = {s: c for s, c in by_category_q}

    by_submitter_q = (
        db.query(FeedbackSubmission.submitter_type, func.count(FeedbackSubmission.id))
        .group_by(FeedbackSubmission.submitter_type)
        .all()
    )
    by_submitter = {s: c for s, c in by_submitter_q}

    # 24h e 7d windows
    now = datetime.datetime.utcnow()
    threshold_24h = (now - datetime.timedelta(hours=24)).isoformat()
    threshold_7d = (now - datetime.timedelta(days=7)).isoformat()
    last_24h = (
        db.query(FeedbackSubmission)
        .filter(FeedbackSubmission.created_at >= threshold_24h)
        .count()
    )
    last_7d = (
        db.query(FeedbackSubmission)
        .filter(FeedbackSubmission.created_at >= threshold_7d)
        .count()
    )

    return FeedbackStatsResponse(
        total=total,
        by_status=by_status,
        by_category=by_category,
        by_submitter_type=by_submitter,
        last_24h=last_24h,
        last_7d=last_7d,
    )


class ContributorRow(BaseModel):
    submitter_id: str  # masked
    submitter_type: str
    total_submissions: int
    accepted: int
    pending: int
    rejected: int
    reputation: float


# IMPORTANTE: /contributors va PRIMA di /{feedback_id} perche' FastAPI
# matcha le route in ordine di registrazione e {feedback_id:int} catturerebbe
# "contributors" tentando di parsarlo come int (422).
@router.get(
    "/contributors",
    response_model=list[ContributorRow],
    summary="Leaderboard contributori",
    description=(
        "Top submitter per numero di feedback accettati. Email mascherate per "
        "privacy. Usato per gamification + accountability."
    ),
)
def contributors(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[ContributorRow]:
    # Top submitter_id by # accepted, gives also pending/rejected counts
    rows = (
        db.query(
            FeedbackSubmission.submitter_id,
            FeedbackSubmission.submitter_type,
            FeedbackSubmission.status,
            func.count(FeedbackSubmission.id).label("c"),
        )
        .filter(FeedbackSubmission.submitter_id.isnot(None))
        .filter(FeedbackSubmission.submitter_id != "")
        .group_by(
            FeedbackSubmission.submitter_id,
            FeedbackSubmission.submitter_type,
            FeedbackSubmission.status,
        )
        .all()
    )

    agg: dict[str, dict] = {}
    for sid, stype, status, c in rows:
        if sid not in agg:
            agg[sid] = {
                "submitter_id": sid,
                "submitter_type": stype,
                "total_submissions": 0,
                "accepted": 0,
                "pending": 0,
                "rejected": 0,
            }
        agg[sid]["total_submissions"] += c
        if status == "accepted":
            agg[sid]["accepted"] += c
        elif status == "pending":
            agg[sid]["pending"] += c
        elif status == "rejected":
            agg[sid]["rejected"] += c

    # Mask submitter_id (email) per privacy
    def _mask(s: str) -> str:
        if "@" in s and "." in s:
            return f"***@{s.rsplit('@', 1)[1]}"
        return s

    output: list[ContributorRow] = []
    for sid, data in agg.items():
        rep = _lookup_reputation(db, sid)
        output.append(
            ContributorRow(
                submitter_id=_mask(sid),
                submitter_type=data["submitter_type"],
                total_submissions=data["total_submissions"],
                accepted=data["accepted"],
                pending=data["pending"],
                rejected=data["rejected"],
                reputation=rep,
            )
        )

    output.sort(key=lambda x: (x.accepted, x.total_submissions), reverse=True)
    return output[:limit]


@router.get(
    "/{feedback_id}",
    response_model=FeedbackResponse,
    summary="Dettaglio singolo feedback",
)
def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    fb = db.query(FeedbackSubmission).filter(FeedbackSubmission.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return FeedbackResponse(**fb.to_public_dict())


@router.patch(
    "/{feedback_id}",
    response_model=FeedbackResponse,
    summary="Review feedback (admin only)",
    description=(
        "Aggiorna lo status di un feedback. Richiede header "
        "`X-Admin-Token` corrispondente a env var `ATLASPI_ADMIN_TOKEN`."
    ),
)
def review_feedback(
    feedback_id: int,
    payload: FeedbackReviewRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    if not _check_admin_token(request):
        raise HTTPException(status_code=403, detail="Admin token required")

    fb = db.query(FeedbackSubmission).filter(FeedbackSubmission.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")

    fb.status = payload.status
    fb.reviewed_at = datetime.datetime.utcnow().isoformat() + "Z"
    fb.reviewed_by = "admin"  # G2 reputation: useremo token-bound identity
    if payload.review_notes is not None:
        fb.review_notes = payload.review_notes
    if payload.status == "accepted" and payload.applied_in_version is not None:
        fb.applied_at = fb.reviewed_at
        fb.applied_in_version = payload.applied_in_version

    db.commit()
    db.refresh(fb)

    logger.info(
        "feedback reviewed: id=%d new_status=%s",
        fb.id, fb.status,
    )

    return FeedbackResponse(**fb.to_public_dict())
