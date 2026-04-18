"""v6.69 — bootstrap Wikidata Q-ID per ogni entità AtlasPI (audit v4 Fase A).

Per ogni entità in `geo_entities`, cerca il Wikidata Q-ID corrispondente e
calcola uno score di confidenza 0..1 basato su:

- match esatto label (0.5)
- match fuzzy label ≥ 0.85 (0.3)
- coerenza tipo (instance of + subclass of ancestors) (0.2)
- overlap year_start ≤10y (0.2)
- overlap year_end ≤10y (0.1)

Penalizzazioni:
- più candidati con score simile (ambiguo): -0.15

## Output

- `scripts/wikidata_cache/search_{hash}.json` — cache wbsearchentities
- `scripts/wikidata_cache/entity_{qid}.json` — cache wbgetentities
- `research_output/audit_v4/fase_a_matches.json` — tutti i match (anche low)
- `data/wikidata/v669_qid_high_confidence.json` — patch file per apply_data_patch

## Usage

```bash
# Run (idempotent, riparte dalla cache)
python -m scripts.wikidata_bootstrap \
    --entities research_output/audit_v4/entities_dump.json \
    --out research_output/audit_v4/fase_a_matches.json \
    --patches data/wikidata/v669_qid_high_confidence.json

# Re-run (usa solo cache, utile per iterare sullo scoring)
python -m scripts.wikidata_bootstrap \
    --entities research_output/audit_v4/entities_dump.json \
    --out research_output/audit_v4/fase_a_matches.json \
    --patches data/wikidata/v669_qid_high_confidence.json \
    --offline
```

ETHICS: Wikidata può avere bias occidentali/colonialisti sui nomi e sulle date.
Il Q-ID che salviamo è solo un puntatore di riferimento per drift detection,
non una fonte autoritativa. Match high-confidence (≥0.85) vanno applicati,
ma le discrepanze sui dati vanno sempre valutate manualmente (Fase B).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests
from rapidfuzz import fuzz


logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).resolve().parent / "wikidata_cache"
SEARCH_CACHE = CACHE_DIR / "search"
ENTITY_CACHE = CACHE_DIR / "entity"

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKIDATA_ENTITY = "https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"

UA = "AtlasPI/6.69 (https://atlaspi.cra-srl.com; contact@cra-srl.com) audit-v4-bootstrap"

# Rate limit: Wikidata ammette ~5 req/sec con UA, stiamo sotto con 4 req/sec.
RATE_LIMIT_SLEEP = 0.25

# Type mapping AtlasPI → Wikidata Q-IDs accettabili come instance_of.
# Il controllo è "ancestors include uno qualsiasi di questi" (via P31 + claims).
# Filosofia: permissivo — se label+anno combaciano, un tipo generico tipo
# Q34770 (historical country) basta. Se il tipo specifico match, bonus.
TYPE_MAP: dict[str, set[str]] = {
    # Q3024240 (historical state entity) incluso quasi ovunque: è il classifier
    # più usato da Wikidata per polity storiche generiche (vedi analisi v6.69).
    "empire": {"Q34770", "Q48349", "Q28171280", "Q417175", "Q7210356", "Q3024240"},
    "kingdom": {"Q34770", "Q417175", "Q1763527", "Q28171280", "Q3024240"},
    "city-state": {"Q34770", "Q133442", "Q179164", "Q515", "Q3024240"},
    "sultanate": {"Q34770", "Q5474748", "Q48349", "Q417175", "Q3024240"},
    "confederation": {"Q34770", "Q5460530", "Q17149090", "Q41710", "Q3024240"},
    "caliphate": {"Q34770", "Q429885", "Q48349", "Q3024240"},
    "khanate": {"Q34770", "Q756316", "Q48349", "Q417175", "Q3024240"},
    "republic": {"Q34770", "Q7270", "Q7278", "Q3024240"},
    "emirate": {"Q34770", "Q526021", "Q417175", "Q3024240"},
    "duchy": {"Q34770", "Q166980", "Q417175", "Q3024240"},
    "dynasty": {"Q34770", "Q164950", "Q48349", "Q417175", "Q3024240"},
    "principality": {"Q34770", "Q208500", "Q417175", "Q3024240"},
    "chiefdom": {"Q34770", "Q3012546", "Q2945124", "Q41710", "Q3024240"},
    "colony": {"Q34770", "Q4321471", "Q107390", "Q3024240"},
    "colonial_outpost": {"Q34770", "Q4321471", "Q107390", "Q5119", "Q3024240"},
    "polity": {"Q34770", "Q1048835", "Q48349", "Q417175", "Q3024240"},
    "culture": {"Q4258850", "Q11042", "Q465299"},
    "civilization": {"Q11042", "Q14752093", "Q4258850", "Q3024240"},
    "cultural_region": {"Q4258850", "Q82794", "Q1620908"},
    "tribal_nation": {"Q41710", "Q133442", "Q34770", "Q3024240"},
    "tribal_federation": {"Q17149090", "Q41710", "Q3024240"},
    "federation": {"Q34770", "Q475050", "Q7270", "Q3024240"},
    "imamate": {"Q34770", "Q48349", "Q3024240"},
    "disputed_territory": {"Q15239622", "Q34770", "Q22713380", "Q3024240"},
    "city": {"Q515", "Q486972"},
    "settlement": {"Q486972", "Q515"},
    "settlement-complex": {"Q486972", "Q839954"},
    "earthwork-complex": {"Q839954", "Q4989906"},
}

# Super-fallback: se nessun P31 match, almeno accettiamo questi tipi molto generici
# di "entità storica/politica/culturale". v6.69: espanso post-analisi band 0.70-0.85
# per capturare dinastie cinesi (Q836688, Q12857432) e altri tipi comuni che
# TYPE_MAP per-entity_type non copre.
GENERIC_HISTORICAL = {
    "Q34770",        # historical country
    "Q15642541",     # historical unrecognized state
    "Q1048835",      # political territorial entity
    "Q56061",        # administrative territorial entity
    # v6.69 espansione: tipi osservati come P31 più frequente per entità
    # storiche con year_start/year_end matching.
    "Q6256",         # country
    "Q3624078",      # sovereign state
    "Q1250464",      # historical nation
    "Q836688",       # Chinese dynasty
    "Q12857432",     # imperial dynasty
    "Q1292119",      # sub-country historical entity
    "Q11514315",     # historical period (dinastie cinesi)
    "Q1288568",      # mother tongue / nation (NO — remove if harmful)
    "Q50068795",     # ancient civilization (Aksum, Wari, etc.)
    "Q20203507",     # religious order (alcuni imamati)
    "Q45762",        # Indian princely state
    "Q38058796",     # (varianti di dinastia)
    "Q19953632",     # former administrative territorial entity
    "Q1620908",      # historical region
    "Q465299",       # chinese archaeology / culture
    "Q1790360",      # colonial empire (British Empire)
    "Q3918",         # precolonial empire
    "Q107390",       # colony of a state
    "Q161243",       # viceroyalty
    "Q1549591",      # big city (capitals with no ancient status)
    "Q7210356",      # political territorial entity (variant)
    "Q2472587",      # historical kingdom
    "Q12759805",     # ancient city
    "Q15661340",     # former tribal nation
    "Q3932025",      # former empire
    "Q4204501",      # ancient civilization variant
    "Q294440",       # public body
    "Q15128558",     # political organization variant
}


class WikidataClient:
    """Client minimale Wikidata con cache e rate limiting."""

    def __init__(self, offline: bool = False):
        self.offline = offline
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": UA})
        SEARCH_CACHE.mkdir(parents=True, exist_ok=True)
        ENTITY_CACHE.mkdir(parents=True, exist_ok=True)
        self._last_call = 0.0
        self.http_calls = 0
        self.cache_hits = 0

    def _throttle(self):
        now = time.monotonic()
        dt = now - self._last_call
        if dt < RATE_LIMIT_SLEEP:
            time.sleep(RATE_LIMIT_SLEEP - dt)
        self._last_call = time.monotonic()

    def _cache_key_search(self, query: str, lang: str) -> Path:
        h = hashlib.md5(f"{lang}|{query}".encode("utf-8")).hexdigest()[:16]
        # sanitize query for filename (best effort)
        safe = re.sub(r"[^\w\-]", "_", query)[:40]
        return SEARCH_CACHE / f"{lang}_{safe}_{h}.json"

    def search(self, label: str, lang: str = "en", limit: int = 10) -> list[dict]:
        """wbsearchentities — cerca candidati per label."""
        if not label or not label.strip():
            return []
        cache = self._cache_key_search(label, lang)
        if cache.exists():
            self.cache_hits += 1
            try:
                return json.loads(cache.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        if self.offline:
            return []
        self._throttle()
        params = {
            "action": "wbsearchentities",
            "search": label,
            "language": lang,
            "limit": limit,
            "format": "json",
            "type": "item",
        }
        try:
            r = self.session.get(WIKIDATA_API, params=params, timeout=30)
            r.raise_for_status()
            self.http_calls += 1
            data = r.json().get("search", [])
        except (requests.RequestException, json.JSONDecodeError) as e:
            logger.warning("search fail for %r (%s): %s", label, lang, e)
            return []
        cache.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return data

    def get_entity(self, qid: str) -> dict | None:
        """Fetch entity via Special:EntityData JSON."""
        if not qid or not qid.startswith("Q"):
            return None
        cache = ENTITY_CACHE / f"{qid}.json"
        if cache.exists():
            self.cache_hits += 1
            try:
                return json.loads(cache.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        if self.offline:
            return None
        self._throttle()
        url = WIKIDATA_ENTITY.format(qid=qid)
        try:
            r = self.session.get(url, timeout=30)
            r.raise_for_status()
            self.http_calls += 1
            full = r.json()
            ent = full.get("entities", {}).get(qid)
        except (requests.RequestException, json.JSONDecodeError) as e:
            logger.warning("get_entity fail %s: %s", qid, e)
            return None
        if ent is None:
            return None
        # Trim per ridurre dim cache: teniamo solo campi utili.
        trimmed = {
            "id": ent.get("id"),
            "labels": ent.get("labels", {}),
            "aliases": ent.get("aliases", {}),
            "claims": {
                k: v
                for k, v in ent.get("claims", {}).items()
                if k in {"P31", "P279", "P571", "P576", "P36", "P17", "P625",
                         "P1365", "P1366", "P361", "P527", "P37", "P150"}
            },
        }
        cache.write_text(json.dumps(trimmed, ensure_ascii=False), encoding="utf-8")
        return trimmed


# ─── Utility ───────────────────────────────────────────────────────────

def parse_wd_time(val: str | None) -> int | None:
    """Parsa una stringa Wikidata time (+1299-01-01T00:00:00Z / -0027-...) → anno int.

    Wikidata usa format ISO8601 con precisione variabile. Estraiamo solo l'anno.
    """
    if not val or not isinstance(val, str):
        return None
    m = re.match(r"^([+-]?)(\d+)-", val)
    if not m:
        return None
    sign = m.group(1)
    year_s = m.group(2)
    year = int(year_s)
    if sign == "-":
        # Wikidata: "-0044" → 44 BC. AtlasPI convention: anno=-44.
        # Nota: Wikidata usa astronomical numbering per BCE (anno 0 esiste),
        # mentre storici usano 1BCE=anno prima di 1CE. Differenza di 1 anno
        # per date BCE. Tolleriamo: il drift check ha margine ±10y.
        year = -year
    return year


def extract_claim_values(entity: dict, prop: str) -> list[Any]:
    """Estrae i valori della claim `prop` dall'entità Wikidata."""
    claims = entity.get("claims", {}).get(prop, [])
    out = []
    for c in claims:
        mainsnak = c.get("mainsnak", {})
        if mainsnak.get("snaktype") != "value":
            continue
        dv = mainsnak.get("datavalue", {})
        val = dv.get("value")
        typ = dv.get("type")
        if typ == "wikibase-entityid" and isinstance(val, dict):
            out.append(val.get("id"))
        elif typ == "time" and isinstance(val, dict):
            out.append(val.get("time"))
        elif typ == "globecoordinate" and isinstance(val, dict):
            out.append((val.get("latitude"), val.get("longitude")))
        elif typ == "monolingualtext" and isinstance(val, dict):
            out.append(val.get("text"))
        else:
            out.append(val)
    return out


