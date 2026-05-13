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

**Step 6b (continued, session 7) — Time Entry off-site intervals (ADR-0034), EmployeeRole shape (ADR-0035), and UserRole atemporal form (ADR-0036) all landed (2026-05-12).** Three substantial ADRs written; full session 7 scope complete. ADR-0034 was the carry-over from session 6; ADR-0035 and ADR-0036 close out the EmployeeRole/UserRole question. Session 8 picks up Project lifecycle on a clean slate.

**Major outputs:**

1. **Time Entry off-site intervals (ADR-0034).** Time Entry replaces scalar `hours` with `on_site_range: (start_time, end_time)` + `off_site_sub_intervals: [(start_time, end_time)]`. Sub-intervals required ⊆ on-site range, pairwise disjoint, positive duration. Net on-site time = on-site range minus union of sub-intervals.
   - **No `reason` field, no `drop_off_time` field for MVP.** Only operational off-site reason today is lab delivery (implicit); manual COC cross-check handles drop-off verification. Both deferred per MVP-scope-philosophy memory (additive migrations with deterministic backfill if/when new off-site categories arise).
   - **Dual-predicate semantics over the structure, pinned in this ADR.**
     - *Cross-project overlap (ADR-0028 amendment):* uses **gross** on-site range. Off-site sub-intervals are project-committed time; don't free the employee for another project's billing.
     - *Blocker #9 (sample collection coverage, ADR-0032 registry entry):* uses **net** on-site time. Sample collection requires physical presence at the school; off-site sub-intervals are physical absences.
     - Project commitment ≠ physical presence. Future Time Entry predicates pick the slice that matches their question and cite this ADR.
   - **Day-of representation canonical example (in ADR).** A workday with a Project A → Project B → Project A pattern is encoded as three separate Time Entries; off-site sub-intervals capture within-project diversions (lab runs), not cross-project work.
   - **Amendments:** ADR-0028 (overlap predicate now structural on gross range); ADR-0032 registry entry #9 (predicate now structural on net on-site time).
   - **Initial recommendation correction.** The session-6-staged recommendation of *net* time for the cross-project overlap predicate was wrong — surfaced when the user clarified how a midday Project B side-stop is actually entered (split A entries + standalone B entry). The dual-predicate framing is the corrected position.

2. **EmployeeRole shape (ADR-0035).** Schema: `(employee_id, role_type, rate, start_date, end_date?)`. Full-day range semantics — `[start_date, end_date]` closed-closed at calendar-day resolution; end_date is the last valid day. `end_date` nullable for open-ended.
   - **Time Entry → EmployeeRole:** mandatory FK to a specific row; rate read transitively. Boundary invariant: `time_entry.date ∈ [employee_role.start_date, employee_role.end_date ?? +∞]`, enforced on `create_time_entry` and `edit_time_entry`.
   - **Rate-change pattern:** end-date current row at day D, create new row starting D+1 with new rate. Two operations atomic; `change_employee_role_rate` compound command candidate deferred to workflow-consolidation step.
   - **Disjoint-ranges-per-(employee, role_type) invariant.** Within a `(employee_id, role_type)` pair, date ranges must be pairwise disjoint. Different role types may overlap freely (Alice as TechRole + ProjectLead simultaneously is fine).
   - **No state machine.** Temporal validity is the only state, computed from the date range. Lifecycle capture (already assigned) records grant/close/edit events.
   - **Temporal rate resolution design pattern (#1) — formalized structurally.** FK + boundary invariant. Future temporal-value-lookup entities (e.g., billing rate per `(subtype, TAT)`) follow the same shape: temporal record + FK from consumer + boundary invariant at write.
   - **Future grants, retroactive grants, future-effective closes** all admitted by schema; disjoint-ranges invariant constrains them all uniformly.
   - **`close_employee_role(role, end_date)` command** sets end_date; rejects if any Time Entry exists for that role with `date > end_date` (would orphan referenced entries).

3. **UserRole atemporal current-state form (ADR-0036).** Schema: `(user_id, role_type)` composite primary key. No timestamps, no state, no temporal range. Grant creates row; revoke hard-deletes row; re-grant creates fresh row.
   - **Audit on User's audit log** (User's pre-assigned history pattern). Two event types: `grant_user_role`, `revoke_user_role`, each carrying `(user_id, role_type, actor, timestamp, reason?)`. Cross-time history of UserRole activity lives here, not on UserRole itself.
   - **"Created in error" cases** modeled as a revoke with `reason: 'created_in_error'`. No separate soft-delete pipeline.
   - **History-pattern amendment.** UserRole moves from lifecycle capture → **no history** (joins School and Note).
   - **Delete-policy amendment.** UserRole moves from soft-delete → **hard delete** (joins School and Note). No incoming references; revoke is the operational deletion path.
   - **No state machine, no temporal validity computation.** Authorization checks query the current set: `SELECT role_type FROM user_role WHERE user_id = ?`. No filter clauses.
   - **Carry-forwards.** Concrete role catalog + per-command authorization predicates remain Step 6c (ADR-0012 carry-forward). `reason` field shape (free-text vs enum) also Step 6c.

