"""Fix dei chain_links che puntano a entita' deprecate + follow-up ETHICS-012.

Contesto (2026-07-02): le catene 99/100/101/106 (aggiunte DOPO il merge
duplicati v6.85) linkavano 5 entita' deprecate — l'ingest risolveva i nomi
senza controllare lo status (guard ora aggiunto in ingest_chains). Le catene
"resuscitavano" cosi' i duplicati nei risultati (timeline, compare, snapshot).

# ETHICS/ADR-005: deprecated = duplicato/superseduto, mai un nodo di catena.
# I 4 re-point vanno alla PRIMARY del merge v6.85 (stessa mappa:
# 855→24, 847→27, 477→143, 849→12 — nomi nativi, ETHICS-001).
# Meroe (552, secondary di 52 Kush GIA' presente in catena a seq1) non ha
# una primary distinta → il link viene RIMOSSO e la fase meroitica resta
# documentata nelle note della catena (non e' una cancellazione: e' la
# stessa regola del Pass 4 del merge v6.85 — dup primary+secondary nella
# stessa catena → il link secondary si elimina).

Include inoltre i follow-up prod-side ereditati da ETHICS-012:
  - cap ETHICS-003: status='disputed' → confidence ≤ 0.70 (prod + JSON);
  - name_variants mancanti in prod per le 4 entita' aggiunte in v6.99.94
    (1037 Premier Empire, 1038 Afsharid, 1039 Old Babylonian, 1040 Early
    Cholas) — INSERT da batch_36 (fonte unica).

Dual-write: edita i JSON (chains + entities per il cap) ED emette
``scripts/sql_chain_deprecated_fixes.sql`` per la prod.

Usage: PYTHONUTF8=1 python -m scripts.apply_chain_deprecated_fixes
"""

from __future__ import annotations

import json
from pathlib import Path

SQL_OUT = Path("scripts/sql_chain_deprecated_fixes.sql")

# name deprecato (JSON) → (nome primary JSON/prod, id prod primary, id prod deprecato)
REPOINT = {
    "Mengist Ityop'p'ya": ("የኢትዮጵያ ንጉሠ ነገሥት መንግሥት", 24, 855),   # chain 100
    "هخامنشیان": ("Xšāça", 27, 847),                              # chain 101
    "دولت غزنویان": ("غزنویان", 143, 477),                        # chain 106
    "سلطنت مغلیہ": ("مغلیہ سلطنت", 12, 849),                      # chain 106
}
CHAIN_IDS = {"Mengist Ityop'p'ya": 100, "هخامنشیان": 101, "دولت غزنویان": 106, "سلطنت مغلیہ": 106}

KUSH_CHAIN_OLD_NAME = "Nile Valley / Kush dynastic trunk: Kerma → Kush → Napata → Meroe"
KUSH_CHAIN_NEW_NAME = "Nile Valley / Kush dynastic trunk: Kerma → Kush → Napata"
KUSH_NOTE_SUFFIX = (
    " NOTE (ADR-005/ETHICS-001, 2026-07-02): the Meroitic-phase node was removed "
    "from this chain because the 'Meroe' entity was deprecated as a duplicate of "
    "Kush (v6.85 merge map 52←552), which is already this chain's seq-1 node and "
    "whose span (-1070..350) includes the Meroitic phase (c. -300..350, capital "
    "at Medewi/Meroë, Meroitic script, iron industry, ruling Kandakes). The phase "
    "remains part of the historical record via the Kush entity and the Napata "
    "node; a dedicated native-named Meroitic-phase entity (like the Napata one) "
    "is open future work, not an erasure."
)

CAP = 0.70  # ETHICS-003: territori/entita' disputed ≤ 0.70


def _newline_of(path: Path) -> str:
    return "\r\n" if b"\r\n" in path.read_bytes() else "\n"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    with path.open("w", encoding="utf-8", newline=_newline_of(path)) as f:
        f.write(text)


