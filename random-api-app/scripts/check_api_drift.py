#!/usr/bin/env python3
"""Local Guardian-style drift check (deterministic, no AI, no GitHub).

Scans ``src/`` for the v1 payment call and compares it with the v2
changelog. This mirrors — in miniature — what API Guardian does:
scan repo -> compare with latest docs -> report + suggest a fix.

Usage:
    python scripts/check_api_drift.py [--root PATH] [--json PATH]

Exit code: 1 if a breaking usage is found, 0 if the code is clean.
Only ``src/`` is scanned, on purpose: this script itself mentions
``create_charge`` as a search pattern, and scanning it would be a
false positive.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

OLD_CALL = re.compile(r"\.create_charge\s*\(")
NEW_CALL = re.compile(r"\.create_payment\s*\(")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repo root (default: current directory)")
    parser.add_argument("--json", default=None, help="Write the JSON report to this path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    changelog = root / "docs" / "API_CHANGELOG-v2.md"
    changelog_text = changelog.read_text(encoding="utf-8") if changelog.exists() else ""
    removed_in_docs = "create_charge" in changelog_text and "removed" in changelog_text.lower()

    findings: list[dict] = []
    usages: list[dict] = []

    for path in sorted((root / "src").rglob("*.py")):
        rel = str(path.relative_to(root))
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if OLD_CALL.search(line):
                findings.append(
                    {
                        "file": rel,
                        "line": lineno,
                        "evidence": line.strip(),
                        "severity": "high",
                        "title": "create_charge was removed in API v2",
                        "recommendation": (
                            "Use create_payment(amount_minor_units, currency_code) "
                            "with amount_minor_units = int(round(amount_dollars * 100))."
                        ),
                        "confirmed_in_changelog": removed_in_docs,
                    }
                )
            if NEW_CALL.search(line):
                usages.append({"file": rel, "line": lineno, "usage": "create_payment (v2, OK)"})
            if "requests.get(" in line or "httpx.get(" in line:
                usages.append({"file": rel, "line": lineno, "usage": line.strip()[:120]})

    report = {
        "repo_root": str(root),
        "changelog_checked": str(changelog) if changelog.exists() else None,
        "removed_in_changelog": removed_in_docs,
        "breaking_findings": findings,
        "other_api_usages": usages,
        "breaking_count": len(findings),
    }

    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2), encoding="utf-8")

    if findings:
        print(f"BREAKING: {len(findings)} breaking API usage(s) found:")
        for f in findings:
            print(f"  - {f['file']}:{f['line']}: {f['evidence']}")
            print(f"    Fix: {f['recommendation']}")
            print(f"    Confirmed in changelog: {f['confirmed_in_changelog']}")
        return 1

    print("No breaking API usages found.")
    print(f"Other API usages checked (unaffected): {len(usages)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
