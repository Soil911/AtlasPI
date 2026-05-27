"""Endpoint /citations — Phase G5 citation tracking via Zenodo + Crossref.

Espone una pagina pubblica + JSON endpoint che mostra paper accademici e
risorse che citano AtlasPI tramite il DOI Zenodo:
  Concept DOI: 10.5281/zenodo.19581784
  v6.1.2 DOI:  10.5281/zenodo.19581785

Sorgenti consultate (al volo, con caching Redis 6h):
1. OpenAlex API (https://api.openalex.org/works?filter=referenced_works.doi:10.5281/zenodo.19581784)
2. Crossref API (https://api.crossref.org/works?query.bibliographic=10.5281/zenodo.19581784)
3. Static `data/citations.json` (manualmente curate, override per ed elenchi)

Endpoint:
- GET /citations              — HTML pagina pubblica
- GET /citations/data         — JSON normalizzato
- GET /citations/refresh      — POST: forza refresh cache (richiede X-Admin-Token)
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import httpx
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/citations", tags=["citations"])

# AtlasPI Zenodo DOIs (vedi MEMORY.md: project_repo_private_blocks_zenodo)
ZENODO_CONCEPT_DOI = "10.5281/zenodo.19581784"
ZENODO_VERSION_DOIS = ["10.5281/zenodo.19581785"]

ALL_DOIS = [ZENODO_CONCEPT_DOI, *ZENODO_VERSION_DOIS]

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
STATIC_CITATIONS_FILE = DATA_DIR / "citations.json"

CACHE_KEY = "atlaspi:citations:v1"
CACHE_TTL = 6 * 3600  # 6 hours


class Citation(BaseModel):
    source: str  # 'openalex' | 'crossref' | 'static' | 'manual'
    type: str  # 'journal-article' | 'preprint' | 'blog' | 'book' | 'other'
    title: str
    authors: list[str] = []
    year: int | None = None
    doi: str | None = None
    url: str | None = None
    cited_doi: str  # which AtlasPI DOI is being cited


class CitationsResponse(BaseModel):
    total: int
    by_source: dict[str, int]
    by_type: dict[str, int]
    items: list[Citation]
    cited_dois: list[str]


# ─── Fetchers ───────────────────────────────────────────────────────


async def _fetch_openalex(doi: str) -> list[Citation]:
    """Query OpenAlex for works that reference this DOI.

    OpenAlex is a free, comprehensive scholarly graph. Better coverage
    than Crossref for many preprint/repository citations.
    """
    out: list[Citation] = []
    try:
        async with httpx.AsyncClient(timeout=15.0) as c:
            # Method 1: find works that have this DOI in referenced_works
            url = f"https://api.openalex.org/works?filter=referenced_works.doi:{doi}&per-page=50"
            r = await c.get(url, headers={"User-Agent": "AtlasPI-citations/1.0 (mailto:info@cra-srl.com)"})
            if r.status_code == 200:
                data = r.json()
                for w in data.get("results", []):
                    out.append(Citation(
                        source="openalex",
                        type=w.get("type") or "other",
                        title=(w.get("title") or "")[:500],
                        authors=[a.get("author", {}).get("display_name", "?") for a in w.get("authorships", [])[:5]],
                        year=w.get("publication_year"),
                        doi=w.get("doi"),
                        url=w.get("doi") and f"https://doi.org/{w['doi'].replace('https://doi.org/', '')}",
                        cited_doi=doi,
                    ))
    except Exception as e:
        logger.warning("OpenAlex fetch failed for %s: %s", doi, e)
    return out


async def _fetch_crossref(doi: str) -> list[Citation]:
    """Query Crossref for works that cite this DOI.

    Less complete than OpenAlex for repository DOIs but worth crosschecking.
    """
    out: list[Citation] = []
    try:
        async with httpx.AsyncClient(timeout=15.0) as c:
            # Crossref doesn't have a direct "cites" filter but has a `query` param
            url = f"https://api.crossref.org/works?query.bibliographic={doi}&rows=25"
            r = await c.get(
                url,
                headers={"User-Agent": "AtlasPI-citations/1.0 (mailto:info@cra-srl.com)"},
            )
            if r.status_code == 200:
                data = r.json()
                for w in data.get("message", {}).get("items", []):
                    # Filter: must actually reference our DOI in its references
                    refs = w.get("reference") or []
                    refs_dois = {(r.get("DOI") or "").lower() for r in refs}
                    if doi.lower() not in refs_dois:
                        continue
                    out.append(Citation(
                        source="crossref",
                        type=w.get("type") or "other",
                        title=(w.get("title") or [""])[0][:500] if isinstance(w.get("title"), list) else str(w.get("title"))[:500],
                        authors=[
                            f"{a.get('given', '')} {a.get('family', '')}".strip()
                            for a in (w.get("author") or [])[:5]
                        ],
                        year=(
                            w.get("published-print", {}).get("date-parts", [[None]])[0][0]
                            or w.get("published-online", {}).get("date-parts", [[None]])[0][0]
                        ),
                        doi=w.get("DOI"),
                        url=w.get("URL"),
                        cited_doi=doi,
                    ))
    except Exception as e:
        logger.warning("Crossref fetch failed for %s: %s", doi, e)
    return out


def _load_static() -> list[Citation]:
    """Carica `data/citations.json` se esiste (cura manuale)."""
    if not STATIC_CITATIONS_FILE.exists():
        return []
    try:
        with STATIC_CITATIONS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return [Citation(**c) for c in data.get("citations", [])]
    except Exception as e:
        logger.warning("Failed to load static citations: %s", e)
        return []


async def _aggregate_all(use_cache: bool = True) -> CitationsResponse:
    from src.cache import get_redis

    redis = get_redis() if use_cache else None
    if redis:
        try:
            cached = redis.get(CACHE_KEY)
            if cached:
                return CitationsResponse(**json.loads(cached))
        except Exception:
            pass

    seen_dois: set[str] = set()
    items: list[Citation] = []

    # Static cure first (always takes precedence on dedup)
    for c in _load_static():
        if c.doi and c.doi.lower() in seen_dois:
            continue
        if c.doi:
            seen_dois.add(c.doi.lower())
        items.append(c)

    # OpenAlex + Crossref for each DOI
    for doi in ALL_DOIS:
        for c in await _fetch_openalex(doi):
            if c.doi and c.doi.lower() in seen_dois:
                continue
            if c.doi:
                seen_dois.add(c.doi.lower())
            items.append(c)
        for c in await _fetch_crossref(doi):
            if c.doi and c.doi.lower() in seen_dois:
                continue
            if c.doi:
                seen_dois.add(c.doi.lower())
            items.append(c)

    # Aggregates
    by_source: dict[str, int] = {}
    by_type: dict[str, int] = {}
    for c in items:
        by_source[c.source] = by_source.get(c.source, 0) + 1
        by_type[c.type] = by_type.get(c.type, 0) + 1

    result = CitationsResponse(
        total=len(items),
        by_source=by_source,
        by_type=by_type,
        items=items,
        cited_dois=ALL_DOIS,
    )

    if redis:
        try:
            redis.setex(CACHE_KEY, CACHE_TTL, json.dumps(result.model_dump()))
        except Exception:
            pass

    return result


# ─── Endpoints ──────────────────────────────────────────────────────


@router.get(
    "/data",
    response_model=CitationsResponse,
    summary="Citation tracking JSON",
)
async def citations_data() -> CitationsResponse:
    return await _aggregate_all()


@router.post(
    "/refresh",
    response_model=CitationsResponse,
    summary="Force refresh citation cache (admin only)",
)
async def citations_refresh(request: Request) -> CitationsResponse:
    import hmac as _hmac

    expected = os.getenv("ATLASPI_ADMIN_TOKEN", "").strip()
    provided = request.headers.get("X-Admin-Token", "")
    if not expected or not provided or not _hmac.compare_digest(provided.encode(), expected.encode()):
        raise HTTPException(status_code=403, detail="Admin token required")
    return await _aggregate_all(use_cache=False)


@router.get(
    "",
    summary="HTML page con paper che citano AtlasPI",
)
async def citations_page() -> Response:
    """HTML public page."""
    data = await _aggregate_all()
    items_html = ""
    if data.total == 0:
        items_html = '<p class="empty">Nessuna citazione tracciata ancora. Se hai citato AtlasPI in un paper o blog post, fai sapere! GitHub Issues: <a href="https://github.com/Soil911/AtlasPI/issues">github.com/Soil911/AtlasPI</a></p>'
    else:
        rows = []
        for c in data.items:
            authors = ", ".join(c.authors[:3]) + (" et al." if len(c.authors) > 3 else "")
            year_str = f" ({c.year})" if c.year else ""
            link = c.url or (c.doi and f"https://doi.org/{c.doi}") or "#"
            rows.append(
                f'<li class="cite-item">'
                f'<a href="{link}" target="_blank" rel="noopener">{c.title}</a>{year_str}<br>'
                f'<span class="auth">{authors or "Unknown authors"}</span> '
                f'<span class="badge">{c.type}</span> '
                f'<span class="src">via {c.source}</span>'
                f'</li>'
            )
        items_html = '<ul class="cite-list">' + "\n".join(rows) + "</ul>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Citations — AtlasPI</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="Academic papers, blog posts, and resources that cite AtlasPI">
  <style>
    body {{ font: 15px/1.6 -apple-system, "Segoe UI", sans-serif; background: #0f1116; color: #e6e8eb; padding: 32px 24px; max-width: 880px; margin: 0 auto; }}
    h1 {{ color: #ffc896; font-size: 26px; margin-bottom: 4px; }}
    .lead {{ color: #9aa1a8; margin-bottom: 28px; }}
    .stats {{ display: flex; gap: 24px; padding: 14px 18px; background: #1a1c20; border-radius: 6px; margin-bottom: 24px; }}
    .stats span {{ color: #c8cdd3; font-size: 13px; }}
    .stats strong {{ color: #ffc896; font-size: 20px; display: block; }}
    .cite-list {{ list-style: none; padding: 0; }}
    .cite-item {{ padding: 14px 0; border-bottom: 1px solid #2a2c33; }}
    .cite-item a {{ color: #ffc896; text-decoration: none; font-weight: 500; }}
    .cite-item a:hover {{ text-decoration: underline; }}
    .auth {{ color: #9aa1a8; font-size: 13px; }}
    .badge {{ background: #2a2c33; color: #c8cdd3; padding: 2px 8px; border-radius: 3px; font-size: 11px; margin-left: 4px; }}
    .src {{ color: #6a7079; font-size: 12px; margin-left: 6px; }}
    .empty {{ color: #9aa1a8; padding: 24px; background: #1a1c20; border-radius: 6px; }}
    .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #2a2c33; color: #6a7079; font-size: 12px; }}
    .doi-list code {{ background: #1a1c20; padding: 2px 6px; border-radius: 3px; color: #c8cdd3; }}
  </style>
</head>
<body>
  <h1>Citations to AtlasPI</h1>
  <p class="lead">Academic papers, blog posts, and other resources that reference AtlasPI via the Zenodo DOI. Auto-discovered via OpenAlex + Crossref + manually curated entries.</p>

  <div class="stats">
    <div><strong>{data.total}</strong><span>citations tracked</span></div>
    <div><strong>{len(data.by_source)}</strong><span>sources</span></div>
    <div><strong>{len(data.by_type)}</strong><span>types</span></div>
  </div>

  {items_html}

  <div class="footer">
    <p>Tracked DOIs:</p>
    <p class="doi-list">{' '.join('<code>'+d+'</code>' for d in data.cited_dois)}</p>
    <p>Caching: 6h. Sources scanned: OpenAlex (free scholarly graph), Crossref, and manual curation in <code>data/citations.json</code>.</p>
    <p>Cited AtlasPI in your work? Open an issue at <a href="https://github.com/Soil911/AtlasPI/issues" style="color:#ffc896">github.com/Soil911/AtlasPI</a>.</p>
  </div>
</body>
</html>
"""
    return Response(content=html, media_type="text/html; charset=utf-8")
