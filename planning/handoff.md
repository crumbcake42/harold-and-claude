# Handoff

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
> **This gate exists because prior sessions (twice on 2026-04-28) stacked or pre-answered decisions.** "The artifact is the deliberation" (rule 1 below) means the doc canvasses options before landing — it does **not** mean writing first and asking later. Agreement on the position is gated on the chat-side proposal; the doc then writes it up.

---

## How to start a session

If the user says something like _"start the next session"_ / _"run the next session"_ / _"do the next session block"_ / _"vamos"_ / _"yallah"_, treat that as: read this file, read `planning/decisions.md`, read the entry in `planning/sessions.md` matching the **Next session** below — and then **enter the STOP-AND-CONFIRM GATE above**. Deliver the chat-side proposal and wait for approval before executing the prompt in **Prompt for the next session**. No need for the user to paste anything.

When the session's work is done, update this file: move **Next session** → **Last session summary**, advance **Next session** to the following entry in `sessions.md`, refresh **Open questions**, and rewrite **Prompt for the next session**.

---

## Session execution rules

These apply to every conceptualization session, in addition to the per-session prompt. They exist because the session-split structure assumes one decision is deliberated at a time, in the artifact — not pre-picked in chat and then justified.

1. **The artifact is the deliberation.** Do not announce a position in chat before writing. Do not eliminate options before the doc canvasses them. Land positions only as the doc concludes.
2. **Stay inside the session's scope.** If a justification for the current decision requires reaching into a later session (auth shape, storage choice, lifecycle vocabulary), that is a signal the position is not decidable yet — push back on the session boundary, do not cross it.
3. **Treat prior ADRs as constraints to address, not exclusions to assume.** If a prior ADR appears to eliminate an option, name the tension inside the doc and deliberate it there. Do not dismiss the option in the pre-amble.
4. **Push back, do not pre-empt.** If the framework or session prompt seems wrong, say so before writing. Do not compensate by quietly importing other-session reasoning.

Cross-conversation context: an incident on 2026-04-28 (Session 2 startup) produced these rules. Memory entry `feedback_no_preanswering.md` captures the same ground from the assistant's side; this section is the durable in-repo restatement.

---

## Current phase

**Conceptualization** — sessions are planning-only, no code is written. See `planning/sessions.md` for the full session list.

## Last session summary

**Session 1 — Abstract entity & state framework (2026-04-28).** Wrote `planning/framework.md` with one position per question (entity definition, four-kind state taxonomy, relationship defaults, identity policy). Added ADR-0002 through ADR-0005 capturing the rejected alternatives. Framework is intentionally thin — it commits to vocabulary, not modeling structure, so Session 3 has room to push back when the domain lands. History implementation shape, cross-system identity, soft-delete policy, and concrete lifecycle vocabularies are explicitly deferred (see "Deferred" section in `framework.md`).

## Open questions

- History _implementation_ shape (event store, append-only history tables, temporal tables) — deferred to Session 8 (stack). Session 2 commits the logic-layer semantics; Session 8 picks the storage.
- History patterns menu — the available per-entity history patterns and selection criteria are defined in Session 5, before domain mapping. TBD.
- Cross-system identity (do our UUIDs need to be stable across other agency systems?) — deferred to Session 6 (domain mapping).
- Soft-delete vs. hard-delete policy — likely regulatory; Session 6.
- Concrete lifecycle vocabularies per entity — Session 6, once entities exist.
- Concrete authorization roles and relationships — Session 6. Session 4 picks the shape; the predicates land in Session 6.
- Whether the existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation session.

## Note on session restructures

**2026-04-28:** The original Session 2 ("Logic & invariants") stacked five large decisions into one block. It was split into three sessions to keep each decision deliberate:

- **Session 2** — Transitions & history-semantics (coupled pair, kept together)
- **Session 3** — Lifecycle rules & invariants (coupled pair, kept together)
- **Session 4** — Authorization

Original Sessions 3–6 (Domain mapping → Data model & roadmap) shifted to Sessions 5–8.

**2026-04-29:** Session 5 (History & auditing patterns) added between Session 4 (authorization) and domain mapping. ADR-0003's universal history commitment narrowed by ADR-0006: historical state remains a named kind in the four-kind taxonomy but is now a per-entity decision from a defined menu. Choosing from the menu is required at entity definition time. Original Sessions 5–8 (Domain mapping → Data model & roadmap) shifted to Sessions 6–9.

## Next session

**Session 2 — Transitions & history-semantics.** See `planning/sessions.md` for the full brief (decisions on the table + candidate positions with tradeoffs).

### Prompt for the next session

> Produce the transitions-and-history-semantics section of `planning/logic.md` and ADR entries closing off the two coupled decisions.
>
> Stay abstract — do **not** introduce environmental-monitoring domain terms. Build directly on `framework.md`'s vocabulary (entity, the four kinds of state, relationships, UUID identity). The decisions on the table and the candidate positions with their tradeoffs are pre-canvassed in `planning/sessions.md` under "Session 2."
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
> - Defer the _implementation_ shape (event store vs temporal tables vs append-only history tables) to Session 8 (stack).
> - Do not pre-empt lifecycle rules, invariants, or authorization — those are Sessions 3 and 4.
> - Do not pre-empt the per-entity history-pattern decisions — those are Session 5. Session 2 establishes the framework-level history infrastructure; Session 5 defines the menu of patterns entities choose from.
> - If you would push back on a framework commitment before answering, say so before writing.

## Pointers

- Session plan: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0006)
- Framework (Session 1 output): `planning/framework.md`
- Logic (Sessions 2–4 output, not yet written): `planning/logic.md`
- History patterns (Session 5 output, not yet written): `planning/history-patterns.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
