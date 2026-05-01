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

**Step 6 — Domain mapping, opening discussion (2026-05-01).** Collected domain context and determined Step 6 does not fit one session. Split into four sub-sessions (6a–6d). Domain context gathered:

- **Agency scope:** Air quality, water quality, site remediation.
- **Project structure:** Two layers — (1) project goals/requirements defined by contract (e.g., air monitoring at a school during asbestos abatement; expected deliverables include final report, samples with results, other documents), and (2) emergent state of the actual project (work scheduled, monitors assigned, inspections happen, samples collected, lab results received, documents prepared).
- **Scope extension:** Projects can extend mid-flight (e.g., asbestos discovered in a second location → more samples, different monitor, additional documents and requirements added to scope).
- **Irreconcilable errors:** Chain-of-custody mismatches between lab samples and monitor activity logs can invalidate samples; a manager must explicitly dismiss such errors before marking the project complete. (Maps to the cross-entity acknowledgement gating pattern in `logic.md`.)
- **Core tracked things:** Projects, inspections (time entries for employees), required documents (files to prepare or save), deliverables (one or many required documents to upload for approval), work authorizations (contracts defining scope and location of work).
- **Users:** Project managers only for initial design; field staff deferred to post-MVP.
- **Deferred to sub-sessions:** Key workflows (item 3 → Step 6b), relationships (item 5 → Step 6c).

## Open questions

- Cross-system identity (do our UUIDs need to be stable across other agency systems?) — Step 6a.
- Soft-delete vs. hard-delete policy — likely regulatory; Step 6a.
- Concrete lifecycle vocabularies per entity — Step 6b.
- Concrete authorization roles, relationships, and per-command predicates — Step 6c.
- **Quarantine as a per-entity violation-handling pattern** — excluded from the history-pattern menu (ADR-0013); remains deferred per ADR-0011. The chain-of-custody error pattern described in domain context may inform this. Step 6d.
- History _implementation_ shape (event store, append-only history tables, temporal tables) — Step 8 (stack), informed by Step 5's pattern menu (now written).
- **Persistence isolation for cross-entity invariants** — what guarantee the persistence layer must provide so the command-pipeline invariant check is meaningful under concurrency (serializable transactions, optimistic locking, advisory locks, etc.). Step 8.
- Whether the existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

## Next session

**Step 6a — Entity identification.** See `planning/steps.md` for the full brief.

### Prompt for the next session

> Identify the domain entities, their intrinsic attributes, and their history-pattern assignments. Build on the domain context captured in the last session summary above and on all prior planning artifacts.
>
> Starting entity list from domain context: projects, inspections (time entries), required documents, deliverables, work authorizations. Evaluate each against `framework.md`'s entity test. Identify any additional entities implied by the domain context (e.g., sites/locations, monitors/staff, samples, lab results).
>
> For each entity:
> - Name and one-line description (what it is)
> - Intrinsic attributes (the facts the entity carries by being itself)
> - History pattern from `history-patterns.md` with a one-line justification using the selection criteria
>
> Open questions to address in this session:
> - **Cross-system identity:** do our UUIDs need to be stable across other agency systems, or are external IDs just intrinsic attributes?
> - **Soft-delete vs. hard-delete policy:** likely regulatory — what does the domain require?
>
> Do not address lifecycles (Step 6b), relationships (Step 6c), or write `domain-model.md` (Step 6d).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6 now split into 6a–6d)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0013)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
