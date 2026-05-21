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

**Implementation** — Phase 2. **Step 1 / M0 Foundations ✓ COMPLETE 2026-05-19 (Session 33).** **Step 2 / M1 Roster** partitioned 2026-05-19 (Session 34, Case 2) into 4 sub-steps. **Step 2.1 / M1.1 Auth substrate + frontend shell ✓ COMPLETE 2026-05-19 (Session 35).** **Step 2.1b / Frontend architecture & conventions** (inserted) ✓ **COMPLETE 2026-05-20** — 2.1b-A (Session 36; ADR-0064/0065) + 2.1b-B (Session 37; ADR-0066). **Step 2.2 / M1.2 Admin substrate + flat roster** partitioned 2026-05-20 (Session 38) into 2.2a/2.2b/2.2c. **Step 2.2a ✓ COMPLETE 2026-05-20 (Session 39)** — branch `m1/02-flat-roster`. **Session 40** found M1.1/M1.2 had drifted from the Session-32 backend design and inserted **Step 2.2b — Backend architecture & conventions** (old 2.2b/2.2c renumbered to 2.2c/2.2d). **Session 41 (2026-05-20)** ran 2.2b: a Case 2 split partitioned it into **2.2b-A** (architecture + ADRs) / **2.2b-B** (conventions docs) / **2.2b-C** (refactor). **Step 2.2b-A ✓ COMPLETE 2026-05-20 (Session 41)** — wrote **ADR-0067–0074**; the structure forks resolved into a **topology reversal** — hexagonal horizontal layers → **vertical feature slices over a shared command engine** (**ADR-0070**), superseding the Session-32/40 hexagonal direction. **Step 2.2b-B ✓ COMPLETE 2026-05-20 (Session 42)** — wrote `backend/CLAUDE.md` + `backend/app/PATTERNS.md`, the backend conventions-doc pair. **Session 43 (2026-05-20)** ran 2.2b-C: a Case 2 check partitioned it into **2.2b-C-1** (structure refactor) / **2.2b-C-2** (audit-column materialization). **Step 2.2b-C-1 ✓ COMPLETE 2026-05-20 (Session 43)** — the M1.1/M1.2 backend moved onto the ADR-0070 vertical-slice layout, behaviour-preserving, in four staged commits. **Step 2.2b-C-2 ✓ COMPLETE 2026-05-21 (Session 44)** — ADR-0072's audit-metadata columns materialized on Contract + User, **ADR-0075** resolving the create-vs-update signal; closes Step 2.2b-C and the inserted Step 2.2b. **Session 45 (2026-05-21)** re-scoped Step 2.2's remaining sub-steps to full-stack entity batching (a Case 2 re-scope, no implementation): **2.2c** is now Contract's frontend admin slice, **2.2d** the four-entity full-stack roster batch. **Step 2.2c / Contract frontend admin ✓ COMPLETE 2026-05-21 (Session 46)** — the Contract admin frontend landed and is green; full browser create/edit/delete dogfood is blocked by a pre-existing backend SERIALIZABLE-isolation bug surfaced during dogfooding. **Next: Session 47 — a focused backend debug session for that bug; then Step 2.2d** (roster batch). M1.3 / M1.4 stubs in `steps.md`.

## Last session summary

**Session 46 — Step 2.2c: Contract frontend admin (2026-05-21).** Branch `m1/02c-contract-frontend` — cut from `m1/02-flat-roster` and held separate until the SERIALIZABLE-isolation bug is fixed. The first M1.2 frontend feature consumer and the exemplar the 2.2d roster batch templates from.

**Landed:** the admin shell promoted from a placeholder page to a **layout** — `_authenticated.tsx` renders `AdminShellLayout` (header + left sidebar nav + `<Outlet/>`); a minimal `pages/dashboard`. The **`features/contracts/` slice** — `api/index.ts` barrel, `form.ts` (Zod schema + form↔API mappers), three mutation hooks, and five components (`ContractsTable`, `ContractForm`, the bespoke `FeeScheduleEditor` JSONB editor, `ValidityBadge`, `DeleteContractDialog`) with colocated tests + stories. List / create / edit **pages** + **routes**, `lib/apiError.ts`, and shadcn `table` / `badge` / `alert-dialog`. The frontend layout-approval gate ran heavyweight (wireframes approved before implementation). `pnpm typecheck` / `lint` / `test` (13/13) / `build` green; API client regenerated, no drift. No ADR (2.2c expected none).

