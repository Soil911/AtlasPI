"""Cross-vendor judge: GPT-4o per validare i risultati del Claude Opus judge.

Stessa rubric di accuracy_judge.py (Opus) per confronto side-by-side.
Usa OpenAI SDK con JSON mode strict + stesso prompt blinded (non rivela
quale condition ha prodotto la risposta).

Install: `pip install openai>=1.0.0`
Env: OPENAI_API_KEY
Cost: GPT-4o ~$2.50/M input + $10/M output → ~$0.005 per judge call
      → 30 Q × 3 cond = 90 calls → ~$0.45 totale
"""

from __future__ import annotations

import json
import os
import time

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # lazy-fail: only needed when class instantiated


JUDGE_SYSTEM = (
    "You are an impartial expert historian judge evaluating answers to "
    "historical questions. You compare a candidate response to an expected "
    "answer and forbidden facts list. You produce strict JSON output.\n\n"
    "Scoring rubric:\n"
    "- accuracy (0.0-1.0): how close to expected. 1.0 = fully correct, "
    "0.5 = partially correct or key fact right but details wrong, "
    "0.0 = wrong or missing.\n"
    "- hallucinations (integer): count of forbidden_facts OR other fabricated "
    "facts in the response (names, dates, events that contradict expected or "
    "are invented).\n"
    "- completeness (0.0-1.0): how much of expected info is covered.\n"
    "- uncertainty_honesty (boolean): response appropriately says 'I don't "
    "know' or hedges when expected_confidence was 'medium/low'.\n"
    "- verdict (string): one of 'correct', 'partially_correct', 'wrong', 'refused'.\n\n"
    "Be strict. A response that says 'Impero Bizantino' when expected is "
    "'Impero Romano d'Oriente, dinastia Paleologa, Manuel II' is partially_correct "
    "at best.\n\n"
    "Output MUST be valid JSON with exactly these keys, no extra text, no markdown."
)


JUDGE_USER_TEMPLATE = """Question: {question}

Expected answer: {expected_answer}

Forbidden facts (count as hallucinations if present):
{forbidden_facts}

Expected confidence level: {expected_confidence}

Response to judge:
---
{response}
---

Produce JSON with: accuracy, hallucinations, completeness, uncertainty_honesty, verdict, reasoning (1-2 sentences)."""


class OpenAIJudge:
    def __init__(self, model: str = "gpt-4o", max_tokens: int = 500):
        if OpenAI is None:
            raise ImportError("Install `openai>=1.0.0`")
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = model
        self.max_tokens = max_tokens

    def judge(self, question: str, expected_answer: str, forbidden_facts: list[str],
              response: str, expected_confidence: str = "high") -> dict:
        start = time.monotonic()
        forbidden_str = "\n".join(f"- {f}" for f in forbidden_facts) if forbidden_facts else "(none)"

        user_msg = JUDGE_USER_TEMPLATE.format(
            question=question,
            expected_answer=expected_answer,
            forbidden_facts=forbidden_str,
            expected_confidence=expected_confidence,
            response=response,
        )

        # GPT-4o supports response_format json_object for strict JSON
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
        )

        text = resp.choices[0].message.content or ""
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = {
                "accuracy": None,
                "hallucinations": None,
                "completeness": None,
                "uncertainty_honesty": None,
                "verdict": "parse_error",
                "reasoning": f"GPT-4o output not valid JSON: {text[:200]}",
            }

        parsed["judge_model"] = self.model
        parsed["judge_latency_ms"] = round((time.monotonic() - start) * 1000.0, 1)
        parsed["judge_tokens_in"] = resp.usage.prompt_tokens
        parsed["judge_tokens_out"] = resp.usage.completion_tokens
        return parsed
