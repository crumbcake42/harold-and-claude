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

**Implementation** — Phase 2. **Step 1 / M0 Foundations ✓ COMPLETE 2026-05-19 (Session 33).** **Step 2 / M1 Roster** partitioned 2026-05-19 (Session 34, Case 2) into 4 sub-steps. **Step 2.1 / M1.1 Auth substrate + frontend shell ✓ COMPLETE 2026-05-19 (Session 35).** **Step 2.1b / Frontend architecture & conventions** (inserted) ✓ **COMPLETE 2026-05-20** — 2.1b-A (Session 36; ADR-0064/0065) + 2.1b-B (Session 37; ADR-0066). **Step 2.2 / M1.2 Admin substrate + flat roster** partitioned 2026-05-20 (Session 38) into 2.2a/2.2b/2.2c. **Step 2.2a ✓ COMPLETE 2026-05-20 (Session 39)** — branch `m1/02-flat-roster`. **Session 40** found M1.1/M1.2 had drifted from the Session-32 backend design and inserted **Step 2.2b — Backend architecture & conventions** (old 2.2b/2.2c renumbered to 2.2c/2.2d). **Session 41 (2026-05-20)** ran 2.2b: a Case 2 split partitioned it into **2.2b-A** (architecture + ADRs) / **2.2b-B** (conventions docs) / **2.2b-C** (refactor). **Step 2.2b-A ✓ COMPLETE 2026-05-20 (Session 41)** — wrote **ADR-0067–0074**; the structure forks resolved into a **topology reversal** — hexagonal horizontal layers → **vertical feature slices over a shared command engine** (**ADR-0070**), superseding the Session-32/40 hexagonal direction. **Step 2.2b-B ✓ COMPLETE 2026-05-20 (Session 42)** — wrote `backend/CLAUDE.md` + `backend/app/PATTERNS.md`, the backend conventions-doc pair. **Session 43 (2026-05-20)** ran 2.2b-C: a Case 2 check partitioned it into **2.2b-C-1** (structure refactor) / **2.2b-C-2** (audit-column materialization). **Step 2.2b-C-1 ✓ COMPLETE 2026-05-20 (Session 43)** — the M1.1/M1.2 backend moved onto the ADR-0070 vertical-slice layout, behaviour-preserving, in four staged commits. **Next: Session 44 — Step 2.2b-C-2** (ADR-0072 audit columns; closes 2.2b-C). M1.3 / M1.4 stubs in `steps.md`.

## Last session summary

**Session 43 — Step 2.2b-C-1 / backend structure refactor (2026-05-20).** Branch `m1/02-flat-roster`. A behaviour-preserving refactor moving the M1.1/M1.2 backend onto ADR-0070's vertical-slice layout — no application-behaviour change, no schema change, no ADR.

Case 2 check ran at session head (the step brief + the user both required it): three signals fired — duration (~90–120 min combined), input reading (>1000 LOC held in context for a whole-tree refactor), cross-concern (code topology vs. dispatcher pipeline behaviour). Step 2.2b-C partitioned into **2.2b-C-1** (structure refactor — this session) / **2.2b-C-2** (audit-column materialization — next).

**Four staged commits on `m1/02-flat-roster`, each green** (`938405a` → `f1dd91d`):

