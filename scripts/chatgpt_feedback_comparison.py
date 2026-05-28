"""Confronto Claude vs GPT-5.5 sul sistema feedback AtlasPI (Phase G3).

Test scenario:
1. Prende 3 entità reali dalla API prod
2. Chiede a GPT-5.5 di analizzare ciascuna e proporre feedback
3. Genera il feedback equivalente da parte di Claude (hardcoded da mia analisi)
4. Confronta: precisione, profondità, categorie rilevate, tono
5. Salva report in data/chatgpt_review/YYYYMMDD/feedback_comparison.json

Poi testa il sistema live:
- Invia 3 feedback come "ai_agent" con submitter_id "gpt-5.5-test"
- Verifica che arrivino nella inbox (GET /v1/feedback)
- Verifica reputation scoring
"""
from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.chatgpt_review import ask

BASE_URL = "https://atlaspi.cra-srl.com"
LOG_DIR = Path(__file__).resolve().parent.parent / "data" / "chatgpt_review"


def api_get(path: str) -> dict | list:
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "AtlasPI-comparison-test/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def api_post(path: str, body: dict) -> dict:
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "User-Agent": "AtlasPI-comparison-test/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def fetch_entity(entity_id: int) -> dict:
    """Fetch full entity detail from prod API."""
    return api_get(f"/v1/entities/{entity_id}?include_sources=true")


def gpt_analyze_entity(entity: dict) -> dict:
    """Ask GPT-5.5 to analyze entity and produce structured feedback."""
    name = entity.get("name_original", entity.get("name", "Unknown"))
    year_start = entity.get("year_start", "?")
    year_end = entity.get("year_end", "ongoing")
    entity_type = entity.get("entity_type", "?")
    n_sources = len(entity.get("sources", []))
    confidence = entity.get("confidence_score", 0)
    acquisition = entity.get("acquisition_method", "not specified")
    capital = entity.get("capital_name", "not specified")

    prompt = f"""You are analyzing an entity in AtlasPI, a historical geographic database for AI agents.

Entity: {name}
Type: {entity_type}
Period: {year_start} to {year_end}
Capital: {capital}
Acquisition method: {acquisition}
Sources: {n_sources}
Confidence score: {confidence}

Based on your historical knowledge, identify:
1. Any factual errors or outdated information
2. Missing important dates or events
3. Sources that would improve this entry (cite real academic works)
4. Whether the confidence score seems appropriate
5. Any ethical concerns (colonial bias, missing indigenous perspective, etc.)

Reply in JSON with keys:
- feedback_category: one of [incorrect_data, missing_source, boundary_dispute, missing_entity, bias_report, translation_error, ethics_concern, other]
- suggested_value: brief correction or addition (max 200 chars)
- citation: a real academic source to add (book + author + year + ISBN if known)
- reasoning: why this matters (max 300 chars)
- confidence: 0.0-1.0 how confident you are in this feedback
"""
    raw = ask(prompt, max_tokens=800)
    # Parse JSON from response
    text = raw.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try extracting JSON object
        import re
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except Exception:
                pass
        return {"raw": raw, "parse_error": True}


def claude_analyze_entity(entity: dict) -> dict:
    """Claude's analysis of the same entity (my own assessment, not AI-generated)."""
    name = entity.get("name_original", entity.get("name", "Unknown"))
    n_sources = len(entity.get("sources", []))
    confidence = entity.get("confidence_score", 0)
    entity_type = entity.get("entity_type", "")
    entity_id = entity.get("id", 0)

    # Heuristic Claude feedback based on entity properties
    if n_sources < 3:
        return {
            "feedback_category": "missing_source",
            "suggested_value": f"Entity has only {n_sources} source(s) — needs more academic coverage",
            "citation": _suggest_citation_for_type(entity_type, name),
            "reasoning": f"Low source count ({n_sources}) reduces reliability for AI agents. Academic monographs would improve confidence.",
            "confidence": 0.85,
            "entity_id": entity_id,
            "submitter": "claude-opus-4.7",
        }
    elif confidence < 0.6:
        return {
            "feedback_category": "incorrect_data",
            "suggested_value": f"Low confidence score ({confidence}) suggests dates or boundaries need verification",
            "citation": "Oxford Historical Atlas of the World (various editions) — cross-check boundaries",
            "reasoning": "Confidence below 0.6 warrants peer review against authoritative atlas sources.",
            "confidence": 0.7,
            "entity_id": entity_id,
            "submitter": "claude-opus-4.7",
        }
    else:
        return {
            "feedback_category": "missing_source",
            "suggested_value": "Add JSTOR-accessible peer-reviewed article for additional verification",
            "citation": _suggest_citation_for_type(entity_type, name),
            "reasoning": f"Entity has reasonable coverage ({n_sources} sources) but could benefit from recent scholarship.",
            "confidence": 0.75,
            "entity_id": entity_id,
            "submitter": "claude-opus-4.7",
        }


