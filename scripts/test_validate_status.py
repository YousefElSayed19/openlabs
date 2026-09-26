#!/usr/bin/env python3
"""Run lab status validator fixtures from scripts/fixtures/validate_status/."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate import check_lab_status, parse_flat_yaml  # noqa: E402

FIXTURES = REPO_ROOT / "scripts" / "fixtures" / "validate_status"

CASES: tuple[tuple[str, int], ...] = (
    ("valid-supported", 0),
    ("valid-experimental", 0),
    ("missing-status", 1),
    ("invalid-status", 1),
)


def run_case(name: str) -> list[str]:
    lab_yml = FIXTURES / name / "lab.yml"
    if not lab_yml.is_file():
        raise FileNotFoundError(f"missing fixture {lab_yml}")
    meta = parse_flat_yaml(lab_yml.read_text(encoding="utf-8"))
    return check_lab_status(meta)


def main() -> int:
    failures = 0
    for name, want_errors in CASES:
        errors = run_case(name)
        if len(errors) != want_errors:
            failures += 1
            print(f"{name}:")
            print(f"  expected errors={want_errors}")
            print(f"  got errors={len(errors)}")
            for line in errors:
                print(f"    error: {line}")
    if failures:
        print(f"failed {failures} of {len(CASES)} status fixtures")
        return 1
    print(f"passed {len(CASES)} status fixtures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
