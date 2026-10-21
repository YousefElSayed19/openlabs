# Technique pages (staged for openlabs)

These 4 files are drafts of the technique pages proposed in `lab.yml` for
`dual-check`'s intake checklist (sub-issue #162). They follow the real
`content/technique/<slug>.mdx` frontmatter schema and body structure used
elsewhere in the `duckurity/openlabs` catalog (same convention confirmed
earlier for VaultCorp's technique pages, against `idor.mdx`, `ssti.mdx`,
and `mass-assignment.mdx`).

Staged here only — not yet moved into `duckurity/openlabs` — per the
standing rule: nothing gets pushed to that repo until all 3 sub-issues
are agreed with the maintainer. Once agreed, each file's final home is:

```
content/technique/static-binary-analysis-ghidra.mdx
content/technique/client-side-obfuscation-xor-base64-masking.mdx
content/technique/chained-byte-transform-reversing.mdx
content/technique/aes-key-derivation-from-split-secrets.mdx
```

`lab.yml`'s `techniques:` field should be uncommented to list these 4
slugs once the files land in `content/technique/` in openlabs.
