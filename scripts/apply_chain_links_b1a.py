"""Apply B1a chain-link extensions (JSON source + emit prod SQL).

Batch B1a (v6.99.102) — estende catene esistenti con entità-intermedie ora seedate
(erano "TODO-listate" nelle note delle catene stesse). Dual-write: aggiorna
``data/chains/*.json`` (per il fresh-seed) ED emette ``scripts/sql_chain_links_b1a.sql``
(per la prod live, dato che ``ingest_chains`` salta le catene il cui nome esiste già).

# ETHICS-002/003/007: ogni link è una claim di successione. transition_type onesto
# (CONQUEST/REVOLUTION/UNIFICATION non eufemizzati), is_violent veritiero, ethical_notes
# che non edulcorano (sacco di Delhi, schiavitù reintrodotta da Napoleone, ecc.).
# Le descrizioni sono in inglese per coerenza con i record-catena esistenti.

Inserzioni:
  1. Afsharian (#1038) → catena Iran #9, tra Safavidi e Qajar (CONQUEST 1736).
  2. Premier Empire français (#1037) → catene Francia #8 e #74, tra Royaume de France
     e République (REVOLUTION 1804).
  3. Regatul României (#441) → catena Romania #35: restructure (consolida la Valacchia
     sul nome locale #93 Țara Românească, droppa il #579 con nome tedesco — ETHICS-001 —
     e appende il Regno, UNIFICATION 1859→Kingdom 1881).

Usage: python -m scripts.apply_chain_links_b1a   (poi rivedi il .sql e applicalo a prod)
"""

from __future__ import annotations

import json
from pathlib import Path

CHAINS_DIR = Path("data/chains")
SQL_OUT = Path("scripts/sql_chain_links_b1a.sql")

# ─── name_original (== entity_name JSON) ↔ id (verificati su prod) ──────────────
ID = {
    "افشاریان": 1038,            # Afsharid
    "Premier Empire français": 1037,
    "Regatul Romaniei": 441,     # Kingdom of Romania
    "Tara Romaneasca": 93,       # Wallachia (local name)
    "Principatul Moldovei": 94,  # Moldavia
    "قاجاریه": 505,              # Qajar (description update)
}

# ─── Link content (scritto UNA volta; usato sia in JSON sia in SQL) ─────────────
AFSHARID = {
    "entity_name": "افشاریان",
    "transition_year": 1736,
    "transition_type": "CONQUEST",
    "is_violent": True,
    "description": (
        "Afsharid dynasty (1736-1796), founded by Nader Shah, a Turkmen military "
        "commander who rose from the chaos after the Safavid collapse (1722 Ghilzai "
        "Afghan sack of Isfahan). He expelled the Afghans, deposed the last Safavid "
        "puppet (Abbas III), and crowned himself shah in 1736, reunifying Iran; his "
        "campaigns reached Delhi (1739) and Central Asia."
    ),
    "ethical_notes": (
        "Nader Shah's reunification was extraordinarily violent: the 1739 sack of "
        "Delhi included a massacre of ~30,000 inhabitants and the looting of the "
        "Mughal treasury (the Peacock Throne, the Koh-i-Noor). His reign degenerated "
        "into paranoid tyranny (he blinded his own son, ordered mass executions) until "
        "his assassination in 1747, after which Iran fragmented again. The Zand dynasty "
        "(Karim Khan, 1751-1794) ruled much of central/southern Iran during this "
        "interregnum but is not yet a separate entity here — a DB-coverage gap, not a "
        "judgment of marginality."
    ),
}

QAJAR_NEW_DESCRIPTION = (
    "Agha Mohammad Khan Qajar crowned Shah in 1796, completing the reunification of "
    "Iran after the Afsharid collapse (Nader Shah's assassination, 1747) and the Zand "
    "ascendancy (1751-1794, still compressed here as the Zand are not yet a separate "
    "entity). His campaigns included the 1795 sack of Tiflis (modern Tbilisi) with "
    "massacres and enslavement of Georgian Christians."
)

PREMIER_EMPIRE = {
    "entity_name": "Premier Empire français",
    "transition_year": 1804,
    "transition_type": "REVOLUTION",
    "is_violent": True,
    "description": (
        "First French Empire (1804-1815). After the 1789 Revolution abolished the "
        "monarchy (First Republic, 1792) and the 1799 coup of 18 Brumaire, Napoleon "
        "Bonaparte crowned himself Emperor on 2 December 1804. At its height the Empire "
        "dominated continental Europe; it collapsed after the disastrous 1812 Russian "
        "campaign and the defeat at Waterloo (1815)."
    ),
    "ethical_notes": (
        "This node makes explicit one of the episodes the chain otherwise compresses: "
        "the First Republic (1792-1804), First Empire (1804-1815), Bourbon Restoration "
        "(1815-1830), July Monarchy, Second Republic, and Second Empire (1852-1870) all "
        "preceded the current republican form. The Napoleonic Wars caused an estimated "
        "3-6 million deaths; the Empire also reinstated slavery in the French colonies "
        "(1802), reversing the 1794 revolutionary abolition."
    ),
}

