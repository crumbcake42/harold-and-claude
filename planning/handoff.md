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

**Implementation** — Phase 2. The 9-milestone roadmap from `planning/roadmap.md` (M0 Foundations → M8 Cutover prep) is the canonical milestone-shape source; `planning/steps.md` mirrors the milestones as 9 steps. **Step 1 (M0) was partitioned 2026-05-17 into 5 sub-steps (1.1 → 1.5); collapsed 2026-05-18 to 4 sub-steps** when the original Step 1.2 (PaaS vendor pick) resolved as a deferral per ADR-0055 (Session 28). Downstream renumbered: original 1.3 → 1.2 (M0.2 Data-layer primitives), 1.4 → 1.3 (M0.3 Dispatcher + history), 1.5 → 1.4 (M0.4 Adapter boundary). **Step 1.1 / M0.1 Scaffolding ✓ COMPLETE 2026-05-18** (Session 27). **Original Step 1.2 closed via deferral 2026-05-18** (Session 28 — administrative bookkeeping branch `m0/admin-paas-deferral` FF-merged into `m0/foundations`). Currently on the **`m0/foundations`** branch (tip advanced post-FF-merge to the Session 28 close-out). Next sub-step branch `m0/02-data-layer-primitives` opens off `m0/foundations` at Step 1.2 (new) session head.

## Last session summary

**Session 28 — original Step 1.2 / M0.2 PaaS vendor pick → closed as deferral (2026-05-18).** Case-3 scoped session. Opened as the substantive vendor canvass; resolved as a deferral after user push-back at session head. Net work: 1 ADR (ADR-0055), 1 structural restructure of M0, 1 new memory. 3 clean commits on `m0/admin-paas-deferral`; FF-merged to `m0/foundations`.

**Pivot at session head.** Agent presented the original Step 1.2 plan (vendor canvass with resume-point decisions on canvass shape + dev/prod parity). User pushed back: *"Can this be deferred indefinitely? I don't see a problem with keeping the entire thing simply in dev mode until it's ready to put in other people's hands. Worst case scenario is no one is interested in adopting it and it just lives as a portfolio/learning project."* Agent assessed reasonable (high confidence): nothing in M0–M7 actually depends on the vendor pick; ADR-0052 already pinned Postgres 15+ independently; M0.5 adapter wraps Postgres-specific (not vendor-specific) features; the "dependency ordering" rationale that placed Step 1.2 in M0 was not load-bearing. Surfaced 4 real risks (Postgres-version lock, extension dependence, driver assumptions, data-export cost) with discipline-note mitigations. User approved: *"approve - defer vendors until I prompt you to circle back to it."*

**Decisions landed (ADR-0055).** Defer production PaaS vendor pick indefinitely. Trigger to revisit: user explicitly prompts to circle back (no later than M8 cutover prep). Five portability discipline notes pinned in the ADR: (1) Postgres-version floor 15+; (2) no vendor-specific extensions (`pgvector` / `citus` / `pg_partman` etc.) without availability check on realistic shortlist; (3) default `psycopg` driver only (no Neon serverless driver, no RDS Proxy); (4) CI stays on docker-compose Postgres in the runner (no vendor-coupled ephemeral-PR DB); (5) architecture.md vendor slot stays "deferred per ADR-0055." ADR-0055 amends-by-supersession ADR-0051 + ADR-0052 carry-forward triggers (reinterpret "implementation kickoff" → "user prompts circle-back").

**Surprise / mid-execution decision: branch-prefix collision.** The planned M0 restructure (Option A: renumber sub-steps so 1.3 → 1.2, 1.4 → 1.3, 1.5 → 1.4) created a conflict — the bookkeeping branch was named `m0/02-defer-paas-pick`, and the renumbered Step 1.2 (data-layer-primitives) would also want the `m0/02-*` prefix. Three resolutions surfaced via AskUserQuestion: keep skip-numbering (M0.1 → M0.3 → M0.4 → M0.5), renumber + rename the bookkeeping branch to free the 02 slot, or renumber + accept the prefix overlap. User picked **rename**: `m0/02-defer-paas-pick` → `m0/admin-paas-deferral` (local rename only — branch had not yet been pushed). Canonical M0 sub-step branches now: `m0/01-scaffolding` (done), `m0/02-data-layer-primitives` (next), `m0/03-dispatcher-and-history`, `m0/04-adapter-boundary`. Admin work sits separately under `m0/admin-*` namespace.

