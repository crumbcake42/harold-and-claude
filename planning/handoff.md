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

---

## How to start a session

If the user says something like _"resume work"_ / _"start the next session"_ / _"run the next session"_ / _"do the next session block"_ / _"vamos"_ / _"yallah"_: follow `planning/_workflow.md`. That file owns the case-detection logic and the completion protocol.

---

## Current phase

**Conceptualization** — steps are planning-only, no code is written. **Step 8b (data layer: persistence + history-impl + `architecture.md`) complete 2026-05-16 (session 22) — ADR-0052 + `planning/architecture.md` landed.** Data layer pinned at PostgreSQL 15+ via SQLAlchemy 2.0 + Alembic; per-entity append-only history tables (9 — 3 comprehensive + 6 lifecycle) + shared `command_audit_log` (polymorphic ref) for the 7 audit-log entities + no history infrastructure for the 5 no-history entities; capture enforced in the `Command` base class + dispatcher (carry-forward from ADR-0051); `SERIALIZABLE` default + `pg_try_advisory_xact_lock` opt-in for ADR-0010 cross-entity invariant isolation. `planning/architecture.md` drafted (component diagram + boundary semantics + 10-step successful-command data flow). Conceptualization-phase work remaining: **Step 9 partitioned 2026-05-16 — 9a (`data-model.md`), 9b (consolidation pass + `roadmap.md` + phase-transition ADR)**; next is **Step 9a**. See `planning/phases.md` for the full phase roster and `planning/steps.md` for the current step list.

## Last session summary

