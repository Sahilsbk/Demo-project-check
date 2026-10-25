# Random API Project — a test repo for API Guardian

You are right: this is **not** your API Guardian code, and it does **not**
use FastAPI at all. Your zip was only a reference for what Guardian checks.

This is just a random, ordinary Python project that calls several public
APIs. Commit it to GitHub, give that repo link to your API Guardian app,
and Guardian should scan it, compare it with the latest docs, and suggest
changes.

No server, no framework, no API keys. Just run it:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python main.py
python main.py --checkout 19.99
python -m pytest -q
python scripts/check_api_drift.py
```

## What this project does

`main.py` prints a small "daily digest" built from public APIs:

1. A post from JSONPlaceholder
2. A GitHub repo's info
3. A random dog picture URL
4. A book search result from Open Library
5. A demo checkout

## The APIs it uses

| API | How it is called | Key needed? |
|---|---|---|
| JSONPlaceholder (`GET /posts/{id}`) | `requests.get` in `src/clients.py` | No |
| GitHub REST API (`GET /repos/{owner}/{repo}`) | `httpx.get` in `src/clients.py` | No |
| Dog CEO API (`GET /breeds/image/random`) | `requests.get` in `src/clients.py` | No |
| Open Library API (`GET /search.json?q=...`) | `requests.get` in `src/clients.py` | No |
| Fictional Payments API (local, in `fictional_payments/`) | `Client.create_charge(...)` in `src/checkout.py` | No |

The first four are real public APIs and are **not** changed by the v2 docs.
The fifth is the one Guardian is supposed to catch.

## The API mistake Guardian should find

`src/checkout.py` still uses the **old** Payments API v1:

```python
client.create_charge(amount=amount_dollars, currency=currency)
```

`docs/API_CHANGELOG-v2.md` — the "latest documentation" — says that
method was **removed in v2** and replaced by:

```python
client.create_payment(amount_minor_units, currency_code)
```

where `amount_minor_units` is an integer in cents:
`int(round(amount_dollars * 100))`. A plain rename without that
conversion would charge $19.99 as 20 cents.

The expected Guardian report is in `EXPECTED-GUARDIAN-REPORT.md`:
**1 breaking finding** (the payment call), and no breaking findings for
the JSONPlaceholder / GitHub / Dog / Open Library calls.

## How to test Guardian with it

1. Unzip this project, commit the files (not the zip) to a new
   **public** GitHub repo. Your Guardian build clones public repos
   without a login, so a private repo will fail to clone.
2. Give Guardian that repo link.
3. Paste the full text of `docs/API_CHANGELOG-v2.md` into Guardian's
   changelog field. Guardian's scanner reads source files, not `.md`
   files, so the changelog has to be given as text.
4. Check its report against `EXPECTED-GUARDIAN-REPORT.md`.
5. Apply the suggested fix and re-scan. Locally, that step is:
   ```bash
   python scripts/apply_migration.py
   python scripts/check_api_drift.py   # expect: no breaking usages
   python -m pytest -q                 # expect: pass, under v1 and v2
   cp src/checkout.py.bak src/checkout.py   # restore the old code
   ```

## Why the payment API is local

A real payment API would need an account and a secret key, which would
make this test repo unusable for anyone else. So `fictional_payments/`
implements the same v1 → v2 breaking change locally, version-gated by
the `PAYMENTS_API_VERSION` environment variable:

- `PAYMENTS_API_VERSION=1` (default): `create_charge` works.
- `PAYMENTS_API_VERSION=2`: `create_charge` raises `RemovedApiError`,
  `create_payment` works.

That is what makes the test meaningful: under the new docs, the old
code is actually broken, not just "old-fashioned".

## Layout

```
random-api-app/
├── main.py                    # CLI entry point: python main.py
├── src/
│   ├── clients.py             # requests + httpx calls (unaffected by v2)
│   ├── checkout.py            # OLD payment code — the breaking usage
│   └── digest.py              # Builds the digest text from the API results
├── fictional_payments/        # Local v1/v2 payment API
├── docs/API_CHANGELOG-v2.md   # Latest docs Guardian must compare against
├── scripts/
│   ├── check_api_drift.py     # Local Guardian-style scan (exit 1 = breaking found)
│   └── apply_migration.py     # Applies the v2 fix to src/checkout.py
├── migrations/001-payments-v2.patch
├── tests/                     # pytest suite, mocked external APIs — no network needed
└── requirements.txt           # requests, httpx, pytest only — no FastAPI
```
