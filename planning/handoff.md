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

**Implementation** — Phase 2. The 9-milestone roadmap from `planning/roadmap.md` (M0 Foundations → M8 Cutover prep) is the canonical milestone-shape source; `planning/steps.md` mirrors the milestones as 9 steps. **Step 1 (M0) partitioned 2026-05-17 into 5 sub-steps; collapsed 2026-05-18 to 4 sub-steps** when the original Step 1.2 (PaaS vendor pick) resolved as a deferral per ADR-0055 (Session 28). **Step 1.3 further partitioned 2026-05-18 (Session 30, Case 2)** into two sub-sub-steps on a single branch: **1.3a Dispatcher pipeline** (M) and **1.3b History infrastructure** (M). Sub-step status: **1.1 / M0.1 Scaffolding ✓ COMPLETE 2026-05-18** (Session 27); original 1.2 closed via deferral 2026-05-18 (Session 28); **1.2 / M0.2 Data-layer primitives ✓ COMPLETE 2026-05-18** (Session 29); **1.3a / M0.3 Dispatcher pipeline ✓ COMPLETE 2026-05-18** (Session 30); **1.3b / M0.3 History infrastructure ✓ COMPLETE 2026-05-19** (Session 32); **1.4 / M0.4 Adapter boundary ✓ COMPLETE 2026-05-19** (Session 33, this rewrite). **Step 1 / M0 Foundations ✓ COMPLETE 2026-05-19** — all four sub-steps landed. Currently on the **`m0/04-adapter-boundary`** branch (tip = Session 33 single-commit). **Next branch ops: FF-merge `m0/04-adapter-boundary` → `m0/foundations`; then merge `m0/foundations` → `dev` with `--no-ff`; tag `m0-complete` on `dev`.** This closes M0 entirely and opens **Step 2 / M1 Roster** on a new milestone branch off `dev`.

## Last session summary

**Session 33 — Step 1.4 / M0.4 Adapter boundary ✓ COMPLETE (2026-05-19).** Case-3 scoped session landing the documented Postgres-specific adapter boundary per ADR-0051 + ADR-0052 + ADR-0056. Three call sites consolidated into a single module; call sites updated; 11 unit tests added; full suite green; alembic upgrade/downgrade cycle clean. No ADRs landed — mechanical refactor as the handoff anticipated. **Step 1 / M0 closes entirely with this session.**

**Three forks resolved at session head (chat-side canvass; no ADRs).**

- **Adapter shape — single module of three functions.** `app/framework/adapter.py` exposes `json_column()`, `try_advisory_xact_lock(session, key)`, `set_serializable_isolation(session)` with inline dialect-dispatch and degraded-fallback semantics documented in the module docstring. Beats Protocol/DI (no swap-flexibility need — tests already exercise both paths by engine URL, not by injecting a fake adapter; DI ceremony pays nothing) and SQLAlchemy-idiomatic (collapses to the single-module shape in practice; SQLAlchemy has no native primitive for "Postgres-only call, no-op on SQLite" for the lock + isolation cases).
- **Postgres CI path — no docker-compose service.** Per user constraint (unreliable Docker access on dev machines), CI does not gain a `postgres:15` service. Live-engine PG verification stays a manual exercise when a developer points `DATABASE_URL` at a real Postgres; CI gate stays SQLite-only. PG dispatch logic is verified by 11 unit tests in `test_adapter.py` that mock `session.bind.dialect.name`. Documented in `test_adapter.py`'s module docstring. The "CI ephemeral-PR DB wiring against the chosen vendor" carry-forward stays deferred per ADR-0055 (unchanged from M0.1's deferral posture).
- **Branch op at session head — non-destructive, executed before substance.** `git checkout m0/foundations && git merge --ff-only m0/03-dispatcher-and-history && git checkout -b m0/04-adapter-boundary` closed Step 1.3 entirely and opened Step 1.4 on its own branch as the handoff prescribed.

**Substance.**

