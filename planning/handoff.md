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

**Implementation** — Phase 2, current as of 2026-05-17 per ADR-0054 (phase-transition; Conceptualization closed). The 9-milestone roadmap from `planning/roadmap.md` (M0 Foundations → M8 Cutover prep) is the canonical milestone-shape source; `planning/steps.md` mirrors the milestones as 9 steps. **Step 1 (M0) partitioned 2026-05-17 (Option A — substrate-then-decisions) into 5 sub-steps (Step 1.1 → Step 1.5).** Currently on the **`m0/01-scaffolding`** branch (sub-step branch off `m0/foundations`; Step 1.1 in flight — see Session 26 below). Working tree on this branch has uncommitted skeleton work; nothing pushed yet.

## Last session summary

**Session 26 — Step 1.1 / M0.1 Scaffolding. ⚠️ INCOMPLETE — wrapped early (2026-05-17). Backend skeleton fully landed and green; frontend skeleton substantially landed (build/typecheck/vitest green, lint pending auto-fix); openapi-ts wiring, runner choice, and CI not started.** Case-3 scoped; canvass completed; implementation in progress at wrap.

**Branch ops.** Created `m0/01-scaffolding` off `m0/foundations` at session open. No commits yet; all work is uncommitted in the working tree on `m0/01-scaffolding`.

**Surprise finding — cleanup is a no-op.** ADR-0001's stale `backend/` + `frontend/` directories don't exist (user deleted them early; predates conceptualization). The separate cleanup commit collapses; skeletons land into empty space.

**Session-head canvass (approved with two amendments).**
- **Backend layout: layered (kind-first)** — `app/{routes, framework, domain, adapters}/` + `app/main.py` + `app/config.py`. Framework/domain/adapters dirs are placeholders for M0.3/M0.4/M0.5. Pytest in `tests/`. Alembic in `migrations/`.
- **Frontend layout: TanStack Router file-based** — `src/routes/__root.tsx` + `src/routes/index.tsx`. Generated `src/routeTree.gen.ts` (built by `@tanstack/router-plugin` during Vite build; gitignored from ESLint to avoid noise).
- **Runner: `just` orchestrator** — accepted at canvass but `just` is NOT installed locally. Decision deferred to next session: install `just` (scoop install just) OR swap to root-level package.json scripts.
- **Docker-compose Postgres: DROPPED** at user pushback — use GH Actions `services: postgres:` block directly. One less file to maintain. Local Postgres via `docker run` documented in backend README if needed (Neon is the dev default per ADR-0051 anyway).
- **Other picks:** `uv` (Python pkg mgr), `pnpm` (Node pkg mgr — user has it installed; pushed back on initial npm pick), Postgres 16, GH Actions CI single workflow, Vitest+RTL test runner.

**Backend skeleton ✓ green.** `backend/` contains: `pyproject.toml` (FastAPI[standard] + SQLAlchemy 2.0 + Alembic + Pydantic + pydantic-settings + psycopg[binary]; dev: pytest, httpx, ruff), `.python-version` (3.12), `.gitignore`, `app/__init__.py`, `app/main.py` (FastAPI app + healthcheck router include), `app/config.py` (Pydantic Settings: `database_url` env var, defaults to local SQLite per ADR-0051 fallback), `app/routes/healthcheck.py` (`GET /health → {"status": "ok"}`), `app/{framework,domain,adapters}/__init__.py` (placeholders), `tests/test_healthcheck.py`. Alembic initialized via `alembic init migrations` (per [[flag-opaque-scaffolding-files]] — first attempt hand-wrote files; user pushed back asking what `script.py.mako` was; redo via the canonical scaffolder). `alembic.ini` edited (blanked `sqlalchemy.url`); `migrations/env.py` edited (pulls `DATABASE_URL` from `app.config.settings`). Baseline empty migration generated. **Verified:** `uv sync` clean, `pytest` 1 pass, `ruff check` clean (with `migrations/versions` excluded — auto-generated files use `Union[X, None]` not PEP 604).