- **(1/4) `adapters/` extraction** — `db.py` / `adapter.py`→`postgres.py` / `history.py` moved out of `framework/` into `adapters/`; `capture.py` split (port + record types + test stubs stay in `framework/`, the concrete `SqlAlchemyCaptureSink` → `adapters/capture.py`). The one genuine decision — the `framework → adapters` dependency the move would create via the dispatcher — resolved as canvassed/approved (Option A): `set_isolation` / `try_advisory_lock` are injected into `Dispatcher.__init__` and wired by `runtime.build_dispatcher`. This extends ADR-0059's constructor-injection pattern; documented in the `Dispatcher` docstring; **no new ADR, no decisions.md amendment**.
- **(2/4) `auth/` module** — `entities` (←`domain/auth.py`) / `security` (←`framework/auth.py`) / `routes` (←`routes/auth.py`) / `schemas` (extracted `LoginRequest`); `__init__.py` re-exports `current_user`.
- **(3/4) `features/contracts/` slice** — `entities` / `commands` / `routes` / `schemas` (extracted DTOs) / `queries` (extracted read logic); `domain/predicates.py` → `framework/predicates.py`; `app/domain/` removed.
- **(4/4) hoist** — `runtime.py` + `error_handlers.py` to `app/` root, `routes/healthcheck.py` → `app/health.py`, `routes/` removed.

`app/` now matches ADR-0070 exactly: `framework/` + `adapters/` + `auth/` + `features/<entity>/` + `cli/` + the root composition files. The dependency rule is audited — `framework/` imports nothing from `adapters/` / `auth/` / `features/`.

**Verification:** 71 backend tests + ruff + pyright green at every commit. OpenAPI contract + frontend client regenerated — structurally byte-identical; the sole delta is the `Caller` model's `description` string, propagated from a corrected stale docstring path (`app.framework.auth` → `app.auth`). No migration (no schema change). No ADR — behaviour-preserving.

**Carried to 2.2b-C-2:** `backend/CLAUDE.md` + `backend/app/PATTERNS.md` still carry the "until the Step 2.2b-C refactor lands, the code has the M1.1/M1.2 layout" caveat — now half-stale (structure landed; audit columns pending). 2.2b-C-2 drops that caveat when it closes 2.2b-C.

No ADRs. `_file-rules.md` not regenerated — no `planning/` file's `## File contract` block changed.

---

## Open questions

**Queued — frontend follow-ups (post-2.1b; not yet scheduled).** Raised by the user at Session 37 wrap-up; still queued — **not** part of M1.2's sub-steps.

- **Item 1 — theme toggle (small, its own step).** A light / dark / auto toggle in the admin shell header; button at `src/components/ThemeToggleBtn`. Substrate already exists — `src/index.css` has `:root` + `.dark` token blocks and `next-themes` is installed. Work: mount `<ThemeProvider>` from `next-themes` (not currently mounted — the Sonner `Toaster` just degrades to "system"), build `ThemeToggleBtn`, wire it into `pages/admin-shell`. `next-themes`' `enableSystem` gives "auto" free. ~30 min. A small dedicated standalone step — slot it between M1.2 sub-steps or after M1.2; out of scope for 2.2d.
- **Item 2 — themeable architecture (POST-MVP).** A theme registry + user-facing theme dropdown; each theme defines light + dark; a user picks either one theme (both modes) or distinct light/dark themes. Design the schema for the general case: a theme = one named token-value set for a single mode; a user preference = `(lightThemeId, darkThemeId, mode)`. Per-user persistence to a `User` preference is a **backend change** → firmly post-MVP, ADR-worthy when it lands. Not MVP — default theme suffices; not in `mvp.md`'s 6 must-haves. **Prep already done:** `PATTERNS.md` § UI components mandates styling via semantic theme tokens only, which keeps this a drop-in.

**For Step 2.2b-C-2 — audit-column materialization.** Step 2.2b-C-1 (structure refactor) ✓ COMPLETE Session 43 — the backend code is now on the ADR-0070 vertical-slice layout. 2.2b-C-2 materializes ADR-0072's `created_*/updated_*` audit-metadata columns on Contract + User: the four columns on each entity (consider a shared mixin), an Alembic migration applied to Neon, a dispatcher stamping step + a create-vs-update signal, read-schema fields, OpenAPI contract + client regenerated. The lone open decision is the create-vs-update signal — likely **ADR-0075** if non-obvious. Closing 2.2b-C-2 also drops the now-half-stale "until the refactor lands" caveat from `backend/CLAUDE.md` + `backend/app/PATTERNS.md`.

