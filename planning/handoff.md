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

**Conceptualization** — steps are planning-only, no code is written. **Step 8a (stack: language/runtime + framework + deployment) complete 2026-05-15 (session 21) — ADR-0051 landed.** Stack pinned at Python 3.12+ / FastAPI / SQLAlchemy 2.0 / Alembic / Pydantic / Ruff / Pytest on the backend; TS / React / Vite / TanStack Router / TanStack Query / openapi-ts / Storybook on the frontend; monolith container on managed PaaS (vendor TBD at implementation), Neon free-tier Postgres as dev default on both work machines + SQLite as offline fallback. Conceptualization-phase work remaining: **Step 8b → Step 9 (data-model sketch + roadmap + phase-transition ADR)**. See `planning/phases.md` for the full phase roster and `planning/steps.md` for the current step list.

## Last session summary

**Session 21 — Step 8a Stack ADR. ✓ COMPLETE (2026-05-15, ADR-0051).** Case-3 scoped — the runtime-stack triple (language/runtime + framework + deployment). All three sub-decisions canvassed at the STOP-AND-CONFIRM gate before the write.

**Local decision at session head:** Bundled into a single ADR-0051 ("Runtime stack") rather than three separate ADRs — the three decisions are coupled (lang rules in/out framework and deployment), and ADR-0009/0010/0012's three-way split was structurally justified by *different declaration surfaces* (state machine / entity / command) which this triple does not share.

