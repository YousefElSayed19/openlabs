# OpenLabs CLI and JSON contract v1

Specification for a future `openlabs` player and maintainer CLI. M1-07 defines
the interface only; repository scripts remain the reference implementation.
Conformance is enforced by `python3 scripts/test_contract.py` in CI (M1-08).

Human decisions live in `wiki/M1-Contract-Decisions.md`. Golden JSON examples
live under `scripts/fixtures/cli_contract/`.

## Global conventions

### Invocation shape

```text
openlabs [--json] [--dry-run] <command> [arguments]
```

| Flag | Behavior |
|:---|:---|
| `--json` | Print one `openlabs.command.v1` envelope on stdout. Human text goes to stderr. |
| `--dry-run` | Resolve targets and print planned work. Must not mutate Docker state, lab files, or git. |

### Exit codes

| Code | Meaning |
|:---:|:---|
| `0` | Success (`ok: true` in JSON mode). |
| `1` | Command failed; blocking errors present. |
| `2` | Usage error (unknown command, missing lab path, invalid action). |
| `3` | Environment not ready (Docker daemon missing, repo layout invalid). |

JSON mode must still print an envelope when exit code is non-zero.

### Response envelope (`openlabs.command.v1`)

Every `--json` run emits a single JSON object:

| Field | Type | Required | Rules |
|:---|:---|:---:|:---|
| `version` | string | yes | Must be `openlabs.command.v1`. |
| `command` | string | yes | Top-level command name. |
| `ok` | boolean | yes | Mirrors exit code `0` vs non-zero. |
| `exit_code` | integer | yes | Same value as process exit code. |
| `dry_run` | boolean | yes | Reflects `--dry-run`. |
| `data` | object | yes | Command-specific payload; may be `{}`. |
| `diagnostics` | array | yes | Registry-backed findings; empty on full success. |
| `meta` | object | no | `duration_ms`, `redacted`, `reset_safe`. |

Each diagnostic item:

| Field | Type | Required |
|:---|:---|:---:|
| `id` | string | yes | `OL-####` from `contracts/diagnostics.json`. |
| `key` | string | yes | Symbolic registry key. |
| `message` | string | yes | Redacted human text. |

### Redaction

CLI output must apply the same redaction rules as `scripts/diagnostic_registry.py`
before writing diagnostics or bundled artifacts: no plaintext flags, no raw
64-char hashes in messages unless explicitly marked `<hash>`, no bearer tokens,
no home-directory paths.

Set `meta.redacted: true` when any diagnostic or bundled field was redacted.

### Reset safety

Commands that stop or remove lab runtime state (`lab reset`, `lab prove` teardown
steps) must:

- Scope Docker changes to a dedicated compose project name per lab run.
- Never delete the lab directory, git metadata, or player notes outside the lab tree.
- Set `meta.reset_safe: true` when a reset completes without touching out-of-scope paths.

## Commands

### `setup`

Prepare the local machine to run labs.

| Action | Default | Purpose |
|:---|:---|:---|
| `run` | yes | Check Docker/Compose, verify repo root, print next steps. |

`data` may include `checks` (tool versions) and `missing` (blocking prerequisites).

### `doctor`

Run repository health checks without starting lab containers.

| Action | Default | Purpose |
|:---|:---|:---|
| `run` | yes | Aggregate validate, catalog drift, and triage signals. |

Maps to maintainer scripts conceptually: `validate.py`, `sync_catalog_public.py --check`,
`lab_triage_inventory.py --check`.

### `issue`

Build a **local diagnostic bundle** for maintainers. M1 does not assign GitHub
issues or call the GitHub API.

| Action | Default | Purpose |
|:---|:---|:---|
| `bundle` | yes | Collect redacted diagnostics, versions, and target lab path into `data.bundle`. |

`data.bundle` fields:

| Field | Purpose |
|:---|:---|
| `generated_at` | ISO-8601 UTC timestamp. |
| `repo_root` | Redacted absolute path or `<path>`. |
| `lab` | Optional lab relative path. |
| `diagnostics` | Array of registry diagnostics. |
| `notes` | Free text; must be redacted. |

### `lab`

Lab-scoped player and maintainer actions.

```text
openlabs [--json] [--dry-run] lab <action> [--level Ln] [path/to/lab]
```

| Action | Maps to | Notes |
|:---|:---|:---|
| `validate` | `scripts/validate.py` on one lab | Metadata and structure. |
| `score` | `scripts/score_lab.py` | Quality score only. |
| `check` | `scripts/check.py` | Flag check; never echo input flag. |
| `compose` | `docker compose config` | L1 compose render. |
| `prove` | `scripts/prove_reference_lab.py` | Supported reference lifecycle. |
| `reset` | Compose down for namespaced project | Must satisfy reset safety rules. |

#### L0–L6 lifecycle mapping (`lab prove`)

Aligned with `scripts/prove_reference_lab.py` and CI **Prove duck-cross L0-L6**:

| Level | Meaning |
|:---|:---|
| `L0` | Required files and catalog metadata valid. |
| `L1` | Compose renders; player port present. |
| `L2` | Image build succeeds. |
| `L3` | Service ready at documented URL. |
| `L4` | Player entry page and public API smoke checks. |
| `L5` | Intended solve path; checker accepts flag without leaking it. |
| `L6` | Teardown removes namespaced resources. |

`lab prove --json` sets `data.levels` to an ordered list of `{level, ok, seconds, detail}`.
Partial runs may pass `--level L3` to stop after that level.

## Fixture validation

```bash
python3 scripts/test_cli_contract_fixtures.py
python3 scripts/test_diagnostic_registry.py
```