**For Step 2.2c (backend remainder) — carry-forwards.** `User.employee_id` FK + UNIQUE in the Employee migration (ADR-0061 — M1.1 left it a plain UUID); `seed_db` coverage for all four entities; extract a shared `require_unique` helper from Contract's `_require_unique_number` once User's `username` is the second consumer (ADR-0071). 2.2c builds on the post-2.2b-C vertical-slice structure.

**For Phase 2 broadly (M1+ outlook):**

- **Step 1 / M0 ✓ COMPLETE 2026-05-19** (Session 33). Substrate for every M1+ command: Command base + dispatcher with retry loop, history infrastructure with real capture sink, advisory-lock + SERIALIZABLE primitives behind a documented adapter, Alembic + CI green on SQLite.
- **Step 2.1 / M1.1 ✓ COMPLETE 2026-05-19** (Session 35). Auth substrate for M1.2+ admin work. Per-role pytest fixtures; concrete Caller flows through dispatcher.
- **Step 2.1b ✓ COMPLETE 2026-05-20** (Sessions 36–37). Frontend four-layer architecture + UI/form stack; `frontend/src/PATTERNS.md` is the conventions doc M1.2 frontend work (2.2d) consumes.
- **Step 2.2a ✓ COMPLETE 2026-05-20** (Session 39). M1.2's three backend abstractions + Contract end-to-end; production dispatcher wired; first M1+ `command_audit_log` writer.
- **Step 2.2b-A ✓ COMPLETE 2026-05-20** (Session 41). Backend architecture settled — vertical feature slices over a shared command engine (ADR-0070); M1.2 closeout ADRs 0067–0074 written; `planning/DRIFTS.md` drift registry created.
- **Step 2.2b-B ✓ COMPLETE 2026-05-20** (Session 42). Backend conventions docs — `backend/CLAUDE.md` + `backend/app/PATTERNS.md`, the backend twin of the frontend doc pair; the prescriptive reference 2.2c+ consumes and `DRIFTS.md` tracks backend drift against.
- **Step 2.2b-C-1 ✓ COMPLETE 2026-05-20** (Session 43). Backend code moved onto the ADR-0070 vertical-slice layout — behaviour-preserving, four staged commits; `app/` now matches `backend/app/PATTERNS.md`'s target structure. 2.2b-C-2 (audit columns) closes 2.2b-C.
- **PaaS vendor pick stays deferred per ADR-0055.** Do not re-propose vendor canvass at any M1+ step head. See [[project-vendor-pick-deferred]].
- **Postgres CI service stays deferred** (Session 33 decision). Revisit if Docker access becomes reliable on the dev machine.
- **Neon dev DB stays current with alembic head per [[project-neon-current-policy]].** Apply migrations to Neon immediately at landing; throwaway sqlite OK for pre-commit iteration only.
- **MVP-attempt-1 rewind protocol** (per [[project-branching-convention]]): with `m0-complete` tag landed, rewind cost to restart M1 from M0 is one tag move. `m1-complete` lands at M1 close.

**Carried into Phase 2 broadly:**

- **Auth substrate (M1.1).** Concrete Caller + per-role pytest fixtures + `current_user` dep + login/logout/me routes are the M1.2+ baseline. M1.2 commands consume `Caller` for ADR-0047 predicates; tests use `as_admin` etc. from `conftest.py`.
- **Adapter boundary (M0.4).** Postgres-specific features live behind the adapter module (`app.framework.adapter` today; relocates to `app/adapters/` per ADR-0070 at 2.2b-C). M1+ entity tables consume `json_column()`; advisory-lock invariants land key-builders in the locks module and call the adapter.
- **PaaS / vendor portability discipline** (ADR-0055 + [[project-vendor-pick-deferred]]). Postgres 15+ floor; no vendor-specific extensions; vanilla `psycopg`; CI on docker-compose Postgres when adopted.
- **Carry-forward landings.** Per `roadmap.md` § Carry-forward landing index. M1's carry-forward: ContractorEngagement signatures + date defaults (lands in M1.4).