**Commits landed (on `m0/admin-paas-deferral` → FF-merged into `m0/foundations`):**
1. `8ba95fc` M0.2: ADR-0055 defer PaaS vendor pick + portability discipline notes — `planning/decisions.md` append (ADR-0055, ~30 lines) + `planning/architecture.md` slot note updates (File contract `Update when` line, diagram caption, out-of-band file-storage pointer).
2. `850c743` M0.2: M0 restructure -- collapse to 4 sub-steps (PaaS pick deferred) — `planning/steps.md` Step 1 sub-step roster collapse + downstream renumber + brief updates; `planning/roadmap.md` M0 row update + M8 row gains PaaS work + per-milestone expansion updates + carry-forward landing index updates (PaaS row moves to M8, +2 new rows for CI ephemeral-DB wiring + connection-pooling decision).
3. `5d74f3c` Step 1.2 / M0.2 closed-by-deferral: handoff close-out (Session 28) — this rewrite + `planning/_file-rules.md` regen (architecture.md `Update when` block + date) + memory updates summary.

**Branch ops.**
- `m0/02-defer-paas-pick` created off `m0/foundations` (`20d2129`), then locally renamed to `m0/admin-paas-deferral`.
- After commit 3: FF-merge `m0/admin-paas-deferral` → `m0/foundations`; push both.
- Local safety branch `m0-01-backup` (M0.1 rewrite safety) carry-forward — user authorized deletion in Session 27 handoff; not deleted this session, still optional.
- Optional housekeeping carried over: `origin/m0/01-scaffolding` (merged, can be deleted); `m0-01-backup` (can be deleted).

**ADRs landed this sub-step.** **ADR-0055** — Defer production PaaS vendor pick until prod is called for; preserve portability via discipline notes (amends ADR-0051 + ADR-0052 carry-forwards by supersession).

**Memories saved (1 new).** [[project-vendor-pick-deferred]] (project; restates the 5 discipline notes; warns future sessions not to re-propose vendor canvass at session heads).

**Files touched.** `planning/decisions.md` (ADR-0055 appended). `planning/architecture.md` (File contract `Update when` line + diagram caption + out-of-band file-storage line). `planning/steps.md` (Step 1 header narrative + sub-step roster + execution order + done-when; Step 1.2 PaaS section removed; Step 1.3/1.4/1.5 renumbered to 1.2/1.3/1.4 + branch names updated; Step 1.1 § Out of scope and § Done when references renumbered; CI-pipeline reference updated). `planning/roadmap.md` (M0 row + M8 row + M0 per-milestone expansion + M8 per-milestone expansion + carry-forward landing index). `planning/_file-rules.md` (architecture.md `Update when` block + Last regenerated date). `planning/handoff.md` (this rewrite). `.claude/memory/project_vendor_pick_deferred.md` (new) + `.claude/memory/MEMORY.md` (index entry).

---

## Open questions

**For the next session (Session 29 — Step 1.2 / M0.2 — Data-layer primitives):**