- **`app/framework/adapter.py` (new).** Three documented functions: `json_column()` (returns `JSON().with_variant(JSONB(), "postgresql")` — relocated from `db.py`); `try_advisory_xact_lock(session, key) -> bool` (PG: `pg_try_advisory_xact_lock(hashtextextended(:key, 0))`; SQLite: returns True unconditionally — degraded per ADR-0056); `set_serializable_isolation(session) -> None` (PG: `execution_options(isolation_level="SERIALIZABLE")`; SQLite: no-op — degraded per ADR-0056). Module docstring names each function's PG-equivalent and SQLite-degraded behavior + ADR references. Imports `validate_key_namespace` from `app.framework.locks` to gate the lock-key on both branches.
- **`app/framework/locks.py` (slimmed to policy).** Retained: `LockNamespace` enum (`CLOSURE_READINESS` namespace), `closure_readiness_key(project_id)` builder, `validate_key_namespace(key)` (renamed from private `_validate_key_namespace` — adapter consumes it cross-module). Removed: `try_advisory_xact_lock` (moved to adapter — mechanism vs. policy split). Module docstring updated to point at the adapter for acquisition.
- **`app/framework/db.py` (slimmed).** `json_column()` removed (relocated to adapter); `Base` declarative base, `json_serializer` (engine-wide JSON serializer for UUID/datetime coercion), `_build_engine`, `engine`, `SessionFactory`, `get_session`, `is_postgres` all retained.
- **`app/framework/history.py`.** Imports `json_column` from adapter instead of `db`. No structural change.
- **`app/framework/dispatcher.py`.** Imports `try_advisory_xact_lock` + `set_serializable_isolation` from adapter (dropped direct `locks` import). Inline `session.connection().execution_options(isolation_level="SERIALIZABLE")` at the top of `_run_pipeline` replaced by `set_serializable_isolation(session)`. TODO marker referencing this step removed from `db.py`'s `json_column` (the function is gone).
- **`tests/fixtures/smoketest/entities.py`.** Imports `json_column` from adapter.
- **`tests/test_adapter.py` (new).** 11 tests: (a) `json_column()` returns a JSON type whose PG dialect impl is JSONB; (b) on SQLite the dialect impl is not JSONB (text-backed); (c) `try_advisory_xact_lock` emits `pg_try_advisory_xact_lock(hashtextextended(...))` on PG mocked dialect; (d) returns False on PG contention; (e) returns True unconditionally on SQLite without executing SQL; (f) raises `ValueError` on unregistered key namespace regardless of dialect; (g) handles unbound session (`session.bind is None`) by falling through to the True path; (h) `set_serializable_isolation` calls `connection().execution_options(isolation_level="SERIALIZABLE")` on PG; (i) is a no-op on SQLite; (j) is a no-op on unbound session; (k) end-to-end smoke against a real SQLite engine (`sqlite_engine` fixture) — all three adapter calls run cleanly.

**Commit landed on `m0/04-adapter-boundary` (1).**

1. (this commit) Step 1.4 / M0.4 complete: adapter boundary for Postgres-specific features + 11 unit tests + handoff close-out. 8 files modified/created spanning `app/framework/{adapter,locks,db,history,dispatcher}.py` + smoke fixtures + new test module + planning files.

**Branch ops.** No new branches beyond `m0/04-adapter-boundary`. **Next at Session 34 head:**
```
git checkout m0/foundations
git merge --ff-only m0/04-adapter-boundary
git checkout dev
git merge --no-ff m0/foundations -m "Step 1 / M0 Foundations complete (1.1 + 1.2 + 1.3 + 1.4)"
git tag m0-complete
git checkout -b m1/roster off dev
```
Closes M0 entirely; tag is the rewind anchor for the milestone per [[project-branching-convention]]. Step 2 / M1 Roster opens on `m1/roster`.

**ADRs landed this session (0).** Three forks resolved via chat-side canvass per the STOP-AND-CONFIRM gate; tradeoffs documented in `app/framework/adapter.py`'s module docstring and `test_adapter.py`'s module docstring.

**Memories saved (0 new this session).**

**Files touched.** `backend/app/framework/adapter.py` (new). `backend/app/framework/locks.py` (slimmed). `backend/app/framework/db.py` (slimmed). `backend/app/framework/history.py`. `backend/app/framework/dispatcher.py`. `backend/tests/fixtures/smoketest/entities.py`. `backend/tests/test_adapter.py` (new). `planning/steps.md` (Step 1.4 + Step 1 marked complete). `planning/handoff.md` (this rewrite). `_file-rules.md` **not regenerated** — no `## File contract` block changed this session.

