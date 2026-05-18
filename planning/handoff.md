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

**Implementation** — Phase 2. The 9-milestone roadmap from `planning/roadmap.md` (M0 Foundations → M8 Cutover prep) is the canonical milestone-shape source; `planning/steps.md` mirrors the milestones as 9 steps. **Step 1 (M0) was partitioned 2026-05-17 into 5 sub-steps (1.1 → 1.5); collapsed 2026-05-18 to 4 sub-steps** when the original Step 1.2 (PaaS vendor pick) resolved as a deferral per ADR-0055 (Session 28). Downstream renumbered: original 1.3 → 1.2 (M0.2 Data-layer primitives), 1.4 → 1.3 (M0.3 Dispatcher + history), 1.5 → 1.4 (M0.4 Adapter boundary). **Step 1.1 / M0.1 Scaffolding ✓ COMPLETE 2026-05-18** (Session 27). **Original Step 1.2 closed via deferral 2026-05-18** (Session 28). **Step 1.2 / M0.2 Data-layer primitives ✓ COMPLETE 2026-05-18** (Session 29 — ADR-0056 + ADR-0057 landed; sub-step branch `m0/02-data-layer-primitives` FF-merged into `m0/foundations`). Currently on the **`m0/foundations`** branch (tip advanced post-FF-merge to the Session 29 close-out). Next sub-step branch `m0/03-dispatcher-and-history` opens off `m0/foundations` at Step 1.3 session head.

## Last session summary

**Session 29 — Step 1.2 / M0.2 Data-layer primitives ✓ COMPLETE (2026-05-18).** Case-3 scoped session. Resolved both of ADR-0052's deferred implementation-phase carry-forwards (per-invariant isolation primitive + audit-log write timing). 4 commits on `m0/02-data-layer-primitives`; FF-merged into `m0/foundations` at close.

**Two meta-questions settled at session head before substance.**
- **Q1 — Bundle vs. split ADR shape.** Split chosen: ADR-0056 for isolation primitive, ADR-0057 for audit-log timing. Rationale: D1 (isolation) and D2 (audit-log timing) are independent dispatcher-internal mechanism choices with no constraint coupling, so ADR-0052's bundling rationale (engine capabilities constrain history-impl viability) does not apply. Split keeps amendment chains focused — a future flip of audit-log timing doesn't muddy the isolation-primitive surface.
- **Q2 — Per-invariant assignment scope.** Framework + 2 worked examples chosen, not full enumeration. Per-invariant choices for invariants landing in M1–M7 are criterion-applications made *with the invariant in code*, when the implementer has actual conflict-frequency context. Pre-assigning primitives for invariants that don't yet exist inverts the "decision with context" principle.

**Substance landed.**
- **D1.a — Two-prong opt-in criterion (ADR-0056).** Default SERIALIZABLE. Reach for `pg_try_advisory_xact_lock` only when (a) the invariant's read footprint is wide enough that SERIALIZABLE produces frequent false-positive serialization failures AND (b) the invariant's scope can be expressed as a small set of named lock keys. Prong (b) is load-bearing — without a stable key, advisory locks are misuse.
- **D1.b — Closure-readiness cluster → advisory lock per-project (ADR-0056).** Every dispatcher invocation that mutates a closure-readiness-relevant entity (Time Entry, Sample Batch, Document, RFA, DepFiling, RFP) tries `pg_try_advisory_xact_lock(closure_readiness_key(project_id))` in the invariant step. `close_project` tries the same lock. Two projects' commands run in parallel; same-project commands serialize.
- **D1.c — EmployeeRole disjoint-ranges → SERIALIZABLE (default) (ADR-0056).** Prong (a) fails — conflict surface scopes to the same `(employee, role_type, contract)` tuple; SERIALIZABLE retry rate near zero in office workflow.
- **D2 — Audit-log write timing → in-txn (ADR-0057).** `command_audit_log` row written in the same SQLAlchemy session as the entity mutation. "Audit row exists iff mutation did" invariant preserved. No outbox / queue machinery in M0.3. Perf revisit trigger documented (M5+ hot-path contention — likely shape: outbox for the specific contended entity, not a global flip).

