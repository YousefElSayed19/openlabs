#!/usr/bin/env python3
"""Validate contracts/diagnostics.json and registry wiring."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from diagnostic_registry import (  # noqa: E402
    REGISTRY_PATH,
    load_registry,
    load_registry_document,
    parse_registry,
    redact_sensitive,
    validate_registry,
    validate_registry_references,
)
from openlabs_contract import CONTRACT_DIAGNOSTIC_KEYS  # noqa: E402


def run_document_shape() -> int:
    data = load_registry_document()
    if data.get("contract_version") != 1:
        print("contract_version must be 1")
        return 1
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        print("entries must be a non-empty array")
        return 1
    print(f"document shape: ok ({len(entries)} entries)")
    return 0


def run_registry_integrity() -> int:
    registry = load_registry()
    errors = validate_registry(registry)
    if errors:
        print("registry integrity:")
        for line in errors:
            print(f"  {line}")
        return 1
    print("registry integrity: ok")
    return 0


def run_reference_parity() -> int:
    registry = load_registry()
    errors = validate_registry_references(CONTRACT_DIAGNOSTIC_KEYS, registry)
    if errors:
        print("registry references:")
        for line in errors:
            print(f"  {line}")
        return 1
    print("registry references: ok")
    return 0


def run_redaction() -> int:
    cases = (
        ("duck{abcdefghijklmnopqrst}", "<redacted-flag>"),
        ("a" * 64, "<hash>"),
        ("Bearer super-secret-token", "<redacted-token>"),
        ("api_key=not-for-logs", "<redacted-secret>"),
        ("under /home/player/labs/web/foo", "<path>"),
    )
    failures = 0
    for raw, needle in cases:
        redacted = redact_sensitive(raw)
        if needle not in redacted:
            failures += 1
            print(f"redaction failed for {raw!r}: {redacted!r}")
    if failures:
        print(f"redaction: failed {failures}")
        return 1
    print("redaction: ok")
    return 0


def run_duplicate_fixture() -> int:
    """Guard against accidental duplicate ids or keys in the JSON file."""
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    ids = [entry["id"] for entry in data["entries"]]
    keys = [entry["key"] for entry in data["entries"]]
    if len(ids) != len(set(ids)) or len(keys) != len(set(keys)):
        print("duplicate id or key in diagnostics.json")
        return 1
    parsed = parse_registry(data)
    if validate_registry(parsed):
        print("parse_registry produced invalid registry")
        return 1
    print("duplicate fixture: ok")
    return 0


def main() -> int:
    for step in (
        run_document_shape,
        run_registry_integrity,
        run_reference_parity,
        run_redaction,
        run_duplicate_fixture,
    ):
        code = step()
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    sys.exit(main())
