"""Matching delle entita' AtlasPI con i confini di Natural Earth.

Strategie di match in ordine di priorita':
  1. ISO_A3 esplicito (campo entita': iso_a3 o note_iso)
  2. Match esatto sul nome (case-insensitive, accent-fold) — name_original
  3. Match esatto su qualunque name_variants[].name
  4. Match cross-language sui campi names_alt di Natural Earth
  5. Fuzzy match (rapidfuzz) sul nome e varianti, soglia 85%
  6. Capitale (lat/lon) contenuta nel polygon del paese moderno

ETHICS — vincoli forti:
  - Solo entita' moderne (year_end > 1800 oppure year_end == None E year_start > 1700)
    sono candidate al match con confini moderni di Natural Earth.
  - NON imporre boundary moderni a stati antichi.
    Esempio errato: Imperium Romanum -> Italia moderna.
    Esempio corretto: Repubblica Italiana (1946-) -> Italia.
  - Per i territori contestati (Taiwan, Western Sahara, Kashmir, Palestina,
    Crimea, Kosovo): vedi ETHICS-005-boundary-natural-earth.md.
    Il match esiste ma il record AtlasPI mantiene status='disputed' e
    ethical_notes esplicite.

Output del modulo: dict {entity_id_or_index: {boundary, ne_record, strategy, score}}
dove entity_id e' l'identificatore stabile dell'entita' AtlasPI (di solito
nome_original + year_start, dato che i batch JSON non hanno id numerici).
"""

from __future__ import annotations

import logging
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

logger = logging.getLogger(__name__)

# ─── Configuration ──────────────────────────────────────────────────────────

# ETHICS: solo entita' che esistono (in tutto o in parte) dopo il 1800
# possono essere matchate con confini moderni di Natural Earth.
# Per le entita' che terminano prima del 1800, il rischio di anacronismo
# nei confini e' troppo alto.
MIN_YEAR_END_FOR_NE_MATCH = 1800

# Per le entita' "ancora vive" (year_end == None), accettiamo se year_start
# e' >= 1700. Esempio: Sverige (1523-presente) ha senso matchare con la
# Svezia moderna anche se nasce nel XVI sec.
MIN_YEAR_START_FOR_LIVE_NE_MATCH = 1700

# Soglia minima per il fuzzy match (0-100, scala rapidfuzz)
FUZZY_THRESHOLD = 85

# ETHICS: territori contestati che richiedono ethical_notes esplicite.
# Vedi ETHICS-005. Quando viene fatto un match con uno di questi, lo
# segnaliamo nel risultato per gestione manuale a valle.
DISPUTED_ISO_CODES = {
    "TWN",  # Taiwan vs RPC
    "ESH",  # Western Sahara
    "PSE",  # Palestina (occupazione/colonizzazione israeliana)
    "XKO",  # Kosovo (riconoscimento parziale)
    "CYN",  # Cipro Nord (riconosciuta solo dalla Turchia)
    "KAS",  # Kashmir (disputa India-Pakistan-Cina)
    "SOL",  # Somaliland
}

# ─── Data structures ────────────────────────────────────────────────────────


@dataclass
class MatchResult:
    """Risultato di un tentativo di match."""

    entity_key: str  # identificatore stabile dell'entita' (name_original|year_start)
    matched: bool
    strategy: str = ""  # "iso_a3" | "exact_name" | "variant" | "alt_lang" | "fuzzy" | "capital_in_polygon"
    confidence: float = 0.0  # 0.0-1.0 (rapidfuzz score / 100, o 1.0 per match esatto)
    ne_iso_a3: Optional[str] = None
    ne_name: Optional[str] = None
    geojson: Optional[dict] = None
    is_disputed: bool = False  # ETHICS: territorio contestato
    rejection_reason: Optional[str] = None  # se matched=False
    notes: list[str] = field(default_factory=list)


# ─── Utility functions ──────────────────────────────────────────────────────


def _normalize(text: str | None) -> str:
    """Normalizza un nome per il matching: lowercase, no diacritici, no spazi multipli."""
    if not text:
        return ""
    # Decompose unicode and drop combining marks
    nfd = unicodedata.normalize("NFKD", str(text))
    no_diacritics = "".join(c for c in nfd if not unicodedata.combining(c))
    return " ".join(no_diacritics.lower().split())


def entity_key(entity: dict) -> str:
    """Genera una chiave stabile per un'entita' AtlasPI."""
    name = entity.get("name_original", "?")
    year_start = entity.get("year_start", 0)
    return f"{name}|{year_start}"