**Mid-session decision: user-requested self-study reference doc.** User flagged unfamiliarity with the Postgres concurrency vocabulary in the ADR canvasses (SSI, advisory locks, MVCC) and requested a self-study list. Saved as `planning/follow-ups/postgres-concurrency-primer.md` — topic list (MVCC → isolation levels → SSI → advisory locks → in-txn vs outbox) + curated source links (Postgres docs canonical; PostgreSQL wiki SSI page; microservices.io outbox; Brandur Leach blog; Ports & Grittner SSI paper for depth) + suggested reading order. **`planning/follow-ups/` is a new directory.** Use it for similar future reference / study docs that aren't planning artifacts proper.

**Commits landed (on `m0/02-data-layer-primitives` → FF-merged into `m0/foundations`):**
1. `e7e2ef6` M0.2: ADR-0056 per-invariant isolation primitive criterion + first assignments — `planning/decisions.md` append (~32 lines).
2. `ddfba04` M0.2: ADR-0057 audit-log write timing -- in-txn with entity mutation — `planning/decisions.md` append (~26 lines).
3. `33940d9` M0.2: architecture.md -- replace ADR-0052 carry-forward placeholders with ADR-0056/0057 pointers — 3 in-place line updates: data-layer topology `command_audit_log` line + data-flow step 7 invariants + data-flow step 8 audit-log write.
4. (this commit) Step 1.2 / M0.2 ✓: handoff close-out + Postgres concurrency primer (Session 29) — this rewrite + `planning/follow-ups/postgres-concurrency-primer.md` (new file).

