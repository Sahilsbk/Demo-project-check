#!/usr/bin/env python3
"""Apply the v2 payment migration to src/checkout.py.

This is the patch API Guardian *should* propose. It is idempotent.
A backup is saved as src/checkout.py.bak.

Usage:
    python scripts/apply_migration.py [--target PATH]
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

OLD = '''def checkout(amount_dollars: float, currency: str = "USD"):
    # This old API is the v1 API from docs/API_CHANGELOG-v2.md.
    # In v2 it is removed; use create_payment(amount_minor_units, currency_code).
    return client.create_charge(amount=amount_dollars, currency=currency)'''

NEW = '''def checkout(amount_dollars: float, currency: str = "USD"):
    # Migrated to API v2: dollars (float) -> minor units (int cents).
    # A plain rename would charge 100x too little, so convert explicitly.
    amount_minor_units = int(round(amount_dollars * 100))
    return client.create_payment(
        amount_minor_units=amount_minor_units, currency_code=currency
    )'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=None, help="checkout.py to migrate")
    args = parser.parse_args()
    target = Path(args.target) if args.target else Path(__file__).resolve().parent.parent / "src" / "checkout.py"

    text = target.read_text(encoding="utf-8")
    if "create_payment" in text and "create_charge" not in text:
        print(f"{target}: already migrated, nothing to do.")
        return 0
    if OLD not in text:
        print(f"{target}: expected old checkout block not found — refusing to guess.", file=sys.stderr)
        return 2

    backup = target.parent / (target.name + ".bak")
    shutil.copyfile(target, backup)
    target.write_text(text.replace(OLD, NEW), encoding="utf-8")
    print(f"Migrated {target} (backup: {backup})")
    print("Verify with: python scripts/check_api_drift.py  # expect exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
