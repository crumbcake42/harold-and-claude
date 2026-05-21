# Implementation Steps

## File contract

**Holds:** Ordered list of steps within the Implementation phase. Each step maps to a milestone from `planning/roadmap.md` (M0 → M8). The first step (M0 Foundations) opens with a full brief; subsequent steps carry short stubs pointing at the roadmap, with full briefs expanded as each step lands (Case 2 sizing per `_workflow.md`).
**Update when:** A step is opened (expand its stub into a full brief — Goal / In scope / Inputs / Outputs / Estimate / Done when); a step completes (mark complete inline; advance `handoff.md`'s next-session pointer); a step partitions (split per `_workflow.md`'s Case 2 protocol). Adding a feature beyond `mvp.md`'s 6 must-haves requires a superseding ADR before editing.

Ordered plan for the Implementation phase of `sca-tracker`. Each step maps 1:1 to a roadmap milestone; partitioning into sessions happens per-step via Case 2 sizing as the step opens. The carry-forward landing index in `roadmap.md` shows which command-shape and implementation-phase carry-forwards land in which step.

---

## Step 1 — M0 Foundations (L)

**Partitioned 2026-05-17 (Option A — substrate-then-decisions, 5 sub-steps). Collapsed 2026-05-18 to 4 sub-steps when Step 1.2 (PaaS vendor pick) resolved as a deferral per ADR-0055** — user push-back established that no production audience exists yet, MVP scope has no vendor-specific feature dependencies, and the "dependency ordering" rationale that placed Step 1.2 inside M0 was not actually load-bearing. The vendor pick carries forward to M8 (or earlier if user prompts circle-back). Downstream sub-steps renumbered: original 1.3 → 1.2 (M0.2 Data-layer primitives), 1.4 → 1.3 (M0.3 Dispatcher + history), 1.5 → 1.4 (M0.4 Adapter boundary). Original partition rationale stands for the remaining four: M0.1 mechanical first; decision sub-steps land in dependency order (primitives → dispatcher consumes them → adapter wraps the Postgres specifics).

**Goal:** Stand up the plumbing the rest of the Implementation phase consumes — repo skeletons, CI, the `Command` base class + dispatcher carrying the `logic.md` pipeline, history infrastructure with dispatcher-enforced capture, the adapter boundary for Postgres-specific features, and the deferred ADR-0052 carry-forwards (per-invariant isolation primitives, audit-log write timing). PaaS pick deferred per ADR-0055.

**Sub-step roster:**

| Sub-step | Title | Size | Branch | ADRs expected |
|---|---|---|---|---|
| **1.1** | M0.1 Scaffolding (cleanup + repo skeletons + CI) | M | `m0/01-scaffolding` | none — mechanical |
| **1.2** | M0.2 Data-layer primitives (isolation + audit-log timing) | S–M | `m0/02-data-layer-primitives` | ADR-0056 (possibly two) |
| **1.3** | M0.3 `Command` base class + dispatcher + history infrastructure | L (partitioned 2026-05-18 → 1.3a M / 1.3b M; single branch) | `m0/03-dispatcher-and-history` | ADR-0058 + likely more if dispatcher design surfaces ADR-worthy decisions |
| **1.4** ✓ | M0.4 Adapter boundary for Postgres-specific features + integration check (Session 33, 2026-05-19) | S | `m0/04-adapter-boundary` | none |

Administrative bookkeeping branch from the 2026-05-18 deferral session: `m0/admin-paas-deferral` (landed ADR-0055 + this restructure; not a canonical M0 sub-step).

**Execution order:** 1.1 ✓ → 1.2 ✓ → 1.3 ✓ (1.3a + 1.3b) → 1.4 ✓ → **Step 1 ✓ COMPLETE 2026-05-19 (Session 33)**; next branch ops: FF-merge `m0/04-adapter-boundary` → `m0/foundations`; merge `m0/foundations` → `dev` with `--no-ff`; tag `m0-complete` on `dev`. Step 2 (M1 Roster) follows on a new milestone branch off `dev`.

**Inputs:** `planning/mvp.md`, `planning/roadmap.md` § M0, `planning/architecture.md`, `planning/data-model.md`, `planning/framework.md`, `planning/logic.md`, `planning/history-patterns.md`, `planning/decisions.md` (esp. ADR-0001, ADR-0051, ADR-0052, ADR-0055), `planning/handoff.md`.

