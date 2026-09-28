# OpenLabs contracts

Machine-readable definitions for the OpenLabs lab metadata contract and related
interfaces. Human decisions live in `wiki/M1-Contract-Decisions.md`.

## Lab metadata v1 (`lab.schema.json`)

JSON Schema 2020-12 describes the **structural** shape of a v1 lab record after
flat `lab.yml` is parsed into JSON types. It does not parse YAML and does not
prove repository layout by itself.

### Structural rules (schema)

| Field | Constraint |
|:---|:---|
| `contract_version` | Integer `1` only in M1 |
| `name` | Lowercase hyphenated slug pattern |
| `track` | One of five track enums |
| `difficulty` | One of four difficulty enums |
| `description` | Non-empty string |
| `flag_hash` | 64 lowercase hex digits |
| `status` | `experimental` or `supported` |
| `techniques` | Array of slug patterns; may be empty |
| `checkpoint_flag_hash` | Optional; same pattern as `flag_hash` |
| `port` | Optional integer 1–65535 |
| Unknown keys | Rejected (`additionalProperties: false`) |

### Repository-context rules (not in JSON Schema)

These stay in `scripts/validate.py` until M1-04 moves them into the shared
contract module:

| Rule | Where enforced today |
|:---|:---|
| `name` equals directory basename | `validate.check_lab` |
| `track` equals parent directory name | `validate.check_lab` |
| Each `techniques` slug has `content/technique/<slug>.mdx` | `validate.check_lab` |
| No plaintext `duck{...}` in `lab.yml` or lab `README.md` | `validate.check_lab` |
| Compose file and README sections present | `validate.check_lab` (structure, not schema) |
| `supported` promotion needs L0-L6 proof | `prove_reference_lab.py`, governance docs |

### YAML authoring surface (M1 v1)

The approved flat subset is documented in `wiki/M1-Contract-Decisions.md`. Parsing
behavior is implemented in M1-03 (`scripts/openlabs_contract.py`). Until M1-06,
on-disk `lab.yml` files may omit `contract_version`; tests can still prove each
catalogued lab **represents** v1 by supplying `contract_version: 1` in the JSON
record used for schema checks.

### Validation command

```bash
python3 scripts/test_contract_schema.py
```