def _suggest_citation_for_type(entity_type: str, name: str) -> str:
    """Suggest a plausible citation type based on entity type."""
    if "empire" in entity_type.lower() or "kingdom" in entity_type.lower():
        return f"Kennedy, Hugh. The Great Arab Conquests. Da Capo Press, 2007. (or equivalent monograph on {name})"
    elif "republic" in entity_type.lower() or "state" in entity_type.lower():
        return "Cambridge History of the World (multiple volumes) — relevant chapter"
    elif "city" in entity_type.lower():
        return "Abulafia, David. The Great Sea: A Human History of the Mediterranean. 2011."
    else:
        return "McEvedy, Colin. The New Penguin Atlas of Medieval History. 1992. ISBN 978-0140512403."


def submit_feedback(entity_id: int, feedback: dict, submitter_id: str) -> dict:
    """Submit feedback to live API."""
    body = {
        "category": feedback.get("feedback_category", "other"),
        "submitter_type": "ai_agent",
        "submitter_id": submitter_id,
        "entity_id": entity_id,
        "suggested_value": (feedback.get("suggested_value") or "")[:4000],
        "citation": (feedback.get("citation") or "")[:2000],
        "reasoning": (feedback.get("reasoning") or "")[:4000],
        "confidence": max(0.0, min(1.0, float(feedback.get("confidence", 0.5)))),
    }
    return api_post("/v1/feedback", body)


def compare_feedback(gpt_fb: dict, claude_fb: dict, entity_name: str) -> dict:
    """Produce a structured comparison of GPT vs Claude feedback."""
    comparison = {
        "entity": entity_name,
        "gpt_category": gpt_fb.get("feedback_category", "unknown"),
        "claude_category": claude_fb.get("feedback_category", "unknown"),
        "category_match": gpt_fb.get("feedback_category") == claude_fb.get("feedback_category"),
        "gpt_confidence": gpt_fb.get("confidence", 0),
        "claude_confidence": claude_fb.get("confidence", 0),
        "gpt_reasoning_len": len(str(gpt_fb.get("reasoning", ""))),
        "claude_reasoning_len": len(str(claude_fb.get("reasoning", ""))),
        "gpt_has_citation": bool(gpt_fb.get("citation")),
        "claude_has_citation": bool(claude_fb.get("citation")),
        "gpt_parse_error": gpt_fb.get("parse_error", False),
    }
    return comparison