**Two structural corrections on user pushback:**

- **Pages regrouped to nested `pages/<entity>/<page>/`** (`pages/contracts/{list,create,edit}/`) — the assumed flat `pages/contracts-new/` layout was rejected; `frontend/src/PATTERNS.md` amended with a Page-structure section (a refinement within ADR-0064, no new ADR).
- **Routes left on the pre-decision `_authenticated/contracts/...` scheme.** The admin surface should be `/admin/`-prefixed (roles run superadmin → admin → coordinator → auditor); defining the default path shape + migrating these routes is a logged follow-up. Route path structure is now treated as a gated structural decision.

**Blocked:** browser create/edit/delete dogfood — `GET /contracts` works, but `POST` 500s on a **pre-existing backend bug**: `set_serializable_isolation` alters `isolation_level` after the connection's transaction has autobegun (`InvalidRequestError`). PG-only; the SQLite test suite structurally cannot catch it. Out of 2.2c's frontend scope and a pre-existing latent bug (M0.4 vintage) — assigned to a dedicated debug session (Session 47) rather than fixed inline. See § Next session.

**Also (a `/eval-prompt` tangent):** `planning/follow-ups/session-46-followups.md` created — four queued items: a refined frontend design-question prompt (container/presentational split), making `/eval-prompt` mid-session aware, an `/assess` skill, and the routing path-shape decision. Not for the Session 47 debug session — pick up at the Step 2.2d head or a dedicated slot.

**Files:** the frontend slice (admin shell, `features/contracts/`, pages, routes, `lib/apiError.ts`, shadcn primitives, tests, stories), `frontend/src/PATTERNS.md`, `frontend/src/routeTree.gen.ts`; `planning/follow-ups/session-46-followups.md`; planning close-out (`steps.md`, `handoff.md`). No `_file-rules.md` regeneration (no `## File contract` block changed). Changes uncommitted in the working tree.

---

## Open questions

**Queued — frontend follow-ups (post-2.1b; not yet scheduled).** Raised by the user at Session 37 wrap-up; still queued — **not** part of M1.2's sub-steps.

- **Item 1 — theme toggle (small, its own step).** A light / dark / auto toggle in the admin shell header; button at `src/components/ThemeToggleBtn`. Substrate already exists — `src/index.css` has `:root` + `.dark` token blocks and `next-themes` is installed. Work: mount `<ThemeProvider>` from `next-themes` (not currently mounted — the Sonner `Toaster` just degrades to "system"), build `ThemeToggleBtn`, wire it into `pages/admin-shell`. `next-themes`' `enableSystem` gives "auto" free. ~30 min. A small dedicated standalone step — slot it between M1.2 sub-steps or after M1.2; out of scope for 2.2d.
- **Item 2 — themeable architecture (POST-MVP).** A theme registry + user-facing theme dropdown; each theme defines light + dark; a user picks either one theme (both modes) or distinct light/dark themes. Design the schema for the general case: a theme = one named token-value set for a single mode; a user preference = `(lightThemeId, darkThemeId, mode)`. Per-user persistence to a `User` preference is a **backend change** → firmly post-MVP, ADR-worthy when it lands. Not MVP — default theme suffices; not in `mvp.md`'s 6 must-haves. **Prep already done:** `PATTERNS.md` § UI components mandates styling via semantic theme tokens only, which keeps this a drop-in.