def _is_modern_eligible(entity: dict) -> tuple[bool, str]:
    """Verifica se l'entita' e' eligibile al match con Natural Earth (moderna).

    Returns: (eligible, reason)
    """
    year_end = entity.get("year_end")
    year_start = entity.get("year_start", 0)

    if year_end is None:
        # Entita' "ancora viva" / open-ended
        if year_start >= MIN_YEAR_START_FOR_LIVE_NE_MATCH:
            return True, "live_modern"
        return False, f"live_but_pre_{MIN_YEAR_START_FOR_LIVE_NE_MATCH}"

    if year_end > MIN_YEAR_END_FOR_NE_MATCH:
        return True, "ends_post_1800"

    return False, f"ends_pre_{MIN_YEAR_END_FOR_NE_MATCH}"


def _gather_entity_names(entity: dict) -> list[str]:
    """Raccoglie tutti i nomi noti dell'entita' (originale + varianti)."""
    names: list[str] = []
    name_original = entity.get("name_original")
    if name_original:
        names.append(str(name_original))
    for variant in entity.get("name_variants", []) or []:
        if isinstance(variant, dict):
            n = variant.get("name")
            if n:
                names.append(str(n))
        elif isinstance(variant, str):
            names.append(variant)
    # dedup preservando ordine
    seen = set()
    out = []
    for n in names:
        if n not in seen:
            out.append(n)
            seen.add(n)
    return out


def _gather_ne_names(ne_record: dict) -> list[str]:
    """Raccoglie tutti i nomi noti per un record Natural Earth."""
    out = []
    for key in ("name", "name_long", "name_official", "sovereign"):
        v = ne_record.get(key)
        if v:
            out.append(str(v))
    for v in (ne_record.get("names_alt") or {}).values():
        if v:
            out.append(str(v))
    # dedup
    seen = set()
    deduped = []
    for n in out:
        nn = n.strip()
        if nn and nn not in seen:
            deduped.append(nn)
            seen.add(nn)
    return deduped


def _extract_iso_hint(entity: dict) -> Optional[str]:
    """Cerca un suggerimento ISO_A3 nei campi dell'entita'.

    L'entita' AtlasPI puo' avere:
      - campo esplicito 'iso_a3'
      - 'iso_code'
      - menzione in 'ethical_notes' tipo 'ISO: ITA'
    """
    for key in ("iso_a3", "iso_code", "iso"):
        v = entity.get(key)
        if v and isinstance(v, str) and len(v) == 3:
            return v.strip().upper()

    # Ricerca in note (best-effort, conservativa)
    notes = entity.get("ethical_notes", "") or ""
    if isinstance(notes, str):
        # Cerca pattern tipo "ISO: XYZ" o "ISO_A3=XYZ"
        import re
        m = re.search(r"ISO[_ ]?A?3?\s*[:=]\s*([A-Z]{3})\b", notes)
        if m:
            return m.group(1)
    return None


# ─── Matching strategies ────────────────────────────────────────────────────


def _try_iso_match(
    entity: dict, ne_by_iso: dict[str, dict]
) -> Optional[MatchResult]:
    iso = _extract_iso_hint(entity)
    if not iso:
        return None
    rec = ne_by_iso.get(iso)
    if not rec:
        return None
    key = entity_key(entity)
    return MatchResult(
        entity_key=key,
        matched=True,
        strategy="iso_a3",
        confidence=1.0,
        ne_iso_a3=iso,
        ne_name=rec.get("name"),
        geojson=rec.get("geojson"),
        is_disputed=iso in DISPUTED_ISO_CODES,
        notes=[f"ISO match esplicito: {iso}"],
    )


def _try_exact_name_match(
    entity: dict, ne_records: list[dict]
) -> Optional[MatchResult]:
    entity_names_norm = {_normalize(n): n for n in _gather_entity_names(entity)}
    if not entity_names_norm:
        return None

    has_capital = (
        entity.get("capital_lat") is not None
        and entity.get("capital_lon") is not None
    )

    for rec in ne_records:
        for n in _gather_ne_names(rec):
            nn = _normalize(n)
            if nn and nn in entity_names_norm:
                iso = rec.get("iso_a3")
                geo = rec.get("geojson")
                # ETHICS-006: even exact-name matches require geographic
                # consistency. Colonial-era entities often share names
                # with modern countries whose borders are irrelevant
                # (e.g., "Nueva España" vs Spain). If we have a capital,
                # the NE polygon must contain it; otherwise reject.
                if has_capital and not _capital_in_geojson(entity, geo):
                    logger.debug(
                        "Exact-name match rejected (capital outside polygon): %s -> %s",
                        entity.get("name_original"), rec.get("name"),
                    )
                    continue
                return MatchResult(
                    entity_key=entity_key(entity),
                    matched=True,
                    strategy="exact_name",
                    confidence=1.0,
                    ne_iso_a3=iso,
                    ne_name=rec.get("name"),
                    geojson=geo,
                    is_disputed=(iso in DISPUTED_ISO_CODES) if iso else False,
                    notes=[f"Match esatto sul nome: '{n}' == '{entity_names_norm[nn]}'"],
                )
    return None


