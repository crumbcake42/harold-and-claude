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

**Implementation** — Phase 2. **Step 1 / M0 Foundations ✓ COMPLETE 2026-05-19 (Session 33).** **Step 2 / M1 Roster** partitioned 2026-05-19 (Session 34, Case 2) into 4 sub-steps. **Step 2.1 / M1.1 Auth substrate + frontend shell ✓ COMPLETE 2026-05-19 (Session 35).** **Step 2.1b / Frontend architecture & conventions** (inserted) ✓ **COMPLETE 2026-05-20** — 2.1b-A (Session 36; ADR-0064/0065) + 2.1b-B (Session 37; ADR-0066). **Step 2.2 / M1.2 Admin substrate + flat roster** partitioned 2026-05-20 (Session 38) into 2.2a/2.2b/2.2c. **Step 2.2a ✓ COMPLETE 2026-05-20 (Session 39)** — branch `m1/02-flat-roster`. **Session 40** found M1.1/M1.2 had drifted from the Session-32 backend design and inserted **Step 2.2b — Backend architecture & conventions** (old 2.2b/2.2c renumbered to 2.2c/2.2d). **Session 41 (2026-05-20)** ran 2.2b: a Case 2 split partitioned it into **2.2b-A** (architecture + ADRs) / **2.2b-B** (conventions docs) / **2.2b-C** (refactor). **Step 2.2b-A ✓ COMPLETE 2026-05-20 (Session 41)** — wrote **ADR-0067–0074**; the structure forks resolved into a **topology reversal** — hexagonal horizontal layers → **vertical feature slices over a shared command engine** (**ADR-0070**), superseding the Session-32/40 hexagonal direction. **Step 2.2b-B ✓ COMPLETE 2026-05-20 (Session 42)** — wrote `backend/CLAUDE.md` + `backend/app/PATTERNS.md`, the backend conventions-doc pair. **Session 43 (2026-05-20)** ran 2.2b-C: a Case 2 check partitioned it into **2.2b-C-1** (structure refactor) / **2.2b-C-2** (audit-column materialization). **Step 2.2b-C-1 ✓ COMPLETE 2026-05-20 (Session 43)** — the M1.1/M1.2 backend moved onto the ADR-0070 vertical-slice layout, behaviour-preserving, in four staged commits. **Step 2.2b-C-2 ✓ COMPLETE 2026-05-21 (Session 44)** — ADR-0072's audit-metadata columns materialized on Contract + User, **ADR-0075** resolving the create-vs-update signal; closes Step 2.2b-C and the inserted Step 2.2b. **Session 45 (2026-05-21)** re-scoped Step 2.2's remaining sub-steps to full-stack entity batching (a Case 2 re-scope, no implementation): **2.2c** is now Contract's frontend admin slice, **2.2d** the four-entity full-stack roster batch. **Next: Session 46 — Step 2.2c / Contract frontend admin.** M1.3 / M1.4 stubs in `steps.md`.

## Last session summary

**Session 45 — Step 2.2 re-scope: full-stack entity batching (2026-05-21).** A planning session — no implementation, no code, no ADR. Branch `m1/02-flat-roster` untouched.

A `_workflow.md` Case 2 re-scope of Step 2.2's remaining sub-steps, on a user decision. The Session-38 decision-first seam (all backends in 2.2a + 2.2c, all five frontends batched in 2.2d) is replaced by **full-stack entity batching** — each batch lands backend + frontend together, so shared abstractions are designed with all of a batch's entities in view rather than extracted retroactively.

- **Step 2.2c** — was "Backend remainder" — is now **Contract frontend admin**: Contract's backend was complete in 2.2a, so its frontend lands as a standalone exemplar slice whose layout templates the other four entities.
- **Step 2.2d** — was "Frontend admin pages (5 entities)" — is now the **roster batch**: Employee / School / Contractor / User built full-stack as one batch, absorbing old 2.2c's backend-remainder scope; Case 2-partitions at its head.
- Sub-step count, execution order, and numbering all unchanged.

**Established: the frontend layout-approval gate** (§ Process notes) — page inventory + an ASCII wireframe per page + IA + interaction flow surfaced in chat for explicit approval before any admin page is implemented; scoped to layout / IA / interaction, not component-level styling. Extends the STOP-AND-CONFIRM gate; applies from 2.2c onward.

