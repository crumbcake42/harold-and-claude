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

**Step 6a-i — Entity roster + scoping policies (2026-05-01).** Established the candidate entity roster, resolved the two scoping policies, and surfaced major modeling decisions. Step 6a's full scope did not fit one session; partitioned into 6a-i (this session) / 6a-ii (history-pattern walk + opens) / 6a-iii (use-case stress-test). See `steps.md` for the partition.

**Process change:** User adopted casual back-and-forth deliberation for entity work (memory `feedback_casual_deliberation`); use-case-driven discovery over enumerated forks-and-tables. Agent self-monitors context and flags wrap points.

**Phase 1 — scoping policies (closed):**
- **Cross-system identity** — deferred indefinitely. No external-ID attributes this iteration. Post-MVP, BQE integration would add `bqe_id`-style intrinsic attributes (per ADR-0005) on relevant entities + a manager-driven drift-reconciliation facility. No new ADR — the position aligns with `framework.md`'s existing "deferred" stance.
- **Soft-delete / guarded-delete** — no new `can_delete` mechanism. Deletion follows the standard command pipeline (auth + lifecycle + invariants per ADRs 0009/0010/0012). The COC-mismatch / orphan scenario is handled by `logic.md`'s cross-entity acknowledgement gating (e.g., `close_project` is gated on samples having reached an acknowledged terminal state). Per-entity soft-vs-hard delete is a per-entity decision deferred to 6a-ii (likely follows history pattern).

**Phase 2 — entity roster (provisional, ~17 entities):**

| # | Entity | Notes |
|---|---|---|
| 1 | Project | SCA engagement. |
| 2 | School | = Site for MVP. |
| 3 | WA | Contract document; supersedable via approved RFA → Amendment WA. |
| 4 | WA Code | Line item; project- or building-level; carries rate, budget, derivation rules. |
| 5 | User | Auth identity (username/password). |
| 6 | Employee | Person doing project work; linked to User via typed reference (0..1 ↔ 0..1). |
| 7 | EmployeeRole | Temporal work-license assignment with `(role_type, rate, start_date, end_date?)`. |
| 8 | UserRole | App-access role with grant/revoke timestamps; drives ADR-0012 authorization predicates. |
| 9 | Inspection | Field-visit event. |
| 10 | Daily Log | Narrative report from a day's work. |
| 11 | Time Entry | Billable hours record. |
| 12 | Sample Batch | Group taken+analyzed together. |
| 13 | Sample | Individual within a batch; carries COC trail. |
| 14 | Document | **Unified slot+file entity. Set-based derivation. Lifecycle includes `pending_rfa`/`outstanding`/`in_preparation`/`in_review`/`in_revision`/`ready`/`submitted`/`approved`/`rejected`/`not_required`.** |
| 15 | Deliverable | SCA-portal submission package; bundles a subset of Documents. |
| 16 | Contractor | On-site abatement (or other) third party. |
| 17 | RFA | Request for Amendment; carries pending WA edits (budget revisions, code add/remove). |

Values / lookups (not entities): Sample Type, Sample Subtype, Project Type (curated label, intrinsic-soft-state, no framework cascade), various status enums.

**Major modeling decisions surfaced this session:**
- **Document and RequiredDocument unified into one entity (Document).** The slot/spec and the file are two stages of the same identity. Document's lifecycle subsumes the slot/file distinction. Reduces entity count and simplifies set-based derivation semantics.
- **Set-based document derivation.** A Document's existence and "required" status is governed by a derivation set — the collection of sources that imply it's needed (WA Codes, project events). WA Code add/remove deltas the derivation set. Document persists as long as derivation set is non-empty; transitions to `not_required` (with history preserved for audit) when set becomes empty. **Documents are not owned by WA Codes — many-to-many through the derivation set.**
- **WA versioning via supersession.** Approved RFA produces an Amendment WA that supersedes the Initial WA; full version chain preserved. Mechanism (self-reference vs. separate Version entity) confirmed in 6a-ii. Derivation-set delta is applied at Amendment WA issuance (not at RFA submission).
- **EmployeeRole and UserRole are separate temporal entities.** EmployeeRole carries billing rate; UserRole carries access permissions. Different vocabularies, different consumers. Both are temporal (start/end dates).
- **Project Type is intrinsic-soft-state.** Curated lookup vocabulary (avoids free-text drift). Manually maintained by Tracker. No framework cascade. Drift detection ("label says Monitor and Survey but no monitoring codes present") is a deferred soft-surface feature.
- **EmployeeRole is a temporal entity.** Rate-on-date-of-work governs billing for Time Entries (temporal join — see design-pattern note below).
- **Sample model is four-layered:** Sample Batch (entity), Sample (entity), Sample Type (value), Sample Subtype (value).
- **Inspection / Daily Log / Time Entry are three separate entities.** (Reverses an earlier merge proposal.)

**Design patterns named for later formalization:**
1. **Temporal rate resolution.** Time Entry → Employee → EmployeeRole-on-date-of-work. Rate is a property of the historical role assignment, not of the Employee.
2. **Pre-conditional lifecycle gating.** A Deliverable's `submit` transition is gated on the parent WA having the relevant WA Code(s). Same family as `logic.md`'s cross-entity acknowledgement gating; trigger is "the contract supports this submission" rather than "all related entities terminal-acknowledged."
3. **Derived blocking status.** Documents (and Deliverables) expose a derived status that aggregates own state + dependency state — e.g., a Document can be `prepared` intrinsically but `blocked from submission` derivatively because of WA/RFA situation. Maps cleanly to `framework.md`'s derived-state kind.