**Process notes (apply to Phase 2 generally):**

- **STOP-AND-CONFIRM gate stays in force, including for source code.** Each sub-step opens with chat-side deliberation before any code or ADR write.
- **Commit pattern: preserve incremental checkpoints; FF sub-step branches to `m1/roster`; merge `m1/roster` → `dev` with `--no-ff` + tag `m1-complete` at M1 close** (per [[preserve-incremental-commits]] + [[project-branching-convention]]). **Per-entity granularity:** within a multi-entity sub-step, commit after each entity's additions land green.
- **Seed coverage is a standing requirement** (Session 38 / ADR-0069): every entity-adding sub-step from M1.2 onward maintains `seed_db` coverage for the entities it introduces.
- **Contract-drift CI job enforces schema + client are in sync.** Any backend OpenAPI-surface change requires `just gen-openapi` + commit of `contracts/openapi.json` + `frontend/src/api/` (see [[committed-generated-artifacts]]).
- **Cross-check architecture.md out-of-band concerns at every Case 2 sizing** per [[check-out-of-band-concerns]].
- **Log surfaced drift to `planning/DRIFTS.md`.** Any drift surfaced during work — from `_workflow.md`'s resumption checks, code review, or ad hoc — gets a log row under an existing `DRIFT-NNN` label, or a newly proposed one (propose → user confirms → catalogue).
- **`mvp.md` is the canonical MVP scope reference.**
- **Migration discipline per [[project-neon-current-policy]].** Author migration → `uv run alembic upgrade head` against Neon → commit. Throwaway sqlite for shape iteration before commit.

## Next session

**Session 44 — Step 2.2b-C-2 / Audit-column materialization.** Materialize ADR-0072's `created_*/updated_*` audit-metadata columns on Contract + User, on the post-2.2b-C-1 vertical-slice structure. Closes Step 2.2b-C and the inserted Step 2.2b; Step 2.2c (backend remainder — Employee / School / Contractor / User-admin-CRUD) follows.

### Prompt for the next session

