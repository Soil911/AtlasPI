"""Smoke test all public API endpoints + static pages on live production.

Purpose: after any deploy, verify every listed endpoint returns a sensible
response shape (not just 200) so that regressions like the USA/France label
bug are caught quickly.

Usage:
    python -m scripts.smoke_test_endpoints
    python -m scripts.smoke_test_endpoints --base=https://atlaspi.cra-srl.com
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from dataclasses import dataclass, field

# Windows stdout UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DEFAULT_BASE = "https://atlaspi.cra-srl.com"


@dataclass
class Check:
    path: str
    expected_status: int = 200
    expected_content_type: str | None = None
    required_keys: list[str] = field(default_factory=list)
    description: str = ""


# Representative checks covering main endpoint categories
CHECKS: list[Check] = [
    # Discovery endpoints
    Check("/v1/entities?limit=5", required_keys=["entities"], description="entity list"),
    Check("/v1/entities/1", required_keys=["id", "name_original"], description="entity detail"),
    Check("/v1/events?limit=5", required_keys=["events"], description="event list"),
    Check("/v1/events/1", required_keys=["id", "name_original", "year"], description="event detail"),
    Check("/v1/periods?limit=5", required_keys=["periods"], description="period list"),
    Check("/v1/periods/1", required_keys=["id", "name", "slug"], description="period detail"),
    Check("/v1/periods/by-slug/bronze-age", required_keys=["slug", "description"]),
    Check("/v1/cities?limit=5", required_keys=["cities"]),
    Check("/v1/routes?limit=5", required_keys=["routes"]),
    Check("/v1/chains?limit=5", required_keys=["chains"]),
    # Temporal
    Check("/v1/snapshot/year/1500", required_keys=["year", "periods", "entities"]),
    Check("/v1/snapshot/year/-500", required_keys=["year", "periods"], description="BCE year"),
    Check("/v1/periods/at-year/1250", required_keys=["year", "total", "periods"]),
    Check("/v1/events/on-this-day/07-14", required_keys=["month", "day", "events"]),
    Check("/v1/events/at-date/1789-07-14", required_keys=["date", "events"]),
    Check("/v1/events/date-coverage", required_keys=["unique_dates", "coverage_pct"]),
    # Cross-resource
    Check("/v1/entities/1/periods", required_keys=["entity_id", "periods"]),
    Check("/v1/entities/1/similar", required_keys=["entity_id", "similar"]),
    Check("/v1/entities/1/events", required_keys=["events"]),
    Check("/v1/entities/1/successors", required_keys=["successors"]),
    Check("/v1/entities/1/predecessors", required_keys=["predecessors"]),
    Check("/v1/events/1/periods", required_keys=["event_id", "periods"]),
    # Spatial
    Check("/v1/nearby?lat=41.9&lon=12.5&year=100", required_keys=["entities"]),
    # Search
    Check("/v1/search?q=roma&limit=5", required_keys=["results"]),
    Check("/v1/search/advanced?q=empire&limit=5"),
    Check("/v1/search/fuzzy?q=roma"),
    # Compare
    Check("/v1/compare/1/2", required_keys=["entity_a", "entity_b", "comparison"]),
    # Enums
    Check("/v1/types", description="entity types list"),
    Check("/v1/events/types"),
    Check("/v1/periods/types", required_keys=["types"]),
    Check("/v1/periods/regions", required_keys=["regions"]),
    Check("/v1/chains/types"),
    Check("/v1/routes/types"),
    Check("/v1/cities/types"),
    Check("/v1/continents"),  # returns a list, not an object
    Check("/v1/stats", required_keys=["total_entities"]),
    # Export
    Check("/v1/export/geojson", description="GeoJSON export — large"),
    Check("/v1/export/csv", expected_content_type="text/csv"),
    # Special
    Check("/v1/random", required_keys=["id", "name_original"]),
    # Meta / docs
    Check("/health", required_keys=["status", "version"]),
    Check("/openapi.json", required_keys=["openapi", "paths"]),
    Check("/llms.txt", expected_content_type="text/plain"),
    Check("/robots.txt", expected_content_type="text/plain"),
    Check("/sitemap.xml", expected_content_type="application/xml"),
    Check("/.well-known/ai-plugin.json", expected_content_type="application/json"),
    Check("/.well-known/mcp.json", expected_content_type="application/json"),
    # Static HTML
    Check("/", expected_content_type="text/html"),
    Check("/app", expected_content_type="text/html"),
    Check("/about", expected_content_type="text/html"),
    Check("/faq", expected_content_type="text/html"),
    Check("/docs", expected_content_type="text/html", description="Swagger UI"),
    Check("/redoc", expected_content_type="text/html"),
]


def smoke_test(base: str) -> tuple[int, int, list[str]]:
    """Return (passed, failed, failure_details)."""
    passed = 0
    failed = 0
    failures: list[str] = []

    for check in CHECKS:
        url = base + check.path
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AtlasPI-Smoke-Test/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                status = resp.status
                content_type = resp.headers.get("content-type", "")
                body = resp.read()

                # Status check
                if status != check.expected_status:
                    failed += 1
                    failures.append(f"✗ {check.path}: status {status} != {check.expected_status}")
                    continue

                # Content type check
                if check.expected_content_type:
                    if check.expected_content_type not in content_type:
                        failed += 1
                        failures.append(
                            f"✗ {check.path}: content-type '{content_type}' doesn't contain '{check.expected_content_type}'"
                        )
                        continue

                # JSON payload checks
                if check.required_keys:
                    try:
                        data = json.loads(body)
                        missing = [k for k in check.required_keys if k not in data]
                        if missing:
                            failed += 1
                            failures.append(
                                f"✗ {check.path}: missing keys {missing}"
                            )
                            continue
                    except json.JSONDecodeError:
                        failed += 1
                        failures.append(f"✗ {check.path}: not valid JSON")
                        continue

                passed += 1
                print(f"✓ {check.path}")

        except urllib.error.HTTPError as e:
            failed += 1
            failures.append(f"✗ {check.path}: HTTP {e.code} — {e.reason}")
        except Exception as e:
            failed += 1
            failures.append(f"✗ {check.path}: {type(e).__name__}: {e}")

    return passed, failed, failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=DEFAULT_BASE, help="Base URL")
    args = parser.parse_args()

    print(f"Smoke testing {args.base} — {len(CHECKS)} checks\n")
    passed, failed, failures = smoke_test(args.base)

    print(f"\n{'='*50}")
    print(f"Passed: {passed}/{len(CHECKS)}")
    print(f"Failed: {failed}/{len(CHECKS)}")
    if failures:
        print("\nFailures:")
        for f in failures:
            print(f"  {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
