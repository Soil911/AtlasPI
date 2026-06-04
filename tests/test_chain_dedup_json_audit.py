"""Fence: no duplicate chain names in the JSON source + unit test del dedup.

Background (chain-dedup, v6.99.101): prod aveva 107 ``dynasty_chains`` ma solo
77 nomi distinti — 30 catene successorie *duplicate* (coppie byte-identiche,
stessi link). Root cause: ``ingest_chains`` salta i nomi già nel DB
(``existing``, calcolato una volta all'avvio) ma NON assorbiva i nomi inseriti
nello stesso run, così due file che elencavano lo stesso ``name`` inserivano
entrambi. La sorgente JSON è stata poi ripulita (77 nomi unici) ma l'ingest
INSERT-only ha lasciato in prod i 30 doppioni — rimossi una tantum.

# ETHICS-002/003: una catena duplicata è una successione *contata due volte*,
# mostrata doppia agli agenti — falsa la rappresentazione della continuità
# storica. Questo fence è il guard veloce (job SQLite, niente DB): gira su ogni
# PR e diventa rosso se una nuova batch reintroduce un nome di catena duplicato
# nella sorgente, prima del merge. ``_dedupe_by_name`` è la rete di sicurezza
# runtime (vedi src/ingestion/ingest_chains.py).
"""

from __future__ import annotations

from collections import Counter

from src.ingestion.ingest_chains import CHAINS_DIR, _dedupe_by_name, _load_json_dir


def _format_dup_failure(dups: dict[str, int], total: int) -> str:
    lines = [
        f"REGRESSION: {len(dups)} nome/i di catena duplicato/i in "
        f"data/chains/*.json ({total} catene totali caricate).",
        "",
        "Ogni catena successoria deve avere un 'name' UNICO across data/chains/.",
        "Un nome duplicato = una catena fantasma mostrata due volte agli agenti",
        "(vedi docs/ethics, ETHICS-002/003). Rinomina o rimuovi il doppione.",
        "",
    ]
    for name, k in sorted(dups.items(), key=lambda kv: (-kv[1], kv[0]))[:12]:
        lines.append(f"  • {k}× {name!r}")
    return "\n".join(lines)


def test_json_chain_names_are_unique():
    """data/chains/*.json non deve contenere nomi di catena duplicati."""
    chains = _load_json_dir(CHAINS_DIR)
    assert chains, "nessuna catena caricata da data/chains/*.json"

    counts = Counter(c.get("name") for c in chains if c.get("name"))
    dups = {n: k for n, k in counts.items() if k > 1}

    assert not dups, _format_dup_failure(dups, len(chains))


def test_dedupe_by_name_keeps_first_drops_repeats():
    """Guard del guard: l'helper tiene la PRIMA occorrenza e scarta i repeat."""
    chains = [
        {"name": "Alpha", "region": "X"},
        {"name": "Beta"},
        {"name": "Alpha", "region": "Y"},  # repeat → dropped
        {"name": "Alpha", "region": "Z"},  # repeat → dropped
    ]
    out, dropped = _dedupe_by_name(chains)

    assert dropped == 2
    assert [c["name"] for c in out] == ["Alpha", "Beta"]
    assert out[0]["region"] == "X"  # FIRST occurrence vince (deterministico)


def test_dedupe_by_name_passes_through_nameless():
    """Chain senza 'name' passano (saranno scartate a valle con un warning)."""
    chains = [{"foo": 1}, {"name": "A"}, {"name": "A"}]
    out, dropped = _dedupe_by_name(chains)

    assert dropped == 1
    assert len(out) == 2
