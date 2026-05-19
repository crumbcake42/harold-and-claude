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

**Implementation** — Phase 2. The 9-milestone roadmap from `planning/roadmap.md` (M0 Foundations → M8 Cutover prep) is the canonical milestone-shape source; `planning/steps.md` mirrors the milestones as 9 steps. **Step 1 (M0) partitioned 2026-05-17 into 5 sub-steps; collapsed 2026-05-18 to 4 sub-steps** when the original Step 1.2 (PaaS vendor pick) resolved as a deferral per ADR-0055 (Session 28). **Step 1.3 further partitioned 2026-05-18 (Session 30, Case 2)** into two sub-sub-steps on a single branch: **1.3a Dispatcher pipeline** (M) and **1.3b History infrastructure** (M). **Step 1.1 / M0.1 Scaffolding ✓ COMPLETE 2026-05-18** (Session 27). **Original Step 1.2 closed via deferral 2026-05-18** (Session 28). **Step 1.2 / M0.2 Data-layer primitives ✓ COMPLETE 2026-05-18** (Session 29 — ADR-0056 + ADR-0057 landed; `m0/02-data-layer-primitives` FF-merged into `m0/foundations`). **Step 1.3a / M0.3 Dispatcher pipeline ✓ COMPLETE 2026-05-18** (Session 30). **Session 31 (2026-05-19) closed three Session-30 follow-ups (F1 + F2 landed; F3 closed-without-save) without 1.3b substance — context-budget call.** **Step 1.3b / M0.3 History infrastructure ✓ COMPLETE 2026-05-19** (Session 32 — no ADRs; three forks resolved via chat-side canvass and documented in code). Currently on the **`m0/03-dispatcher-and-history`** branch (tip = Session 32 single-commit consolidation). **FF-merge `m0/03-dispatcher-and-history` → `m0/foundations` is the next branch op**, closing Step 1.3 entirely and opening Step 1.4 / M0.4 Adapter boundary.

## Last session summary

**Session 32 — Step 1.3b / M0.3 History infrastructure ✓ COMPLETE (2026-05-19).** Case-3 scoped session that landed all seven 1.3b in-scope items in a single sweep: production `Base`, the 9 per-entity history tables + `command_audit_log`, the real `SqlAlchemyCaptureSink`, the Alembic migration, integration tests against real DB rows, and one mid-session correction (engine-wide JSON serializer for UUID/datetime coercion) the integration test surfaced. No ADRs landed — three deliberable forks were resolved via chat-side canvass at session head and documented in code rather than as a formal ADR. Step 1.3 closes here entirely (1.3a Session 30 + 1.3b Session 32); FF-merge `m0/03-dispatcher-and-history` → `m0/foundations` is the next branch op, then Step 1.4 / M0.4 Adapter boundary opens.

**Three forks resolved (chat-side canvass, no ADR-0061).**

- **Generator shape — mixin-based explicit classes.** `CommonHistoryMixin` (7 common-metadata columns) + `ComprehensiveHistoryMixin` (adds `snapshot`) + `LifecycleHistoryMixin` (adds `from_state` / `to_state` / `transition_name` / `state_context`); 9 concrete classes × ~3 lines each. Beats fully-explicit (repetitive — 7 columns × 9 tables) and dynamic factory (opaque to pyright, harder to grep). Tradeoffs obvious enough that the choice records in `history.py`'s module docstring rather than as a formal ADR. ADR-0061 unused; available if a generator-shape question with non-obvious tradeoffs surfaces in M1+.
- **Sink seam — extend `CaptureSink.emit` Protocol signature.** Changed `emit(record)` → `emit(record, session)` so the real sink can `session.add()` inside the dispatcher's current transaction per ADR-0008 + ADR-0057. `InMemorySink` / `NullSink` accept and ignore the session arg. Small surgical correction to the seam 1.3a pinned; the seam was almost right but missed this parameter.
- **FK timing — defer per-entity FKs to M1+.** Per-entity history tables hold `entity_id` as a plain UUID column with **no FK constraint** at M0.3 — the referenced entity tables don't exist yet (no domain entities until M1+). Each M1+ entity migration will add its FK alongside its entity table. `command_audit_log` correctly carries no FK (polymorphic per ADR-0052 § Audit-log table). data-model.md § Common metadata's "FK on per-entity history tables" line is honored at full step-1 completion, not at 1.3b alone.