> Resume work. **Session 43 completed Step 2.2b-C-1** — the behaviour-preserving backend structure refactor onto ADR-0070's vertical-slice layout (`framework/` + `adapters/` + `auth/` + `features/contracts/`), four staged commits, 71 tests / ruff / pyright green. Branch unchanged: `m1/02-flat-roster`.
>
> **Session 44 is Step 2.2b-C-2 — the ADR-0072 audit-column materialization.** Add the four `created_at` / `created_by` / `updated_at` / `updated_by` columns to Contract and User. They are written **uniformly by the dispatcher** — `created_*` on the creating command, `updated_*` on every later mutating command — and **never by a handler**; they are a dispatcher-maintained read projection over `command_audit_log` + the history tables (ADR-0072).
>
> **Scope:** **(1)** the four columns on `features/contracts/entities.py`'s Contract + `auth/entities.py`'s User — consider a shared mixin or declarative-base addition. **(2)** an Alembic migration adding the eight columns, applied to the Neon dev DB per [[project-neon-current-policy]] (`uv run alembic upgrade head` → commit). **(3)** a dispatcher stamping step in `framework/dispatcher.py` (`_run_steps`) + a **create-vs-update signal** — how the dispatcher knows a command created vs. mutated its target. This is the lone open decision: **STOP-AND-CONFIRM canvass at session head**; likely **ADR-0075** if non-obvious. **(4)** read-schema fields — `features/contracts/schemas.py`'s `ContractRead` (and any User read schema) surface the four columns. **(5)** green — backend tests + ruff + pyright, OpenAPI contract + client regenerated; and drop the now-half-stale "until the Step 2.2b-C refactor lands" caveat from `backend/CLAUDE.md` + `backend/app/PATTERNS.md` (the structure landed in 2.2b-C-1; 2.2b-C-2 closes 2.2b-C).
>
> **Read first:** `handoff.md` § Session 43 summary + § Open questions "For Step 2.2b-C-2"; **ADR-0072** (audit columns) + **ADR-0073** in `decisions.md`; `backend/app/PATTERNS.md` § Audit-metadata columns; `data-model.md` § Conventions (the audit-metadata column kind); `steps.md` § Step 2.2b-C-2; `backend/app/framework/dispatcher.py` (the stamping step slots into `_run_steps`); the Contract + User entities + `ContractRead` schema.
>
> **Process notes:** STOP-AND-CONFIRM gate applies, including for source code. Branch `m1/02-flat-roster` shared across 2.2a–2.2d, FF-merge to `m1/roster` at M1.2 close. Next ADR free: **ADR-0075**. Migration discipline per [[project-neon-current-policy]] — author migration → apply to Neon → commit; throwaway SQLite for pre-commit shape iteration only. Log any surfaced drift to `planning/DRIFTS.md`.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-20)
- **Drift registry:** `planning/DRIFTS.md` — catalog of drift kinds + instance log; all surfaced drift is logged here. Currently 1 kind: `DRIFT-001` (parallel-definition drift).
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 ✓ COMPLETE (Session 33)**; **Step 2.1 ✓ COMPLETE (Session 35)**; **Step 2.1b ✓ COMPLETE (Sessions 36–37)**; **Step 2.2 partitioned 2026-05-20 (Session 38)**; **Step 2.2a ✓ COMPLETE (Session 39)**; **Step 2.2b inserted Session 40, partitioned into 2.2b-A/2.2b-B/2.2b-C Session 41**; **Step 2.2b-A ✓ COMPLETE 2026-05-20 (Session 41)**; **Step 2.2b-B ✓ COMPLETE 2026-05-20 (Session 42)**; **Step 2.2b-C partitioned into 2.2b-C-1 / 2.2b-C-2; 2.2b-C-1 ✓ COMPLETE 2026-05-20 (Session 43)**; M1.3 / M1.4 stubs; Steps 3–9 stubs)
- Archived step list (Phase 1): `planning/steps.archive/conceptualization.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0074; next ADR at write time: **ADR-0075**)
- **Roadmap (Step 9b output):** `planning/roadmap.md` — 9 milestones (M0 → M8). Canonical milestone-shape source for Phase 2.
- **MVP scope (Step 7 output):** `planning/mvp.md` — 6 must-have features + categorized "not now" list + 1 carve-out + 7 command-shape carry-forwards.
- **Domain model (Step 6d output):** `planning/domain-model.md` — 21 entities, relationship table, per-entity lifecycles, authorization predicates (via ADR-0047), history patterns, delete policy, 14 design patterns, blocker registry, vocabulary.
- **Data model (Step 9a output):** `planning/data-model.md` — conceptual data model: 21 entity sections + conventions block + history-table shapes per ADR-0052.
- **Architecture (Step 8b output):** `planning/architecture.md` — one-page sketch: component diagram, boundary semantics, 10-step data flow, **out-of-band concerns** — cross-check at every Case 2 sizing per [[check-out-of-band-concerns]].
- **Consolidated blocker model (Session 25 / ADR-0053):** `planning/decisions.md` § ADR-0053.
- **Phase-transition (Session 25 / ADR-0054):** `planning/decisions.md` § ADR-0054.
- **Branching convention (memory):** [[project-branching-convention]] — `main` → `dev` → `m<N>/<slug>` → `m<N>/<sub-slug>`; tags on `dev` as rewind anchors (`m0-complete` applied 2026-05-19; `m<X>-complete` per milestone; `mvp-shipped` at MVP cutover).
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md` (superseded by `mvp.md` § Not now; retained for trace continuity)
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
