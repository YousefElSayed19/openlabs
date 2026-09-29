"""Command handlers."""

from __future__ import annotations

from openlabs_cli.commands.issue import handle_issue
from openlabs_cli.commands.lab import handle_lab
from openlabs_cli.context import CliContext
from openlabs_cli.envelope import CliResult
from openlabs_cli.errors import UsageError


def handle_setup(ctx: CliContext, args: list[str]) -> CliResult:
    _ = ctx
    if args and args[0] not in {"run", "help", "--help"}:
        raise UsageError(f"unknown setup action {args[0]!r}")
    return CliResult.not_implemented("setup", "openlabs setup")


def handle_doctor(ctx: CliContext, args: list[str]) -> CliResult:
    _ = ctx
    if args and args[0] == "--fix":
        args = args[1:]
    if args and args[0] not in {"run", "help", "--help"}:
        raise UsageError(f"unknown doctor action {args[0]!r}")
    return CliResult.not_implemented("doctor", "openlabs doctor")


__all__ = [
    "handle_doctor",
    "handle_issue",
    "handle_lab",
    "handle_setup",
]