**Frontend skeleton (substantially landed; lint pending auto-fix).** `frontend/` scaffolded via `pnpm create vite --template react-ts`. Added: `@tanstack/react-router`, `@tanstack/react-query` (runtime); `@tanstack/router-plugin`, `@tanstack/react-router-devtools`, `@tanstack/react-query-devtools`, `@hey-api/openapi-ts`, `prettier`, `eslint-plugin-prettier`, `eslint-config-prettier`, `vitest`, `@testing-library/{react,jest-dom,user-event}`, `jsdom` (dev). Storybook 10.4 hit an upstream autodetect bug (init tried to install non-existent `@storybook/tanstack-react` framework when TanStack Router was present); recovered by installing `@storybook/react-vite` + `@storybook/addon-docs` + `eslint-plugin-storybook` directly and rewriting `.storybook/main.ts` + `.storybook/preview.tsx` to use the real framework. Replaced default `src/App.tsx` with TanStack Router file-based routing (`src/routes/__root.tsx`, `src/routes/index.tsx`) + QueryClient bootstrap in `src/main.tsx`. Updated `vite.config.ts` (uses `vitest/config`; adds TanStack router plugin + Vitest jsdom env + setup file). Wrote `.prettierrc`. `eslint.config.js` extends `eslint-plugin-prettier/recommended` (formatting via ESLint per [[prettier-via-eslint-plugin]]); added route-file rule override (`react-refresh/only-export-components` with `allowExportNames: ['Route']`). Deleted Storybook example stories (used the bad framework name). Added scripts: `test` (vitest run), `typecheck` (tsc -b --noEmit), `lint:fix`. **Verified:** `pnpm build` ✓ (generates routeTree.gen.ts), `pnpm typecheck` ✓, `pnpm test` ✓ (1 sample test passing). **Pending:** `pnpm lint` has 4 Prettier auto-fixes queued; ran the rule override edit but didn't get to verify `pnpm lint:fix` clean before wrap.

**Memories saved (3 new).** [[flag-opaque-scaffolding-files]] (don't batch-write files whose role isn't obvious from filename; prefer framework init commands). [[prettier-via-eslint-plugin]] (wire Prettier through eslint-plugin-prettier, no standalone prettier command). [[storybook-tanstack-autodetect]] — actually, did NOT save this one as a memory; it's session-specific and lives in this handoff. Future re-runs of `storybook@latest init` in a TanStack Router project should skip `--yes` and manually configure.

**Stray cleanup.** `pnpm dlx storybook init` ran with cwd at repo root and dropped a `node_modules/.cache/` (10K) there; deleted. Added top-level `.gitignore` so this can't recur. Deleted `frontend/debug-storybook.log`.

**Files touched.** `backend/` (entire tree, new). `frontend/` (entire tree, new). `.gitignore` (new, top-level). `.claude/memory/feedback_flag_opaque_scaffolding_files.md` (new). `.claude/memory/feedback_prettier_via_eslint_plugin.md` (new). `.claude/memory/MEMORY.md` (index updated). `planning/handoff.md` (this rewrite).

**Incomplete scope (for next session — Session 27, continues Step 1.1):**

