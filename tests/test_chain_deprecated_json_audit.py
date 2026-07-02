"""Fence JSON-side: nessuna catena può referenziare entità deprecate o inesistenti.

# ETHICS/ADR-005 (v6.99.107): le catene 99-106 linkavano 5 duplicati deprecati
# del merge v6.85 perché l'ingest risolveva i nomi senza guardare lo status
# (guard runtime ora in ingest_chains). Questo fence blocca la classe di bug
# alla PR: ogni entity_name nei data/chains/*.json deve risolvere a un'entità
# JSON viva (vista effettiva last-wins, come src/db/seed.load_all_entities).
# I riferimenti morti (es. il vecchio 'Māt Akkadī' della città Bābilim) qui
# sarebbero stati colti al primo run.
"""

import json
from pathlib import Path

CHAINS_DIR = Path("data/chains")
ENTITIES_DIR = Path("data/entities")


def _effective_entities() -> dict[str, str]:
    """name_original → status, con semantica last-wins (= seed)."""
    out: dict[str, str] = {}
    for path in sorted(ENTITIES_DIR.glob("*.json")):
        for ent in json.loads(path.read_text(encoding="utf-8")):
            name = ent.get("name_original")
            if name:
                out[name] = ent.get("status", "confirmed")
    return out


def _chain_refs() -> list[tuple[str, str, str]]:
    """(file, chain_name, entity_name) per ogni link di ogni catena."""
    refs = []
    for path in sorted(CHAINS_DIR.glob("*.json")):
        for chain in json.loads(path.read_text(encoding="utf-8")):
            for link in chain.get("links", []):
                name = link.get("entity_name")
                if name:
                    refs.append((path.name, chain.get("name", "?"), name))
    return refs


def test_chain_links_resolve_to_live_entities():
    entities = _effective_entities()
    dead: list[str] = []
    deprecated: list[str] = []
    for fname, chain, ent_name in _chain_refs():
        status = entities.get(ent_name)
        if status is None:
            dead.append(f"{fname} :: {chain[:50]} → '{ent_name}' (nessuna entità)")
        elif status == "deprecated":
            deprecated.append(f"{fname} :: {chain[:50]} → '{ent_name}' (deprecated)")
    assert not deprecated, (
        "Catene che referenziano entità DEPRECATE (ADR-005 — ripuntare alla "
        "primary del merge):\n" + "\n".join(deprecated)
    )
    assert not dead, (
        "Catene con riferimenti MORTI (entity_name non risolve — typo o "
        "rename non cascadato):\n" + "\n".join(dead)
    )
