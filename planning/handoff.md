# Handoff

## File contract

**Holds:** Transient state between Claude Code contexts — current phase pointer, last session summary, next session pointer and prompt, open questions, and pointers to all other planning files. Session execution rules live in `planning/sessions.md`; restructure log lives there too.
**Update when:** A session completes or wraps up (advance next-session pointer, summarize last session, refresh open questions, rewrite prompt); a phase changes; the step list in `steps.md` is restructured. Full protocol in `planning/_workflow.md` (Case 3, completion protocol).

The single source of truth between sessions. Read this first.

---

# **STOP-AND-CONFIRM GATE — READ BEFORE WRITING ANYTHING**

> **Every session starts in chat, not in a file. Surface the decisions; wait for explicit approval; then write.**
>
> For each decision on the table, deliver in chat (≤150 words each):
>
> - The fork(s) actually on the table
> - 2–3 candidate positions, each with **what it buys** and **what it gives up**
> - What it depends on or defers to
> - **Your recommendation, labeled as such, with reasoning.** Chime in on which option looks stronger and call out specific options to avoid. Per `CLAUDE.md`'s base rule: if you think an option is bad, say so and explain why. Recommendations do not pre-decide — the user retains the position.
>
> **Do NOT write ADRs. Do NOT modify any planning file (or any other file) in the proposal turn.** Wait for the user's explicit `approved` (or amendments) before touching files. If you're unsure whether something counts as a file modification, ask.
>
> If two decisions are genuinely inseparable, say so and explain why — but default to splitting. Roadmap length is not a constraint; splitting a session into more sessions is preferred over rushing a decision.
>
> **This gate exists because prior sessions (twice on 2026-04-28) stacked or pre-answered decisions by writing the answer into a file before agreement.** "The artifact is the deliberation" (rule 1 in `planning/sessions.md`) means the doc canvasses options before landing — it does **not** mean writing first and asking later. The gate is on **writes** (ADRs, planning files), not on **opinions**. Agreement on the position is gated on the chat-side proposal; the doc then writes it up.
>
> **Gate applies to source code too.** Phase 2's surface includes implementation files; the "writes vs. opinions" framing covers source files. Non-trivial structural code decisions and ADR proposals earn a chat-side canvass before the write.

---

## How to start a session

If the user says something like _"resume work"_ / _"start the next session"_ / _"run the next session"_ / _"do the next session block"_ / _"vamos"_ / _"yallah"_: follow `planning/_workflow.md`. That file owns the case-detection logic and the completion protocol.

---

## Current phase

**Implementation** — Phase 2. The 9-milestone roadmap from `planning/roadmap.md` (M0 Foundations → M8 Cutover prep) is the canonical milestone-shape source; `planning/steps.md` mirrors the milestones as 9 steps. **Step 1 (M0) partitioned 2026-05-17 into 5 sub-steps; collapsed 2026-05-18 to 4 sub-steps** when the original Step 1.2 (PaaS vendor pick) resolved as a deferral per ADR-0055 (Session 28). **Step 1.3 further partitioned 2026-05-18 (Session 30, Case 2)** into two sub-sub-steps on a single branch: **1.3a Dispatcher pipeline** (M) and **1.3b History infrastructure** (M). **Step 1.1 / M0.1 Scaffolding ✓ COMPLETE 2026-05-18** (Session 27). **Original Step 1.2 closed via deferral 2026-05-18** (Session 28). **Step 1.2 / M0.2 Data-layer primitives ✓ COMPLETE 2026-05-18** (Session 29 — ADR-0056 + ADR-0057 landed; `m0/02-data-layer-primitives` FF-merged into `m0/foundations`). **Step 1.3a / M0.3 Dispatcher pipeline ✓ COMPLETE 2026-05-18** (Session 30 — ADR-0058 + ADR-0059 + ADR-0060 landed; commits accumulate on `m0/03-dispatcher-and-history`; FF-merge into `m0/foundations` happens after 1.3b lands). Currently on the **`m0/03-dispatcher-and-history`** branch (tip = Session 30 handoff close-out).

## Last session summary