# Romania #35 — restructure completo (3 link target). Consolida la Valacchia sul nome
# locale #93; il #579 "Furstentum Walachei" (nome tedesco) esce dalla catena (ETHICS-001).
ROMANIA_LINKS = [
    {
        "entity_name": "Tara Romaneasca",
        "transition_year": None,
        "transition_type": None,
        "is_violent": False,
        "description": (
            "Principality of Wallachia (Țara Românească), founded by Basarab I c. 1330 "
            "after independence from the Kingdom of Hungary at the Battle of Posada "
            "(1330). It produced Vlad III Țepeș (the historical basis for Dracula). An "
            "Ottoman vassal from the 16th century while retaining internal autonomy."
        ),
    },
    {
        "entity_name": "Principatul Moldovei",
        "transition_year": 1346,
        "transition_type": "SUCCESSION",
        "is_violent": False,
        "description": (
            "Principality of Moldavia, founded 1346 under Dragoș as a Hungarian march, "
            "achieving independence under Bogdan I (1359). Stephen the Great (1457-1504) "
            "resisted Ottoman expansion. Wallachia and Moldavia were PARALLEL "
            "principalities (not one succeeding the other), both Ottoman vassals from the "
            "16th century; the linear order here is a model artifact — they unite at the "
            "next node."
        ),
    },
    {
        "entity_name": "Regatul Romaniei",
        "transition_year": 1859,
        "transition_type": "UNIFICATION",
        "is_violent": False,
        "description": (
            "United Principalities of Moldavia and Wallachia, formed when Alexandru Ioan "
            "Cuza was elected prince of both Moldavia (Jan 1859) and Wallachia (Feb 1859); "
            "formal union as Romania in 1862, full independence in 1878 (Treaty of Berlin, "
            "after the violent 1877-78 Russo-Turkish war). Proclaimed the Kingdom of "
            "Romania (Regatul României) under Carol I in 1881; the monarchy lasted until "
            "1947, when it was abolished under Soviet pressure."
        ),
        "ethical_notes": (
            "Greater Romania (1918) integrated Transylvania, Bessarabia, and Bukovina, "
            "changing the ethnic balance — still contested by Hungarian historiography. "
            "Romania's alignment with Nazi Germany (1940-44) and the Iași pogrom (1941, "
            "~13,000 Jews killed) are part of the record; Ceaușescu's nationalist narrative "
            "minimized them."
        ),
    },
]

# ETHICS-001 nota a livello catena (Valacchia tedesca rimossa)
ROMANIA_CHAIN_NOTE_SUFFIX = (
    " NOTE (ETHICS-001): the early-Wallachia entity 'Furstentum Walachei' (a German-"
    "language name) was removed from this chain in favor of the local-named Țara "
    "Românească; that entity's German name_original is itself slated for an entity-level "
    "rename/deprecation."
)


def _load(name: str) -> list[dict]:
    return json.loads((CHAINS_DIR / name).read_text(encoding="utf-8"))


def _save(name: str, data: list[dict]) -> None:
    (CHAINS_DIR / name).write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _find(chains: list[dict], name_substr: str) -> dict:
    for c in chains:
        if c["name"].startswith(name_substr):
            return c
    raise SystemExit(f"chain not found: {name_substr!r}")


def _insert_after(links: list[dict], after_entity: str, new_link: dict) -> None:
    for i, lk in enumerate(links):
        if lk["entity_name"] == after_entity:
            links.insert(i + 1, new_link)
            return
    raise SystemExit(f"anchor not found: {after_entity!r}")


def _sql_str(v) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def _insert_sql(chain_id: int, link: dict, seq: int) -> str:
    eid = ID[link["entity_name"]]
    cols = "(chain_id,entity_id,sequence_order,transition_year,transition_type,is_violent,description,ethical_notes)"
    vals = (
        f"({chain_id},{eid},{seq},{_sql_str(link.get('transition_year'))},"
        f"{_sql_str(link.get('transition_type'))},{_sql_str(link.get('is_violent', False))},"
        f"{_sql_str(link.get('description'))},{_sql_str(link.get('ethical_notes'))})"
    )
    return f"INSERT INTO chain_links {cols} VALUES\n  {vals};"