def _capital_in_geojson(entity: dict, geojson: dict | None) -> bool:
    """Return True iff the entity's capital coordinates fall inside geojson.

    ETHICS-006: used as a geographic sanity check for fuzzy matches.
    Protects against catastrophic name-based false positives (e.g.
    Garenganze -> Russia, Primer Imperio Mexicano -> Belgium) where the
    fuzzy scorer pattern-matches on generic tokens like "Kingdom" or
    "Empire" and picks a geographically unrelated country.
    """
    lat = entity.get("capital_lat")
    lon = entity.get("capital_lon")
    if lat is None or lon is None or not geojson:
        return False
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return False
    try:
        from shapely.geometry import Point, shape
    except ImportError:
        # Without shapely we can't validate geometrically; fail safe.
        return False
    try:
        return shape(geojson).contains(Point(float(lon), float(lat)))
    except Exception:
        return False


def _try_fuzzy_match(
    entity: dict, ne_records: list[dict], threshold: int = FUZZY_THRESHOLD
) -> Optional[MatchResult]:
    try:
        from rapidfuzz import fuzz
    except ImportError:
        logger.warning("rapidfuzz non installato — fuzzy match disabilitato")
        return None

    entity_names = _gather_entity_names(entity)
    if not entity_names:
        return None

    # ETHICS-006: fuzzy match is dangerous without a geographic guard.
    # If the entity carries capital coordinates we use them to filter
    # candidates up front: a record whose polygon does NOT contain the
    # capital cannot be a valid fuzzy match, regardless of how high the
    # name score is. An entity without capital coordinates is treated
    # conservatively — we still compute a best name match but reject if
    # we cannot verify geographic consistency.
    has_capital = (
        entity.get("capital_lat") is not None
        and entity.get("capital_lon") is not None
    )

    best: tuple[int, dict, str, str] | None = None  # (score, ne_record, ne_name, entity_name)

    for rec in ne_records:
        ne_names = _gather_ne_names(rec)
        for en in entity_names:
            en_norm = _normalize(en)
            if not en_norm:
                continue
            for nn in ne_names:
                nn_norm = _normalize(nn)
                if not nn_norm:
                    continue
                # token_set_ratio funziona meglio con nomi multi-parola
                score = max(
                    fuzz.ratio(en_norm, nn_norm),
                    fuzz.token_set_ratio(en_norm, nn_norm),
                    fuzz.partial_ratio(en_norm, nn_norm),
                )
                if score >= threshold:
                    if best is None or score > best[0]:
                        best = (score, rec, nn, en)

    if best is None:
        return None

    score, rec, ne_name, en = best
    iso = rec.get("iso_a3")

    # ETHICS-006: geographic guard. Fuzzy is only trusted when the
    # capital of the entity actually falls inside the matched NE
    # polygon. Without this check we produced 133 displaced matches
    # (Garenganze -> Russia, Mapuche -> Australia, CSA -> Italy, ...).
    if has_capital:
        if not _capital_in_geojson(entity, rec.get("geojson")):
            logger.debug(
                "Fuzzy match rejected (capital outside polygon): %s -> %s (%s)",
                entity.get("name_original"), ne_name, iso,
            )
            return None
    else:
        # No capital to validate against — refuse the fuzzy match.
        # Conservative: a name-only match with no geographic evidence
        # is the exact class of bug that produced ETHICS-006.
        logger.debug(
            "Fuzzy match rejected (no capital to validate): %s -> %s",
            entity.get("name_original"), ne_name,
        )
        return None

    return MatchResult(
        entity_key=entity_key(entity),
        matched=True,
        strategy="fuzzy",
        confidence=score / 100.0,
        ne_iso_a3=iso,
        ne_name=rec.get("name"),
        geojson=rec.get("geojson"),
        is_disputed=(iso in DISPUTED_ISO_CODES) if iso else False,
        notes=[
            f"Fuzzy match {score}%: '{en}' ~ '{ne_name}' (capital in polygon: validated)"
        ],
    )