**Files updated:** `steps.md`, `handoff.md`, `sessions.md` (restructure-log entry). No ADR; no `_file-rules.md` regeneration (no `## File contract` block changed). Planning-only — changes uncommitted in the working tree.

---

## Open questions

**Queued — frontend follow-ups (post-2.1b; not yet scheduled).** Raised by the user at Session 37 wrap-up; still queued — **not** part of M1.2's sub-steps.

- **Item 1 — theme toggle (small, its own step).** A light / dark / auto toggle in the admin shell header; button at `src/components/ThemeToggleBtn`. Substrate already exists — `src/index.css` has `:root` + `.dark` token blocks and `next-themes` is installed. Work: mount `<ThemeProvider>` from `next-themes` (not currently mounted — the Sonner `Toaster` just degrades to "system"), build `ThemeToggleBtn`, wire it into `pages/admin-shell`. `next-themes`' `enableSystem` gives "auto" free. ~30 min. A small dedicated standalone step — slot it between M1.2 sub-steps or after M1.2; out of scope for 2.2d.
- **Item 2 — themeable architecture (POST-MVP).** A theme registry + user-facing theme dropdown; each theme defines light + dark; a user picks either one theme (both modes) or distinct light/dark themes. Design the schema for the general case: a theme = one named token-value set for a single mode; a user preference = `(lightThemeId, darkThemeId, mode)`. Per-user persistence to a `User` preference is a **backend change** → firmly post-MVP, ADR-worthy when it lands. Not MVP — default theme suffices; not in `mvp.md`'s 6 must-haves. **Prep already done:** `PATTERNS.md` § UI components mandates styling via semantic theme tokens only, which keeps this a drop-in.

**For Step 2.2d (roster batch) — carry-forwards.** `User.employee_id` FK + UNIQUE in the Employee migration (ADR-0061 — M1.1 left it a plain UUID); `seed_db` coverage for all four entities; extract a shared `require_unique` helper from Contract's `_require_unique_number` once User's `username` is the second consumer (ADR-0071). Every new entity is born with `AuditMetadataMixin` + a `creates`-flagged create command (ADR-0072 / ADR-0075). The four-entity backend builds on the post-2.2b vertical-slice structure with audit columns; the frontend portion designs the shared abstractions (`EntityListPage` etc.) with all four entities + Contract's 2.2c exemplar in view, resolving ADR-0064's "extract at the second consumer" deferral.

**For Phase 2 broadly (M1+ outlook):**

- **Step 1 / M0 ✓ COMPLETE 2026-05-19** (Session 33). Substrate for every M1+ command: Command base + dispatcher with retry loop, history infrastructure with real capture sink, advisory-lock + SERIALIZABLE primitives behind a documented adapter, Alembic + CI green on SQLite.
- **Step 2.1 / M1.1 ✓ COMPLETE 2026-05-19** (Session 35). Auth substrate for M1.2+ admin work. Per-role pytest fixtures; concrete Caller flows through dispatcher.
- **Step 2.1b ✓ COMPLETE 2026-05-20** (Sessions 36–37). Frontend four-layer architecture + UI/form stack; `frontend/src/PATTERNS.md` is the conventions doc M1.2 frontend work (2.2d) consumes.
- **Step 2.2a ✓ COMPLETE 2026-05-20** (Session 39). M1.2's three backend abstractions + Contract end-to-end; production dispatcher wired; first M1+ `command_audit_log` writer.
- **Step 2.2b-A ✓ COMPLETE 2026-05-20** (Session 41). Backend architecture settled — vertical feature slices over a shared command engine (ADR-0070); M1.2 closeout ADRs 0067–0074 written; `planning/DRIFTS.md` drift registry created.
- **Step 2.2b-B ✓ COMPLETE 2026-05-20** (Session 42). Backend conventions docs — `backend/CLAUDE.md` + `backend/app/PATTERNS.md`, the backend twin of the frontend doc pair; the prescriptive reference 2.2c+ consumes and `DRIFTS.md` tracks backend drift against.
- **Step 2.2b-C-1 ✓ COMPLETE 2026-05-20** (Session 43). Backend code moved onto the ADR-0070 vertical-slice layout — behaviour-preserving, four staged commits; `app/` now matches `backend/app/PATTERNS.md`'s target structure.
- **Step 2.2b-C-2 ✓ COMPLETE 2026-05-21** (Session 44). ADR-0072's audit-metadata columns materialized on Contract + User; **ADR-0075** settled the create-vs-update signal (declared `Command.creates` flag, refining ADR-0072 so `updated_*` is stamped at creation). Step 2.2b fully closed — the backend is on the ADR-0070 structure with audit columns. Step 2.2c (backend remainder) follows.
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

