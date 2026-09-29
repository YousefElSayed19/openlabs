#!/usr/bin/env python3
"""Load and validate the OpenLabs diagnostic registry (M1-05)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "contracts" / "diagnostics.json"

ID_RE = re.compile(r"^OL-\d{4}$")
KEY_RE = re.compile(r"^contract\.(parse|schema|context)\.[a-z0-9_]+$")

FLAG_PLAINTEXT_RE = re.compile(r"duck\{[a-z0-9_]{16,40}\}")
HEX64_RE = re.compile(r"\b[0-9a-f]{64}\b")
BEARER_RE = re.compile(r"(?i)(bearer\s+)[^\s'\"]+")
TOKEN_PAIR_RE = re.compile(
    r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[^\s'\"]+"
)
HOME_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])(/home/[^\s'\"]+)")


@dataclass(frozen=True)
class RegistryEntry:
    id: str
    key: str
    summary: str


@dataclass(frozen=True)
class DiagnosticRegistry:
    contract_version: int
    id_prefix: str
    entries: tuple[RegistryEntry, ...]

    def by_key(self) -> dict[str, RegistryEntry]:
        return {entry.key: entry for entry in self.entries}


def load_registry_document(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("diagnostics.json root must be an object")
    return data


def parse_registry(data: dict[str, Any]) -> DiagnosticRegistry:
    version = data.get("contract_version")
    prefix = data.get("id_prefix")
    raw_entries = data.get("entries")
    if version != 1:
        raise ValueError("diagnostics.json contract_version must be 1")
    if prefix != "OL":
        raise ValueError("diagnostics.json id_prefix must be OL")
    if not isinstance(raw_entries, list):
        raise ValueError("diagnostics.json entries must be an array")
    entries: list[RegistryEntry] = []
    for index, item in enumerate(raw_entries):
        if not isinstance(item, dict):
            raise ValueError(f"entries[{index}] must be an object")
        entry_id = item.get("id")
        key = item.get("key")
        summary = item.get("summary")
        if not isinstance(entry_id, str) or not isinstance(key, str) or not isinstance(summary, str):
            raise ValueError(f"entries[{index}] requires id, key, and summary strings")
        entries.append(RegistryEntry(id=entry_id, key=key, summary=summary.strip()))
    return DiagnosticRegistry(
        contract_version=version,
        id_prefix=prefix,
        entries=tuple(entries),
    )


def validate_registry(registry: DiagnosticRegistry) -> list[str]:
    errors: list[str] = []
    seen_ids: dict[str, str] = {}
    seen_keys: dict[str, str] = {}
    expected_number = 1
    for entry in registry.entries:
        if not ID_RE.fullmatch(entry.id):
            errors.append(f"invalid id format: {entry.id!r}")
        if not KEY_RE.fullmatch(entry.key):
            errors.append(f"invalid key format: {entry.key!r}")
        if entry.id in seen_ids:
            errors.append(f"duplicate id {entry.id!r}")
        if entry.key in seen_keys:
            errors.append(f"duplicate key {entry.key!r}")
        seen_ids[entry.id] = entry.key
        seen_keys[entry.key] = entry.id
        number_text = entry.id.split("-", 1)[1]
        if number_text.isdigit():
            number = int(number_text)
            if number != expected_number:
                errors.append(
                    f"expected id OL-{expected_number:04d}, got {entry.id!r}"
                )
            expected_number += 1
        if not entry.summary:
            errors.append(f"empty summary for {entry.key}")
    return errors


def validate_registry_references(required_keys: frozenset[str], registry: DiagnosticRegistry) -> list[str]:
    errors: list[str] = []
    by_key = registry.by_key()
    for key in sorted(required_keys):
        if key not in by_key:
            errors.append(f"missing registry entry for emitter key {key!r}")
    for key in by_key:
        if key not in required_keys:
            errors.append(f"registry key {key!r} is not emitted by openlabs_contract")
    return errors


@lru_cache(maxsize=1)
def load_registry() -> DiagnosticRegistry:
    registry = parse_registry(load_registry_document())
    errors = validate_registry(registry)
    if errors:
        raise ValueError("invalid diagnostics.json:\n" + "\n".join(f"  {line}" for line in errors))
    return registry


def lookup_registry_id(key: str) -> str:
    entry = load_registry().by_key().get(key)
    if entry is None:
        raise KeyError(f"unregistered diagnostic key {key!r}")
    return entry.id


def redact_sensitive(text: str) -> str:
    """Redact flags, tokens, secrets, and home paths from diagnostic text."""
    redacted = FLAG_PLAINTEXT_RE.sub("<redacted-flag>", text)
    redacted = HEX64_RE.sub("<hash>", redacted)
    redacted = BEARER_RE.sub(r"\1<redacted-token>", redacted)
    redacted = TOKEN_PAIR_RE.sub(r"\1<redacted-secret>", redacted)
    redacted = HOME_PATH_RE.sub("<path>", redacted)
    return redacted


def prefix_registry_id(message: str, *, registry_id: str) -> str:
    token = f"[{registry_id}]"
    if token in message:
        return message
    return f"{token} {message}"
