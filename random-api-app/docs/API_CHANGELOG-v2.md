# Fictional Payments API — Changelog (latest documentation)

This file is the "latest documentation" that API Guardian must compare
the repo against.

## Version 2.0

- BREAKING: The `create_charge(amount, currency)` method has been removed.
- Use `create_payment(amount_minor_units, currency_code)` instead.
- `amount_minor_units` must be an integer amount in the smallest currency unit.
  For USD, convert dollars to cents: `amount_minor_units = int(round(amount_dollars * 100))`.
- The new method returns a Payment object instead of a Charge object.
  The response field `amount` is replaced by `amount_minor_units`, and
  `currency` is replaced by `currency_code`.

## What did NOT change in v2

- The JSONPlaceholder posts API is unchanged.
- The GitHub REST API is unchanged.
- The Dog CEO API is unchanged.
- The Open Library API is unchanged.
- Plain helper functions that call no external API are unchanged.

So a correct Guardian report flags exactly one breaking usage
(`create_charge` in `src/checkout.py`) and leaves the other API calls alone.
