"""M4 — sincronizza i 14 rename nativi prod-only (v6.99.124, pattern Wadai/ETHICS-001).

Prod ha già il nome nativo; il JSON aveva ancora la forma latina come
name_original → il fresh-seed non name-matcha prod e `ingest_new_entities`
creerebbe duplicati. Qui: rename JSON name_original latino→nativo + forma
latina conservata come variante (romanizzazione), cascata dei riferimenti
per-nome in chains/events/rulers, e INSERT idempotente della variante latina
su prod (per la simmetria fresh-seed ≡ prod).

#413 (Dar Fur) è ESCLUSO: ha due record JSON ('Dar Fur' + 'Saltanat Dar Fur'),
è anche un ombreggiato → va gestito nel track dedup, non qui.

Input:  data/fixes/native_rename_queue_20260704.json (diff prod↔JSON per capitale+anno)
Output: chirurgia data/entities/* + cascata data/chains|events|rulers/*
        scripts/sql_native_rename_variants.sql (solo INSERT variante latina)

Usage: PYTHONUTF8=1 python -m scripts.apply_native_renames
"""
from __future__ import annotations

import json
from pathlib import Path

QUEUE = Path("data/fixes/native_rename_queue_20260704.json")
SQL_OUT = Path("scripts/sql_native_rename_variants.sql")

# lang code della romanizzazione per id
LATIN_LANG = {
    405: "ar-Latn", 406: "ar-Latn", 410: "ar-Latn", 411: "ar-Latn",
    420: "uk-Latn", 430: "ka-Latn", 434: "bg-Latn", 435: "sr-Latn",
    436: "grc-Latn", 438: "el-Latn", 440: "uk-Latn", 658: "ti-Latn",
    664: "bg-Latn", 736: "ar-Latn",
}
SKIP_IDS = {413}  # doppio record JSON → track dedup


def q(s):
    return "NULL" if s is None else "'" + str(s).replace("'", "''") + "'"


def load_renames():
    rows = json.loads(QUEUE.read_text(encoding="utf-8"))
    out = []
    for r in rows:
        if r["id"] in SKIP_IDS:
            continue
        out.append(r)
    # dedup per id (tieni la prima occorrenza)
    seen = set(); uniq = []
    for r in out:
        if r["id"] in seen:
            continue
        seen.add(r["id"]); uniq.append(r)
    return uniq


def rename_entity_json(rid: int, latin: str, native: str) -> bool:
    """Rinomina name_original latino→nativo nel file entità + aggiunge variante latina."""
    for p in sorted(Path("data/entities").glob("*.json")):
        raw = p.read_bytes().decode("utf-8")
        anchor = f'"name_original": "{latin}"'
        if raw.count(anchor) != 1:
            continue
        # 1) rename name_original
        raw = raw.replace(anchor, f'"name_original": "{native}"')
        # 2) aggiungi la variante latina se non già presente come variante
        #    (la aggiungo in testa all'array name_variants di QUESTO record)
        # trova il name_variants di questo record (dopo l'anchor rinominato)
        idx = raw.find(f'"name_original": "{native}"')
        vi = raw.find('"name_variants"', idx)
        # rileva newline stile
        seg = raw[vi:vi+200]
        nl = "\r\n" if "\r\n" in seg else "\n"
        # inserisci un blocco variante subito dopo l'apertura dell'array
        open_br = raw.find("[", vi)
        lang = LATIN_LANG[rid]
        if f'"{latin}"' in raw[idx:raw.find('"territory_changes"', idx) if raw.find('"territory_changes"', idx) > 0 else idx+4000]:
            # la forma latina è già una variante da qualche parte nel record → non duplicare
            already = True
        else:
            already = False
        if not already:
            var = (nl + "      {" + nl +
                   f'        "name": "{latin}",' + nl +
                   f'        "lang": "{lang}",' + nl +
                   '        "period_start": null,' + nl +
                   '        "period_end": null,' + nl +
                   '        "context": "romanizzazione (ETHICS-001; era il name_original latino prima del sync nativo v6.99.124)",' + nl +
                   '        "source": "M4 reconciliation"' + nl +
                   "      },")
            raw = raw[:open_br+1] + var + raw[open_br+1:]
        p.write_bytes(raw.encode("utf-8"))
        json.loads(raw)
        print(f"  OK entity #{rid}: {latin!r} → {native!r} [{p.name}]" + ("" if not already else " (variante già presente)"))
        return True
    raise AssertionError(f"#{rid}: anchor name_original {latin!r} non trovato (o non unico)")


def cascade_refs(latin: str, native: str):
    """Cascata dei riferimenti per-nome nei file non-entità."""
    total = 0
    for d in ("data/chains", "data/events", "data/rulers", "data/cities"):
        for p in sorted(Path(d).glob("*.json")):
            raw = p.read_bytes().decode("utf-8")
            token = f'"{latin}"'
            n = raw.count(token)
            if n == 0:
                continue
            raw = raw.replace(token, f'"{native}"')
            p.write_bytes(raw.encode("utf-8"))
            json.loads(raw)
            total += n
            print(f"  cascade {p.name}: {n}× {latin!r} → nativo")
    return total


def gen_sql(renames) -> str:
    out = ["-- v6.99.124 (M4) — aggiunge la variante latina (romanizzazione) su prod",
           "-- per simmetria fresh-seed ≡ prod. Idempotente (NOT EXISTS). Nessun rename",
           "-- prod (il name_original nativo è già corretto). psql -v ON_ERROR_STOP=1.",
           "BEGIN;", ""]
    for r in renames:
        rid, latin = r["id"], r["json_name"]
        lang = LATIN_LANG[rid]
        out.append(
            f"INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) "
            f"SELECT {rid}, {q(latin)}, {q(lang)}, NULL, NULL, "
            f"'romanizzazione (ETHICS-001; ex name_original latino, sync M4 v6.99.124)', 'M4 reconciliation' "
            f"WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = {rid} AND name = {q(latin)});")
    out += ["", "-- validazione: ogni entità ha ora la variante latina",
            "DO $$ DECLARE bad int; BEGIN",
            "  SELECT count(*) INTO bad FROM (VALUES " +
            ",".join(f"({r['id']}, {q(r['json_name'])})" for r in renames) +
            ") v(eid, nm) WHERE NOT EXISTS (SELECT 1 FROM name_variants nv WHERE nv.entity_id = v.eid AND nv.name = v.nm);",
            "  IF bad <> 0 THEN RAISE EXCEPTION '% varianti latine mancanti', bad; END IF;",
            "  RAISE NOTICE 'M4 v6.99.124 OK: 14 varianti latine sincronizzate';",
            "END $$;", "", "COMMIT;"]
    return "\n".join(out) + "\n"


def main():
    renames = load_renames()
    print(f"Rename da sincronizzare: {len(renames)} (escluso #413)")
    for r in renames:
        rename_entity_json(r["id"], r["json_name"], r["prod_name"])
        cascade_refs(r["json_name"], r["prod_name"])
    SQL_OUT.write_text(gen_sql(renames), encoding="utf-8")
    print(f"OK {SQL_OUT}")

    # fence: nessun ref di catena a nomi latini rinominati
    latin_set = {r["json_name"] for r in renames}
    for p in sorted(Path("data/chains").glob("*.json")):
        raw = p.read_text(encoding="utf-8")
        for nm in latin_set:
            assert f'"{nm}"' not in raw, f"ref residuo {nm!r} in {p.name}"
    print("OK fence: nessun ref latino residuo nelle catene")


if __name__ == "__main__":
    main()