def entity_label(entity: dict, langs: list[str]) -> str | None:
    labels = entity.get("labels", {})
    for lang in langs:
        lab = labels.get(lang)
        if lab and lab.get("value"):
            return lab["value"]
    # fallback: qualsiasi label
    for lab in labels.values():
        if lab.get("value"):
            return lab["value"]
    return None


# ─── Scoring ───────────────────────────────────────────────────────────

def compute_score(
    atlas: dict,
    wd_entity: dict,
    search_hit: dict | None = None,
) -> tuple[float, list[str], dict]:
    """Calcola score 0..1 di match tra entità AtlasPI e candidato Wikidata.

    Ritorna (score, reasons, flags) — flags utile per penalty tuning."""
    reasons: list[str] = []
    flags = {"exact_label": False, "type_exact": False, "year_match": False}
    score = 0.0

    atlas_labels = {atlas["name_original"].lower()}
    for v in atlas.get("name_variants", []):
        if v.get("name"):
            atlas_labels.add(v["name"].lower())

    wd_labels: set[str] = set()
    for lang_data in wd_entity.get("labels", {}).values():
        if lang_data.get("value"):
            wd_labels.add(lang_data["value"].lower())
    for lang_al in wd_entity.get("aliases", {}).values():
        for al in lang_al:
            if al.get("value"):
                wd_labels.add(al["value"].lower())
    if search_hit and search_hit.get("label"):
        wd_labels.add(search_hit["label"].lower())
    if search_hit and search_hit.get("match", {}).get("text"):
        wd_labels.add(search_hit["match"]["text"].lower())

    # Label matching
    exact = atlas_labels & wd_labels
    if exact:
        score += 0.4
        flags["exact_label"] = True
        reasons.append(f"exact_label={next(iter(exact))}")
    else:
        best_fuzz = 0.0
        best_pair = None
        for a in atlas_labels:
            for w in wd_labels:
                r = fuzz.ratio(a, w) / 100.0
                if r > best_fuzz:
                    best_fuzz = r
                    best_pair = (a, w)
        if best_fuzz >= 0.85:
            score += 0.3
            reasons.append(f"fuzzy={best_pair}@{best_fuzz:.2f}")
        elif best_fuzz >= 0.7:
            score += 0.1
            reasons.append(f"fuzzy_weak={best_pair}@{best_fuzz:.2f}")

    # Type consistency
    p31 = set(extract_claim_values(wd_entity, "P31"))
    expected = TYPE_MAP.get(atlas["entity_type"], set())
    expected_with_fallback = expected | GENERIC_HISTORICAL
    if p31 & expected:
        score += 0.25
        flags["type_exact"] = True
        reasons.append(f"type_exact={sorted(p31 & expected)}")
    elif p31 & expected_with_fallback:
        score += 0.18
        reasons.append(f"type_generic={sorted(p31 & expected_with_fallback)}")

    # Combo bonus (label+type = very strong signal)
    if flags["exact_label"] and flags["type_exact"]:
        score += 0.1
        reasons.append("combo_label_type")

    # Year overlap
    p571 = [parse_wd_time(v) for v in extract_claim_values(wd_entity, "P571")]
    p571 = [y for y in p571 if y is not None]
    atlas_ys = atlas.get("year_start")
    if p571 and atlas_ys is not None:
        best = min(abs(atlas_ys - y) for y in p571)
        if best <= 10:
            score += 0.15
            flags["year_match"] = True
            reasons.append(f"year_start Δ{best}")
        elif best <= 30:
            score += 0.08
            reasons.append(f"year_start Δ{best} (weak)")
        elif best <= 100:
            reasons.append(f"year_start Δ{best} (drift!)")

    p576 = [parse_wd_time(v) for v in extract_claim_values(wd_entity, "P576")]
    p576 = [y for y in p576 if y is not None]
    atlas_ye = atlas.get("year_end")
    ye_match = False
    if p576 and atlas_ye is not None:
        best = min(abs(atlas_ye - y) for y in p576)
        if best <= 10:
            score += 0.1
            flags["year_match"] = True
            ye_match = True
            reasons.append(f"year_end Δ{best}")
        elif best <= 30:
            score += 0.05
        elif best <= 100:
            reasons.append(f"year_end Δ{best} (drift!)")

    # Triple bonus: label + both years match è un signal molto robusto
    # (probabilità di 3 coincidenze indipendenti ~0). Promuove 0.75→0.90.
    # v6.69: bumped 0.1→0.15 per capture cases dove P31 non matcha TYPE_MAP
    # nostro ma le date sono perfette (es. British Empire Q8680 con P31=Q1790360).
    ys_match = any(r.startswith("year_start Δ") and not r.endswith("(weak)") and not r.endswith("(drift!)") for r in reasons)
    if flags["exact_label"] and ys_match and ye_match:
        score += 0.15
        reasons.append("triple_match")

    return min(score, 1.0), reasons, flags


