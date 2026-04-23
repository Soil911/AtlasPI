"""AtlasPI-prompt-only agent: Claude con system prompt atlaspi MA senza tools.

Isolation test (v7.0.3): separa l'effetto prompt engineering dall'effetto
tool usage. Se atlaspi-prompt-only > baseline, il valore è nel prompt.
Se atlaspi-full > atlaspi-prompt-only, il valore aggiunto viene dai tools.

Usa lo STESSO system prompt di atlaspi_agent.py (importato), zero tool
definitions. Signature identica a baseline_agent.py per drop-in.
"""

from __future__ import annotations

import os
import time

from anthropic import Anthropic

# Import same system prompt used by full atlaspi agent
from scripts.benchmark.agents.atlaspi_agent import SYSTEM_PROMPT as ATLASPI_SYSTEM_PROMPT


class AtlasPIPromptOnlyAgent:
    def __init__(self, model: str = "claude-sonnet-4-5-20250929", max_tokens: int = 800):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model
        self.max_tokens = max_tokens

    def answer(self, question: str) -> dict:
        start = time.monotonic()
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=ATLASPI_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": question}],
        )
        latency_ms = (time.monotonic() - start) * 1000.0

        text_parts = [b.text for b in resp.content if b.type == "text"]
        answer_text = "\n".join(text_parts).strip()

        return {
            "condition": "atlaspi_prompt_only",
            "model": self.model,
            "response": answer_text,
            "latency_ms": round(latency_ms, 1),
            "tokens_in": resp.usage.input_tokens,
            "tokens_out": resp.usage.output_tokens,
            "stop_reason": resp.stop_reason,
            "tool_calls_count": 0,  # by design: no tools available
        }
