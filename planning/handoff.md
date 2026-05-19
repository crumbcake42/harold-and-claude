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

**Implementation** — Phase 2. The 9-milestone roadmap from `planning/roadmap.md` (M0 Foundations → M8 Cutover prep) is the canonical milestone-shape source; `planning/steps.md` mirrors the milestones as 9 steps. **Step 1 (M0) partitioned 2026-05-17 into 5 sub-steps; collapsed 2026-05-18 to 4 sub-steps** when the original Step 1.2 (PaaS vendor pick) resolved as a deferral per ADR-0055 (Session 28). **Step 1.3 further partitioned 2026-05-18 (Session 30, Case 2)** into two sub-sub-steps on a single branch: **1.3a Dispatcher pipeline** (M) and **1.3b History infrastructure** (M). **Step 1.1 / M0.1 Scaffolding ✓ COMPLETE 2026-05-18** (Session 27). **Original Step 1.2 closed via deferral 2026-05-18** (Session 28). **Step 1.2 / M0.2 Data-layer primitives ✓ COMPLETE 2026-05-18** (Session 29 — ADR-0056 + ADR-0057 landed; `m0/02-data-layer-primitives` FF-merged into `m0/foundations`). **Step 1.3a / M0.3 Dispatcher pipeline ✓ COMPLETE 2026-05-18** (Session 30 — ADR-0058 + ADR-0059 + ADR-0060 landed; commits accumulate on `m0/03-dispatcher-and-history`; FF-merge into `m0/foundations` happens after 1.3b lands). **Session 31 (2026-05-19) closed the three Session-30 follow-ups (F1 + F2 landed; F3 closed-without-save) without entering 1.3b substance — context-budget call.** Currently on the **`m0/03-dispatcher-and-history`** branch (tip = Session 31 handoff close-out).

## Last session summary

**Session 31 — Step 1.3b follow-ups F1 + F2 ✓; F3 closed-without-save (2026-05-19).** Case-3 scoped session that, per the Session-30 prompt directive, opened with the three queued follow-ups (F1 pyright gate / F2 Neon ping / F3 memory save) before touching 1.3b substance. F1 + F2 landed; F3 closed without writing memory; **no 1.3b substance reached** — wrapping pre-substance was a context-budget call so the per-entity history-table generator-shape decision (possible ADR-0061) and the rest of 1.3b open in a fresh window.

**Substance.**

- **F1 — Pyright dev dep + CI typecheck gate (commit `168f320`).** Added `pyright>=1.1` to `[dependency-groups] dev` in `backend/pyproject.toml`; added a minimal `[tool.pyright]` block (`include = ["app", "tests"]`, `pythonVersion = "3.12"`, `typeCheckingMode = "basic"`); inserted a `Typecheck (pyright)` step in `.github/workflows/ci.yml`'s `backend` job between `Lint (ruff)` and `Test (pytest)`. `uv sync` installed `pyright==1.1.409` + `nodeenv==1.10.0`. Local verification: ruff clean / `pyright app/ tests/` → 0 errors, 0 warnings, 0 informations / pytest 11 passed. Resolves the Session-30 process gap where Pylance-only type-checking caught two real errors (`Command` instance-attr declarations + Caller Protocol `id` read-only) that ruff missed.
- **F2 — Neon `SELECT 1` smoke test ✓.** `DATABASE_URL` confirmed set in `backend/.env`; connection via `psycopg` succeeded. Host: `ep-silent-rain-aqlneil8.c-8.us-east-1.aws.neon.tech`. Server: **PostgreSQL 17.8** — comfortably above the 15+ floor per ADR-0055 portability discipline. `current_database()` = `neondb`; `current_user` = `neondb_owner`. `alembic upgrade head` deliberately **not run** — there's already an empty baseline migration in place (normal Alembic idiom — establishes `alembic_version` row + parent revision for autogenerate to diff against), and the first non-empty migration will be authored as part of 1.3b's per-entity history-table generator.
- **F3 — Closed without saving memory.** Recommendation flipped between proposal turn and execution turn: the original "save the gap as feedback" framing was stale once F1 closed the gap; saving the resolved state ("pyright runs in CI") duplicates project tooling state directly derivable from `pyproject.toml` + `.github/workflows/ci.yml` and falls under the auto-memory don't-save guidance ("Code patterns, conventions, architecture, file paths, or project structure — these can be derived by reading the current project state"). User confirmed close-without-save.

**Commits landed on `m0/03-dispatcher-and-history` (1).**
1. `168f320` M0.3 / Step 1.3b: add pyright to dev deps + CI typecheck gate — `backend/pyproject.toml` + `backend/uv.lock` + `.github/workflows/ci.yml`.
2. (this commit) Session 31 handoff close-out — this rewrite.

**Branch ops.** No new branches; no FF-merges. `m0/03-dispatcher-and-history` continues accumulating commits per Round B's single-branch decision (Session 30). FF-merge into `m0/foundations` still happens after 1.3b lands.

**ADRs landed this session (0).** F1 was a tooling/process change (not architecturally novel). F2 was verification. No ADRs.

**Memories saved (0 new this session).** F3 closed-without-save per above.

**Files touched.** `backend/pyproject.toml`. `backend/uv.lock`. `.github/workflows/ci.yml`. `planning/handoff.md` (this rewrite). `_file-rules.md` **not regenerated** — no File contract block changed this session.

**Verification at session close.** `uv run ruff check .` → All checks passed. `uv run pyright app/ tests/` → 0 errors, 0 warnings, 0 informations. `uv run pytest` → 11 passed.

---

## Open questions

**For the next session (Session 32 — Step 1.3b / M0.3 — History infrastructure):**

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
> **Branch state:** `m0/03-dispatcher-and-history` carries 12 commits ahead of `m0/foundations` (10 from Session 30 + 2 from Session 31 — pyright CI gate at `168f320` + Session-31 handoff close-out). Continue on the same branch — single-branch convention per Round B (Session 30). Do NOT create a new sub-sub-step branch. FF-merge into `m0/foundations` happens AFTER 1.3b lands.
>
> **Session-31 follow-ups are CLOSED — do not re-raise.** F1 (pyright in dev deps + CI typecheck gate) landed at `168f320`. F2 (Neon `SELECT 1` smoke) confirmed connectivity: PostgreSQL 17.8 on `ep-silent-rain-aqlneil8.c-8.us-east-1.aws.neon.tech` / `neondb` / `neondb_owner`. F3 (memory save for the ruff vs. type-check gap) closed without saving — resolved state duplicates `pyproject.toml` + `ci.yml` and falls under the auto-memory don't-save guidance. **Run 1.3b substance directly.**
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
