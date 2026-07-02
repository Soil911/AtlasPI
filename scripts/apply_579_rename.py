"""Rename entità #579: 'Furstentum Walachei' → 'Terra Transalpina' (ETHICS-001).

Il name_original era in TEDESCO con una giustificazione fattualmente errata
("forma tedesca usata nei documenti reali ungheresi contemporanei"): la
cancelleria ungherese medievale scriveva in LATINO — la Diploma dei Giovanniti
(1247) è latina e nomina i voivodati singolarmente ('terra Lytua', 'terra
Szeneslai'); 'Fürstentum Walachei' è storiografia tedesca MODERNA.

# ETHICS-001: in assenza di una forma scritta vernacolare (il proto-rumeno non
# aveva scrittura nel 1247-1330), il nome primario è la designazione scritta
# CONTEMPORANEA: 'Terra Transalpina' (latino di cancelleria ungherese) — un
# esonimo anch'esso, dichiarato come tale nelle note, ma contemporaneo e
# documentato, non retro-proiettato. La forma tedesca resta come name_variant.
# Cross-check ChatGPT-5.5 (log data/chatgpt_review/20260702/): conferma (a);
# caveat recepiti: Terra Transalpina è parzialmente retrospettivo per il 1247
# (la Diploma nomina i voivodati singoli) e la capitale del periodo è incerta
# (Câmpulung/Curtea de Argeș) — entrambe dichiarate nelle note.

Dual-write: batch_17_europe_medieval.json + scripts/sql_579_rename.sql.
Usage: PYTHONUTF8=1 python -m scripts.apply_579_rename
"""

from __future__ import annotations

import json
from pathlib import Path

ENTITY_PATH = Path("data/entities/batch_17_europe_medieval.json")
SQL_OUT = Path("scripts/sql_579_rename.sql")

OLD_NAME = "Furstentum Walachei"
NEW_NAME = "Terra Transalpina"
NEW_LANG = "la"

NEW_NOTES = (
    "ETHICS-001: The early Wallachian voivodates before the Battle of Posada "
    "(1330) are poorly documented and historiographically contested. Romanian "
    "national historiography emphasizes continuity with Daco-Roman populations; "
    "Hungarian historiography emphasizes Hungarian suzerainty over the region. "
    "The status 'disputed' reflects genuine scholarly uncertainty. "
    "ETHICS-001 (rename 2026-07-02): name_original is 'Terra Transalpina', the "
    "contemporary Latin designation of the Hungarian royal chancery for the "
    "trans-Carpathian Wallachian polity — an exonym, declared as such, but the "
    "only contemporary WRITTEN naming tradition (proto-Romanian had no written "
    "form in this period; the self-designation 'Țara Românească' is attested "
    "only from the 14th century and belongs to the successor entity). The 1247 "
    "Diploma of the Joannites names the component voivodates individually "
    "('terra Lytua', 'terra Szeneslai') — 'Terra Transalpina' as a unified name "
    "is partially retrospective for 1247. The previous name_original "
    "'Fürstentum Walachei' was MODERN German historiography, wrongly described "
    "as contemporary — kept as name_variant for traceability. NOTE: the capital "
    "'Curtea de Arges' is too firm for this period — early Wallachian political "
    "centers are uncertain and shifted (Câmpulung, Curtea de Argeș). "
    "ETHICS-003: This entry covers the proto-state period (1247-1330) before "
    "the established Principality of Wallachia (already in the database "
    "starting 1330). The dates and political structure of this period are "
    "genuinely uncertain. Boundary da aourednik/historical-basemaps (1279, "
    "strategy=capital_in_polygon, precision=1). CC BY 4.0.\n\n"
    "[v6.30-displaced-rollback] Boundary reverted to capital-based "
    "approximation: aourednik fuzzy match placed polygon centroid=2817km / "
    "edge=0km from capital (exceeded thresholds). Regenerated as 80.0km "
    "radius circle."
)

GERMAN_VARIANT = {
    "name": "Fürstentum Walachei",
    "lang": "de",
    "period_start": 1247,
    "period_end": 1330,
    "context": (
        "modern German historiographical name; was this record's name_original "
        "until 2026-07-02 (ETHICS-001 rename — not a contemporary form)"
    ),
    "source": None,
}
DIPLOMA_VARIANT = {
    "name": "terra Lytua / terra Szeneslai",
    "lang": "la",
    "period_start": 1247,
    "period_end": 1330,
    "context": (
        "the component voivodates (Litovoi, Seneslau) as actually named in the "
        "Diploma of the Joannites (1247), the earliest document on organized "
        "Wallachian polities"
    ),
    "source": "Diploma of the Joannites (1247), Hungarian royal chancery",
}


def _sql_str(v) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def main() -> None:
    data = json.loads(ENTITY_PATH.read_text(encoding="utf-8"))
    ent = next(e for e in data if e.get("name_original") == OLD_NAME)
    ent["name_original"] = NEW_NAME
    ent["name_original_lang"] = NEW_LANG
    ent["ethical_notes"] = NEW_NOTES
    existing_variant_names = {v["name"] for v in ent.get("name_variants", [])}
    for nv in (GERMAN_VARIANT, DIPLOMA_VARIANT):
        if nv["name"] not in existing_variant_names:
            ent["name_variants"].append(dict(nv))
    newline = "\r\n" if b"\r\n" in ENTITY_PATH.read_bytes() else "\n"
    with ENTITY_PATH.open("w", encoding="utf-8", newline=newline) as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    sql = [
        "-- v6.99.108 — rename #579 Furstentum Walachei → Terra Transalpina (ETHICS-001).",
        "-- Generato da scripts/apply_579_rename.py — NON editare a mano.",
        "BEGIN;",
        "",
        f"UPDATE geo_entities SET name_original = {_sql_str(NEW_NAME)}, "
        f"name_original_lang = {_sql_str(NEW_LANG)}, ethical_notes = {_sql_str(NEW_NOTES)} "
        f"WHERE id = 579 AND name_original = {_sql_str(OLD_NAME)};",
        "",
    ]
    for nv in (GERMAN_VARIANT, DIPLOMA_VARIANT):
        sql.append(
            "INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)"
            f"\n  SELECT 579, {_sql_str(nv['name'])}, {_sql_str(nv['lang'])}, {nv['period_start']}, "
            f"{nv['period_end']}, {_sql_str(nv['context'])}, {_sql_str(nv['source'])}"
            f"\n  WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 579 AND name = {_sql_str(nv['name'])});"
        )
    sql += [
        "",
        "DO $$ DECLARE bad int; BEGIN",
        f"  SELECT count(*) INTO bad FROM geo_entities WHERE id = 579 AND name_original <> {_sql_str(NEW_NAME)};",
        "  IF bad > 0 THEN RAISE EXCEPTION 'rename 579 non applicato'; END IF;",
        "  SELECT count(*) INTO bad FROM name_variants WHERE entity_id = 579;",
        "  IF bad < 4 THEN RAISE EXCEPTION 'variants 579 attese >= 4, trovate %', bad; END IF;",
        "END $$;",
        "",
        "SELECT id, name_original, name_original_lang, status, confidence_score FROM geo_entities WHERE id = 579;",
        "",
        "COMMIT;",
    ]
    SQL_OUT.write_text("\n".join(sql) + "\n", encoding="utf-8")
    print(f"JSON aggiornato ({ENTITY_PATH}). SQL → {SQL_OUT}")


if __name__ == "__main__":
    main()