**Verification at session close.** `uv run ruff check .` → All checks passed. `uv run pyright app/ tests/ migrations/` → 0 errors, 0 warnings, 0 informations. `uv run pytest` → 27 passed (11 adapter + 5 integration + 10 dispatcher + 1 healthcheck). `alembic upgrade head` / `downgrade base` cycle against SQLite clean.

---

## Open questions

**For the next session (Session 34 — Step 1 close-out + Step 2 / M1 Roster open):**

- **First branch ops at session head (M0 close-out).** Five mechanical git operations to close M0 entirely and open M1:
  1. `git checkout m0/foundations`
  2. `git merge --ff-only m0/04-adapter-boundary`
  3. `git checkout dev`
  4. `git merge --no-ff m0/foundations -m "Step 1 / M0 Foundations complete (1.1 + 1.2 + 1.3 + 1.4)"` (the `--no-ff` merge produces the milestone-level table-of-contents entry visible via `git log --first-parent dev` per [[preserve-incremental-commits]])
  5. `git tag m0-complete` (rewind anchor per [[project-branching-convention]])
  6. `git checkout -b m1/roster` (new milestone branch off the updated `dev`)
- **Case detection at Session 34 head.** Step 2 / M1 Roster currently has only a stub brief in `planning/steps.md` (no scoped prompt). This is a **Case 2** session head — Session 34 needs to size M1 (Case-2 sizing checklist; partition if any signal fires). M1 candidates per `planning/roadmap.md` § M1: Employee / School / Contractor / User / EmployeeRole / UserRole / ContractorEngagement (7 roster entities); admin CRUD; `grant_user_role` / `revoke_user_role` with audit_reason Notes per ADR-0040; EmployeeRole disjoint-ranges-per-`(employee, role_type, contract)` invariant (ADR-0045); `change_employee_role_rate` 4-branch compound (ADR-0039 + ADR-0045); ContractorEngagement signatures + date defaults (carry-forward landing). **Likely partition signals to expect:** >1 independently-deliberable decision (entity-table-shape vs. admin-CRUD shape vs. EmployeeRole disjoint-ranges enforcement vs. compound-command authoring shape); >1 new artifact (7 entity models + their Alembic migration + admin command modules); cross-concern reach (entity authoring + invariant primitives + admin UI signal); duration >60 min. Sizing the M of M1 honestly probably partitions into 3–4 sub-steps.
- **Read first at session head:** Session 33 summary above + `planning/steps.md` § Step 2 stub + `planning/roadmap.md` § M1 brief + `planning/domain-model.md` § Roster entities + ADR-0040 (audit_reason Note pattern) + ADR-0045 (EmployeeRole disjoint-ranges + change_employee_role_rate 4-branch compound) + ADR-0047 (authorization predicates) + ADR-0059 (Command base class shape) + ADR-0060 (cascade mechanism). Skim `app/framework/command.py` (the abstract Command shape M1+ commands inherit) + `app/framework/dispatcher.py` (the pipeline M1+ commands flow through) + `app/framework/adapter.py` (the adapter call sites M1+ entity-table declarations consume via `json_column`).
- **No ADRs guaranteed yet.** M1 will likely surface ADR-worthy decisions (e.g., admin CRUD generalization shape; how `change_employee_role_rate`'s 4-branch compound decomposes into cascade-invokes; per-invariant primitive choice for EmployeeRole disjoint-ranges already pinned by ADR-0056 D1.c as SERIALIZABLE so that's not in play). ADR numbering: next at write time **ADR-0061** (unused since 1.3b — still available).
- **Commit pattern.** New branch `m1/roster` off `dev` (NOT off `m0/foundations`) per [[project-branching-convention]]: M0 closed, next milestone branches off `dev`. Preserve incremental checkpoints per [[preserve-incremental-commits]]; FF-merge sub-step branches to `m1/roster` (if partitioned); merge `m1/roster` → `dev` with `--no-ff` at M1 close + tag `m1-complete`.