**Session 30 — Step 1.3a / M0.3 Dispatcher pipeline ✓ COMPLETE (2026-05-18).** Case-3 scoped session. Step 1.3 partitioned at session head into 1.3a (dispatcher pipeline) + 1.3b (history infrastructure) on a single branch per Case 2 fit-checklist (5 of 7 signals fired). Three rounds of STOP-AND-CONFIRM canvasses (A: retry boundary + Command shape; B: cascade mechanism + capture-sink shape; C: engine isolation placement + lock-key namespace + smoke-test location). 8 commits on `m0/03-dispatcher-and-history` (1 partition + 7 implementation/wrap); 3 ADRs landed (0058, 0059, 0060). 11 pytest tests passing; ruff + pyright both clean. Framework spine in place; 1.3b will replace the in-memory capture-sink stub with real SQLAlchemy-backed INSERTs into per-entity history tables + `command_audit_log`.

**Round-by-round substance.**

- **Round A — Retry boundary + Command shape.**
  - **A1 — Dispatcher built-in retry loop (ADR-0058).** Dispatcher owns the retry loop for both contention modes (advisory-lock fast-fail + Postgres `serialization_failure`). MAX_ATTEMPTS=3 with exponential jittered backoff (~100ms total budget); WARN log on every retry so hidden retries cannot hide bugs; `TransientContention` surfaced on exhaustion. Auth/lifecycle/invariant rejections propagate unwrapped (deterministic, not transient). Per-transaction SERIALIZABLE isolation set dispatcher-level (not engine-level) per ADR-0010 write-path-only scope.
  - **A2 — Plain class + nested Pydantic Payload + explicit registry (ADR-0059).** Rejected Pydantic-as-command (value-shape/behavior-shape mixing; ClassVar footgun) and function+decorator (cascade ergonomics; introspection loss; test-registry leakage). Authoring shape: `class FooCommand(Command):` with class-level metadata (`target_entity`, `transition_name`, `authorization`, `invariants`, `cascade`, `destructive`, `cascade_allowed_destructive`); nested `Payload` Pydantic model; `handler(self, session, payload) -> entity` method; `register(FooCommand)` after class definition.
  - **WET-code clarification (logged in ADR-0058 § Alternatives).** User asked whether two dispatch functions (serializable vs. non-serializable) would scope the SERIALIZABLE setting per-command. Pushed back: every command is write-path per ADR-0010 and runs under SERIALIZABLE uniformly; there is no "non-serializable command" category. Per-command differentiation already exists at the invariant-primitive level (ADR-0056 advisory-lock opt-in declared on the invariant attached to the command). One dispatch function; one place sets SERIALIZABLE.

- **Round B — Cascade mechanism + capture-sink shape.**
  - **B1 — Mechanism #1 (context flag + skip auth) + 3 safeguards (ADR-0060).** Rejected mechanism #2 (always-true predicate just relocates the bypass) and mechanism #3 (token-based machinery doesn't change the dominant failure mode at this trust boundary). Three structural safeguards: **(G1) Runtime guard** — `cascade_invoke()` enforces child ∈ parent.cascade list at call time (CascadeViolation otherwise); the wrong invocation is impossible at runtime. **(G2) Registry-load-time check** — `validate_registry()` raises DestructiveCascadeViolation at app startup if a destructive child appears in a parent's cascade list without explicit `cascade_allowed_destructive=True` on the parent. **(G3) Static AST drift inspector** — `extract_handler_cascade_invocations()` + `cascade_drift_report()` compare declared vs. invoked per command at test time. Per-child cascade allowlist deferred to post-MVP if cascade declaration surface outgrows PR review.
  - **B2 — Single `emit(record)` with typed union; constructor-injected sink; In-Memory + Null stubs (no ADR; code-level).** Dispatcher constructs the right variant (`ComprehensiveRecord | LifecycleRecord | AuditLogRecord`) based on the target entity's declared `history_pattern` class attr; sink impl pattern-matches on variant. 1.3a ships InMemorySink (tests inspect `.records`) and NullSink (no-op). 1.3b replaces with real SQLAlchemy-backed sink.