**Three sub-decisions settled:**
- **(D1) Language/runtime → Python 3.12+ on CPython** (backend); TypeScript on Node for frontend tooling. Canvassed against TS-on-Node (agent's initial recommendation) and TS-on-Bun/Deno; non-candidates Rust/Go/JVM/C#/Elixir ruled out at canvass head. Settled Python after honest comparison: the openapi-ts → TanStack Query pipeline cancels the FE-BE-type-sharing argument for TS; Pydantic does runtime validation more honestly than zod (schema *is* the validator); SQLAlchemy 2.0 + Alembic migration maturity meaningfully exceeds Drizzle/Prisma. Residual TS exhaustiveness edge mitigated in Python with discipline (Pydantic discriminated unions + `match`/`case` + base `Command` class + `assert_never`).
- **(D2) Framework → FastAPI backend + React/Vite/TanStack frontend.** Backend canvassed against Django (admin-UI win not enough to justify weight at MVP's narrow admin surface) and plain Starlette/Flask (weaker validation story). Frontend canvassed against Next.js (RSC/middleware/caching machinery overkill for an internal tool — user's "bloat" concern operationally correct) and Remix. Supporting libs pinned: SQLAlchemy 2.0 + Alembic + Pydantic + Ruff + Pytest (backend); Vite + TanStack Router + TanStack Query + openapi-ts + Storybook + ESLint + Prettier (frontend). Architectural pin: routes are transport, commands are the unit — thin `Command` base class + dispatcher (design carried to implementation phase) hosts the `logic.md` pipeline.
- **(D3) Deployment → monolith container on managed PaaS (vendor TBD)**, static SPA on same platform CDN, dev DB config-driven with **Neon free-tier Postgres** as default on both work machines + **SQLite as offline fallback**, CI tests against Postgres, engine-specific code behind adapter boundary. Rejected: service split (no scale/cadence/isolation pressure), serverless (cold-start UX tax + pooling/background-job complexity), major-cloud-direct AWS/GCP (weeks of IAM/VPC/IaC plumbing at MVP scale), self-hosted VPS (sysadmin load not worth $5-20/month savings). User's initial SQLite-as-dev-default proposal revised after honest pushback on the ADR-0010 concurrency-bug class — Machine B's constraint is Docker-lock not internet-lock, so Neon resolves it at $0/month.

**Carry-forwards (per ADR-0051):** specific PaaS vendor (implementation kickoff); `Command` base class + dispatcher design (implementation); frontend test runner pick (implementation); stale-scaffolding cleanup of `backend/` and `frontend/` (implementation per ADR-0001); persistence engine + history-impl shape + `architecture.md` (Step 8b — next session).

**Step 8b inheritance:** ADR-0051 passes one constraint forward — the persistence engine must be SQLAlchemy-supported, RDBMS-class, available as a managed offering on the chosen PaaS, AND support concurrency primitives strong enough for ADR-0010's cross-entity-invariant-revalidation requirement. Postgres overwhelmingly likely but not foreclosed.

**Files touched:** `planning/decisions.md` — ADR-0051 appended. `planning/handoff.md` — Current phase line, Last session summary, Open questions, Next session pointer + prompt, Pointers step-list + Decisions log lines. No other planning files touched. `_file-rules.md` not regenerated (no file contracts changed).

---

*(Prior session retained for context — Session 20 / Step 8 sizing + partition.)*

**Session 20 — Step 8 sizing + partition. ✓ COMPLETE (2026-05-15).** Case-2 sizing — Step 8 tripped 4 fit-checklist signals (1: 5 sub-decisions in ~3 coupling-groups; 3: >60 min with 5 sub-decisions + new file; 4: input reading >3 substantial planning files; 5: cross-concern reach runtime/serving vs. storage/history-impl). Partitioned along Option B (coupling-respecting seam): **Step 8a — Stack (language/runtime + framework + deployment)** → **Step 8b — Persistence + history-impl shape + `architecture.md`**. Options A (handoff's original suggested seam — stack vs. data+deployment) and C (3-way split with deployment alone) rejected. `planning/steps.md` and `planning/handoff.md` updated; no ADRs written; no other planning files touched.

---

## Open questions

**Carried into Step 8b from ADR-0051:** the persistence engine must be **SQLAlchemy-supported, RDBMS-class, available as a managed offering on the chosen PaaS, AND support concurrency primitives strong enough for ADR-0010's cross-entity-invariant-revalidation requirement** (serializable transactions, advisory locks, or equivalent). Postgres is overwhelmingly likely but ADR-0051 does not foreclose alternatives. The dev-default Neon Postgres + SQLite-offline-fallback shape from ADR-0051 also constrains 8b's choice — engine must accommodate that env-config model.

**For the next session — Step 8b (persistence + history-impl shape + `architecture.md`):**

Step 8b decides the data layer (persistence engine + history-impl shape) and writes the one-page architecture sketch covering both 8a's runtime layer and 8b's data layer.

**Items in scope (per `steps.md` → Step 8b):**

1. **Persistence engine.** RDBMS (Postgres / SQLite-and-Postgres / …) vs. event store vs. document store vs. hybrid. Constrained by the ADR-0051 inheritance (see above).
2. **History implementation shape.** Event store vs. append-only tables vs. temporal tables vs. hybrid. Must honestly support all 4 patterns in use across 21 entities per `domain-model.md`: Comprehensive (3 — Document / WA / RFA), Lifecycle (6 — Project / Sample Batch / Deliverable / EmployeeRole / WA Code / ContractorEngagement), Audit log (7 — Employee / User / Time Entry / Contractor / DepFiling / Contract / WABundle), No history (5 — School / Note / UserRole / WACodeAssignment / WABundleSite). Per-pattern reconstructability requirements in `history-patterns.md` constrain honest choices. ADR-0008 (mandatory capture at command boundary) is load-bearing on whichever impl shape lands. ADR-0003 was superseded by ADR-0006 (per-entity decision).
3. **`planning/architecture.md`** — one-page sketch (component boxes, data flow). New file; add a `## File contract` block. Lands here after both data-layer decisions settle, avoiding drafting the sketch twice.

**Inputs (per the step brief):** ADR-0051 (8a's stack — defines what data-layer choices the runtime can host); `history-patterns.md` (the pattern menu); `domain-model.md` § History patterns per entity (3/6/7/5 distribution); `mvp.md`; `framework.md`; `decisions.md` (esp. ADR-0006 per-entity history; ADR-0008 mandatory capture; ADR-0010 invariant-isolation requirement); `handoff.md` (this file).

**Local decision at session head:** single bundled ADR for persistence + history-impl, or split into two? They're coupled (history-impl shape depends on engine capabilities — e.g., temporal tables need engine support, append-only history tables are engine-neutral) but conceptually separable in ways ADR-0051's three sub-decisions weren't. Decide at session head.

**Process notes:**
- STOP-AND-CONFIRM gate applies. Each sub-decision (persistence engine, history-impl shape) surfaces options + tradeoffs in chat before any ADR write.
- `architecture.md` lands AFTER both ADR sub-decisions settle, to avoid drafting the sketch twice.
- Recommendation strength: state confidence; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).

## Next session

**Step 8b — Persistence + history-impl shape + `architecture.md`.** Case-3 scoped — the partition decision settled session 20; Step 8a settled session 21 (ADR-0051). Goal: pick persistence engine + history-impl shape; write the supporting ADR(s); draft `planning/architecture.md` after both data-layer decisions settle. Brief in `steps.md` → Step 8b. Execution order: Step 7 ✓ → Step 8 partitioned ✓ → Step 8a ✓ → **Step 8b** → Step 9 (data model sketch + roadmap + phase-transition ADR + pre-transition ADR consolidation pass). ADR numbers at write time: starting at **ADR-0052**.

### Prompt for the next session

> Resume work. Next is **Step 8b — Persistence + history-impl shape + `architecture.md`**. Brief in `steps.md` → § Step 8b. Case-3 scoped — Step 8a settled session 21 (ADR-0051).
>
> **Read first:** this prompt + the Open questions block above + **ADR-0051** in `decisions.md` (the stack-side decisions; constrains 8b's persistence engine to SQLAlchemy-supported, RDBMS-class, managed PaaS offering, ADR-0010 isolation primitives, and the Neon-dev/SQLite-offline env-config model) + `history-patterns.md` (the pattern menu) + `domain-model.md` § History patterns per entity (3/6/7/5 distribution across Comprehensive / Lifecycle / Audit log / No history) + `framework.md` (entity/state taxonomy) + `decisions.md` for ADR pointers (esp. ADR-0006 per-entity history; ADR-0008 mandatory capture; ADR-0010 invariant-isolation requirement).
>
> **Items in scope (per `steps.md` → Step 8b):**
> 1. **Persistence engine.** Constrained by ADR-0051 inheritance. Postgres overwhelmingly likely but not foreclosed.
> 2. **History implementation shape.** Event store / append-only tables / temporal tables / hybrid. Must honestly support all 4 patterns in use across 21 entities; per-pattern reconstructability requirements in `history-patterns.md` constrain honest choices.
> 3. **`planning/architecture.md`** — one-page sketch (component boxes, data flow). New file; needs a `## File contract` block. Lands after both ADR sub-decisions settle, to avoid drafting twice. Add `architecture.md` entry to `_file-rules.md` (regen) when it lands.
>
> Single bundled ADR or split into two — decide at session head.
>
> **Out of scope — later steps:**
> - Conceptual data model + DDL (Step 9).
> - Roadmap (Step 9).
> - Phase-transition ADR + pre-transition ADR consolidation pass (Step 9).
> - Stack-side decisions (settled in ADR-0051 — runtime, framework, deployment, dev DB workflow).
> - Command-shape carry-forwards (implementation phase per `mvp.md` § Command-shape carry-forwards).
>
> **Sequencing:** Step 7 ✓ → Step 8 partitioned ✓ → Step 8a ✓ → **Step 8b (this session)** → Step 9 → (phase transition).
>
> **Reference:** 21 entities (post-ADR-0048), 14 design patterns, roles `superadmin`/`admin`/`coordinator`/`auditor`, 10-entry blocker registry, Conceptualization phase carries ADR-0001 through ADR-0051. Stack pinned: Python 3.12+ / FastAPI / SQLAlchemy 2.0 / Alembic / Pydantic backend + TS / React / Vite / TanStack frontend on managed-PaaS monolith deployment with Neon-dev / SQLite-offline DB config. Full detail in `domain-model.md` + `mvp.md` + ADR-0051.
>
> **Process notes:**
> - STOP-AND-CONFIRM gate applies — each sub-decision surfaces in chat with options + tradeoffs before any ADR write.
> - `architecture.md` lands AFTER both ADR sub-decisions settle.
> - Recommendation strength: state confidence; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-15)
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6 ✓ COMPLETE — 6a / 6b core / 6b-residual / 6b-residual-2 / 6c-i / 6c-ii / 6c-iii-a / 6c-iii-b-i / 6c-iii-b-ii / 6c-iv-a / 6c-iv-b / 6d all complete; **Step 7 ✓ COMPLETE**; **Step 8 partitioned 2026-05-15 — 8a ✓ COMPLETE (ADR-0051), 8b next (persistence + history-impl shape + `architecture.md`)**; next: **Step 8b**)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0051; next ADR at write time: ADR-0052)
- **MVP scope (Step 7 output):** `planning/mvp.md` — 6 must-have features + categorized "not now" list + 1 carve-out + 7 command-shape carry-forwards + pointers. Canonical MVP-scope reference.
- **Domain model (Step 6d output):** `planning/domain-model.md` — rolled-up domain projection: 21 entities, relationship table, per-entity lifecycles, authorization predicates (via ADR-0047), history patterns, delete policy, 14 design patterns, 10-entry blocker registry, vocabulary, deferred / open questions
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md` (superseded by `mvp.md` § Not now; retained for trace continuity)
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
