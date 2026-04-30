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

**Step 2 — Transitions & history-semantics (2026-04-29).** Wrote `planning/logic.md` with the transitions and history-semantics sections. ADR-0007 (commands as transition unit) and ADR-0008 (state-mutating with mandatory history capture for entities declared history-carrying; capture is framework-enforced inside the command pipeline) appended to `decisions.md`. ADR-0006's per-entity history opt-out is honored — capture is mandatory only for entities declared history-carrying; non-history entities just mutate. Audit-log-as-pattern stays alive as a Step 5 menu option (opt-in, with a documented best-effort tradeoff), not the framework default. Coupling between the two decisions made explicit in `logic.md`. STOP-AND-CONFIRM gate revised: recommendations are now welcomed in chat — the gate is on writes (ADRs, planning files), not on opinions.

## Open questions

- History _implementation_ shape (event store, append-only history tables, temporal tables) — Step 8 (stack), informed by Step 5's pattern menu.
- Per-entity history-pattern menu and selection criteria — Step 5, before domain mapping.
- **Reference snapshotting:** when a history-carrying entity references a non-history entity (or another history-carrying one), what does the history record capture so the past reference remains interpretable? Surfaces as a Step 5 concern.
- **History-pattern promotion path:** how does an entity get promoted from "no history" to "history-carrying" mid-life? Backfill is impossible (the past is lost) — only forward-history is achievable. Step 5 should address this explicitly when defining the pattern menu.
- **Exact history-record contents** (full before/after vs. command + payload only vs. deltas) — varies per Step 5 pattern.
- Cross-system identity (do our UUIDs need to be stable across other agency systems?) — Step 6.
- Soft-delete vs. hard-delete policy — likely regulatory; Step 6.
- Concrete lifecycle vocabularies per entity — Step 6, once entities exist.
- Concrete authorization roles and relationships — Step 6. Step 4 picks the shape; the predicates land in Step 6.
- Whether the existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

## Next session

**Step 3 — Lifecycle rules & invariants.** See `planning/steps.md` for the full brief (decisions on the table + candidate positions with tradeoffs).

### Prompt for the next session

> Produce the lifecycle-and-invariants section of `planning/logic.md` (append) and ADR entries closing off the three coupled decisions.
>
> Stay abstract — do **not** introduce environmental-monitoring domain terms. Build directly on `framework.md` (lifecycle status as its own state kind) and `logic.md`'s transitions section (commands as the unit of change; rules attach to commands). The decisions on the table and the candidate positions with their tradeoffs are pre-canvassed in `planning/steps.md` under "Step 3."
>
> Three decisions to close (coupled — lifecycle rules are temporal invariants, splitting them invites duplicated reasoning):
>
> 1. **Lifecycle specification.** Declarative state machine per entity type, guards as command preconditions, or imperative handlers?
> 2. **Invariant declaration & enforcement layer.** On entities, on commands, on read schemas? Write-path only, read-path only, or both?
> 3. **Violation handling.** Reject, error-with-allow, warn, quarantine?
>
> Constraints:
>
> - One position per decision. Rejected alternatives go in ADR entries (one ADR per decision).
> - Lifecycle rules attach to commands (per ADR-0007) — work with that surface, do not relitigate it. If you find a tension, name it inside the doc and deliberate it there (per `sessions.md` rule 3).
> - Do not pre-empt authorization (Step 4) or per-entity history-pattern decisions (Step 5).
> - Concrete lifecycle vocabularies per entity (`draft → active → archived`, etc.) are deferred to Step 6 — Step 3 picks the *shape* of lifecycle specification, not the contents.
> - If you would push back on a framework or `logic.md` commitment before answering, say so before writing.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0008)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; Step 2 sections written, Steps 3–4 to append): `planning/logic.md`
- History patterns (Step 5 output, not yet written): `planning/history-patterns.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