- **Round C — Engine isolation + lock-key + smoke-test location.**
  - **C1 — Dispatcher-level SERIALIZABLE via `connection.execution_options` (no ADR; implements ADR-0056).** Set per-transaction inside `_run_pipeline` after session open; dialect-aware (no-op on SQLite). Reads / scripts / health checks via the same engine inherit default isolation. `.env.example` documents Neon dev default + SQLite offline fallback per ADR-0051. `app/framework/db.py` is the new engine-wiring module.
  - **C2 — `hashtextextended` + `LockNamespace` enum + per-namespace key-builders (no ADR; implements ADR-0056).** Rejected `hashtext` (32-bit entropy, sign-extended — lossy) and two-int4 signature (no collision-resistance gain). Namespace discipline: `LockNamespace.CLOSURE_READINESS` is the first entry; per-namespace key-builders (`closure_readiness_key`) live in `app/framework/locks.py`. Runtime validator rejects un-namespaced keys.
  - **C3 — Smoke-test fakes under `backend/tests/fixtures/smoketest/` per Q2 user decision (clean production surface; fakes never ship).** Two entities (SmokeEntity comprehensive, SmokeLifecycleEntity lifecycle) + 6 commands exercising create / edit / non-lifecycle-on-lifecycle-entity / lifecycle-transition / auth-denied paths. `tests/test_dispatcher.py` runs 10 end-to-end pipeline tests against in-memory SQLite + InMemorySink.

**Mid-session pyright surprise (logged for follow-up).** Two attempts to commit Task 7 (dispatcher) caught Pylance/Pyright errors that ruff did not — first on `Command` attribute assignments (`command._session = session` etc.) because the attrs weren't declared on the class; second on `FakeCaller` not satisfying the `Caller` Protocol because frozen-dataclass `id` is read-only but the Protocol declared `id` as writable. Resolved by (a) declaring `_session/_command_id/_caller/_dispatcher` as instance attrs with None defaults on Command (with TYPE_CHECKING import for the Dispatcher forward ref); (b) changing Caller Protocol's `id` to a read-only `@property`. **Process gap surfaced:** the project has no static-type-check gate — Pylance runs only in the user's editor. Should add pyright to dev deps + a `[tool.pyright]` config so CI fails on type errors the way it does on ruff. Queued as a follow-up before next session (see Open questions).

**Commits landed on `m0/03-dispatcher-and-history`:**
1. `048845c` M0.3: partition Step 1.3 into 1.3a (dispatcher pipeline) + 1.3b (history infrastructure) — `planning/steps.md` (~79 lines added).
2. `c553672` M0.3 / Step 1.3a: DB engine + session wiring + SQLite test fixture — new `app/framework/db.py`, `.env.example`, `tests/conftest.py`.
3. `3dac4fd` M0.3 / Step 1.3a: lock-key utility for advisory-lock invariant primitives — new `app/framework/locks.py`.
4. `3a98223` M0.3 / Step 1.3a: capture-sink interface + in-memory stubs — new `app/framework/capture.py`.
5. `eb03780` M0.3 / Step 1.3a: framework exception types for dispatcher rejections — new `app/framework/exceptions.py`.
6. `588f87c` M0.3 / Step 1.3a: Command base class + explicit registry + ADR-0059 — new `app/framework/command.py` + decisions.md append.
7. `32306a8` M0.3 / Step 1.3a: cascade mechanism + safeguards + ADR-0060 — `command.py` + `exceptions.py` extensions + decisions.md append.
8. `c100982` M0.3 / Step 1.3a: Dispatcher pipeline + retry loop + ADR-0058 — new `app/framework/dispatcher.py` + command.py instance-attr declarations + decisions.md append.
9. `c59328e` M0.3 / Step 1.3a: smoke-test fixtures + end-to-end dispatcher tests — `tests/fixtures/smoketest/*` + `tests/test_dispatcher.py` + Caller Protocol → `@property id` fix.
10. (this commit) Step 1.3a ✓: handoff close-out (Session 30) — this rewrite.

**Branch ops.**
- `m0/03-dispatcher-and-history` created off `m0/foundations` at session head.
- **No FF-merge into `m0/foundations` yet** — per Round B's single-branch decision, both 1.3a and 1.3b commits accumulate on this branch; FF-merge happens after 1.3b lands.
- Housekeeping branches listed in Session 29 handoff (`origin/m0/01-scaffolding`, `m0-01-backup`, `m0/admin-paas-deferral`, `m0/02-data-layer-primitives`) found already deleted at session head — done out-of-session between Sessions 29 and 30; handoff was carrying a stale punch list.