def _sql_str(v) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def edit_chains() -> None:
    # 1. batch_21: chain 99 (rimozione Meroe + rename) e chain 100 (repoint)
    p21 = Path("data/chains/batch_21_nile_valley_ethiopia.json")
    b21 = _load(p21)
    kush = next(c for c in b21 if c["name"] == KUSH_CHAIN_OLD_NAME)
    before = len(kush["links"])
    kush["links"] = [lk for lk in kush["links"] if lk["entity_name"] != "Meroe"]
    if len(kush["links"]) != before - 1:
        raise SystemExit("chain 99: link 'Meroe' non trovato")
    kush["name"] = KUSH_CHAIN_NEW_NAME
    if KUSH_NOTE_SUFFIX.strip() not in (kush.get("ethical_notes") or ""):
        kush["ethical_notes"] = (kush.get("ethical_notes") or "") + KUSH_NOTE_SUFFIX

    eth = next(c for c in b21 if c["name"].startswith("Ethiopian state trunk"))
    hits = 0
    for lk in eth["links"]:
        if lk["entity_name"] == "Mengist Ityop'p'ya":
            lk["entity_name"] = REPOINT["Mengist Ityop'p'ya"][0]
            hits += 1
    if hits != 1:
        raise SystemExit("chain 100: link Mengist non trovato")
    _save(p21, b21)

    # 2. batch_22: chain 101
    p22 = Path("data/chains/batch_22_ancient_near_east_branches.json")
    b22 = _load(p22)
    hits = 0
    for c in b22:
        for lk in c.get("links", []):
            if lk["entity_name"] == "هخامنشیان":
                lk["entity_name"] = REPOINT["هخامنشیان"][0]
                hits += 1
    if hits != 1:
        raise SystemExit(f"chain 101: attesi 1 hit, trovati {hits}")
    _save(p22, b22)

    # 3. batch_24: chain 106 (2 repoint)
    p24 = Path("data/chains/batch_24_indian_subcontinent.json")
    b24 = _load(p24)
    hits = 0
    for c in b24:
        for lk in c.get("links", []):
            if lk["entity_name"] in ("دولت غزنویان", "سلطنت مغلیہ"):
                lk["entity_name"] = REPOINT[lk["entity_name"]][0]
                hits += 1
    if hits != 2:
        raise SystemExit(f"chain 106: attesi 2 hit, trovati {hits}")
    _save(p24, b24)


def cap_disputed_in_json() -> list[str]:
    capped: list[str] = []
    for path in sorted(Path("data/entities").glob("*.json")):
        data = _load(path)
        touched = False
        for ent in data:
            if ent.get("status") == "disputed" and float(ent.get("confidence_score", 0)) > CAP:
                capped.append(f"{ent['name_original'][:45]} {ent['confidence_score']} -> {CAP} ({path.name})")
                ent["confidence_score"] = CAP
                touched = True
        if touched:
            _save(path, data)
    return capped