**For Step 2.2d (roster batch) — carry-forwards.** `User.employee_id` FK + UNIQUE in the Employee migration (ADR-0061 — M1.1 left it a plain UUID); `seed_db` coverage for all four entities; extract a shared `require_unique` helper from Contract's `_require_unique_number` once User's `username` is the second consumer (ADR-0071). Every new entity is born with `AuditMetadataMixin` + a `creates`-flagged create command (ADR-0072 / ADR-0075). The four-entity backend builds on the post-2.2b vertical-slice structure with audit columns; the frontend portion designs the shared abstractions (`EntityListPage` etc.) with all four entities + Contract's 2.2c exemplar in view, resolving ADR-0064's "extract at the second consumer" deferral. **Pagination** must be designed into the shared list abstraction (`EntityListPage` / `DataTable`): Contract has ~2 rows so 2.2c's `ContractsTable` is unpaginated, but School will carry a couple hundred entities (raised by the user, Session 46).

**For Phase 2 broadly (M1+ outlook):**

- **Step 1 / M0 ✓ COMPLETE 2026-05-19** (Session 33). Substrate for every M1+ command: Command base + dispatcher with retry loop, history infrastructure with real capture sink, advisory-lock + SERIALIZABLE primitives behind a documented adapter, Alembic + CI green on SQLite.
- **Step 2.1 / M1.1 ✓ COMPLETE 2026-05-19** (Session 35). Auth substrate for M1.2+ admin work. Per-role pytest fixtures; concrete Caller flows through dispatcher.
- **Step 2.1b ✓ COMPLETE 2026-05-20** (Sessions 36–37). Frontend four-layer architecture + UI/form stack; `frontend/src/PATTERNS.md` is the conventions doc M1.2 frontend work (2.2d) consumes.
- **Step 2.2a ✓ COMPLETE 2026-05-20** (Session 39). M1.2's three backend abstractions + Contract end-to-end; production dispatcher wired; first M1+ `command_audit_log` writer.
- **Step 2.2b-A ✓ COMPLETE 2026-05-20** (Session 41). Backend architecture settled — vertical feature slices over a shared command engine (ADR-0070); M1.2 closeout ADRs 0067–0074 written; `planning/DRIFTS.md` drift registry created.
- **Step 2.2b-B ✓ COMPLETE 2026-05-20** (Session 42). Backend conventions docs — `backend/CLAUDE.md` + `backend/app/PATTERNS.md`, the backend twin of the frontend doc pair; the prescriptive reference 2.2c+ consumes and `DRIFTS.md` tracks backend drift against.
- **Step 2.2b-C-1 ✓ COMPLETE 2026-05-20** (Session 43). Backend code moved onto the ADR-0070 vertical-slice layout — behaviour-preserving, four staged commits; `app/` now matches `backend/app/PATTERNS.md`'s target structure.
- **Step 2.2b-C-2 ✓ COMPLETE 2026-05-21** (Session 44). ADR-0072's audit-metadata columns materialized on Contract + User; **ADR-0075** settled the create-vs-update signal (declared `Command.creates` flag, refining ADR-0072 so `updated_*` is stamped at creation). Step 2.2b fully closed — the backend is on the ADR-0070 structure with audit columns.
- **Step 2.2c ✓ COMPLETE 2026-05-21** (Session 46). Contract admin frontend — the `features/contracts/` slice + admin-shell layout + list/create/edit pages; first M1.2 frontend feature consumer and the 2.2d exemplar. Green on typecheck / lint / test / build. Browser create/edit/delete dogfood blocked by a pre-existing backend bug → Session 47.
- **Backend SERIALIZABLE-isolation bug — Session 47 focus.** `POST /contracts` (any command dispatch) 500s on real Postgres: `set_serializable_isolation` alters `isolation_level` after the connection's transaction has autobegun. PG-only; the SQLite test suite cannot catch it. Pre-existing (M0.4 vintage). Full brief in § Next session.
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

**Session 47 — Backend SERIALIZABLE-isolation bug fix.** A focused debug session, not a milestone step: `POST /contracts` (any command dispatch) 500s on real Postgres. Fix it, verify against Neon, re-run the 2.2c browser dogfood. Step 2.2d (roster batch) follows.

### Prompt for the next session

