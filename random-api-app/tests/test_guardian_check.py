"""Prove this repo is a valid Guardian fixture, on temp copies.

This does NOT test Guardian itself. It tests that this repo, as shipped,
contains exactly one breaking usage, and that the proposed migration
removes it. Temp copies use known OLD code, so the suite passes even
after the user migrates their real working copy.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "scripts" / "check_api_drift.py"
MIGRATOR = ROOT / "scripts" / "apply_migration.py"

OLD_CHECKOUT = '''"""Checkout code — INTENTIONALLY written against the OLD (v1) payment API."""

from fictional_payments import Client

client = Client(api_key="demo-key")


def checkout(amount_dollars: float, currency: str = "USD"):
    # This old API is the v1 API from docs/API_CHANGELOG-v2.md.
    # In v2 it is removed; use create_payment(amount_minor_units, currency_code).
    return client.create_charge(amount=amount_dollars, currency=currency)
'''


def _copy_src_to(tmp_path: Path) -> Path:
    dest = tmp_path / "demo"
    (dest / "src").mkdir(parents=True)
    (dest / "docs").mkdir()
    shutil.copytree(ROOT / "src", dest / "src", dirs_exist_ok=True)
    shutil.copy(ROOT / "docs" / "API_CHANGELOG-v2.md", dest / "docs" / "API_CHANGELOG-v2.md")
    (dest / "src" / "checkout.py").write_text(OLD_CHECKOUT)
    return dest


def test_checker_flags_shipped_code(tmp_path):
    dest = _copy_src_to(tmp_path)
    proc = subprocess.run([sys.executable, str(CHECKER), "--root", str(dest)], capture_output=True, text=True)
    assert proc.returncode == 1, proc.stdout
    assert "create_charge" in proc.stdout and "src/checkout.py" in proc.stdout


def test_checker_passes_after_migration(tmp_path):
    dest = _copy_src_to(tmp_path)
    migrated = subprocess.run(
        [sys.executable, str(MIGRATOR), "--target", str(dest / "src" / "checkout.py")],
        capture_output=True, text=True,
    )
    assert migrated.returncode == 0, migrated.stdout + migrated.stderr
    proc = subprocess.run([sys.executable, str(CHECKER), "--root", str(dest)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout
    assert "No breaking API usages found." in proc.stdout


def test_unaffected_usages_are_not_flagged(tmp_path):
    dest = _copy_src_to(tmp_path)
    subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(dest), "--json", str(tmp_path / "report.json")],
        capture_output=True, text=True,
    )
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["breaking_count"] == 1
    assert all("create_charge" in f["evidence"] for f in report["breaking_findings"])
    assert len(report["other_api_usages"]) >= 4  # requests x3 + httpx x1