def _try_capital_in_polygon(
    entity: dict, ne_records: list[dict]
) -> Optional[MatchResult]:
    """Match basato sul fatto che la capitale e' dentro al polygon del paese moderno.

    Strategia di fallback piu' debole — usata quando il nome non matcha ma
    la capitale e' inequivocabilmente dentro un solo paese moderno.
    """
    lat = entity.get("capital_lat")
    lon = entity.get("capital_lon")
    if lat is None or lon is None:
        return None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None

    try:
        from shapely.geometry import Point, shape
    except ImportError:
        logger.warning("shapely non installato — capital_in_polygon disabilitato")
        return None

    point = Point(float(lon), float(lat))

    matches: list[dict] = []
    for rec in ne_records:
        geom = rec.get("geojson")
        if not geom:
            continue
        try:
            shp = shape(geom)
            if shp.contains(point):
                matches.append(rec)
        except Exception:
            # Geometria invalida o malformata — skip
            continue

    # Solo se la capitale e' in UN solo paese moderno (no ambiguita')
    if len(matches) != 1:
        return None

    rec = matches[0]
    iso = rec.get("iso_a3")
    return MatchResult(
        entity_key=entity_key(entity),
        matched=True,
        strategy="capital_in_polygon",
        confidence=0.6,  # piu' bassa: match geografico, non semantico
        ne_iso_a3=iso,
        ne_name=rec.get("name"),
        geojson=rec.get("geojson"),
        is_disputed=(iso in DISPUTED_ISO_CODES) if iso else False,
        notes=[f"Capitale ({lat:.2f},{lon:.2f}) dentro al polygon di {rec.get('name')}"],
    )


# ─── Public API ─────────────────────────────────────────────────────────────


def match_entity(entity: dict, ne_by_iso: dict[str, dict]) -> MatchResult:
    """Tenta di matchare una singola entita' AtlasPI con Natural Earth.

    Applica le strategie in ordine. Restituisce sempre un MatchResult,
    matched=False se nessuna strategia ha avuto successo (o se l'entita'
    non e' eligibile per anacronismo).
    """
    key = entity_key(entity)

    # Eligibility check (anacronismo)
    eligible, reason = _is_modern_eligible(entity)
    if not eligible:
        return MatchResult(
            entity_key=key,
            matched=False,
            rejection_reason=f"not_modern_eligible:{reason}",
            notes=[
                f"ETHICS: entita' pre-moderna (year_end={entity.get('year_end')}, "
                f"year_start={entity.get('year_start')}) — no NE match per evitare anacronismo"
            ],
        )

    ne_records = list(ne_by_iso.values())

    # Strategia 1: ISO esplicito
    res = _try_iso_match(entity, ne_by_iso)
    if res:
        return res

    # Strategia 2+3+4: nomi esatti
    res = _try_exact_name_match(entity, ne_records)
    if res:
        return res

    # Strategia 5: fuzzy
    res = _try_fuzzy_match(entity, ne_records)
    if res:
        return res

    # Strategia 6: capitale nel poligono (solo se un singolo match geografico)
    res = _try_capital_in_polygon(entity, ne_records)
    if res:
        return res

    return MatchResult(
        entity_key=key,
        matched=False,
        rejection_reason="no_strategy_succeeded",
        notes=[
            f"Nessun match: tried ISO, exact, fuzzy>={FUZZY_THRESHOLD}%, capital-in-polygon"
        ],
    )


def match_natural_earth_to_entities(
    entities: Iterable[dict],
    ne_by_iso: dict[str, dict],
) -> dict[str, MatchResult]:
    """Matcha un batch di entita' con Natural Earth.

    Args:
        entities: iterable di dict entita' AtlasPI (caricati dai batch JSON).
        ne_by_iso: mapping {iso_a3: ne_record} prodotto da
            natural_earth_import.import_natural_earth().

    Returns:
        Mapping {entity_key: MatchResult} dove entity_key e' name_original|year_start.

    ETHICS: solo entita' moderne (year_end > 1800) o con continuita' storica
    chiara (year_end == None E year_start > 1700) sono candidate al match.
    NON imporre boundary moderni a stati antichi (es. impero romano con
    boundary italiani moderni = errore grave).
    """
    results: dict[str, MatchResult] = {}
    for entity in entities:
        key = entity_key(entity)
        results[key] = match_entity(entity, ne_by_iso)
    return results


def summarize_matches(results: dict[str, MatchResult]) -> dict[str, Any]:
    """Produce un sommario delle statistiche di matching."""
    total = len(results)
    matched = sum(1 for r in results.values() if r.matched)
    by_strategy: dict[str, int] = {}
    by_rejection: dict[str, int] = {}
    disputed = 0
    for r in results.values():
        if r.matched:
            by_strategy[r.strategy] = by_strategy.get(r.strategy, 0) + 1
            if r.is_disputed:
                disputed += 1
        elif r.rejection_reason:
            by_rejection[r.rejection_reason] = by_rejection.get(r.rejection_reason, 0) + 1

    return {
        "total": total,
        "matched": matched,
        "matched_pct": round(matched / total * 100, 1) if total else 0.0,
        "by_strategy": by_strategy,
        "by_rejection": by_rejection,
        "disputed_matches": disputed,
    }
