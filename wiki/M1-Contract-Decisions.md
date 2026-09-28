# M1 contract decisions (draft)

Decision record for milestone **M1 - OpenLabs contract**. It inventories current
`lab.yml` consumers, records observed parser behavior, and proposes the v1
contract boundary. Senior maintainer approval is required before **M1-02** or
**M1-03** merge.

- **Issue:** [#104 M1-01](https://github.com/duckurity/openlabs/issues/104)
- **Baseline reviewed:** `main` at `88a61f9dc6be6f3f8ceb1883eb9bb5b46b8a7a42`
- **Catalog at baseline:** 20 catalogued labs (1 `supported`, 19 `experimental`), 5 uncatalogued directories
- **Record status:** draft awaiting maintainer sign-off (see [Approval](#approval))


## Metadata consumers

Every row is a repository entry point that reads, validates, generates from, or
documents `lab.yml`. Paths are relative to the repository root.

| Consumer | Path | Parser / read path | Fields and rules used |
|:---|:---|:---|:---|
| Structure and metadata validation | `scripts/validate.py` | `parse_flat_yaml` | `name`, `track`, `difficulty`, `description`, `flag_hash` (required keys); `status` (required, two values); optional `techniques` (bracket list, slug + `content/technique/` existence); flag plaintext scan on `lab.yml` and `README.md` |
| Player flag checker | `scripts/check.py` | Line scan with strict regex | `flag_hash`, optional `checkpoint_flag_hash` only; rejects quotes, comments on hash lines, duplicates, malformed lines |
| Lab inventory and JSON reports | `scripts/lab_inventory.py` | `validate.parse_flat_yaml` | `name`, `status` (via `lab_status`) |
| Status-aware validate CLI | `scripts/validate.py` + `lab_inventory.py` | same as validate | Full `check_lab`; experimental vs supported exit policy |
| Public catalog model | `scripts/catalog_public.py` | `validate.parse_flat_yaml` | `name`, `track`, `difficulty`, `description`, `status` |
| Catalog sync (README, wiki tables) | `scripts/sync_catalog_public.py` | via `catalog_public` | Same public fields; counts by status |
| Site MDX generation | `scripts/sync_site_content.py` | `parse_lab_yml` (separate) | All keys in file; uses `name`, `track`, `difficulty`, `description`, `status`, `techniques`; `port` from README or compose unless `port` key present; git-derived author fields; calls `validate.check_lab`, `score_lab` |
| Lab author metadata test | `scripts/test_lab_author_metadata.py` | `sync_site_content.parse_lab_yml` | Generated MDX vs fixture registry |
| Lab scoring | `scripts/score_lab.py` | `validate.parse_flat_yaml` | `techniques` (optional, for docs notes); structural checks use files, not extra keys |
| Triage inventory | `scripts/lab_triage_inventory.py` | `validate.parse_flat_yaml` | `name`, `status`; structural blockers |
| Reference lab proof (L0-L6) | `scripts/prove_reference_lab.py` | `validate.parse_flat_yaml` + `check_lab` | `status` must be `supported` for duck-cross proof |
| Challenge sheet PDF | `scripts/make_lab_pdf.py` | Local `parse_flat_yaml` (strict) | `name`, `track`, `difficulty`, `description` required for PDF; duplicate keys rejected; lists, quotes, block scalars supported |
| Shape SVG generation | `scripts/make_shapes.py` | Line scan for `flag_hash` | `flag_hash` only |
| Badges / brand pipeline | `scripts/make_badges.py` | Indirect via lab discovery | Uses catalog paths; does not parse `lab.yml` directly |
| Baseline evidence report | `scripts/baseline_report.py` | Inventory and validate outputs | Aggregates validation, not direct parse |
| Next.js lab schema | `source.config.ts` | MDX frontmatter | `track`, `difficulty`, `port`, `status`, author fields, `verified`, score fields (from sync, not raw YAML) |
| Contributor docs | `CONTRIBUTING.md` | Prose | Documents five keys only (missing `status`, `techniques`, hashes beyond `flag_hash`, `port`) |
| Wiki authoring | `wiki/Authoring-a-Lab.md`, `wiki/Lab-Anatomy.md`, `wiki/Lab-Catalog-Status.md`, `wiki/Flag-Format.md`, `wiki/Tracks-and-Difficulty.md` | Prose + examples | Mixed completeness vs validator |
| Agent entry | `AGENTS.md` | Prose | Flag format and high-level lab layout |
| CI workflows | `.github/workflows/labs.yml`, `.github/workflows/site.yml` | Path triggers | Rebuild when `labs/**/lab.yml` changes |
| Lab-local tooling | e.g. `labs/web/firmdrama/scripts/sync_flag_hash.py`, `labs/web/snapconnect/ops/validate.py` | Ad hoc reads | `flag_hash` / `checkpoint_flag_hash` for that lab only |

**Coupling note:** `lab_inventory`, `catalog_public`, `score_lab`, `prove_reference_lab`, and triage import `validate.parse_flat_yaml` or `check_lab`. Site generation and PDF generation use separate parsers today.

---

## Field matrix (catalogued labs)

Keys observed across all 20 catalogued `lab.yml` files and `labs/_template/lab.yml`
at baseline.

| Field | Required today (validate) | In template | Catalog presence (20 labs) | Notes |
|:---|:---|:---|:---|:---|
| `name` | yes | yes | 20/20 | Must match directory; `NAME_RE` |
| `track` | yes | yes | 20/20 | Must match parent directory track |
| `difficulty` | yes | yes | 20/20 | `easy`, `medium`, `hard`, `insane` |
| `description` | yes | yes | 20/20 | Single-line in practice |
| `flag_hash` | yes | yes | 20/20 | 64 lowercase hex |
| `status` | yes | yes | 20/20 | `experimental` or `supported`; exactly one supported (`duck-cross`) |
| `techniques` | no (validated if present) | commented example | 20/20 | Bracket list; slug must match `content/technique/<slug>.mdx` |
| `checkpoint_flag_hash` | no | no | 1/20 (`firmdrama`) | `check.py` strict line format |
| `port` | no | no | 1/20 (`switf01-hit3`) | Site sync usually derives port from README or compose |
| `contract_version` | no | no | 0/20 | **Proposed M1 addition** |

Per-lab optional fields:

| Lab | Extra keys |
|:---|:---|
| `labs/web/firmdrama` | `checkpoint_flag_hash` |
| `labs/web/switf01-hit3` | `port` |

Uncatalogued directories (no `lab.yml` at baseline): `labs/web/duckdesk`,
`labs/web/duckfleet`, `labs/web/duckmarket`, `labs/web/duckcorp-savegame`,
`labs/web/Sayed_Khashana_REST_API_IDOR_CTF`. They stay outside the public catalog
until they ship valid metadata.

---

## Syntax and parser behavior

Observed behavior for ambiguous or edge-case input. Intended v1 behavior is in
the right column where it differs from today.

| Input case | `validate.parse_flat_yaml` | `make_lab_pdf.parse_flat_yaml` | `sync_site_content.parse_lab_yml` | `check.py` | Proposed v1 |
|:---|:---|:---|:---|:---|:---|
| Blank lines | ignored | ignored | kept as keys if line has `:` | hash lines only | ignore |
| `#` comments | ignored | ignored | **not ignored** (can break keys) | N/A for hashes | ignore full-line and inline where defined |
| Duplicate keys | last wins silently | error with line | last wins | error on hash fields | **reject** with line and `OL-####` |
| Unquoted scalars | strip; optional `'\"'` unwrap | strip inline comment; JSON double-quote | strip only | exact `field: hex` | unify strip and quoting rules |
| Colons in values | remainder after first `:` | same | split on first `:` | N/A | allow via quoting or block scalars |
| Bracket lists `[a, b]` | `techniques` only via helper | parsed as scalar | parsed as scalar | N/A | typed list for `techniques` |
| YAML list `- item` | not supported | supported for some keys | not supported | N/A | **one form** in v1 (recommend bracket list to match catalog) |
| `\|` / `>` block scalars | not supported | supported | not supported | N/A | retain only if PDF path keeps them; else document rejection |
| Unknown keys | ignored | stored in dict | stored in dict | ignored | **reject** in strict mode |
| Empty value | fails required key checks | may error on block | empty string | N/A | reject required empties |
| Invalid UTF-8 | read error surfaces in validate | die with message | read error | exit 2 | deterministic encoding error |
| Indented keys | treated as flat key name | error | may parse wrong | N/A | reject indented mapping |

**Deterministic generated outputs:** `content/labs/*.mdx`, `public/llms.txt`,
`public/llms-full.txt`, README catalog tables, wiki catalog pages, badges,
`public/shapes/*.svg`, lab sheet PDFs, and catalog JSON from
`sync_catalog_public.py` must stay byte-stable except when metadata or source
READMEs change.
