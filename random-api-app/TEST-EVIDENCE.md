# Test evidence — verified before delivery

Date: 2026-10-24. Python 3.12, fresh venv, `pip install -r requirements.txt`.
No FastAPI, no uvicorn, no server anywhere in the code
(the words "no FastAPI" appear only in README/main docstrings).

## Shipped state (before migration)

- `python -m pytest -q` → **12 passed**
- `python scripts/check_api_drift.py` → exit **1**, 1 breaking finding:
  `src/checkout.py:16: return client.create_charge(amount=amount_dollars, currency=currency)`
- Live CLI `python main.py --checkout 19.99` → real data, no mocks:
  - Post of the day from JSONPlaceholder
  - GitHub repo `python/cpython` (77760 stars at test time)
  - Random dog image URL from Dog CEO
  - Book pick from Open Library
  - Checkout: Charge, amount 19.99 USD

## After migration (`python scripts/apply_migration.py`)

- `python scripts/check_api_drift.py` → exit **0**, "No breaking API usages found."
- `python -m pytest -q` → **12 passed**
- `PAYMENTS_API_VERSION=2 python -m pytest -q` → **12 passed**
- Live CLI under `PAYMENTS_API_VERSION=2` with `--checkout 19.99` →
  Payment, `amount_minor_units: 1999`, `currency_code: USD`

The working copy was then restored to the shipped (old) state, so
Guardian still has a finding to detect on first run.
Re-verify after restoring: drift check exit 1 again, pytest 12 passed.
