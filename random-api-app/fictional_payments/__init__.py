"""A tiny, local payment API with a real v1 -> v2 breaking change.

This package exists so the demo runs without any external account or key,
while still giving API Guardian a genuine old-vs-new API to detect.

Version is selected with the ``PAYMENTS_API_VERSION`` environment variable:

* ``1`` (default): ``create_charge(amount, currency)`` works.
* ``2``: ``create_charge`` is removed and raises ``RemovedApiError``.
  ``create_payment(amount_minor_units, currency_code)`` works in both
  versions, so migrated code keeps working after the upgrade.

The amounts are deliberately different types on purpose, mirroring the
changelog in ``docs/API_CHANGELOG-v2.md``: v1 takes dollars as a float,
v2 takes integer minor units (cents). A blind rename without the
``* 100`` conversion would silently charge 100x too little.
"""

from __future__ import annotations

import os
import uuid


class RemovedApiError(AttributeError):
    """Raised when code calls an API method removed in the active version."""


class Client:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Read at construction time so tests can flip versions per client.
        self.version = os.environ.get("PAYMENTS_API_VERSION", "1")

    def create_charge(self, amount, currency):
        """v1 only. Removed in v2 — see docs/API_CHANGELOG-v2.md."""
        if self.version == "2":
            raise RemovedApiError(
                "create_charge(amount, currency) was removed in API v2. "
                "Use create_payment(amount_minor_units, currency_code) instead."
            )
        return {
            "id": f"ch_{uuid.uuid4().hex[:12]}",
            "type": "Charge",
            "amount": amount,
            "currency": currency,
            "status": "succeeded",
            "api_version": "1",
        }

    def create_payment(self, amount_minor_units, currency_code):
        """v2 replacement. Works in both versions so migrated code is safe."""
        if not isinstance(amount_minor_units, int):
            raise TypeError(
                "amount_minor_units must be an integer amount in the "
                f"smallest currency unit, got {amount_minor_units!r}"
            )
        return {
            "id": f"pay_{uuid.uuid4().hex[:12]}",
            "type": "Payment",
            "amount_minor_units": amount_minor_units,
            "currency_code": currency_code,
            "status": "succeeded",
            "api_version": self.version,
        }
