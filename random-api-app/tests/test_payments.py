"""Payment API v1/v2 behaviour, on temp files so tests pass before and after migration."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fictional_payments import Client, RemovedApiError

OLD_CHECKOUT = '''from fictional_payments import Client

client = Client(api_key="demo-key")


def checkout(amount_dollars: float, currency: str = "USD"):
    return client.create_charge(amount=amount_dollars, currency=currency)
'''


def test_v1_create_charge_works(monkeypatch):
    monkeypatch.setenv("PAYMENTS_API_VERSION", "1")
    result = Client(api_key="demo-key").create_charge(amount=19.99, currency="USD")
    assert result["type"] == "Charge" and result["amount"] == 19.99


def test_v2_create_charge_is_removed(monkeypatch):
    monkeypatch.setenv("PAYMENTS_API_VERSION", "2")
    with pytest.raises(RemovedApiError, match="create_payment"):
        Client(api_key="demo-key").create_charge(amount=19.99, currency="USD")


def test_v2_create_payment_requires_integer_minor_units(monkeypatch):
    monkeypatch.setenv("PAYMENTS_API_VERSION", "2")
    client = Client(api_key="demo-key")
    result = client.create_payment(amount_minor_units=1999, currency_code="USD")
    assert result["type"] == "Payment" and result["amount_minor_units"] == 1999
    with pytest.raises(TypeError):
        client.create_payment(amount_minor_units=19.99, currency_code="USD")


def test_old_checkout_breaks_under_v2_and_migrated_does_not(monkeypatch, tmp_path):
    import importlib.util

    monkeypatch.setenv("PAYMENTS_API_VERSION", "2")
    old_path = tmp_path / "old_checkout.py"
    old_path.write_text(OLD_CHECKOUT)
    spec = importlib.util.spec_from_file_location("old_checkout", old_path)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    with pytest.raises(RemovedApiError):
        old.checkout(19.99)

    migrated = tmp_path / "checkout.py"
    migrated.write_text(
        OLD_CHECKOUT.replace(
            "return client.create_charge(amount=amount_dollars, currency=currency)",
            "return client.create_payment(amount_minor_units=int(round(amount_dollars * 100)), currency_code=currency)",
        )
    )
    spec2 = importlib.util.spec_from_file_location("migrated_checkout", migrated)
    new = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(new)
    result = new.checkout(19.99)
    assert result["type"] == "Payment" and result["amount_minor_units"] == 1999