def emit_sql() -> None:
    b36 = _load(Path("data/entities/batch_36_prod_reconciliation.json"))
    variants_targets = {
        "Premier Empire français": 1037,
        "افشاریان": 1038,
        "𒆍𒀭𒊏𒆠 (Old Babylonian)": 1039,
        "சோழர் (Sangam-era)": 1040,
    }

    sql: list[str] = [
        "-- v6.99.107 — chain_links → entita' deprecate: fix + follow-up ETHICS-012.",
        "-- Generato da scripts/apply_chain_deprecated_fixes.py — NON editare a mano.",
        "-- Dual-write: questo SQL allinea la prod; i JSON allineano il fresh-seed.",
        "BEGIN;",
        "",
        "-- ── 1. Re-point dei 4 link a entita' deprecate → primary (mappa merge v6.85) ──",
    ]
    for dep_name, (new_name, primary_id, dep_id) in REPOINT.items():
        cid = CHAIN_IDS[dep_name]
        sql.append(
            f"UPDATE chain_links SET entity_id = {primary_id} "
            f"WHERE chain_id = {cid} AND entity_id = {dep_id};  -- {dep_name} → {new_name}"
        )
    sql += [
        "",
        "-- ── 2. Chain 99: rimozione link Meroe (552, dup di Kush 52 gia' in catena) ──",
        "DELETE FROM chain_links WHERE chain_id = 99 AND entity_id = 552;",
        f"UPDATE dynasty_chains SET name = {_sql_str(KUSH_CHAIN_NEW_NAME)} WHERE id = 99;",
        f"UPDATE dynasty_chains SET ethical_notes = COALESCE(ethical_notes, '') || {_sql_str(KUSH_NOTE_SUFFIX)} "
        "WHERE id = 99 AND COALESCE(ethical_notes, '') NOT LIKE '%ADR-005/ETHICS-001, 2026-07-02%';",
        "",
        "-- ── 3. Cap ETHICS-003: disputed ≤ 0.70 (follow-up #3 di ETHICS-012) ──",
        f"UPDATE geo_entities SET confidence_score = {CAP} WHERE status = 'disputed' AND confidence_score > {CAP};",
        "",
        "-- ── 4. name_variants mancanti in prod (follow-up #5 di ETHICS-012, fonte batch_36) ──",
    ]
    for ent in b36:
        target_id = variants_targets.get(ent.get("name_original"))
        if target_id is None:
            continue
        for nv in ent.get("name_variants", []):
            sql.append(
                "INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)"
                f"\n  SELECT {target_id}, {_sql_str(nv['name'])}, {_sql_str(nv['lang'])},"
                f" {_sql_str(nv.get('period_start'))}, {_sql_str(nv.get('period_end'))},"
                f" {_sql_str(nv.get('context'))}, {_sql_str(nv.get('source'))}"
                f"\n  WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = {target_id} AND name = {_sql_str(nv['name'])});"
            )

    sql += [
        "",
        "-- ── guard finale ──",
        "DO $$",
        "DECLARE bad int;",
        "BEGIN",
        "  SELECT count(*) INTO bad FROM chain_links cl JOIN geo_entities g ON g.id = cl.entity_id",
        "  WHERE g.status = 'deprecated';",
        "  IF bad > 0 THEN RAISE EXCEPTION 'chain_links verso entita'' deprecate: %', bad; END IF;",
        "",
        "  SELECT count(*) INTO bad FROM (",
        "    SELECT chain_id, count(*) n, max(sequence_order) mx, min(sequence_order) mn",
        "    FROM chain_links WHERE chain_id IN (99,100,101,106) GROUP BY chain_id",
        "  ) q WHERE mn <> 0 OR mx <> n - 1;",
        "  IF bad > 0 THEN RAISE EXCEPTION 'sequence_order non contiguo in % catene', bad; END IF;",
        "",
        "  SELECT count(*) INTO bad FROM geo_entities WHERE status = 'disputed' AND confidence_score > 0.70;",
        "  IF bad > 0 THEN RAISE EXCEPTION 'cap ETHICS-003 non applicato su % entita''', bad; END IF;",
        "",
        "  SELECT count(*) INTO bad FROM name_variants WHERE entity_id IN (1037,1038,1039,1040);",
        "  IF bad < 4 THEN RAISE EXCEPTION 'name_variants follow-up #5 incompleto (%)', bad; END IF;",
        "END $$;",
        "",
        "SELECT cl.chain_id, cl.sequence_order, cl.entity_id, g.name_original, g.status",
        "FROM chain_links cl JOIN geo_entities g ON g.id = cl.entity_id",
        "WHERE cl.chain_id IN (99,100,101,106) ORDER BY cl.chain_id, cl.sequence_order;",
        "",
        "COMMIT;",
    ]
    SQL_OUT.write_text("\n".join(sql) + "\n", encoding="utf-8")


def main() -> None:
    edit_chains()
    capped = cap_disputed_in_json()
    print(f"Cap ETHICS-003 in JSON: {len(capped)} entita'")
    for c in capped:
        print("  ", c)
    emit_sql()
    print("JSON aggiornati. SQL →", SQL_OUT)


if __name__ == "__main__":
    main()
