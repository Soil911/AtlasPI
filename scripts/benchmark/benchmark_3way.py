"""v7.0.3 — Isolation test prompt-vs-tool.

Runs 20 stratified questions across 3 conditions:
1. baseline: Claude + "historian" prompt (no tools)
2. atlaspi_prompt_only: Claude + atlaspi prompt (no tools) ← new isolation
3. atlaspi_full: Claude + atlaspi prompt + MCP-like tools

Then judges all 3 with Claude Opus.

Purpose: determine where the (marginal) accuracy advantage comes from:
- If atlaspi_prompt_only > baseline → value is in prompt engineering
- If atlaspi_full > atlaspi_prompt_only → marginal tool value
- If atlaspi_full <= atlaspi_prompt_only → tools are dead weight

Usage:
    ANTHROPIC_API_KEY=sk-... python -m scripts.benchmark.benchmark_3way \\
        --questions scripts/benchmark/questions/questions-bank-v1.json \\
        --output scripts/benchmark/results/3way-v1 \\
        --limit 20

Safety:
- Per-Q flush to disk (resumable)
- Credit-exhaustion guard (exit 2)
- Rate limit: sleep 3s between agents per Q (avoid 429)
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root))

from scripts.benchmark.agents.baseline_agent import BaselineAgent
from scripts.benchmark.agents.atlaspi_agent import AtlasPIAgent
from scripts.benchmark.agents.atlaspi_prompt_only_agent import AtlasPIPromptOnlyAgent
from scripts.benchmark.judges.accuracy_judge import AccuracyJudge
from scripts.benchmark.benchmark_runner import load_questions, pick_question_text


CONDITIONS = ("baseline", "atlaspi_prompt_only", "atlaspi_full")


def stratified_sample(questions: list[dict], n_per_category: int = 4, seed: int = 42) -> list[dict]:
    """Stratified random sample by category."""
    rng = random.Random(seed)
    by_cat = {}
    for q in questions:
        cat = q.get("category", "unknown")
        by_cat.setdefault(cat, []).append(q)
    sample = []
    for cat, qs in by_cat.items():
        rng.shuffle(qs)
        sample.extend(qs[:n_per_category])
    rng.shuffle(sample)
    return sample


def save_jsonl(path: Path, rows: list[dict]):
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def is_credit_error(e: Exception) -> bool:
    s = str(e).lower()
    return "credit balance" in s or "low to access" in s


def is_rate_limit(e: Exception) -> bool:
    s = str(e).lower()
    return "rate_limit" in s or "rate limit" in s or "429" in s


def main():
    # Fix Windows cp1252 stdout crash on unicode chars (e.g. Ọyọ́, Cham letters).
    # errors='replace' ensures progress prints never crash on char mapping.
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass  # Python <3.7 or already utf-8

    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--limit", type=int, default=20, help="N questions sampled (stratified by category)")
    ap.add_argument("--lang", default="en", choices=["en", "it"])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--sleep", type=float, default=3.0, help="Sleep seconds between agents per Q (rate limit mitigation)")
    args = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    args.output.mkdir(parents=True, exist_ok=True)
    raw_path = args.output / "raw_responses.jsonl"
    eval_path = args.output / "evaluations.jsonl"
    report_path = args.output / "report.md"
    summary_path = args.output / "summary.json"

    all_questions = load_questions(args.questions)
    n_per_cat = max(1, args.limit // 5)  # 5 categories
    sample = stratified_sample(all_questions, n_per_category=n_per_cat, seed=args.seed)
    if args.limit:
        sample = sample[:args.limit]

    print(f"Sampled {len(sample)} questions across categories")
    from collections import Counter
    c = Counter(q.get("category") for q in sample)
    print(f"Distribution: {dict(c)}")

    baseline = BaselineAgent()
    prompt_only = AtlasPIPromptOnlyAgent()
    full = AtlasPIAgent()
    judge = AccuracyJudge()

    # Resume support: read existing if any
    raw_rows = []
    eval_rows = []
    if raw_path.exists():
        raw_rows = [json.loads(l) for l in raw_path.open(encoding="utf-8") if l.strip()]
    if eval_path.exists():
        eval_rows = [json.loads(l) for l in eval_path.open(encoding="utf-8") if l.strip()]
    raw_by_id = {r["id"]: r for r in raw_rows}
    eval_by_id = {e["id"]: e for e in eval_rows}

    for i, q in enumerate(sample, 1):
        qid = q["id"]
        q_text = pick_question_text(q, args.lang)
        expected = q.get("expected_answer", "")
        forbidden = q.get("forbidden_facts", [])
        expected_conf = q.get("expected_confidence", "high")

        # Skip if already complete
        existing = raw_by_id.get(qid)
        all_done = (
            existing
            and all(
                isinstance(existing.get(c), dict) and existing[c].get("response")
                for c in CONDITIONS
            )
        )
        if all_done:
            print(f"[{i}/{len(sample)}] {qid}: already complete, skipping")
            continue

        row = existing or {
            "id": qid,
            "category": q.get("category"),
            "epoch_bucket": q.get("epoch_bucket"),
            "region": q.get("region"),
            "lang": args.lang,
            "question": q_text,
            "expected_answer": expected,
            "expected_confidence": expected_conf,
        }

        print(f"[{i}/{len(sample)}] {qid} [{q.get('category')}/{q.get('region')}]: {q_text[:70]}...")

        for cond_name, agent in (
            ("baseline", baseline),
            ("atlaspi_prompt_only", prompt_only),
            ("atlaspi_full", full),
        ):
            existing_cond = row.get(cond_name)
            if isinstance(existing_cond, dict) and existing_cond.get("response"):
                continue

            for attempt in range(3):
                try:
                    resp = agent.answer(q_text)
                    row[cond_name] = resp
                    tool_info = f", tools={resp.get('tool_calls_count',0)}" if cond_name == "atlaspi_full" else ""
                    print(f"  {cond_name}: {resp.get('tokens_out',0)} tok{tool_info}")
                    break
                except Exception as e:
                    if is_credit_error(e):
                        print(f"  {cond_name}: CREDIT EXHAUSTED. Saving and stopping.")
                        raw_by_id[qid] = row
                        save_jsonl(raw_path, list(raw_by_id.values()))
                        save_jsonl(eval_path, list(eval_by_id.values()))
                        sys.exit(2)
                    if is_rate_limit(e):
                        wait = 10 * (attempt + 1)
                        print(f"  {cond_name}: RATE LIMIT, sleep {wait}s then retry")
                        time.sleep(wait)
                        continue
                    # Other error: log and proceed
                    row[cond_name] = {"error": str(e)[:300], "condition": cond_name}
                    print(f"  {cond_name}: ERROR: {str(e)[:150]}")
                    break
            else:
                # All retries failed
                row[cond_name] = {"error": "max retries on rate limit", "condition": cond_name}
                print(f"  {cond_name}: max retries exhausted")

            time.sleep(args.sleep)  # rate limit mitigation

        raw_by_id[qid] = row

        # Judge all 3 conditions
        eval_row = eval_by_id.get(qid, {"id": qid, "category": row.get("category"),
                                          "epoch_bucket": row.get("epoch_bucket"),
                                          "region": row.get("region")})
        for cond_name in CONDITIONS:
            existing_verdict = eval_row.get(cond_name)
            if isinstance(existing_verdict, dict) and existing_verdict.get("accuracy") is not None:
                continue
            cond_resp = row.get(cond_name)
            if not (isinstance(cond_resp, dict) and cond_resp.get("response")):
                continue
            for attempt in range(3):
                try:
                    verdict = judge.judge(
                        question=q_text,
                        expected_answer=expected,
                        forbidden_facts=forbidden,
                        response=cond_resp["response"],
                        expected_confidence=expected_conf,
                    )
                    eval_row[cond_name] = verdict
                    break
                except Exception as e:
                    if is_credit_error(e):
                        print(f"  judge/{cond_name}: CREDIT EXHAUSTED.")
                        eval_by_id[qid] = eval_row
                        save_jsonl(raw_path, list(raw_by_id.values()))
                        save_jsonl(eval_path, list(eval_by_id.values()))
                        sys.exit(2)
                    if is_rate_limit(e):
                        wait = 10 * (attempt + 1)
                        time.sleep(wait)
                        continue
                    eval_row[cond_name] = {"error": str(e)[:300], "verdict": "judge_error"}
                    break
            time.sleep(args.sleep / 2)

        eval_by_id[qid] = eval_row

        # Flush after every Q
        save_jsonl(raw_path, list(raw_by_id.values()))
        save_jsonl(eval_path, list(eval_by_id.values()))

    # Aggregate
    def mean_acc(cond: str) -> tuple[float, int]:
        vals = []
        for e in eval_by_id.values():
            v = e.get(cond, {})
            if isinstance(v, dict) and isinstance(v.get("accuracy"), (int, float)):
                vals.append(v["accuracy"])
        return (sum(vals) / len(vals) * 100 if vals else 0.0, len(vals))

    def mean_halluc(cond: str) -> float:
        vals = []
        for e in eval_by_id.values():
            v = e.get(cond, {})
            if isinstance(v, dict) and isinstance(v.get("hallucinations"), (int, float)):
                vals.append(v["hallucinations"])
        return sum(vals) / len(vals) if vals else 0.0

    b_acc, b_n = mean_acc("baseline")
    p_acc, p_n = mean_acc("atlaspi_prompt_only")
    f_acc, f_n = mean_acc("atlaspi_full")

    summary = {
        "n_sample": len(sample),
        "conditions": {
            "baseline": {"accuracy_pct": round(b_acc, 1), "hallucinations_avg": round(mean_halluc("baseline"), 3), "n": b_n},
            "atlaspi_prompt_only": {"accuracy_pct": round(p_acc, 1), "hallucinations_avg": round(mean_halluc("atlaspi_prompt_only"), 3), "n": p_n},
            "atlaspi_full": {"accuracy_pct": round(f_acc, 1), "hallucinations_avg": round(mean_halluc("atlaspi_full"), 3), "n": f_n},
        },
        "deltas": {
            "prompt_effect": round(p_acc - b_acc, 1),
            "tool_effect": round(f_acc - p_acc, 1),
            "combined_effect": round(f_acc - b_acc, 1),
        },
    }

    # Interpretation
    pe = summary["deltas"]["prompt_effect"]
    te = summary["deltas"]["tool_effect"]
    ce = summary["deltas"]["combined_effect"]

    if abs(ce) < 2:
        diagnosis = "FLAT: neither prompt nor tools move the needle meaningfully"
    elif pe > 3 and te < 1:
        diagnosis = "PROMPT-DOMINANT: value is in system prompt, tools are dead weight"
    elif te > 3 and pe < 2:
        diagnosis = "TOOL-DOMINANT: value is in tool calls, prompt alone insufficient"
    elif pe > 2 and te > 2:
        diagnosis = "SYNERGISTIC: prompt + tool both contribute"
    elif pe > 1 and te < 0:
        diagnosis = "PROMPT-POSITIVE-TOOL-NEGATIVE: prompt helps but tool adds noise"
    else:
        diagnosis = "MIXED: unclear attribution"

    summary["diagnosis"] = diagnosis

    # Write outputs
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    report_lines = [
        "# 3-Way Isolation Test (v7.0.3)",
        "",
        f"Sample: {len(sample)} questions (stratified by category)",
        "",
        "## Accuracy per condition",
        "",
        "| Condition | Accuracy | Hallucinations | N |",
        "|---|---|---|---|",
        f"| baseline (Claude only) | {b_acc:.1f}% | {mean_halluc('baseline'):.2f} | {b_n} |",
        f"| atlaspi_prompt_only | {p_acc:.1f}% | {mean_halluc('atlaspi_prompt_only'):.2f} | {p_n} |",
        f"| atlaspi_full (prompt + tools) | {f_acc:.1f}% | {mean_halluc('atlaspi_full'):.2f} | {f_n} |",
        "",
        "## Attribution",
        "",
        f"- **Prompt effect** (prompt_only - baseline): **{pe:+.1f}pp**",
        f"- **Tool effect** (full - prompt_only): **{te:+.1f}pp**",
        f"- **Combined effect** (full - baseline): **{ce:+.1f}pp**",
        "",
        f"**Diagnosis**: {diagnosis}",
        "",
    ]
    with report_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")

    print(f"\nDone. Summary: {summary_path}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
