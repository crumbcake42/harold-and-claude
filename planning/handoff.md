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

**Implementation** — Phase 2. **Step 1 / M0 Foundations ✓ COMPLETE 2026-05-19 (Session 33).** **Step 2 / M1 Roster** partitioned 2026-05-19 (Session 34, Case 2) into 4 sub-steps. **Step 2.1 / M1.1 Auth substrate + frontend shell ✓ COMPLETE 2026-05-19 (Session 35).** **Step 2.1b / Frontend architecture & conventions** (inserted) ✓ **COMPLETE 2026-05-20** — 2.1b-A (Session 36; ADR-0064/0065) + 2.1b-B (Session 37; ADR-0066). **Step 2.2 / M1.2 Admin substrate + flat roster** partitioned 2026-05-20 (Session 38) into 2.2a/2.2b/2.2c. **Step 2.2a ✓ COMPLETE 2026-05-20 (Session 39)** — branch `m1/02-flat-roster`. **Session 40** found M1.1/M1.2 had drifted from the Session-32 backend design and inserted **Step 2.2b — Backend architecture & conventions** (old 2.2b/2.2c renumbered to 2.2c/2.2d). **Session 41 (2026-05-20)** ran 2.2b: a Case 2 split partitioned it into **2.2b-A** (architecture + ADRs) / **2.2b-B** (conventions docs) / **2.2b-C** (refactor). **Step 2.2b-A ✓ COMPLETE 2026-05-20 (Session 41)** — wrote **ADR-0067–0074**; the structure forks resolved into a **topology reversal** — hexagonal horizontal layers → **vertical feature slices over a shared command engine** (**ADR-0070**), superseding the Session-32/40 hexagonal direction. **Step 2.2b-B ✓ COMPLETE 2026-05-20 (Session 42)** — wrote `backend/CLAUDE.md` + `backend/app/PATTERNS.md`, the backend conventions-doc pair. **Session 43 (2026-05-20)** ran 2.2b-C: a Case 2 check partitioned it into **2.2b-C-1** (structure refactor) / **2.2b-C-2** (audit-column materialization). **Step 2.2b-C-1 ✓ COMPLETE 2026-05-20 (Session 43)** — the M1.1/M1.2 backend moved onto the ADR-0070 vertical-slice layout, behaviour-preserving, in four staged commits. **Step 2.2b-C-2 ✓ COMPLETE 2026-05-21 (Session 44)** — ADR-0072's audit-metadata columns materialized on Contract + User, **ADR-0075** resolving the create-vs-update signal; closes Step 2.2b-C and the inserted Step 2.2b. **Session 45 (2026-05-21)** re-scoped Step 2.2's remaining sub-steps to full-stack entity batching (a Case 2 re-scope, no implementation): **2.2c** is now Contract's frontend admin slice, **2.2d** the four-entity full-stack roster batch. **Step 2.2c / Contract frontend admin ✓ COMPLETE 2026-05-21 (Session 46)** — the Contract admin frontend landed and is green. **Session 47 (2026-05-21)** — a focused backend debug session, not a milestone step — fixed the pre-existing SERIALIZABLE-isolation bug that blocked 2.2c's browser dogfood (`set_serializable_isolation` set `isolation_level` after the connection's transaction had autobegun; **ADR-0076** corrects ADR-0058's mechanism), verified the fix against Neon, ran the 2.2c create/edit/delete browser dogfood green, and FF-merged into `m1/02-flat-roster`. **Session 48 (2026-05-21)** ran the Step 2.2d Case 2 sizing — partitioned into **2.2d-1** (roster backend) / **2.2d-2** (shared FE abstractions) / **2.2d-3** (roster FE pages), and pulled the Session-46 routing + skill follow-ups (items 2/3/4) into a dedicated non-milestone slot (`m1/admin-followups`) ahead of 2.2d-1. **Session 49 (2026-05-21)** partitioned that slot (Case 2) into **Slot-A** (routing) / **Slot-B** (skills) and ran **Slot-A ✓ COMPLETE** on branch `m1/admin-followups` — the role-segmented `/admin/*` URL scheme (**ADR-0077**) plus the Contract route migration, browser-dogfooded green. **Session 50 (2026-05-21)** ran **Slot-B ✓ COMPLETE** on `m1/admin-followups` — the two skill follow-ups: `/eval-prompt` gained a keyword-`here` mid-session mode (refines against the live session, freezes the main task, executes on approval), and a new `/assess` skill landed (objective, agenda-free proposal assessment with a calibrated confidence scale). No ADR — skills are `.claude/` harness config. Closes the `m1/admin-followups` slot (`--no-ff` merge back to `m1/02-flat-roster`). **Session 51 (2026-05-21)** partitioned **Step 2.2d-1** (Case 2, signals 2 + 3) into **2.2d-1a** (Employee + Contractor) / **2.2d-1b** (School + User-admin-CRUD) and opened **2.2d-1a**: the pagination contract was settled (**ADR-0078** — page-based wire, offset-based internals, wrapped envelope; Contract exempt) and its substrate + the shared `require_unique` extraction (ADR-0071) landed green; a `/assess` review surfaced **DRIFT-002** (layer-charter erosion — `pagination.py` carries FastAPI into the transport-agnostic engine). The user approved an `engine`/`http` layer rename as the root-cause fix, queued as a non-milestone slot (`m1/engine-http-rename`). 2.2d-1a is partially complete — interrupted before the Employee/Contractor slices. **Session 52 (2026-05-21)** ran the **`engine`/`http` layer rename slot ✓ COMPLETE** on `m1/engine-http-rename` — `app/framework/` → `app/engine/`, a new `app/http/` transport layer (`error_handlers` / `pagination` / `health` moved in; the engine is now FastAPI-free), **ADR-0079** (five-layer taxonomy + charter-check placement rule), ADR-0070 amended, `DRIFT-002` resolved; `--no-ff` merged back to `m1/02-flat-roster`. **Next: the remainder of Step 2.2d-1a** (Employee + Contractor slices, the Alembic migration, `seed_db` coverage, OpenAPI regen), on `m1/02-flat-roster`, built on the post-rename structure. M1.3 / M1.4 stubs in `steps.md`.