def main() -> None:
    sql: list[str] = [
        "-- v6.99.102 — B1a chain-link extensions (generato da scripts/apply_chain_links_b1a.py).",
        "-- Dual-write: questo SQL allinea la prod live; data/chains/*.json allinea il fresh-seed.",
        "-- ETHICS-002/003/007: claim di successione con transition_type onesto + ethical_notes.",
        "BEGIN;",
        "",
    ]

    # ── 1. Iran #9: insert Afsharid after Safavid (seq1); update Qajar desc ──────
    b02 = _load("batch_02_more_chains.json")
    iran = _find(b02, "Iranian state forms")
    _insert_after(iran["links"], "دولت صفویه", json.loads(json.dumps(AFSHARID)))
    for lk in iran["links"]:
        if lk["entity_name"] == "قاجاریه":
            lk["description"] = QAJAR_NEW_DESCRIPTION
    sql += [
        "-- 1. Iran #9: Afsharid tra Safavidi e Qajar",
        "UPDATE chain_links SET sequence_order = sequence_order + 1 WHERE chain_id = 9 AND sequence_order >= 1;",
        _insert_sql(9, AFSHARID, 1),
        f"UPDATE chain_links SET description = {_sql_str(QAJAR_NEW_DESCRIPTION)} WHERE chain_id = 9 AND entity_id = {ID['قاجاریه']};",
        "",
    ]

    # ── 2a. French #8 (batch_02): insert Premier Empire after Royaume de France ──
    fr8 = _find(b02, "French state forms")
    _insert_after(fr8["links"], "Royaume de France", json.loads(json.dumps(PREMIER_EMPIRE)))
    _save("batch_02_more_chains.json", b02)
    sql += [
        "-- 2a. France #8: Premier Empire tra Royaume de France e République",
        "UPDATE chain_links SET sequence_order = sequence_order + 1 WHERE chain_id = 8 AND sequence_order >= 3;",
        _insert_sql(8, PREMIER_EMPIRE, 3),
        "",
    ]

    # ── 2b. French #74 (batch_27): insert Premier Empire after Royaume de France ─
    b27 = _load("batch_27_french_russian.json")
    fr74 = _find(b27, "French state deep trunk")
    _insert_after(fr74["links"], "Royaume de France", json.loads(json.dumps(PREMIER_EMPIRE)))
    _save("batch_27_french_russian.json", b27)
    sql += [
        "-- 2b. France #74: Premier Empire tra Royaume de France e République",
        "UPDATE chain_links SET sequence_order = sequence_order + 1 WHERE chain_id = 74 AND sequence_order >= 3;",
        _insert_sql(74, PREMIER_EMPIRE, 3),
        "",
    ]

    # ── 3. Romania #35 (batch_20): restructure (drop #579, consolidate #93, +#441) ─
    b20 = _load("batch_20_balkan.json")
    rom = _find(b20, "Romanian principalities")
    rom["links"] = [json.loads(json.dumps(lk)) for lk in ROMANIA_LINKS]
    rom["description"] = (
        "Romanian state-formation: the medieval principalities of Wallachia (Țara "
        "Românească, c. 1330) and Moldavia (1346), both Ottoman vassals, united under "
        "Alexandru Ioan Cuza (1859), independent 1878, proclaimed the Kingdom of Romania "
        "under Carol I (1881-1947)."
    )
    if ROMANIA_CHAIN_NOTE_SUFFIX.strip() not in (rom.get("ethical_notes") or ""):
        rom["ethical_notes"] = (rom.get("ethical_notes") or "") + ROMANIA_CHAIN_NOTE_SUFFIX
    _save("batch_20_balkan.json", b20)
    sql += [
        "-- 3. Romania #35: restructure — drop #579 (German name), consolidate Wallachia on #93, append Kingdom #441",
        "DELETE FROM chain_links WHERE chain_id = 35;",
    ]
    for seq, lk in enumerate(ROMANIA_LINKS):
        sql.append(_insert_sql(35, lk, seq))
    sql += [""]

    # ── guard + commit ──────────────────────────────────────────────────────────
    sql += [
        "-- guard: ogni catena toccata deve avere sequence_order contigui da 0",
        "DO $$ DECLARE bad int; BEGIN",
        "  SELECT count(*) INTO bad FROM (",
        "    SELECT chain_id, count(*) n, max(sequence_order) mx, min(sequence_order) mn",
        "    FROM chain_links WHERE chain_id IN (8,9,74,35) GROUP BY chain_id",
        "  ) q WHERE mn <> 0 OR mx <> n - 1;",
        "  IF bad > 0 THEN RAISE EXCEPTION 'sequence_order non contiguo in % catene', bad; END IF;",
        "END $$;",
        "COMMIT;",
    ]
    SQL_OUT.write_text("\n".join(sql) + "\n", encoding="utf-8")
    print(f"JSON aggiornati (batch_02, batch_20, batch_27). SQL → {SQL_OUT}")


if __name__ == "__main__":
    main()
