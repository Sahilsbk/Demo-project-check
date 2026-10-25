"""Checkout — INTENTIONALLY written against the OLD (v1) payment API.

This is the file API Guardian should flag. Do not "fix" it by hand
before running Guardian, or there will be nothing left to find.
Use scripts/apply_migration.py after Guardian has reported it.
"""

from fictional_payments import Client

client = Client(api_key="demo-key")


def checkout(amount_dollars: float, currency: str = "USD"):
    # This old API is the v1 API from docs/API_CHANGELOG-v2.md.
    # In v2 it is removed; use create_payment(amount_minor_units, currency_code).
    return client.create_charge(amount=amount_dollars, currency=currency)
