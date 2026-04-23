"""Cross-vendor rejudge: rilancia i judgments di un results dir con GPT-4o
invece di Claude Opus, salva evaluations_gpt4o.jsonl, produce side-by-side
report Opus-vs-GPT4o per cross-vendor bias mitigation.

Usage:
    # After running `benchmark_3way.py` with Claude Opus judge:
    OPENAI_API_KEY=sk-... python -m scripts.benchmark.cross_vendor_rejudge \\
        scripts/benchmark/results/3way-hard-v2

Output:
    evaluations_gpt4o.jsonl    — nuovi verdetti GPT-4o
    cross_vendor_report.md     — comparison Opus vs GPT-4o per condition + attribution
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root))

from scripts.benchmark.judges.openai_judge import OpenAIJudge


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def save_jsonl(path: Path, rows: list[dict]):
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


CONDITIONS = ("baseline", "atlaspi_prompt_only", "atlaspi_full")


def mean_acc(evals: list[dict], cond: str) -> tuple[float, int]:
    vals = []
    for e in evals:
        v = e.get(cond, {})
        if isinstance(v, dict) and isinstance(v.get("accuracy"), (int, float)):
            vals.append(v["accuracy"])
    return (sum(vals) / len(vals) * 100 if vals else 0.0, len(vals))


def mean_halluc(evals: list[dict], cond: str) -> float:
    vals = []
    for e in evals:
        v = e.get(cond, {})
        if isinstance(v, dict) and isinstance(v.get("hallucinations"), (int, float)):
            vals.append(v["hallucinations"])
    return sum(vals) / len(vals) if vals else 0.0


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir", type=Path)
    ap.add_argument("--limit", type=int, help="Limit to first N Q (for quick test)")
    args = ap.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    raw_path = args.results_dir / "raw_responses.jsonl"
    opus_evals_path = args.results_dir / "evaluations.jsonl"
    gpt_evals_path = args.results_dir / "evaluations_gpt4o.jsonl"
    cross_report_path = args.results_dir / "cross_vendor_report.md"

    if not raw_path.exists() or not opus_evals_path.exists():
        print(f"ERROR: raw_responses or evaluations not found in {args.results_dir}", file=sys.stderr)
        sys.exit(1)

    raw_rows = load_jsonl(raw_path)
    opus_evals = load_jsonl(opus_evals_path)

    # Resume: load existing gpt4o evals if any
    gpt_evals = load_jsonl(gpt_evals_path) if gpt_evals_path.exists() else []
    gpt_by_id = {e["id"]: e for e in gpt_evals}

    if args.limit:
        raw_rows = raw_rows[:args.limit]

    judge = OpenAIJudge()
    print(f"Cross-vendor rejudge: {len(raw_rows)} Q × {len(CONDITIONS)} conditions with GPT-4o")

    for i, raw in enumerate(raw_rows, 1):
        qid = raw["id"]
        q_text = raw.get("question", "")
        expected = raw.get("expected_answer", "")
        forbidden = raw.get("forbidden_facts", [])
        expected_conf = raw.get("expected_confidence", "high")

        # Skip if GPT-4o eval already complete for this Q
        existing = gpt_by_id.get(qid, {"id": qid, "category": raw.get("category"),
                                        "epoch_bucket": raw.get("epoch_bucket"),
                                        "region": raw.get("region")})
        all_judged = all(
            isinstance(existing.get(c), dict) and existing[c].get("accuracy") is not None
            for c in CONDITIONS
            if isinstance(raw.get(c), dict) and raw[c].get("response")
        )
        if all_judged and qid in gpt_by_id:
            print(f"[{i}/{len(raw_rows)}] {qid}: already judged by GPT-4o, skip")
            continue

        print(f"[{i}/{len(raw_rows)}] {qid} [{raw.get('category')}/{raw.get('region')}]")

        for cond in CONDITIONS:
            if isinstance(existing.get(cond), dict) and existing[cond].get("accuracy") is not None:
                continue
            cond_resp = raw.get(cond)
            if not (isinstance(cond_resp, dict) and cond_resp.get("response")):
                continue
            try:
                verdict = judge.judge(
                    question=q_text,
                    expected_answer=expected,
                    forbidden_facts=forbidden,
                    response=cond_resp["response"],
                    expected_confidence=expected_conf,
                )
                existing[cond] = verdict
                acc = verdict.get("accuracy")
                print(f"  {cond}: acc={acc}")
            except Exception as e:
                existing[cond] = {"error": str(e)[:200], "verdict": "judge_error"}
                print(f"  {cond}: ERROR {str(e)[:100]}")

        gpt_by_id[qid] = existing
        save_jsonl(gpt_evals_path, list(gpt_by_id.values()))

    # Comparison report
    gpt_all = list(gpt_by_id.values())
    report_lines = ["# Cross-vendor judge comparison: Claude Opus vs GPT-4o\n"]
    report_lines.append(f"Sample: {len(raw_rows)} Q × {len(CONDITIONS)} conditions\n")
    report_lines.append("## Accuracy per condition (both judges)\n")
    report_lines.append("| Condition | Opus acc | GPT-4o acc | Δ (GPT-Opus) | Opus halluc | GPT-4o halluc |")
    report_lines.append("|---|---|---|---|---|---|")

    for cond in CONDITIONS:
        o_acc, o_n = mean_acc(opus_evals, cond)
        g_acc, g_n = mean_acc(gpt_all, cond)
        o_h = mean_halluc(opus_evals, cond)
        g_h = mean_halluc(gpt_all, cond)
        delta = g_acc - o_acc
        report_lines.append(
            f"| {cond} | {o_acc:.1f}% (n={o_n}) | {g_acc:.1f}% (n={g_n}) | "
            f"{delta:+.1f}pp | {o_h:.2f} | {g_h:.2f} |"
        )

    report_lines.append("\n## Attribution (per judge)\n")
    report_lines.append("| Effect | Opus | GPT-4o | Agreement |")
    report_lines.append("|---|---|---|---|")

    o_b, _ = mean_acc(opus_evals, "baseline")
    o_p, _ = mean_acc(opus_evals, "atlaspi_prompt_only")
    o_f, _ = mean_acc(opus_evals, "atlaspi_full")
    g_b, _ = mean_acc(gpt_all, "baseline")
    g_p, _ = mean_acc(gpt_all, "atlaspi_prompt_only")
    g_f, _ = mean_acc(gpt_all, "atlaspi_full")

    effects = [
        ("prompt_effect (prompt_only - baseline)", o_p - o_b, g_p - g_b),
        ("tool_effect (full - prompt_only)", o_f - o_p, g_f - g_p),
        ("combined_effect (full - baseline)", o_f - o_b, g_f - g_b),
    ]
    for name, o_eff, g_eff in effects:
        diff = g_eff - o_eff
        agreement = "HIGH" if abs(diff) < 2 else "MED" if abs(diff) < 5 else "LOW"
        report_lines.append(
            f"| {name} | {o_eff:+.1f}pp | {g_eff:+.1f}pp | {agreement} (Δ={diff:+.1f}pp) |"
        )

    report_lines.append("\n## Interpretation\n")
    tool_diff = abs((g_f - g_p) - (o_f - o_p))
    if tool_diff < 2:
        report_lines.append(
            "- **Tool effect HIGH agreement**: cross-vendor validation **conferma** il "
            "TOOL-DOMINANT finding di bank v2 hard. Opus judge non aveva bias same-vendor."
        )
    elif tool_diff < 5:
        report_lines.append(
            "- **Tool effect MED agreement**: direzione qualitativa confermata ma "
            "magnitude differ. Caveat nel report finale."
        )
    else:
        report_lines.append(
            "- **Tool effect LOW agreement**: Opus e GPT-4o danno verdetti divergenti. "
            "Same-vendor bias POSSIBILE. Servirebbe 3° judge (Gemini) per triangolare."
        )

    with cross_report_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\nCross-vendor report: {cross_report_path}")
    print("\n".join(report_lines))


if __name__ == "__main__":
    main()
