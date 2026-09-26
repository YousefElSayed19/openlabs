## Purpose

The public lab catalog is not the same as every directory under `labs/`.
A directory becomes catalogued when it ships a valid `lab.yml`. Everything
else is repository content awaiting a maintainer decision.

## Status field

Catalogued labs carry a `status` key in `lab.yml`. Only two values are
allowed:

| Status | Meaning |
|:---:|:---|
| `experimental` | Metadata-valid and runnable, but not yet promoted with full L0–L6 evidence |
| `supported` | Promoted lab with restored evidence on file |

Do not infer status from directory presence, README wording, site copy, or
`score_lab.py` output alone.

## Migration

Missing `status` is a validation error. Set `experimental` or `supported`
explicitly in every catalogued lab.

## Uncatalogued directories

A track subdirectory without `lab.yml` is uncatalogued. It is excluded from
the public catalog and reported separately from validation failures on
registered labs.

## Promotion

Move `experimental` to `supported` only after L0–L6 evidence is recorded
(structure, secrets hygiene, compose, player brief, solve path, maintainer
sign-off). Update `status: supported` in the same pull request that adds or
refreshes the evidence.

## Demotion

When a supported lab regresses (CI failure, broken compose, score drop below
the gate, or lost evidence), set `status: experimental` until the evidence is
restored. Do not leave `supported` on a lab that no longer passes the
baseline checks.

Promotion and demotion rules stay in this page. **`duck-cross`** is the
reference supported lab; CI proves L0–L6 with
`python3 scripts/prove_reference_lab.py`.

## Local checks

```bash
python3 scripts/test_validate_status.py
python3 scripts/validate.py
```

The fixture runner covers valid, missing, and invalid `status` values.
`python3 scripts/validate.py` prints catalog counts and lists uncatalogued
directories separately.
