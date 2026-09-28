#!/usr/bin/env python3
"""Parser and model tests for scripts/openlabs_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from openlabs_contract import (  # noqa: E402
    load_lab_metadata,
    legacy_string_map,
    validate_lab_context,
)
from validate import LABS_DIR, parse_flat_yaml, parse_bracket_list  # noqa: E402

FIXTURES = REPO_ROOT / "scripts" / "fixtures" / "openlabs_contract"

VALID_CASES = (
    "valid/explicit-version",
    "valid/quoted-description",
)

INVALID_CASES = (
    ("invalid/duplicate-key", "contract.parse.duplicate_key"),
    ("invalid/unknown-field", "contract.parse.unknown_field"),
    ("invalid/indented-key", "contract.parse.indented_key"),
)


def run_fixture_cases() -> int:
    failures = 0
    for rel in VALID_CASES:
        path = FIXTURES / rel / "lab.yml"
        result = load_lab_metadata(path)
        if result.record is None:
            failures += 1
            print(f"{rel}: expected valid, got diagnostics:")
            for diag in result.diagnostics:
                print(f"  [{diag.key}] {diag.format()}")
    for rel, want_key in INVALID_CASES:
        path = FIXTURES / rel / "lab.yml"
        result = load_lab_metadata(path)
        if result.record is not None:
            failures += 1
            print(f"{rel}: expected invalid")
            continue
        keys = {diag.key for diag in result.diagnostics}
        if want_key not in keys:
            failures += 1
            print(f"{rel}: expected key {want_key}, got {sorted(keys)}")
    if failures:
        print(f"fixtures: failed {failures}")
        return 1
    print(f"fixtures: passed {len(VALID_CASES) + len(INVALID_CASES)} cases")
    return 0


def compare_legacy_fields(record_map: dict[str, str], legacy: dict[str, str]) -> list[str]:
    mismatches: list[str] = []
    keys = ("name", "track", "difficulty", "description", "flag_hash", "status")
    for key in keys:
        if record_map.get(key) != legacy.get(key):
            mismatches.append(f"{key}: {record_map.get(key)!r} != {legacy.get(key)!r}")
    legacy_techniques = parse_bracket_list(legacy.get("techniques", ""))
    record_techniques = parse_bracket_list(record_map.get("techniques", "[]"))
    if legacy_techniques != record_techniques:
        mismatches.append(f"techniques: {record_techniques!r} != {legacy_techniques!r}")
    for optional in ("checkpoint_flag_hash", "port"):
        if legacy.get(optional, "").strip() != record_map.get(optional, "").strip():
            if legacy.get(optional) or record_map.get(optional):
                mismatches.append(f"{optional}: {record_map.get(optional)!r} != {legacy.get(optional)!r}")
    return mismatches


def run_catalog_compatibility() -> int:
    failures = 0
    labs: list[Path] = []
    for track in sorted(LABS_DIR.iterdir()):
        if not track.is_dir() or track.name.startswith((".", "_")):
            continue
        for lab in sorted(track.iterdir()):
            if lab.is_dir() and (lab / "lab.yml").is_file():
                labs.append(lab)
    for lab in labs:
        yml = lab / "lab.yml"
        result = load_lab_metadata(yml)
        if result.record is None:
            failures += 1
            print(f"{lab.relative_to(REPO_ROOT)}: load failed:")
            for diag in result.diagnostics:
                print(f"  [{diag.key}] {diag.format()}")
            continue
        legacy = parse_flat_yaml(yml.read_text(encoding="utf-8"))
        mismatches = compare_legacy_fields(legacy_string_map(result.record), legacy)
        if mismatches:
            failures += 1
            print(f"{lab.relative_to(REPO_ROOT)}:")
            for line in mismatches:
                print(f"  {line}")
            continue
        context = validate_lab_context(result.record, lab)
        if context:
            failures += 1
            print(f"{lab.relative_to(REPO_ROOT)}: context errors:")
            for diag in context:
                print(f"  [{diag.key}] {diag.format()}")
    if failures:
        print(f"catalog compatibility: failed {failures} labs")
        return 1
    print(f"catalog compatibility: passed {len(labs)} labs")
    return 0


def main() -> int:
    for step in (run_fixture_cases, run_catalog_compatibility):
        code = step()
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    sys.exit(main())
