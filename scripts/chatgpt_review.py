"""ChatGPT (gpt-5.5) wrapper for AtlasPI dual-review.

Loads API key from ~/.openai-atlaspi-key. Usage:

    from scripts.chatgpt_review import fact_check, ask
    result = fact_check(entity_dict)        # JSON dict back
    answer = ask("Suggest 10 missing African entities for AtlasPI")

Outputs are saved to data/chatgpt_review/YYYYMMDD/ for auditing.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# v6.99.29: model "ultimo" available — gpt-5.5 with reasoning_effort=low
DEFAULT_MODEL = "gpt-5.5"
FALLBACK_MODELS = ["gpt-5.4", "gpt-4-turbo"]

API_URL = "https://api.openai.com/v1/chat/completions"
KEY_FILE = Path.home() / ".openai-atlaspi-key"

# Where to log every prompt+response (auditing + cost tracking)
LOG_DIR = Path(__file__).resolve().parent.parent / "data" / "chatgpt_review"


def _load_key() -> str:
    if not KEY_FILE.exists():
        raise FileNotFoundError(f"Missing API key file: {KEY_FILE}")
    return KEY_FILE.read_text(encoding="utf-8").strip()


def _today_dir() -> Path:
    d = LOG_DIR / datetime.utcnow().strftime("%Y%m%d")
    d.mkdir(parents=True, exist_ok=True)
    return d


def _log(payload: dict, response: dict, tag: str = "ask") -> None:
    """Append the (prompt, response, usage) tuple to today's log file."""
    fp = _today_dir() / f"{tag}.jsonl"
    record = {
        "ts": datetime.utcnow().isoformat(),
        "model": payload.get("model"),
        "messages": payload.get("messages"),
        "response": response.get("choices", [{}])[0].get("message", {}).get("content"),
        "usage": response.get("usage"),
    }
    with fp.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _call(messages: list[dict], *, model: str = DEFAULT_MODEL, max_tokens: int = 2500,
          reasoning_effort: str = "low", timeout: int = 180, tag: str = "ask") -> str:
    """Call OpenAI chat/completions with fallback. Returns the text content."""
    key = _load_key()
    last_error = None
    for m in [model] + FALLBACK_MODELS:
        payload = {
            "model": m,
            "messages": messages,
            "max_completion_tokens": max_tokens,
        }
        # reasoning_effort only valid for gpt-5.x — gpt-4-turbo doesn't support it
        if "gpt-5" in m or m.startswith("o"):
            payload["reasoning_effort"] = reasoning_effort
        req = urllib.request.Request(
            API_URL,
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
            _log(payload, data, tag=tag)
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            last_error = f"HTTP {e.code} on {m}: {body[:300]}"
            # Retry on rate-limit, fallback on other errors
            if e.code == 429:
                time.sleep(10)
                continue
            print(f"[chatgpt_review] {last_error}")
            # Try next fallback model
            continue
        except Exception as e:
            last_error = f"{type(e).__name__} on {m}: {e}"
            print(f"[chatgpt_review] {last_error}")
            continue
    raise RuntimeError(f"All models failed. Last error: {last_error}")


def ask(prompt: str, *, system: str | None = None, **kwargs) -> str:
    """One-shot question. Returns plain text."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return _call(messages, tag="ask", **kwargs)


def fact_check(entity: dict, *, max_tokens: int = 2500) -> dict:
    """Fact-check an entity dict against gpt-5.5.

    Returns dict with keys verdict, confidence, notes, corrections (array).
    """
    system = (
        "You are a historian fact-checker for the AtlasPI historical-geographic database. "
        "Reply ONLY in valid JSON with keys: verdict (correct/partial/incorrect), "
        "confidence (0.0-1.0), notes (1-3 sentences), corrections (array of strings — "
        "specific factual fixes you suggest). Do not include any markdown or prose outside JSON."
    )
    # Build user prompt from entity
    fields = []
    for key in ("id", "name_original", "name_original_lang", "entity_type",
                "year_start", "year_end", "capital_name", "ethical_notes",
                "confidence_score", "boundary_source"):
        if key in entity and entity[key] is not None:
            v = entity[key]
            if isinstance(v, str) and len(v) > 400:
                v = v[:400] + "..."
            fields.append(f"{key}: {v}")
    sources = entity.get("sources", [])
    fields.append(f"n_sources: {len(sources)}")
    if sources:
        sample = "; ".join(s.get("citation", "")[:120] for s in sources[:3])
        fields.append(f"sample_sources: {sample}")
    prompt = "Entity to fact-check:\n" + "\n".join(fields) + (
        "\n\nIs the above historically accurate? List any factual errors, "
        "missing key dates/people, or ethical concerns (omitted conquest, "
        "non-locale names, etc.)."
    )
    raw = ask(prompt, system=system, max_tokens=max_tokens)
    # Strip ```json fences if present
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```", 2)
        text = text[1] if len(text) >= 2 else text[0]
        if text.startswith("json\n"):
            text = text[5:]
        text = text.rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # If parsing fails, wrap raw text
        return {"verdict": "unparsed", "confidence": 0.0, "notes": raw, "corrections": []}


if __name__ == "__main__":
    # Self-test
    print("[self-test] gpt-5.5 ping...")
    print(ask("Reply with one word: ok.", max_tokens=50))
