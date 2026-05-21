# Backend Patterns

Conventions for the `sca-tracker` backend. **Read before building any new
feature.** Established in Step 2.2b — ADR-0067 through ADR-0074 (especially
ADR-0070, the architecture); the layer taxonomy was refined by ADR-0079.

This document describes the backend structure (ADR-0070, layer taxonomy
refined by ADR-0079).

Engine internals — the dispatcher pipeline, history capture, isolation
primitives — are M0 substrate and are **not** re-documented here. This doc
covers how to *author a feature slice* over that engine.

---

## Architecture

The backend is **vertical feature slices over a shared command engine** — not
horizontal layers. Horizontal structure is used only where code is genuinely
cross-cutting (the engine, the I/O adapters, the transport layer);
per-concern code is vertical.

```
app/
├── engine/           the command engine — domain- and framework-agnostic
├── adapters/         shared concrete I/O
├── http/             cross-cutting FastAPI / transport code
├── auth/             identity: User / UserRole / Session, login, current_user
├── features/         one vertical slice per concern
│   └── <entity>/
├── cli/              dev / admin CLIs (bootstrap_admin, seed_db, ...)
├── config.py         settings
├── runtime.py        composition root (builds the production dispatcher)
└── main.py           FastAPI app assembly
```

| Folder       | Holds                                                                                                                                                                            |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `engine/`    | `Command` / `Invariant` base + registry, the dispatcher, `Caller` / `Role`, the `CaptureSink` port + record types, exceptions, the `require_role` predicate factory, CRUD authoring helpers, lock-key policy. Domain- *and* framework-agnostic — imports no web framework. |
| `adapters/`  | The SQLAlchemy engine / `Base` / session factory, the Postgres-specific primitives (`json_column`, advisory lock, SERIALIZABLE isolation), the per-entity history tables + `command_audit_log`, the concrete `SqlAlchemyCaptureSink`. |
| `http/`      | Cross-cutting FastAPI / transport code not owned by one feature: the exception → HTTP mapping (`error_handlers`), the read-API pagination contract (`pagination` — `Page` / `PaginationParams` / `paginate`), the healthcheck route (`health`). |
| `auth/`      | The entire identity concern — `User` / `UserRole` / `Session` entities, login / logout / me routes, user-admin CRUD, password hashing, session lifecycle, the `current_user` dependency. Not a feature: every request resolves it. |
| `features/*` | One vertical slice per concern. See **Feature-slice structure**.                                                                                                                  |

### The dependency rule

The backend twin of ADR-0064's frontend layering. Enforced by convention +
review (a mechanical import-linter check is a candidate follow-up).

| Module                | May import                                              |
| --------------------- | ------------------------------------------------------- |
| `engine/`             | nothing internal                                        |
| `adapters/`           | `engine/`                                               |
| `http/`               | `engine/`                                               |
| `auth/`, `features/*` | `engine/`, `adapters/`, `http/` (a feature may also import `auth/`) |
| `runtime.py`, `main.py` | everything (composition roots)                        |

`features/*` must **not** import each other — an entity class may be
cross-imported only where an FK relationship requires the referenced class
(provisional; firmed when M1.4 introduces the first FK). Commands and routes
are never cross-imported between slices.

`User` has **no `features/users/` slice** — the `User` entity, its admin CRUD,
and login all live in `auth/`, because login needs the `User` entity and
splitting it would re-create the scatter this layout removes (ADR-0070).

---

## Feature-slice structure

A `features/<entity>/` slice is a Python module. Its submodules are drawn from
a **closed vocabulary**:

| Submodule  | Holds                                                          |
| ---------- | -------------------------------------------------------------- |
| `entities` | the SQLAlchemy model(s) for the slice                          |
| `commands` | the `Create*` / `Edit*` / `Delete*` command classes + pre-checks |
| `routes`   | the FastAPI `APIRouter` + route functions                      |
| `schemas`  | route request / response DTOs (Pydantic)                       |
| `queries`  | read-query functions backing the read routes                   |

Each submodule is **a file or a package** — `commands.py` *or*
`commands/__init__.py` — addressed by the same import path either way
(`app.features.contracts.commands`). Start as a file; promote to a package when
it outgrows one, with no change to any consumer's import.

The vocabulary is closed; none are mandatory — create a submodule when it gets
its first content, and keep no loose files at a slice root. A package
`__init__.py` is re-exports + `__all__` only. Non-uniform domain logic gets a
concretely-named module (`features/contracts/pricing.py`), not a generic
bucket.

Slice folders are named in the **plural** (`features/contracts/`,
`features/employees/`) — matching the frontend and the route prefixes.

---

## The command engine

The dispatcher runs a fixed pipeline once per command:

```
authorization → lifecycle gate → apply (handler) → invariants → history → commit
```

wrapped in a retry loop that re-runs the whole pipeline on transient
contention (advisory-lock fast-fail, Postgres `serialization_failure`). **Any
rejection rolls the whole thing back** — no mutation persists, no history row
is written. History and `command_audit_log` capture is enforced by the
dispatcher and cannot be skipped.

