#!/usr/bin/env python3
"""Sanity-check the documented CI routing matrix fixture."""

from __future__ import annotations

import json
import sys
from pathlib import Path

FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "ci_routing_matrix.json"
)
REQUIRED_KEYS = frozenset(
    {
        "run_validate",
        "run_security",
        "run_content",
        "run_pdf",
        "run_reference",
    }
)


def main() -> int:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if data.get("required_check") != "CI required":
        print("required_check must be 'CI required'", file=sys.stderr)
        return 1
    failures = 0
    for case in data.get("examples", []):
        if case.get("labs_workflow_triggers") is False:
            continue
        missing = REQUIRED_KEYS - case.keys()
        if missing:
            failures += 1
            print(f"{case.get('change')}: missing keys {sorted(missing)}")
    if failures:
        print(f"failed {failures} routing examples")
        return 1
    print(f"passed {len(data.get('examples', []))} routing examples")
    return 0


if __name__ == "__main__":
    sys.exit(main())