**Done when:** All 4 sub-steps complete; M1 can begin (M0 dispatcher + history infrastructure can host M1's first command, e.g., `create_employee`).

---

### Step 1.1 — M0.1 Scaffolding (M)

**Goal:** Land the mechanical scaffolding — clean the stale `backend/` and `frontend/` directories, stand up the backend + frontend repo skeletons per ADR-0051, wire CI. No deliberation, no ADRs.

**In scope:**

1. **Stale-scaffolding cleanup.** Per ADR-0001 + ADR-0051: clear the existing `backend/` and `frontend/` directories. Commit the deletion separately so the cleanup is auditable in the log.
2. **Backend repo skeleton.** Python 3.12+ on CPython + FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic + Ruff + Pytest per ADR-0051. Initial migration scaffold (no domain entities yet — just the Alembic baseline). Project layout decisions for where commands / entities / handlers / dispatcher will live (light decisions; surface at session head if any are non-obvious). Dependency pinning.
3. **Frontend repo skeleton.** TypeScript on Node + Vite + React + TanStack Router + TanStack Query + openapi-ts + Storybook + ESLint + Prettier per ADR-0051. Wire the openapi-ts pipeline (FastAPI OpenAPI schema → typed TanStack Query hooks) so the contract is enforced from M1 onward.
4. **CI pipeline.** Backend + frontend lint + test + typecheck on PR. Integration test suite against Postgres (docker-compose Postgres in the runner; vendor-coupled ephemeral-branch wiring stays deferred per ADR-0055 until the PaaS pick lands).

**Out of scope:**

- PaaS vendor pick — deferred per ADR-0055 (lands at user-triggered circle-back or at latest M8).
- Per-invariant isolation primitives + audit-log write timing — M0.2 (Step 1.2).
- `Command` base class + dispatcher + history infrastructure — M0.3 (Step 1.3).
- Adapter boundary code — M0.4 (Step 1.4).
- Any domain entity, command, or handler — M1+.

**Inputs:** ADR-0001 (stale-scaffolding); ADR-0051 (runtime stack); `architecture.md` § component diagram; `roadmap.md` § M0; `planning/handoff.md`.

**Outputs:**

- Cleaned `backend/` and `frontend/` directories (cleanup commit separate from skeleton commits).
- Backend skeleton: runnable `uvicorn` server with a healthcheck endpoint; Alembic baseline migration in place; `pytest` runs green on a sample test; `ruff check` clean.
- Frontend skeleton: runnable `vite` dev server with a sample TanStack-routed page; `tsc --noEmit` clean; ESLint + Prettier clean; Storybook scaffolding runnable; openapi-ts pipeline wired against a placeholder OpenAPI schema.
- CI workflow(s): green on the sample tests + lint + typecheck. docker-compose Postgres in the runner.
- No ADRs.

**Estimate:** M.

**Done when:**

- Both skeletons start locally with a single command (e.g., `make dev` or equivalent).
- CI is green on a PR-style integration test run.
- The openapi-ts pipeline successfully regenerates the frontend client from a sample backend OpenAPI schema.
- The `backend/` and `frontend/` directories contain only the new skeletons (no leftover stale-scaffolding files).
- Repository is ready for M0.2's data-layer primitives work to land without scaffolding changes.

---

### Step 1.2 — M0.2 Data-layer primitives (S–M)

**Brief:** Resolve ADR-0052's two deferred carry-forwards as a coupled pair (both are data-layer enforcement-mechanism decisions): per-invariant isolation-primitive assignment (`SERIALIZABLE` default + `pg_try_advisory_xact_lock` opt-in; first per-invariant choices land here — likely candidates per `domain-model.md` § Design patterns #3 closure-readiness cluster + EmployeeRole disjoint-ranges per ADR-0045); audit-log write timing (in-txn vs. post-commit). Lands as ADR-0056 (possibly two).

**Roadmap pointer:** `planning/roadmap.md` § M0 items for isolation primitives + audit-log timing.

**Branch:** `m0/02-data-layer-primitives` off `m0/foundations`.

---

### Step 1.3 — M0.3 `Command` base class + dispatcher + history infrastructure (L)

**Brief:** The load-bearing substrate. Implement the `Command` base class + dispatcher per ADR-0051 + ADR-0052, with the `logic.md` pipeline: auth (ADR-0012 predicate eval per ADR-0047) → lifecycle (ADR-0009) → apply → invariants (ADR-0010 + per-invariant primitive acquisition per ADR-0056) → history (ADR-0008 / ADR-0052 / in-txn audit emit per ADR-0057) → commit. No handler-level skip of history capture; framework surface does not expose a skip path. History infrastructure per ADR-0052: per-entity append-only tables generator (3 comprehensive — Document / WA / RFA; 6 lifecycle — Project / Sample Batch / Deliverable / EmployeeRole / WA Code / ContractorEngagement) + shared `command_audit_log` (polymorphic `(entity_type, entity_id)`) with in-txn timing per ADR-0057. Common-metadata columns; comprehensive-pattern `snapshot` JSONB; lifecycle-pattern `from_state` / `to_state` / `transition_name` / `state_context`; reference-snapshotting rule (typed-UUID refs only) per ADR-0013 + ADR-0052 § S5.

**Partitioned 2026-05-18 (Session 30, Case 2)** into two sub-sub-steps on a single branch (`m0/03-dispatcher-and-history`). Five of seven fit-checklist signals fired (≥1 independently-deliberable decision, ≥1 new artifact, >60 min, >3 input files, cross-concern). Seam chosen: concern-split — dispatcher pipeline vs. history infrastructure. The capture-sink interface is the seam: 1.3a pins it, 1.3b implements it. Commits land sequentially on the single branch; FF-merge to `m0/foundations` happens after 1.3b lands.

**Roadmap pointer:** `planning/roadmap.md` § M0 items for dispatcher + history infrastructure.

**Branch:** `m0/03-dispatcher-and-history` off `m0/foundations`. Single branch holds both sub-sub-step commits.

---

#### Step 1.3a — Dispatcher pipeline (M)

**Goal:** Land the `Command` base class + dispatcher with the `logic.md` pipeline wired end-to-end against a stub history sink. Pin the capture-sink interface that 1.3b will implement against.

**In scope:**

1. **`Command` base class.** Registration / discovery shape. Introspection surface (name, target entity type, declared invariants, declared cascade children). Cascade semantics per `domain-model.md` § Design patterns #5 (auth-inheritance for compound cascading commands — pre-flag for ADR if non-obvious tradeoffs surface).
2. **Dispatcher pipeline.** Implement `logic.md` order: authorization (ADR-0012 predicate eval per ADR-0047) → lifecycle gate (ADR-0009 state-machine check) → apply (handler mutation) → invariants (ADR-0010 + per-invariant lock acquisition per ADR-0056) → history (emits to capture-sink interface) → commit. Rejection at any step rolls back per ADR-0011 (no mutation, no history).
3. **Per-invariant primitive acquisition wiring.** Wire the `pg_try_advisory_xact_lock` opt-in path per ADR-0056. SERIALIZABLE is the default — set transaction isolation accordingly.
4. **Lock-key namespace.** Pin the hash function + key-prefix discipline (e.g., `hashtext('closure-readiness:' || project_id)::bigint` is illustrative per ADR-0056 — confirm or revise). Namespace must not collide with future advisory-lock uses. Utility module for callers.
5. **`serialization_failure` retry boundary.** Decide: built-in N-attempt retry loop in dispatcher, or pushed up to the route layer. ADR-0058 likely lands here.
6. **Capture-sink interface.** Define the narrow typed interface the history step calls. Stub implementation (in-memory / no-op) for 1.3a smoke tests; 1.3b replaces with real INSERT path.
7. **Sample command for smoke test.** Minimal command exercising the full pipeline end-to-end against the stub sink. Not a domain command — purely substrate verification.

**Out of scope:**

- Per-entity history tables + `command_audit_log` table + Alembic migrations → 1.3b.
- Adapter boundary for Postgres-specific features → Step 1.4.
- Any domain entity / handler beyond the smoke-test sample → M1+.

**Inputs:** ADR-0008, ADR-0009, ADR-0010, ADR-0011, ADR-0012, ADR-0013, ADR-0047, ADR-0051, ADR-0052, ADR-0056, ADR-0057; `planning/logic.md` (pipeline order); `planning/domain-model.md` § Design patterns #5 (cascade auth-inheritance).

**Outputs:**

- `Command` base class module.
- Dispatcher module with pipeline impl.
- Lock-key utility module.
- Capture-sink interface (stub impl).
- Sample command + smoke test exercising the pipeline.
- ADR-0058 (retry boundary) + possibly more if surfaced.

**Estimate:** M.

**Done when:** Sample command runs end-to-end through the pipeline; tests verify rejection at each step rolls back; capture-sink interface is stable enough for 1.3b to implement against.

---

#### Step 1.3b — History infrastructure (M)

**Goal:** Land the per-entity history tables + `command_audit_log` + Alembic migrations. Replace 1.3a's stub capture sink with a real in-txn INSERT path per ADR-0057.

**In scope:**

1. **Per-entity history-table generator.** 9 tables per ADR-0052: 3 comprehensive (Document / WA / RFA) + 6 lifecycle (Project / Sample Batch / Deliverable / EmployeeRole / WA Code / ContractorEngagement). Decide: declarative-base-per-entity vs. dynamic class factory — ADR-worthy if non-obvious.
2. **Common-metadata columns.** `id`, `entity_id` FK, `command_id`, `command_name`, `caller_id`, `at`; default index `(entity_id, at DESC)`. Comprehensive `snapshot` JSONB; lifecycle `from_state` / `to_state` / `transition_name` / `state_context` JSONB.
3. **Typed-UUID reference rule.** References in snapshots are typed UUIDs only per ADR-0013 § Reference snapshotting + ADR-0052 § S5. Enforcement at write time.
4. **`command_audit_log` table.** Polymorphic `(entity_type, entity_id)` shape per ADR-0052 § Audit-log table. Wired for the 7 audit-log entities (Employee, User, Time Entry, Contractor, DepFiling, Contract, WABundle).
5. **Alembic migrations.** All 10 tables.
6. **Replace stub capture sink with real impl.** In-txn write per ADR-0057. Same SQLAlchemy session as the entity mutation. Smoke-test sample command from 1.3a now exercises real INSERTs.
7. **Capture enforcement.** Verify no handler-level skip path. The framework surface does not expose a "skip history" or "skip audit" hook (per ADR-0008 + ADR-0052).

**Out of scope:**

- Anything in 1.3a's scope (already landed).
- Adapter boundary code → Step 1.4 (1.3b may stub adapter call sites for JSONB / advisory locks; full adapter lands in 1.4).
- Any domain entity / handler → M1+.

**Inputs:** ADR-0013, ADR-0052, ADR-0057; `planning/data-model.md` § per-entity attribute rosters + history-table shapes; `planning/history-patterns.md`; 1.3a outputs (capture-sink interface).

**Outputs:**

- 9 per-entity history-table models (or generator).
- `command_audit_log` model.
- Alembic migrations.
- Real capture-sink implementation replacing 1.3a's stub.
- Smoke-test sample command end-to-end against real tables.
- Possible ADR if generator shape surfaces ADR-worthy tradeoffs.

**Estimate:** M.

**Done when:** All 10 tables exist in Postgres; sample command write produces correct history + audit-log rows in the same transaction as the entity mutation; FF-merge `m0/03-dispatcher-and-history` → `m0/foundations` (closing Step 1.3 entirely); M0.4 / Step 1.4 ready to open.

---

### Step 1.4 — M0.4 Adapter boundary for Postgres-specific features (S) ✓ COMPLETE

**Completed Session 33 (2026-05-19).** Three Postgres-specific call sites consolidated into `app/framework/adapter.py`: `json_column()` (relocated from `db.py`), `try_advisory_xact_lock(session, key)` (mechanism moved from `locks.py`; `locks.py` retained as policy — `LockNamespace` + key-builders + `validate_key_namespace`), `set_serializable_isolation(session)` (extracted from `dispatcher._run_pipeline`'s inline call). Call sites updated in `history.py`, `dispatcher.py`, and the smoke-test entities fixture. 11 unit tests added (`tests/test_adapter.py`) verifying dialect-dispatch via mocked `session.bind.dialect.name` for the PG branch and live SQLite for the degraded branch + key-namespace validation + unbound-session edge cases. **Fork resolution: no docker-compose Postgres CI service.** Per user constraint (unreliable Docker access on dev machines), live-engine PG verification is a manual exercise when a developer points `DATABASE_URL` at a real Postgres; CI gate stays SQLite-only. The "CI ephemeral-PR DB wiring" carry-forward stays deferred per ADR-0055. No ADRs landed — mechanical refactor as anticipated.

**Brief (original):** Wrap the Postgres-specific features (JSONB ops; advisory locks per M0.2 choice; `SERIALIZABLE` isolation) behind a documented adapter per ADR-0051. SQLite offline-fallback path uses degraded equivalents; buildable but **not production-equivalent** (acknowledged in ADR-0051 + ADR-0052; restate in code-level docs). Integration check: a sample command flows through the full pipeline (dispatcher → invariants under chosen isolation → history write at chosen timing → commit) via the adapter; both Postgres and SQLite paths build (Postgres production-equivalent; SQLite degraded).

**Roadmap pointer:** `planning/roadmap.md` § M0 item for adapter boundary.

**Branch:** `m0/04-adapter-boundary` off `m0/foundations`. After Step 1.4 lands: FF-merge → `m0/foundations`; then merge `m0/foundations` → `dev` with `--no-ff`; tag `m0-complete` on `dev`. Closes M0 entirely.

---

## Step 2 — M1 Roster + role administration (M, partitioned)

**Partitioned 2026-05-19 (Session 34, Case 2)** into 4 sub-steps. All 7 fit-checklist signals fired during sizing: admin CRUD authoring shape, Caller concrete materialization (ADR-0059 deferred carry-forward), `audit_reason` Note polymorphism mechanism (ADR-0040 deferred carry-forward), `change_employee_role_rate` 4-branch decomposition, plus cross-concern reach (entity authoring + invariants + auth predicates + admin UI). Two scope additions resolved at sizing:

- **Contract hoisted from M2 to M1.2.** ADR-0045 makes EmployeeRole's `contract_id` mandatory; the original M2 placement was a packaging convenience that left EmployeeRole's mandatory FK without an upstream entity. Contract is admin-roster CRUD in character per ADR-0047 Cluster 1.
- **Auth substrate pulled into M1.1.** Authentication was an `architecture.md` line 108 out-of-band concern *"pinned at implementation kickoff"* but never milestoned in `roadmap.md`. M1's "admin dashboard skeleton" forces the question; M1.1 answers it. Lesson saved as [[check-out-of-band-concerns]].

**Goal:** Build the 7 roster entities (+ Contract hoisted from M2) and the admin-side CRUD + role-administration surface that operates on them. Backend + frontend slices land per-sub-step so the admin dashboard is browser-dogfoodable end-to-end from M1.1 onward.

**Sub-step roster:**

| Sub-step | Title | Size | Branch | ADRs expected |
|---|---|---|---|---|
| **1.1** ✓ | M1.1 Auth substrate + frontend shell (Session 35, 2026-05-19) | M+ | `m1/01-auth-shell` | 3 (ADR-0061 auth substrate + ADR-0062 Caller shape + ADR-0063 route-guard pattern) |
| **1.1b** ✓ | Frontend architecture & conventions (inserted 2026-05-19 — not an M-milestone) | M–L | `m1/01b-fe-conventions` | 3 (ADR-0064 four-layer architecture, ADR-0065 UI/form stack, ADR-0066 auth module + conventions) |
| **1.2** | M1.2 Admin substrate + flat roster (Employee / School / Contractor / User / Contract) — **partitioned 2026-05-20 (Session 38, Case 2) → 2.2a / 2.2b / 2.2c / 2.2d** (2.2b — Backend architecture & conventions — inserted Session 40) | L (was M) | `m1/02-flat-roster` (shared) | ~8 (M1.2 closeout, written in 2.2b-A from ADR-0067) |
| **1.3** | M1.3 Role administration (UserRole grant/revoke + `audit_reason` Note) | S–M | `m1/03-role-admin` | 1 (`audit_reason` Note polymorphism mechanism) |
| **1.4** | M1.4 Range-typed entities (EmployeeRole + ContractorEngagement + `change_employee_role_rate`) | M (possibly L) | `m1/04-range-typed` | 0–1 (compound decomposition if non-obvious) |

**Execution order:** 1.1 → 1.1b → 1.2 → 1.3 → 1.4. Each sub-step FF-merges to `m1/roster`; `m1/roster` merges to `dev` with `--no-ff` + tag `m1-complete` at M1 close. Pre-M1.1 cleanup commit (consolidate `scripts/` → `app/cli/`) already landed on `m1/roster` (3684fad, 2026-05-19).

**Inputs:** `planning/mvp.md` § Roster + role administration; `planning/roadmap.md` § M1; `planning/domain-model.md` § Roster entities + § Authorization predicates; `planning/data-model.md` (per-entity attribute rosters); `planning/decisions.md` — ADR-0040 (role catalog + audit_reason Notes), ADR-0045 (EmployeeRole contract scoping), ADR-0047 (per-command authorization predicates), ADR-0059 (Command base class + Caller carry-forward), ADR-0060 (cascade mechanism); `planning/architecture.md` § Out-of-band concerns (auth pull-in rationale).

**Done when:** All 4 sub-steps complete; M2 can begin (Project + WABundle can hang off Contract; admin can grant coordinator roles to users who will run M2's project-tracking flows).

---

### Step 2.1 — M1.1 Auth substrate + frontend shell (M+) ✓ COMPLETE

**Completed Session 35 (2026-05-19).** Auth substrate landed end-to-end on branch `m1/01-auth-shell` (tip = `f0a651d`). Two commits: backend slice (`b7b75b6`) — Caller concrete, User/UserRole/Session models + Alembic migration (`25ea83fcec61_auth_substrate` applied to Neon), framework.auth (argon2id pinned + session CRUD + current_user dep), `/auth/login` `/auth/logout` `/auth/me` routes, CORS middleware; frontend + tests slice (`f0a651d`) — `bootstrap_admin` CLI, per-role pytest fixtures, 13 new auth tests, login/`_authenticated`/admin-shell routes, `useCurrentUser` hook, cookie wiring. **Three ADRs landed: ADR-0061 (auth substrate bundle), ADR-0062 (Caller concrete shape — resolves ADR-0059 carry-forward), ADR-0063 (frontend route-guard pattern + `setQueryData` over `invalidateQueries`).** **One non-obvious bug surfaced + fixed at browser-flow verification:** login's `invalidateQueries` with no active subscriber left the cache stale → `_authenticated.beforeLoad` read the cached null → redirect loop. Fix: `setQueryData(currentUserQueryKey, response.data)` — the login response already contains the Caller. Pattern pinned in ADR-0063. **Verification:** 40 backend tests green (27 prior + 13 new), 1 frontend test green, ruff + ESLint + tsc clean; browser round-trip verified (login → admin shell → sign out → back to login). Neon dev DB at head per [[project-neon-current-policy]].

**Goal (original):** Land the authentication substrate end-to-end — backend login flow producing a Caller, session persistence, frontend login page, auth-guarded route shell, and the Caller concrete shape (resolves ADR-0059's deferred carry-forward). Subsequent sub-steps dogfood the admin dashboard in a browser.

**Locked decisions** (Session 34 chat-side canvass; ADRs author them up):

1. **Session mechanism:** DB-backed server-side sessions. Opaque random token in `httpOnly Secure SameSite=Lax` cookie. `sessions` table `(id, user_id, created_at, expires_at, last_seen_at)`. Default TTL 12h sliding (refresh `last_seen_at` on each request; `expires_at = last_seen_at + 12h`). Revoke = delete row.
2. **Password hashing:** argon2id via `argon2-cffi`. OWASP 2024 default parameters.
3. **First-admin bootstrap:** `app/cli/bootstrap_admin.py` CLI command — prompts for username + password; creates User row + UserRole `superadmin` grant. Pytest fixture seeds a known superadmin for tests.
4. **CORS:** `fastapi.middleware.cors.CORSMiddleware(allow_origins=[settings.FRONTEND_ORIGIN])`. Single allowed origin from settings.
5. **CSRF tokens:** deferred. `SameSite=Lax` cookies cover the practical CSRF surface at single-deployment MVP scale.
6. **Caller concrete shape:** Pydantic `Caller(id: UUID, username: str, roles: frozenset[Role])`. Constructed by FastAPI dependency from session lookup; passed to dispatcher. ADR-0047 predicates read `.roles` directly. Resolves ADR-0059's *"Caller concrete shape"* carry-forward.
7. **Route guard:** TanStack Router `_authenticated` route layout group with `beforeLoad` checking the current-user query; login route sits outside the group; API client interceptor redirects to login on 401.
8. **Login as non-Command surface:** login itself does not go through the Command pipeline (pipeline requires a Caller; login produces one). Implemented as a FastAPI route directly. Documented as the exception.

**In scope:**

- **Backend:**
  - User entity table + Alembic migration. Schema: `(id, username UNIQUE, password_hash, employee_id? UNIQUE, soft_delete_at?)`.
  - Session entity table + Alembic migration per Decision 1.
  - `app.framework.auth` module: argon2id hash/verify wrappers; session creation/lookup/deletion; FastAPI `current_user` dependency producing Caller.
  - Auth routes (non-Command): `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`.
  - `Caller` Pydantic model (location decided at session head — likely `app.framework.caller`).
  - CORS middleware wiring.
  - `app/cli/bootstrap_admin.py`.
  - Pytest fixture for "logged in as <role>" (creates User + Session + returns Caller).
- **Frontend:**
  - `/login` route with form (username/password) + error surface.
  - `_authenticated` route layout group with `beforeLoad` auth check.
  - `useCurrentUser` TanStack Query hook.
  - Logout button in the authenticated shell.
  - API client interceptor that redirects to `/login` on 401.
  - Admin dashboard shell page (placeholder header + nav; per-entity pages land in 1.2+).
  - Storybook entries for login form + auth shell.

**Out of scope (MVP-deferred):**

- Password reset flow (admin re-sets via `edit_user` in M1.2).
- Login rate limiting / lockout.
- Remember-me / persistent sessions beyond 12h sliding TTL.
- 2FA / MFA / OAuth / SSO.
- Immediate session invalidation on `revoke_user_role` (per `mvp.md` line 73; next-request authorization check is MVP behavior).
- CSRF tokens (deferred per Decision 5).

**Inputs:** Session 34 canvass (Decisions A–G + D'); ADR-0040 (role catalog); ADR-0047 (predicates); ADR-0059 (Caller carry-forward); `app/framework/command.py` (Caller Protocol shape); `app/framework/dispatcher.py` (Caller call sites); `app/framework/db.py` (engine + session factory); `app/cli/export_openapi.py` (existing CLI pattern).

**Outputs:**

- User + Session entity tables + Alembic migration.
- `app.framework.auth` module + `Caller` concrete Pydantic model.
- Auth routes (`/auth/login`, `/auth/logout`, `/auth/me`).
- CORS middleware wired.
- `app/cli/bootstrap_admin.py` + pytest fixture.
- Frontend login page + authenticated layout group + current-user hook + 401 interceptor + admin dashboard shell.
- 2–3 ADRs at write time **ADR-0061+**: auth substrate (sessions + hashing + bootstrap + CORS + non-Command login, likely bundled); Caller concrete shape (closes ADR-0059 carry-forward); possibly frontend route-guard pattern if non-obvious.

**Estimate:** M+ (possibly L). Contingency: if frontend route-guard pattern surfaces unexpected complexity (TanStack Router `beforeLoad` × current-user hook interaction), split 1.1a backend / 1.1b frontend.

**Done when:**

- Fresh DB + `uv run python -m app.cli.bootstrap_admin` produces a usable superadmin.
- Browser flow: visit `/`, redirected to `/login`, log in, land on admin shell, can hit `/auth/me`, logout returns to login.
- Pytest fixtures let M1.2+ tests construct "logged in as admin" Callers trivially.
- Auth ADRs land + Caller concrete shape consumed by the dispatcher (no Protocol-typed placeholder).

---

### Step 2.1b — Frontend architecture & conventions (M–L, inserted) ✓ COMPLETE

**✓ COMPLETE 2026-05-20 (Session 37).** Both sub-sub-steps landed on `m1/01b-fe-conventions`: 2.1b-A (Session 36 — four-layer architecture + UI/form stack; ADR-0064/0065) and 2.1b-B (Session 37 — auth port + test/story colocation; ADR-0066). FF-merge `m1/01b-fe-conventions` → `m1/roster` at close.

**Inserted 2026-05-19** between Step 2.1 (M1.1) and Step 2.2 (M1.2) — an insertion, not a split (mirrors the `6b-residual-2` precedent; logged in `sessions.md` § Restructure log). **Does not map to a roadmap milestone** — a documented exception to this file's 1:1 step↔milestone contract. Triggered by a planning side-session: adapt-and-port `sca-ih-tracker`'s mature four-layer frontend architecture into this repo *before* M1.2 builds the first substantial frontend feature.

**Scoped brief (2026-05-20):** the sub-sub-step briefs below + the intact `sca-ih-tracker` reference repo (`C:\Users\msilberstein\Documents\sca-ih-tracker`) are the authoritative in-repo brief for this step.

**Partitioned 2026-05-20 (Session 36, Case 2)** into two sub-sub-steps on a single branch. Fit-checklist signals 2 (multiple from-scratch artifacts — `PATTERNS.md` + `CLAUDE.md` + ADR-0064/0065), 3 (duration >60 min), 5 (cross-concern — tooling adoption + architecture + documentation) fired. Seam: **A** adopt + scaffold + document; **B** port M1.1 auth + test/story colocation. B depends on all of A. Commits land sequentially on the single branch (1.3a/1.3b precedent); FF-merge to `m1/roster` after 2.1b-B.

**Goal:** Establish and enforce the frontend code-organization conventions M1.2+ will consume — a strictly one-way four-layer architecture (`routes → pages → features → components/hooks/fields/lib`), a per-feature API-barrel layer over the generated client, test/story colocation — captured in a co-located conventions doc, ESLint-enforced, with the M1.1 auth code restructured into the model as a working reference. Adopt shadcn/ui + Zod + react-hook-form so M1.2 is fully equipped (this also settles the shadcn-adoption question previously flagged as an open M1.2 decision).

**Out of scope (whole step):** entity-abstraction patterns (`EntityListPage`, `useEntityForm`, `DataTable`, comboboxes) — extracted just-in-time when M1.2+ yields a second consumer, not invented now; any M1.2 roster entity / command / route / admin page; backend or OpenAPI-surface changes.

**Inputs:** the `sca-ih-tracker` reference repo — `frontend/src/PATTERNS.md`, `frontend/CLAUDE.md`, `frontend/eslint.config.js`, `frontend/components.json`, `frontend/package.json`, `frontend/src/{auth,features/auth,features/schools/api}/*`; ADR-0063 (frontend route-guard pattern — the port must preserve it); current `frontend/src/` (M1.1 auth shell).

**Branch:** `m1/01b-fe-conventions` off `m1/roster` (after the `m1/01-auth-shell` FF-merge the handoff prescribes). Single branch holds both sub-sub-step commits.

**Estimate:** M–L.

**Done when:** both sub-sub-steps complete; conventions doc lands; four-layer skeleton + ESLint layering enforcement in place; shadcn/Zod/RHF installed; M1.1 auth runs unchanged from the new structure (login round-trip verified); `pnpm lint` / `typecheck` / `test` / `build` green; ADR-0064 (+ poss. ADR-0065) written.

---

#### Step 2.1b-A — Adopt + scaffold + document (M–L) ✓ COMPLETE

**Completed Session 36 (2026-05-20).** Frontend four-layer architecture adopted on branch `m1/01b-fe-conventions`. Generated OpenAPI client relocated to `src/api/generated/` (hand-written config → `src/api/configure.ts`); `@/` alias wired; UI/form stack installed (Tailwind 4, shadcn/ui `radix-lyra` — Button / Input / Card / Field family / Sonner, Zod, react-hook-form, Phosphor, sonner); four-layer folder skeleton + ESLint `no-restricted-imports` layering rules for `features/` + `pages/` (the `routes/` rule deferred to 2.1b-B — the not-yet-ported M1.1 auth routes still import `@/api/generated/` directly); `src/PATTERNS.md` + `frontend/CLAUDE.md` written. **ADR-0064** (four-layer architecture) + **ADR-0065** (UI/form stack) landed; ADR-0063's config-file consequence amended. `pnpm lint` / `typecheck` / `test` / `build` green; M1.1 auth functionally unchanged (import-path edits only). Step 2.1b-B (the auth port) is next.

**Goal:** Lay the substrate M1.2+ builds on and 2.1b-B ports onto — the dependency stack, the four-layer folder skeleton with ESLint enforcement, the relocated generated-client layout, and the conventions docs. Green at close with the M1.1 auth shell still round-tripping (unchanged behavior, new import paths only).

**In scope:**

1. Install + config Tailwind 4 + shadcn/ui (`radix-lyra` style) + Zod + react-hook-form (+ `@hookform/resolvers`) + Phosphor icons + sonner. Install only the shadcn primitives the 2.1b-B auth port consumes (Button, Input, Card, Field family) + Toaster — M1.2 adds more just-in-time.
2. Wire the `@/` import alias (`tsconfig` + Vite).
3. Relocate the openapi-ts output to `src/api/generated/` (update `openapi-ts.config.ts`, regenerate, fix the ~6 M1.1 import sites); move hand-written `api-config.ts` → `src/api/configure.ts` (sibling of the now-isolated generated dir).
4. Scaffold the four-layer folder skeleton (`pages/`, `features/`, `components/`, `hooks/`, `fields/`, `lib/`, `auth/`; `routes/` exists).
5. Add ESLint `no-restricted-imports` layering rules (features / pages / routes), adapted to scank's existing `typescript-eslint` flat config — add rules, do not swap the base config.
6. Write `frontend/src/PATTERNS.md` (adapted from sca-ih-tracker, scoped to what this repo actually has — no entity-abstraction sections yet) + thin auto-loaded `frontend/CLAUDE.md`.
7. ADR-0064 (four-layer FE architecture + API barrel + test/story colocation + ESLint enforcement) + ADR-0065 (shadcn `radix-lyra` + Zod + RHF stack).

**Out of scope:** the M1.1 auth port + test/story colocation (2.1b-B); the whole-step out-of-scope list.

**Decisions to canvass at session head:** shadcn primitive install scope; `src/api/configure.ts` placement (the relocated generated dir reopens the in-`src/api/` option the M1.1 fix commit closed); `@/` alias mechanism (manual Vite alias vs `vite-tsconfig-paths`); ADR-0064/0065 split boundary.

**Done when:** stack installed; `@/` alias resolves; four-layer skeleton + ESLint layering rules in place; generated client at `src/api/generated/`; `PATTERNS.md` + `CLAUDE.md` land; `pnpm lint` / `typecheck` / `test` / `build` green; M1.1 auth still round-trips; ADR-0064 (+ ADR-0065) written.

---

#### Step 2.1b-B — Port M1.1 auth + test/story colocation (M) ✓ COMPLETE

**Completed Session 37 (2026-05-20).** M1.1 auth ported into the four-layer model on branch `m1/01b-fe-conventions`. After a three-point conventions deliberation (resolved in ADR-0066), auth landed as a **single cross-cutting `src/auth/` module** — `api/{index,currentUser}.ts`, `hooks/{useCurrentUser,useLogin,useLogout}.ts`, `components/LoginForm.tsx` (+ colocated `.test.tsx` / `.stories.tsx`) — **no `features/auth/`**. `LoginForm` rebuilt on shadcn `Field` + RHF + Zod; pages `pages/login/` + `pages/admin-shell/`; routes slimmed to config; `<Toaster/>` mounted in `__root.tsx`. Test infra relocated `src/tests/` → `src/test/`. `routes/**` ESLint layering rule added (deferred from 2.1b-A). ADR-0063 preserved exactly. **ADR-0066** landed (auth-as-module + `api/index.ts` barrel + feature subfolder vocabulary); ADR-0064 annotated. `pnpm lint` / `typecheck` / `test` (4/4) / `build` green. Closes Step 2.1b.

**Goal (original):** Move the M1.1 auth code into the four-layer model as the working reference for the conventions 2.1b-A documented, and establish test/story colocation. Structural port only — ADR-0063's cookie-session behavior is preserved exactly.

**In scope:**

1. Restructure the M1.1 auth code into the four-layer model: route files in `routes/` (config only), page compositions in `pages/`, the login feature (`LoginForm` + login/logout API barrel) in `features/auth/`, cross-cutting auth (`useCurrentUser` / `currentUserQueryOptions`, consumed by the route guard) in `src/auth/`.
2. Rebuild `LoginForm` on shadcn + react-hook-form + Zod. **Preserve ADR-0063 exactly:** `setQueryData` (not `invalidateQueries`) on login success; cookie-session model (no Zustand store, no 401 interceptor — both explicitly rejected in ADR-0063); `beforeLoad` + `ensureQueryData` route guard.
3. Test/story colocation: `src/tests/` → `src/test/` (infra only — setup, `renderWithProviders`, `createTestQueryClient`); add the first colocated `*.test.tsx` + `*.stories.tsx` sibling.
4. Amend `PATTERNS.md` if the port surfaces a scank-specific convention wrinkle.

**Out of scope:** everything in 2.1b-A; the whole-step out-of-scope list.

**Decisions to canvass at session head:** the exact four-layer placement of each auth file (`src/auth/` vs `features/auth/` boundary); whether logout is an API-barrel mutation or a cross-cutting helper.

**Done when:** M1.1 auth runs from the four-layer structure; login round-trip verified in a browser; first colocated test + story land; `pnpm lint` / `typecheck` / `test` / `build` green; FF-merge `m1/01b-fe-conventions` → `m1/roster`.

---

### Step 2.2 — M1.2 Admin substrate + flat roster (L, partitioned)

**Partitioned 2026-05-20 (Session 38, Case 2)** into 3 sub-steps. Six of seven fit-checklist signals fired: (1) multiple independently-deliberable decisions — admin-CRUD authoring shape, admin auth-predicate factory, seed-tooling shape; (2) multiple from-scratch artifacts; (3) >60 min; (4) input reading >3 planning files; (5) cross-concern reach — domain entities + authorization + read API + frontend + dev tooling; (6) partial — the seed framework depends on the `create_*` commands existing (an intra-step ordering constraint). Seam: **decision-first** — 2.2a settles the three backend abstractions (admin-CRUD authoring factory, admin auth-predicate factory, seed framework) and proves them against the hardest, most non-uniform entity (Contract); 2.2b applies the settled pattern to the four remaining backend entities; 2.2c builds the frontend admin pages. Commits land sequentially on a single shared branch (1.3a/1.3b + 2.1b-A/B precedent); FF-merge to `m1/roster` after 2.2d.

**Inserted 2026-05-20 (Session 40): Step 2.2b — Backend architecture & conventions.** A backend-structure review found M1.1/M1.2 drifted from the Session-32 hexagonal `app/` design; M1.2 closeout (ADRs + conventions docs) + the structure refactor are packaged as a new inserted sub-step. **Old 2.2b → 2.2c, old 2.2c → 2.2d.** The Session-38 seam description above predates the insertion — current order: 2.2a → 2.2b → 2.2c → 2.2d.

**Re-scoped 2026-05-21 (Session 45) — 2.2c / 2.2d restructured to full-stack entity batching.** Per a user decision, the Session-38 decision-first seam (all backends in 2.2a + 2.2c, all five frontends in 2.2d) is replaced by full-stack batching. Contract — backend complete in 2.2a — gets its frontend as a standalone exemplar slice (**new 2.2c — Contract frontend admin**); the four similar entities (Employee / School / Contractor / User) are built full-stack as one batch (**new 2.2d — roster batch**) so the shared frontend abstractions are designed with all four entity shapes plus Contract's concrete frontend in view, rather than extracted retroactively. Old 2.2c's backend-remainder scope is absorbed into new 2.2d's backend portion. Sub-step count unchanged (2.2a–2.2d); no ADR — a Case 2 re-scope. The Session-38 seam description above is superseded for 2.2c / 2.2d.

**Scope addition — dev seed tooling (Session 38).** Scoped into M1.2 at this Case 2 sizing: a `seed_db` CLI that loads redacted CSVs into the DB **through the Command pipeline** (not direct ORM inserts — keeps seeded data real: invariants run, history + audit-log rows written; avoids a second exception to the every-state-change-is-a-Command rule, since a `Caller` exists post-bootstrap). Pairs with the dropped-in `redact_csv.py` (real data → redacted CSV → seed folder → `seed_db`). **Standing requirement: every entity-adding sub-step from M1.2 onward maintains `seed_db` coverage for the entities it introduces** (applies to M1.3 / M1.4 / M2+). Dev infrastructure, parallel to `bootstrap_admin` — not a roadmap milestone; distinct from M8's production data-import-from-spreadsheets work. Click adoption (ADR-0061's "3rd CLI command" trigger) **deferred** — `seed_db` uses stdlib `argparse` (matches `redact_csv` + `export_openapi`); the real Click trigger is restated as "when a unified `app.cli` subcommand group is wanted," a clean standalone step. `just` recipes split idempotent env-setup (`install` + `alembic upgrade head`) from interactive/destructive data-init (`bootstrap-admin`, `seed`); optional thin `first-run` chains them.

**Goal:** First ADR-0047 Cluster 1 predicate landing in M1+ code; the 5 flat roster entities (Employee, School, Contractor, User-admin-CRUD, Contract) with admin CRUD + read routes; per-entity admin pages; and the dev seed-tooling substrate.

**Sub-step roster:**

| Sub-step | Title | Size | ADRs expected |
|---|---|---|---|
| **2.2a** ✓ | Backend substrate + Contract exemplar (decisions + factories + seed framework) — COMPLETE Session 39 | M–L | M1.2 closeout ADRs deferred to 2.2b-A |
| **2.2b** | Backend architecture & conventions (inserted Session 40) — closeout ADRs + `CLAUDE.md`/`PATTERNS.md` + structure refactor | M–L | ~8 from ADR-0067 (3 abstractions + 5 in-flight decisions + backend-architecture ADR) |
| **2.2c** ✓ | Contract frontend admin — COMPLETE Session 46 | S–M | 0 |
| **2.2d** | Roster batch — Employee / School / Contractor / User, full-stack (re-scoped Session 45; Case 2-partitions at head) | L | 0–1 |

**Execution order:** 2.2a ✓ (Session 39) → 2.2b ✓ (2.2b-A → 2.2b-B → 2.2b-C-1 → 2.2b-C-2) → 2.2c ✓ (Session 46) → 2.2d (roster batch — full-stack; Case 2-partitions at head). Single shared branch `m1/02-flat-roster` off `m1/roster`; FF-merge to `m1/roster` at M1.2 close. Per-entity / per-page checkpoint commits within 2.2c and 2.2d (commit after each entity's additions, not only at sub-step close — per [[preserve-incremental-commits]]).

**Roadmap pointer:** `planning/roadmap.md` § M1.

**Branch:** `m1/02-flat-roster` off `m1/roster`.

---

#### Step 2.2a — Backend substrate + Contract exemplar (M–L) ✓ COMPLETE

**✓ COMPLETE Session 39 (2026-05-20).** The three M1.2 backend abstractions landed on branch `m1/02-flat-roster` (7 commits) and were proven end-to-end against Contract: the `require_role` admin auth-predicate factory; admin-CRUD authoring as hand-authored Command classes over shared `app/framework/crud.py` helpers (the **hybrid** shape — not a generalized class factory); the `seed_db` framework (CSV rows dispatched through the Command pipeline, skip-existing idempotency, JSONB sidecar CSV, seeds at `app/cli/seeds/`). Contract entity + migration `6dd5906ef088` (applied to Neon); `create/edit/delete_contract`; read routes `GET /contracts` + `/contracts/{id}`; production dispatcher wiring + dispatcher-exception→HTTP handlers; `just` recipes (`migrate` / `bootstrap-admin` / `seed` / `first-run`). 71 backend tests + ruff + pyright green; OpenAPI contract + client regenerated. **ADRs deferred to a Session 40 review** of the session's commits (user's call) — three approved abstractions + five in-flight implementation decisions to ratify, then ADRs from **ADR-0067**. Full record: `handoff.md` § Session 39 summary.

**Goal:** Settle M1.2's three backend abstractions and prove them end-to-end against Contract — the most non-uniform of the five entities (JSONB `code_flat_fee_schedule`, derived `validity`). Hardest-first: if the abstractions survive Contract, the remaining four entities are mechanical. The ADRs land here.

**Decisions to canvass at session head (STOP-AND-CONFIRM gate):**
1. **Admin-CRUD authoring shape** — generalized factory (`make_create_command(Entity, Payload)` etc.) vs. hand-authored `Command` per entity. Factory wins on volume (5 entities × 3 commands); hand-authored wins on non-uniform predicates/handlers. ADR-worthy regardless of pick.
2. **Admin auth-predicate factory** — ADR-0047 Cluster 1's class rule is uniform `role >= admin`; encode once as a reusable predicate factory over `has_role_at_least` (ADR-0062) vs. inline per command. Lean factory.
3. **Seed-tooling shape** — through-the-Command-pipeline is locked (Session 38). Open: CSV→Payload mapping mechanism; how a flat CSV represents Contract's JSONB `code_flat_fee_schedule` collection column; entity dependency ordering; idempotency (wipe-and-reload vs. skip-existing); seed-data folder location (default gitignored). ADR-worthy.

**In scope:**
1. The admin auth-predicate factory (consumes `has_role_at_least`, ADR-0062).
2. The admin-CRUD authoring mechanism (factory or hand-authored per decision 1).
3. **Contract** end-to-end backend: entity model (`contract_number`, `name?`, `start_date`, `end_date?`, `code_flat_fee_schedule` JSONB via `json_column()`, derived `validity`; `command_audit_log` history pattern); `create_contract` / `edit_contract` / `delete_contract`; read routes `GET /contracts`, `GET /contracts/{id}`; Alembic migration.
4. The `seed_db` CLI (`app/cli/seed_db.py`, `argparse`, `python -m app.cli.seed_db`) + the seed-data folder convention + `seed_db` coverage for Contract.
5. `just` recipe updates: `install` gains `alembic upgrade head`; new `seed` recipe; optional `first-run` chain.
6. ADRs from **ADR-0067**: admin-CRUD authoring shape; admin predicate factory (possibly folded in); seed-tooling shape.

**Out of scope:** Employee / School / Contractor / User-admin-CRUD (now 2.2c); all frontend (now 2.2d). `redact_csv.py` committed Session 40.

**Inputs:** ADR-0047 (Cluster 1), ADR-0040 (role catalog + grant authority), ADR-0043 / ADR-0044 / ADR-0045 (Contract entity + shape + `code_flat_fee_schedule`), ADR-0061 / ADR-0062 (auth substrate + `Caller` + `has_role_at_least`), ADR-0052 / ADR-0057 (history / audit-log), ADR-0056 (`json_column` / SERIALIZABLE adapter); `data-model.md` § Contract; `app/framework/{command,dispatcher,caller,history,adapter}.py`; `app/domain/auth.py` (entity pattern); `app/cli/bootstrap_admin.py` (CLI + `SessionFactory` pattern); `tests/conftest.py` § per-role fixtures.

**Done when:** the three abstractions exist; Contract CRUD + read routes flow through the dispatcher; `seed_db` loads a Contract CSV through `create_contract`; `just` recipes updated; backend tests + ruff green; migration applied to Neon per [[project-neon-current-policy]]; ADRs written.

---

#### Step 2.2b — Backend architecture & conventions (M–L, inserted) ✓ COMPLETE

**Inserted 2026-05-20 (Session 40)** — an insertion, not a milestone sub-step; the backend twin of Step 2.1b. A Session 40 backend-structure review found M1.1/M1.2 drifted from the Session-32 hexagonal `app/` design (`planning/follow-ups/backend-directory-structure-rewind.md`): `domain/` landed flat with a `domain/commands/` type-bucket instead of per-entity folders; `adapters/` was left empty while concrete-I/O code piled into `framework/`; route files carry transport DTOs + cookie helpers. **Renumbered:** old 2.2b → 2.2c, old 2.2c → 2.2d.

**Goal:** Settle the backend architecture, write the deferred M1.2 closeout ADRs, produce `backend/CLAUDE.md` + `backend/app/PATTERNS.md` (the backend twin of the frontend pair), and refactor the existing code onto the settled structure — so 2.2c builds its four entities on it.

**Architecture settled — Session 41 / ADR-0070** (do not re-deliberate): the backend moved from hexagonal horizontal layers to **vertical feature slices over a shared command engine** — `framework/` (engine) + `adapters/` (shared concrete I/O) + `auth/` (top-level identity module) + `features/<entity>/` (per-entity slices; submodules file-or-package with uniform import paths). Route DTOs stay separate from command `Payload`s. This reversed the Session-32/40 hexagonal direction; the rewind follow-up doc is annotated superseded. **ADR-0067–0074** record the full M1.2 closeout — admin-CRUD authoring, `require_role` factory, `seed_db`, backend architecture, uniqueness pre-check, uniform audit-metadata columns, `EntityNotFound`→404, Cluster 1 → Contract.

**Partitioned into 2.2b-A / 2.2b-B / 2.2b-C** — original 2.2b-A further split 2026-05-20 (Session 41, Case 2; 5 of 7 fit signals — multiple deliberable decisions, 2 from-scratch docs, >60 min, input reading, cross-concern). Seam: architecture deliberation (structure forks + ADRs, 2.2b-A) vs. conventions-doc authoring (2.2b-B); old 2.2b-B refactor → 2.2b-C. Single shared branch `m1/02-flat-roster`; commits land sequentially (1.3a/1.3b + 2.1b-A/B precedent). **2.2b-C itself further partitioned 2026-05-20 (Session 43, Case 2)** into 2.2b-C-1 (structure refactor) / 2.2b-C-2 (audit-column materialization) — see that sub-step's partition note.

##### Step 2.2b-A — Structure forks + M1.2 ADRs (M–L) ✓ COMPLETE

**✓ COMPLETE 2026-05-20 (Session 41).** The structure forks reopened the topology itself — settled (ADR-0070) as a reversal from hexagonal horizontal layers to **vertical feature slices over a shared command engine**. Wrote **ADR-0067–0074** (M1.2 closeout). Also created `planning/DRIFTS.md` (drift registry, seeded `DRIFT-001` — parallel-definition drift) and added a drift-logging pointer to `_workflow.md`. Planning/ADR work only — no conventions docs (2.2b-B), no code refactor (2.2b-C).

**Split out 2026-05-20 (Session 41, Case 2)** from the original 2.2b-A — 5 of 7 fit signals fired. Seam: architecture deliberation here; conventions-doc authoring → the new 2.2b-B.

**Goal:** Settle the open structure forks and write all deferred M1.2 ADRs from ADR-0067. Planning only — no conventions docs (→ 2.2b-B), no code refactor (→ 2.2b-C).

**In scope:** (1) settle the four structure forks (STOP-AND-CONFIRM canvass); (2) write the M1.2 ADRs — three Session-39 approved abstractions + five ratified in-flight decisions + a backend-architecture ADR (twin of ADR-0064).

**Inputs:** `handoff.md` § Session 40 summary + § Open questions "For Step 2.2b-A"; `planning/follow-ups/backend-directory-structure-rewind.md`; the Session 39 commits (`git log origin/m1/roster..HEAD`); ADR-0064 (ADR model).

**Done when:** structure forks settled; M1.2 ADRs written from ADR-0067.

##### Step 2.2b-B — Backend conventions docs (M) ✓ COMPLETE

**✓ COMPLETE 2026-05-20 (Session 42).** Wrote `backend/CLAUDE.md` (thin, auto-loaded pointer) + `backend/app/PATTERNS.md` (the authoritative conventions doc, 13 sections) synthesizing ADR-0067–0074 into prescriptive backend conventions — the ADR-0070 vertical-slice architecture + dependency rule, the slice submodule vocabulary, the `Command` contract surface + `crud.py` helpers + PascalCase naming, the `require_role` factory, the uniqueness pre-check, audit-metadata columns, the exception→HTTP table, route DTOs vs `Payload`s, seeding, migrations, testing. Modeled on the `frontend/CLAUDE.md` + `frontend/src/PATTERNS.md` pair; `PATTERNS.md` written as Option B (a complete slice-authoring guide — restates the `Command` contract surface, points at M0 ADRs for engine internals). Case 2 check ran at head — no signal fired decisively, one session. `PATTERNS.md` describes the ADR-0070 *target* (the code keeps the M1.1/M1.2 layout until 2.2b-C). Documentation only — no application code, no ADRs; plus a wrap-up tooling fix at the user's request — backend `pyright` wired into `just typecheck` / `just ci` via a new `typecheck-backend` recipe (verified green).

**Split out 2026-05-20 (Session 41, Case 2)** from the original 2.2b-A — the conventions-doc authoring half of the seam.

**Goal:** Produce `backend/CLAUDE.md` (thin, auto-loaded) + `backend/app/PATTERNS.md` (the conventions doc 2.2c+ consumes), synthesizing 2.2b-A's settled ADRs into prescriptive conventions. Modeled on the frontend `CLAUDE.md` + `src/PATTERNS.md` pair.

**In scope:** `backend/CLAUDE.md` + `backend/app/PATTERNS.md`. Documentation only — no code refactor (→ 2.2b-C).

**Inputs:** 2.2b-A's ADRs (esp. the backend-architecture ADR); `frontend/CLAUDE.md` + `frontend/src/PATTERNS.md` + ADR-0064 (doc model); the Session 39 backend code.

**Done when:** `backend/CLAUDE.md` + `backend/app/PATTERNS.md` land.

##### Step 2.2b-C — Backend structure refactor + audit columns (Case 2 → partitioned) ✓ COMPLETE

**Partitioned 2026-05-20 (Session 43, Case 2)** into 2.2b-C-1 / 2.2b-C-2. The mandated session-head 7-signal check fired three signals: signal 3 (duration — structure refactor ~50–70 min + audit-column materialization ~30–45 min; combined 90–120 min), signal 4 (input reading — a behaviour-preserving refactor holds the whole `app/` tree, >1000 LOC, in context), signal 5 (cross-concern — code topology vs. dispatcher pipeline behaviour). Signals 1/2/6/7 did not fire: the structure is fully settled by ADR-0070 (mechanical, no open structural decision), the lone genuine decision is the audit create-vs-update signal, all inputs exist, scope is well-specified. Seam: **structure refactor vs. audit-column materialization** — the seam this step brief pre-identified. Order is forced — refactor first, so the audit-column work lands on the target layout rather than being moved twice. Single shared branch `m1/02-flat-roster`; commits land sequentially (1.3a/1.3b + 2.1b-A/B + 2.2b-A/B precedent).

###### Step 2.2b-C-1 — Backend structure refactor (M) ✓ COMPLETE

**✓ COMPLETE 2026-05-20 (Session 43).** Four staged commits on `m1/02-flat-roster` (`938405a` → `f1dd91d`), each behaviour-preserving and green: (1) `adapters/` extraction — `db` / `postgres` (←`adapter`) / `history` + the concrete `SqlAlchemyCaptureSink` split out of `framework/capture.py`; the `framework → adapters` dependency the move would create resolved by injecting `set_isolation` / `try_advisory_lock` into `Dispatcher.__init__`, wired by `runtime.build_dispatcher` (extends ADR-0059; no new ADR); (2) `auth/` identity module — `entities` / `security` / `routes` / `schemas`; (3) `features/contracts/` slice — `entities` / `commands` / `routes` / `schemas` / `queries`; `predicates.py` → `framework/`; `app/domain/` removed; (4) `runtime.py` + `error_handlers.py` + `health.py` hoisted to `app/` root, `routes/` removed. `app/` now matches ADR-0070; `framework/` imports nothing outward (audited). 71 tests + ruff + pyright green. OpenAPI contract + client regenerated — structurally byte-identical; the sole delta is the `Caller` model's `description` string, propagated from a corrected docstring path. No migration; no ADR.

**Goal:** Execute ADR-0070 against the existing backend code — a behaviour-preserving move of the M1.1/M1.2 layout onto the vertical-slice structure. No new behaviour; no ADR.

**In scope:** reorganize `app/` into `framework/` + `adapters/` + `auth/` + `features/contracts/`; move concrete I/O out of `framework/` into `adapters/` (`db.py`, `adapter.py`, `history.py`); split `capture.py` — the `CaptureSink` port + record types stay in `framework/`, the concrete `SqlAlchemyCaptureSink` → `adapters/`; consolidate auth (`framework/auth.py` + `domain/auth.py` + `routes/auth.py`) into `app/auth/`; turn `domain/contract.py` + `domain/commands/contract.py` + `routes/contracts.py` into a `features/contracts/` slice (`entities` / `commands` / `routes` / `schemas` / `queries` — extract route DTOs into `schemas`, read-query logic into `queries`); `framework/crud.py` + `framework/predicates.py` (currently `domain/predicates.py`) stay in `framework/` per ADR-0070; hoist `runtime.py` + `error_handlers.py` to `app/` root; update every import, the command registry, the tests, `migrations/env.py`, and the OpenAPI export.

**Out of scope:** the audit-column materialization (2.2b-C-2); any behaviour change.

**Done when:** backend runs on the ADR-0070 structure; backend tests + ruff + pyright green; OpenAPI contract + client regenerated (no surface change expected — a behaviour-preserving refactor); no migration (no schema change).

###### Step 2.2b-C-2 — Audit-column materialization (S–M) ✓ COMPLETE

**✓ COMPLETE 2026-05-21 (Session 44).** ADR-0072's four audit-metadata columns materialized on Contract + User via `AuditMetadataMixin` (new `app/framework/audit.py`); Alembic migration `162ac1ebc916` applied to Neon — the one bootstrap-superadmin row backfilled from `UserRole.granted_at` + self-id. The create-vs-update signal resolved as **ADR-0075** — a declared `Command.creates` flag over ORM-state introspection; the dispatcher's stamping step writes `created_*` on creating commands and `updated_*` on every command (so `created_* == updated_*` at creation — a deliberate refinement of ADR-0072 that lets all four columns be `NOT NULL`). `ContractRead` surfaces the columns; OpenAPI contract + client regenerated. `bootstrap_admin` stamps the columns itself (it bypasses the dispatcher). 75 tests + ruff + pyright green. Two checkpoint commits on `m1/02-flat-roster`. Closes Step 2.2b-C and the inserted Step 2.2b.

**Goal:** Materialize ADR-0072's `created_*/updated_*` audit-metadata columns on Contract + User, on the post-2.2b-C-1 vertical-slice structure.

**In scope:** add `created_at` / `created_by` / `updated_at` / `updated_by` to Contract + User; an Alembic migration; a dispatcher stamping step (`created_*` on the creating command, `updated_*` on every later mutating command) + a create-vs-update signal; read-schema fields; migration applied to Neon; OpenAPI contract + client regenerated.

**ADR note:** the create-vs-update signal is the lone genuine open decision — likely **ADR-0075** if it is non-obvious. The behaviour-preserving 2.2b-C-1 carries no ADR.

**Done when:** Contract + User carry the four columns; reads surface them; the dispatcher stamps them; backend tests + ruff + pyright green; migration applied to Neon; OpenAPI regenerated.

---

#### Step 2.2c — Contract frontend admin (S–M) ✓ COMPLETE

**✓ COMPLETE 2026-05-21 (Session 46).** Contract's admin frontend landed on branch `m1/02-flat-roster` as a `features/contracts/` slice — `api/index.ts` barrel, `form.ts` (Zod schema + form↔API mappers), three mutation hooks, five components (`ContractsTable`, `ContractForm`, the bespoke `FeeScheduleEditor` JSONB editor, `ValidityBadge`, `DeleteContractDialog`) with colocated tests + stories — plus list/create/edit pages, routes, and `lib/apiError.ts`. The admin shell was promoted from a placeholder page to a layout (header + left sidebar nav); `pages/dashboard` added. shadcn `table` / `badge` / `alert-dialog` vendored. Two mid-session structural corrections on user pushback: pages regrouped to nested `pages/<entity>/<page>/` (`PATTERNS.md` amended — a refinement within ADR-0064, no new ADR), and the assumed `_authenticated/...` route scheme flagged as wrong-road (an `/admin/`-prefixed shape is a logged follow-up). `pnpm typecheck` / `lint` / `test` (13/13) / `build` green; API client regenerated (no drift). No ADR. **Browser create/edit/delete dogfood was blocked by a pre-existing backend bug** — `set_serializable_isolation` altered `isolation_level` after the connection's transaction had autobegun; PG-only, never caught by the SQLite test suite. Fixed in Session 47 (a dedicated debug session; ADR-0076 corrects ADR-0058's mechanism); the 2.2c create/edit/delete browser dogfood then passed, closing this step's Done-when.

**Re-scoped 2026-05-21 (Session 45)** from "Backend remainder" to Contract's frontend slice — see the Step 2.2 header re-scope note. Contract's backend (CRUD + read routes) landed in 2.2a; this wires its admin frontend.

**Goal:** Wire Contract's admin frontend — list/overview, create, edit pages + admin-shell nav — on the Step 2.1b four-layer + shadcn/RHF/Zod conventions. First frontend feature consumer in M1.2; establishes the exemplar layout the 2.2d roster batch templates from.

**Layout-approval gate (heavyweight here):** before implementation, surface page inventory + an ASCII wireframe per page + information architecture + interaction flow in chat; wait for explicit approval. This review sets the pattern all five roster entities follow. Per `handoff.md` § Process notes — Frontend layout-approval gate.

**In scope:**
1. `src/features/contracts/` feature slice with an `api/index.ts` barrel over the regenerated client.
2. List/overview, create, and edit pages in `pages/`; route config in `routes/`.
3. Admin-shell nav entry for Contracts.
4. The bespoke `code_flat_fee_schedule` JSONB editor (Contract-specific — does not generalize).
5. Colocated tests + stories.

Built **concrete** — no shared `EntityListPage` / `useEntityForm` abstractions yet; those are designed in 2.2d with all four roster entities plus this concrete Contract frontend in view.

**Out of scope:** any backend; the four roster entities (2.2d); the queued theme-toggle follow-up.

**Commit cadence:** per-page checkpoint commit.

**Inputs:** `frontend/src/PATTERNS.md`; ADR-0064 / ADR-0065 / ADR-0066; 2.2a's Contract read + CRUD routes (regenerate the client via `pnpm gen-api`); `frontend/src/auth/` (the working four-layer reference); Contract's OpenAPI surface (`ContractRead` etc.).

**Done when:** Contract admin pages list + create/edit/delete through the backend; nav wired; `pnpm lint` / `typecheck` / `test` / `build` green; the exemplar layout is approved.

---

#### Step 2.2d — Roster batch: Employee / School / Contractor / User, full-stack (L)

**Re-scoped 2026-05-21 (Session 45)** from "Frontend admin pages (5 entities)" to a full-stack batch of the four similar roster entities — see the Step 2.2 header re-scope note. Absorbs old 2.2c's backend-remainder scope.

**Goal:** The four similar roster entities — Employee, School, Contractor, User-admin-CRUD — built full-stack as one batch: backends (consuming 2.2a's settled factory + `crud.py` helpers) and frontends, with the shared frontend abstractions (`EntityListPage` / `DataTable` / `useEntityForm` / comboboxes) designed at the batch head with all four entity shapes plus Contract's concrete 2.2c frontend in view — not extracted retroactively.

**Case 2 check mandatory at session head:** four entities × full-stack is L — expect a partition (likely 4-entity backend → shared-component design → 4-entity frontend). "Batch" is the design/scoping unit; implementation spans multiple sessions. Cross-check `architecture.md`'s out-of-band concerns per [[check-out-of-band-concerns]].

**In scope — backend portion** (absorbed from old 2.2c):
1. **Employee** — `name` + HR attrs; `command_audit_log`; CRUD + read routes. Migration adds the Employee table **and** the `User.employee_id` FK + UNIQUE constraint (ADR-0061 carry-forward; the bootstrap superadmin's null `employee_id` is the nullable-FK shape ADR-0041 Gap 5 anticipates).
2. **School** — `name` + identifying attrs; `no history`; CRUD + read routes.
3. **Contractor** — `name` + roster attrs; `command_audit_log`; CRUD + read routes.
4. **User-admin-CRUD** — admin CRUD on User beyond M1.1's bootstrap insert: `create_user`, `edit_user` (password reset via `hash_password`; `employee_id` link), `delete_user` per delete policy. All under ADR-0047 Cluster 1's `role >= admin` class rule.
5. `seed_db` coverage for all four entities.
6. Alembic migration(s) for the four tables + the `User.employee_id` alter.

Each new entity is born with `AuditMetadataMixin` + a `creates`-flagged create command (ADR-0072 / ADR-0075); extract the shared `require_unique` helper from Contract's `_require_unique_number` once User's `username` is the second consumer (ADR-0071).

**In scope — frontend portion:**
7. Shared frontend abstractions designed at the batch head with all four entities + the Contract exemplar in view (resolves ADR-0064's "extract at the second consumer" deferral).
8. Decide: retrofit Contract's generic frontend parts onto the shared components, or leave Contract standalone.
9. List + create + edit pages for the four entities; admin-shell nav entries; per-feature `api/index.ts` barrels over the regenerated client; colocated tests + stories. Per-page layout-approval as deltas off the Contract exemplar (per `handoff.md` § Process notes).

**Out of scope:** anything in 2.2a / 2.2b / 2.2c's scope; the queued theme-toggle follow-up.

**Commit cadence:** per-entity checkpoint commit — commit after each entity's additions land green, not only at sub-step close ([[preserve-incremental-commits]]).

**Inputs:** 2.2a outputs (the settled factory + predicate factory + seed framework); 2.2c's Contract frontend (the exemplar); `data-model.md` § Employee / School / Contractor / User; ADR-0047 Cluster 1; ADR-0061 § `user.employee_id` carry-forward; ADR-0064 / ADR-0065 / ADR-0066; `frontend/src/PATTERNS.md`; `app/auth/` (User model) + `app/features/contracts/` (the backend slice reference).

**Done when:** four entities full-stack — backend CRUD + read routes + seed coverage on the settled pattern, plus frontend admin pages — work through the dispatcher and through the browser; the `User.employee_id` FK/UNIQUE is migrated; the shared frontend abstractions are extracted; backend tests + ruff + pyright green; `pnpm lint` / `typecheck` / `test` / `build` green; migration(s) applied to Neon; FF-merge `m1/02-flat-roster` → `m1/roster` (closes Step 2.2 / M1.2; Step 2.3 / M1.3 next).

---

### Step 2.3 — M1.3 Role administration (S–M)

**Brief:** UserRole entity + `grant_user_role` / `revoke_user_role` commands with conservative grant authority parameterized predicate per ADR-0040. `audit_reason` Note materialization mechanism (Note polymorphism extension to history records per ADR-0040 — concrete implementation deferred from ADR-0040; ADR-worthy). Frontend: role-management UI (grant/revoke flows with optional reason text input).

**Roadmap pointer:** `planning/roadmap.md` § M1.

**Branch:** `m1/03-role-admin` off `m1/roster`.

---

### Step 2.4 — M1.4 Range-typed entities (M, possibly L)

**Brief:** EmployeeRole + ContractorEngagement entities. EmployeeRole `(employee, role_type, contract_id, rate, start_date, end_date?)` with disjoint-ranges-per-`(employee, role_type, contract)` invariant under SERIALIZABLE (first ADR-0056 D1.c consumer in M1+ code; record as code-comment criterion-application referencing ADR-0056 — no new ADR). Lifecycle commands: `create_employee_role`, `edit_employee_role`, `close_employee_role`, `start_contractor_engagement`, `end_contractor_engagement`. `change_employee_role_rate` 4-branch compound (signature includes `contract` per ADR-0045; auto-reparent branch stays dissolved since Time Entry doesn't exist until M4 — branches 1/2/4 fully functional; branch 3 reduces to close+create). ContractorEngagement signatures + date defaults (carry-forward landing per `planning/roadmap.md` § Carry-forward landing index). Frontend: EmployeeRole rate-management UI + ContractorEngagement UI.

**Roadmap pointer:** `planning/roadmap.md` § M1.

**Branch:** `m1/04-range-typed` off `m1/roster`.

---

## Step 3 — M2 Contract + Project + WABundle (M)

**Brief:** Build Contract (audit-log capture, derived validity, `code_flat_fee_schedule`), Project, WABundle, WABundleSite. `create_project` compound (Project + WABundle + sites + v0 pending WA atomically per ADR-0044 + ADR-0048). `edit_wabundle` admin-only with site-mgmt guards (ADR-0048). Project-state-driven immutability substrate (pattern #13 — applied in Step 7 / M6). Coordinator project-tracking dashboard skeleton.

**Roadmap pointer:** `planning/roadmap.md` § M2.

---

## Step 4 — M3 WA + WA Code + RFA cycle (L)

**Brief:** The largest state-machinery step. WA versioning (`version_seq`), WA Code with `level` + `school_id?` + bundle-sites invariant, WACodeAssignment (WACA), WACodeConf code-side static config. Generalized `issue_wa` (initial in-place v0 + SCA-direct branch + hard-gate). `dismiss_wa_code(reason_text?)` narrowed + cascade-keep-FK + cascade `write_off` Notes (ADR-0048 + ADR-0049). `removed` terminal cascade. RFA state machine + hybrid line items (`add` system-derived; `remove` via `add_rfa_line_item`). `approve_rfa` composition `(prior ∪ adds) \ removes` with polymorphic per-line-item resolution. Auto-draft regeneration + cancelled-project suppression. `reassign_wa_project` + school-subset guard + deeper mechanics (carry-forward). Revoke-line-item command (carry-forward). Smart-command-inference landing state (carry-forward).

**Roadmap pointer:** `planning/roadmap.md` § M3.

---

## Step 5 — M4 Time Entry + Sample Batch (M)

**Brief:** Time Entry self-describing schema (no `employee_role_id` FK; derived/validated lookup per ADR-0041 + ADR-0045). On-site/off-site invariants. Cross-project overlap predicate substrate (consumed by Step 7 / M6 blocker #8). Sample Batch (stateless per ADR-0038; lifecycle capture only). Derived COC + Lab Report Document scaffolding (full per-`document_type` dispatch lands in Step 6 / M5). `relink_sample_batch_wa_code` per ADR-0049 restatement.

**Roadmap pointer:** `planning/roadmap.md` § M4.

---

## Step 6 — M5 Documents + Deliverables + DepFilings (L)

**Brief:** Document single-scope via `(scope_type, scope_id)`. Per-`document_type` lifecycle dispatch (simple / cycling-family / bespoke per ADR-0024). 12 MVP document types (ACP{7,8,13,15,21}, VAR9, Emergency Notification, COC, Daily Log, CPR, FAMR, Lab Report, RFP). Deliverable + bundle query + lifecycle commands. DepFiling + TRU + editable `required_doc_types`. Document derivation rules (Deliverable, DepFiling, Sample Batch, Project). File storage adapter (architecture.md out-of-band; storage backend TBD — local vs S3-equivalent).

**Roadmap pointer:** `planning/roadmap.md` § M5.

---

## Step 7 — M6 Closure gate + blockers + write-off + project lifecycle terminals (L)

**Brief:** The hard-mechanics step. 10-entry registry implementation per ADR-0053. Predicate evaluation over not-written-off entities. Lazy materialization. Immutable Note subtypes (blocker / resolution / audit_reason / write_off). `default_resolve` generic + named compounds (`resolve_open_rfa`, `resolve_overlap`). Chain shape `te_batches_by_coverage` (entries #5, #8, #11, #12). `comment_blocker`, `dismiss_blocker`. `close_project` compound. `cancel_project` cascade. `reopen_project` both forms. Project-state-driven immutability rule applied (pattern #13). `revoke_write_off` (carry-forward). `split_entry` (carry-forward — load-bearing for #8). `resolve_overlap_paired` (carve-out — ships if `split_entry` mechanics land, else slips per ADR-0050). ADR-0031 auto-draft regeneration suppression at closure-gate (carry-forward).

**Roadmap pointer:** `planning/roadmap.md` § M6.

---

## Step 8 — M7 Reads + reporting (M)

**Brief:** Read APIs / query views. Audit-log UI (audit_reason Notes inline). Auditor dashboard (read-only with simple filters per ADR-0040). Project-status views. Closure-readiness panel (the unresolved-blocker batch surface). Draft-invoice estimator per ADR-0038 — reads `EmployeeRole.rate` via `(employee, role_type, contract, date)` lookup; reads `Contract.code_flat_fee_schedule[wa_code.code_type]`; aggregates over Time Entries + Sample Batches; unpriced surfacing for missing schedule entries (ADR-0045).

**Roadmap pointer:** `planning/roadmap.md` § M7.

---

## Step 9 — M8 Cutover prep + hardening (S–M)

**Brief:** Data import from current spreadsheets + SCA-portal exports. Error-path hardening. Office training. Cutover plan. First real project in the tool. Placeholder for post-MVP capture (stale-RFP signal etc. — tracked, not built).

**Roadmap pointer:** `planning/roadmap.md` § M8.

---

## Carry-forward landing index

See `planning/roadmap.md` § Carry-forward landing index for the full index. Summary:

- **M0 (Step 1):** Stale-scaffolding cleanup; PaaS vendor pick + Postgres offering; `Command` base class + dispatcher; per-invariant isolation primitives; audit-log write timing.
- **M1 (Step 2):** ContractorEngagement signatures + date defaults.
- **M3 (Step 4):** `reassign_wa_project` deeper mechanics; revoke-line-item command; smart-command-inference landing state.
- **M6 (Step 7):** `split_entry`; `revoke_write_off`; ADR-0031 auto-draft regeneration suppression at closure-gate; `resolve_overlap_paired` (conditional carve-out).
