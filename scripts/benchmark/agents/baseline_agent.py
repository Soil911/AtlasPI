"""Baseline agent: Claude senza tool access.

Claude risponde usando solo il suo internal training. Questa è la condizione
control del benchmark A/B.
"""

from __future__ import annotations

import os
import time

from anthropic import Anthropic


SYSTEM_PROMPT = (
    "You are a rigorous historian with deep knowledge of world history. "
    "Answer questions about historical entities, rulers, events, and "
    "geographic changes based on your training knowledge.\n\n"
    "Rules:\n"
    "1. Be precise with dates, names, and places.\n"
    "2. If uncertain, explicitly say so (e.g., 'I'm not sure but...').\n"
    "3. Prefer primary historical sources when citing.\n"
    "4. Do not make up facts. Say 'I don't know' rather than guess.\n"
    "5. Respond in the same language as the question (Italian or English).\n"
    "6. Be concise: 2-4 sentences typical. Cite sources only when asked."
)


class BaselineAgent:
    def __init__(self, model: str = "claude-sonnet-4-5-20250929", max_tokens: int = 800):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model
        self.max_tokens = max_tokens

    def answer(self, question: str) -> dict:
        start = time.monotonic()
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": question}],
        )
        latency_ms = (time.monotonic() - start) * 1000.0

        # Collect text content
        text_parts = [b.text for b in resp.content if b.type == "text"]
        answer_text = "\n".join(text_parts).strip()

        return {
            "condition": "baseline",
            "model": self.model,
            "response": answer_text,
            "latency_ms": round(latency_ms, 1),
            "tokens_in": resp.usage.input_tokens,
            "tokens_out": resp.usage.output_tokens,
            "stop_reason": resp.stop_reason,
            "tool_calls_count": 0,
        }