1. **Frontend lint clean.** Run `pnpm lint:fix` (4 Prettier auto-fixes pending in `.storybook/preview.tsx` + `vite.config.ts`); verify the `src/routes/**` rule override clears the `react-refresh/only-export-components` error on `index.tsx`. Then `pnpm lint` clean.
2. **openapi-ts wiring (Task #4).** Write `openapi-ts.config.ts` pointing at the FastAPI `/openapi.json` (likely `http://localhost:8000/openapi.json` per Vite proxy or env var). Add `gen-api` script. Test: regenerate types from the live backend schema, commit generated output.
3. **Runner decision (Task #5).** `just` is not installed locally. Two options: (a) install `just` (`scoop install just` on Windows; assets a single binary) and write `justfile` per the canvass plan; (b) swap to root-level package.json scripts (no extra tool; less Python-idiomatic but no install needed). User canvassed (a); the install ask earns a 30-second pause at next session head — reconfirm or swap.
4. **GitHub Actions CI (Task #6).** `.github/workflows/ci.yml` with jobs: backend-lint+test (uv + ruff + pytest), frontend-lint+test+typecheck+build (pnpm), backend-integration (with `services: postgres: image: postgres:16` block per the dropped-compose decision). Trigger on PR.
5. **Push + watch CI (Task #7).** First push of `m0/01-scaffolding` to remote (`git push -u origin m0/01-scaffolding`); confirm CI is green; then sub-step FF-merge to `m0/foundations` per [[project-branching-convention]].
6. **No commit landed this session.** Working tree is uncommitted. Next session opens with the option to either commit-as-progress (one commit "M0.1 scaffolding WIP — backend + frontend skeletons") or wait until lint + openapi-ts + CI all green and commit as one "M0.1 scaffolding" commit. Recommend the single-commit option — closer to the audit-trail discipline carried from ADR-0001.

---

## Open questions

**For the next session (Session 27 — resume Step 1.1 / M0.1 — Scaffolding):**

- **Runner choice (deferred from Session 26 canvass).** User accepted `just` at canvass but `just` is not installed locally. Options: (a) `scoop install just` + write `justfile`; (b) swap to root-level package.json scripts (no extra tool). 30-second decision at session head.
- **openapi-ts schema source.** Two reasonable shapes: (i) point at the live backend (`http://localhost:8000/openapi.json`) — requires backend to be running during `pnpm gen-api`; (ii) export schema to a file (`backend/openapi.json` committed) and have the frontend read from that file. Option (ii) decouples but adds a manual step. Pick one.
- **Commit shape for incomplete-then-complete sub-step.** Recommend one "M0.1 scaffolding" commit landing when everything is green (lint + openapi-ts + CI) rather than progress-checkpoint commits. Audit-trail discipline carried from ADR-0001. Confirm at session head.

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

**Step 1.1 — M0.1 Scaffolding (continuation).** Resume the in-flight sub-step. Backend skeleton ✓ green; frontend skeleton built and green on build/typecheck/test, lint pending one auto-fix pass. Remaining: (1) frontend lint clean; (2) openapi-ts wiring; (3) runner (just vs. package.json scripts); (4) CI workflow; (5) first push + watch CI; (6) one consolidated commit at end.

**Branch:** already on `m0/01-scaffolding`. All Session 26 work is uncommitted in the working tree.

**Execution order within Step 1:** 1.1 (continuing) → 1.2 → 1.3 → 1.4 → 1.5 → Step 1 ✓ (merge `m0/foundations` to `dev` with `--no-ff`; tag `m0-complete` on `dev`) → Step 2 (M1 Roster).

### Prompt for the next session

> Resume work. **Step 1.1 — M0.1 Scaffolding** is in flight (Session 27 continues Session 26's work). Backend skeleton ✓ green. Frontend skeleton built + green on build/typecheck/vitest; lint pending one auto-fix pass. openapi-ts wiring, runner, CI, and the consolidating commit are the remaining surface.
>
> **Branch state:** already on `m0/01-scaffolding`. Session 26 work is uncommitted in the working tree (`git status` will show `backend/`, `frontend/`, `.gitignore`, `planning/handoff.md`, `.claude/memory/*` as untracked/modified).
>
> **Read first:** this prompt + the Open questions block above + the Last session summary (Session 26 — captures every decision and resolution from Session 26's canvass).
>
> **Resume-point checks (before resuming work):**
> 1. **Runner decision.** `just` not installed locally. Pick: (a) `scoop install just` then write `justfile`, or (b) root-level package.json scripts. Confirm at session head.
> 2. **openapi-ts schema source.** Live-server vs. committed-file. Pick at session head (see Open questions).
> 3. **Commit shape.** Recommend one "M0.1 scaffolding" commit when everything green. Confirm at session head.
>
> **Remaining in scope:**
> 1. **Frontend lint clean.** `pnpm lint:fix` (4 Prettier auto-fixes); verify route-file rule override clears `react-refresh/only-export-components` on `src/routes/index.tsx`. Then `pnpm lint` clean.
> 2. **openapi-ts wiring.** `openapi-ts.config.ts` + `gen-api` script; regenerate types; commit generated output.
> 3. **Runner.** Per the resume-point decision.
> 4. **GitHub Actions CI.** `.github/workflows/ci.yml` with backend (uv + ruff + pytest) + frontend (pnpm lint+test+typecheck+build) + backend-integration (with `services: postgres: image: postgres:16`).
> 5. **First push + CI verification.** `git push -u origin m0/01-scaffolding`; watch CI green.
> 6. **Single commit "M0.1 scaffolding"** when everything green. Then sub-step FF-merge to `m0/foundations` per [[project-branching-convention]].
>
> **Out of scope (unchanged):**
> - PaaS vendor pick (M0.2 / Step 1.2).
> - Per-invariant isolation primitives + audit-log timing (M0.3 / Step 1.3).
> - `Command` base class + dispatcher + history infrastructure (M0.4 / Step 1.4).
> - Adapter boundary code (M0.5 / Step 1.5).
> - Any domain entity / command / handler (M1+).
>
> **Process notes:**
> - **STOP-AND-CONFIRM gate applies to code.** Resume-point decisions earn a chat-side canvass before files land.
> - **No ADRs in this sub-step.** If a residual decision feels ADR-worthy, pause and surface.
> - **Storybook 10.4 + TanStack Router autodetect bug** — if you re-run `storybook init` for any reason, do NOT pass `--yes`; it will try to install the phantom `@storybook/tanstack-react` framework. Session 26 worked around by installing `@storybook/react-vite` directly and rewriting `.storybook/main.ts`.
> - **Merge back to `m0/foundations` with FF** when done; do not merge to `dev` yet (`dev` waits until all of M0 lands).
> - **ADR numbering.** Next ADR at write time: **ADR-0055** (M0.2 / Step 1.2).
> - **`mvp.md` is the canonical MVP scope reference.**

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
