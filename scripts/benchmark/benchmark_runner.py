"""v7.0 AtlasPI benchmark runner — A/B test baseline vs AtlasPI-tools.

Usage:
    # Dry run (5 seed questions, verifica setup)
    python -m scripts.benchmark.benchmark_runner --dry-run

    # Run completo (100 questions se bank completo, altrimenti quante ci sono)
    python -m scripts.benchmark.benchmark_runner \\
        --questions scripts/benchmark/questions/questions-bank-v1.json \\
        --output scripts/benchmark/results/$(date +%Y%m%d-%H%M%S)

    # Solo subset (prima di spendere full budget)
    python -m scripts.benchmark.benchmark_runner \\
        --questions scripts/benchmark/questions/questions-bank-v1.json \\
        --limit 20 \\
        --output scripts/benchmark/results/subset-20

Env vars richieste:
    ANTHROPIC_API_KEY  — per Claude (baseline + atlaspi + judge)

Decisioni pre-run fissate dal cofounder (v7.0):
    - Primary LLM: Claude Sonnet 4.5
    - Judge LLM: Claude Opus 4.5 (imparziale, modello diverso)
    - Threshold success: tier-based, vedi README
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from scripts.benchmark.agents.baseline_agent import BaselineAgent
from scripts.benchmark.agents.atlaspi_agent import AtlasPIAgent
from scripts.benchmark.judges.accuracy_judge import AccuracyJudge


def load_questions(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "questions" in data:
        return data["questions"]
    if isinstance(data, list):
        return data
    raise ValueError(f"Invalid questions format in {path}")


def pick_question_text(q: dict, lang: str = "en") -> str:
    """Pick the IT or EN version of the question."""
    if lang == "it":
        return q.get("question_it") or q.get("question_en") or q.get("question")
    return q.get("question_en") or q.get("question_it") or q.get("question")


def run_benchmark(
    questions: list[dict],
    output_dir: Path,
    lang: str = "en",
    limit: int | None = None,
    skip_baseline: bool = False,
    skip_atlaspi: bool = False,
    skip_judge: bool = False,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "raw_responses.jsonl"
    eval_path = output_dir / "evaluations.jsonl"
    report_path = output_dir / "report.md"

    if limit:
        questions = questions[:limit]

    baseline = BaselineAgent() if not skip_baseline else None
    atlaspi = AtlasPIAgent() if not skip_atlaspi else None
    judge = AccuracyJudge() if not skip_judge else None

    results: list[dict] = []
    print(f"Running benchmark on {len(questions)} questions (lang={lang})")
    print(f"Output: {output_dir}")

    with raw_path.open("w", encoding="utf-8") as raw_f, eval_path.open("w", encoding="utf-8") as eval_f:
        for i, q in enumerate(questions, 1):
            qid = q.get("id", f"Q-{i:03d}")
            question_text = pick_question_text(q, lang)
            expected = q.get("expected_answer", "")
            forbidden = q.get("forbidden_facts", [])
            expected_conf = q.get("expected_confidence", "high")
            category = q.get("category", "unknown")
            epoch = q.get("epoch_bucket", "unknown")
            region = q.get("region", "unknown")

            print(f"[{i}/{len(questions)}] {qid} ({category}/{epoch}/{region}): {question_text[:80]}...")

            row: dict = {
                "id": qid,
                "category": category,
                "epoch_bucket": epoch,
                "region": region,
                "lang": lang,
                "question": question_text,
                "expected_answer": expected,
                "expected_confidence": expected_conf,
            }

            if baseline:
                try:
                    b_resp = baseline.answer(question_text)
                    row["baseline"] = b_resp
                except Exception as e:
                    row["baseline"] = {"error": str(e), "condition": "baseline"}
                    print(f"  baseline ERROR: {e}")

            if atlaspi:
                try:
                    a_resp = atlaspi.answer(question_text)
                    row["atlaspi"] = a_resp
                    print(f"  atlaspi: {a_resp.get('tool_calls_count', 0)} tool calls, "
                          f"{a_resp.get('tokens_out', 0)} tok out")
                except Exception as e:
                    row["atlaspi"] = {"error": str(e), "condition": "atlaspi"}
                    print(f"  atlaspi ERROR: {e}")

            # Persist raw immediately
            raw_f.write(json.dumps(row, ensure_ascii=False) + "\n")
            raw_f.flush()

            # Judge both
            if judge:
                eval_row = {"id": qid, "category": category, "epoch_bucket": epoch, "region": region}
                for cond in ("baseline", "atlaspi"):
                    if cond in row and "response" in row[cond]:
                        try:
                            verdict = judge.judge(
                                question=question_text,
                                expected_answer=expected,
                                forbidden_facts=forbidden,
                                response=row[cond]["response"],
                                expected_confidence=expected_conf,
                            )
                            eval_row[cond] = verdict
                        except Exception as e:
                            eval_row[cond] = {"error": str(e), "verdict": "judge_error"}
                eval_f.write(json.dumps(eval_row, ensure_ascii=False) + "\n")
                eval_f.flush()
                row["evaluations"] = eval_row

            results.append(row)

    # Aggregate and write report
    summary = aggregate_summary(results)
    with report_path.open("w", encoding="utf-8") as f:
        f.write(render_report(summary, len(questions)))

    print(f"\nDone. {len(results)} questions processed.")
    print(f"Raw: {raw_path}")
    print(f"Evals: {eval_path}")
    print(f"Report: {report_path}")
    return summary


def aggregate_summary(results: list[dict]) -> dict:
    """Compute overall + stratified deltas."""
    def _accuracy_of(ev, cond):
        if not ev or cond not in ev:
            return None
        v = ev[cond]
        if not isinstance(v, dict):
            return None
        return v.get("accuracy")

    def _hallucs_of(ev, cond):
        if not ev or cond not in ev:
            return None
        v = ev[cond]
        if not isinstance(v, dict):
            return None
        return v.get("hallucinations")

    buckets = {"overall": {"baseline": [], "atlaspi": [], "hallucs_b": [], "hallucs_a": []}}
    for dim in ("category", "epoch_bucket", "region"):
        buckets[dim] = {}

    for r in results:
        ev = r.get("evaluations", {})
        b_acc = _accuracy_of(ev, "baseline")
        a_acc = _accuracy_of(ev, "atlaspi")
        b_hal = _hallucs_of(ev, "baseline")
        a_hal = _hallucs_of(ev, "atlaspi")

        if b_acc is not None:
            buckets["overall"]["baseline"].append(b_acc)
        if a_acc is not None:
            buckets["overall"]["atlaspi"].append(a_acc)
        if b_hal is not None:
            buckets["overall"]["hallucs_b"].append(b_hal)
        if a_hal is not None:
            buckets["overall"]["hallucs_a"].append(a_hal)

        for dim in ("category", "epoch_bucket", "region"):
            key = r.get(dim, "unknown")
            if key not in buckets[dim]:
                buckets[dim][key] = {"baseline": [], "atlaspi": []}
            if b_acc is not None:
                buckets[dim][key]["baseline"].append(b_acc)
            if a_acc is not None:
                buckets[dim][key]["atlaspi"].append(a_acc)

    def _mean(xs):
        return (sum(xs) / len(xs)) if xs else 0.0

    summary = {"overall": {}, "by_category": {}, "by_epoch": {}, "by_region": {}}
    overall_b = _mean(buckets["overall"]["baseline"]) * 100
    overall_a = _mean(buckets["overall"]["atlaspi"]) * 100
    summary["overall"] = {
        "baseline_accuracy_pct": round(overall_b, 1),
        "atlaspi_accuracy_pct": round(overall_a, 1),
        "delta_pp": round(overall_a - overall_b, 1),
        "baseline_hallucinations_avg": round(_mean(buckets["overall"]["hallucs_b"]), 2),
        "atlaspi_hallucinations_avg": round(_mean(buckets["overall"]["hallucs_a"]), 2),
        "n": len(buckets["overall"]["baseline"]),
    }

    for dim, label in [("category", "by_category"), ("epoch_bucket", "by_epoch"), ("region", "by_region")]:
        for key, vals in buckets[dim].items():
            b = _mean(vals["baseline"]) * 100
            a = _mean(vals["atlaspi"]) * 100
            summary[label][key] = {
                "baseline_pct": round(b, 1),
                "atlaspi_pct": round(a, 1),
                "delta_pp": round(a - b, 1),
                "n": len(vals["baseline"]),
            }

    # Verdict based on pre-committed threshold tier
    d = summary["overall"]["delta_pp"]
    strong_categories = [k for k, v in summary["by_category"].items() if v["delta_pp"] >= 20 and v["n"] >= 3]
    if d < 5:
        verdict = "❌ FAIL — AtlasPI non giustifica MCP complexity. Revisione strategy drastica."
    elif d < 12:
        verdict = "⚠️ WEAK — margine ridotto. Investigate: coverage dataset o UX MCP?"
    elif d < 20:
        verdict = "✅ ACCEPTABLE — valore misurabile. Procedere v7.1-v7.4."
    else:
        verdict = "🟢 STRONG — killer feature. Push adoption + case study."

    # Bonus: se almeno 1 category con delta >= 20pp, upgrade by 1 tier minimum ACCEPTABLE
    if strong_categories and d < 12:
        verdict += f" (NB: {strong_categories} mostrano delta ≥+20pp — specialty strength anche con overall weak)"

    summary["verdict"] = verdict
    summary["strong_categories"] = strong_categories
    return summary


def render_report(summary: dict, total_q: int) -> str:
    ov = summary["overall"]
    lines = [
        "# AtlasPI v7.0 Benchmark — Report A/B",
        f"Generated: {datetime.now().isoformat()}",
        f"Total questions: {total_q} (judged: {ov['n']})",
        "",
        "## Overall delta",
        "",
        "| Metric | Baseline (Claude solo) | AtlasPI (Claude + tools) | Delta |",
        "|---|---|---|---|",
        f"| Accuracy | {ov['baseline_accuracy_pct']}% | {ov['atlaspi_accuracy_pct']}% | **{ov['delta_pp']:+} pp** |",
        f"| Hallucinations (avg per question) | {ov['baseline_hallucinations_avg']} | {ov['atlaspi_hallucinations_avg']} | {ov['atlaspi_hallucinations_avg'] - ov['baseline_hallucinations_avg']:+.2f} |",
        "",
        f"**Verdict**: {summary['verdict']}",
        "",
        "## By category",
        "",
        "| Category | n | Baseline | AtlasPI | Delta |",
        "|---|---|---|---|---|",
    ]
    for cat, v in sorted(summary["by_category"].items()):
        lines.append(f"| {cat} | {v['n']} | {v['baseline_pct']}% | {v['atlaspi_pct']}% | **{v['delta_pp']:+} pp** |")

    lines.extend(["", "## By epoch", "", "| Epoch | n | Baseline | AtlasPI | Delta |", "|---|---|---|---|---|"])
    for ep, v in sorted(summary["by_epoch"].items()):
        lines.append(f"| {ep} | {v['n']} | {v['baseline_pct']}% | {v['atlaspi_pct']}% | **{v['delta_pp']:+} pp** |")

    lines.extend(["", "## By region", "", "| Region | n | Baseline | AtlasPI | Delta |", "|---|---|---|---|---|"])
    for rg, v in sorted(summary["by_region"].items()):
        lines.append(f"| {rg} | {v['n']} | {v['baseline_pct']}% | {v['atlaspi_pct']}% | **{v['delta_pp']:+} pp** |")

    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", type=Path, help="Path to questions JSON")
    ap.add_argument("--output", type=Path, required=True, help="Output directory")
    ap.add_argument("--dry-run", action="store_true", help="Use seed_questions.json (5 dummies)")
    ap.add_argument("--limit", type=int, help="Limit to first N questions")
    ap.add_argument("--lang", default="en", choices=["en", "it"])
    ap.add_argument("--skip-baseline", action="store_true")
    ap.add_argument("--skip-atlaspi", action="store_true")
    ap.add_argument("--skip-judge", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        seed_path = Path(__file__).parent / "questions" / "seed_questions.json"
        if not seed_path.exists():
            print(f"Seed questions not found: {seed_path}", file=sys.stderr)
            sys.exit(1)
        questions = load_questions(seed_path)
    elif args.questions:
        questions = load_questions(args.questions)
    else:
        print("Either --dry-run or --questions <path> required", file=sys.stderr)
        sys.exit(1)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    summary = run_benchmark(
        questions=questions,
        output_dir=args.output,
        lang=args.lang,
        limit=args.limit,
        skip_baseline=args.skip_baseline,
        skip_atlaspi=args.skip_atlaspi,
        skip_judge=args.skip_judge,
    )
    print("\n" + "=" * 60)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import os
    main()
