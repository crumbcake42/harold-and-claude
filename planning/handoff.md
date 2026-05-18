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

**Implementation** — Phase 2. The 9-milestone roadmap from `planning/roadmap.md` (M0 Foundations → M8 Cutover prep) is the canonical milestone-shape source; `planning/steps.md` mirrors the milestones as 9 steps. **Step 1 (M0) partitioned into 5 sub-steps (1.1 → 1.5).** **Step 1.1 / M0.1 Scaffolding ✓ COMPLETE 2026-05-18** (Session 27 closed the work Session 26 started; 4 commits landed on `m0/foundations` at `a37db7f`; CI green on all 4 jobs). Currently on the **`m0/foundations`** branch. Next sub-step branch `m0/02-paas-pick` opens off `m0/foundations` at Step 1.2 session head.

## Last session summary

**Session 27 — Step 1.1 / M0.1 Scaffolding ✓ COMPLETE (2026-05-18).** Case-3 scoped continuation of Session 26's in-flight work. All 6 remaining items resolved; 4 clean commits on `m0/foundations`; CI green on all 4 jobs; FF merge landed.

**Resume-point decisions (canvassed at session head; resolved):**
- **Runner: `just`** — already installed locally (handoff was stale on this — `just 1.49.0` was already on PATH). Wrote top-level `justfile` with recipes for install / dev / lint / format / typecheck / test / gen-openapi / ci. `set windows-shell := ["sh", "-c"]` for git-bash compatibility.
- **openapi-ts schema source: committed `contracts/openapi.json` at repo root** — neither side reaches into the other's tree to read/write it. Established the `<root>/contracts/` folder pattern (see [[folder-creation-specificity]] — specific name, not premature). The script lives at `backend/scripts/export_openapi.py` because it imports `from app.main import app` and runs in the backend's uv-managed env; only the artifact crosses the boundary.
- **Commit shape: preserve incremental checkpoints, no squash** — revised mid-session. Agent initially recommended end-of-sub-step squash; user pushed back asking for honest reassessment as a *pattern*; agent reversed (see [[preserve-incremental-commits]]). Force-pushed once to collapse the prior `cfc6400 started scaffolding` emergency-save commit into the next natural checkpoint + reword 3 "M0.1 wip:" subjects to "M0.1:" (they were coherent atomic changes, not WIP).

**Surprise findings.**
- **`pnpm-lock.yaml` 2400-line churn.** Diagnosis: `lockfileVersion: '6.0'` → `'9.0'`. Local pnpm is 10.30.0; the `cfc6400` lockfile was written by some pnpm v8. Same dependency tree, format upgrade only. Resolved by accepting the v9 rewrite + pinning pnpm via `"packageManager": "pnpm@10.30.0"` in `frontend/package.json` (corepack respects this).
- **Frontend lint warning solution.** `react-refresh/only-export-components` doesn't accept `allowExportNames: ["Route"]` for TanStack route files (it still warns about the internal `HomePage` component). Standard solution: disable the rule entirely for `src/routes/**` (TanStack `Route` is a config object, not a hot-reloadable component).
- **`gh` CLI deferred to post-MVP.** User has no admin on this PC; scoop install would work (user-scope) but the value of `gh` is small at this stage (one CI status check per sub-step; 10s in browser). Defer until post-MVP scripting needs justify it.
- **Drift finding flagged at session head.** Handoff said "all Session 26 work uncommitted"; actually `cfc6400 started scaffolding` had landed and was pushed. Coherent tack-on; no action needed beyond noting it.

**Commits landed (on `m0/foundations` at `a37db7f`):**
1. `388b5f1` M0.1: backend + frontend skeletons (lint clean) — squashes the prior `cfc6400` emergency-save + the in-session `d8d230a` (lint clean + skeleton edits) into one coherent commit covering the entire skeleton.
2. `687eaf3` M0.1: justfile (task runner).
3. `d6cbf7c` M0.1: openapi-ts wiring (backend export script + frontend config + generated client at `frontend/src/api/`).
4. `a37db7f` M0.1: GitHub Actions CI workflow (4 jobs: backend, frontend, contract-drift, backend-integration with `services: postgres:16`).

**Branch ops.**
- `m0/01-scaffolding` force-pushed once (cfc6400 + 4 wip → 4 clean commits).
- `m0/01-scaffolding` FF-merged into `m0/foundations` (advanced `a1a6b31..a37db7f`).
- Both branches now at `a37db7f` on origin.
- Local safety branch `m0-01-backup` (pre-rewrite tip at `4df23f2`) preserved one cycle; user can delete.
- Housekeeping: `origin/m0/01-scaffolding` could be deleted (merged; no longer needed). Not done; user's call.

