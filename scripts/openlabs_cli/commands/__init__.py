"""Command handlers (stubs until later M2 issues)."""

from __future__ import annotations

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


def handle_issue(ctx: CliContext, args: list[str]) -> CliResult:
    _ = ctx
    if not args:
        raise UsageError("issue requires explain OL-#### or bundle")
    action = args[0]
    if action not in {"explain", "bundle"}:
        raise UsageError(f"unknown issue action {action!r}")
    return CliResult.not_implemented("issue", f"openlabs issue {action}")


def handle_lab(ctx: CliContext, args: list[str]) -> CliResult:
    _ = ctx
    if not args:
        raise UsageError("lab requires an action")
    action = args[0]
    result = CliResult.not_implemented("lab", f"openlabs lab {action}")
    result.data["action"] = action
    return result