**ADRs landed this sub-sub-step (3).** **ADR-0058** — Dispatcher contention-retry boundary (dispatcher-owned loop with 3-attempt budget + jittered backoff; TransientContention on exhaustion; per-transaction SERIALIZABLE at dispatcher level). **ADR-0059** — Command base class shape (plain class + nested Pydantic Payload + explicit registry; rejects Pydantic-as-command and decorator forms). **ADR-0060** — Cascade auth-inheritance mechanism (context flag + skip auth; 3 safeguards: G1 runtime guard + G2 registry-load-time destructive check + G3 AST drift inspector; amends ADR-0047 with the implementation envelope).

**Memories saved (0 new this session).** Three follow-up candidates queued in Open questions; will be saved next session per user direction.

**Files touched.** `planning/steps.md` (Step 1.3 partition block + sub-sub-step roster). `planning/decisions.md` (ADR-0058, ADR-0059, ADR-0060 appended). `backend/.env.example` (new). `backend/app/framework/{db,locks,capture,exceptions,command,dispatcher}.py` (all new). `backend/tests/conftest.py` (new SQLite fixtures). `backend/tests/fixtures/{__init__.py,smoketest/{__init__,entities,invariants,commands}.py}` (all new). `backend/tests/test_dispatcher.py` (new — 10 tests). `planning/handoff.md` (this rewrite). `_file-rules.md` **not regenerated** — no File contract block changed this session.

**Verification at session close.** `uv run ruff check app/ tests/` → All checks passed. `uv run pytest -v` → 11 passed (10 dispatcher + 1 existing healthcheck). `uv run --with pyright pyright app/ tests/` → 0 errors, 0 warnings, 0 informations.

---

## Open questions

**Discuss BEFORE substance at next session head (queued follow-ups from Session 30):**

- **(F1) Pyright in dev deps + CI gate.** Session 30 caught two real type errors that ruff missed — Pylance/Pyright runs only in the user's editor, so the type-check gate isn't enforced in CI or for other contributors. **Action:** add `pyright` (or `basedpyright`) to `pyproject.toml` `[dependency-groups] dev`; add a minimal `[tool.pyright]` config block (target Python 3.12; include `app/` + `tests/`; reasonable strictness); update CI to run `uv run pyright app/ tests/` alongside ruff + pytest. ~10 lines of pyproject + ~5 lines of CI config. ~10 min. **Should land before any more code commits** (otherwise more drift accumulates). Decide at session head: land as the first commit of Session 31, or punt to M0.4 / Step 1.4.
- **(F2) Neon live smoke-test.** Session 30 did not exercise the live Neon path — user has not pasted a `DATABASE_URL` into the conversation yet. **Action:** confirm `.env` is set on the active dev machine; optionally run `psql $DATABASE_URL -c 'SELECT 1'` + `uv run alembic upgrade head` against Neon to verify connectivity + baseline migration. Pytest currently uses SQLite in-memory; running the full suite against Postgres is also doable but adds network latency (skip unless concerned about Postgres-specific bugs). Neon setup walkthrough was delivered at Session 30 close (see chat transcript). Decide at session head: do it now (5 min) or defer to first M1 work.
- **(F3) Save memory: "ruff is lint + format only; project's type-check gate is currently editor-only Pylance."** Candidate as a [[feedback]] memory file so future sessions don't repeat the surprise. Body should include the workaround (`uv run --with pyright pyright`) and the eventual fix (F1). Save once F1 lands (so the memory reflects the resolved state) OR save now as "known gap pending F1" (so future sessions know to run pyright manually until F1 lands). Decide at session head.

**For the next session (Session 31 — Step 1.3b / M0.3 — History infrastructure):**

