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

**Conceptualization** — steps are planning-only, no code is written. **Step 8b (data layer: persistence + history-impl + `architecture.md`) complete 2026-05-16 (session 22) — ADR-0052 + `planning/architecture.md` landed.** Data layer pinned at PostgreSQL 15+ via SQLAlchemy 2.0 + Alembic; per-entity append-only history tables (9 — 3 comprehensive + 6 lifecycle) + shared `command_audit_log` (polymorphic ref) for the 7 audit-log entities + no history infrastructure for the 5 no-history entities; capture enforced in the `Command` base class + dispatcher (carry-forward from ADR-0051); `SERIALIZABLE` default + `pg_try_advisory_xact_lock` opt-in for ADR-0010 cross-entity invariant isolation. `planning/architecture.md` drafted (component diagram + boundary semantics + 10-step successful-command data flow). Conceptualization-phase work remaining: **Step 9 (data-model sketch + roadmap + phase-transition ADR + pre-transition ADR consolidation pass)**. See `planning/phases.md` for the full phase roster and `planning/steps.md` for the current step list.

## Last session summary

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

*(Prior session retained for context — Session 21 / Step 8a Stack ADR.)*

**Session 21 — Step 8a Stack ADR. ✓ COMPLETE (2026-05-15, ADR-0051).** Case-3 scoped — the runtime-stack triple (language/runtime + framework + deployment). Bundled into ADR-0051 (three sub-decisions coupled — lang rules in/out framework and deployment). **D1 → Python 3.12+ on CPython** (backend) + TS on Node (frontend tooling) — canvassed against TS-on-Node (agent's initial recommendation) and TS-on-Bun/Deno; settled Python after honest comparison (openapi-ts cancels FE-BE-type-sharing argument; Pydantic more honest than zod; SQLAlchemy + Alembic maturity exceeds Drizzle/Prisma). **D2 → FastAPI backend + React/Vite/TanStack frontend** with SQLAlchemy 2.0 + Alembic + Pydantic + Ruff + Pytest (backend) and Vite + TanStack Router + TanStack Query + openapi-ts + Storybook + ESLint + Prettier (frontend); routes-as-transport / commands-as-unit pin with thin `Command` base class + dispatcher carried to implementation. **D3 → monolith container on managed PaaS** (vendor TBD); static SPA on platform CDN; Neon free-tier Postgres dev default + SQLite offline fallback; CI tests against Postgres; engine-specific code behind adapter boundary. Rejected: service split, serverless (cold-start UX tax), major-cloud-direct, self-hosted VPS, SQLite-as-dev-default. Passed one constraint forward to Step 8b (persistence engine must be SQLAlchemy-supported, RDBMS-class, managed offering on chosen PaaS, ADR-0010 isolation primitives, Neon-dev/SQLite-offline env-config model) — answered in this session (Session 22) by ADR-0052's Postgres pick.

---

## Open questions

**Carried into Step 9 from ADR-0052:** Data-layer shape is now concrete enough that Step 9's conceptual data-model sketch can hang off it directly — 21 entity tables, 9 per-entity history tables (3 comprehensive + 6 lifecycle), 1 shared `command_audit_log` table, all on PostgreSQL 15+ via SQLAlchemy 2.0 + Alembic. The conceptual model is attribute-level / relationship-level / typed-reference-level only — **DDL stays in the implementation phase**. Engine-specific column types (JSONB, PostGIS, etc.) are noted as "to be implemented with X" in the conceptual model, not specified in DDL.

**For the next session — Step 9 (data model sketch + roadmap + phase-transition ADR + pre-transition ADR consolidation pass):**

Step 9 is the closing step of the Conceptualization phase. It produces three artifacts and triggers the phase transition.

**Items in scope (per `steps.md` → Step 9):**

1. **`planning/data-model.md`** — conceptual data model. Entities (the 21-entity roster from `domain-model.md`), their attributes (intrinsic + lifecycle + derived-if-cheap), relationships (typed references per `framework.md`), and references to history-table + audit-log topology per ADR-0052. **Not DDL** — conceptual only.
2. **`planning/roadmap.md`** — ordered implementation milestones with rough sizing. The implementation phase's step list, sized at coarse granularity.
3. **Pre-transition ADR consolidation pass (one-time).** Scan `decisions.md` for ADRs with 2+ amendments; consolidate each into a fresh, definitive ADR (mark old ones `superseded by #N`). Skip if no ADR has accumulated 2+ amendments. Per session-9 deliberation: phase boundary is the right moment for this — deliberation is settled, the resulting record becomes the foundation for implementation-phase work.
4. **Phase-transition ADR.** "Conceptualization phase complete; implementation begins." Triggers the four `phases.md` writes per `_workflow.md`'s phase-roster protocol: mark Conceptualization complete; mark Implementation current; archive `steps.md` to `steps.archive/conceptualization.md`; create new `steps.md` for the implementation phase (drawing from `roadmap.md`). Lightweight gate per `_workflow.md`.

**Inputs (per the step brief):** all prior planning files. The dominant ones: `framework.md`, `logic.md`, `history-patterns.md`, `domain-model.md`, `mvp.md`, `architecture.md`, `decisions.md` (ADRs 0001–0052), `handoff.md` (this file).

**Local decision at session head:**
- (a) **Sizing.** Step 9 bundles three deliverables (data-model.md + roadmap.md + phase-transition ADR) + one one-time pass (ADR consolidation). Run the `_workflow.md` Case 2 fit checklist at session head. Cross-concern reach (data modeling vs. roadmap planning vs. archival/governance) is real; signal 5 likely fires. Likely partition: **9a (data-model.md) → 9b (roadmap.md + consolidation pass + phase-transition ADR)**, but call it at the session head, not now.
- (b) **Consolidation candidates.** A quick scan of `decisions.md` for ADRs with 2+ amendments before partitioning — if zero, item 3 dissolves. ADRs known to have multiple amendments: ADR-0010 (now amended-by-deferral-answer in ADR-0052 — but that's the answer, not an amendment; count carefully), ADR-0017 (amended by ADR-0044), ADR-0027 (dropped from amendment set by ADR-0045 + retired by ADR-0049), ADR-0032 (extended by ADR-0042 + ADR-0046 + ADR-0049), ADR-0035 (amended by ADR-0045), ADR-0037 (amended by ADR-0043). ADR-0032 is the obvious 2+-amendments candidate; check ADR-0044 / ADR-0043's reach for any others. Treat as a sizing input, not a step output.

**Process notes:**
- STOP-AND-CONFIRM gate applies. Each substantive decision (entity attribute choices, relationship modeling, roadmap milestones, consolidation pass conclusions) surfaces in chat before any file write.
- Sizing first: run the Case 2 fit checklist at session head. Step 9 is the most likely-to-overflow step in the phase; partitioning is the default expectation, not the exception.
- Recommendation strength: state confidence; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).

## Next session

**Step 9 — Data model sketch + roadmap + phase-transition ADR + pre-transition ADR consolidation pass.** Case-2 sizing expected first — Step 9 is the most likely-to-overflow step in the phase (three deliverables + one one-time pass + cross-concern reach data-modeling vs. roadmap-planning vs. archival/governance). Likely partition at session head: **9a (data-model.md) → 9b (roadmap.md + consolidation pass + phase-transition ADR)**. Brief in `steps.md` → Step 9. Execution order: Step 7 ✓ → Step 8 partitioned ✓ → Step 8a ✓ → Step 8b ✓ → **Step 9** → (phase transition → Implementation phase). ADR numbers at write time: starting at **ADR-0053**.

### Prompt for the next session

> Resume work. Next is **Step 9 — Data model sketch + roadmap + phase-transition ADR + pre-transition ADR consolidation pass**. Brief in `steps.md` → § Step 9. Sizing first — likely Case-2 partition at session head.
>
> **Read first:** this prompt + the Open questions block above + `framework.md` + `logic.md` + `history-patterns.md` + `domain-model.md` (the 21-entity roster + per-entity histories + relationships + lifecycles) + `mvp.md` (the cut — defines what the implementation roadmap must deliver first) + `architecture.md` (stack + data-layer sketch) + `decisions.md` (esp. ADR-0050 MVP scope, ADR-0051 stack, ADR-0052 data layer, plus ADR-0032 / 0042 / 0046 / 0049 cluster for blocker model, ADR-0044 / 0048 cluster for WA/WABundle model, ADR-0043 / 0045 cluster for Contract model).
>
> **Items in scope (per `steps.md` → Step 9):**
> 1. **`planning/data-model.md`** — conceptual data model. 21-entity roster + attributes + relationships + typed-reference shape + history-table references per ADR-0052. **Conceptual only — not DDL.** Engine-specific column types noted as "to be implemented with X" not specified.
> 2. **`planning/roadmap.md`** — ordered implementation milestones with rough sizing. The implementation phase's step list at coarse granularity, drawn from `mvp.md`'s 6 must-have features + carry-forward mechanics.
> 3. **Pre-transition ADR consolidation pass (one-time).** Scan `decisions.md` for ADRs with 2+ amendments; consolidate each into a fresh definitive ADR (mark old ones `superseded by #N`). Skip if no ADR has accumulated 2+ amendments. Likely candidates: **ADR-0032** (extended by 0042 / 0046 / 0049 — almost certainly 2+ amendments); check ADR-0017 (amended by 0044), ADR-0035 (amended by 0045), ADR-0037 (amended by 0043), ADR-0044 (cluster amendments). Quick scan at session head before sizing.
> 4. **Phase-transition ADR.** "Conceptualization phase complete; implementation begins." Triggers the four `phases.md` writes per `_workflow.md`'s phase-roster protocol (mark Conceptualization complete; mark Implementation current; archive `steps.md` to `steps.archive/conceptualization.md`; create new `steps.md` for implementation).
>
> **Local decision at session head:** sizing. Run the `_workflow.md` Case 2 fit checklist. Likely partition: **9a (data-model.md) → 9b (roadmap.md + consolidation pass + phase-transition ADR)**, but call it explicitly. The consolidation pass is sequenced before the phase-transition ADR per `steps.md` § Step 9 — keep that order.
>
> **Out of scope — later phase:**
> - DDL (implementation phase first step).
> - `Command` base class + dispatcher concrete design (implementation phase, per ADR-0051 + ADR-0052 carry-forwards).
> - PaaS vendor pick + managed-Postgres offering name (implementation kickoff per ADR-0051 + ADR-0052).
> - Per-invariant isolation-primitive assignment (implementation phase per ADR-0052).
> - Audit-log write timing (implementation phase per ADR-0052).
> - Stale-scaffolding cleanup of `backend/` and `frontend/` (implementation-phase opening session per ADR-0001 + ADR-0051).
> - Command-shape carry-forwards (implementation phase per `mvp.md`).
>
> **Sequencing:** Step 7 ✓ → Step 8 partitioned ✓ → Step 8a ✓ → Step 8b ✓ → **Step 9 (this session — likely partitioned to 9a / 9b)** → (phase transition → Implementation).
>
> **Reference:** 21 entities (post-ADR-0048), 14 design patterns, roles `superadmin`/`admin`/`coordinator`/`auditor`, 10-entry blocker registry, Conceptualization phase carries ADR-0001 through ADR-0052. Stack pinned: Python 3.12+ / FastAPI / SQLAlchemy 2.0 / Alembic / Pydantic backend + TS / React / Vite / TanStack frontend on managed-PaaS monolith deployment with Neon-dev / SQLite-offline DB config. Data layer pinned: PostgreSQL 15+; 9 per-entity history tables + 1 shared `command_audit_log` table; capture in the `Command` dispatcher. Full detail in `domain-model.md` + `mvp.md` + `architecture.md` + ADR-0051 + ADR-0052.
>
> **Process notes:**
> - STOP-AND-CONFIRM gate applies — each substantive decision (entity attribute choices, relationship modeling, roadmap milestones, consolidation conclusions) surfaces in chat with options + tradeoffs before any file write.
> - Sizing first: run the Case 2 fit checklist at session head; partitioning is the default expectation for Step 9, not the exception.
> - Recommendation strength: state confidence; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-16)
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6 ✓ COMPLETE — 6a / 6b core / 6b-residual / 6b-residual-2 / 6c-i / 6c-ii / 6c-iii-a / 6c-iii-b-i / 6c-iii-b-ii / 6c-iv-a / 6c-iv-b / 6d all complete; **Step 7 ✓ COMPLETE**; **Step 8 partitioned 2026-05-15 — 8a ✓ COMPLETE (ADR-0051), 8b ✓ COMPLETE (ADR-0052 + `architecture.md`)**; next: **Step 9** — likely partitioned to 9a / 9b at session head)
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
