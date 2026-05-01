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

**Step 4 — Authorization (2026-05-01).** Appended the authorization section to `planning/logic.md` (sub-sections for predicate shape, declaration site, form, pipeline position, deferred concrete predicates) plus a coupling section showing how authorization, lifecycle, and invariants form a unified declarative pipeline. ADR-0012 (authorization predicates are declarative expressions over (caller, command, target), declared per command, evaluated first in the pipeline) appended to `decisions.md`. Three coupled sub-questions closed in one ADR: primary axis is predicate over (caller, command, target) — subsumes RBAC and ReBAC without committing to either; declaration site is on commands — differs from invariants because authorization is inherently per-command; form is declarative — consistent with lifecycle and invariants. Pipeline evaluation order now defined: authorization → lifecycle → apply → invariants → commit.

## Open questions

- Per-entity history-pattern menu and selection criteria — Step 5, before domain mapping.
- **Reference snapshotting:** when a history-carrying entity references a non-history entity (or another history-carrying one), what does the history record capture so the past reference remains interpretable? Surfaces as a Step 5 concern.
- **History-pattern promotion path:** how does an entity get promoted from "no history" to "history-carrying" mid-life? Backfill is impossible (the past is lost) — only forward-history is achievable. Step 5 should address this explicitly when defining the pattern menu.
- **Exact history-record contents** (full before/after vs. command + payload only vs. deltas) — varies per Step 5 pattern.
- **Quarantine as a per-entity violation-handling pattern** — whether to commission it (and on what criteria); ADR-0011 hedges between Step 5 and a later step.
- Cross-system identity (do our UUIDs need to be stable across other agency systems?) — Step 6.
- Soft-delete vs. hard-delete policy — likely regulatory; Step 6.
- Concrete lifecycle vocabularies per entity — Step 6, once entities exist.
- Concrete authorization roles, relationships, and per-command predicates — Step 6. ADR-0012 picks the shape; the contents land in Step 6.
- History _implementation_ shape (event store, append-only history tables, temporal tables) — Step 8 (stack), informed by Step 5's pattern menu.
- **Persistence isolation for cross-entity invariants** — what guarantee the persistence layer must provide so the command-pipeline invariant check is meaningful under concurrency (serializable transactions, optimistic locking, advisory locks, etc.). Step 8.
- Whether the existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

## Next session

**Step 5 — History & auditing patterns.** See `planning/steps.md` for the full brief.

### Prompt for the next session

> Produce `planning/history-patterns.md` and a single ADR recording the pattern set and selection criteria.
>
> Stay abstract — do **not** introduce environmental-monitoring domain terms. Build on `framework.md` (four-kind state taxonomy, per-entity history decision at definition time), `logic.md` (commands as unit of change, mandatory capture for history-carrying entities via the command pipeline, authorization/lifecycle/invariant pipeline), and the existing ADRs — especially ADR-0006 (per-entity history decision from a defined menu), ADR-0008 (state-mutating with mandatory capture; bolted-on audit log preserved as an opt-in pattern).
>
> Deliverables:
>
> 1. **`planning/history-patterns.md`** — the menu of available history patterns. For each pattern: what it captures, what it commits to structurally, what it gives up, and a prototype example (abstract, not domain-specific) of an entity that would use it. "No history" must be an explicit option. At least two substantively different history-carrying options.
> 2. **Selection criteria** — documented in the same file. How to choose between patterns given an entity's characteristics.
> 3. **One ADR** recording the pattern set and selection criteria.
>
> Open questions to address:
>
> - **Reference snapshotting:** when a history-carrying entity references another entity, what does the history record capture so the past reference remains interpretable?
> - **History-pattern promotion path:** how does an entity move from "no history" to "history-carrying" mid-life? Backfill is impossible — only forward-history is achievable.
> - **Exact history-record contents** — what each pattern captures (full before/after, command + payload only, deltas) should vary per pattern.
> - **Quarantine as a per-entity pattern** — whether to include it in the pattern menu (per ADR-0011's deferral).
>
> Constraints:
>
> - One ADR for the pattern set. Include selection criteria in the ADR's consequences.
> - Every entity defined in Step 6 must choose from this menu — design the menu with that forcing function in mind.
> - Do not commit to implementation shape (event store / temporal tables / append-only) — that's Step 8.
> - Audit-log-as-pattern is already preserved as an option per ADR-0008 — include it in the menu if warranted, with its documented tradeoff.
> - If you would push back on a framework or `logic.md` commitment before answering, say so before writing.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0012)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output, not yet written): `planning/history-patterns.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
