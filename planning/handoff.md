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

**Step 6a-iii — Use-case stress-test (2026-05-10).** Walked through primary use case ("samples arrive before the WA is issued"). Secondary use case (CPR 5-date workflow) deferred to next session. Three model adjustments surfaced and formalized as ADRs 0020–0022. No structural gaps found — the model handles the pre-WA scenario with adjustments, not workarounds.

**Primary use case: "Samples arrive before the WA is issued"**

Scenario: project exists, field staff collects samples and works hours before the WA is formally issued. The stress test probed Time Entry, Sample Batch, Document derivation, Deliverable lifecycle gating, and reconciliation workflows.

**Key findings and decisions:**

1. **WA pre-issuance lifecycle.** A Project opens with a WA in "not issued" state. The WA can exist with zero codes. The tracker adds expected WA Codes as scope becomes known — either proactively (top-down) or inferred by the system when work is recorded (bottom-up). ADR-0020.

2. **WA Code is project-scoped (ADR-0020).** WA Code references Project, not WA. The WA authorizes codes and sets budgets, but codes persist across WA versions. Rate resolution for time entries comes from EmployeeRole, not WA Code. Sample billing uses the deferred `(subtype, TAT) → rate` lookup. Only the latest WA is relevant for queries.

3. **WA Code carries a lifecycle (ADR-0021).** States established (concrete names deferred to 6b): `expected` (anticipated, WA not yet issued), `issued` (confirmed on issued WA), `pending_RFA` (not on issued WA, RFA needed), `dismissed` (tracker decided code isn't needed). Promoted from no-history to lifecycle capture. Delete policy changed from hard to soft.

4. **Smart commands infer missing structure.** When a tracker records a time entry or sample batch and the WA Code doesn't exist, the system creates the WA Code in `expected` state as part of the same atomic operation. Domain invariant holds (Time Entry requires WA Code, always); the command layer handles inference. This is application-layer orchestration, not a framework change.

5. **Derivation fires on expected codes (ADR-0022).** Document and Deliverable slots appear as soon as a WA Code exists, regardless of authorization status. The system is useful from the moment work begins.

6. **WA issuance reconciliation.** When the formal WA arrives, expected codes are reconciled: matching codes → `issued`; unmatched codes → `pending_RFA` + system auto-creates an unsubmitted RFA entity; codes on the WA that weren't expected → added as `issued`.

7. **Deliverable lifecycle gated by code status (ADR-0022).** Deliverables derived from unissued codes start in `pending_RFA`. They transition to `outstanding` (actionable) when the code reaches `issued`. This transition is a cascading side effect of the code issuance compound command.

8. **Derived vs operational blocking.** Structural blocking (from WA Code authorization status) is automatic and derived. Operational blocking (waiting on contractor, lab results, etc.) is user-initiated via Notes (ADR-0018). Two independent channels, both visible.

9. **Unresolved codes are project blockers.** WA Codes in `pending_RFA` or `dismissed`-pending status surface as derived blockers on the Project. Must be resolved or dismissed before project completion.

**Revised entity roster (15 entities, unchanged count):**

| # | Entity | Notes |
|---|---|---|
| 1 | Project | SCA engagement. |
| 2 | School | = Site for MVP. |
| 3 | WA | Contract document; supersedable via self-reference (ADR-0016, ADR-0017). Pre-issuance lifecycle. |
| 4 | WA Code | Project-scoped line item (ADR-0020). Carries code identifier, description, scope level, budget (from WA authorization), derivation rules. Lifecycle tracks authorization status (ADR-0021). |
| 5 | User | Auth identity (username/password). |
| 6 | Employee | Person doing project work; linked to User via typed reference (0..1 ↔ 0..1). |
| 7 | EmployeeRole | Temporal work-license assignment with `(role_type, rate, start_date, end_date?)`. |
| 8 | UserRole | App-access role with grant/revoke timestamps; drives ADR-0012 authorization predicates. |
| 9 | Time Entry | Billable hours record. Employee + site + date + hours + WA Code reference (mandatory). |
| 10 | Sample Batch | COC group. Carries sample type, TAT, location(s), composition `[{subtype, quantity}]`. WA Code reference (mandatory). |
| 11 | Document | Unified slot+file entity. Set-based derivation (ADR-0015). `document_type` discriminates tracking behavior. `current_assignee` (→ Employee). File upload as intrinsic attribute. Derivation fires on expected codes (ADR-0022). |
| 12 | Deliverable | SCA-portal submission package; bundles Documents (M:M). Derivation fires on expected codes (ADR-0022). Lifecycle gated by WA Code status. |
| 13 | Contractor | On-site abatement (or other) third party. |
| 14 | RFA | Request for Amendment; carries pending WA edits (budget revisions, code add/remove). May be auto-created during WA issuance reconciliation. |
| 15 | Note | Polymorphic commentary; typed reference to any entity. Creator-only edits. Not deletable. |

Values / lookups (not entities): Sample Type, Sample Subtype, Project Type (curated label), TAT options, various status enums.

**Updated per-entity history-pattern assignments:**

| Pattern | Entities |
|---|---|
| Comprehensive capture | Document, WA, RFA |
| Lifecycle capture | Project, Sample Batch, Deliverable, EmployeeRole, UserRole, WA Code |
| Audit log | Employee, User, Time Entry, Contractor |
| No history | School, Note |

**Updated per-entity delete policy:**

| Policy | Entities | Notes |
|---|---|---|
| Soft delete (guarded hard-delete eligible) | Document, WA, RFA, Project, Sample Batch, Deliverable, EmployeeRole, UserRole, Employee, User, Time Entry, Contractor, WA Code | History-carrying or referenced by history records. Hard-delete permitted if no inbound references exist. |
| Hard delete | School, Note | No history, no external history references. |

**Design patterns (updated):**
1. **Temporal rate resolution.** Time Entry → Employee → EmployeeRole-on-date-of-work. Sample billing: Sample Batch → `(subtype, TAT)` → rate-on-date. Rate comes from EmployeeRole / billing rate table, not from WA Code or WA.
2. **Pre-conditional lifecycle gating.** Deliverable submission gated on WA Code `issued` status. Deliverables in `pending_RFA` until code is issued.
3. **Derived blocking status.** Two independent channels: structural (automatic, from WA Code authorization status) and operational (user-initiated, via Notes).
4. **Smart command inference.** Recording work (time entry, sample batch) against a non-existent WA Code creates the code in `expected` state atomically. Domain invariants hold; the command layer infers missing structure.
5. **Compound cascading commands.** WA Code issuance atomically transitions the code and cascades lifecycle transitions to all derived Documents and Deliverables.
6. **WA issuance reconciliation.** Matching expected codes to the formal WA; auto-creating RFAs for unmatched codes; adding unexpected codes as `issued`.

**Vocabulary (carried forward + additions):**
- **Tracker** — the app's user (job title: "project manager"; function: tracking).
- **Coordinator** — office staff who manage work (scheduling, dispatch). Not an app user in MVP.
- **Project** — SCA engagement. The codebase is "the app" or "sca-tracker."
- **School** — = Site for MVP.
- **WA / WA Code** — contract document / project-scoped line item.
- **FAMR** — Final Air Monitoring Report.
- **CPR** — Contractor Package Record; a specific required document type (not a separate entity).
- **TAT** — Turnaround time for sample analysis (24hr, 1hr, 3hr, etc.); property of Sample Batch.
- **COC** — Chain of Custody; the document accompanying a sample batch.

**Additional modeling decisions (carried forward from 6a-ii):**
- **File upload on Document:** intrinsic attribute (storage pointer). Revision history captured by Document's comprehensive history pattern. Can be introduced as a requirement at any point.
- **Document per-type tracking behavior:** `document_type` attribute acts as discriminator selecting applicable lifecycle, tracking fields, and invariants. E.g., CPR (Contractor Package Record) tracks 5 dates with ordering invariants; simple docs have missing → saved lifecycle. Details deferred to 6b.
- **Blocked state:** likely modeled as a flag orthogonal to lifecycle (`is_blocked` + required note), not a lifecycle state — avoids "return to previous state" problem. Details deferred to 6b.
- **Sample Batch refinements:** TAT is per-batch. Location(s) per-batch. Batch composition invariant: PCM/TEM batches require single subtype; Bulk allows mixed subtypes. WA Code reference mandatory.
- **Billing rate lookup:** `(subtype, TAT) → rate` with temporal validity, parallel to EmployeeRole's temporal rate. Whether this is an entity (BillingRate) or a configuration table is deferred.
- **Bulk import:** legacy documents (~300 projects) land in `missing` state without file uploads. File-upload requirement enforced by transition guards. Import-specific relaxation is a 6b/implementation concern.
- **Guarded hard-delete:** soft-delete entities can be hard-deleted if no inbound references exist. Framework-compatible (invariant check on delete command per ADR-0010).
- **Dev-environment cascade delete:** dev pipeline can bypass invariant enforcement for test cleanup. Environment configuration, not a framework decision.

## Open questions

**For Step 6b (next session, opening with deferred CPR walkthrough):**
- Walk through CPR's 5-date workflow to validate the `document_type` discriminator model. Exercises per-type tracking behavior and will inform how lifecycle vocabularies are structured for Document subtypes.
- WA ↔ WA Code authorization relationship: how budget-per-code is tracked across WA versions (the WA authorizes codes and sets budgets, but codes are project-scoped — where do the per-code budget terms live?).
- WA Code `dismissed` semantics: what happens to Time Entries and Sample Batches referencing a dismissed code? Reassigned to another code, or remain as "work done, not billed"?

**Carried forward (deferred to later steps):**
- **Billing Rate entity/table** — temporal `(subtype, TAT) → rate` lookup. Likely Step 6c or 6d.
- **Blocked-as-flag design** — how `is_blocked` flag interacts with lifecycle transitions and gating. Step 6b.
- **Concrete lifecycle vocabularies per entity** — Step 6b.
- **Concrete authorization roles, relationships, and per-command predicates** — Step 6c.
- **Document → Deliverable M:M** — confirmed; formal relationship declaration in Step 6c.
- **Quarantine as a per-entity violation-handling pattern** — excluded from history-pattern menu (ADR-0013); remains deferred per ADR-0011. Step 6d.
- **Bulk import file-upload relaxation** — 6b or implementation.
- **History implementation shape** (event store, append-only tables, temporal tables) — Step 8.
- **Persistence isolation for cross-entity invariants** — Step 8.
- Whether existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

## Next session

**Step 6b — Workflows & lifecycles.** See `planning/steps.md` for the full brief. Open with the CPR 5-date walkthrough deferred from 6a-iii.

### Prompt for the next session

> Map key workflows to command sequences and concrete lifecycle state machines per entity. Build on the entity roster (15 entities), updated history-pattern assignments, updated design patterns, and model adjustments from 6a-iii (ADRs 0020–0022) captured in the last session summary above and in all prior planning artifacts.
>
> **Opening: CPR 5-date walkthrough (deferred from 6a-iii).** Walk through the Contractor Package Record's 5-date workflow to validate the `document_type` discriminator model. This exercises per-type tracking behavior and will inform how Document lifecycle vocabularies are structured. Key questions:
> - What are the 5 dates and their ordering invariants?
> - How does `document_type` select the applicable lifecycle, tracking fields, and invariants?
> - Does the unified Document entity handle type-specific complexity without becoming a god-entity?
>
> **Main scope: concrete lifecycles and commands.** For each entity with a lifecycle:
> - Named state machine (state names + allowed transitions)
> - Named commands per entity type
> - Invariant declarations (intra-entity and cross-entity)
>
> Key entities requiring lifecycle definition: Project, WA (including pre-issuance states), WA Code (expected/issued/pending_RFA/dismissed), Document (per document_type), Deliverable (including pending_RFA gating), Sample Batch, RFA, EmployeeRole, UserRole.
>
> **Process notes:**
> - Stay in casual back-and-forth mode. Self-monitor context window and flag wrap points.
> - The CPR walkthrough may surface adjustments to the `document_type` discriminator model. Handle those before defining Document lifecycles.
> - Compound cascading commands (e.g., WA Code issuance → Deliverable transitions) should be named and their cascade behavior specified.
> - Do not write to `domain-model.md` (that's Step 6d).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6a complete across 6a-i / 6a-ii / 6a-iii)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0022)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
