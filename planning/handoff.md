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
>
> **Do NOT recommend a position. Do NOT write ADRs. Do NOT modify any planning file (or any other file) in the proposal turn.** Wait for the user's explicit `approved` (or amendments) before touching files. If you're unsure whether something counts as a file modification, ask.
>
> If two decisions are genuinely inseparable, say so and explain why — but default to splitting. Roadmap length is not a constraint; splitting a session into more sessions is preferred over rushing a decision.
>
> **This gate exists because prior sessions (twice on 2026-04-28) stacked or pre-answered decisions.** "The artifact is the deliberation" (rule 1 in `planning/sessions.md`) means the doc canvasses options before landing — it does **not** mean writing first and asking later. Agreement on the position is gated on the chat-side proposal; the doc then writes it up.

---

## How to start a session

If the user says something like _"resume work"_ / _"start the next session"_ / _"run the next session"_ / _"do the next session block"_ / _"vamos"_ / _"yallah"_: follow `planning/_workflow.md`. That file owns the case-detection logic and the completion protocol.

---

## Current phase

**Conceptualization** — steps are planning-only, no code is written. See `planning/phases.md` for the full phase roster and `planning/steps.md` for the current step list.

## Last session summary

**Step 1 — Abstract entity & state framework (2026-04-28).** Wrote `planning/framework.md` with one position per question (entity definition, four-kind state taxonomy, relationship defaults, identity policy). Added ADR-0002 through ADR-0005 capturing the rejected alternatives. Framework is intentionally thin — it commits to vocabulary, not modeling structure, so Step 3 has room to push back when the domain lands. History implementation shape, cross-system identity, soft-delete policy, and concrete lifecycle vocabularies are explicitly deferred (see "Deferred" section in `framework.md`).

## Open questions

- History _implementation_ shape (event store, append-only history tables, temporal tables) — deferred to Step 8 (stack). Step 2 commits the logic-layer semantics; Step 8 picks the storage.
- History patterns menu — the available per-entity history patterns and selection criteria are defined in Step 5, before domain mapping. TBD.
- Cross-system identity (do our UUIDs need to be stable across other agency systems?) — deferred to Step 6 (domain mapping).
- Soft-delete vs. hard-delete policy — likely regulatory; Step 6.
- Concrete lifecycle vocabularies per entity — Step 6, once entities exist.
- Concrete authorization roles and relationships — Step 6. Step 4 picks the shape; the predicates land in Step 6.
- Whether the existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

## Next session

**Step 2 — Transitions & history-semantics.** See `planning/steps.md` for the full brief (decisions on the table + candidate positions with tradeoffs).

### Prompt for the next session

> Produce the transitions-and-history-semantics section of `planning/logic.md` and ADR entries closing off the two coupled decisions.
>
> Stay abstract — do **not** introduce environmental-monitoring domain terms. Build directly on `framework.md`'s vocabulary (entity, the four kinds of state, relationships, UUID identity). The decisions on the table and the candidate positions with their tradeoffs are pre-canvassed in `planning/steps.md` under "Step 2."
>
> Two decisions to close:
>
> 1. **Transition unit.** Direct writes, commands as named operations, or events as primary?
> 2. **History semantics.** Event-producing, state-mutating with mandatory history capture, or state-mutating with bolted-on audit log?
>
> The two are coupled — picking "events as primary" in (1) largely forces "event-producing" in (2). Be explicit about the coupling in the doc.
>
> Constraints:
>
> - One position per decision. Rejected alternatives go in ADR entries (one ADR per decision).
> - Defer the _implementation_ shape (event store vs temporal tables vs append-only history tables) to Step 8 (stack).
> - Do not pre-empt lifecycle rules, invariants, or authorization — those are Steps 3 and 4.
> - Do not pre-empt the per-entity history-pattern decisions — those are Step 5. Step 2 establishes the framework-level history infrastructure; Step 5 defines the menu of patterns entities choose from.
> - If you would push back on a framework commitment before answering, say so before writing.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0006)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output, not yet written): `planning/logic.md`
- History patterns (Step 5 output, not yet written): `planning/history-patterns.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
