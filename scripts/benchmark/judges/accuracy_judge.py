"""LLM-as-judge per valutare accuracy + hallucinations + completeness.

Usa Claude Opus (modello più forte di Sonnet testata) come giudice.
Prompt blinded: non sa quale condizione (baseline/atlaspi) ha prodotto
la risposta. Output JSON strict.
"""

from __future__ import annotations

import json
import os
import time

from anthropic import Anthropic


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
    "- completeness (0.0-1.0): how much of expected info is covered. "
    "1.0 = all key points covered, 0.5 = half covered, 0.0 = missing core.\n"
    "- uncertainty_honesty (boolean): response appropriately says 'I don't "
    "know' or hedges when expected_confidence was 'medium/low'. True if honest.\n"
    "- verdict (string): one of 'correct', 'partially_correct', 'wrong', "
    "'refused' (said don't know).\n\n"
    "Be strict. A response that says 'Impero Bizantino' when expected is "
    "'Impero Romano d'Oriente, dinastia Paleologa, Manuel II' is partially_correct "
    "at best — the core fact is right but detail is missing.\n\n"
    "Output MUST be valid JSON with exactly these keys, no extra text."
)


JUDGE_USER_TEMPLATE = """Question: {question}

Expected answer: {expected_answer}

Forbidden facts (if present in response, count as hallucinations):
{forbidden_facts}

Expected confidence level (for uncertainty_honesty): {expected_confidence}

Response to judge:
---
{response}
---

Produce JSON with: accuracy, hallucinations, completeness, uncertainty_honesty, verdict, reasoning (1-2 sentences)."""


class AccuracyJudge:
    def __init__(self, model: str = "claude-opus-4-5-20251101", max_tokens: int = 500):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
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

        resp = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=JUDGE_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )

        text_parts = [b.text for b in resp.content if b.type == "text"]
        text = "\n".join(text_parts).strip()

        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:].strip()
            text = text.strip()

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = {
                "accuracy": None,
                "hallucinations": None,
                "completeness": None,
                "uncertainty_honesty": None,
                "verdict": "parse_error",
                "reasoning": f"Judge output was not valid JSON: {text[:200]}",
            }

        parsed["judge_model"] = self.model
        parsed["judge_latency_ms"] = round((time.monotonic() - start) * 1000.0, 1)
        parsed["judge_tokens_in"] = resp.usage.input_tokens
        parsed["judge_tokens_out"] = resp.usage.output_tokens
        return parsed