- **Bundle-vs-split ADR shape.** Two coupled decisions (per-invariant isolation-primitive assignment + audit-log write timing) — bundle as a single ADR-0056 (precedent: ADR-0052 bundled persistence + history-impl) or split into ADR-0056 + ADR-0057 (precedent: ADR-0009 / 0010 / 0012's split). Pick at session head; honest argument exists either way (both decisions are data-layer enforcement-mechanism choices — same "different declaration surfaces" framing that justified the 0009/10/12 split does *not* apply here).
- **Per-invariant assignment scope.** ADR-0052 said per-invariant assignment is implementation-phase, but didn't say *how many* must be assigned at M0.2 vs. left to "as each invariant lands later." Candidate worked examples: the closure-readiness cluster (`domain-model.md` § Design patterns #3) + EmployeeRole disjoint-ranges (per ADR-0045). Two postures: (a) M0.2 pins the framework + 1–2 worked examples; per-invariant decisions land with the invariants in M1–M7; (b) M0.2 enumerates all known invariants up-front and assigns each one isolation primitive now (heavier session, more decisions stacked, but milestone-level decisions resolved). Pick at session head.

**For the milestone (M0 Foundations) broadly:**

- **M0.3 Dispatcher + history infrastructure is sized L — likely needs further partitioning when opened.** (Renumbered from M0.4 per the 2026-05-18 collapse.) Run Case 2 fit checklist at M0.3's session head; candidate seam: dispatcher (pipeline + auth/lifecycle/invariants integration) as one sub-sub-step, history-infrastructure (per-entity table generator + `command_audit_log` + capture wiring) as another.
- **Sub-step branches off `m0/foundations`** per [[project-branching-convention]]. Sub-step merges back into `m0/foundations` with FF (all checkpoint commits intact — see [[preserve-incremental-commits]]). M0 closes when all four canonical sub-steps merge to `m0/foundations` (the `m0/admin-paas-deferral` admin branch is already merged); `m0/foundations` then merges to `dev` with `--no-ff`, tag `m0-complete` on `dev`.
- **PaaS vendor pick stays deferred per ADR-0055.** Do not re-propose a vendor canvass at any future M0 sub-step session head. See [[project-vendor-pick-deferred]] for the 5 portability discipline notes that constrain forward work.
- **MVP-attempt-1 rewind protocol** (per [[project-branching-convention]]): if implementation attempt 1 tanks, tag `dev` as `attempt-1-archived` (or delete `dev`), recreate `dev` fresh from `main` (or `phase-1-complete` tag), restart at M0. All attempt-1 history preserved through milestone branches + tags.
- **Branch housekeeping carried forward.** `origin/m0/01-scaffolding` is merged and could be deleted (no longer needed). Local `m0-01-backup` (safety branch from M0.1 rewrite) can be deleted now that the merge is verified. After Session 28 close-out: `m0/admin-paas-deferral` (both local + origin if pushed) can be deleted (FF-merged into `m0/foundations`).

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

**Step 1.2 — M0.2 Data-layer primitives (S–M).** (Renumbered from original Step 1.3 / M0.3 per the Session 28 restructure.) Substantive deliberation step. Resolves ADR-0052's two deferred carry-forwards: per-invariant isolation-primitive assignment + audit-log write timing. ADR-0056 lands here (possibly two ADRs — see Open questions). Branch `m0/02-data-layer-primitives` off `m0/foundations` (post Session 28 FF-merge tip) at session head.

**Execution order within Step 1 (post-collapse):** 1.1 ✓ → original 1.2 closed-by-deferral (Session 28) → **new 1.2 (next)** → 1.3 → 1.4 → Step 1 ✓ (merge `m0/foundations` to `dev` with `--no-ff`; tag `m0-complete` on `dev`) → Step 2 (M1 Roster).

### Prompt for the next session

> Resume work. **Step 1.2 — M0.2 Data-layer primitives** (renumbered from original Step 1.3 / M0.3 per the Session 28 restructure) is the next sub-step. Original Step 1.2 (PaaS vendor pick) closed via deferral in Session 28 — ADR-0055 landed; PaaS pick now deferred until user prompts circle-back (no later than M8). **Do not re-propose the vendor canvass.** This new Step 1.2 is a substantive deliberation step landing ADR-0056 (possibly two — see Open questions).
>
> **Branch state:** `m0/foundations` advanced post-Session-28 (FF-merged `m0/admin-paas-deferral` carrying 3 commits: ADR-0055 + M0 restructure + handoff close-out). Create `m0/02-data-layer-primitives` off `m0/foundations` at session head. Optional housekeeping: delete `origin/m0/01-scaffolding` + local `m0-01-backup` + `m0/admin-paas-deferral` (local + origin if pushed) — all merged or superseded.
>
> **Read first:** this prompt + the Open questions block above + the Last session summary (Session 28 — original M0.2 deferral + restructure) + `planning/steps.md` § Step 1.2 brief (new M0.2 — data-layer primitives) + `planning/roadmap.md` § M0 § "data-layer primitives" area + ADR-0052 (persistence + history-impl with the two deferred carry-forwards) + ADR-0055 (the deferral + the 5 portability discipline notes) + ADR-0010 (write-path invariant enforcement requirement) + ADR-0008 (atomic capture). Skim `domain-model.md` § Design patterns #3 (closure-readiness cluster — the obvious advisory-lock candidate) + ADR-0045 (EmployeeRole disjoint-ranges-per-`(employee, role_type, contract)` invariant — the obvious second worked example).
>
> **Resume-point canvass (before any writes):**
> 1. **Bundle-vs-split ADR shape.** Per Open questions. Honest call needed at session head.
> 2. **Per-invariant assignment scope.** Per Open questions. (a) framework + 1–2 worked examples or (b) enumerate-all-now.
>
> **In scope (substance):**
> - **D1 — Per-invariant isolation-primitive assignment.** Choose between `SERIALIZABLE` (default per ADR-0052) and `pg_try_advisory_xact_lock` (opt-in) for each invariant assigned in this session. Per Open question 2: either 1–2 worked examples (closure-readiness + EmployeeRole disjoint-ranges are the obvious candidates) or full enumeration.
> - **D2 — Audit-log write timing.** Choose between in-txn (within the same transaction as the entity mutation) and post-commit (best-effort fire-and-forget, ADR-0013-permitted) for the `command_audit_log` writes the dispatcher emits for audit-log entities. Trade-offs: in-txn guarantees the audit row is present iff the mutation is (no orphans / no missing rows); post-commit allows the response to return before the audit write blocks. Both are honestly defensible; the call depends on whether audit-log writes are likely to become a perf-tail vs. how much we value the "audit row exists iff mutation did" invariant.
> - Land ADR-0056 (and possibly ADR-0057) in `planning/decisions.md`.
> - Update `planning/architecture.md` if the choices change any boundary semantics or data-flow language (likely a 1–4 line tweak to the dispatcher pipeline caption).
>
> **Out of scope:**
> - PaaS vendor pick — **stays deferred per ADR-0055**.
> - `Command` base class + dispatcher + history infrastructure code — M0.3 / Step 1.3.
> - Adapter boundary code — M0.4 / Step 1.4.
> - Any domain entity / command / handler — M1+.
>
> **Process notes:**
> - **STOP-AND-CONFIRM gate applies.** Canvass the two decisions in chat (≤150 words per position) before writing the ADR(s).
> - **Commit pattern: preserve incremental checkpoints; FF to milestone, no squash** (per [[preserve-incremental-commits]]).
> - **Sub-step branch convention** (per [[project-branching-convention]]): `m0/02-data-layer-primitives` off `m0/foundations`; FF-merge back when done; do NOT merge to `dev` yet (waits until all M0 sub-steps land).
> - **ADR numbering.** Next ADR at write time: **ADR-0056**.
> - **Portability discipline** (per ADR-0055 + [[project-vendor-pick-deferred]]). Choices made here must hold across the realistic vendor shortlist for Postgres 15+; `pg_try_advisory_xact_lock` is core Postgres, fine; if any choice would require a vendor-specific extension, flag it before writing.
> - **`mvp.md` is the canonical MVP scope reference.**

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-18)
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 partitioned into 5 sub-steps 2026-05-17, collapsed to 4 sub-steps 2026-05-18 per ADR-0055 deferral**; Steps 2–9 stubs)
- Archived step list (Phase 1): `planning/steps.archive/conceptualization.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0055; next ADR at write time: **ADR-0056**)
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