You author a `Command`; the engine enforces auth, lifecycle, invariants,
history / audit, and commit. The engine itself is M0 substrate — see ADR-0058
(dispatcher + retry), ADR-0052 / ADR-0057 (history + audit), ADR-0056
(isolation), and `engine/dispatcher.py`.

---

## Writing a command

Admin-roster CRUD commands are **hand-authored `Command` subclasses** — one
class per (entity, operation) — over the shared helpers in `engine/crud.py`
(ADR-0067). **Not** a generalized factory: the roster entities are non-uniform
(Contract's JSONB schedule, User's password hash), and a factory wide enough to
cover them stops being simpler than an explicit class.

A command subclass declares:

| Member                          | Purpose                                                          |
| ------------------------------- | ---------------------------------------------------------------- |
| `target_entity`                 | the SQLAlchemy model the command operates on                     |
| `authorization`                 | the authorization predicate (see **Authorization**)              |
| `Payload`                       | a nested Pydantic model — the command's input contract           |
| `handler(self, session, payload)` | applies the mutation; returns the created / mutated entity     |
| `invariants`                    | list of `Invariant` subclasses, revalidated post-handler (default `[]`) |
| `transition_name` + `resolve_target` | lifecycle commands only — none in M1.2's flat roster        |
| `cascade` / `destructive`       | cascade machinery; default off                                   |

Register the class at module-import time: `register(CreateContract)`.

**Naming: PascalCase verb-then-noun** — `CreateContract`, `EditContract`,
`DeleteContract`. `Command.name()` returns the class name; that string is the
registry key *and* the `command_name` written into every history /
`command_audit_log` row. It is a stable public identifier — renaming a command
class is a contract change.

### Shared `crud.py` helpers

| Helper                                   | Use                                                                          |
| ---------------------------------------- | ---------------------------------------------------------------------------- |
| `resolve_for_command(session, model, id)` | get-by-id; raises `EntityNotFound` on a missing or soft-deleted row. Use in every edit / delete handler. |
| `apply_scalar_fields(entity, payload, fields)` | copy named scalar fields payload → entity. JSONB-collection columns are set explicitly at the command. |
| `soft_delete(entity)`                    | stamp `deleted_at` for the soft-delete policy.                               |

The non-uniform parts stay explicit at the command (Contract's
`_schedule_to_json`, the uniqueness pre-check). If a new entity pressures the
helper set, **amend the helpers** — do not introduce a factory.

```python
class CreateContract(Command):
    target_entity = Contract
    authorization = require_role(Role.ADMIN)

    class Payload(BaseModel):
        contract_number: str
        name: str | None = None
        start_date: date
        # ...

    def handler(self, session: Session, payload: BaseModel) -> Contract:
        assert isinstance(payload, CreateContract.Payload)
        _require_unique_number(session, payload.contract_number)
        contract = Contract()
        apply_scalar_fields(contract, payload, _SCALAR_FIELDS)
        session.add(contract)
        return contract


register(CreateContract)
```

---

## Authorization

ADR-0047's chain-level **class-rule** predicates are encoded once as the
factory `require_role(minimum: Role)` in `engine/predicates.py` (ADR-0068).
It returns the `(caller, command_cls, payload, session) -> bool` callable the
dispatcher reads off `Command.authorization`.

- Admin-roster CRUD uses `require_role(Role.ADMIN)` verbatim — ADR-0047
  Cluster 1, whose entity set is Employee / School / Contractor / User /
  Contract (ADR-0074).
- Later clusters use `require_role(Role.COORDINATOR)`, etc.
- **Non-uniform predicates** — ADR-0040's parameterized grant / revoke
  authority, creator-only rules — are **not** the factory's job. Author them
  inline at the command; they read `caller.roles` directly (ADR-0062).

---

## Natural-key uniqueness