**Session 46 — Step 2.2c / Contract frontend admin.** Wire Contract's admin frontend — list/overview, create, edit pages + admin-shell nav — on the Step 2.1b four-layer + shadcn/RHF/Zod conventions. Contract's backend landed in 2.2a; this is M1.2's first frontend feature consumer and the exemplar the 2.2d roster batch templates from.

### Prompt for the next session

> Resume work. **Session 45 re-scoped Step 2.2's remaining sub-steps** — a Case 2 re-scope, no implementation. The Session-38 decision-first seam is replaced by full-stack entity batching: **2.2c** is now Contract's frontend admin slice; **2.2d** is the four-entity (Employee / School / Contractor / User) full-stack roster batch. Branch unchanged: `m1/02-flat-roster`.
>
> **Session 46 is Step 2.2c — Contract frontend admin.** Wire Contract's admin frontend as a `src/features/contracts/` slice: list/overview, create, and edit pages + route config + the Contracts admin-shell nav entry, on the Step 2.1b four-layer + shadcn/RHF/Zod conventions. Contract's backend (CRUD + read routes) is already live from 2.2a. This is the **exemplar** — its layout sets the template all five roster entities follow.
>
> **The frontend layout-approval gate is mandatory and heavyweight here.** Before implementing any page, surface in chat — page inventory, an ASCII wireframe per page, information architecture, interaction flow — and wait for explicit approval. Scoped to layout / IA / interaction, not component-level visual styling. See § Process notes — Frontend layout-approval gate.
>
> **Scope (per `steps.md` § Step 2.2c):** **(1)** `src/features/contracts/` slice + an `api/index.ts` barrel over the regenerated client. **(2)** List/overview, create, edit pages in `pages/`; route config in `routes/`. **(3)** The Contracts admin-shell nav entry. **(4)** The bespoke `code_flat_fee_schedule` JSONB editor (Contract-specific — does not generalize). **(5)** Colocated tests + stories. Built **concrete** — no shared `EntityListPage` / `useEntityForm` abstractions yet; those are designed in 2.2d with all four roster entities in view.
>
> **Read first:** `handoff.md` § Open questions + § Process notes; `steps.md` § Step 2.2c; `frontend/src/PATTERNS.md` (the frontend conventions doc — four-layer architecture, feature slices, API barrels, forms); **ADR-0064 / ADR-0065 / ADR-0066**; `frontend/src/auth/` as the working four-layer reference; Contract's OpenAPI surface (`ContractRead`). Regenerate the API client via `pnpm gen-api` before building.
>
> **Process notes:** STOP-AND-CONFIRM gate applies, plus the frontend layout-approval gate. Branch `m1/02-flat-roster` shared across 2.2a–2.2d, FF-merge to `m1/roster` at M1.2 close. No ADR expected for 2.2c; next ADR free: **ADR-0076**. Per-page checkpoint commits per [[preserve-incremental-commits]]. Log any surfaced drift to `planning/DRIFTS.md`.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-20)
- **Drift registry:** `planning/DRIFTS.md` — catalog of drift kinds + instance log; all surfaced drift is logged here. Currently 1 kind: `DRIFT-001` (parallel-definition drift).
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 ✓ COMPLETE (Session 33)**; **Step 2.1 ✓ COMPLETE (Session 35)**; **Step 2.1b ✓ COMPLETE (Sessions 36–37)**; **Step 2.2 partitioned 2026-05-20 (Session 38)**; **Step 2.2a ✓ COMPLETE (Session 39)**; **Step 2.2b inserted Session 40, partitioned into 2.2b-A/2.2b-B/2.2b-C Session 41**; **Step 2.2b-A ✓ COMPLETE 2026-05-20 (Session 41)**; **Step 2.2b-B ✓ COMPLETE 2026-05-20 (Session 42)**; **Step 2.2b-C ✓ COMPLETE — 2.2b-C-1 (Session 43) + 2.2b-C-2 (Session 44); Step 2.2b fully closed 2026-05-21**; M1.3 / M1.4 stubs; Steps 3–9 stubs)
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