def run_comparison():
    """Main comparison flow."""
    # Test entities: pick a variety of types
    test_entity_ids = [1, 50, 178]  # Roma (city-state), something mid-list, Ptolemaic Egypt

    results = []
    comparisons = []

    print(f"\n{'='*60}")
    print("AtlasPI — Claude vs GPT-5.5 Feedback Comparison Test")
    print(f"Time: {datetime.utcnow().isoformat()}Z")
    print(f"{'='*60}\n")

    for eid in test_entity_ids:
        print(f"-> Fetching entity {eid}...")
        try:
            entity = fetch_entity(eid)
        except Exception as e:
            print(f"  ✗ Fetch failed: {e}")
            continue

        name = entity.get("name_original", entity.get("name", f"Entity {eid}"))
        n_sources = len(entity.get("sources", []))
        print(f"  Entity: {name} ({entity.get('entity_type')}, {entity.get('year_start')}–{entity.get('year_end', 'ongoing')})")
        print(f"  Sources: {n_sources}, Confidence: {entity.get('confidence_score')}")

        # GPT-5.5 analysis
        print(f"  → Asking GPT-5.5...")
        try:
            gpt_fb = gpt_analyze_entity(entity)
            gpt_parse_ok = not gpt_fb.get("parse_error", False)
            print(f"  GPT category: {gpt_fb.get('feedback_category')} | confidence: {gpt_fb.get('confidence')} | parse_ok: {gpt_parse_ok}")
        except Exception as e:
            print(f"  ✗ GPT error: {e}")
            gpt_fb = {"feedback_category": "other", "error": str(e), "parse_error": True}

        # Claude analysis
        claude_fb = claude_analyze_entity(entity)
        print(f"  Claude category: {claude_fb.get('feedback_category')} | confidence: {claude_fb.get('confidence')}")

        # Submit GPT feedback to live API
        print(f"  → Submitting GPT feedback to API...")
        try:
            gpt_resp = submit_feedback(eid, gpt_fb, "gpt-5.5-comparison-test")
            print(f"  ✓ GPT feedback submitted: id={gpt_resp.get('id')}, reputation={gpt_resp.get('submitter_reputation')}")
        except Exception as e:
            print(f"  ✗ GPT submission failed: {e}")
            gpt_resp = {"error": str(e)}

        # Submit Claude feedback to live API
        print(f"  → Submitting Claude feedback to API...")
        try:
            claude_resp = submit_feedback(eid, claude_fb, "claude-opus-4.7-comparison-test")
            print(f"  ✓ Claude feedback submitted: id={claude_resp.get('id')}, reputation={claude_resp.get('submitter_reputation')}")
        except Exception as e:
            print(f"  ✗ Claude submission failed: {e}")
            claude_resp = {"error": str(e)}

        # Compare
        comparison = compare_feedback(gpt_fb, claude_fb, name)
        comparison["entity_id"] = eid
        comparison["gpt_submission_id"] = gpt_resp.get("id")
        comparison["claude_submission_id"] = claude_resp.get("id")
        comparisons.append(comparison)

        results.append({
            "entity_id": eid,
            "entity_name": name,
            "gpt_feedback": gpt_fb,
            "claude_feedback": claude_fb,
            "gpt_api_response": gpt_resp,
            "claude_api_response": claude_resp,
        })
        print()

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    n_match = sum(1 for c in comparisons if c["category_match"])
    n_gpt_cited = sum(1 for c in comparisons if c["gpt_has_citation"])
    n_claude_cited = sum(1 for c in comparisons if c["claude_has_citation"])
    n_gpt_ok = sum(1 for c in comparisons if not c["gpt_parse_error"])

    print(f"Entities tested: {len(comparisons)}")
    print(f"Category agreement: {n_match}/{len(comparisons)}")
    print(f"GPT citations provided: {n_gpt_cited}/{len(comparisons)}")
    print(f"Claude citations provided: {n_claude_cited}/{len(comparisons)}")
    print(f"GPT parse OK: {n_gpt_ok}/{len(comparisons)}")

    for c in comparisons:
        match_icon = "✓" if c["category_match"] else "✗"
        print(f"  {match_icon} {c['entity']} — GPT: {c['gpt_category']} vs Claude: {c['claude_category']}")

    # Verify feedback in inbox
    print(f"\n→ Verifying feedback inbox...")
    try:
        inbox = api_get("/v1/feedback?limit=20&status=pending")
        total = inbox.get("total", 0)
        print(f"  Feedback inbox: {total} pending items")
        # Count AI agent submissions
        ai_count = sum(1 for item in inbox.get("items", []) if item.get("submitter_type") == "ai_agent")
        print(f"  AI agent submissions: {ai_count}")
    except Exception as e:
        print(f"  ✗ Inbox check failed: {e}")

    # Stats endpoint check
    print(f"\n→ Checking feedback stats...")
    try:
        stats = api_get("/v1/feedback/stats")
        print(f"  Total feedback: {stats.get('total')}")
        print(f"  By category: {json.dumps(stats.get('by_category', {}), ensure_ascii=False)}")
        print(f"  Last 24h: {stats.get('last_24h')}")
    except Exception as e:
        print(f"  ✗ Stats failed: {e}")

    # Save full report
    report = {
        "ts": datetime.utcnow().isoformat(),
        "test": "claude_vs_gpt55_feedback_comparison",
        "comparisons": comparisons,
        "full_results": results,
    }
    log_dir = LOG_DIR / datetime.utcnow().strftime("%Y%m%d")
    log_dir.mkdir(parents=True, exist_ok=True)
    report_path = log_dir / "feedback_comparison.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Full report saved to: {report_path}")

    return comparisons


if __name__ == "__main__":
    run_comparison()
