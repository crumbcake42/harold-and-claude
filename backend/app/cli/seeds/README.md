# Seed data

CSVs in this folder are loaded into the database by `seed_db`:

```
uv run python -m app.cli.seed_db          # or: just seed
```

Each row is dispatched as a `create_*` Command through the full pipeline
(invariants run, audit-log rows are written) — not INSERTed directly.
Seeding is idempotent: a row whose natural key already exists is skipped.

The CSV files themselves are **gitignored** — they hold redacted real data,
produced by `redact_csv.py`. Only this README is committed. Run `seed_db`
on a fresh checkout with no CSVs present and it reports `0 created`.

`seed_db` resolves its actor from the database: it runs as the superadmin
created by `bootstrap_admin`, so bootstrap first.

## File formats

One CSV per entity; an empty cell means "no value" (→ `NULL` for optional
columns). Dates are ISO format (`YYYY-MM-DD`).

### `contract.csv`

| column            | required | notes                                  |
|-------------------|----------|----------------------------------------|
| `contract_number` | yes      | natural key — uniqueness-constrained    |
| `name`            | no       | blank → display label derives from `#` |
| `start_date`      | yes      | ISO date                               |
| `end_date`        | no       | ISO date; blank → open-ended            |

### `contract_code_fees.csv` (sidecar)

Contract's `code_flat_fee_schedule` is a JSONB collection, so it lives in a
flat sidecar joined to `contract.csv` by `contract_number`. Optional — a
contract with no rows here seeds with an empty schedule.

| column            | required | notes                          |
|-------------------|----------|--------------------------------|
| `contract_number` | yes      | joins to `contract.csv`        |
| `code_type`       | yes      | WA code type the fee prices    |
| `fee`             | yes      | decimal flat fee               |
