"""Idempotent ingestion of dynasty / succession chains — v6.5.

Reads all JSON files in ``data/chains/`` and inserts only those chains that
aren't already present (dedup key: ``name``).

Entity resolution:
    Each link in a chain references an entity by ``entity_name`` (matching
    ``GeoEntity.name_original``). Unresolved references are logged as WARNING
    and the offending link is SKIPPED — the rest of the chain is still
    inserted. This means partial chains can land even if some historical
    entities aren't yet in the DB (legitimate case: Tawantinsuyu might be
    seeded in a later batch).

ETHICS-002 sanity:
    A link with ``sequence_order > 0`` SHOULD have a ``transition_type``.
    Missing transition_types on non-first links are logged as WARNING. We
    don't raise because there's a legitimate use case (uncertain
    transitions) — but the operator should see them.

ETHICS-003 sanity:
    Chains with ``chain_type="IDEOLOGICAL"`` MUST have ``ethical_notes``
    populated at the chain level (self-proclaimed continuity ≠ historical
    legitimacy — this disclaimer is mandatory). Missing notes on
    IDEOLOGICAL chains are logged as WARNING.

Usage:
    python -m src.ingestion.ingest_chains
"""

from __future__ import annotations

import io
import json
import logging
import sys
from pathlib import Path
from typing import Any

# Windows cp1252 stdout fix for non-latin names
if sys.platform == "win32" and isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except AttributeError:
        pass

from src.config import DATA_DIR
from src.db.database import SessionLocal
from src.db.models import ChainLink, DynastyChain, GeoEntity

logger = logging.getLogger(__name__)


CHAINS_DIR = Path(DATA_DIR) / "chains"


def _load_json_dir(dir_path: Path) -> list[dict[str, Any]]:
    """Load & concatenate all *.json files in a directory."""
    if not dir_path.exists():
        return []
    out: list[dict[str, Any]] = []
    for fp in sorted(dir_path.glob("*.json")):
        try:
            with fp.open(encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, list):
                out.extend(data)
            else:
                logger.warning("File %s non è una lista JSON, skip.", fp)
        except Exception as exc:
            logger.error("Errore lettura %s: %s", fp, exc)
    return out


def ingest_chains() -> dict[str, Any]:
    """Insert chains whose ``name`` isn't already in DB.

    Returns a dict with insert/skip/unresolved stats.
    """
    db = SessionLocal()
    try:
        existing = {c.name for c in db.query(DynastyChain.name).all()}

        all_chains = _load_json_dir(CHAINS_DIR)
        logger.info("Catene nei JSON: %d", len(all_chains))

        entity_map = {e.name_original: e.id for e in db.query(GeoEntity).all()}

        inserted = 0
        skipped = 0
        total_links_created = 0
        unresolved: list[str] = []
        missing_transition_types: list[str] = []
        ideological_without_notes: list[str] = []

        for ch_data in all_chains:
            name = ch_data.get("name")
            if not name:
                logger.warning("Chain senza 'name' — skip.")
                continue
            if name in existing:
                skipped += 1
                continue

            chain_type = ch_data.get("chain_type", "OTHER")
            ethical_notes = ch_data.get("ethical_notes")

            # ETHICS-003: IDEOLOGICAL chains MUST carry a disclaimer.
            if chain_type == "IDEOLOGICAL" and not ethical_notes:
                ideological_without_notes.append(name)

            chain = DynastyChain(
                name=name,
                name_lang=ch_data.get("name_lang", "en"),
                chain_type=chain_type,
                region=ch_data.get("region"),
                description=ch_data.get("description"),
                confidence_score=ch_data.get("confidence_score", 0.7),
                status=ch_data.get("status", "confirmed"),
                ethical_notes=ethical_notes,
                sources=(
                    json.dumps(ch_data["sources"], ensure_ascii=False)
                    if ch_data.get("sources")
                    else None
                ),
            )
            db.add(chain)
            db.flush()  # assigns chain.id for the FK in ChainLink

            links_data = ch_data.get("links", [])
            for i, link_data in enumerate(links_data):
                ent_name = link_data.get("entity_name")
                if not ent_name:
                    logger.warning(
                        "Chain '%s' link[%d] senza entity_name — skip.", name, i
                    )
                    continue

                entity_id = entity_map.get(ent_name)
                if entity_id is None:
                    unresolved.append(f"chain='{name}' link[{i}] → entity='{ent_name}'")
                    continue

                transition_type = link_data.get("transition_type")
                # ETHICS-002: non-first links should ideally have a transition_type.
                if i > 0 and not transition_type:
                    missing_transition_types.append(
                        f"chain='{name}' link[{i}] entity='{ent_name}' has no transition_type"
                    )

                db.add(
                    ChainLink(
                        chain_id=chain.id,
                        entity_id=entity_id,
                        sequence_order=i,
                        transition_year=link_data.get("transition_year"),
                        transition_type=transition_type,
                        is_violent=bool(link_data.get("is_violent", False)),
                        description=link_data.get("description"),
                        ethical_notes=link_data.get("ethical_notes"),
                    )
                )
                total_links_created += 1

            inserted += 1

        db.commit()
        logger.info(
            "Ingest catene: %d inserite, %d saltate, %d link creati, "
            "%d entity-refs non risolti, %d link senza transition_type, "
            "%d catene IDEOLOGICAL senza ethical_notes",
            inserted,
            skipped,
            total_links_created,
            len(unresolved),
            len(missing_transition_types),
            len(ideological_without_notes),
        )
        for ref in unresolved[:20]:
            logger.warning(" unresolved: %s", ref)
        for m in missing_transition_types[:10]:
            logger.warning(" ETHICS-002 soft: %s", m)
        for c in ideological_without_notes:
            logger.warning(
                " ETHICS-003: chain '%s' is IDEOLOGICAL but has no ethical_notes", c
            )

        return {
            "inserted": inserted,
            "skipped_existing": skipped,
            "total_in_json": len(all_chains),
            "total_links_created": total_links_created,
            "unresolved_entity_refs": len(unresolved),
            "missing_transition_types": len(missing_transition_types),
            "ideological_without_notes": len(ideological_without_notes),
        }
    finally:
        db.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    res = ingest_chains()
    print("=== Chains ingest ===")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