**Branch ops.**
- `m0/02-data-layer-primitives` created off `m0/foundations` (`6f2cefb`) at session head.
- After commit 4: FF-merge `m0/02-data-layer-primitives` → `m0/foundations`; push both.
- Optional housekeeping carried over (not done this session): delete `origin/m0/01-scaffolding` (merged); local `m0-01-backup` (M0.1 rewrite safety); `m0/admin-paas-deferral` (FF-merged into `m0/foundations` in Session 28); `m0/02-data-layer-primitives` itself (after this session's FF-merge).

**ADRs landed this sub-step (2).** **ADR-0056** — Per-invariant isolation primitive: two-prong opt-in criterion + first per-invariant assignments (amends ADR-0052's per-invariant primitive carry-forward). **ADR-0057** — Audit-log write timing: in-txn with the entity mutation (amends ADR-0052's audit-log timing carry-forward).

**Memories saved (1 new).** [[user-postgres-concurrency-gap]] (user; user has solid project-strategy fluency but is unfamiliar with Postgres concurrency mechanics — SERIALIZABLE / SSI, MVCC, advisory locks, isolation levels. Asked for self-study material proactively. Inform tone in future canvasses involving similar primitives: lean toward grounding terms before reaching for them; offer worked examples; offer to ground unfamiliar phrases on request).

**Files touched.** `planning/decisions.md` (ADR-0056 + ADR-0057 appended). `planning/architecture.md` (3 in-place line updates). `planning/follow-ups/postgres-concurrency-primer.md` (new file + new directory). `planning/handoff.md` (this rewrite). `.claude/memory/user_postgres_concurrency_gap.md` (new) + `.claude/memory/MEMORY.md` (index entry). `_file-rules.md` **not regenerated** — no File contract block changed this session (architecture.md edits were in body sections; decisions.md edits were appends).

---

## Open questions

**For the next session (Session 30 — Step 1.3 / M0.3 — Dispatcher + history infrastructure):**

- **Case 2 partitioning at session head — Step 1.3 is sized L.** Per the carry-forward, candidate seam is: **dispatcher** (pipeline scaffold + auth/lifecycle/invariants/audit integration per `logic.md` order) as one sub-sub-step; **history infrastructure** (per-entity history table generator + `command_audit_log` schema + capture-wiring inside dispatcher) as another. Run the Case 2 fit checklist before substance. Alternative seam to consider: by *layer* rather than by *concern* — scaffold the dispatcher + history capture wiring as one sub-sub-step (touching all layers shallowly) and the per-entity history table generator + audit-log schema as a second. Decide at session head.
- **Dispatcher concrete-design ADR-worthiness.** Pipeline order is the spec (`logic.md`: auth → lifecycle → apply → invariants → history → commit; ADR-0012 / 0009 / 0010 / 0008). Per-invariant primitive acquisition lands in the invariants step per ADR-0056. Audit-log emit lands in the history step in-txn per ADR-0057. Pre-flag: ADR-0058 may land if dispatcher design surfaces ADR-worthy decisions (e.g., command-registration / introspection shape; cascade-command auth-inheritance per `domain-model.md` § Design patterns #5; retry-loop boundary for `serialization_failure`).
- **History infrastructure shape.** 9 per-entity history tables (3 comprehensive — Document / WA / RFA; 6 lifecycle — Project / Sample Batch / Deliverable / EmployeeRole / WA Code / ContractorEngagement) + `command_audit_log` (polymorphic, 7 audit-log entities). Common metadata per ADR-0052. Comprehensive `snapshot` JSONB; lifecycle `from_state` / `to_state` / `transition_name` / `state_context`. Reference-snapshotting rule per ADR-0013 + ADR-0052 § S5. Capture framework-enforced — no handler-level skip. Per-entity table generator (SQLAlchemy declarative bases) is a design surface; could be ADR-worthy if non-obvious tradeoffs surface.
- **Lock-key namespace.** Per ADR-0056 carry-forward: lock-key hash function + namespacing must be decided in M0.3 (the closure-readiness key shape `hashtext('closure-readiness:' || project_id)::bigint` is illustrative, not pinned). If other future advisory-lock uses are anticipated, the namespace prefix discipline lands here.

**For the milestone (M0 Foundations) broadly:**

- **M0.4 Adapter boundary (Step 1.4) opens after 1.3 lands.** Sized S. Wraps Postgres-specific features behind the adapter per ADR-0051: JSONB ops + `pg_try_advisory_xact_lock` (per ADR-0056) + `SERIALIZABLE` isolation. SQLite degraded equivalents — explicit not production-equivalent (per ADR-0051 + ADR-0052 + ADR-0056). Integration check: sample command flows through the full pipeline via the adapter on both Postgres and SQLite paths.
- **Sub-step branches off `m0/foundations`** per [[project-branching-convention]]. Step 1.3 = `m0/03-dispatcher-and-history`. Step 1.4 = `m0/04-adapter-boundary`. Sub-step merges back into `m0/foundations` with FF (all checkpoint commits intact — see [[preserve-incremental-commits]]). M0 closes when all four canonical sub-steps merge to `m0/foundations` (M0.1 ✓, M0.2 ✓, M0.3 pending, M0.4 pending); `m0/foundations` then merges to `dev` with `--no-ff`, tag `m0-complete` on `dev`.
- **PaaS vendor pick stays deferred per ADR-0055.** Do not re-propose a vendor canvass at any future M0 sub-step session head. See [[project-vendor-pick-deferred]] for the 5 portability discipline notes that constrain forward work.
- **MVP-attempt-1 rewind protocol** (per [[project-branching-convention]]): if implementation attempt 1 tanks, tag `dev` as `attempt-1-archived` (or delete `dev`), recreate `dev` fresh from `main` (or `phase-1-complete` tag), restart at M0. All attempt-1 history preserved through milestone branches + tags.
- **Branch housekeeping carried forward.** `origin/m0/01-scaffolding` (merged) + local `m0-01-backup` (M0.1 rewrite safety) + `m0/admin-paas-deferral` (FF-merged Session 28) + `m0/02-data-layer-primitives` (FF-merged Session 29) — all can be deleted; user authorization standing from Session 27 forward. Defer or batch at user discretion.

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

**Step 1.3 — M0.3 `Command` base class + dispatcher + history infrastructure (L).** Load-bearing substrate step. Implements the `Command` base class + dispatcher per ADR-0051 + ADR-0052 with the `logic.md` pipeline (auth → lifecycle → apply → invariants → history → commit); the per-entity history infrastructure (9 tables + `command_audit_log`); the per-invariant primitive acquisition wiring per ADR-0056; the in-txn audit-log emit per ADR-0057. **Likely needs Case 2 partitioning at session head** — sized L; candidate seam in Open questions. ADR-0058 if dispatcher design surfaces ADR-worthy decisions. Branch `m0/03-dispatcher-and-history` off `m0/foundations` (post Session 29 FF-merge tip) at session head.

**Execution order within Step 1 (post-collapse):** 1.1 ✓ → original 1.2 closed-by-deferral (Session 28) → 1.2 ✓ (Session 29) → **1.3 (next)** → 1.4 → Step 1 ✓ (merge `m0/foundations` to `dev` with `--no-ff`; tag `m0-complete` on `dev`) → Step 2 (M1 Roster).

### Prompt for the next session

> Resume work. **Step 1.3 — M0.3 `Command` base class + dispatcher + history infrastructure (L)** is the next sub-step. Step 1.2 / M0.2 closed in Session 29 — ADR-0056 (per-invariant isolation primitive criterion + first assignments) and ADR-0057 (audit-log write timing — in-txn) landed; both amend ADR-0052's deferred carry-forwards. Per-invariant primitive choices for invariants landing in M1–M7 are criterion-applications under ADR-0056 (no per-invariant ADR amendment required).
>
> **Branch state:** `m0/foundations` advanced post-Session-29 (FF-merged `m0/02-data-layer-primitives` carrying 4 commits: ADR-0056 + ADR-0057 + architecture.md tweaks + handoff close-out). Create `m0/03-dispatcher-and-history` off `m0/foundations` at session head. Optional housekeeping: delete `origin/m0/01-scaffolding` + local `m0-01-backup` + `m0/admin-paas-deferral` + `m0/02-data-layer-primitives` — all merged or superseded; user authorization standing.
>
> **Open with Case 2 sizing.** Step 1.3 is L. Per Session 29 handoff Open questions: candidate seam is dispatcher (pipeline scaffold + auth/lifecycle/invariants/audit integration) vs. history-infrastructure (per-entity table generator + `command_audit_log` schema + capture wiring). Run the Case 2 fit checklist (`_workflow.md`); name the firing signal(s) before proposing a partition. Alternative seam (by layer rather than by concern) also on the table — see Open questions. Resolve sizing before any substance writes.
>
> **Read first:** this prompt + the Open questions block above + the Last session summary (Session 29 — M0.2 data-layer primitives) + `planning/steps.md` § Step 1.3 brief (M0.3 dispatcher + history infrastructure) + `planning/roadmap.md` § M0 dispatcher + history items + ADR-0051 (runtime stack envelope) + ADR-0052 (data layer pin + history-impl shape + capture-enforcement semantics) + ADR-0056 (per-invariant isolation primitive criterion + assignments — Session 29) + ADR-0057 (audit-log write timing — in-txn — Session 29) + ADR-0008 (atomic capture — framework-enforced) + ADR-0009 (lifecycle gate) + ADR-0010 (write-path invariant enforcement) + ADR-0011 (rejection on violation; no mutation, no history) + ADR-0012 (authorization predicate) + ADR-0013 (4-pattern history menu + reference rules). Skim `planning/logic.md` (pipeline order spec) + `planning/history-patterns.md` (4-pattern menu) + `planning/data-model.md` (per-entity attribute rosters + history-table shapes) + `domain-model.md` § Design patterns #5 (compound cascading commands — auth inheritance).
>
> **In scope (substance, subject to Case 2 partition):**
> - **Dispatcher.** `Command` base class shape (registration / introspection / cascade semantics per design pattern #5). Pipeline implementation in the order per `logic.md`: authorization (ADR-0012 predicate eval) → lifecycle gate (ADR-0009 state-machine check) → apply (handler mutation) → invariants (ADR-0010 + ADR-0056 primitive acquisition) → history (ADR-0008 / ADR-0052 / ADR-0057 in-txn audit emit) → commit. Rejection at any step rolls back per ADR-0011 — no mutation, no history.
> - **Lock-key namespace.** Per ADR-0056 carry-forward: pin the hash function + key prefix discipline. Closure-readiness key (`closure_readiness_key(project_id)`) is the first user; namespace must not collide with future advisory-lock uses.
> - **Per-entity history table generator.** 9 tables (3 comprehensive — Document / WA / RFA; 6 lifecycle — Project / Sample Batch / Deliverable / EmployeeRole / WA Code / ContractorEngagement) per ADR-0052. Common-metadata columns (`id`, `entity_id` FK, `command_id`, `command_name`, `caller_id`, `at`; default index `(entity_id, at DESC)`). Comprehensive `snapshot` JSONB; lifecycle `from_state` / `to_state` / `transition_name` / `state_context` JSONB. Typed-UUID references only per ADR-0013 § Reference snapshotting.
> - **`command_audit_log` table.** Polymorphic `(entity_type, entity_id)` shape per ADR-0052 § Audit-log table. Written in-txn per ADR-0057. Wired into the dispatcher for the 7 audit-log entities (Employee, User, Time Entry, Contractor, DepFiling, Contract, WABundle).
> - **Capture enforcement.** No handler-level skip path. The framework surface does not expose a "skip history" or "skip audit" hook (per ADR-0008 + ADR-0052).
> - **`serialization_failure` retry boundary.** Where does retry live — in the dispatcher (built-in N-attempt loop) or pushed up to the route layer? Decide; possibly ADR-0058.
> - Land ADR-0058 (and possibly more) in `planning/decisions.md` for any dispatcher-design decisions that surface as ADR-worthy.
> - Update `planning/architecture.md` if dispatcher/history shape clarifies any boundary or data-flow language.
>
> **Out of scope:**
> - PaaS vendor pick — **stays deferred per ADR-0055**.
> - Adapter boundary code (the named adapter functions wrapping JSONB / advisory-lock / SERIALIZABLE) — M0.4 / Step 1.4. M0.3 may stub adapter call sites; the full adapter lands in 1.4.
> - Any domain entity / command / handler beyond a smoke-test sample — M1+. (M0.3 may include a sample command to exercise the pipeline end-to-end, but no domain commands.)
>
> **Process notes:**
> - **STOP-AND-CONFIRM gate applies, including for source code.** Non-trivial structural code decisions (dispatcher shape, history generator shape, retry boundary) earn a chat-side canvass before the write.
> - **Commit pattern: preserve incremental checkpoints; FF to milestone, no squash** (per [[preserve-incremental-commits]]). Substrate step — expect more commits than M0.2.
> - **Sub-step branch convention** (per [[project-branching-convention]]): `m0/03-dispatcher-and-history` off `m0/foundations`; FF-merge back when done; do NOT merge to `dev` yet (waits until M0.4 lands).
> - **ADR numbering.** Next ADR at write time: **ADR-0058**.
> - **Portability discipline** (per ADR-0055 + [[project-vendor-pick-deferred]]). All dispatcher / history mechanics must work on vanilla `psycopg` + Postgres 15+. SQLite offline-fallback path uses degraded equivalents — explicit not production-equivalent per ADR-0051 + ADR-0052 + ADR-0056.
> - **`mvp.md` is the canonical MVP scope reference.**
> - **User-knowledge note.** Per [[user-postgres-concurrency-gap]]: when discussing Postgres-specific dispatcher mechanics (transaction boundaries, lock acquisition, isolation-level effects), lean toward grounding terms before reaching for them; offer worked examples when introducing a primitive.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-18)
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 partitioned into 5 sub-steps 2026-05-17, collapsed to 4 sub-steps 2026-05-18 per ADR-0055 deferral**; Steps 2–9 stubs)
- Archived step list (Phase 1): `planning/steps.archive/conceptualization.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0057; next ADR at write time: **ADR-0058**)
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
