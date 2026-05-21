# sca-tracker — Backend

FastAPI + SQLAlchemy 2.0 service. Every state-changing operation is a
`Command` run through the dispatcher pipeline; the OpenAPI schema is exported
to a committed contract the frontend client is generated from.

## Build & run

- `uv sync` — install dependencies
- `uv run uvicorn app.main:app --reload` — dev server
- `uv run pytest` — test suite
- `uv run ruff check .` / `uv run ruff format .` — lint / format
- `uv run pyright` — type check (or `just typecheck-backend`; `just ci` runs it)
- `uv run alembic upgrade head` — apply migrations
- `uv run python -m app.cli.export_openapi --out ../contracts/openapi.json` —
  re-export the schema (or `just gen-openapi` to also regenerate the client)

`just` recipes: `just migrate`, `just bootstrap-admin`, `just seed`,
`just first-run` (chains install + bootstrap + seed).

## Conventions

**Read `app/PATTERNS.md` before building any feature.** It owns the
vertical-slice architecture, the dependency rule, command authoring,
authorization, errors, and seeding.

Non-obvious points:

- **Every state change goes through a `Command`** dispatched through the
  pipeline — never a direct ORM `INSERT` / `UPDATE`. Login is the one
  documented exception (it produces the `Caller` the pipeline requires).
  `seed_db` is *not* an exception — it dispatches `create_*` commands.
- **`app/PATTERNS.md` describes the ADR-0070 target structure.** Until the
  Step 2.2b-C refactor lands, the code still has the M1.1/M1.2 layout
  (`app/domain/`, `app/routes/`, concrete I/O inside `app/framework/`).
- **Migrations apply to Neon immediately.** Author the migration, run
  `uv run alembic upgrade head` against the Neon dev DB, then commit — the
  dev DB stays at Alembic head. Throwaway SQLite is for pre-commit shape
  iteration only.
- **The OpenAPI schema is a committed artifact.** Any change to a route's
  request/response surface requires re-exporting `contracts/openapi.json`
  and regenerating the frontend client (`just gen-openapi`); CI fails on
  drift.
- **Postgres 15+ is the production target; SQLite is a degraded fallback**
  for offline iteration and tests — advisory locks and SERIALIZABLE
  isolation are not exercised on it.