**Cumulative tables below reflect ADR-locked state through ADR-0036.**

**Per-`document_type` assignments (cumulative):**

| Pattern | document_types |
|---|---|
| Simple `missing → saved` | ACP13, ACP7, ACP15, ACP21, Emergency Notification, ACP8, VAR9 (all DepFiling docs — issued externally); COC; Daily Log |
| Cycling-family | CPR (RFA/RFP fork, 5 dates), FAMR (single-step review) |
| Bespoke | Lab Report (3 states: `missing`, `saved`, `invalid`; 4 transitions including `saved → invalid` for tracker-discovered errors and `invalid → saved` for amended reports) |

**Entity roster (16 entities):**

| # | Entity | Notes |
|---|---|---|
| 1 | Project | SCA engagement. |
| 2 | School | = Site for MVP. |
| 3 | WA | Contract document; supersedable via self-reference (ADR-0016, ADR-0017). States: `pending` / `issued` / `superseded` (ADR-0030). |
| 4 | WA Code | Project-scoped line item (ADR-0020). States: `expected` / `pending_rfa` / `rfa_in_review` / `issued` / `budget_rfa_needed` (deferred) / `dismissed` (ADR-0027). |
| 5 | User | Auth identity (username/password). |
| 6 | Employee | Person doing project work; linked to User via typed reference (0..1 ↔ 0..1). |
| 7 | EmployeeRole | Temporal work-license assignment: `(employee_id, role_type, rate, start_date, end_date?)` (ADR-0035). Full-day closed-closed range. Disjoint-ranges-per-`(employee, role_type)` invariant. Referenced by Time Entry; rate read transitively. |
| 8 | UserRole | App-access role: `(user_id, role_type)` composite key (ADR-0036). No timestamps, no state. Grant creates row; revoke hard-deletes; audit on User's log. Drives ADR-0012 authorization predicates. |
| 9 | Time Entry | Billable time record. Employee + site (school) + date + WA Code reference (mandatory) + EmployeeRole reference (mandatory) + `on_site_range: (start_time, end_time)` + `off_site_sub_intervals: [(start_time, end_time)]` (ADR-0034). Sub-intervals ⊆ on-site range, pairwise disjoint. Rate read transitively from EmployeeRole. |
| 10 | Sample Batch | COC group. Carries sample type, TAT, location(s), composition `[{subtype, quantity}]`. WA Code reference (mandatory, nullable via dismiss cascade only). States: `received` / `billed` (ADR-0033). Document-derivation source (COC + Lab Report). |
| 11 | Document | Unified slot+file entity. Per-`document_type` lifecycle dispatch (ADR-0024). Derivation set spans WA Codes, DepFilings, project events. Derivation fires on expected codes (ADR-0022). |
| 12 | Deliverable | SCA-portal submission package; bundles Documents (M:M). States: `pending_rfa` / `outstanding` / `under_review` / `approved` (ADR-0029). `wasted` derived flag. |
| 13 | Contractor | On-site abatement (or other) third party. |
| 14 | RFA | Request for Amendment; carries pending WA edits. May be auto-created during WA issuance reconciliation. |
| 15 | Note | Polymorphic commentary; typed reference to any entity. Subtypes `regular | blocker | resolution` (ADR-0032). `authorship_class: 'user' | 'system'` + nullable `created_by`. Inter-Note `references` field. Regular user Notes are creator-editable per ADR-0018; blocker and resolution Notes are immutable. Not deletable. |
| 16 | DepFiling | TRU-numbered regulatory filing bundle (ADR-0023). Project-scoped; editable `required_doc_types` set; Document-derivation source. No lifecycle. |