**Vocabulary adopted this session (carried forward):**
- **Tracker** — the app's user (job title at office is "project manager"; function is tracking, not work-management).
- **Coordinator** — office staff who actually manage work (scheduling, dispatch). Not an app user in MVP.
- **Project** — SCA engagement (the domain entity). The codebase is referred to as "the app" or "sca-tracker."
- **School** — = Site for MVP.
- **WA / WA Code** — contract document / line item.
- **FAMR** — Final Air Monitoring Report.

**History patterns assigned this session:**
- **Document** = comprehensive capture (audit case for blocking issues, responsibility shifts, derivation-set churn).
- **Sample** = at least lifecycle capture, implied by COC/acknowledgement scenario; confirm in 6a-ii.
- All other entities pending in 6a-ii.

## Open questions

**For Step 6a-ii (next session):**
- **Q6 — Final Project Package:** derived state (project's "ready to close" computed from Document/Deliverable state + final invoice Document) vs. entity (a `FinalSubmission` with its own lifecycle). User described what it *is* (internal packet of all required docs + final invoice) but didn't pick a/b. Agent leans (a).
- **Document responsibility/notes structure:** intrinsic attributes (`current_assignee`, `blocker_note`) vs. separate Note entity attached to Documents. Audit case ("employee A hasn't prepared this in months — left a note that contractor is holding it up") motivates capturing both.
- **WA versioning mechanism:** `supersedes` self-reference on WA vs. separate WA Version entity.
- **Document → Deliverable cardinality:** many-to-many (a Document can be in multiple Deliverables) vs. many-to-one (a Document belongs to at most one Deliverable).
- **LabResult disposition:** separate entity vs. intrinsic state on Sample (parked from Phase 2). Worth a fresh look given Sample Batch is now an entity.
- **Per-entity history-pattern walk** (~17 entities, required by ADR-0006 before Step 6b can begin).
- **Per-entity soft/hard delete confirmations** (likely follow from history-pattern choices).

**For Step 6a-iii (after 6a-ii):**
- Use-case stress-test of the entity model + set-based derivation + acknowledgement gating. Default candidate use case: "Samples arrive before the WA is issued."

**Carried forward (deferred to later steps):**
- Concrete lifecycle vocabularies per entity — Step 6b.
- Concrete authorization roles, relationships, and per-command predicates — Step 6c.
- **Quarantine as a per-entity violation-handling pattern** — excluded from the history-pattern menu (ADR-0013); remains deferred per ADR-0011. The COC scenario may inform this. Step 6d.
- History _implementation_ shape (event store, append-only history tables, temporal tables) — Step 8.
- **Persistence isolation for cross-entity invariants** — Step 8.
- Whether existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

**Candidate ADRs noted but not written this session** (user to decide whether to formalize at start of 6a-ii):
- "Documents derive from a set of sources, not from 1:1 ownership; existence is governed by derivation-set non-emptiness."
- "WA is supersedable via approved RFA; full version chain preserved."
- "Document and RequiredDocument unified into one entity with a slot-spanning lifecycle."

## Next session

**Step 6a-ii — History-pattern walk + remaining open modeling questions.** See `planning/steps.md` for the full brief.

### Prompt for the next session

> Complete Step 6a by (1) resolving the open modeling questions surfaced in 6a-i and (2) walking each entity in the roster for its history-pattern assignment per ADR-0006. Build on the entity roster, modeling decisions, and design-pattern names captured in the last session summary above and in all prior planning artifacts.
>
> **Open modeling questions to resolve (in roughly this order):**
> 1. Final Project Package — derived state vs entity (Q6)
> 2. Document responsibility/notes structure — intrinsic attributes vs separate Note entity
> 3. WA versioning mechanism — supersedes self-reference vs separate WA Version entity
> 4. Document → Deliverable cardinality — many-to-many vs many-to-one
> 5. LabResult — separate entity vs intrinsic state on Sample
>
> **Per-entity history-pattern walk:**
> - Already assigned: Document = comprehensive capture
> - Implied (confirm): Sample = at least lifecycle capture
> - Pending (assign one of {no history | audit log | comprehensive capture | lifecycle capture} per entity, with a one-line justification): Project, School, WA, WA Code, User, Employee, EmployeeRole, UserRole, Inspection, Daily Log, Time Entry, Sample Batch, Deliverable, Contractor, RFA
>
> **Per-entity soft/hard delete:** confirm per entity (likely follows from history pattern).
>
> **Process notes:**
> - Stay in casual back-and-forth mode (per `feedback_casual_deliberation` memory). Self-monitor context window and flag wrap points.
> - Do not write to `domain-model.md` (that's Step 6d).
> - At the start of the session, ask whether to formalize the candidate ADRs listed in the prior session's open questions before proceeding.
> - Do not address Step 6b (lifecycles) or Step 6c (relationships/authorization).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6a now split across 6a-i / 6a-ii / 6a-iii)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0013; no new ADRs from 6a-i)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
