"""Report diagnostico del dataset AtlasPI.

Stampa a stdout un report testuale con statistiche aggregate su entità,
eventi, città, rotte commerciali, catene dinastiche, fonti e confidence
scores. Utile per verificare rapidamente lo stato del dataset dopo un
import o un merge.

Uso:
    python -m scripts.diagnose_dataset
    python scripts/diagnose_dataset.py

Output:
    Solo testo ASCII-safe (niente emoji). Per Windows impostare
    PYTHONIOENCODING=utf-8 se si stampa verso file con redirezione.

ETHICS: il report mostra anche dati "pesanti" (rotte schiaviste,
confidence score bassi, catene violente) senza edulcorarli —
coerente con ETHICS-007 / ETHICS-010.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

# Assicura che la root del progetto sia in PYTHONPATH quando lo script
# è eseguito come `python scripts/diagnose_dataset.py` (cioè NON come modulo).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.api.routes.entities import _get_continent  # noqa: E402
from src.db.database import SessionLocal  # noqa: E402
from src.db.models import (  # noqa: E402
    DynastyChain,
    EventSource,
    GeoEntity,
    HistoricalCity,
    HistoricalEvent,
    TradeRoute,
)


# ─── Helpers ─────────────────────────────────────────────────────────────

def _section(title: str) -> str:
    """Intestazione di sezione a larghezza fissa."""
    line = "=" * 72
    return f"\n{line}\n{title}\n{line}"


def _ordinal_suffix(n: int) -> str:
    """Suffisso ordinale inglese: 1st, 2nd, 3rd, 4th, ... 11th, 12th, 13th."""
    n_abs = abs(n)
    if 10 <= (n_abs % 100) <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n_abs % 10, "th")


def _century_label(year: int) -> str:
    """Restituisce l'etichetta del secolo per un anno intero.

    Convenzione: il I secolo CE va da 1 a 100, il II secolo da 101 a 200,
    ecc. Per anni BCE usiamo la stessa logica speculare: da -100 a -1 è
    il I secolo BCE, da -200 a -101 il II secolo BCE, ecc. L'anno 0 non
    esiste convenzionalmente; qui lo consideriamo come I sec. BCE/CE a
    seconda del segno (non dovrebbe comparire nei dati reali).
    """
    if year > 0:
        century_num = (year - 1) // 100 + 1
        era = "CE"
    else:
        # BCE: -1..-100 = 1st BCE, -101..-200 = 2nd BCE
        century_num = (-year - 1) // 100 + 1
        era = "BCE"
    return f"{century_num}{_ordinal_suffix(century_num)} century {era}"


def _century_sort_key(label: str) -> tuple[int, int]:
    """Ordina secoli cronologicamente: BCE antichi -> CE recenti."""
    is_bce = label.endswith("BCE")
    # "21st century CE" -> 21
    num_str = label.split()[0]
    num = int("".join(ch for ch in num_str if ch.isdigit()))
    # BCE: più alto il numero = più antico -> chiave negativa decrescente.
    # CE: più alto il numero = più recente -> chiave positiva crescente.
    return (0 if is_bce else 1, -num if is_bce else num)


def _format_table(rows: list[tuple[str, int]], key_header: str, value_header: str = "Count") -> str:
    """Formatta due colonne (label, count) come tabella ASCII."""
    if not rows:
        return "  (no data)"
    key_width = max(len(key_header), max(len(str(k)) for k, _ in rows))
    val_width = max(len(value_header), max(len(str(v)) for _, v in rows))
    lines = [
        f"  {key_header.ljust(key_width)}  {value_header.rjust(val_width)}",
        f"  {'-' * key_width}  {'-' * val_width}",
    ]
    for k, v in rows:
        lines.append(f"  {str(k).ljust(key_width)}  {str(v).rjust(val_width)}")
    return "\n".join(lines)


# ─── Sezioni del report ──────────────────────────────────────────────────

def report_entities_by_continent(db) -> str:
    """Totale entità per continente (calcolato dalle coordinate delle capitali)."""
    entities = db.query(
        GeoEntity.capital_lat, GeoEntity.capital_lon
    ).all()
    counts: Counter[str] = Counter()
    for lat, lon in entities:
        counts[_get_continent(lat, lon)] += 1
    rows = sorted(counts.items(), key=lambda t: -t[1])
    out = [_section("Entities by continent"), f"  Total entities: {sum(counts.values())}", ""]
    out.append(_format_table(rows, "Continent"))
    return "\n".join(out)


def report_events_by_century(db) -> str:
    """Totale eventi per secolo (secoli negativi segnati BCE)."""
    years = [y for (y,) in db.query(HistoricalEvent.year).all()]
    counts: Counter[str] = Counter()
    for y in years:
        counts[_century_label(y)] += 1
    rows = sorted(counts.items(), key=lambda t: _century_sort_key(t[0]))
    out = [_section("Events by century"), f"  Total events: {len(years)}", ""]
    out.append(_format_table(rows, "Century"))
    return "\n".join(out)


def report_cities_by_type(db) -> str:
    """Totale città per city_type."""
    rows = (
        db.query(HistoricalCity.city_type)
        .all()
    )
    counts: Counter[str] = Counter(r[0] for r in rows)
    sorted_rows = sorted(counts.items(), key=lambda t: -t[1])
    out = [_section("Cities by type"), f"  Total cities: {sum(counts.values())}", ""]
    out.append(_format_table(sorted_rows, "City type"))
    return "\n".join(out)


def report_routes_by_type(db) -> str:
    """Totale rotte per route_type + conteggio involves_slavery=True."""
    rows = db.query(TradeRoute.route_type, TradeRoute.involves_slavery).all()
    counts: Counter[str] = Counter(r[0] for r in rows)
    slavery_total = sum(1 for _, s in rows if s)
    sorted_rows = sorted(counts.items(), key=lambda t: -t[1])
    out = [
        _section("Trade routes by type"),
        f"  Total routes: {sum(counts.values())}",
        f"  Routes with involves_slavery=true: {slavery_total}",
        "",
    ]
    out.append(_format_table(sorted_rows, "Route type"))
    return "\n".join(out)


def report_chains_by_type(db) -> str:
    """Totale catene dinastiche per chain_type."""
    rows = db.query(DynastyChain.chain_type).all()
    counts: Counter[str] = Counter(r[0] for r in rows)
    sorted_rows = sorted(counts.items(), key=lambda t: -t[1])
    out = [_section("Dynasty chains by type"), f"  Total chains: {sum(counts.values())}", ""]
    out.append(_format_table(sorted_rows, "Chain type"))
    return "\n".join(out)


def report_lowest_confidence_entities(db, limit: int = 10) -> str:
    """Top 10 entità con confidence_score più basso."""
    rows = (
        db.query(
            GeoEntity.id,
            GeoEntity.name_original,
            GeoEntity.entity_type,
            GeoEntity.status,
            GeoEntity.confidence_score,
        )
        .order_by(GeoEntity.confidence_score.asc())
        .limit(limit)
        .all()
    )
    out = [_section(f"Top {limit} entities with lowest confidence_score")]
    if not rows:
        out.append("  (no entities)")
        return "\n".join(out)
    # Tabella custom a 4 colonne.
    id_w = max(2, max(len(str(r[0])) for r in rows))
    name_w = max(4, min(40, max(len(r[1]) for r in rows)))
    type_w = max(4, max(len(r[2]) for r in rows))
    status_w = max(6, max(len(r[3]) for r in rows))
    header = (
        f"  {'ID'.rjust(id_w)}  "
        f"{'Name'.ljust(name_w)}  "
        f"{'Type'.ljust(type_w)}  "
        f"{'Status'.ljust(status_w)}  "
        f"{'Score'.rjust(6)}"
    )
    sep = (
        f"  {'-' * id_w}  "
        f"{'-' * name_w}  "
        f"{'-' * type_w}  "
        f"{'-' * status_w}  "
        f"{'-' * 6}"
    )
    out.extend([header, sep])
    for eid, name, etype, status, score in rows:
        name_trunc = name if len(name) <= name_w else name[: name_w - 1] + "~"
        out.append(
            f"  {str(eid).rjust(id_w)}  "
            f"{name_trunc.ljust(name_w)}  "
            f"{etype.ljust(type_w)}  "
            f"{status.ljust(status_w)}  "
            f"{f'{score:.2f}'.rjust(6)}"
        )
    return "\n".join(out)


def report_top_event_sources(db, limit: int = 5) -> str:
    """Top 5 fonti più referenziate dagli eventi.

    Aggrega dalla tabella event_sources (EventSource.citation), che è la
    sorgente di verità per le citazioni degli eventi. Il prompt originale
    menziona "events.sources JSON"; nello schema reale le citazioni sono
    normalizzate in una tabella relazionale — aggrego lì.
    """
    rows = db.query(EventSource.citation).all()
    counts: Counter[str] = Counter()
    for (citation,) in rows:
        # Gestione difensiva: se qualcuno inserisce JSON in citation.
        if citation is None:
            continue
        cit = citation.strip()
        if not cit:
            continue
        # Se il campo fosse stato popolato come JSON array, splittalo.
        if cit.startswith("[") and cit.endswith("]"):
            try:
                arr = json.loads(cit)
                for item in arr:
                    if isinstance(item, str) and item.strip():
                        counts[item.strip()] += 1
                    elif isinstance(item, dict) and item.get("citation"):
                        counts[str(item["citation"]).strip()] += 1
                continue
            except (json.JSONDecodeError, TypeError):
                pass
        counts[cit] += 1

    top = counts.most_common(limit)
    out = [_section(f"Top {limit} most-referenced event sources")]
    if not top:
        out.append("  (no event sources in dataset)")
        return "\n".join(out)

    # Trunca citation lunghe per leggibilità.
    max_name_w = 80
    rank_w = len(str(len(top)))
    count_w = max(5, max(len(str(c)) for _, c in top))
    for i, (citation, count) in enumerate(top, 1):
        cit_display = citation if len(citation) <= max_name_w else citation[: max_name_w - 1] + "~"
        out.append(f"  {str(i).rjust(rank_w)}. [{str(count).rjust(count_w)}]  {cit_display}")
    return "\n".join(out)


# ─── Entry point ─────────────────────────────────────────────────────────

def main() -> int:
    # Incoraggia UTF-8 anche su Windows quando lo stdout è redirezionato.
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        # Python < 3.7 o stream non-riconfigurabile: ignora.
        pass

    db = SessionLocal()
    try:
        print("AtlasPI dataset diagnostic report")
        print("=" * 72)
        print(report_entities_by_continent(db))
        print(report_events_by_century(db))
        print(report_cities_by_type(db))
        print(report_routes_by_type(db))
        print(report_chains_by_type(db))
        print(report_lowest_confidence_entities(db, limit=10))
        print(report_top_event_sources(db, limit=5))
        print()
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
