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

**Conceptualization** — steps are planning-only, no code is written. See `planning/phases.md` for the full phase roster and `planning/steps.md` for the current step list.

## Last session summary

**Step 3 — Lifecycle rules & invariants (2026-04-30).** Appended the lifecycle-and-invariants section to `planning/logic.md` (sub-sections for lifecycle specification, well-formedness invariants, violation handling, and a "cross-entity acknowledgement gating" pattern naming how the three ADRs combine) plus a short coupling section. ADR-0009 (lifecycle per entity type as a declarative state machine; commands declare the transition they effect), ADR-0010 (well-formedness invariants declared on the schema element they constrain; write-path enforcement in the command pipeline), and ADR-0011 (reject as the framework violation-handling default; quarantine deferred as a per-entity pattern) appended to `decisions.md`. User-supplied domain context (project tracking with three-layer state: base + inferred expectations, closeable gaps with per-requirement sign-off) reconciled abstractly — divergence between expected and actual outcomes is modeled as state via the four-kind taxonomy, not as a violation; the acknowledgement-gating pattern keeps sign-off structurally inescapable without committing to domain vocabulary. Quarantine-as-per-entity-pattern added to `logic.md`'s Deferred list.

## Open questions

- History _implementation_ shape (event store, append-only history tables, temporal tables) — Step 8 (stack), informed by Step 5's pattern menu.
- **Persistence isolation for cross-entity invariants** — what guarantee the persistence layer must provide so the command-pipeline invariant check is meaningful under concurrency (serializable transactions, optimistic locking, advisory locks, etc.). Step 8.
- Per-entity history-pattern menu and selection criteria — Step 5, before domain mapping.
- **Reference snapshotting:** when a history-carrying entity references a non-history entity (or another history-carrying one), what does the history record capture so the past reference remains interpretable? Surfaces as a Step 5 concern.
- **History-pattern promotion path:** how does an entity get promoted from "no history" to "history-carrying" mid-life? Backfill is impossible (the past is lost) — only forward-history is achievable. Step 5 should address this explicitly when defining the pattern menu.
- **Exact history-record contents** (full before/after vs. command + payload only vs. deltas) — varies per Step 5 pattern.
- **Quarantine as a per-entity violation-handling pattern** — whether to commission it (and on what criteria); ADR-0011 hedges between Step 5 and a later step.
- Cross-system identity (do our UUIDs need to be stable across other agency systems?) — Step 6.
- Soft-delete vs. hard-delete policy — likely regulatory; Step 6.
- Concrete lifecycle vocabularies per entity — Step 6, once entities exist.
- Concrete authorization roles and relationships — Step 6. Step 4 picks the shape; the predicates land in Step 6.
- Whether the existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

## Next session

**Step 4 — Authorization.** See `planning/steps.md` for the full brief (decisions on the table + candidate positions with tradeoffs).

### Prompt for the next session

> Produce the authorization section of `planning/logic.md` (append) and a single ADR closing off the authorization shape.
>
> Stay abstract — do **not** introduce environmental-monitoring domain terms. Build directly on `framework.md` (entities, identity) and `logic.md`'s transitions, history-semantics, and lifecycle-and-invariants sections (commands as the unit of change; cross-cutting concerns attach to commands; the command pipeline rejects on rule/invariant violation). The questions on the table and the candidate positions with their tradeoffs are pre-canvassed in `planning/steps.md` under "Step 4."
>
> Three coupled sub-questions to close in one ADR:
>
> 1. **Primary axis.** Role-based (RBAC), relationship-based (ReBAC), predicate over (caller, command, target), or hybrid?
> 2. **Predicate location.** On commands, on entities, in a separate policy layer?
> 3. **Form.** Declarative (inspectable, testable) or imperative (code in handlers)?
>
> Constraints:
>
> - One ADR for the authorization shape. Group rejected alternatives by sub-question inside the ADR.
> - Authorization predicates attach to commands (per ADR-0007) — the predicate is checked as part of the command pipeline, alongside lifecycle and invariant checks. Work with that surface, do not relitigate it. If you find a tension, name it inside the doc and deliberate it there (per `sessions.md` rule 3).
> - Concrete roles and relationships are deferred to Step 6. Step 4 picks the *shape* of the authorization predicate, not the contents.
> - Do not pre-empt per-entity history-pattern decisions (Step 5).
> - If you would push back on a framework or `logic.md` commitment before answering, say so before writing.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0011)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; Steps 2–3 sections written, Step 4 to append): `planning/logic.md`
- History patterns (Step 5 output, not yet written): `planning/history-patterns.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