- **Per-entity history-table generator shape.** 9 tables per ADR-0052: 3 comprehensive (`document_history`, `wa_history`, `rfa_history`) + 6 lifecycle (`project_history`, `sample_batch_history`, `deliverable_history`, `employee_role_history`, `wa_code_history`, `contractor_engagement_history`). Decision surface: declarative-base-per-entity (one class per table, fully explicit) vs. dynamic class factory (programmatic generation from a per-entity spec). Could be ADR-worthy if non-obvious tradeoffs surface (e.g., Alembic autogenerate compatibility, type-check ergonomics on dynamically-generated classes). Pre-flag: **ADR-0061** if it surfaces.
- **`command_audit_log` table.** Polymorphic `(entity_type, entity_id)` shape per ADR-0052 § Audit-log table. Written in-txn per ADR-0057. Wired into the dispatcher's capture sink for the 7 audit-log entities (Employee, User, Time Entry, Contractor, DepFiling, Contract, WABundle). Schema: `id`, `entity_type`, `entity_id`, `command_id`, `command_name`, `caller_id`, `at`, `payload_summary` (JSONB). Index: `(entity_type, entity_id, at DESC)` + `(command_id)` for cascade lineage queries.
- **Real `CaptureSink` implementation.** Replaces 1.3a's `InMemorySink` stub. Pattern-matches on `HistoryRecord` variant and INSERTs into the appropriate table. Same SQLAlchemy session as the dispatcher's mutation (no new session) — atomicity per ADR-0008 + ADR-0057.
- **Alembic migrations.** All 10 tables (9 per-entity + `command_audit_log`). One migration file or one per table? Probably one for the common-metadata pattern + JSONB columns; Alembic autogenerate may produce one big migration that's easier to read as one unit.
- **Typed-UUID reference rule enforcement.** Per ADR-0013 § Reference snapshotting + ADR-0052 § S5: snapshots contain typed UUIDs only, no denormalized copies. The comprehensive snapshot in 1.3a is built via `_snapshot_entity()` which iterates SQLAlchemy column attrs — that's already typed-UUID-only because column values are scalars (relationships are skipped). For 1.3b, verify this holds when real domain entities land in M1+ (no `relationship()` attrs accidentally serialized).
- **Smoke test extension.** 1.3a's `InMemorySink` tests should mostly survive unchanged when the real sink replaces it — the dispatcher's API contract is unchanged. Add a small integration test verifying real rows land in the per-entity history tables and `command_audit_log` after a smoke dispatch.
- **Smoke entity migration parity.** SmokeBase / smoke-entity tables currently get created by `SmokeBase.metadata.create_all(engine)` in the test fixture (not via Alembic). 1.3b can either (a) leave smoke tables out of Alembic (test-only; create_all stays in fixture) or (b) add them to Alembic with a test-marker migration. Probably (a) — smoke entities are test fakes per Q2.

**For the milestone (M0 Foundations) broadly:**