## Last session summary

**Session 52 — `engine` / `http` layer rename slot ✓ COMPLETE (2026-05-21).** A Case 3 scoped session; the non-milestone structural slot that is DRIFT-002's root-cause remedy. Behaviour-preserving, three commits on `m1/engine-http-rename`. The session-head 7-signal fit check fired no signal — one session, M.

**The rename.** `app/framework/` → `app/engine/` — the folder holds the framework-*agnostic* command engine, so the old name actively invited framework-coupled code. All `app.framework` imports updated to `app.engine` across 38 files; `git mv` preserved history.

**The `http/` layer.** A fifth top-level layer `app/http/` for cross-cutting FastAPI / transport code: `error_handlers.py`, `pagination.py`, and `health.py` moved in — **Option B**, `health.py` included beyond the brief's literal two files (a healthcheck route is cross-cutting transport code; leaving it at root would have been a fresh charter-erosion instance). The engine is now FastAPI-free — DRIFT-002's root cause removed. `app/` root reduced to `main.py` / `runtime.py` / `config.py`.

**Docs + ADRs.** `backend/app/PATTERNS.md` rewritten for the five-layer taxonomy (stale "until 2.2b-C lands" preamble cleared). **ADR-0079** written — the taxonomy ADR: the rename rationale, the `http/` layer, and a charter-check placement rule (DRIFT-002's standing remedy). ADR-0070 amended in place (layer names + dependency rule); ADR-0078's placement caveat closed. `DRIFT-002` set `resolved` (catalog + log). `backend/CLAUDE.md` left unchanged — it carries no layer names, so the rename touched nothing in it.

**Verification:** 79 backend tests passed + 1 skipped (PG-only), ruff + pyright green, `app.main` assembles (13 routes, unchanged). `--no-ff` merged back to `m1/02-flat-roster`.

**Observation (not acted on):** `ruff format --check` flags ~16 files with pre-existing format drift (present in files only renamed, never content-edited — so it predates this slot). CI runs `ruff check`, not `ruff format`, so it is unenforced. Left untouched to keep the slot behaviour-preserving — surfaced for a possible standalone follow-up or a new DRIFT kind; the user has not yet ruled.

**Files:** `app/framework/` → `app/engine/` (renamed); `app/http/` (new — `__init__.py`, `error_handlers.py`, `pagination.py`, `health.py`); imports updated across `app/` + `tests/`; `backend/app/PATTERNS.md`; `planning/decisions.md` (ADR-0079 + ADR-0070/0078 amendments); `planning/DRIFTS.md` (DRIFT-002 resolved); `steps.md` + `handoff.md`. No `_file-rules.md` regeneration (no `## File contract` block changed).

---

## Open questions

**Queued — frontend follow-ups (post-2.1b; not yet scheduled).** Raised by the user at Session 37 wrap-up; still queued — **not** part of M1.2's sub-steps.

- **Item 1 — theme toggle (small, its own step).** A light / dark / auto toggle in the admin shell header; button at `src/components/ThemeToggleBtn`. Substrate already exists — `src/index.css` has `:root` + `.dark` token blocks and `next-themes` is installed. Work: mount `<ThemeProvider>` from `next-themes` (not currently mounted — the Sonner `Toaster` just degrades to "system"), build `ThemeToggleBtn`, wire it into `pages/admin-shell`. `next-themes`' `enableSystem` gives "auto" free. ~30 min. A small dedicated standalone step — slot it between M1.2 sub-steps or after M1.2; out of scope for 2.2d.
- **Item 2 — themeable architecture (POST-MVP).** A theme registry + user-facing theme dropdown; each theme defines light + dark; a user picks either one theme (both modes) or distinct light/dark themes. Design the schema for the general case: a theme = one named token-value set for a single mode; a user preference = `(lightThemeId, darkThemeId, mode)`. Per-user persistence to a `User` preference is a **backend change** → firmly post-MVP, ADR-worthy when it lands. Not MVP — default theme suffices; not in `mvp.md`'s 6 must-haves. **Prep already done:** `PATTERNS.md` § UI components mandates styling via semantic theme tokens only, which keeps this a drop-in.

**Queued — routing follow-ups (deferred to the `tracker` / `review` surfaces).** Recorded in ADR-0077; built when the coordinator/auditor surfaces land, not before.

- **Per-surface role gating.** The `hasRoleAtLeast(user, role)` pure predicate (frontend twin of backend `has_role_at_least`, ADR-0062), the `requireMinRole(user, role, redirectTo)` `beforeLoad` guard, and a `highestRole(user)` selector. The `admin` layout route has no role gate today — every authenticated user is an admin until M1.3 role administration exists.
- **Top-navbar cross-surface switcher.** The admin shell has only within-surface (sidebar) nav today. When `tracker`/`review` exist, add a top-bar surface switcher showing the surfaces a caller can reach (an `admin` sees admin/tracker/review; an `auditor` sees review only — visibility driven by `hasRoleAtLeast`).
- **Multi-surface dispatch.** `/` and post-login both hard-code `/admin/dashboard` today; they become a role-dispatch to the caller's highest accessible dashboard once more than one surface exists.
- **Login `redirect` / `location` param.** A bounced user is not returned to their intended page after authenticating — `_authenticated.beforeLoad` throws a bare `redirect({ to: '/login' })`. Add the standard search-param round-trip when warranted.

**For Step 2.2d (roster batch) — carry-forwards.** `User.employee_id` FK + UNIQUE in the Employee migration (ADR-0061 — M1.1 left it a plain UUID); `seed_db` coverage for all four entities; extract a shared `require_unique` helper from Contract's `_require_unique_number` once User's `username` is the second consumer (ADR-0071). Every new entity is born with `AuditMetadataMixin` + a `creates`-flagged create command (ADR-0072 / ADR-0075). The four-entity backend builds on the post-2.2b vertical-slice structure with audit columns; the frontend portion designs the shared abstractions (`EntityListPage` etc.) with all four entities + Contract's 2.2c exemplar in view, resolving ADR-0064's "extract at the second consumer" deferral. **Pagination** must be designed into the shared list abstraction (`EntityListPage` / `DataTable`): Contract has ~2 rows so 2.2c's `ContractsTable` is unpaginated, but School will carry a couple hundred entities (raised by the user, Session 46). **QA walkthrough guide** — a reusable end-user-testing walkthrough (per-entity create/edit/delete steps, for non-developer testers) was raised and deferred in Session 47; design its format here with all five entities in view, likely under `docs/qa/`. Out of MVP scope as a product feature — tester-facing process doc, not one of `mvp.md`'s 6 must-haves.

**For Phase 2 broadly (M1+ outlook):**

- **Step 1 / M0 ✓ COMPLETE 2026-05-19** (Session 33). Substrate for every M1+ command: Command base + dispatcher with retry loop, history infrastructure with real capture sink, advisory-lock + SERIALIZABLE primitives behind a documented adapter, Alembic + CI green on SQLite.
- **Step 2.1 / M1.1 ✓ COMPLETE 2026-05-19** (Session 35). Auth substrate for M1.2+ admin work. Per-role pytest fixtures; concrete Caller flows through dispatcher.
- **Step 2.1b ✓ COMPLETE 2026-05-20** (Sessions 36–37). Frontend four-layer architecture + UI/form stack; `frontend/src/PATTERNS.md` is the conventions doc M1.2 frontend work (2.2d) consumes.
- **Step 2.2a ✓ COMPLETE 2026-05-20** (Session 39). M1.2's three backend abstractions + Contract end-to-end; production dispatcher wired; first M1+ `command_audit_log` writer.
- **Step 2.2b-A ✓ COMPLETE 2026-05-20** (Session 41). Backend architecture settled — vertical feature slices over a shared command engine (ADR-0070); M1.2 closeout ADRs 0067–0074 written; `planning/DRIFTS.md` drift registry created.
- **Step 2.2b-B ✓ COMPLETE 2026-05-20** (Session 42). Backend conventions docs — `backend/CLAUDE.md` + `backend/app/PATTERNS.md`, the backend twin of the frontend doc pair; the prescriptive reference 2.2c+ consumes and `DRIFTS.md` tracks backend drift against.
- **Step 2.2b-C-1 ✓ COMPLETE 2026-05-20** (Session 43). Backend code moved onto the ADR-0070 vertical-slice layout — behaviour-preserving, four staged commits; `app/` now matches `backend/app/PATTERNS.md`'s target structure.
- **Step 2.2b-C-2 ✓ COMPLETE 2026-05-21** (Session 44). ADR-0072's audit-metadata columns materialized on Contract + User; **ADR-0075** settled the create-vs-update signal (declared `Command.creates` flag, refining ADR-0072 so `updated_*` is stamped at creation). Step 2.2b fully closed — the backend is on the ADR-0070 structure with audit columns.
- **Step 2.2c ✓ COMPLETE 2026-05-21** (Session 46). Contract admin frontend — the `features/contracts/` slice + admin-shell layout + list/create/edit pages; first M1.2 frontend feature consumer and the 2.2d exemplar. Green on typecheck / lint / test / build. Browser create/edit/delete dogfood passed in Session 47 after the isolation fix — Step 2.2c Done-when closed.
- **Backend SERIALIZABLE-isolation bug ✓ FIXED 2026-05-21** (Session 47). `set_serializable_isolation` applied `isolation_level` after the connection's transaction had autobegun (`InvalidRequestError`, 500ing every command dispatch on Postgres); corrected to apply it at connection procurement. **ADR-0076** records the fix and amends ADR-0058's mechanism. Verified against Neon; a live-PG regression test was added.
- **Backend layer taxonomy ✓ SETTLED 2026-05-21** (Session 52). The `engine`/`http` rename slot — `app/framework/` → `app/engine/` plus a new `app/http/` transport layer — landed behaviour-preserving; **ADR-0079** records the five-layer taxonomy (`engine` / `adapters` / `http` / `auth` / `features`) + a charter-check placement rule; `DRIFT-002` resolved. New backend code: feature slices import from `engine/` + `adapters/` + `http/`; cross-cutting FastAPI code goes in `http/`, never the engine.
- **PaaS vendor pick stays deferred per ADR-0055.** Do not re-propose vendor canvass at any M1+ step head. See [[project-vendor-pick-deferred]].
- **Postgres CI service stays deferred** (Session 33 decision). Revisit if Docker access becomes reliable on the dev machine.
- **Neon dev DB stays current with alembic head per [[project-neon-current-policy]].** Apply migrations to Neon immediately at landing; throwaway sqlite OK for pre-commit iteration only.
- **MVP-attempt-1 rewind protocol** (per [[project-branching-convention]]): with `m0-complete` tag landed, rewind cost to restart M1 from M0 is one tag move. `m1-complete` lands at M1 close.

**Carried into Phase 2 broadly:**

- **Auth substrate (M1.1).** Concrete Caller + per-role pytest fixtures + `current_user` dep + login/logout/me routes are the M1.2+ baseline. M1.2 commands consume `Caller` for ADR-0047 predicates; tests use `as_admin` etc. from `conftest.py`.
- **Adapter boundary (M0.4).** Postgres-specific features live behind the adapter module (`app/adapters/`, relocated there in 2.2b-C-1 per ADR-0070). M1+ entity tables consume `json_column()`; advisory-lock invariants land key-builders in the locks module and call the adapter.
- **PaaS / vendor portability discipline** (ADR-0055 + [[project-vendor-pick-deferred]]). Postgres 15+ floor; no vendor-specific extensions; vanilla `psycopg`; CI on docker-compose Postgres when adopted.
- **Carry-forward landings.** Per `roadmap.md` § Carry-forward landing index. M1's carry-forward: ContractorEngagement signatures + date defaults (lands in M1.4).

**Process notes (apply to Phase 2 generally):**

- **STOP-AND-CONFIRM gate stays in force, including for source code.** Each sub-step opens with chat-side deliberation before any code or ADR write.
- **Frontend layout-approval gate.** Before implementing any admin page, surface in chat — page inventory, an ASCII wireframe per page, information architecture (list vs. detail/form fields, nav placement), and interaction flow (create/edit routing, delete-confirm, validation surfacing) — and wait for explicit approval. Scoped to layout / IA / interaction; component-level visual styling is constrained by shadcn/ui + semantic theme tokens and is not gated. Genuine layout forks get side-by-side ASCII mockups. The exemplar page's review is heavyweight; subsequent same-shape pages are reviewed as deltas. Extends the STOP-AND-CONFIRM gate; applies from Step 2.2c onward.
- **Commit pattern: preserve incremental checkpoints; FF sub-step branches to `m1/roster`; merge `m1/roster` → `dev` with `--no-ff` + tag `m1-complete` at M1 close** (per [[preserve-incremental-commits]] + [[project-branching-convention]]). **Per-entity granularity:** within a multi-entity sub-step, commit after each entity's additions land green.
- **Seed coverage is a standing requirement** (Session 38 / ADR-0069): every entity-adding sub-step from M1.2 onward maintains `seed_db` coverage for the entities it introduces.
- **Contract-drift CI job enforces schema + client are in sync.** Any backend OpenAPI-surface change requires `just gen-openapi` + commit of `contracts/openapi.json` + `frontend/src/api/` (see [[committed-generated-artifacts]]).
- **Cross-check architecture.md out-of-band concerns at every Case 2 sizing** per [[check-out-of-band-concerns]].
- **Log surfaced drift to `planning/DRIFTS.md`.** Any drift surfaced during work — from `_workflow.md`'s resumption checks, code review, or ad hoc — gets a log row under an existing `DRIFT-NNN` label, or a newly proposed one (propose → user confirms → catalogue).
- **`mvp.md` is the canonical MVP scope reference.**
- **Migration discipline per [[project-neon-current-policy]].** Author migration → `uv run alembic upgrade head` against Neon → commit. Throwaway sqlite for shape iteration before commit.

## Next session

**Step 2.2d-1a — remainder: Employee + Contractor backend slices** — the back half of an already-opened, already-scoped Case 3 step, resuming on `m1/02-flat-roster`, built on the post-rename `engine/` + `http/` structure. No new partition (Step 2.2d-1 was partitioned in Session 51; 2.2d-1a is already scoped and partially complete).

### Prompt for the next session

> Resume work. **Step 2.2d-1a — remainder: Employee + Contractor backend slices.** Continue on `m1/02-flat-roster` (the `engine`/`http` rename slot has merged back — no branch op needed). This is the back half of an already-opened, already-scoped Case 3 step — no new fit check, no partition; the pagination contract (ADR-0078) and the `require_unique` extraction (ADR-0071) already landed in Session 51.
>
> Read the **Step 2.2d-1a brief** in `planning/steps.md` — its **Partially complete** note records what landed, its **Concrete attributes** block has the settled Employee / Contractor field shapes. Read `backend/app/PATTERNS.md` (the five-layer taxonomy — feature slices import from `engine/` + `adapters/` + `http/`) and `app/features/contracts/` as the slice exemplar.
>
> Scope: the `features/employees/` + `features/contractors/` slices (`entities` / `commands` / `routes` / `schemas` / `queries`) — each entity born with `AuditMetadataMixin` + a `creates`-flagged create command (ADR-0072 / ADR-0075); the pagination substrate (`app/http/pagination.py`, ADR-0078) applied to the new read routes; Employee's `username` consuming the shared `require_unique` (ADR-0071); `seed_db` coverage for both; one Alembic migration creating the `employee` + `contractor` tables and adding the `User.employee_id` FK + UNIQUE alter (ADR-0061 — the Employee table is its precondition); OpenAPI contract + client regenerated. Per-entity checkpoint commits.
>
> The STOP-AND-CONFIRM gate still applies — open with a chat-side canvass of any non-trivial structural choice before writing. Done when: Employee + Contractor backends flow through the dispatcher; pagination emitted on their read routes; `seed_db` covers both; the `User.employee_id` FK/UNIQUE is migrated; backend tests + ruff + pyright green; migration applied to Neon per [[project-neon-current-policy]]; OpenAPI regenerated. **Step 2.2d-1b** (School + User-admin-CRUD) follows.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-20)
- **Drift registry:** `planning/DRIFTS.md` — catalog of drift kinds + instance log; all surfaced drift is logged here. Currently 2 kinds: `DRIFT-001` (parallel-definition drift — tracking), `DRIFT-002` (layer-charter erosion — ✓ resolved by ADR-0079 / the `engine`/`http` rename slot, Session 52).
- **Session 46 follow-ups:** `planning/follow-ups/session-46-followups.md` — closed historical record, all four items resolved. Items 2/3 (`/eval-prompt` mid-session mode, `/assess` skill) ✓ landed Session 50 / Slot-B; item 4 (routing path-shape) ✓ Session 49 / Slot-A (ADR-0077); item 1 (container/presentational split) folded into Step 2.2d-2's head.
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 ✓ COMPLETE (Session 33)**; **Step 2.1 ✓ COMPLETE (Session 35)**; **Step 2.1b ✓ COMPLETE (Sessions 36–37)**; **Step 2.2 partitioned 2026-05-20 (Session 38)**; **Step 2.2a ✓ COMPLETE (Session 39)**; **Step 2.2b inserted Session 40, partitioned into 2.2b-A/2.2b-B/2.2b-C Session 41**; **Step 2.2b-A ✓ COMPLETE 2026-05-20 (Session 41)**; **Step 2.2b-B ✓ COMPLETE 2026-05-20 (Session 42)**; **Step 2.2b-C ✓ COMPLETE — 2.2b-C-1 (Session 43) + 2.2b-C-2 (Session 44); Step 2.2b fully closed 2026-05-21**; **Step 2.2c ✓ COMPLETE (Session 46)**; **Step 2.2d partitioned Session 48 → 2.2d-1 / 2.2d-2 / 2.2d-3**; M1.3 / M1.4 stubs; Steps 3–9 stubs)
- Archived step list (Phase 1): `planning/steps.archive/conceptualization.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0079; next ADR at write time: **ADR-0080**)
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
