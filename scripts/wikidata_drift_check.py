"""v6.70 — drift check tra AtlasPI e Wikidata per entità con Q-ID (audit v4 Fase B).

Per ogni entità AtlasPI con `wikidata_qid != NULL`, confronta:

| AtlasPI field           | Wikidata property          | Severity cutoff |
|-------------------------|----------------------------|-----------------|
| year_start              | P571 (inception)           | HIGH>50y MED>20 |
| year_end                | P576 (dissolved)           | HIGH>50y MED>20 |
| capital_name            | P36 (capital)              | MED se mismatch |
| capital_lat, capital_lon| P36→P625 (coord)           | HIGH>200km MED>50|

Genera:
- `research_output/audit_v4/fase_b_drift_report.md` — report narrativo
- `research_output/audit_v4/fase_b_drift_data.json` — dati strutturati
- `research_output/audit_v4/fase_b_autofixable.json` — patch applicabili in automatico

## Autofix rules (conservative)

- **NIENTE autofix per date**: Wikidata e AtlasPI possono avere convention diverse
  (astronomical vs historian BCE, inclusive vs exclusive endpoints). Flag only.
- **Autofix per coordinate typo**: se km_diff > 1000km E coord swap/sign flip
  produce < 10km diff → applica il flip (è un typo evidente).
- **Autofix per coordinate allineate**: no (può essere legittimo che AtlasPI usi
  coordinate diverse per capitale storica vs attuale).

## Usage

```bash
python -m scripts.wikidata_drift_check \
    --matches research_output/audit_v4/fase_a_matches.json \
    --entities research_output/audit_v4/entities_dump.json \
    --out-report research_output/audit_v4/fase_b_drift_report.md \
    --out-data research_output/audit_v4/fase_b_drift_data.json \
    --out-patches research_output/audit_v4/fase_b_autofixable.json
```

ETHICS: Le discrepanze Wikidata↔AtlasPI non sono automaticamente bug AtlasPI.
Wikidata può avere bias occidentali o imprecisioni. Questo script identifica
segnali per review, NON autority override. Vedi CLAUDE.md valore #2.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import re
import time
from pathlib import Path
from typing import Any

import requests


logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).resolve().parent / "wikidata_cache"
ENTITY_CACHE = CACHE_DIR / "entity"

WIKIDATA_ENTITY = "https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"

UA = "AtlasPI/6.70 (https://atlaspi.cra-srl.com; contact@cra-srl.com) audit-v4-drift"
RATE_LIMIT_SLEEP = 0.25


class WDClient:
    def __init__(self, offline: bool = False):
        self.offline = offline
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": UA})
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

    def get_entity(self, qid: str) -> dict | None:
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
        try:
            r = self.session.get(WIKIDATA_ENTITY.format(qid=qid), timeout=30)
            r.raise_for_status()
            self.http_calls += 1
            full = r.json()
            ent = full.get("entities", {}).get(qid)
        except (requests.RequestException, json.JSONDecodeError) as e:
            logger.warning("get_entity fail %s: %s", qid, e)
            return None
        if ent is None:
            return None
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
    if not val or not isinstance(val, str):
        return None
    m = re.match(r"^([+-]?)(\d+)-", val)
    if not m:
        return None
    sign = m.group(1)
    year = int(m.group(2))
    if sign == "-":
        year = -year
    return year


def extract_claim_values(entity: dict, prop: str) -> list[Any]:
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


def label_of(entity: dict, langs: list[str]) -> str | None:
    labels = entity.get("labels", {})
    for lang in langs:
        lab = labels.get(lang)
        if lab and lab.get("value"):
            return lab["value"]
    for lab in labels.values():
        if lab.get("value"):
            return lab["value"]
    return None


def aliases_of(entity: dict, langs: list[str]) -> list[str]:
    out: list[str] = []
    for lang in langs:
        for al in entity.get("aliases", {}).get(lang, []):
            if al.get("value"):
                out.append(al["value"])
    return out


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance in km between two points on Earth."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def labels_similar(a: str | None, b: str | None) -> bool:
    """Soft label match: case-insensitive + strip accents-ish."""
    if not a or not b:
        return False
    from rapidfuzz import fuzz
    an, bn = a.strip().lower(), b.strip().lower()
    if an == bn:
        return True
    return fuzz.ratio(an, bn) >= 85


# ─── Drift checks ──────────────────────────────────────────────────────

def check_year_start(atlas: dict, wd_entity: dict) -> dict | None:
    atlas_ys = atlas.get("year_start")
    if atlas_ys is None:
        return None
    p571 = [parse_wd_time(v) for v in extract_claim_values(wd_entity, "P571")]
    p571 = [y for y in p571 if y is not None]
    if not p571:
        return None
    best = min(p571, key=lambda y: abs(atlas_ys - y))
    delta = atlas_ys - best
    abs_d = abs(delta)
    if abs_d <= 10:
        return None
    severity = "LOW"
    if abs_d > 50:
        severity = "HIGH"
    elif abs_d > 20:
        severity = "MED"
    return {
        "field": "year_start",
        "atlas": atlas_ys,
        "wikidata": best,
        "wikidata_all": p571,
        "delta": delta,
        "abs_delta": abs_d,
        "severity": severity,
    }


def check_year_end(atlas: dict, wd_entity: dict) -> dict | None:
    atlas_ye = atlas.get("year_end")
    if atlas_ye is None:
        return None
    p576 = [parse_wd_time(v) for v in extract_claim_values(wd_entity, "P576")]
    p576 = [y for y in p576 if y is not None]
    if not p576:
        return None
    best = min(p576, key=lambda y: abs(atlas_ye - y))
    delta = atlas_ye - best
    abs_d = abs(delta)
    if abs_d <= 10:
        return None
    severity = "LOW"
    if abs_d > 50:
        severity = "HIGH"
    elif abs_d > 20:
        severity = "MED"
    return {
        "field": "year_end",
        "atlas": atlas_ye,
        "wikidata": best,
        "wikidata_all": p576,
        "delta": delta,
        "abs_delta": abs_d,
        "severity": severity,
    }


def check_capital(atlas: dict, wd_entity: dict, client: WDClient) -> list[dict]:
    """Verify capital name + coordinates via P36 → P625."""
    diffs: list[dict] = []
    p36_list = extract_claim_values(wd_entity, "P36")
    if not p36_list:
        return diffs
    atlas_cap = atlas.get("capital_name")
    atlas_lat = atlas.get("capital_lat")
    atlas_lon = atlas.get("capital_lon")
    if atlas_cap is None and atlas_lat is None:
        # No AtlasPI data; skip but note opportunity
        diffs.append({
            "field": "capital",
            "atlas": None,
            "wikidata": p36_list[0],
            "note": "atlas has no capital, wikidata has P36 → backfill candidate",
            "severity": "LOW",
        })
        return diffs

    # Find best match capital from P36 list
    best_cap_match = None
    best_cap_dist = None
    best_name_match = None
    for cap_qid in p36_list[:5]:
        cap = client.get_entity(cap_qid)
        if not cap:
            continue
        cap_label = label_of(cap, ["en", atlas.get("name_original_lang") or "en"])
        cap_coords = extract_claim_values(cap, "P625")
        # name check
        if atlas_cap and cap_label and labels_similar(atlas_cap, cap_label):
            best_name_match = cap_label
        # coord check
        if atlas_lat is not None and atlas_lon is not None and cap_coords:
            for c in cap_coords:
                if not (isinstance(c, tuple) and c[0] is not None):
                    continue
                dist = haversine_km(atlas_lat, atlas_lon, c[0], c[1])
                if best_cap_dist is None or dist < best_cap_dist:
                    best_cap_dist = dist
                    best_cap_match = (cap_qid, cap_label, c)

    # Emit name diff if atlas has capital but wikidata doesn't match
    if atlas_cap and not best_name_match and p36_list:
        first_cap = client.get_entity(p36_list[0])
        first_label = label_of(first_cap, ["en"]) if first_cap else p36_list[0]
        # check aliases too
        all_names = [first_label] if first_label else []
        if first_cap:
            all_names.extend(aliases_of(first_cap, ["en", atlas.get("name_original_lang") or "en"]))
        name_ok = any(labels_similar(atlas_cap, n) for n in all_names if n)
        if not name_ok:
            diffs.append({
                "field": "capital_name",
                "atlas": atlas_cap,
                "wikidata": first_label,
                "wikidata_qid": p36_list[0],
                "severity": "MED",
                "note": f"AtlasPI capital '{atlas_cap}' vs Wikidata P36 '{first_label}'",
            })

    # Coordinate diff
    if best_cap_dist is not None:
        if best_cap_dist > 50:
            sev = "HIGH" if best_cap_dist > 200 else "MED"
            diffs.append({
                "field": "capital_coord",
                "atlas": {"lat": atlas_lat, "lon": atlas_lon},
                "wikidata": {"lat": best_cap_match[2][0], "lon": best_cap_match[2][1], "qid": best_cap_match[0]},
                "km_difference": round(best_cap_dist, 1),
                "severity": sev,
            })

    return diffs


def find_coord_autofix(
    atlas_lat: float,
    atlas_lon: float,
    wd_lat: float,
    wd_lon: float,
) -> tuple[float, float] | None:
    """If the current atlas coord is clearly a typo, suggest a fix.

    Try:
    - swap (lat ↔ lon): common mistake when data entry reversed axes
    - negate lat or lon: sign flip typo
    - combine swap + negation

    Accept only if the fixed coord is within 20km of Wikidata.
    """
    original_dist = haversine_km(atlas_lat, atlas_lon, wd_lat, wd_lon)
    if original_dist <= 1000:
        return None  # not a typo-level drift

    candidates = [
        (atlas_lon, atlas_lat),          # swap
        (-atlas_lat, atlas_lon),         # negate lat
        (atlas_lat, -atlas_lon),         # negate lon
        (-atlas_lat, -atlas_lon),        # negate both
        (atlas_lon, -atlas_lat),         # swap + negate lat
        (-atlas_lon, atlas_lat),         # swap + negate lon
        (-atlas_lon, -atlas_lat),        # swap + negate both
    ]
    best = None
    best_dist = 1e12
    for c_lat, c_lon in candidates:
        if not (-90 <= c_lat <= 90 and -180 <= c_lon <= 180):
            continue
        d = haversine_km(c_lat, c_lon, wd_lat, wd_lon)
        if d < best_dist:
            best_dist = d
            best = (c_lat, c_lon)
    if best is not None and best_dist <= 20:
        return best
    return None


# ─── Main ──────────────────────────────────────────────────────────────

def run_drift_check(
    matches: list[dict],
    entities_by_id: dict[int, dict],
    client: WDClient,
    threshold: float = 0.85,
) -> list[dict]:
    """Per ogni match con score ≥threshold, esegui drift checks."""
    results: list[dict] = []
    relevant = [m for m in matches if m["score"] >= threshold and m["wikidata_qid"]]
    logger.info("drift check on %d entities (score ≥ %.2f)", len(relevant), threshold)
    for i, m in enumerate(relevant):
        if i and i % 50 == 0:
            logger.info("progress %d/%d (http=%d cache=%d)", i, len(relevant), client.http_calls, client.cache_hits)
        entity_id = m["entity_id"]
        atlas = entities_by_id.get(entity_id)
        if not atlas:
            continue
        qid = m["wikidata_qid"]
        wd = client.get_entity(qid)
        if not wd:
            continue
        diffs: list[dict] = []
        ys = check_year_start(atlas, wd)
        if ys:
            diffs.append(ys)
        ye = check_year_end(atlas, wd)
        if ye:
            diffs.append(ye)
        diffs.extend(check_capital(atlas, wd, client))
        if not diffs:
            continue
        results.append({
            "entity_id": entity_id,
            "name_original": atlas["name_original"],
            "entity_type": atlas["entity_type"],
            "wikidata_qid": qid,
            "wikidata_label": m.get("wikidata_label"),
            "score": m["score"],
            "diffs": diffs,
        })
    return results


def generate_autofixable(drift_results: list[dict]) -> list[dict]:
    """Genera patch per fix autofixable (coord typo only)."""
    patches: list[dict] = []
    for res in drift_results:
        for d in res["diffs"]:
            if d["field"] != "capital_coord":
                continue
            if d["severity"] != "HIGH":
                continue
            km = d.get("km_difference", 0)
            if km <= 1000:
                continue
            atlas = d["atlas"]
            wd = d["wikidata"]
            fix = find_coord_autofix(atlas["lat"], atlas["lon"], wd["lat"], wd["lon"])
            if fix is None:
                continue
            patches.append({
                "resource": "entity",
                "id": res["entity_id"],
                "field": "capital_lat",
                "new_value": fix[0],
                "rationale": (
                    f"v6.70 audit_v4 Fase B: capital coord typo detected "
                    f"({atlas['lat']},{atlas['lon']} {km:.0f}km from Wikidata "
                    f"{wd['lat']},{wd['lon']}). Flip→ {fix[0]},{fix[1]} matches "
                    f"within 20km."
                ),
                "source": f"Wikidata {res['wikidata_qid']}",
                "audit_ref": "audit_v4/fase_b",
            })
            patches.append({
                "resource": "entity",
                "id": res["entity_id"],
                "field": "capital_lon",
                "new_value": fix[1],
                "rationale": (
                    f"v6.70 audit_v4 Fase B: capital coord typo detected, paired "
                    f"with capital_lat fix. See lat patch rationale."
                ),
                "source": f"Wikidata {res['wikidata_qid']}",
                "audit_ref": "audit_v4/fase_b",
            })
    return patches


def render_report(drift_results: list[dict], total_checked: int, autofix_count: int) -> str:
    """Genera il markdown report Fase B."""
    # Classifica
    by_sev = {"HIGH": [], "MED": [], "LOW": []}
    by_field = {"year_start": [], "year_end": [], "capital_name": [], "capital_coord": [], "capital": []}
    for r in drift_results:
        for d in r["diffs"]:
            sev = d.get("severity", "LOW")
            by_sev.setdefault(sev, []).append((r, d))
            by_field.setdefault(d["field"], []).append((r, d))

    total_diffs = sum(len(r["diffs"]) for r in drift_results)
    entities_with_diff = len(drift_results)

    lines: list[str] = []
    lines.append("# Audit v4 — Fase B: Drift Report (Wikidata ↔ AtlasPI)\n")
    lines.append("**Data**: v6.70 post-bootstrap Fase A.\n")
    lines.append("**Scopo**: identificare discrepanze tra AtlasPI e Wikidata sui ")
    lines.append("campi chiave (anno inizio/fine, capitale, coordinate capitale). ")
    lines.append("I risultati sono segnali di drift, NON errori certificati — ")
    lines.append("Wikidata può avere convention diverse o bias. Ogni HIGH va ")
    lines.append("valutato manualmente (Fase C).\n\n")

    lines.append("## Stats\n")
    lines.append(f"- Entità con Wikidata Q-ID controllate: **{total_checked}**\n")
    lines.append(f"- Entità con ≥1 drift: **{entities_with_diff}**\n")
    lines.append(f"- Drift totali: **{total_diffs}**\n")
    lines.append(f"  - HIGH: {len(by_sev.get('HIGH', []))}\n")
    lines.append(f"  - MED: {len(by_sev.get('MED', []))}\n")
    lines.append(f"  - LOW: {len(by_sev.get('LOW', []))}\n")
    lines.append(f"- Patch autofixable generate: **{autofix_count}**\n\n")

    lines.append("## Distribuzione per campo\n\n")
    lines.append("| Campo | HIGH | MED | LOW | Totale |\n")
    lines.append("|-------|------|-----|-----|--------|\n")
    for field in ["year_start", "year_end", "capital_name", "capital_coord", "capital"]:
        hi = sum(1 for _, d in by_field.get(field, []) if d.get("severity") == "HIGH")
        me = sum(1 for _, d in by_field.get(field, []) if d.get("severity") == "MED")
        lo = sum(1 for _, d in by_field.get(field, []) if d.get("severity") == "LOW")
        tot = len(by_field.get(field, []))
        if tot == 0:
            continue
        lines.append(f"| {field} | {hi} | {me} | {lo} | {tot} |\n")
    lines.append("\n")

    # Top HIGH drift
    high = by_sev.get("HIGH", [])
    # sort by abs_delta (year) or km_difference desc
    def _rank_key(pair):
        r, d = pair
        return d.get("abs_delta", d.get("km_difference", 0))
    high.sort(key=_rank_key, reverse=True)

    lines.append(f"## Top {min(50, len(high))} HIGH drift (review urgenti)\n\n")
    for i, (r, d) in enumerate(high[:50], 1):
        name = r["name_original"]
        qid = r["wikidata_qid"]
        label = r.get("wikidata_label") or ""
        field = d["field"]
        sev = d["severity"]
        if field in ("year_start", "year_end"):
            atlas_v = d["atlas"]
            wd_v = d["wikidata"]
            delta = d["abs_delta"]
            lines.append(
                f"{i}. **[{r['entity_id']}]** {name} ({r['entity_type']}) — "
                f"{field}: AtlasPI={atlas_v} vs Wikidata={wd_v} (**Δ={delta}y**, {sev}). "
                f"Ref: [{qid}](https://www.wikidata.org/wiki/{qid}) {label}\n"
            )
        elif field == "capital_coord":
            km = d.get("km_difference", 0)
            lines.append(
                f"{i}. **[{r['entity_id']}]** {name} — "
                f"capital coord Δ={km}km (AtlasPI={d['atlas']}, Wikidata={d['wikidata']}). "
                f"Ref: [{qid}](https://www.wikidata.org/wiki/{qid}) {label}\n"
            )
        elif field == "capital_name":
            lines.append(
                f"{i}. **[{r['entity_id']}]** {name} — "
                f"capital AtlasPI='{d['atlas']}' vs Wikidata='{d['wikidata']}'. "
                f"Ref: [{qid}](https://www.wikidata.org/wiki/{qid}) {label}\n"
            )
        else:
            lines.append(f"{i}. **[{r['entity_id']}]** {name} — {field}: {d}\n")
    lines.append("\n")

    # MED drift
    med = by_sev.get("MED", [])
    med.sort(key=_rank_key, reverse=True)
    if med:
        lines.append(f"## MED drift ({len(med)} totali, mostro primi 30)\n\n")
        for i, (r, d) in enumerate(med[:30], 1):
            field = d["field"]
            if field in ("year_start", "year_end"):
                lines.append(
                    f"{i}. **[{r['entity_id']}]** {r['name_original']} — "
                    f"{field}: {d['atlas']} vs {d['wikidata']} (Δ={d['abs_delta']}y). "
                    f"[{r['wikidata_qid']}]\n"
                )
            elif field == "capital_coord":
                lines.append(
                    f"{i}. **[{r['entity_id']}]** {r['name_original']} — "
                    f"capital coord Δ={d.get('km_difference')}km. [{r['wikidata_qid']}]\n"
                )
            elif field == "capital_name":
                lines.append(
                    f"{i}. **[{r['entity_id']}]** {r['name_original']} — "
                    f"capital '{d['atlas']}' vs '{d['wikidata']}'. [{r['wikidata_qid']}]\n"
                )
    lines.append("\n")

    # Pattern analysis
    lines.append("## Pattern systemici\n\n")
    # Year start bias
    ys_all = [d for _, d in by_field.get("year_start", [])]
    if ys_all:
        deltas = [d["delta"] for d in ys_all]
        if deltas:
            avg = sum(deltas) / len(deltas)
            pos = sum(1 for x in deltas if x > 0)
            neg = sum(1 for x in deltas if x < 0)
            lines.append(f"- **year_start bias**: media Δ = {avg:.1f}y ({pos} AtlasPI>Wikidata, {neg} AtlasPI<Wikidata) su {len(deltas)} diff\n")
    ye_all = [d for _, d in by_field.get("year_end", [])]
    if ye_all:
        deltas = [d["delta"] for d in ye_all]
        if deltas:
            avg = sum(deltas) / len(deltas)
            pos = sum(1 for x in deltas if x > 0)
            neg = sum(1 for x in deltas if x < 0)
            lines.append(f"- **year_end bias**: media Δ = {avg:.1f}y ({pos} AtlasPI>Wikidata, {neg} AtlasPI<Wikidata) su {len(deltas)} diff\n")

    lines.append("\n## Note importanti\n\n")
    lines.append("- **Convention BCE**: Wikidata usa astronomical numbering, AtlasPI usa convention storica. Per date BCE può esserci offset sistematico ±1y.\n")
    lines.append("- **AtlasPI boundary_geojson null + Wikidata P625**: entità con capitale in AtlasPI ma senza boundary potrebbero essere backfillate via Wikidata. Vedi fase_b_drift_data.json filtrando per field='capital' note='backfill'.\n")
    lines.append("- **Capitali multiple**: P36 in Wikidata può avere multiple capitali (storico successivo/precedente). Il drift è riportato sul match più vicino.\n")

    return "".join(lines)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="Wikidata drift check")
    parser.add_argument("--matches", required=True, help="fase_a_matches.json")
    parser.add_argument("--entities", required=True, help="entities_dump.json")
    parser.add_argument("--out-report", required=True, help="fase_b_drift_report.md")
    parser.add_argument("--out-data", required=True, help="fase_b_drift_data.json")
    parser.add_argument("--out-patches", required=True, help="fase_b_autofixable.json")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--threshold", type=float, default=0.85)
    args = parser.parse_args()

    with open(args.matches, "rb") as f:
        matches = json.loads(f.read().decode("utf-8"))
    with open(args.entities, "rb") as f:
        ents = json.loads(f.read().decode("utf-8"))["entities"]
    entities_by_id = {e["id"]: e for e in ents}

    client = WDClient(offline=args.offline)
    results = run_drift_check(matches, entities_by_id, client, threshold=args.threshold)
    logger.info(
        "drift check done: entities_with_drift=%d http=%d cache=%d",
        len(results), client.http_calls, client.cache_hits,
    )

    patches = generate_autofixable(results)
    logger.info("autofixable patches: %d", len(patches))

    total_checked = sum(1 for m in matches if m["score"] >= args.threshold and m["wikidata_qid"])

    Path(args.out_data).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_data).write_text(
        json.dumps({"total_checked": total_checked, "drift_results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    Path(args.out_patches).write_text(
        json.dumps(patches, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    Path(args.out_report).write_text(
        render_report(results, total_checked, len(patches)),
        encoding="utf-8",
    )
    logger.info("wrote: report=%s data=%s patches=%s", args.out_report, args.out_data, args.out_patches)


if __name__ == "__main__":
    main()