- **Step 1.3b is the second sub-sub-step on `m0/03-dispatcher-and-history`.** Commits continue on the same branch (per Round B's single-branch decision). After 1.3b lands, FF-merge `m0/03-dispatcher-and-history` → `m0/foundations`.
- **M0.4 Adapter boundary (Step 1.4) opens after 1.3 (full Step 1.3 = 1.3a + 1.3b) lands.** Sized S. Wraps Postgres-specific features behind the adapter per ADR-0051: JSONB ops + `pg_try_advisory_xact_lock` (per ADR-0056) + `SERIALIZABLE` isolation. SQLite degraded equivalents — explicit not production-equivalent (per ADR-0051 + ADR-0052 + ADR-0056). Integration check: sample command flows through the full pipeline via the adapter on both Postgres and SQLite paths.
- **Sub-step branches off `m0/foundations`** per [[project-branching-convention]]. Step 1.4 = `m0/04-adapter-boundary`. Sub-step merges back into `m0/foundations` with FF (all checkpoint commits intact — see [[preserve-incremental-commits]]). M0 closes when all four canonical sub-steps merge to `m0/foundations` (M0.1 ✓, M0.2 ✓, M0.3 1.3a ✓ / 1.3b pending, M0.4 pending); `m0/foundations` then merges to `dev` with `--no-ff`, tag `m0-complete` on `dev`.
- **PaaS vendor pick stays deferred per ADR-0055.** Do not re-propose a vendor canvass at any future M0 sub-step session head. See [[project-vendor-pick-deferred]] for the 5 portability discipline notes that constrain forward work.
- **MVP-attempt-1 rewind protocol** (per [[project-branching-convention]]): if implementation attempt 1 tanks, tag `dev` as `attempt-1-archived` (or delete `dev`), recreate `dev` fresh from `main` (or `phase-1-complete` tag), restart at M0. All attempt-1 history preserved through milestone branches + tags.

**Carried into Phase 2 broadly:**

- **Adapter boundary scope.** Postgres-specific features live behind the adapter per ADR-0051. M0 establishes the boundary (M0.4 — renumbered from M0.5); subsequent milestones add features behind it as they need them. SQLite offline fallback is buildable but **not production-equivalent** (explicit per ADR-0051 + ADR-0052).
- **PaaS / vendor portability discipline** (per ADR-0055 + [[project-vendor-pick-deferred]]). Postgres 15+ floor; no vendor-specific extensions without availability check on realistic shortlist; vanilla `psycopg` only; CI stays on docker-compose Postgres; architecture.md vendor slot stays "deferred per ADR-0055."
- **Carry-forward landings.** All 7 command-shape carry-forwards land in specific milestones per `roadmap.md` § Carry-forward landing index. When each milestone opens, the carry-forwards landing in it should be raised at session head so the brief covers them.
- **MVP carve-out tracking.** `resolve_overlap_paired` (blocker #8 joint compound) ships in M6 conditionally on `split_entry`'s mechanics. If `split_entry` proves heavier than estimated when M6 opens, `resolve_overlap_paired` slips post-MVP per ADR-0050. Re-evaluate at M6 session head.

**Process notes (apply to Phase 2 generally):**

- **STOP-AND-CONFIRM gate stays in force, including for source code.** Each step / sub-step opens with chat-side deliberation before any code or ADR write.
- **Commit pattern: preserve incremental checkpoints; FF to milestone with all checkpoints intact** (per [[preserve-incremental-commits]]). Each checkpoint = a coherent atomic change at a green-state boundary, with a proper subject (no "wip:" prefix). `git log --first-parent dev` gives the milestone-level table of contents via the `--no-ff` milestone→dev merge convention.
- **Contract-drift CI job enforces schema + client are in sync.** Any backend OpenAPI-surface change requires `just gen-openapi` + commit of both `contracts/openapi.json` and `frontend/src/api/` (see [[committed-generated-artifacts]]).
- **`Command` base class + dispatcher is the structural anchor for all of Phase 2.** ADR-0008's atomicity (entity mutation + history write in the same transaction) is framework-enforced via the dispatcher (lands in M0.3 — renumbered from M0.4); no handler-level skip. Verify this invariant at every M1+ command-add.
- **Engine-portability discipline (ADR-0051 + ADR-0052).** Postgres-specific features stay behind the adapter; SQLite offline fallback uses degraded equivalents. Explicit not production-equivalent.
- **`mvp.md` is the canonical MVP scope reference.** Adding a feature beyond the 6 must-haves requires a superseding ADR. `mvp.md` § Carve-outs tracks the slip-eligible items; § Command-shape carry-forwards tracks the in-MVP-but-shape-deferred items.

## Next session

**Step 1.3b — M0.3 History infrastructure (M).** Replaces the in-memory `CaptureSink` stub from 1.3a with a real SQLAlchemy-backed sink that INSERTs into per-entity history tables + `command_audit_log` per ADR-0052 + ADR-0057. Lands the per-entity history-table generator (9 tables: 3 comprehensive + 6 lifecycle), the `command_audit_log` polymorphic table, Alembic migrations for all 10 tables, the real capture-sink impl replacing the stub, and an integration test verifying rows land in the right tables. Continues on the existing `m0/03-dispatcher-and-history` branch (no new branch — per Round B's single-branch decision). Possible ADR-0061 if the per-entity history-table generator shape surfaces non-obvious tradeoffs (declarative-base-per-entity vs. dynamic class factory).

**Execution order within Step 1 (post-collapse + 1.3 partition):** 1.1 ✓ → original 1.2 closed-by-deferral → 1.2 ✓ (Session 29) → 1.3a ✓ (Session 30) → **1.3b (next)** → FF-merge `m0/03-dispatcher-and-history` → `m0/foundations` after 1.3b lands → 1.4 → Step 1 ✓ (merge `m0/foundations` to `dev` with `--no-ff`; tag `m0-complete` on `dev`) → Step 2 (M1 Roster).

### Prompt for the next session

> Resume work. **Step 1.3b — M0.3 History infrastructure (M)** is the next sub-sub-step. Step 1.3a closed in Session 30 — ADR-0058 (dispatcher retry boundary), ADR-0059 (Command base class shape: plain class + nested Pydantic Payload + explicit registry), and ADR-0060 (cascade auth-inheritance mechanism + 3 safeguards) landed. The framework spine is in place: `app/framework/{db,locks,capture,exceptions,command,dispatcher}.py`; 10 dispatcher tests + 1 healthcheck test pass under SQLite; ruff + pyright clean.
>
> **Branch state:** `m0/03-dispatcher-and-history` carries 10 commits from Session 30 (1 partition + 7 implementation + 1 cascade safeguards + 1 handoff close-out). Continue on the same branch — single-branch convention per Round B (Session 30). Do NOT create a new sub-sub-step branch. FF-merge into `m0/foundations` happens AFTER 1.3b lands.
>
> **Open with the three queued follow-ups from Session 30 (F1 / F2 / F3 in Open questions above).** Discuss in order; act per user direction before any 1.3b substance:
> - **F1 — Pyright in dev deps + CI gate.** Strong recommend: land first (single small commit on `m0/03-dispatcher-and-history` adding `pyright` to dev deps + `[tool.pyright]` config + CI step). Without it, more type-error drift accumulates.
> - **F2 — Neon live smoke-test.** Quick: confirm `.env` set; optionally `psql $DATABASE_URL -c 'SELECT 1'` + `alembic upgrade head`. 5 min.
> - **F3 — Memory save for ruff vs. type-check gap.** Save as [[feedback]] memory after F1 lands (then memory reflects resolved state) OR now as "known gap pending F1" (so future sessions know to run pyright manually).
>
> **No Case 2 sizing at session head** — 1.3b is sized M, fits one session per the Round B partition decision.
>
> **Read first:** this prompt + the Open questions block above + the Last session summary (Session 30 — Step 1.3a) + `planning/steps.md` § Step 1.3b brief + `planning/data-model.md` § per-entity attribute rosters + history-table shapes + ADR-0013 (4-pattern history menu + reference rules) + ADR-0052 (data layer pin + history topology + per-pattern columns + audit-log shape) + ADR-0057 (in-txn audit-log timing). Skim `planning/history-patterns.md` (4-pattern menu) + 1.3a's outputs (`app/framework/capture.py` for the `HistoryRecord` typed union the real sink must accept; `app/framework/dispatcher.py` § `_build_capture_record` for what variants land in what cases).
>
> **In scope:**
> - **Per-entity history-table generator.** 9 tables per ADR-0052: 3 comprehensive (`document_history`, `wa_history`, `rfa_history`) + 6 lifecycle (`project_history`, `sample_batch_history`, `deliverable_history`, `employee_role_history`, `wa_code_history`, `contractor_engagement_history`). Decide declarative-base-per-entity vs. dynamic factory (ADR-0061 if non-obvious). Common-metadata columns + per-pattern columns per ADR-0052 § Consequences. Default index `(entity_id, at DESC)`.
> - **`command_audit_log` table.** Polymorphic `(entity_type, entity_id)` shape per ADR-0052 § Audit-log table. Schema: `id`, `entity_type`, `entity_id`, `command_id`, `command_name`, `caller_id`, `at`, `payload_summary` (JSONB). Index `(entity_type, entity_id, at DESC)` + `(command_id)` for cascade-lineage queries.
> - **Real `CaptureSink` implementation.** Pattern-matches on `HistoryRecord` variant from `app/framework/capture.py` (`ComprehensiveRecord | LifecycleRecord | AuditLogRecord`) and INSERTs into the appropriate table using the same SQLAlchemy session the dispatcher hands in (atomicity per ADR-0008 + ADR-0057). Constructor signature stays unchanged (the dispatcher constructs `Dispatcher(session_factory=..., sink=...)`); 1.3a's `InMemorySink` + `NullSink` stay for tests.
> - **Alembic migrations.** All 10 tables (9 per-entity + `command_audit_log`). Use Alembic autogenerate or hand-author; verify both Postgres + SQLite paths apply cleanly (smoke entity tables stay test-fixture-only via `create_all`).
> - **Capture enforcement** stays framework-enforced — no handler-level skip path (per ADR-0008 + ADR-0052; already enforced by 1.3a's dispatcher).
> - **Integration smoke test extension.** Add a test that runs a smoke command through the dispatcher with the real sink (against a real DB — SQLite in-memory or Postgres docker-compose), then queries the corresponding history table + `command_audit_log` to verify rows land correctly.
> - **Possibly ADR-0061** if generator shape surfaces ADR-worthy tradeoffs.
>
> **Out of scope:**
> - PaaS vendor pick — **stays deferred per ADR-0055**.
> - Adapter boundary code (named adapter functions wrapping JSONB / advisory-lock / SERIALIZABLE) — M0.4 / Step 1.4.
> - Any domain entity / command / handler beyond smoke-test fakes — M1+.
> - Changes to dispatcher pipeline shape, command base class, retry loop, cascade mechanism — settled in 1.3a's ADRs. Replacing the sink is the only dispatcher-facing change.
>
> **Process notes:**
> - **STOP-AND-CONFIRM gate applies, including for source code.** Generator shape decision is ADR-worthy; pin via chat-side canvass before writing.
> - **Commit pattern: preserve incremental checkpoints; FF to `m0/foundations` after 1.3b lands** (per [[preserve-incremental-commits]]).
> - **Branch:** continue on `m0/03-dispatcher-and-history`. After 1.3b lands: `git checkout m0/foundations && git merge --ff-only m0/03-dispatcher-and-history`.
> - **ADR numbering.** Next ADR at write time: **ADR-0061** (only if generator shape surfaces ADR-worthy tradeoffs).
> - **Portability discipline** (per ADR-0055 + [[project-vendor-pick-deferred]]). Per-entity history tables must use SQLAlchemy core types + portable SQL idioms; JSONB columns sit behind the adapter boundary landing in Step 1.4 (1.3b may use `JSONB` directly with a TODO marker for Step 1.4's adapter swap, OR use SQLAlchemy's `JSON` portable type and accept SQLite's text-backed equivalent as degraded).
> - **`mvp.md` is the canonical MVP scope reference.**
> - **User-knowledge note.** Per [[user-postgres-concurrency-gap]]: when discussing Postgres-specific data-layer mechanics (JSONB ops, GIN indexes, polymorphic FK alternatives), lean toward grounding terms before reaching for them; offer worked examples when introducing a primitive.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-18)
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 partitioned 2026-05-17 → 5 sub-steps; collapsed 2026-05-18 → 4 sub-steps per ADR-0055 deferral; Step 1.3 further partitioned 2026-05-18 (Session 30) → sub-sub-steps 1.3a + 1.3b on single branch**; Steps 2–9 stubs)
- Archived step list (Phase 1): `planning/steps.archive/conceptualization.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0060; next ADR at write time: **ADR-0061**)
- **Roadmap (Step 9b output):** `planning/roadmap.md` — 9 milestones (M0 → M8) with rough sizing (S/M/L), ordering rationale, carry-forward landing index. Canonical milestone-shape source for Phase 2.
- **MVP scope (Step 7 output):** `planning/mvp.md` — 6 must-have features + categorized "not now" list + 1 carve-out + 7 command-shape carry-forwards + pointers. Canonical MVP-scope reference.
- **Domain model (Step 6d output):** `planning/domain-model.md` — rolled-up domain projection: 21 entities, relationship table, per-entity lifecycles, authorization predicates (via ADR-0047), history patterns, delete policy, 14 design patterns, 10-entry blocker registry, vocabulary, deferred / open questions.
- **Data model (Step 9a output):** `planning/data-model.md` — conceptual data model: 21 entity sections (attribute table per entity with `Attribute | Kind | Type / notes`, outgoing-references line, state-enum line, history-surface label) + conventions block + history-table shapes per ADR-0052 (3 comprehensive + 6 lifecycle + `command_audit_log`). Conceptual only — not DDL.
- **Architecture (Step 8b output):** `planning/architecture.md` — one-page sketch: component diagram (Browser → CDN/SPA → API container → managed Postgres on managed PaaS), boundary semantics per layer, successful-command 10-step data flow, out-of-band concerns (file storage / background jobs / notifications / auth) flagged for implementation phase, pointers.
- **Consolidated blocker model (Session 25 / ADR-0053):** `planning/decisions.md` § ADR-0053 — current blocker-and-resolution model (supersedes ADR-0032).
- **Phase-transition (Session 25 / ADR-0054):** `planning/decisions.md` § ADR-0054 — phase-transition ADR.
- **Branching convention (memory):** [[project-branching-convention]] — `main` → `dev` → `m<N>/<slug>` → `m<N>/<sub-slug>`; tags on `main` as rewind anchors (`phase-1-complete` applied; `m<X>-complete` per milestone; `mvp-shipped` at MVP cutover); no type-prefixes; no `vN/`.
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md` (superseded by `mvp.md` § Not now; retained for trace continuity)
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
