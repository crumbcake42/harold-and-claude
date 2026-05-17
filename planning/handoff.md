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

**Implementation** — Phase 2, current as of 2026-05-17 per ADR-0054 (phase-transition; Conceptualization closed). The 9-milestone roadmap from `planning/roadmap.md` (M0 Foundations → M8 Cutover prep) is the canonical milestone-shape source; `planning/steps.md` mirrors the milestones as 9 steps. **Step 1 (M0) partitioned 2026-05-17 (Option A — substrate-then-decisions) into 5 sub-steps (Step 1.1 → Step 1.5).** Currently on the **`m0/foundations`** branch (milestone integration branch off `dev`; see [[project-branching-convention]] and `planning/phases.md` pointers).

## Last session summary

**Session 25 — Step 9b: consolidation pass + `roadmap.md` + phase-transition ADR + Step 1 partition + branch ops. ✓ COMPLETE (2026-05-17, ADR-0053 + ADR-0054, closes Conceptualization phase; opens Implementation phase + Step 1 partitioned).** Case-3 scoped; ran the session-head sizing check first, then proceeded as a single Case-3 session per the partition mitigation's escape hatch.

**Session-head sizing check finding.** Scan of `decisions.md` for ADRs amended 2+ times turned up **18 ADRs** crossing the literal threshold — far past the session-23 preview's "1 firm + 1–2 borderline" estimate. Per the partition mitigation, this triggered re-running the Case 2 fit checklist on 9b. **Position B-narrowed accepted:** consolidate ADR-0032 alone via ADR-0053; the 17 other 2+-amender ADRs stay standing (their amender chains preserve correctly-readable models). The deviation from the literal "2+ amendments" framing of `steps.md` line 612 is recorded honestly in ADR-0054's Alternatives considered.

