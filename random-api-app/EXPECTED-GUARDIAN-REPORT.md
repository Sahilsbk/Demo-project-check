# Expected API Guardian report for this project

Use this as the answer key when you test Guardian.

## Before migration (the shipped state)

| File | Usage found | Breaking? | Suggested fix |
|---|---|---|---|
| `src/checkout.py` | `client.create_charge(amount=amount_dollars, currency=currency)` | **Yes — removed in v2** | `client.create_payment(amount_minor_units=int(round(amount_dollars * 100)), currency_code=currency)` |
| `src/clients.py` | `requests.get("https://jsonplaceholder.typicode.com/posts/...")` | No | None |
| `src/clients.py` | `httpx.get("https://api.github.com/repos/...")` | No | None |
| `src/clients.py` | `requests.get("https://dog.ceo/api/breeds/image/random")` | No | None |
| `src/clients.py` | `requests.get("https://openlibrary.org/search.json")` | No | None |
| `src/clients.py` | `greet(name)` | No | None — no API call at all |

Expected counts: **1 breaking finding, 5 unaffected usages, 0 false positives.**

A fix that only renames `create_charge` to `create_payment` without the
`* 100` conversion is **wrong**: `$19.99` would become 20 minor units
(20 cents) instead of 1999 cents. See `migrations/001-payments-v2.patch`.

## After migration (run `python scripts/apply_migration.py`)

- `python scripts/check_api_drift.py` → exit 0, "No breaking API usages found."
- Guardian re-scan → 0 breaking findings
- `python -m pytest -q` → pass, under v1 and under `PAYMENTS_API_VERSION=2`
- `python main.py --checkout 19.99` under v2 → Payment, 1999 minor units
