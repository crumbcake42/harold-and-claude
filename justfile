# sca-tracker task runner. Default shell is `sh`; on Windows git-bash provides it.

set windows-shell := ["sh", "-c"]

default:
    @just --list

# --- install (idempotent env setup) ---

install: install-backend install-frontend migrate

install-backend:
    cd backend && uv sync

install-frontend:
    cd frontend && pnpm install

# --- database ---

# Apply Alembic migrations to the configured DATABASE_URL (idempotent).
migrate:
    cd backend && uv run alembic upgrade head

# --- data init (interactive / destructive — kept out of `install`) ---

# Create the first superadmin (prompts for username + password).
bootstrap-admin:
    cd backend && uv run python -m app.cli.bootstrap_admin

# Load redacted CSVs from app/cli/seeds/ through the Command pipeline.
seed:
    cd backend && uv run python -m app.cli.seed_db

# Fresh-machine setup: env setup, then interactive data init.
first-run: install bootstrap-admin seed

# --- dev servers ---

dev-backend:
    cd backend && uv run uvicorn app.main:app --reload

dev-frontend:
    cd frontend && pnpm dev

# --- lint ---

lint: lint-backend lint-frontend

lint-backend:
    cd backend && uv run ruff check .

lint-frontend:
    cd frontend && pnpm lint

# --- format ---

format: format-backend format-frontend

format-backend:
    cd backend && uv run ruff format .

format-frontend:
    cd frontend && pnpm lint:fix

# --- typecheck ---

typecheck: typecheck-backend typecheck-frontend

typecheck-backend:
    cd backend && uv run pyright

typecheck-frontend:
    cd frontend && pnpm typecheck

# --- test ---

test: test-backend test-frontend

test-backend:
    cd backend && uv run pytest

test-frontend:
    cd frontend && pnpm test

# --- openapi (backend export -> frontend client regen) ---

gen-openapi: gen-openapi-schema gen-openapi-client

gen-openapi-schema:
    cd backend && uv run python -m app.cli.export_openapi --out ../contracts/openapi.json

gen-openapi-client:
    cd frontend && pnpm gen-api

# --- everything CI runs ---

ci: lint typecheck test