A natural key backed by a DB `UNIQUE` constraint (Contract's
`contract_number`, User's `username`) is enforced by a **handler pre-check
before `session.add` / `flush`** — *not* as a dispatcher `Invariant`
(ADR-0071). The pipeline flushes before its invariant step, so a uniqueness
`Invariant` would never run: the DB `UNIQUE` constraint fires at the flush and
raises a raw `IntegrityError` first.

The handler queries for an existing row with the candidate value (excluding the
entity's own id on edit) and raises `InvariantViolation` if found. The DB
`UNIQUE` constraint stays as the hard backstop against a concurrent race; a
violation that slips past the pre-check surfaces as `IntegrityError` → 409.

Contract currently has a private `_require_unique_number`; a shared
`require_unique` helper is extracted into `crud.py` once User's `username` is
the second consumer (a Step 2.2c carry-forward).

---

## Audit-metadata columns

Every domain entity carries four **audit-metadata columns** — `created_at`,
`created_by`, `updated_at`, `updated_by` — written **uniformly by the
dispatcher** (ADR-0072 / ADR-0075). An entity opts in by mixing in
`AuditMetadataMixin` from `app.engine.audit` alongside `Base`; the
dispatcher stamps any command target it recognizes. **Do not set them in a
handler.**

The dispatcher stamps `created_*` only when the command **creates** its
target and `updated_*` on **every** command — so at creation
`created_* == updated_*`, and every later mutating command (including a soft
delete) refreshes `updated_*` only. A creating command signals itself by
declaring `creates = True` on the Command class (ADR-0075); the default is
`False`.

They are a dispatcher-maintained **read projection** — a denormalized
convenience surfaced directly in read schemas — over the authoritative
who / what / when record in `command_audit_log` and the per-entity history
tables. They are reproducible from those; they are not a rival source of
truth: the command clock stamped here is the same instant written to the
matching `command_audit_log` / history row.

Contract and User gained the columns in Step 2.2b-C-2; every entity authored
from Step 2.2c onward is born with the mixin and a `creates`-flagged create
command.

---

## Errors

Handlers raise typed domain exceptions; the dispatcher lets them propagate
unwrapped (ADR-0011); `app/http/error_handlers.py` owns the HTTP mapping. A handler
must **never** raise `HTTPException` — that couples the domain to FastAPI.

| Exception                                            | HTTP | Raised when                                          |
| ---------------------------------------------------- | ---- | ---------------------------------------------------- |
| `AuthorizationDenied`                                | 403  | the authorization predicate returned `False`         |
| `EntityNotFound`                                     | 404  | an edit / delete target is missing or soft-deleted   |
| `LifecycleViolation` / `InvariantViolation` (`CommandRejected`) | 409 | a transition is not permitted / an invariant failed |
| `TransientContention`                                | 503  | the retry loop exhausted under contention            |
| `IntegrityError`                                     | 409  | DB-constraint backstop (e.g. a lost uniqueness race) |

`EntityNotFound` is a `CommandRejected` subclass (ADR-0073) — FastAPI resolves
handlers by walking the exception MRO, so its 404 handler takes precedence over
the `CommandRejected` 409 base handler. It is raised by `resolve_for_command`,
so every edit / delete gets clean 404 behavior for free.

---

## Routes, DTOs, and reads

A slice's HTTP surface lives in its `routes` submodule. The **route DTOs live
in `schemas`, kept separate from the command `Payload`s** (ADR-0070): the DTO
is the OpenAPI wire contract the generated frontend client consumes; the
`Payload` is the command's internal input contract. They evolve independently —
e.g. `EditContract.Payload` carries `id` from the URL path, while the write DTO
is body-only. The field duplication is **accepted, not derived away** (tracked
as `DRIFT-001` in `planning/DRIFTS.md`).

**Write routes** dispatch through the pipeline: inject the dispatcher with
`Depends(get_dispatcher)`, build the command `Payload` from the request DTO,
and call `dispatcher.dispatch(Command, payload, caller)`.

**Read routes are not Commands** — they take a plain session via
`Depends(get_db)` and require any authenticated user (`Depends(current_user)`).
The read-query logic backing them belongs in the slice's `queries` submodule.

---

## Seeding

Seed data is loaded by `app/cli/seed_db.py`, which **dispatches `create_*`
commands through the pipeline** (ADR-0069) — never direct ORM inserts — so
seeded rows carry real history + `command_audit_log` records, identical to data
created through the UI.

**Standing requirement: every entity-adding sub-step from M1.2 onward extends
`seed_db` coverage for the entities it introduces.** When you add an entity:

- add a `SeedSpec` to `SEED_ORDER` (in dependency order) — the entity name, its
  `create_*` command, the entity model, the natural key, and a CSV-row →
  `Payload` loader;
- a JSONB-collection column gets a **sidecar CSV** joined on the natural key
  (see Contract's `contract_code_fees.csv`);
- idempotency is **skip-existing** on the natural key — re-running tops up,
  never wipes.

Seed CSVs live in `app/cli/seeds/` and are gitignored (redacted real data);
only the README describing the formats is committed.

---

## Migrations

Schema changes are Alembic migrations in `migrations/versions/`. Per the
project's Neon-current policy: author the migration, apply it to the Neon dev
DB with `uv run alembic upgrade head`, then commit — the dev DB stays at
Alembic head. Throwaway SQLite is for pre-commit shape iteration only.

Postgres 15+ is the production floor; no vendor-specific extensions (ADR-0055).
Postgres-specific features — `json_column()`, advisory locks, SERIALIZABLE —
go through the `adapters/` boundary, which has degraded SQLite equivalents for
offline / test use.

---

## Testing

- Runner: pytest. `uv run pytest` (or `just test-backend`). Tests live in
  `backend/tests/` — a top-level tree, **not** colocated (unlike the frontend).
- `tests/conftest.py` provides the shared seams: `sqlite_engine` /
  `sqlite_session_factory` (in-memory SQLite); `auth_client` (a `TestClient`
  wired to SQLite for full login round-trips); and the per-role `as_superadmin`
  / `as_admin` / `as_coordinator` / `as_auditor` fixtures, which override
  `current_user` so command / route tests can assert ADR-0047 predicates
  without a real login.
- A **command test** exercises the handler + its authorization predicate + its
  invariants / pre-checks; a **route test** exercises the HTTP surface,
  including the exception → status mapping.
- Tests run on SQLite — advisory locks and SERIALIZABLE isolation are not
  exercised; that is the documented degraded-fallback boundary.