**ADR-0053 written (consolidates ADR-0032 — blocker-and-resolution model).** Position 1a (narrow): supersedes ADR-0032 only; ADR-0042 / 0046 / 0049 stay accepted. Position 2a (reread-of-current-model). Body covers current blocker-and-resolution model: Note subtypes (`regular | blocker | resolution | audit_reason | write_off`); polymorphic target; lazy materialization; closure gate = "no registry blocker holds" over not-written-off entities; canonical 10-entry registry (gap-preserving numbering since #1/#2 retired post-keep-FK); registry schema; chain shape `te_batches_by_coverage`; default-resolution command family; nuclear-option guard.

**`planning/roadmap.md` written.** Fork 1b (medium granularity, 9 milestones) + Fork 2a (S/M/L sizing only). Milestone table M0–M8 with per-milestone expansion + ordering rationale + carry-forward landing index for all 7 command-shape carry-forwards + 5 implementation-phase carry-forwards + `resolve_overlap_paired` conditional carve-out + pointers.

**ADR-0054 written (phase-transition).** Records the consolidation-pass deviation honestly; pre-enumerates Phase 3 as a stub. Triggers the four `phases.md` writes (lightweight gate).

**Four `phases.md` writes executed** (lightweight gate): Phase 1 → complete with archive pointer; Phase 2 → current with concrete Goal; `planning/steps.md` archived to `planning/steps.archive/conceptualization.md`; new `planning/steps.md` written; Phase 3 stub appended.

**Branch ops executed (post-completion-protocol, per user-approved branching convention):**

1. Step 9b commit landed on `take1` as `97d5e3e`.
2. FF-merged `take1` → `main` (planning artifacts now on `main`).
3. Tagged `phase-1-complete` at `97d5e3e` on `main` (clean-slate rewind anchor).
4. Created `dev` from `main` (long-lived per-attempt integration branch).
5. Created `m0/foundations` from `dev` (milestone integration branch).
6. Currently checked out on `m0/foundations`. Working tree clean post-Step-1-partition write.

**Branching convention (saved to memory as [[project-branching-convention]]):** `main` (finalized) → `dev` (ongoing implementation; per-attempt, disposable) → `m<N>/<slug>` (milestone working branches off dev) → `m<N>/<sub-slug>` (sub-step branches off the milestone branch, when partitioned). Tags as rewind anchors on `main`: `phase-1-complete` (applied), `m<X>-complete` (per milestone), `mvp-shipped` (at MVP cutover). No type-prefixes (`feature/`, `bugfix/`); no `vN/` prefix.

**Step 1 (M0 Foundations) partitioned 2026-05-17 (Option A — substrate-then-decisions).** Case 2 fit checklist on Step 1 fired signals 1, 2, 3, 4, 5. Option A chosen because (a) M0.1 is mechanical with no deliberation overhead — lets the implementation branch get a cheap first commit (and gives Claude auto mode an easy "no-decisions" first attempt at the workplan); (b) decision sub-steps land in dependency order (PaaS picks Postgres flavor → primitives bind to it → dispatcher consumes the primitives → adapter wraps the Postgres specifics). Option B (decisions-first) rejected — delays mechanical-confidence-building and stacks 2–3 sessions of pure deliberation before any code lands. Option C (3-step coarser partition) rejected — bundles 2–3 substantive decisions in one session, risking the stacking-decisions anti-pattern.

**Five sub-steps (1.1 → 1.5; full briefs in `steps.md` § Step 1):** 1.1 M0.1 Scaffolding (M — cleanup + repo skeletons + CI; no ADRs); 1.2 M0.2 PaaS pick (S — ADR-0055); 1.3 M0.3 Data-layer primitives (S–M — isolation + audit-log timing; ADR-0056, possibly two); 1.4 M0.4 Dispatcher + history infrastructure (L — likely needs further partitioning when opened; ADR-0057 if dispatcher design surfaces ADR-worthy decisions); 1.5 M0.5 Adapter boundary (S; no ADRs expected).

**Files touched:** `planning/decisions.md` (ADR-0053 + ADR-0054 appended; ADR-0032 status flipped). `planning/roadmap.md` (new). `planning/phases.md` (Phase 1/2 flipped; Phase 3 stub added). `planning/steps.md` (replaced — old archived; then Step 1 partitioned into 5 sub-steps inline). `planning/steps.archive/conceptualization.md` (new — archive of the conceptualization-phase steps). `planning/_file-rules.md` (regenerated). `planning/handoff.md` (rewritten for phase-2 + post-partition state). `.claude/memory/project_branching_convention.md` (new — branching convention saved). `.claude/memory/MEMORY.md` (index updated).

---

## Open questions

**For the next session (Step 1.1 / M0.1 — Scaffolding) — surface at session head:**

- **Project-layout decisions in the backend skeleton.** Where do entity definitions live? Where do command classes live? Where does the dispatcher live? Where does the adapter boundary code (Postgres-specific wrappers) live? Per the gate, surface candidate layouts before committing structure. Light decisions — but they shape every M1+ entity addition. Likely candidates: `app/entities/`, `app/commands/`, `app/dispatcher/`, `app/adapters/postgres/`, `app/adapters/sqlite/`. Don't pre-decide — canvass at session head.
- **Project-layout decisions in the frontend skeleton.** Where do generated API hooks live (from openapi-ts)? Where does TanStack Router config live? Light decisions; same canvass rule.
- **Sample command for CI tests.** M0.1's done-when criteria includes "openapi-ts pipeline successfully regenerates the frontend client from a sample backend OpenAPI schema" + "CI is green on a PR-style integration test run." A no-op or healthcheck command is sufficient for the sample; do not introduce a domain entity (those land in M1+).
- **Docker-compose Postgres config for CI.** Pick a Postgres version (15+ per ADR-0052); decide whether to seed any baseline data (likely no — CI tests run from empty schema). Neon ephemeral-branch wiring is deferred to M0.2 (PaaS pick).
- **`make dev` vs. equivalent.** Pick a per-skeleton runner convention. Make / just / npm-script / package.json scripts. Light decision; pick one and document.

**For the milestone (M0 Foundations) broadly:**

- **M0.4 Dispatcher + history infrastructure is sized L — likely needs further partitioning when opened.** Run Case 2 fit checklist at M0.4's session head; candidate seam: dispatcher (pipeline + auth/lifecycle/invariants integration) as one sub-sub-step, history-infrastructure (per-entity table generator + `command_audit_log` + capture wiring) as another.
- **Sub-step branches off `m0/foundations`** per the branching convention. Sub-step merges back into `m0/foundations` with FF. M0 closes when all five sub-steps merge to `m0/foundations`; `m0/foundations` then merges to `dev` with `--no-ff`, tag `m0-complete` on `dev`.
- **MVP-attempt-1 rewind protocol** (per [[project-branching-convention]]): if implementation attempt 1 tanks, tag `dev` as `attempt-1-archived` (or delete `dev`), recreate `dev` fresh from `main` (or `phase-1-complete` tag), restart at M0. All attempt-1 history preserved through milestone branches + tags.

**Carried into Phase 2 broadly:**

- **Adapter boundary scope.** Postgres-specific features live behind the adapter per ADR-0051. M0 establishes the boundary (M0.5); subsequent milestones add features behind it as they need them. SQLite offline fallback is buildable but **not production-equivalent** (explicit per ADR-0051 + ADR-0052).
- **Carry-forward landings.** All 7 command-shape carry-forwards land in specific milestones per `roadmap.md` § Carry-forward landing index. When each milestone opens, the carry-forwards landing in it should be raised at session head so the brief covers them.
- **MVP carve-out tracking.** `resolve_overlap_paired` (blocker #8 joint compound) ships in M6 conditionally on `split_entry`'s mechanics. If `split_entry` proves heavier than estimated when M6 opens, `resolve_overlap_paired` slips post-MVP per ADR-0050. Re-evaluate at M6 session head.

**Process notes (apply to Phase 2 generally):**

- **STOP-AND-CONFIRM gate stays in force, including for source code.** Each step / sub-step opens with chat-side deliberation before any code or ADR write.
- **`Command` base class + dispatcher is the structural anchor for all of Phase 2.** ADR-0008's atomicity (entity mutation + history write in the same transaction) is framework-enforced via the dispatcher (lands in M0.4); no handler-level skip. Verify this invariant at every M1+ command-add.
- **Engine-portability discipline (ADR-0051 + ADR-0052).** Postgres-specific features stay behind the adapter; SQLite offline fallback uses degraded equivalents. Explicit not production-equivalent.
- **`mvp.md` is the canonical MVP scope reference.** Adding a feature beyond the 6 must-haves requires a superseding ADR. `mvp.md` § Carve-outs tracks the slip-eligible items; § Command-shape carry-forwards tracks the in-MVP-but-shape-deferred items.

## Next session

**Step 1.1 — M0.1 Scaffolding.** First sub-step of M0 Foundations; first executable session of Phase 2. Mechanical scaffolding: clean stale `backend/` + `frontend/` directories; stand up backend repo skeleton (FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic + Ruff + Pytest); stand up frontend repo skeleton (Vite + React + TanStack Router + TanStack Query + openapi-ts + Storybook + ESLint + Prettier); wire CI (lint + test + typecheck on PR; docker-compose Postgres in the runner). No ADRs; no domain entities. Brief in `steps.md` → § Step 1.1.

**Branch:** create `m0/01-scaffolding` off `m0/foundations` at session open. Sub-step work happens there; merge back to `m0/foundations` with FF on completion. Two-digit zero-padded sub-step prefix per [[project-branching-convention]] (sorts lexicographically in GitHub branch listings).

**Execution order within Step 1:** 1.1 (this session) → 1.2 → 1.3 → 1.4 → 1.5 → Step 1 ✓ (merge to `dev` with `--no-ff`; tag `m0-complete` on `dev`) → Step 2 (M1 Roster).

### Prompt for the next session

> Resume work. Next is **Step 1.1 — M0.1 Scaffolding** (Phase 2 / Implementation; first sub-step of Step 1 / M0 Foundations). Brief in `steps.md` → § Step 1.1.
>
> **Branch setup at session open:** Currently on `m0/foundations` (milestone integration branch, off `dev`, off `main`). Create `m0/01-scaffolding` off `m0/foundations` for the sub-step work (two-digit zero-padded sub-step prefix sorts lexicographically in GitHub branch listings). Merge back to `m0/foundations` with FF on completion. See [[project-branching-convention]] for full structure.
>
> **Read first:** this prompt + the Open questions block above + `planning/steps.md` § Step 1.1 (full brief) + `planning/roadmap.md` § M0 (canonical milestone shape) + ADR-0001 (stale-scaffolding) + ADR-0051 (runtime stack) + `planning/architecture.md` (component diagram + out-of-band concerns).
>
> **Session-head canvass (per the gate, before any code lands):**
> 1. **Project-layout decisions.** Surface candidate backend + frontend layouts (entity / command / dispatcher / adapter dirs on backend; generated-API-hooks / router-config dirs on frontend). Pick a layout per the user's preference; document in the skeleton.
> 2. **Runner convention.** Pick `make` / `just` / package.json scripts / equivalent. Confirm before writing.
> 3. **Docker-compose Postgres config.** Confirm Postgres 15+; confirm no baseline data seeded; minimal `docker-compose.yml` for CI use.
>
> **In scope (per `steps.md` § Step 1.1):**
> 1. Stale-scaffolding cleanup of `backend/` + `frontend/` (per ADR-0001; cleanup commit separate from skeleton commits).
> 2. Backend repo skeleton: FastAPI healthcheck endpoint runnable via `uvicorn`; Alembic baseline migration; sample `pytest` test runs green; `ruff check` clean; dependency pinning.
> 3. Frontend repo skeleton: Vite dev server runnable; sample TanStack-routed page; `tsc --noEmit` clean; ESLint + Prettier clean; Storybook scaffolding runnable; openapi-ts pipeline wired against a placeholder OpenAPI schema.
> 4. CI workflow(s): lint + test + typecheck + integration test (against docker-compose Postgres) green on PR.
>
> **Out of scope:**
> - PaaS vendor pick (M0.2 / Step 1.2).
> - Per-invariant isolation primitives + audit-log timing (M0.3 / Step 1.3).
> - `Command` base class + dispatcher + history infrastructure (M0.4 / Step 1.4).
> - Adapter boundary code (M0.5 / Step 1.5).
> - Any domain entity / command / handler (M1+).
>
> **Process notes:**
> - **STOP-AND-CONFIRM gate applies to code.** Layout / runner / docker-compose decisions earn a chat-side canvass before files land.
> - **No ADRs in this sub-step.** If a layout decision feels ADR-worthy (e.g., it pre-commits the dispatcher-package shape in a non-trivial way), pause and surface — the dispatcher is M0.4's concern, not M0.1's.
> - **Cleanup commit separate from skeleton commits.** Audit-trail discipline per ADR-0001.
> - **Merge back to `m0/foundations` with FF** when done; do not merge to `dev` yet (`dev` waits until all of M0 lands).
> - **ADR numbering.** Next ADR at write time: **ADR-0055** (M0.2 / Step 1.2).
> - **`mvp.md` is the canonical MVP scope reference.** Adding a feature beyond the 6 must-haves requires a superseding ADR.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-17)
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 partitioned into 5 sub-steps 2026-05-17**; Steps 2–9 stubs)
- Archived step list (Phase 1): `planning/steps.archive/conceptualization.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0054; next ADR at write time: **ADR-0055**)
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
