import re
from pathlib import Path

base = Path("labs/binary/nexawallet")
FLAG_RE = re.compile(r"duck\{[a-z0-9_]{16,40}\}")

# 1) Redact plaintext flags outside app/
for rel in ("docs/official-solution.mdx", "docs/validation-report.mdx"):
    p = base / rel
    text = p.read_text()
    new_text, count = FLAG_RE.subn("duck{...}", text)
    if count:
        p.write_text(new_text)
        print(f"{rel}: redacted {count} occurrence(s)")
    else:
        print(f"{rel}: no occurrences found")

# 2) README.md: add Brief/Setup/Goal
readme = base / "README.md"
text = readme.read_text()
marker = "## What this is"
if "## Brief" not in text and marker in text:
    insert = (
        "## Brief\n\n"
        "A custom-built Android crackme (NexaWallet) that simulates a digital wallet "
        "with a maximum transfer limit. Defeat an anti-instrumentation layer and a "
        "hidden, non-exported Activity, entirely in-process with Frida, to approve a "
        "transfer above the limit and mint the flag.\n\n"
        "## Setup\n\n"
        "```bash\n"
        "adb install bin/NexaWallet-debug.apk\n"
        "```\n\n"
        "Requires an Android emulator/device, adb, and a Frida stack (see "
        "docs/operations.mdx for the tested version matrix). No server-side "
        "component — this is a BYOD artifact lab.\n\n"
        "## Goal\n\n"
        "Approve and confirm a transfer above the wallet's limit using dynamic "
        "instrumentation, then recover the minted flag. Verify with:\n\n"
        "```bash\n"
        "python3 check.py \"duck{...}\"\n"
        "```\n\n"
    )
    readme.write_text(text.replace(marker, insert + marker))
    print("README.md: Brief/Setup/Goal added")
else:
    print("README.md: already has Brief, or marker missing — check manually")
