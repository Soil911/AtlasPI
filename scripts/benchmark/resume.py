"""Resume utility per benchmark interrotto da credit exhaustion.

Legge raw_responses.jsonl + questions bank, identifica Q con error (no response
text), ri-runna baseline+atlaspi+judge SOLO per quelle. Salva in place (update
row by id), rigenera evaluations + report.

Usage:
    ANTHROPIC_API_KEY=sk-... python -m scripts.benchmark.resume \\
        scripts/benchmark/results/full-v1 \\
        --questions scripts/benchmark/questions/questions-bank-v1.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root))

from scripts.benchmark.agents.baseline_agent import BaselineAgent
from scripts.benchmark.agents.atlaspi_agent import AtlasPIAgent
from scripts.benchmark.judges.accuracy_judge import AccuracyJudge
from scripts.benchmark.benchmark_runner import (
    aggregate_summary,
    render_report,
    pick_question_text,
    load_questions,
)


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def save_jsonl(path: Path, rows: list[dict]):
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def has_response(entry: dict) -> bool:
    return isinstance(entry, dict) and bool(entry.get("response"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir", type=Path)
    ap.add_argument("--questions", type=Path, required=True)
    ap.add_argument("--lang", default="en", choices=["en", "it"])
    ap.add_argument("--limit", type=int, help="Limit resume to first N incomplete")
    args = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    raw_path = args.results_dir / "raw_responses.jsonl"
    eval_path = args.results_dir / "evaluations.jsonl"
    report_path = args.results_dir / "report.md"

    raw_rows = load_jsonl(raw_path)
    eval_rows = load_jsonl(eval_path) if eval_path.exists() else []
    questions = load_questions(args.questions)
    q_by_id = {q["id"]: q for q in questions}

    raw_by_id = {r["id"]: r for r in raw_rows}
    eval_by_id = {e["id"]: e for e in eval_rows}

    # Identify incomplete: no response for baseline or atlaspi
    incomplete_ids = [
        r["id"] for r in raw_rows
        if not has_response(r.get("baseline")) or not has_response(r.get("atlaspi"))
    ]
    print(f"Total raw: {len(raw_rows)}")
    print(f"Incomplete (need resume): {len(incomplete_ids)}")
    if not incomplete_ids:
        print("Nothing to do.")
        return

    if args.limit:
        incomplete_ids = incomplete_ids[:args.limit]
        print(f"Limiting to first {len(incomplete_ids)}")

    baseline = BaselineAgent()
    atlaspi = AtlasPIAgent()
    judge = AccuracyJudge()

    # Re-run and save incrementally (per Q, flush to disk)
    for i, qid in enumerate(incomplete_ids, 1):
        q = q_by_id.get(qid)
        if not q:
            print(f"[SKIP] {qid}: not in questions bank")
            continue

        q_text = pick_question_text(q, args.lang)
        expected = q.get("expected_answer", "")
        forbidden = q.get("forbidden_facts", [])
        expected_conf = q.get("expected_confidence", "high")

        row = raw_by_id.get(qid) or {
            "id": qid,
            "category": q.get("category"),
            "epoch_bucket": q.get("epoch_bucket"),
            "region": q.get("region"),
            "lang": args.lang,
            "question": q_text,
            "expected_answer": expected,
            "expected_confidence": expected_conf,
        }

        print(f"[{i}/{len(incomplete_ids)}] {qid} ({q.get('category')}/{q.get('region')}): {q_text[:70]}...")

        # Re-run baseline if missing
        if not has_response(row.get("baseline")):
            try:
                b_resp = baseline.answer(q_text)
                row["baseline"] = b_resp
                print(f"  baseline: {b_resp.get('tokens_out', 0)} tok")
            except Exception as e:
                row["baseline"] = {"error": str(e), "condition": "baseline"}
                print(f"  baseline ERROR: {e}")
                # If credit error, stop
                if "credit balance" in str(e).lower() or "low to access" in str(e).lower():
                    print("\nCREDIT EXHAUSTED. Stopping resume. Saving progress.")
                    # Flush current state
                    raw_rows = [raw_by_id.get(r["id"], r) for r in raw_rows]
                    raw_by_id[qid] = row
                    # Rebuild from raw_by_id
                    save_jsonl(raw_path, list(raw_by_id.values()))
                    save_jsonl(eval_path, list(eval_by_id.values()))
                    sys.exit(2)

        # Re-run atlaspi if missing
        if not has_response(row.get("atlaspi")):
            try:
                a_resp = atlaspi.answer(q_text)
                row["atlaspi"] = a_resp
                print(f"  atlaspi: {a_resp.get('tool_calls_count', 0)} tool calls, {a_resp.get('tokens_out', 0)} tok")
            except Exception as e:
                row["atlaspi"] = {"error": str(e), "condition": "atlaspi"}
                print(f"  atlaspi ERROR: {e}")
                if "credit balance" in str(e).lower() or "low to access" in str(e).lower():
                    print("\nCREDIT EXHAUSTED. Stopping resume. Saving progress.")
                    raw_by_id[qid] = row
                    save_jsonl(raw_path, list(raw_by_id.values()))
                    save_jsonl(eval_path, list(eval_by_id.values()))
                    sys.exit(2)

        raw_by_id[qid] = row

        # Judge both conditions
        eval_row = eval_by_id.get(qid, {"id": qid, "category": row.get("category"),
                                          "epoch_bucket": row.get("epoch_bucket"),
                                          "region": row.get("region")})
        for cond in ("baseline", "atlaspi"):
            if has_response(row.get(cond)):
                try:
                    verdict = judge.judge(
                        question=q_text,
                        expected_answer=expected,
                        forbidden_facts=forbidden,
                        response=row[cond]["response"],
                        expected_confidence=expected_conf,
                    )
                    eval_row[cond] = verdict
                except Exception as e:
                    eval_row[cond] = {"error": str(e), "verdict": "judge_error"}
                    if "credit balance" in str(e).lower() or "low to access" in str(e).lower():
                        print("\nCREDIT EXHAUSTED (judge). Saving progress.")
                        eval_by_id[qid] = eval_row
                        save_jsonl(raw_path, list(raw_by_id.values()))
                        save_jsonl(eval_path, list(eval_by_id.values()))
                        sys.exit(2)
        eval_by_id[qid] = eval_row

        # Flush after every question (resumable even if killed)
        save_jsonl(raw_path, list(raw_by_id.values()))
        save_jsonl(eval_path, list(eval_by_id.values()))

    # Final aggregate + report
    final_raw = list(raw_by_id.values())
    for r in final_raw:
        r["evaluations"] = eval_by_id.get(r["id"], {})

    summary = aggregate_summary(final_raw)
    with report_path.open("w", encoding="utf-8") as f:
        f.write(render_report(summary, len(final_raw)))

    print(f"\nDone. Report: {report_path}")
    # Write summary to file instead of printing (avoids Windows Unicode crash)
    summary_path = args.results_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Summary JSON: {summary_path}")


if __name__ == "__main__":
    main()