Values / lookups (not entities): Sample Type, Sample Subtype, Project Type, TAT options, status enums, `document_type` registry, DepFiling template constants.

**Per-entity history-pattern assignments:**

| Pattern | Entities |
|---|---|
| Comprehensive capture | Document, WA, RFA |
| Lifecycle capture | Project, Sample Batch, Deliverable, EmployeeRole, WA Code |
| Audit log | Employee, User, Time Entry, Contractor, DepFiling |
| No history | School, Note, UserRole |

**Per-entity delete policy:**

| Policy | Entities | Notes |
|---|---|---|
| Soft delete (guarded hard-delete eligible) | Document, WA, RFA, Project, Sample Batch, Deliverable, EmployeeRole, Employee, User, Time Entry, Contractor, WA Code, DepFiling | History-carrying or referenced by history records. |
| Hard delete | School, Note, UserRole | No history, no external history references. |

**Design patterns (cumulative):**
1. Temporal rate resolution. *Formalized structurally in ADR-0035: temporal record carrying value + FK from consumer + boundary invariant at write. Template for future temporal-value-lookup patterns.*
2. Pre-conditional lifecycle gating.
3. Derived blocking status.
4. Smart command inference.
5. Compound cascading commands.
6. WA issuance reconciliation.
7. Parameterized cycling state machine.
8. Set-based derivation extended.
9. **Delete-or-dismiss gate.** Entities with no external references hard-delete; entities with references use the dismiss cascade. Gate: check for references before choosing path.
10. **Derived wasted flag.** A finalized or submitted entity retroactively invalidated by a downstream action is flagged rather than mutated. Flag is derived; entity retains its last persisted state.
11. **Blocker-as-Note with lazy materialization.** System-derived blockers stay derived (registry scan) until a tracker engages (comment or dismissal). First engagement materializes a blocker Note (system-authored) with `surfaced_at` backfilled from entity history. Dismissable vs fix-only classification per registry. Cross-project blockers materialize as paired Notes linked via `paired_blocker_ref`. (ADR-0032)
12. **Chain-dismissal.** When dismissing one blocker structurally causes another's condition to fire, the secondary materializes as already-dismissed atomically; the secondary's resolution Note `references` the primary dismissal Note. (ADR-0032; first concrete instance in ADR-0033 for blocker #9 → #2.)

**Vocabulary (cumulative):**
- **Tracker** — the app's user (job title: "project manager"; function: tracking).
- **Coordinator** — office staff who manage work. Not an app user in MVP.
- **Project / School / WA / WA Code** — as before. School = site = building for MVP. Sample collection codes are school-scoped (e.g., "asbestos sampling at school A"); a WA may authorize work across multiple schools and carry multiple sample-collection codes (one per `(sample_type, school)`).
- **FAMR** — Final Air Monitoring Report. Cycling-family doc with single-step review.
- **CPR** — Contractor Package Record. Cycling-family doc with 2 buckets (RFA, RFP), 5 tracking dates.
- **TAT** — Turnaround time for sample analysis.
- **COC** — Chain of Custody. Simple `missing → saved` per ADR-0024 menu. Derived from Sample Batch (ADR-0033); created in `saved` state at batch creation.
- **Lab Report** — Bespoke 3-state document type (`missing`, `saved`, `invalid`) per ADR-0033. Derived from Sample Batch; created in `missing` state.
- **DepFiling** — Regulatory filing bundle, TRU-numbered. New entity (ADR-0023).
- **TRU** — Unique identifier the regulator assigns to a DepFiling. Natural key on DepFiling.
- **ACP / VAR** — Document-type prefixes for regulatory forms (ACP13, ACP7, ACP15, ACP21, ACP8, VAR9, etc.). All simple `missing → saved`.
- **Wasted** — derived flag on Deliverable: WA Code dismissed after documents prepared or submission attempted. Entity stays in current state; flag signals retroactive invalidity.
- **Limbo chain** — WA `pending` → WA Code `expected` → Deliverable `pending_rfa`. Resolves atomically when `issue_wa` fires.
- **Blocker** — A structural condition (registry entry from ADR-0032) or user-flagged Note declaring something is held up. Dismissable (real-world acceptance path exists) or fix-only (logical impossibility, must be resolved).
- **Materialized blocker** — A blocker that exists as a persisted Note record (vs purely-derived, registry-only). System-derived blockers materialize on first user engagement.
- **Engagement** — A tracker writing a comment about a blocker or dismissing it. The trigger for lazy materialization of system-derived blockers.
- **Chain-dismissal** — When dismissing one blocker structurally causes another's condition to fire, the secondary is materialized as already-dismissed atomically. Linked via the resolution Note's `references` field.
- **On-site range / off-site sub-interval (Time Entry)** — `on_site_range` is the parent range of an entry; `off_site_sub_intervals` are project-committed time-away spans within the on-site range (currently always lab delivery). Sub-intervals are pairwise disjoint, entirely within on-site range, positive-duration. (ADR-0034)
- **Gross on-site range** — the full `on_site_range` of a Time Entry, inclusive of off-site sub-intervals. Represents *project commitment*. Used by the cross-project overlap predicate (ADR-0028 amendment).
- **Net on-site time** — `on_site_range` minus the union of off-site sub-intervals. Represents *physical presence at the parent project's site*. Used by blocker #9 (sample collection coverage).

## Open questions

**For session 8 — immediate:**
- **Project lifecycle ADR.** Substantial; the main work of session 8. Closure invariants span: no fix-only blockers + every dismissable blocker resolved (per ADR-0032 closure gate text). DepFiling completeness, WA Code states (no open RFAs), Daily Log coverage, Deliverable status, cross-project time conflicts, non-billable records — all flow through the registry now. State machine to be defined; candidate states include something like `active`, `closing`, `closed`, `cancelled`. Cancellation handling for open drafts and `in_review` RFAs (deferred from ADR-0031) lands here. Open `pending` WAs with no work referenced — hard-delete per ADR-0031's consequences. The `close_project` and `cancel_project` commands write against the registry-derived gate, not a re-stated invariant list.

**Carry-forwards worth re-checking when relevant:**
- **Billing finalization flow** (the `received → billed` Sample Batch trigger from ADR-0033): specific command and authorization at billing-design step.
- **Cross-project Sample Batch reassignment as a structured command**: in `post-mvp.md` alongside notifications.
- **`change_employee_role_rate` compound command** (candidate from ADR-0035): full spec deferred to workflow-consolidation step.
- **Retroactive rate corrections via Time-Entry rate snapshot** (carry-forward from ADR-0035): reversible additive change post-MVP if signal emerges.
- **`reason` field shape on UserRole grant/revoke audit events** (free-text vs enum vs both): deferred to Step 6c alongside concrete role catalog.
- **Security-immediate revoke runtime semantics** (session invalidation on `revoke_user_role`): implementation concern, deferred to auth implementation step.

**Carried forward (deferred to later steps):**
- **WA ↔ WA Code budget tracking implementation** — Option B direction confirmed; design deferred until budget tracking is in scope.
- **Billing Rate entity/table** — temporal `(subtype, TAT) → rate` lookup. Likely Step 6c or 6d. Follows the temporal rate resolution template formalized in ADR-0035.
- **Concrete authorization roles, relationships, and per-command predicates** — Step 6c. ADR-0036 establishes UserRole as the substrate; the role catalog and per-command predicates are Step 6c's work.
- **Document → Deliverable M:M** — confirmed; formal relationship declaration in Step 6c.
- **Quarantine as a per-entity violation-handling pattern** — excluded from history-pattern menu (ADR-0013); remains deferred per ADR-0011. Step 6d.
- **Bulk import file-upload relaxation** — 6b or implementation.
- **Project structure for managing N `document_types`** — defer to implementation phase.
- **History implementation shape** (event store, append-only tables, temporal tables) — Step 8.
- **Persistence isolation for cross-entity invariants** — Step 8.
- Whether existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

## Next session

**Step 6b (continued, session 8) — Project lifecycle ADR.** See `planning/steps.md` for the full step brief. Substantial — the closure-gate text from ADR-0032 is the canonical predicate; this session writes the state machine, `close_project` / `cancel_project` commands, and resolves cancellation handling for open drafts/`in_review` RFAs (deferred from ADR-0031).

### Prompt for the next session

> Resume Step 6b. Session 7 landed ADR-0034 (Time Entry off-site intervals + dual-predicate overlap semantics), ADR-0035 (EmployeeRole shape + Time Entry FK invariant + disjoint-ranges-per-role-type), and ADR-0036 (UserRole atemporal current-state form + audit on User's log + history-pattern and delete-policy amendments). All EmployeeRole/UserRole questions are now closed. Time Entry has structural shape; the temporal rate resolution pattern is formalized as a template via ADR-0035.
>
> **Immediate scope — Project lifecycle ADR.** Substantial. The session 8 work in full:
> 1. **Project state machine.** Candidate states: something like `active`, `closing`, `closed`, `cancelled`. Surface the fork in chat: do we need an intermediate `closing` state (a phase where the closure gate is being satisfied — blockers being resolved, dismissals being recorded, etc.), or does the gate transition directly from `active → closed` when satisfied? Same question for `cancelling`. Pose with recommendations.
> 2. **`close_project` command.** Guards against ADR-0032's closure gate: no `fix-only` blockers held + every `dismissable` blocker either no longer holds OR has a dismissal resolution Note. Read-side check; no re-stated invariant list. The Project lifecycle ADR doesn't redefine the gate — it consumes it.
> 3. **`cancel_project` command.** Handles open drafts and `in_review` RFAs (deferred from ADR-0031). Open `pending` WAs with no work referenced get hard-deleted (per ADR-0031 consequence). The fork: does `cancel_project` cascade to terminate `in_review` RFAs (auto-withdrawal), or block on them?
> 4. **Closure invariants reference flow.** DepFiling completeness, WA Code states (no open RFAs), Daily Log coverage, Deliverable status, cross-project time conflicts (Time Entry now structurally checks via ADR-0028 amendment), non-billable records — all flow through the ADR-0032 registry now. The Project lifecycle ADR confirms which registry entries are project-scope-relevant; doesn't enumerate them as new invariants.
> 5. **History pattern: lifecycle capture (already assigned).** Project state transitions + close/cancel events.
>
> **Pose Block A (state machine) first in chat under the STOP-AND-CONFIRM gate**, then Block B (cancel-cascade question), then write.
>
> **State machines locked through session 7:** WA Code (6 states, ADR-0027 — acknowledged-flag aspect superseded by ADR-0032), Deliverable (4 states, ADR-0029), WA (3 states, ADR-0030), RFA (5 states, ADR-0031), Sample Batch (2 states, ADR-0033), Lab Report document_type (3 states bespoke, ADR-0033). EmployeeRole has no state machine (temporal validity = state, ADR-0035). UserRole has no state machine (row existence = grant, ADR-0036).
>
> **Pattern menu through session 7:** 12 design patterns cumulative (unchanged count); pattern #1 (temporal rate resolution) was formalized structurally in ADR-0035 — template for future temporal-value-lookup patterns.
>
> **Time Entry dual-predicate reminder.** Project lifecycle's cross-project conflict check reads on **gross on-site range** (ADR-0028 amendment via ADR-0034). Don't conflate with blocker #9's net on-site time predicate.
>
> **Stack confirmed (no ADR yet, Step 8 will write):** backend Python/FastAPI/Ruff/SQLAlchemy/Pydantic/pytest; frontend Vite/React/TypeScript/TanStack Router/TanStack Query/openapi-ts/shadcn-ui/Storybook.
>
> **Process notes:**
> - Casual back-and-forth. Self-monitor context.
> - STOP-AND-CONFIRM gate applies — surface options in chat, await `approved`, only then write.
> - Do not write to `domain-model.md` (that's Step 6d).
> - Project lifecycle is the *entire* session 8 scope. If it doesn't fit, partition mid-session — don't bolt other entities on.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6a complete; Step 6b in progress across multiple sessions)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0036)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
