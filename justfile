# sca-tracker task runner. Default shell is `sh`; on Windows git-bash provides it.

set windows-shell := ["sh", "-c"]

default:
    @just --list

# --- install ---

install: install-backend install-frontend

install-backend:
    cd backend && uv sync

install-frontend:
    cd frontend && pnpm install

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

# --- typecheck (frontend only; mypy not in stack) ---

typecheck:
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
