"""Cleanup: drop `aourednik` polygons that are shared across 3+ unrelated entities.

Context (v6.7.1): the boundary-quality audit
(`docs/boundary_audit_2026_04_15.md`) identified 74 entities whose
`boundary_aourednik_name` is reused by 3+ distinct entities. Structurally
these are wrong: the aourednik matcher picked a single generic polygon
("Holy Roman Empire", "Greek city-states", "Fatimid Caliphate", ...) and
bound it to every vassal/constituent in the cluster. Only the entity
whose canonical name text-matches the aourednik_name should keep the polygon.

Algorithm per cluster (aourednik_name shared by >=3 entities):
  1. For each entity in the cluster, collect `name_original` and all
     `NameVariant.name` values.
  2. Strip generic administrative suffixes (empire/kingdom/dynasty/...)
     and score each name against the aourednik_name using rapidfuzz
     token_set_ratio or ratio, whichever is higher.
  3. Entities whose best score < 0.80 are dropped: the aourednik polygon
     is replaced by a deterministic `name_seeded_boundary` generated from
     the capital coords, and `boundary_source` becomes `approximate_generated`.
  4. Entities whose best score >= 0.80 keep the aourednik polygon (they
     ARE the aourednik feature, or a close synonym — Ghaznavid Empire
     == Ghaznavid Dynasty, Chagatai Khanate == Moghulistan, etc.).

ETHICS-006/008: dropped entities lose the "aourednik" provenance badge —
their boundary is transparently labelled as generated. Any `confirmed`
entity that loses its only boundary source is NOT auto-demoted to
`uncertain`; the status is a separate question about the entity's
historical existence (not about polygon quality).

Idempotent: re-running produces 0 additional drops once the DB is stable.

Usage:
    python -m src.ingestion.cleanup_shared_polygons --dry-run
    python -m src.ingestion.cleanup_shared_polygons --apply
    python -m src.ingestion.cleanup_shared_polygons --apply --json-only
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from rapidfuzz import fuzz
from sqlalchemy.orm import Session

from src.db.database import SessionLocal
from src.db.models import GeoEntity, NameVariant
from src.ingestion.boundary_generator import name_seeded_boundary

logger = logging.getLogger(__name__)

ENTITIES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "entities"

# ─── Tunable constants ──────────────────────────────────────────────────────

# Cluster size at which we treat a shared polygon as structurally wrong.
# 2 can legitimately represent sibling entities (e.g. name-change); 3+
# is almost always a matcher error.
MIN_SHARED_CLUSTER_SIZE = 3

# Similarity threshold above which an entity is considered a legitimate
# owner of the shared polygon. Empirically calibrated against the v6.7.0
# dataset: 0.80 separates "Ghaznavid Dynasty == Ghaznavid Empire" (1.00)
# from "Sagaing == Pagan" (0.67 false positive).
KEEP_THRESHOLD = 0.80

# Post-drop confidence: same cap used by cleanup_displaced_ne_matches.
# ETHICS-004 treats approximate_generated as the lowest provenance tier.
APPROX_CONFIDENCE = 0.4

# Generic words to strip before comparing names. Most historical entities
# carry ONE of these as a category suffix (Empire / Kingdom / Dynasty /
# Sultanate / ...), and we want "Sui Dynasty" and "Sui Empire" to match.
GENERIC_TOKENS = {
    "empire", "kingdom", "dynasty", "sultanate", "caliphate", "khanate",
    "republic", "republica", "repubblica", "regno", "regnum", "imperium",
    "confederation", "commonwealth", "principality", "duchy", "emirate",
    "states", "state", "city", "of", "the", "la", "le", "du", "de", "der",
    "das", "des", "di", "al", "bey", "beylik", "satrapy", "realm", "domain",
    "dominion", "tribe", "nation", "league", "federation", "country",
    "land", "and",
}


# ─── Scoring helpers ────────────────────────────────────────────────────────


def strip_generic_tokens(s: str) -> str:
    """Return `s` lowercased, punctuation stripped, with GENERIC_TOKENS removed.

    Arabic/Hebrew/CJK names that contain no Latin letters collapse to an
    empty string; the caller must handle that as a no-match.
    """
    tokens = re.split(r"[^a-zA-Z]+", s.lower())
    return " ".join(t for t in tokens if t and t not in GENERIC_TOKENS)


def best_name_score(entity_names: Iterable[str], ao_name: str) -> float:
    """Max similarity between any entity name and `ao_name`, both stripped.

    Uses the max of `token_set_ratio` and `ratio` so that reordered tokens
    ("Sultanate of Delhi" vs "Delhi Sultanate") and identical strings both
    score 1.0. Returns 0.0..1.0.
    """
    stripped_ao = strip_generic_tokens(ao_name)
    if not stripped_ao:
        return 0.0
    best = 0
    for name in entity_names:
        stripped = strip_generic_tokens(name)
        if not stripped:
            continue
        score = max(
            fuzz.token_set_ratio(stripped, stripped_ao),
            fuzz.ratio(stripped, stripped_ao),
        )
        if score > best:
            best = score
    return best / 100.0


# ─── Cluster analysis ───────────────────────────────────────────────────────


@dataclass
class ClusterDecision:
    aourednik_name: str
    entity_ids_to_keep: list[int]
    entity_ids_to_drop: list[int]
    scores: dict[int, float]


def analyze_clusters(session: Session) -> list[ClusterDecision]:
    """Walk the DB and produce a keep/drop decision for every shared cluster.

    Returns a list of ClusterDecision, one per `aourednik_name` whose
    cluster size is >= MIN_SHARED_CLUSTER_SIZE. Clusters below that
    threshold are left untouched (they're ambiguous but not auto-fixable).
    """
    variants_by_entity: dict[int, list[str]] = defaultdict(list)
    for nv in session.query(NameVariant).all():
        variants_by_entity[nv.entity_id].append(nv.name)

    clusters: dict[str, list[GeoEntity]] = defaultdict(list)
    for e in session.query(GeoEntity).filter(
        GeoEntity.boundary_aourednik_name.isnot(None)
    ).all():
        clusters[e.boundary_aourednik_name].append(e)

    decisions: list[ClusterDecision] = []
    for ao_name, ents in clusters.items():
        if len(ents) < MIN_SHARED_CLUSTER_SIZE:
            continue
        keep_ids: list[int] = []
        drop_ids: list[int] = []
        scores: dict[int, float] = {}
        for e in ents:
            names = [e.name_original] + variants_by_entity.get(e.id, [])
            score = best_name_score(names, ao_name)
            scores[e.id] = score
            if score >= KEEP_THRESHOLD:
                keep_ids.append(e.id)
            else:
                drop_ids.append(e.id)
        decisions.append(ClusterDecision(
            aourednik_name=ao_name,
            entity_ids_to_keep=keep_ids,
            entity_ids_to_drop=drop_ids,
            scores=scores,
        ))
    return decisions


# ─── Cleanup ────────────────────────────────────────────────────────────────


@dataclass
class CleanupStats:
    clusters_analyzed: int = 0
    entities_dropped_db: int = 0
    entities_dropped_json: int = 0
    json_files_written: list[str] = field(default_factory=list)
    skipped_no_capital: int = 0
    dropped_by_cluster: dict[str, int] = field(default_factory=dict)
    dropped_samples: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        d = self.__dict__.copy()
        d["json_files_written"] = list(self.json_files_written)
        d["dropped_samples"] = list(self.dropped_samples[:20])
        return d


def _generate_replacement_boundary(entity: GeoEntity) -> dict | None:
    """Return a name-seeded approximate polygon, or None if we lack a capital."""
    if entity.capital_lat is None or entity.capital_lon is None:
        return None
    return name_seeded_boundary(
        name=entity.name_original or "",
        lat=float(entity.capital_lat),
        lon=float(entity.capital_lon),
        entity_type=entity.entity_type or "kingdom",
    )


def _apply_drop_to_entity(entity: GeoEntity) -> bool:
    """Mutate `entity` in place: strip aourednik provenance, replace polygon.

    Returns True if the mutation was applied, False if we had to skip
    (entity lacks capital coordinates and we cannot generate a replacement).
    """
    new_geom = _generate_replacement_boundary(entity)
    if new_geom is None:
        return False
    entity.boundary_geojson = json.dumps(new_geom)
    entity.boundary_source = "approximate_generated"
    entity.boundary_aourednik_name = None
    entity.boundary_aourednik_year = None
    entity.boundary_aourednik_precision = None
    entity.boundary_ne_iso_a3 = None
    if entity.confidence_score is None or entity.confidence_score > APPROX_CONFIDENCE:
        entity.confidence_score = APPROX_CONFIDENCE
    return True


def _apply_drops_to_db(
    session: Session, drop_ids: set[int], dry_run: bool, stats: CleanupStats
) -> dict[str, dict]:
    """Run DB mutations; return {name_original: new_boundary_dict} for JSON sync."""
    replacements: dict[str, dict] = {}
    rows = session.query(GeoEntity).filter(GeoEntity.id.in_(list(drop_ids))).all()
    for row in rows:
        if row.capital_lat is None or row.capital_lon is None:
            stats.skipped_no_capital += 1
            logger.warning(
                "Skipping entity %d (%r): no capital coords, cannot generate replacement",
                row.id, row.name_original,
            )
            continue
        new_geom = _generate_replacement_boundary(row)
        if new_geom is None:
            stats.skipped_no_capital += 1
            continue
        replacements[row.name_original] = new_geom

        if not dry_run:
            _apply_drop_to_entity(row)
        stats.entities_dropped_db += 1
        stats.dropped_samples.append(
            f"id={row.id} {row.name_original!r} "
            f"(was aourednik:{getattr(row, '_original_ao_name', '?')})"
        )

    if not dry_run and stats.entities_dropped_db > 0:
        session.commit()
        logger.info(
            "DB cleanup: committed %d drops across %d clusters",
            stats.entities_dropped_db, stats.clusters_analyzed,
        )
    elif dry_run:
        session.rollback()
        logger.info(
            "DB cleanup DRY-RUN: would drop %d entities",
            stats.entities_dropped_db,
        )

    return replacements


def _apply_drops_to_json(
    drop_names: set[str], replacements: dict[str, dict], dry_run: bool, stats: CleanupStats
) -> None:
    """Walk data/entities/batch_*.json and apply matching drops in place."""
    if not ENTITIES_DIR.is_dir():
        logger.warning("Entities directory not found: %s", ENTITIES_DIR)
        return

    for json_file in sorted(ENTITIES_DIR.glob("batch_*.json")):
        try:
            with open(json_file, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError) as exc:
            logger.warning("Skipping unreadable %s: %s", json_file.name, exc)
            continue

        container = (
            data["entities"]
            if isinstance(data, dict) and "entities" in data
            else data
        )
        if not isinstance(container, list):
            continue

        file_changed = False
        for entity in container:
            if not isinstance(entity, dict):
                continue
            name = entity.get("name_original")
            if not name or name not in drop_names:
                continue
            new_geom = replacements.get(name)
            if not new_geom:
                # DB side skipped due to no capital — skip JSON too
                continue
            entity["boundary_geojson"] = new_geom
            entity["boundary_source"] = "approximate_generated"
            entity.pop("boundary_aourednik_name", None)
            entity.pop("boundary_aourednik_year", None)
            entity.pop("boundary_aourednik_precision", None)
            entity.pop("boundary_ne_iso_a3", None)
            cur = entity.get("confidence_score")
            if not isinstance(cur, (int, float)) or cur > APPROX_CONFIDENCE:
                entity["confidence_score"] = APPROX_CONFIDENCE
            file_changed = True
            stats.entities_dropped_json += 1

        if file_changed and not dry_run:
            with open(json_file, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            stats.json_files_written.append(json_file.name)
            logger.info("Wrote drops into %s", json_file.name)


# ─── Entry point ────────────────────────────────────────────────────────────


def run_cleanup(
    *,
    dry_run: bool = True,
    json_only: bool = False,
    db_only: bool = False,
    session: Session | None = None,
) -> dict:
    """Produce + persist drop decisions for every shared cluster.

    Returns a flat dict with decisions + stats for downstream assertions.
    """
    stats = CleanupStats()
    own_session = session is None
    db: Session = session if session is not None else SessionLocal()

    try:
        decisions = analyze_clusters(db)
        stats.clusters_analyzed = len(decisions)

        drop_ids: set[int] = set()
        for d in decisions:
            drop_ids.update(d.entity_ids_to_drop)
            stats.dropped_by_cluster[d.aourednik_name] = len(d.entity_ids_to_drop)

        # Collect name_originals for JSON side before DB mutations
        drop_names_rows = db.query(GeoEntity.name_original).filter(
            GeoEntity.id.in_(list(drop_ids))
        ).all()
        drop_names: set[str] = {r[0] for r in drop_names_rows if r[0]}

        replacements: dict[str, dict] = {}
        if not json_only:
            replacements = _apply_drops_to_db(db, drop_ids, dry_run=dry_run, stats=stats)

        if not db_only and drop_names:
            # In json_only mode we still need to compute replacements even though
            # we skipped the DB pass. Do it from the ORM rows directly.
            if not replacements:
                for row in db.query(GeoEntity).filter(
                    GeoEntity.id.in_(list(drop_ids))
                ).all():
                    geom = _generate_replacement_boundary(row)
                    if geom is not None and row.name_original:
                        replacements[row.name_original] = geom
            _apply_drops_to_json(drop_names, replacements, dry_run=dry_run, stats=stats)

        return {
            "dry_run": dry_run,
            "decisions": [
                {
                    "aourednik_name": d.aourednik_name,
                    "keep_count": len(d.entity_ids_to_keep),
                    "drop_count": len(d.entity_ids_to_drop),
                    "keep_ids": d.entity_ids_to_keep,
                    "drop_ids": d.entity_ids_to_drop,
                    "scores": d.scores,
                }
                for d in decisions
            ],
            "stats": stats.as_dict(),
        }
    finally:
        if own_session:
            db.close()


def main() -> int:
    # Windows cp1252 can't encode non-Latin entity names in logs.
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true",
                       help="Compute decisions without writing (default).")
    group.add_argument("--apply", action="store_true",
                       help="Perform mutations against DB + JSON.")
    parser.add_argument("--json-only", action="store_true",
                        help="Skip DB writes; only rewrite batch JSONs.")
    parser.add_argument("--db-only", action="store_true",
                        help="Skip JSON writes; only mutate the live DB.")
    args = parser.parse_args()

    dry_run = not args.apply  # safety default

    result = run_cleanup(
        dry_run=dry_run, json_only=args.json_only, db_only=args.db_only,
    )

    print(f"\n=== cleanup_shared_polygons (dry_run={result['dry_run']}) ===\n")
    print(f"Clusters analyzed (>= {MIN_SHARED_CLUSTER_SIZE}-entity): "
          f"{result['stats']['clusters_analyzed']}")
    print(f"Entities dropped in DB:   {result['stats']['entities_dropped_db']}")
    print(f"Entities dropped in JSON: {result['stats']['entities_dropped_json']}")
    print(f"Skipped (no capital):     {result['stats']['skipped_no_capital']}")
    print(f"\nPer-cluster drops:")
    for ao_name, count in sorted(
        result['stats']['dropped_by_cluster'].items(), key=lambda x: -x[1]
    ):
        print(f"  [-{count:>2}x] {ao_name}")

    print(f"\nSample drops (first 20):")
    for sample in result['stats']['dropped_samples']:
        print(f"  {sample}")

    if dry_run:
        print("\n(dry-run: re-run with --apply to persist changes)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