**Substance.**

- **Production `Base` + portable JSON column + JSON serializer (`app/framework/db.py`).** Added `class Base(DeclarativeBase)` (first occupant: the 10 history tables; domain entities join in M1+). Added `json_column()` factory returning `JSON().with_variant(JSONB(), "postgresql")` — JSONB on PG, portable JSON on SQLite; TODO marker references M0.4's adapter wrap. Added engine-wide `json_serializer = lambda obj: json.dumps(obj, default=str)` on `_build_engine()`; mid-session integration-test failure surfaced that `_snapshot_entity()` returns dicts containing raw `UUID` objects which Python's default JSON encoder rejects. Engine-wide serializer keeps UUIDs/datetimes in JSON columns as strings — consistent with ADR-0013's typed-UUID rule (readers parse the type back from the string).
- **History models (`app/framework/history.py`, new).** 2 pattern mixins + 1 common mixin; 3 comprehensive classes (`DocumentHistory`, `WAHistory`, `RFAHistory`); 6 lifecycle classes (`ProjectHistory`, `SampleBatchHistory`, `DeliverableHistory`, `EmployeeRoleHistory`, `WACodeHistory`, `ContractorEngagementHistory`); 1 `CommandAuditLog` (standalone, common mixin + `entity_type` + `payload_summary`). Per-entity index `(entity_id, at)` on each per-entity table; `command_audit_log` carries `(entity_type, entity_id, at)` + `(command_id)` per ADR-0052 § Audit-log table. Two module-level registries: `COMPREHENSIVE_HISTORY: dict[str, type]` and `LIFECYCLE_HISTORY: dict[str, type]`, keyed by entity class name (matches `type(target).__name__` from the dispatcher). Module docstring records the mixin-explicit choice and the FK-deferred decision. Columns honored: `id, entity_id, command_id, command_name, caller_id, at` — matches the `HistoryRecord` variants from 1.3a's `app/framework/capture.py`. Columns deferred from `data-model.md` § Common metadata: **`sequence_no`** (gap-free per-entity ordering — requires either per-entity advisory lock or a serial-per-entity scheme; not load-bearing for any current consumer) and **`command_payload`** (full request payload — `snapshot` / `state_context` / `payload_summary` cover the audit story per pattern). Both re-addable as additive M1+ migrations if a consumer needs them.
- **`CaptureSink` Protocol + `SqlAlchemyCaptureSink` (`app/framework/capture.py`).** Protocol signature extended to `emit(record: HistoryRecord, session: Session) -> None`. `InMemorySink` + `NullSink` updated to accept the session arg (ignored). New `SqlAlchemyCaptureSink` class: constructor `__init__(comprehensive: dict[str, type], lifecycle: dict[str, type], audit_log_model: type)` — caller wires the registries (production wires `COMPREHENSIVE_HISTORY` / `LIFECYCLE_HISTORY` / `CommandAuditLog`; integration tests wire smoke-only maps targeting SmokeBase tables). `emit()` pattern-matches the record variant via `isinstance`, constructs the matching model instance, and calls `session.add()` — atomicity per ADR-0008 + ADR-0057 (the dispatcher's commit decides whether the row persists; no `session.commit()` inside the sink). Unregistered `entity_type` raises a useful `KeyError` (covered by an integration test). Unknown record variant raises `TypeError` (defense-in-depth; statically unreachable given the typed union).
- **Dispatcher one-line update (`app/framework/dispatcher.py`).** `self.sink.emit(record)` → `self.sink.emit(record, session)`. All other dispatcher behavior unchanged.
- **Alembic wiring + migration (`backend/migrations/env.py` + new revision `b555ac8d13da_history_infrastructure.py`).** env.py imports `Base` from `app.framework.db` + the `history` module (populates `Base.metadata`); sets `target_metadata = Base.metadata`. Migration authored via `alembic revision --autogenerate` against a fresh SQLite (`tmp_autogen.db`) with the empty baseline applied — produced one clean diff with all 10 `create_table` ops + their indices. One mechanical cleanup: stripped the `astext_type=Text()` artifact autogenerate emitted on every JSONB column (`Text` wasn't imported in the migration; the default `astext_type` is already `Text`). Verified upgrade → downgrade → upgrade cycle against SQLite via DATABASE_URL override; alembic_version stamping correct; full table inventory inspected post-upgrade (10 history tables + alembic_version, all columns + indices present). Migration uses `sa.JSON().with_variant(postgresql.JSONB(), 'postgresql')` — same portable form as the model declarations.
- **Smoke audit fixture (`backend/tests/fixtures/smoketest/entities.py`).** Added `SmokeAuditEntity` (the audit-log-pattern gap pre-flagged in the 1.3a fixture docstring). Added 3 smoke history tables on `SmokeBase` reusing the production mixins (`SmokeComprehensiveHistory`, `SmokeLifecycleHistory`, `SmokeAuditLog`) so integration tests can wire `SqlAlchemyCaptureSink` against `SmokeBase` in isolation from production registries. Mixin reuse works because the mixins don't bind to `Base` — they contribute columns to any concrete declarative class that inherits them. Renamed `_CommonHistoryMixin` → `CommonHistoryMixin` (public) and `_json_serializer` → `json_serializer` (public) as a consequence of the cross-module imports; both are first-class reuse points now.
- **Smoke audit command (`backend/tests/fixtures/smoketest/commands.py`).** Added `CreateSmokeAudit` exercising the audit-log path.
- **Integration tests (`backend/tests/test_capture_sink_integration.py`, new).** 5 tests against a real SQLite engine wired with `SqlAlchemyCaptureSink`: (a) `CreateSmoke` writes a comprehensive row with the full snapshot; (b) `CreateSmokeLifecycle` + `CloseSmokeLifecycle` write two lifecycle rows with correct `from_state` / `to_state` / `transition_name`; (c) `CreateSmokeAudit` writes an audit-log row with `entity_type` + `payload_summary`; (d) `CreateSmoke` with `value=0` (invariant violation) rolls back — no history row persists, demonstrating ADR-0008's atomicity; (e) `SqlAlchemyCaptureSink.emit` raises `KeyError` for an unregistered entity_type. Existing 11 dispatcher tests + 1 healthcheck test stay green using `InMemorySink`. **Total: 16 tests, all green.**
- **conftest update (`backend/tests/conftest.py`).** `sqlite_engine` fixture now uses the production `json_serializer` so JSON column writes coerce UUIDs/datetimes consistently across test and production engines.

**Commit landed on `m0/03-dispatcher-and-history` (1).**

1. (this commit) Step 1.3b complete: history infrastructure + real capture sink + integration tests + handoff close-out. 10 files modified/created spanning `app/framework/{db,history,capture,dispatcher}.py` + `migrations/env.py` + new migration + smoke fixture extensions + new integration test module + handoff rewrite.

**Branch ops.** No new branches; no FF-merges yet. After this commit lands: `git checkout m0/foundations && git merge --ff-only m0/03-dispatcher-and-history` closes Step 1.3 entirely. Step 1.4 / M0.4 opens on a new branch `m0/04-adapter-boundary` off the updated `m0/foundations`.

**ADRs landed this session (0).** Three forks resolved via chat-side canvass per the STOP-AND-CONFIRM gate; tradeoffs documented in `history.py`'s module docstring. ADR-0061 remains unused — available if a generator-shape question with non-obvious tradeoffs surfaces later.

**Memories saved (0 new this session).**

**Files touched.** `backend/app/framework/db.py`. `backend/app/framework/history.py` (new). `backend/app/framework/capture.py`. `backend/app/framework/dispatcher.py`. `backend/migrations/env.py`. `backend/migrations/versions/b555ac8d13da_history_infrastructure.py` (new). `backend/tests/conftest.py`. `backend/tests/fixtures/smoketest/entities.py`. `backend/tests/fixtures/smoketest/commands.py`. `backend/tests/test_capture_sink_integration.py` (new). `planning/handoff.md` (this rewrite). `_file-rules.md` **not regenerated** — no `## File contract` block changed this session.

**Verification at session close.** `uv run ruff check .` → All checks passed. `uv run pyright app/ tests/ migrations/` → 0 errors, 0 warnings, 0 informations. `uv run pytest` → 16 passed (11 dispatcher + 1 healthcheck + 5 integration). `alembic upgrade head` / `downgrade base` / `upgrade head` cycle against SQLite all clean; post-upgrade schema inspection confirmed 10 history tables + correct columns + correct indices.

---

## Open questions

**For the next session (Session 33 — Step 1.4 / M0.4 Adapter boundary):**

- **Adapter boundary surface.** Wraps the three Postgres-specific features behind a documented adapter per ADR-0051 + ADR-0052: (a) JSONB ops (currently used directly in history snapshots via `json_column()` in `app/framework/db.py` with a TODO marker referencing this step); (b) `pg_try_advisory_xact_lock` (currently called directly from `app/framework/dispatcher.py` § Invariants step via `try_advisory_xact_lock` in `app/framework/locks.py`); (c) `SERIALIZABLE` transaction isolation (currently set inline at the top of `_run_pipeline` in `app/framework/dispatcher.py`). Decision surface: shape of the adapter (single module with three functions vs. a `DBAdapter` Protocol with PG/SQLite implementations vs. SQLAlchemy dialect dispatch in a thin adapter module). Adapter must remain Step 1.3b's JSON-column / sink wiring with a one-call swap.
- **SQLite degraded equivalents.** Per ADR-0051 + ADR-0052 + ADR-0056: SQLite fallback is buildable but **not production-equivalent**. Specifically: SQLite's JSON type is text-backed (works for `json_column()` already via `with_variant`); SQLite has no native advisory locks (degraded: optimistic-locking or no-op for tests); SQLite defaults to `SERIALIZABLE` isolation by virtue of single-writer concurrency (not the same primitive Postgres uses; degraded). Document the gap in the adapter's docstring; tests verify both paths build but the production path is Postgres-only.
- **Integration check.** A sample command (likely re-using the smoke fixtures) flows through the full pipeline via the adapter on both Postgres (docker-compose in CI) and SQLite (offline) paths. Both apply cleanly; both produce correct history rows; both reject invariant-violators correctly. Distinct from 1.3b's integration test (which already runs the full pipeline on SQLite via the real sink) by adding the Postgres path.
- **No ADRs expected.** The adapter shape is mostly mechanical wrapping of features already pinned by ADRs 0051 / 0052 / 0056. ADR-0061 remains unused; available if a non-obvious tradeoff surfaces.
- **Commit pattern.** New branch `m0/04-adapter-boundary` off `m0/foundations` per [[project-branching-convention]]; preserve incremental checkpoints; FF-merge to `m0/foundations` after 1.4 lands; then merge `m0/foundations` → `dev` with `--no-ff` + tag `m0-complete` on `dev`. Closes M0 entirely.

**For the milestone (M0 Foundations) broadly:**

- **Step 1.3 ✓ COMPLETE (1.3a + 1.3b).** FF-merge `m0/03-dispatcher-and-history` → `m0/foundations` is the next branch op. Confirm at Session 33 head before opening Step 1.4 on its own branch.
- **M0.4 Adapter boundary (Step 1.4) is the last canonical M0 sub-step.** Sized S. After 1.4 lands and `m0/04-adapter-boundary` FF-merges to `m0/foundations`: `m0/foundations` merges to `dev` with `--no-ff`; tag `m0-complete` on `dev`. M0 closes; Step 2 (M1 Roster) opens on a new milestone branch off `dev`.
- **Smoke fixtures stay as test fakes.** SmokeBase tables are created via `SmokeBase.metadata.create_all(engine)` in the test fixture (not in Alembic), and SmokeBase-bound history tables in 1.3b followed the same convention. M1+ domain entities + their history-table FKs land via Alembic migrations.
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

**Step 1.4 — M0.4 Adapter boundary for Postgres-specific features (S).** Wraps the three Postgres-specific features Step 1.3 exposed inline (JSONB ops via `json_column()`; `pg_try_advisory_xact_lock` via `try_advisory_xact_lock`; per-transaction `SERIALIZABLE` isolation set at the top of the dispatcher's pipeline) behind a documented adapter per ADR-0051. SQLite offline-fallback path uses degraded equivalents — buildable but **not production-equivalent** per ADR-0051 + ADR-0052 + ADR-0056. Integration check: a sample command flows through the full pipeline (dispatcher → invariants under chosen isolation → history write at chosen timing → commit) via the adapter on both Postgres (docker-compose CI) and SQLite (offline) paths. **First branch op at Session-33 head: FF-merge `m0/03-dispatcher-and-history` → `m0/foundations` to close Step 1.3 entirely; then open new branch `m0/04-adapter-boundary` off the updated `m0/foundations`.** No ADRs expected.

**Execution order within Step 1 (post-collapse + 1.3 partition):** 1.1 ✓ → original 1.2 closed-by-deferral → 1.2 ✓ (Session 29) → 1.3a ✓ (Session 30) → 1.3b ✓ (Session 32) → **FF-merge `m0/03-dispatcher-and-history` → `m0/foundations`** (Session 33 head) → **1.4 (next)** → Step 1 ✓ (merge `m0/foundations` to `dev` with `--no-ff`; tag `m0-complete` on `dev`) → Step 2 (M1 Roster).

### Prompt for the next session

> Resume work. **Step 1.4 — M0.4 Adapter boundary for Postgres-specific features (S)** is the next sub-step and the last canonical M0 work item. Step 1.3 closed in Session 32 — full pipeline + 10 history tables + real `SqlAlchemyCaptureSink` all land green; 16 tests pass; ruff + pyright clean; Alembic upgrade/downgrade cycle clean on SQLite. No ADRs landed in Session 32 — three forks (mixin generator shape / sink `emit(record, session)` Protocol signature / per-entity FK timing deferred to M1+) were resolved via chat-side canvass and documented in code rather than as a formal ADR.
>
> **First branch op (do this at session head, before any 1.4 substance):**
> ```
> git checkout m0/foundations
> git merge --ff-only m0/03-dispatcher-and-history
> git checkout -b m0/04-adapter-boundary
> ```
> This closes Step 1.3 entirely and opens Step 1.4 on its own branch off the updated `m0/foundations`. Per [[project-branching-convention]]: sub-step branches off `m0/foundations`; FF back into `m0/foundations` after Step 1.4 lands; `m0/foundations` then merges to `dev` with `--no-ff` + tag `m0-complete` on `dev`.
>
> **Branch state before merge:** `m0/03-dispatcher-and-history` carries 13 commits ahead of `m0/foundations` (10 from Session 30 + 2 from Session 31 — pyright CI gate at `168f320` + Session-31 handoff close-out — + 1 from Session 32: Step 1.3b complete). After FF-merge `m0/foundations` carries 13 new commits; `m0/03-dispatcher-and-history` becomes safe to delete (or keep as a historical tag/branch reference).
>
> **No Case 2 sizing at session head** — 1.4 is sized S; the adapter shape is mostly mechanical wrapping of features already pinned by ADR-0051 + ADR-0052 + ADR-0056.
>
> **Read first:** this prompt + the Open questions block above + the Last session summary (Session 32 — Step 1.3b) + `planning/steps.md` § Step 1.4 brief + ADR-0051 (runtime stack + adapter boundary pin) + ADR-0052 § Engine-portability discipline + ADR-0056 (per-invariant isolation primitives + first per-invariant assignments). Skim `app/framework/db.py` (json_column factory; engine builder; `Base`), `app/framework/locks.py` (advisory-lock helper currently called inline from the dispatcher), `app/framework/dispatcher.py` § `_run_pipeline` (where SERIALIZABLE is set inline), `app/framework/history.py` (JSON columns currently use `json_column()` directly with a TODO marker for this step).
>
> **In scope:**
> - **Adapter boundary module.** Decide shape: single module with three functions vs. a `DBAdapter` Protocol with PG/SQLite implementations vs. SQLAlchemy dialect dispatch in a thin module. Wraps: (a) JSONB columns (replace direct `json_column()` calls with adapter-provided column factory); (b) advisory-lock acquisition (replace direct `try_advisory_xact_lock` call from dispatcher); (c) per-transaction SERIALIZABLE isolation (replace inline `execution_options(isolation_level=...)` call in dispatcher's `_run_pipeline`).
> - **SQLite degraded equivalents.** SQLite already gets text-backed JSON via `with_variant` (works); advisory locks become a no-op or optimistic-locking stand-in (test-only; explicit not production-equivalent); SERIALIZABLE isolation is implicit on SQLite due to single-writer concurrency (different primitive; document the gap). Adapter docstring names what's production-equivalent vs. degraded.
> - **Integration check.** A sample command (re-use smoke fixtures or extend) flows through the full pipeline via the adapter on both Postgres (docker-compose CI) and SQLite (offline) paths. Both apply cleanly; both produce correct history rows; both reject invariant-violators correctly. Distinct from 1.3b's integration test by adding the Postgres path.
> - **Documentation refresh.** Remove the TODO markers in `json_column()` and elsewhere that point at this step; replace with adapter-call sites.
>
> **Out of scope:**
> - PaaS vendor pick — **stays deferred per ADR-0055**.
> - Any domain entity / command / handler beyond smoke-test fakes — M1+.
> - Changes to dispatcher pipeline shape, command base class, retry loop, cascade mechanism, sink interface, history models, or migration — settled in 1.3a + 1.3b. The adapter is a refactor of the *call sites* of three Postgres-specific features, not a redesign of the features themselves.
> - `sequence_no` / `command_payload` columns on history tables — explicitly deferred from 1.3b (additive M1+ migrations if a consumer needs them).
>
> **Process notes:**
> - **STOP-AND-CONFIRM gate applies, including for source code.** Adapter-shape decision earns a chat-side canvass before writing.
> - **Commit pattern: preserve incremental checkpoints; FF to `m0/foundations` after 1.4 lands; then merge to `dev` with `--no-ff` + tag `m0-complete`** (per [[preserve-incremental-commits]] + [[project-branching-convention]]).
> - **Branch:** new branch `m0/04-adapter-boundary` off `m0/foundations` after the 1.3b FF-merge.
> - **ADR numbering.** Next ADR at write time: **ADR-0061** (only if adapter shape surfaces ADR-worthy tradeoffs — unlikely; mostly mechanical).
> - **Portability discipline** (per ADR-0055 + [[project-vendor-pick-deferred]]). The whole point of this step is to land the adapter boundary; portability discipline is exactly what this step formalizes.
> - **`mvp.md` is the canonical MVP scope reference.**
> - **User-knowledge note.** Per [[user-postgres-concurrency-gap]]: when discussing Postgres-specific data-layer mechanics (JSONB ops, advisory locks, isolation primitives), lean toward grounding terms before reaching for them; offer worked examples when introducing a primitive.

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