**No ADRs landed this sub-step** (M0.1 was mechanical per the partition plan).

**Memories saved (3 new).** [[preserve-incremental-commits]] (feedback; squashing reflex correction). [[folder-creation-specificity]] (feedback; specific names ≠ premature folder creation). [[committed-generated-artifacts]] (project; both schema + client are committed; CI's `contract-drift` job enforces no-skew).

**Files touched.** `backend/scripts/export_openapi.py` (new). `contracts/openapi.json` (new). `frontend/openapi-ts.config.ts` (new). `frontend/src/api/**` (new — generated client). `frontend/package.json` (packageManager pin + gen-api script). `frontend/eslint.config.js` (src/api/** ignored; routes rule disabled). `frontend/pnpm-lock.yaml` (v9 rewrite). `frontend/.storybook/*`, `frontend/src/{main,routes,tests}/*`, `frontend/vite.config.ts` (session-26 in-flight edits absorbed into the squashed skeleton commit). `justfile` (new, root). `.github/workflows/ci.yml` (new). `.claude/memory/*` (3 new + index updated). `planning/handoff.md` (this rewrite).

---

## Open questions

**For the next session (Session 28 — Step 1.2 / M0.2 — PaaS vendor pick):**

- **Vendor canvass shape.** Two reasonable openings: (i) filter by hard requirements first (managed Postgres availability; region; cost ceiling; ops-familiarity floor) then canvass survivors; (ii) roundtable all candidates first then apply filters. Option (i) is leaner if the filters are crisp; (ii) is fairer if any filter is fuzzy. Pick at session head.
- **Production / dev parity.** Neon is the dev default per ADR-0051. Two postures: (a) stack consistency — pick Neon (or its parent vendor) for both dev + prod; (b) best-tool-for-job in production even if it splits dev/prod. Real consideration: connection-string portability, branching/seeding parity, vendor-specific extensions exposure.

**For the milestone (M0 Foundations) broadly:**

- **M0.4 Dispatcher + history infrastructure is sized L — likely needs further partitioning when opened.** Run Case 2 fit checklist at M0.4's session head; candidate seam: dispatcher (pipeline + auth/lifecycle/invariants integration) as one sub-sub-step, history-infrastructure (per-entity table generator + `command_audit_log` + capture wiring) as another.
- **Sub-step branches off `m0/foundations`** per [[project-branching-convention]]. Sub-step merges back into `m0/foundations` with FF (all checkpoint commits intact — see [[preserve-incremental-commits]]). M0 closes when all five sub-steps merge to `m0/foundations`; `m0/foundations` then merges to `dev` with `--no-ff`, tag `m0-complete` on `dev`.
- **MVP-attempt-1 rewind protocol** (per [[project-branching-convention]]): if implementation attempt 1 tanks, tag `dev` as `attempt-1-archived` (or delete `dev`), recreate `dev` fresh from `main` (or `phase-1-complete` tag), restart at M0. All attempt-1 history preserved through milestone branches + tags.
- **Branch housekeeping carried forward.** `origin/m0/01-scaffolding` is merged and could be deleted (no longer needed). Local `m0-01-backup` (safety branch from M0.1 rewrite) can be deleted now that the merge is verified.

**Carried into Phase 2 broadly:**

- **Adapter boundary scope.** Postgres-specific features live behind the adapter per ADR-0051. M0 establishes the boundary (M0.5); subsequent milestones add features behind it as they need them. SQLite offline fallback is buildable but **not production-equivalent** (explicit per ADR-0051 + ADR-0052).
- **Carry-forward landings.** All 7 command-shape carry-forwards land in specific milestones per `roadmap.md` § Carry-forward landing index. When each milestone opens, the carry-forwards landing in it should be raised at session head so the brief covers them.
- **MVP carve-out tracking.** `resolve_overlap_paired` (blocker #8 joint compound) ships in M6 conditionally on `split_entry`'s mechanics. If `split_entry` proves heavier than estimated when M6 opens, `resolve_overlap_paired` slips post-MVP per ADR-0050. Re-evaluate at M6 session head.

**Process notes (apply to Phase 2 generally):**

- **STOP-AND-CONFIRM gate stays in force, including for source code.** Each step / sub-step opens with chat-side deliberation before any code or ADR write.
- **Commit pattern: preserve incremental checkpoints; FF to milestone with all checkpoints intact** (per [[preserve-incremental-commits]]). Each checkpoint = a coherent atomic change at a green-state boundary, with a proper subject (no "wip:" prefix). `git log --first-parent dev` gives the milestone-level table of contents via the `--no-ff` milestone→dev merge convention.
- **Contract-drift CI job enforces schema + client are in sync.** Any backend OpenAPI-surface change requires `just gen-openapi` + commit of both `contracts/openapi.json` and `frontend/src/api/` (see [[committed-generated-artifacts]]).
- **`Command` base class + dispatcher is the structural anchor for all of Phase 2.** ADR-0008's atomicity (entity mutation + history write in the same transaction) is framework-enforced via the dispatcher (lands in M0.4); no handler-level skip. Verify this invariant at every M1+ command-add.
- **Engine-portability discipline (ADR-0051 + ADR-0052).** Postgres-specific features stay behind the adapter; SQLite offline fallback uses degraded equivalents. Explicit not production-equivalent.
- **`mvp.md` is the canonical MVP scope reference.** Adding a feature beyond the 6 must-haves requires a superseding ADR. `mvp.md` § Carve-outs tracks the slip-eligible items; § Command-shape carry-forwards tracks the in-MVP-but-shape-deferred items.

## Next session

**Step 1.2 — M0.2 PaaS vendor pick + managed-Postgres offering (S).** Substantive deliberation step. ADR-0055 lands here. Branch `m0/02-paas-pick` off `m0/foundations` (which sits at `a37db7f`) at session head.

**Execution order within Step 1:** 1.1 ✓ → **1.2 (next)** → 1.3 → 1.4 → 1.5 → Step 1 ✓ (merge `m0/foundations` to `dev` with `--no-ff`; tag `m0-complete` on `dev`) → Step 2 (M1 Roster).

### Prompt for the next session

> Resume work. **Step 1.2 — M0.2 PaaS vendor pick + managed-Postgres offering** is the next sub-step. Step 1.1 ✓ COMPLETE (Session 27 closed it). This is a substantive deliberation step — NOT mechanical like M0.1. ADR-0055 lands here.
>
> **Branch state:** `m0/foundations` is at `a37db7f` on origin (4 M0.1 commits landed; CI green). Create `m0/02-paas-pick` off `m0/foundations` at session head. Optional housekeeping: delete `origin/m0/01-scaffolding` (merged) and local `m0-01-backup` (M0.1 safety branch, no longer needed).
>
> **Read first:** this prompt + the Open questions block above + the Last session summary (Session 27 — M0.1 closure) + `planning/steps.md` § Step 1.2 brief + `planning/roadmap.md` § M0 item 2 + ADR-0051 (Neon is the dev default).
>
> **Resume-point canvass (before any writes):**
> 1. **Vendor canvass shape.** Filter-first vs. roundtable-first. Per Open questions.
> 2. **Production / dev parity.** Stack consistency (Neon both) vs. best-tool-for-job (split allowed). Per Open questions.
>
> **In scope:**
> - Canvass candidates: managed PaaS bundles (Render / Fly.io / Railway); AWS (RDS + EB / ECS / Lightsail); GCP (Cloud SQL + Cloud Run); Azure (App Service + Azure DB for PostgreSQL); stay-on-Neon (production tier).
> - Trade-offs to surface: managed-bundle simplicity vs. cloud-vendor integration depth vs. cost vs. ops familiarity vs. dev/prod parity.
> - Land ADR-0055 in `planning/decisions.md` with the pick + rationale + alternatives considered.
> - Update `planning/architecture.md` if the vendor pin changes any boundary semantics (Step 8b's File contract: *"the PaaS vendor is pinned at implementation kickoff (vendor name + DB managed-offering name)"*).
>
> **Out of scope:**
> - Per-invariant isolation primitives + audit-log timing (M0.3 / Step 1.3).
> - `Command` base class + dispatcher + history infrastructure (M0.4 / Step 1.4).
> - Adapter boundary code (M0.5 / Step 1.5).
> - Any domain entity / command / handler (M1+).
> - Provisioning the actual production environment (this step picks the vendor; provisioning happens later).
>
> **Process notes:**
> - **STOP-AND-CONFIRM gate applies.** Canvass the vendor deliberation in chat (≤150 words per candidate / position) before writing the ADR.
> - **Commit pattern: preserve incremental checkpoints; FF to milestone, no squash** (per [[preserve-incremental-commits]]).
> - **Sub-step branch convention** (per [[project-branching-convention]]): `m0/02-paas-pick` off `m0/foundations`; FF-merge back when done; do NOT merge to `dev` yet (waits until all 5 sub-steps land).
> - **ADR numbering.** Next ADR at write time: **ADR-0055**.
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
