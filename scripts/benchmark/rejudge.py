"""Re-judge utility per recovery da judge failures (credit exhausted, API errors, ecc).

Usage:
    # Re-judge ONLY missing (acc=None) evaluations with Opus (default)
    python scripts/benchmark/rejudge.py scripts/benchmark/results/full-v1

    # Re-judge ALL with Sonnet (cheaper, for credit-limited scenarios)
    python scripts/benchmark/rejudge.py scripts/benchmark/results/full-v1 \\
        --model sonnet --rejudge-all

    # Re-judge only specific IDs
    python scripts/benchmark/rejudge.py scripts/benchmark/results/full-v1 \\
        --ids Q-035,Q-040,Q-055

Mantiene raw_responses.jsonl invariato. Sovrascrive evaluations.jsonl
con merged results (old + new). Rigenera report.md.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Path fix so we can import scripts.benchmark.*
_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root))

from scripts.benchmark.judges.accuracy_judge import AccuracyJudge
from scripts.benchmark.benchmark_runner import aggregate_summary, render_report


MODEL_MAP = {
    "opus": "claude-opus-4-5-20251101",
    "sonnet": "claude-sonnet-4-5-20250929",
    "haiku": "claude-haiku-4-5-20250929",
}


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def save_jsonl(path: Path, rows: list[dict]):
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def needs_rejudge(eval_row: dict, rejudge_all: bool) -> tuple[bool, bool]:
    """Returns (need_baseline, need_atlaspi)."""
    if rejudge_all:
        return True, True
    b = eval_row.get("baseline", {})
    a = eval_row.get("atlaspi", {})
    need_b = not isinstance(b, dict) or b.get("accuracy") is None
    need_a = not isinstance(a, dict) or a.get("accuracy") is None
    return need_b, need_a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir", type=Path, help="Directory with raw_responses.jsonl + evaluations.jsonl")
    ap.add_argument("--model", default="opus", choices=list(MODEL_MAP.keys()))
    ap.add_argument("--rejudge-all", action="store_true", help="Re-judge ALL, not only missing")
    ap.add_argument("--ids", help="Comma-separated list of IDs to rejudge (overrides missing)")
    args = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    raw_path = args.results_dir / "raw_responses.jsonl"
    eval_path = args.results_dir / "evaluations.jsonl"
    report_path = args.results_dir / "report.md"

    if not raw_path.exists() or not eval_path.exists():
        print(f"ERROR: raw or evaluations not found in {args.results_dir}", file=sys.stderr)
        sys.exit(1)

    raw_rows = load_jsonl(raw_path)
    eval_rows = load_jsonl(eval_path)
    raw_by_id = {r["id"]: r for r in raw_rows}
    eval_by_id = {e["id"]: e for e in eval_rows}

    print(f"Loaded {len(raw_rows)} raw, {len(eval_rows)} evaluations")
    print(f"Using judge model: {MODEL_MAP[args.model]}")

    specific_ids = set(args.ids.split(",")) if args.ids else None

    judge = AccuracyJudge(model=MODEL_MAP[args.model])
    rejudged = 0
    skipped = 0

    for eval_row in eval_rows:
        qid = eval_row["id"]
        if specific_ids and qid not in specific_ids:
            skipped += 1
            continue

        need_b, need_a = needs_rejudge(eval_row, args.rejudge_all)
        if not need_b and not need_a:
            skipped += 1
            continue

        raw = raw_by_id.get(qid)
        if not raw:
            print(f"[SKIP] {qid}: no raw response found")
            skipped += 1
            continue

        q_text = raw.get("question") or raw.get("question_en") or raw.get("question_it")
        expected = raw.get("expected_answer", "")
        forbidden = raw.get("forbidden_facts") or raw.get("expected_forbidden_facts") or []
        expected_conf = raw.get("expected_confidence", "high")

        # Extract responses to re-judge
        for cond, should in (("baseline", need_b), ("atlaspi", need_a)):
            if not should:
                continue
            raw_resp = raw.get(cond, {})
            response_text = raw_resp.get("response") if isinstance(raw_resp, dict) else None
            if not response_text:
                print(f"[SKIP] {qid}/{cond}: no response text in raw")
                continue
            try:
                verdict = judge.judge(
                    question=q_text,
                    expected_answer=expected,
                    forbidden_facts=forbidden,
                    response=response_text,
                    expected_confidence=expected_conf,
                )
                eval_row[cond] = verdict
                print(f"[OK] {qid}/{cond}: accuracy={verdict.get('accuracy')}, verdict={verdict.get('verdict')}")
                rejudged += 1
            except Exception as e:
                print(f"[ERR] {qid}/{cond}: {type(e).__name__}: {str(e)[:200]}")
                eval_row[cond] = {
                    "accuracy": None,
                    "verdict": "judge_error",
                    "reasoning": f"Rejudge error: {str(e)[:300]}",
                    "judge_model": MODEL_MAP[args.model],
                }

    # Save updated evaluations
    save_jsonl(eval_path, eval_rows)
    print(f"\nRejudged: {rejudged}, Skipped: {skipped}")

    # Rebuild raw+evals joined for aggregate
    merged = []
    for raw in raw_rows:
        e = eval_by_id.get(raw["id"], {})
        raw["evaluations"] = e
        merged.append(raw)

    summary = aggregate_summary(merged)
    with report_path.open("w", encoding="utf-8") as f:
        f.write(render_report(summary, len(raw_rows)))

    print(f"\nReport rebuilt: {report_path}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