> Resume work. **Session 47 is a focused backend debug session** — not a milestone step. Branch `m1/02c-contract-frontend` (the isolated 2.2c branch — the fix lands here so the branch can be dogfooded, then merged back to `m1/02-flat-roster`).
>
> **The bug.** `POST /contracts` against real Postgres returns 500. `app/adapters/postgres.py` → `set_serializable_isolation(session)` runs `session.connection().execution_options(isolation_level="SERIALIZABLE")`. `Session.connection()` autobegins the transaction, and SQLAlchemy then refuses to alter `isolation_level` on a connection with an open transaction — `InvalidRequestError: This connection has already initialized a SQLAlchemy Transaction()`. The dispatcher calls this at `_run_pipeline` entry (`app/framework/dispatcher.py`). The PG branch is dialect-guarded, so the SQLite-only test suite (Step 1.4 — no docker PG in CI) never exercises it; this is the manual-PG-verification catch Step 1.4 anticipated. Pre-existing latent bug (M0.4 vintage), independent of 2.2c's frontend work.
>
> **Scope.** Make the dispatcher's top-level command transaction run at SERIALIZABLE on Postgres, with the SQLite path staying a no-op. The fix likely changes *where/how* isolation is applied — candidates: bind the dispatcher's `session_factory` to an engine carrying `execution_options(isolation_level="SERIALIZABLE")`; apply it via `Session.connection(execution_options=...)` before autobegin; or a connect/begin event hook. **STOP-AND-CONFIRM** — canvass the options before writing; the fix may warrant a wording amendment to ADR-0056 D1.a ("set per-transaction at the dispatcher's top-level pipeline entry").
>
> **Verify** against Neon — the SQLite suite cannot catch this. Confirm a command dispatch commits at SERIALIZABLE; backend tests + ruff + pyright stay green.
>
> **Then** re-run the 2.2c browser dogfood — create / edit / delete a Contract through the running app — closing Step 2.2c's Done-when. **Merge `m1/02c-contract-frontend` → `m1/02-flat-roster`.** Then open **Step 2.2d** (roster batch; Case 2-partitions at its head — see `steps.md` § Step 2.2d).
>
> **Read first:** `app/adapters/postgres.py`; `app/framework/dispatcher.py` (`_run_pipeline` + the `set_isolation` injection in `__init__`); `app/framework/runtime.py` (dispatcher wiring + `session_factory`); `app/adapters/db.py` (engine + sessionmaker); ADR-0052 + ADR-0056.
>
> **Process notes:** STOP-AND-CONFIRM gate applies. Branch `m1/02c-contract-frontend`. Next ADR free: **ADR-0076** (only if the fix amends ADR-0056). `planning/follow-ups/session-46-followups.md` holds four unrelated queued items (a frontend design-question prompt + two skill ideas + the routing path-shape decision) — **not** for this debug session; pick them up at the Step 2.2d head or a dedicated slot.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-20)
- **Drift registry:** `planning/DRIFTS.md` — catalog of drift kinds + instance log; all surfaced drift is logged here. Currently 1 kind: `DRIFT-001` (parallel-definition drift).
- **Session 46 follow-ups:** `planning/follow-ups/session-46-followups.md` — four queued items (frontend design-question prompt, `/eval-prompt` mid-session mode, `/assess` skill, routing path-shape decision). Pick up at the Step 2.2d head or a dedicated slot — not the Session 47 debug session.
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 ✓ COMPLETE (Session 33)**; **Step 2.1 ✓ COMPLETE (Session 35)**; **Step 2.1b ✓ COMPLETE (Sessions 36–37)**; **Step 2.2 partitioned 2026-05-20 (Session 38)**; **Step 2.2a ✓ COMPLETE (Session 39)**; **Step 2.2b inserted Session 40, partitioned into 2.2b-A/2.2b-B/2.2b-C Session 41**; **Step 2.2b-A ✓ COMPLETE 2026-05-20 (Session 41)**; **Step 2.2b-B ✓ COMPLETE 2026-05-20 (Session 42)**; **Step 2.2b-C ✓ COMPLETE — 2.2b-C-1 (Session 43) + 2.2b-C-2 (Session 44); Step 2.2b fully closed 2026-05-21**; **Step 2.2c ✓ COMPLETE (Session 46)**; M1.3 / M1.4 stubs; Steps 3–9 stubs)
- Archived step list (Phase 1): `planning/steps.archive/conceptualization.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0075; next ADR at write time: **ADR-0076**)
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
