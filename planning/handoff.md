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

**Step 5 — History & auditing patterns (2026-05-01).** Created `planning/history-patterns.md` with a four-pattern menu: (1) no history, (2) audit log, (3) comprehensive capture, (4) lifecycle capture. Patterns 1–2 are not history-carrying; patterns 3–4 are. Lifecycle capture refines ADR-0008's scope — only lifecycle-affecting commands produce history records, but capture within that scope remains mandatory and framework-enforced. ADR-0013 appended to `decisions.md` recording the pattern set, selection criteria, and positions on all four open questions. Reference snapshotting settled: typed UUIDs only, no denormalized copies. Promotion path documented: forward-only, no backfill. Quarantine excluded from the history menu — it's a violation-handling concern orthogonal to history, remains deferred per ADR-0011.

## Open questions

- Cross-system identity (do our UUIDs need to be stable across other agency systems?) — Step 6.
- Soft-delete vs. hard-delete policy — likely regulatory; Step 6.
- Concrete lifecycle vocabularies per entity — Step 6, once entities exist.
- Concrete authorization roles, relationships, and per-command predicates — Step 6. ADR-0012 picks the shape; the contents land in Step 6.
- **Quarantine as a per-entity violation-handling pattern** — excluded from the history-pattern menu (ADR-0013); remains deferred per ADR-0011. Could be commissioned as a separate per-entity declaration at Step 6 or a later step if specific entities warrant it.
- History _implementation_ shape (event store, append-only history tables, temporal tables) — Step 8 (stack), informed by Step 5's pattern menu (now written).
- **Persistence isolation for cross-entity invariants** — what guarantee the persistence layer must provide so the command-pipeline invariant check is meaningful under concurrency (serializable transactions, optimistic locking, advisory locks, etc.). Step 8.
- Whether the existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

## Next session

**Step 6 — Domain mapping.** See `planning/steps.md` for the full brief.

### Prompt for the next session

> Project the abstract framework onto the environmental-monitoring agency domain. Produce `planning/domain-model.md`.
>
> Build on all prior planning artifacts: `framework.md` (entity/state/relationship/identity vocabulary), `logic.md` (commands, lifecycle, invariants, authorization pipeline), `history-patterns.md` (four-pattern menu and selection criteria), and all ADRs (0001–0013).
>
> Deliverables:
>
> 1. **`planning/domain-model.md`** — the mapped domain. For each entity: name, what it is, its state kinds (intrinsic attributes, lifecycle states if any, derived state if any), relationships to other entities, and the history pattern chosen from `history-patterns.md` with a one-line justification using the selection criteria.
> 2. **ADR entries** for domain-shape decisions that close off alternatives.
>
> Constraints:
>
> - Every entity must have a history-pattern assignment. No entity may be defined without one.
> - Aim for the load-bearing 80% of the domain, not completeness. Lookup tables and edge-case entities can be added later.
> - Concrete lifecycle vocabularies (the actual state names per entity type) should be defined here — Step 3 picked the shape; this step fills in the contents.
> - Concrete authorization roles, relationships, and per-command predicates should be defined here — Step 4 picked the shape; this step fills in the contents.
> - Address the deferred open questions that land in Step 6: cross-system identity, soft-delete vs. hard-delete policy.
> - The user will supply domain context in the session. Ask if needed before writing.
>
> Open questions to address:
>
> - **Cross-system identity:** do our UUIDs need to be stable across other agency systems, or are external IDs just intrinsic attributes?
> - **Soft-delete vs. hard-delete policy:** likely regulatory — what does the domain require?
> - **Quarantine:** does any specific entity warrant commissioning quarantine as a violation-handling override (per ADR-0011's deferral, excluded from history menu by ADR-0013)?

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0013)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