# ─── Main bootstrap loop ───────────────────────────────────────────────

def find_match(client: WikidataClient, atlas: dict) -> dict:
    """Ritorna il best match Wikidata per un'entità AtlasPI."""
    # Query candidates: provo label original + variants + english variant.
    queries: list[tuple[str, str]] = []
    name_o = (atlas.get("name_original") or "").strip()
    lang_o = atlas.get("name_original_lang") or "en"
    # Wikidata search è poco tollerante con lingue esotiche; fallback a en.
    # Aggiungo anche la query con lingua original e en (entrambe).
    if name_o:
        # normalizza lingua: "grc" → "en" (search non accetta grc)
        search_lang = lang_o if lang_o in {
            "en", "fr", "de", "es", "it", "ru", "zh", "ja", "ar", "tr",
            "pt", "nl", "pl", "sv", "fi", "he", "hi", "la", "el",
        } else "en"
        queries.append((name_o, search_lang))
        if search_lang != "en":
            queries.append((name_o, "en"))
    for v in atlas.get("name_variants", []):
        n = (v.get("name") or "").strip()
        if n and n != name_o:
            vlang = v.get("lang") or "en"
            if vlang not in {"en", "fr", "de", "es", "it"}:
                vlang = "en"
            queries.append((n, vlang))

    # dedup by (query, lang)
    seen = set()
    queries_dd = []
    for q in queries:
        if q in seen:
            continue
        seen.add(q)
        queries_dd.append(q)
    queries = queries_dd[:5]  # max 5 query per entità → limite HTTP

    candidates: dict[str, dict] = {}  # qid → best search hit
    for q, lang in queries:
        hits = client.search(q, lang=lang, limit=5)
        for h in hits:
            qid = h.get("id")
            if not qid:
                continue
            # tieni la prima occorrenza (migliore ranking Wikidata)
            if qid not in candidates:
                candidates[qid] = h

    # Fetch entity details per candidate e scoring
    scored: list[dict] = []
    for qid, hit in list(candidates.items())[:8]:  # limita dettaglio a top 8 per perf
        ent = client.get_entity(qid)
        if not ent:
            continue
        score, reasons, flags = compute_score(atlas, ent, hit)
        scored.append({
            "qid": qid,
            "label": entity_label(ent, ["en", "la", lang_o, atlas["name_original_lang"]]),
            "description": (hit or {}).get("description", ""),
            "score": round(score, 3),
            "reasons": reasons,
            "flags": flags,
        })

    scored.sort(key=lambda x: -x["score"])

    # Penalizzazione ambiguità: applica solo se il top NON ha discriminatori forti.
    # Se il top ha (exact_label AND type_exact AND year_match) la scelta è robusta
    # anche con più candidati label-simili (Roman Empire vs Roman Republic, ecc.).
    penalty = 0.0
    if len(scored) >= 2:
        top = scored[0]
        alt = scored[1]
        close = alt["score"] >= top["score"] - 0.05
        strong_top = top["flags"]["exact_label"] and top["flags"]["type_exact"]
        top_discriminates = top["flags"]["year_match"] and not alt["flags"]["year_match"]
        if close and top_discriminates:
            penalty = 0.0  # il top vince grazie al year match
        elif close and not strong_top and top["score"] >= 0.6:
            penalty = 0.10
        elif close and strong_top and alt["flags"]["type_exact"] and alt["flags"]["exact_label"]:
            # Entrambi hanno exact_label + type_exact → veramente ambiguo
            penalty = 0.05

    best = scored[0] if scored else None
    if best:
        final = max(0.0, best["score"] - penalty)
        return {
            "entity_id": atlas["id"],
            "name_original": atlas["name_original"],
            "entity_type": atlas["entity_type"],
            "year_start": atlas["year_start"],
            "wikidata_qid": best["qid"],
            "wikidata_label": best["label"],
            "wikidata_description": best["description"],
            "score": round(final, 3),
            "score_raw": best["score"],
            "ambiguity_penalty": penalty,
            "match_reasons": best["reasons"],
            "alternatives": scored[1:5],
            "review_needed": final < 0.85,
        }
    return {
        "entity_id": atlas["id"],
        "name_original": atlas["name_original"],
        "entity_type": atlas["entity_type"],
        "year_start": atlas["year_start"],
        "wikidata_qid": None,
        "score": 0.0,
        "match_reasons": ["no_candidates"],
        "alternatives": [],
        "review_needed": True,
    }


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description="Bootstrap Wikidata Q-IDs")
    parser.add_argument("--entities", required=True, help="JSON file with entities dump")
    parser.add_argument("--out", required=True, help="Output matches JSON")
    parser.add_argument("--patches", required=True, help="Output patch file (score ≥0.85)")
    parser.add_argument("--offline", action="store_true", help="Use only cache, skip HTTP")
    parser.add_argument("--limit", type=int, default=0, help="Limit entities (for debug)")
    parser.add_argument("--threshold", type=float, default=0.85, help="Score threshold for auto-apply")
    args = parser.parse_args()

    with open(args.entities, "rb") as f:
        data = json.loads(f.read().decode("utf-8"))
    ents = data["entities"]
    if args.limit:
        ents = ents[: args.limit]

    client = WikidataClient(offline=args.offline)

    results: list[dict] = []
    for i, atlas in enumerate(ents):
        if i and i % 50 == 0:
            logger.info(
                "progress %d/%d (http=%d cache=%d)",
                i, len(ents), client.http_calls, client.cache_hits,
            )
        try:
            res = find_match(client, atlas)
        except Exception as e:
            logger.exception("error on entity %s: %s", atlas["id"], e)
            res = {
                "entity_id": atlas["id"],
                "name_original": atlas["name_original"],
                "entity_type": atlas["entity_type"],
                "year_start": atlas["year_start"],
                "wikidata_qid": None,
                "score": 0.0,
                "match_reasons": [f"error: {e}"],
                "alternatives": [],
                "review_needed": True,
            }
        results.append(res)

    # Stats
    n_high = sum(1 for r in results if r["score"] >= args.threshold)
    n_mid = sum(1 for r in results if 0.5 <= r["score"] < args.threshold)
    n_low = sum(1 for r in results if r["score"] < 0.5)
    logger.info(
        "done: total=%d high(≥%.2f)=%d mid=%d low=%d | http=%d cache=%d",
        len(results), args.threshold, n_high, n_mid, n_low,
        client.http_calls, client.cache_hits,
    )

    # Write full matches
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write patch file (only high-confidence)
    patches = [
        {
            "resource": "entity",
            "id": r["entity_id"],
            "field": "wikidata_qid",
            "new_value": r["wikidata_qid"],
            "rationale": f"Wikidata bootstrap v6.69 score={r['score']}: {r['wikidata_label']}",
            "source": "Wikidata " + r["wikidata_qid"],
            "audit_ref": "audit_v4/fase_a",
        }
        for r in results
        if r["score"] >= args.threshold and r["wikidata_qid"]
    ]
    patch_path = Path(args.patches)
    patch_path.parent.mkdir(parents=True, exist_ok=True)
    patch_path.write_text(json.dumps(patches, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("wrote %d patches to %s", len(patches), patch_path)


if __name__ == "__main__":
    main()