**Session 23 — Step 9 partitioning + Step 9a session plan. ✓ COMPLETE (2026-05-16, no ADRs).** Case-2 sizing session. Ran the `_workflow.md` Case 2 fit checklist on Step 9 — **five signals fired** (1: >1 deliberable decisions — data-model + roadmap + consolidation + phase-transition; 2: >1 new artifact — `data-model.md` + `roadmap.md` + phase-transition ADR; 3: >60 min; 4: input reading exceeds ~3 substantial files — framework + logic + history-patterns + domain-model + mvp + architecture + decisions.md/52 ADRs; 5: cross-concern reach — data modeling vs. roadmap planning vs. archival/governance). Three partition options canvassed; **Option A (single-concern seam — 9a `data-model.md` / 9b consolidation + `roadmap.md` + phase-transition ADR) accepted with mitigation** (re-run the fit checklist at 9b's session head if the consolidation candidate scan turns up more than ~2 qualifying ADRs; partition further to a 9c if needed). Option B (three-way split) rejected — `roadmap.md` and consolidation don't compete for the same context budget. Option C (data-model + consolidation paired) rejected — separates the consolidation pass from the phase-transition ADR it directly enables, against the original "consolidation before phase-transition" sequencing.

**Consolidation-candidate preview (informs 9b sizing).** Quick scan of `decisions.md` Status lines: **ADR-0032** (extended by 0042, 0046, 0049 + registry amended by 0044 — 4 amendments; firm consolidation target). Borderline (verify at 9b's session head): **ADR-0027** (likely 2–3 amendments — `acknowledged` aspect superseded by 0032, further touched by 0045 / retired by 0049), **ADR-0037** (likely 1–2 — amended by 0043; verify 0044's reach). Single-amendment cases (no trigger): ADR-0017, ADR-0030, ADR-0035, ADR-0040. Net: probably 1 firm + 1–2 borderline → 9b stays under the partition-further threshold.

**Step 9a session plan canvassed; six structural choices (Q1–Q6) settled with recommendations accepted:** (Q1) per-entity outgoing-references line inline — cross-entity table stays in `domain-model.md`; (Q2) `state` enum noted per entity, transitions referenced; (Q3) flat per-entity table with `Attribute | Kind | Type / notes` columns; (Q4) Document is one entity row with `document_type` as an attribute; (Q5) ordering — `## File contract` → `## Reading this file` → `## Conventions` → `## Per-entity attributes` (21 sub-sections) → `## History tables` → `## Pointers`; (Q6) no new ADRs expected — if a substantive design gap surfaces during attribute drafting, surface at the gate and defer (likely to implementation phase). 9a executes next session.

**Files touched:** `planning/steps.md` — Step 9 section gains partition block + Step 9a sub-section + Step 9b sub-section (Option A; mitigation recorded). `planning/handoff.md` — Current phase line updated to flag the partition; Last session summary (this entry); Open questions refreshed; Next session pointer + prompt rewritten for 9a; Pointers line updated. No `decisions.md` changes (sizing is governance, not an ADR-grade decision). No `_file-rules.md` regeneration needed (no `## File contract` blocks touched this session).

---

*(Prior session retained for context — Session 22 / Step 8b data-layer ADR + `architecture.md`.)*

**Session 22 — Step 8b Data-layer ADR + `architecture.md`. ✓ COMPLETE (2026-05-16, ADR-0052 + `planning/architecture.md`).** Case-3 scoped — the persistence + history-impl pair plus the one-page architecture sketch. Both sub-decisions canvassed at the STOP-AND-CONFIRM gate; ten sub-commitments amend-or-accepted before any ADR text drafted.

**Local decision at session head:** Bundled into a single ADR-0052 ("Data layer") — same coupling-respecting reasoning as ADR-0051's three-way bundle. Engine capabilities (JSONB, advisory locks, `SERIALIZABLE` isolation) directly constrain history-impl viability; ADR-0009/0010/0012's three-way split was justified by *different declaration surfaces* (state machine / entity / command) which this pair doesn't share; persistence sub-decision was honestly short (Postgres falls out of the ADR-0051 envelope in ~1 paragraph). One bundled ADR avoids restating the coupling twice.

**Two sub-decisions settled:**
- **(D1) Persistence engine → PostgreSQL 15+** via SQLAlchemy 2.0 + Alembic. Managed offering selected at PaaS-vendor pick; Neon free-tier remains dev default per ADR-0051. Canvassed against (b) MySQL/MariaDB (weaker `SERIALIZABLE` gap-locking semantics + `GET_LOCK` is connection-scoped not transaction-scoped — wrong primitive for cross-entity invariant guards + JSON ergonomics weaker than JSONB + conflicts with Neon dev pin), (c) SQLite-everywhere with Litestream (categorically violates ADR-0010 isolation — single-writer-by-design "satisfies" serializability by removing concurrency, doesn't handle it), (d) Distributed-Postgres flavors / CockroachDB / YugabyteDB (overkill at MVP scale, no scale pressure ever projected, pricier than Neon free-tier, Alembic compatibility imperfect). High confidence — the ADR-0051 envelope was tight enough that Postgres was effectively the only honest answer; canvass exists to record the others were ruled out on merits.
- **(D2) History implementation shape → per-entity append-only history tables.** 9 tables total — 3 comprehensive (`document_history`, `wa_history`, `rfa_history`) + 6 lifecycle (`project_history`, `sample_batch_history`, `deliverable_history`, `employee_role_history`, `wa_code_history`, `contractor_engagement_history`); written in the same SQLAlchemy txn as the entity mutation. Shared `command_audit_log` table with polymorphic `(entity_type, entity_id)` ref (same shape as Note per ADR-0018) for the 7 audit-log entities — command metadata only, no state snapshots, timing (in-txn vs. post-commit) deferred to implementation. No history infrastructure for the 5 no-history entities. Capture enforced structurally in the `Command` base class + dispatcher (carry-forward from ADR-0051); ADR-0008 atomicity guaranteed by same-txn write — no handler-level escape hatch. Canvassed against (b) Single polymorphic history table (polymorphic FK orphan risk + shared-column nullables + per-entity indexing degenerates), (c) Temporal tables / hand-rolled triggers (wrong dependency direction — capture at row-mutation surface inverts ADR-0008's command-pipeline-boundary enforcement; triggers can't access caller identity / command name; lifecycle-affecting detection from column diffs inverts ADR-0009's application-level declaration), (d) Event store (already foreclosed by ADR-0007 + ADR-0008 — re-opening would reverse two settled ADRs without new evidence). High confidence — per-entity tables fall out of every constraint cleanly.

**10 sub-commitments pinned in ADR-0052 (S1–S10):** common metadata schema (S1); comprehensive-pattern columns — `snapshot` JSONB (S2); lifecycle-pattern columns — `from_state`/`to_state`/`transition_name`/`state_context` JSONB (S3); audit-log table shape — polymorphic ref, no DB-level FK, timing deferred (S4); no-history entities — no history infrastructure (S5); reference-snapshotting rule — restatement of ADR-0013, typed-UUID refs only (S6); schema evolution — JSONB absorbs most entity-schema changes, only metadata-column changes require Alembic migrations on history tables (S7); capture enforcement — dispatcher-level, no skip path (S8); cross-entity invariant isolation — `SERIALIZABLE` default + `pg_try_advisory_xact_lock` opt-in (S9); engine-portability discipline — Postgres-specific features behind adapter boundary per ADR-0051, SQLite-fallback path buildable but not production-equivalent (S10).

**ADR-0010 deferred isolation-mechanism question answered here.** ADR-0010 explicitly deferred the isolation choice (serializable transactions / optimistic locking / advisory locks) to Step 8; ADR-0052 pins the primitives (`SERIALIZABLE` default + advisory-lock opt-in). Recorded as the answer to ADR-0010's deferral rather than as an amendment to ADR-0010, since ADR-0010 explicitly carried this forward to Step 8.

**`planning/architecture.md` drafted.** New file with `## File contract` block. Contents: ASCII component diagram (Browser → CDN/SPA → API container → managed Postgres, all on managed PaaS); boundary semantics per layer (browser↔CDN, SPA↔API, routes↔dispatcher, dispatcher↔SQLAlchemy session, SQLAlchemy↔Postgres, internal data-layer topology); successful-command 10-step data flow; out-of-band concerns flagged for implementation phase (file storage / background jobs / notifications / auth mechanism); pointers section.

**Carry-forwards (per ADR-0052):** PaaS vendor pick + managed-Postgres offering name (implementation kickoff); `Command` base class + dispatcher concrete design with history-write step inside (implementation); per-invariant isolation-primitive assignment — `SERIALIZABLE` vs. `pg_try_advisory_xact_lock` per invariant (implementation); audit-log write timing — in-txn vs. post-commit (implementation); `backend/` and `frontend/` stale-scaffolding cleanup (implementation per ADR-0001 + ADR-0051).

**Step 9 inheritance:** Data-layer shape is now concrete enough that Step 9's conceptual data-model sketch can hang off it directly — entity tables for the 21 entities, 9 per-entity history tables, 1 shared audit-log table, all under Postgres 15+ via SQLAlchemy 2.0 + Alembic. The conceptual model in Step 9 is attribute-level / relationship-level / typed-reference-level only — DDL stays in the implementation phase.

**Files touched:** `planning/decisions.md` — ADR-0052 appended. `planning/architecture.md` — new file created. `planning/_file-rules.md` — regenerated (architecture.md entry added between domain-model.md and mvp.md; last-regen date updated to 2026-05-16). `planning/steps.md` — Step 8b marked ✓ COMPLETE inline. `planning/handoff.md` — Current phase line, Last session summary, Open questions, Next session pointer + prompt, Pointers (step-list + Decisions log + file-rules last-regen + architecture.md added).

---

## Open questions

**Step 9a structural choices (Q1–Q6) settled in Session 23.** No 9a-execution open questions remain; the session plan is canvassed, recommendations accepted, ready to execute next session.

**Substantive design gaps to watch for during 9a attribute drafting** (if any surfaces, flag at the STOP-AND-CONFIRM gate and defer rather than decide in 9a — per Q6 scope discipline). Most likely candidates:
- Time Entry `off_site_sub_intervals` representation shape (list-of-pairs as JSONB? separate table?). ADR-0034 declared the semantic shape; storage representation may be open.
- Contract `code_flat_fee_schedule` storage representation (inline JSONB? separate associative table?). ADR-0043/0045 declared as "inline non-temporal `{code_type, fee}` collection" — representation may be implicit but not pinned.
- Note polymorphic `target` + `references` shape (target is `(entity_type, entity_id)` or polymorphic-with-history-record per ADR-0040 extension; `references` is Note→Note per ADR-0032). Representation may need a Note-internal discriminator beyond the existing `subtype`.

If pinned by ADR text on closer reading, cite the ADR; if open, surface and defer (likely to implementation phase per the Q6 discipline).

**Carried into 9b (verify at 9b's session head):**
- Consolidation candidate count — preview puts it at 1 firm (ADR-0032, 4 amendments) + 1–2 borderline (ADR-0027 likely 2–3; ADR-0037 likely 1–2). If >2 qualify (per the partition mitigation), re-run the fit checklist on 9b and partition further.
- Roadmap milestone shape — implementation-phase step list drawn from `mvp.md`'s 6 must-have features + the 7 command-shape carry-forwards + the implementation-phase carry-forwards from ADR-0051 + ADR-0052 (PaaS vendor pick, `Command` dispatcher concrete design, per-invariant isolation-primitive assignment, audit-log write timing, stale-scaffolding cleanup).

**Process notes (apply to 9a):**
- STOP-AND-CONFIRM gate applies — each entity-section structural decision (e.g., kind of an ambiguous attribute, how to represent a polymorphic ref, whether to split or merge a derived-from-stored attribute pair) surfaces in chat with options + tradeoffs before writing.
- No new ADRs expected. If a substantive design gap surfaces, surface + defer.
- `data-model.md` needs a `## File contract` block. Trigger `_file-rules.md` regeneration in the completion protocol since a new planning file is being added.
- Recommendation strength: state confidence; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).

## Next session

**Step 9a — `data-model.md`.** Single-concern artifact: 21-entity attribute roster + relationship table + typed-ref shape + history-table reference column per ADR-0052. **Conceptual only — not DDL.** Brief in `steps.md` → § Step 9a. Execution order: Step 7 ✓ → Step 8 partitioned ✓ → Step 8a ✓ → Step 8b ✓ → Step 9 partitioned ✓ → **Step 9a** → Step 9b → (phase transition → Implementation). No new ADRs expected for 9a — `data-model.md` is a documentation artifact, not a decision artifact; the data layer is already pinned by ADR-0052. (ADR-0053 reserved for 9b's consolidation pass / phase-transition ADR.)

### Prompt for the next session

> Resume work. Next is **Step 9a — `planning/data-model.md`**. Brief in `steps.md` → § Step 9a. Step 9 was partitioned 2026-05-16 (Option A, single-concern seam) — 9a is `data-model.md` alone; 9b is consolidation pass + `roadmap.md` + phase-transition ADR. Sizing already done; this session is Case-3 scoped.
>
> **Read first:** this prompt + the Open questions block above + `domain-model.md` (the 21-entity roster + per-entity histories + relationships + lifecycles — the primary input) + `framework.md` (typed-ref shape + derived-fields rule) + `architecture.md` (ADR-0052 data-layer topology) + `decisions.md` clusters: ADR-0044 / 0045 / 0048 (WABundle / Contract re-homing / WACodeAssignment), ADR-0032 / 0042 / 0046 / 0049 (blocker model), ADR-0035 / 0041 (EmployeeRole + Time Entry temporal model), ADR-0015 / 0041 (Document derivation set), ADR-0018 + Note amendments across the cluster, ADR-0052 (data-layer topology). `logic.md` + `history-patterns.md` skim only — command-side context already pinned.
>
> **Items in scope (per `steps.md` → Step 9a):**
> 1. **Entity attributes.** For each of the 21 entities: intrinsic + lifecycle (state field where applicable) + derived-if-cheap attributes per `framework.md`. Engine-specific column types noted as "to be implemented with X" (e.g., JSONB, PostGIS) — not specified as DDL.
> 2. **Relationship table.** Typed references per `framework.md`. Cover the WABundle / Contract / WA / WACodeAssignment / Site cluster (ADR-0044/0045/0048); the polymorphic Note target (ADR-0018 + amendments); the EmployeeRole temporal model (ADR-0035 + ADR-0041); the Document derivation-set (ADR-0015 + ADR-0041); etc.
> 3. **History-table reference column.** Per entity, name the history surface per ADR-0052: per-entity history table name (for the 9 entities in 3-comprehensive + 6-lifecycle), or "`command_audit_log` (polymorphic)" (for the 7 audit-log entities), or "no history" (for the 5 no-history entities). Conceptual entry only — not the column schema.
>
> **Out of scope — 9b or implementation phase:**
> - DDL (implementation phase first step).
> - `roadmap.md`, consolidation pass, phase-transition ADR (9b).
> - `Command` base class + dispatcher concrete design (implementation per ADR-0051 + ADR-0052).
> - PaaS vendor pick + managed-Postgres offering name (implementation kickoff per ADR-0051 + ADR-0052).
> - Per-invariant isolation-primitive assignment + audit-log write timing (implementation per ADR-0052).
> - Stale-scaffolding cleanup of `backend/` and `frontend/` (implementation-phase opening session per ADR-0001 + ADR-0051).
>
> **No ADRs expected.** `data-model.md` is a documentation artifact — it rolls up already-pinned decisions into one conceptual view of the data layer. Any new design decision surfacing here should be canvassed at the STOP-AND-CONFIRM gate and flagged as out-of-scope for 9a unless trivial.
>
> **Reference:** 21 entities (post-ADR-0048), 14 design patterns, roles `superadmin`/`admin`/`coordinator`/`auditor`, 10-entry blocker registry, Conceptualization phase carries ADR-0001 through ADR-0052. Data layer pinned: PostgreSQL 15+ via SQLAlchemy 2.0 + Alembic; 9 per-entity history tables (3 comprehensive — Document/WA/RFA; 6 lifecycle — Project/Sample Batch/Deliverable/EmployeeRole/WA Code/ContractorEngagement) + 1 shared `command_audit_log` (polymorphic) for the 7 audit-log entities (Employee/User/Time Entry/Contractor/DepFiling/Contract/WABundle) + no history infrastructure for the 5 no-history entities (School/Note/UserRole/WACodeAssignment/WABundleSite); capture enforced in the `Command` base class + dispatcher.
>
> **Process notes:**
> - STOP-AND-CONFIRM gate applies — surface structure decisions in chat (e.g., per-entity attribute scope; how granular to make the relationship table; whether to inline lifecycles or point to `domain-model.md`) with options + tradeoffs before writing.
> - `data-model.md` needs a `## File contract` block. Trigger `_file-rules.md` regeneration in the completion protocol since a new planning file is being added.
> - Recommendation strength: state confidence; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-16)
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6 ✓ COMPLETE — 6a / 6b core / 6b-residual / 6b-residual-2 / 6c-i / 6c-ii / 6c-iii-a / 6c-iii-b-i / 6c-iii-b-ii / 6c-iv-a / 6c-iv-b / 6d all complete; **Step 7 ✓ COMPLETE**; **Step 8 partitioned 2026-05-15 — 8a ✓ COMPLETE (ADR-0051), 8b ✓ COMPLETE (ADR-0052 + `architecture.md`)**; **Step 9 partitioned 2026-05-16 — 9a (`data-model.md`), 9b (consolidation pass + `roadmap.md` + phase-transition ADR)**; next: **Step 9a**)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0052; next ADR at write time: ADR-0053)
- **MVP scope (Step 7 output):** `planning/mvp.md` — 6 must-have features + categorized "not now" list + 1 carve-out + 7 command-shape carry-forwards + pointers. Canonical MVP-scope reference.
- **Domain model (Step 6d output):** `planning/domain-model.md` — rolled-up domain projection: 21 entities, relationship table, per-entity lifecycles, authorization predicates (via ADR-0047), history patterns, delete policy, 14 design patterns, 10-entry blocker registry, vocabulary, deferred / open questions
- **Architecture (Step 8b output):** `planning/architecture.md` — one-page sketch: component diagram (Browser → CDN/SPA → API container → managed Postgres on managed PaaS), boundary semantics per layer, successful-command 10-step data flow, out-of-band concerns (file storage / background jobs / notifications / auth) flagged for implementation phase, pointers.
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md` (superseded by `mvp.md` § Not now; retained for trace continuity)
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