**For Phase 2 broadly (M1+ outlook):**

- **Step 1 / M0 ✓ COMPLETE 2026-05-19 (Session 33).** All four sub-steps landed: 1.1 scaffolding (Session 27); 1.2 data-layer primitives (Session 29 — ADR-0056 + ADR-0057); 1.3a dispatcher pipeline (Session 30 — ADR-0058 + ADR-0059 + ADR-0060); 1.3b history infrastructure (Session 32 — no ADRs); 1.4 adapter boundary (Session 33 — no ADRs). The substrate for every M1+ command is in place: `Command` base class + dispatcher with retry loop, 10 history tables + real `SqlAlchemyCaptureSink`, advisory-lock + isolation primitives behind a documented adapter, Alembic + CI green on SQLite, smoke fixtures demonstrating all three history patterns.
- **PaaS vendor pick stays deferred per ADR-0055.** Do not re-propose a vendor canvass at any future M1+ step session head. See [[project-vendor-pick-deferred]] for the 5 portability discipline notes that constrain forward work.
- **Postgres CI service stays deferred.** Session 33 declined to add docker-compose Postgres to CI; PG-path verification is manual when a developer points `DATABASE_URL` at a real Postgres. If Docker access becomes reliable on the dev machine, revisit by adding `services: postgres:15` to the CI workflow (vendor-agnostic, allowed by ADR-0055's discipline notes — distinct from the still-deferred vendor-coupled ephemeral-PR DB wiring).
- **Smoke fixtures stay as test fakes.** SmokeBase tables created via `SmokeBase.metadata.create_all(engine)` in fixtures (not in Alembic). M1+ domain entities + their history-table FKs land via Alembic migrations.
- **MVP-attempt-1 rewind protocol** (per [[project-branching-convention]]): if implementation attempt 1 tanks, tag `dev` as `attempt-1-archived` (or delete `dev`), recreate `dev` fresh from `main` (or `phase-1-complete` tag), restart at M0. All attempt-1 history preserved through milestone branches + tags. With M0 closed and `m0-complete` tag (pending Session 34 head), the rewind cost is one tag.

**Carried into Phase 2 broadly:**

- **Adapter boundary established (M0.4).** Postgres-specific features live behind `app.framework.adapter` per ADR-0051. M1+ entity-table declarations call `json_column()` from the adapter (not from `db.py`); new advisory-lock invariants land their key-builders in `app.framework.locks` and call the adapter's `try_advisory_xact_lock`; the dispatcher's `set_serializable_isolation` is the single isolation call site. SQLite offline fallback is buildable but **not production-equivalent** (explicit per ADR-0051 + ADR-0052 + ADR-0056).
- **PaaS / vendor portability discipline** (per ADR-0055 + [[project-vendor-pick-deferred]]). Postgres 15+ floor; no vendor-specific extensions without availability check on realistic shortlist; vanilla `psycopg` only; CI stays on docker-compose Postgres when adopted (deferred to circle-back or vendor pick); architecture.md vendor slot stays "deferred per ADR-0055."
- **Carry-forward landings.** All 7 command-shape carry-forwards land in specific milestones per `roadmap.md` § Carry-forward landing index. When each milestone opens, the carry-forwards landing in it should be raised at session head so the brief covers them.
- **MVP carve-out tracking.** `resolve_overlap_paired` (blocker #8 joint compound) ships in M6 conditionally on `split_entry`'s mechanics. If `split_entry` proves heavier than estimated when M6 opens, `resolve_overlap_paired` slips post-MVP per ADR-0050. Re-evaluate at M6 session head.

**Process notes (apply to Phase 2 generally):**

- **STOP-AND-CONFIRM gate stays in force, including for source code.** Each step / sub-step opens with chat-side deliberation before any code or ADR write.
- **Commit pattern: preserve incremental checkpoints; FF to milestone with all checkpoints intact; merge milestone → `dev` with `--no-ff` + tag** (per [[preserve-incremental-commits]] + [[project-branching-convention]]). Each checkpoint = a coherent atomic change at a green-state boundary, with a proper subject (no "wip:" prefix). `git log --first-parent dev` gives the milestone-level table of contents.
- **Contract-drift CI job enforces schema + client are in sync.** Any backend OpenAPI-surface change requires `just gen-openapi` + commit of both `contracts/openapi.json` and `frontend/src/api/` (see [[committed-generated-artifacts]]).
- **`Command` base class + dispatcher is the structural anchor for all of Phase 2.** ADR-0008's atomicity (entity mutation + history write in the same transaction) is framework-enforced via the dispatcher (M0.3 ✓); no handler-level skip. Verify this invariant at every M1+ command-add.
- **Engine-portability discipline (ADR-0051 + ADR-0052).** Postgres-specific features stay behind the adapter (M0.4 ✓); SQLite offline fallback uses degraded equivalents. Explicit not production-equivalent.
- **`mvp.md` is the canonical MVP scope reference.** Adding a feature beyond the 6 must-haves requires a superseding ADR. `mvp.md` § Carve-outs tracks the slip-eligible items; § Command-shape carry-forwards tracks the in-MVP-but-shape-deferred items.

## Next session

**Step 1 close-out (5 git ops at session head) → Step 2 / M1 Roster (Case 2 sizing, then implementation).** Five-step M0 close-out at session head: FF-merge `m0/04-adapter-boundary` → `m0/foundations`; merge `m0/foundations` → `dev` with `--no-ff`; tag `m0-complete` on `dev`; create new branch `m1/roster` off `dev`. After M0 closes, Session 34 runs Case 2 sizing on Step 2 (M1 Roster — the 7 roster entities + admin CRUD + grant/revoke role commands + EmployeeRole disjoint-ranges + ContractorEngagement carry-forward). M1 is sized M in the roadmap; expect partitioning under the fit-checklist (>1 deliberable decision; >1 new artifact; cross-concern reach). No ADRs guaranteed yet — partition shape will signal whether ADR-0061+ lands in M1.

**Execution order within Step 1 (closed):** 1.1 ✓ → original 1.2 closed-by-deferral → 1.2 ✓ (Session 29) → 1.3a ✓ (Session 30) → 1.3b ✓ (Session 32) → 1.4 ✓ (Session 33) → **Step 1 ✓ COMPLETE.** Next branch ops: FF `m0/04-adapter-boundary` → `m0/foundations` → merge `m0/foundations` → `dev` `--no-ff` + tag `m0-complete` → Step 2 (M1 Roster) opens on `m1/roster` off `dev`.

### Prompt for the next session

> Resume work. **Step 1 / M0 Foundations ✓ COMPLETE 2026-05-19 (Session 33).** All four sub-steps landed; the framework substrate is in place for M1+ command authoring. Session 34 is split-purpose: (1) close M0 out with the prescribed branch ops at session head; (2) open Step 2 / M1 Roster via Case 2 sizing.
>
> **First branch ops (do this at session head, before any M1 substance):**
> ```
> git checkout m0/foundations
> git merge --ff-only m0/04-adapter-boundary
> git checkout dev
> git merge --no-ff m0/foundations -m "Step 1 / M0 Foundations complete (1.1 + 1.2 + 1.3 + 1.4)"
> git tag m0-complete
> git checkout -b m1/roster
> ```
> This closes M0 entirely (FF the last sub-step into `m0/foundations`; `--no-ff` merge of `m0/foundations` into `dev` produces the milestone-level table-of-contents entry; `m0-complete` is the rewind anchor) and opens M1 on `m1/roster` off `dev` per [[project-branching-convention]].
>
> **Branch state before close-out:** `m0/04-adapter-boundary` carries 1 commit ahead of `m0/foundations` (Session 33: Step 1.4 complete). After FF + `--no-ff` merge to `dev`, `dev`'s `git log --first-parent` shows one entry per closed milestone — `m0-complete` is the first.
>
> **Case 2 sizing at session head.** After branch ops, run the Case 2 fit-checklist on M1. M1 candidates per `planning/roadmap.md` § M1: 7 roster entities (Employee / School / Contractor / User / EmployeeRole / UserRole / ContractorEngagement) + admin CRUD + `grant_user_role` / `revoke_user_role` (with audit_reason Notes per ADR-0040) + EmployeeRole disjoint-ranges invariant (ADR-0045) + `change_employee_role_rate` 4-branch compound (ADR-0039 + ADR-0045) + ContractorEngagement signatures + date defaults (carry-forward landing). Expect partition signals: >1 independently-deliberable decision, >1 new artifact, cross-concern reach, duration >60 min. Likely partition: 3–4 sub-steps. Propose partition shape via STOP-AND-CONFIRM canvass; wait for approval before writing to `steps.md`.
>
> **Read first:** this prompt + the Open questions block above + the Last session summary (Session 33) + `planning/steps.md` § Step 2 stub + `planning/roadmap.md` § M1 brief + `planning/domain-model.md` § Roster entities (Employee / School / Contractor / User / EmployeeRole / UserRole / ContractorEngagement) + ADR-0040 (audit_reason Note pattern) + ADR-0045 (EmployeeRole disjoint-ranges + change_employee_role_rate 4-branch compound) + ADR-0047 (authorization predicates) + ADR-0059 (Command base class shape) + ADR-0060 (cascade mechanism). Skim `app/framework/command.py` (Command base), `app/framework/dispatcher.py` (pipeline), `app/framework/adapter.py` (json_column for entity tables), `app/framework/history.py` (history-pattern mixins M1+ history tables will reuse if any roster entity carries history — most are audit-log or no-history per `domain-model.md`).
>
> **Pre-flagged for M1 brief:**
> - **Carry-forward:** ContractorEngagement signatures + date defaults (per `planning/roadmap.md` § Carry-forward landing index).
> - **First per-invariant primitive assignment in M1+ code:** EmployeeRole disjoint-ranges is pre-pinned to SERIALIZABLE per ADR-0056 D1.c (not advisory-lock). Record this as a code-comment criterion-application referencing ADR-0056; no new ADR.
> - **History patterns expected:** EmployeeRole + ContractorEngagement = lifecycle (already declared in `app/framework/history.py`); the other 5 roster entities = audit-log or no-history per `domain-model.md`. No new history tables; M1 only adds entity tables + (likely) FKs from existing history tables to the new entity tables.
> - **Admin CRUD shape:** ADR-0047's `role >= admin` predicate applies. Whether to generalize admin CRUD or hand-author each command is a Round-A canvass item.
>
> **Out of scope:**
> - Anything in M0's scope (closed in Sessions 27 / 28 / 29 / 30 / 32 / 33).
> - Project / Sample Batch / WA / RFA / Time Entry / etc. — M2+.
> - PaaS vendor pick — **stays deferred per ADR-0055**.
> - Postgres CI service — stays deferred (Session 33 decision; revisit if Docker access becomes reliable).
>
> **Process notes:**
> - **STOP-AND-CONFIRM gate applies, including for source code.** M1 will surface multiple deliberable decisions (admin CRUD shape, compound-command decomposition, history-pattern wiring per roster entity). Each earns a chat-side canvass before the write.
> - **Commit pattern: preserve incremental checkpoints; FF sub-step branches to `m1/roster`; merge `m1/roster` → `dev` with `--no-ff` + tag `m1-complete`** (per [[preserve-incremental-commits]] + [[project-branching-convention]]).
> - **Branch:** new branch `m1/roster` off `dev` (NOT off `m0/foundations` — M0 is closed). Sub-step partitions (if any) branch off `m1/roster`.
> - **ADR numbering.** Next ADR at write time: **ADR-0061** (unused since 1.3b — still available).
> - **`mvp.md` is the canonical MVP scope reference.**
> - **User-knowledge note.** Per [[user-postgres-concurrency-gap]]: when discussing Postgres-specific data-layer mechanics (JSONB ops, advisory locks, isolation primitives), lean toward grounding terms before reaching for them; offer worked examples when introducing a primitive. Less likely to surface in M1 (mostly entity authoring + admin CRUD) than M0, but the SERIALIZABLE pin on EmployeeRole disjoint-ranges per ADR-0056 D1.c is a touchpoint.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-18)
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 ✓ COMPLETE 2026-05-19 (Session 33) — all 4 sub-steps landed**; Steps 2–9 stubs)
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
