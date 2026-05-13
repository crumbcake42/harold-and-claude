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

**Step 6b (continued, session 8) — Project lifecycle ADR landed (ADR-0037), substantially expanded mid-session to include the SCA RFP closure artifact and the reopen-RFP-replacement mechanic (2026-05-12).** Closes out Step 6b's core entity-lifecycle scope. Residual workflow items (Sample Batch `received → billed` billing-finalization trigger; `change_employee_role_rate` compound command shape) defer as carry-forwards into Step 6c or a brief workflow-consolidation pass.

**Major outputs:**

1. **Project state machine + commands (ADR-0037).** Three states: `active` / `closed` / `cancelled`. Reopen permitted from both terminals.
   - **`close_project(project, rfp_file)`** compound: gate-checks ADR-0032 closure predicate, transitions the project's open RFP Document `missing → saved`, transitions Project `active → closed`. All atomic. The compound's atomicity ensures no intermediate window where the RFP is saved but the project is still `active`.
   - **`cancel_project(project)`** compound cascade: (1) hard-deletes `pending` WAs with no work-referenced codes + their codes (per ADR-0031); (2) withdraws all `in_review` RFAs (under `withdraw_rfa`'s any-tracker authorization, ADR-0031); auto-draft regeneration suppressed on cancelled projects; (3) auto-deletes `draft` RFAs that empty as a side effect; (4) transitions Project `active → cancelled`. Cancellation does **not** pass through the closure gate — intentional, to support the "cancel a project precisely because its blockers can't be resolved" path.
   - **`reopen_project`** has two forms. From `closed`: takes `rfp_reason: 'rfp_rejected' | 'rfp_withdrawn'`, transitions current `saved` RFP to the named terminal state, derives a new RFP Document in `missing`, transitions Project. From `cancelled`: pure state-flip with **no structural reason** captured (self-reported reasons for course corrections are unreliable — people will either be dishonest or use it to point fingers; contextual rationale fits a regular user Note per ADR-0018).
   - **`issued` WAs and codes stay on cancellation.** Time Entries, Sample Batches, Deliverables, Documents, DepFilings, Notes all stay attached for audit; no state changes on cancellation.

2. **RFP (Request for Payment) as new `document_type` — bespoke 4-state machine (ADR-0037).** States: `missing`, `saved`, `rejected`, `withdrawn`. Transitions: `missing → saved` at `close_project` time (only structural path in); `saved → rejected` / `saved → withdrawn` at `reopen_project` from `closed`. **`rejected` and `withdrawn` are terminal** — no path back. No `missing → invalid` or `invalid → saved` paths (unlike Lab Report): RFPs are SCA-side, no "defective RFP" operational path. Joins ADR-0024's bespoke row alongside Lab Report.
   - **Naming.** "RFP" is reused at two schema levels: top-level `document_type` (SCA → us payment-request receipt) and CPR's internal RFP bucket (contractor → us payment-request phase). Acronym overlap accepted: current office vocabulary tolerates the ambiguity; disambiguation can land later if scale or onboarding pressure forces it.

3. **Project as Document-derivation source + closure blocker registry growth (ADR-0037).** Project joins ADR-0015's derivation-source roster (was WA Code, DepFiling, Sample Batch + project events). **Per-project derivation rule: exactly one non-terminal RFP at any time** — initial at project creation; new instances at each reopen-from-`closed` event. Terminal RFPs (`rejected`, `withdrawn`) accumulate unboundedly as historical record. ADR-0032 registry grows by entry **#10 (fix-only): "project's non-terminal RFP not in `saved` state at closure"** — no real-world acceptance path; RFP-saved IS the system-side evidence of submission.

4. **ADR-0031 deferred question resolved.** "Handling of open drafts and `in_review` RFAs on a cancelled project" → cascade both. Block-on-`in_review` and mixed-cascade alternatives explicitly rejected (gap-period risk, no audit-quality gain).

5. **Closure gate consumption (not redefinition).** All ten ADR-0032 registry entries are project-scope-relevant — entries #1–#9 attach to project-scoped entities (Time Entry, Sample Batch, DepFiling, RFA) or cross-project relationships (#8 — both projects involved per ADR-0028), and entry #10 attaches directly to Project. ADR-0037 confirms this and consumes the gate; doesn't re-state invariants.

6. **Step 6b core scope complete.** All entities with lifecycles have named state machines and named commands. Remaining `Step 6b`-flavored items are residual workflow consolidations, not core lifecycle work.

**Cumulative tables below reflect ADR-locked state through ADR-0037.**

**Per-`document_type` assignments (cumulative):**

| Pattern | document_types |
|---|---|
| Simple `missing → saved` | ACP13, ACP7, ACP15, ACP21, Emergency Notification, ACP8, VAR9 (all DepFiling docs — issued externally); COC; Daily Log |
| Cycling-family | CPR (RFA/RFP fork, 5 dates), FAMR (single-step review) |
| Bespoke | Lab Report (3 states: `missing`, `saved`, `invalid`; 4 transitions including `saved → invalid` for tracker-discovered errors and `invalid → saved` for amended reports); RFP (4 states: `missing`, `saved`, `rejected`, `withdrawn`; SCA closure-receipt artifact per ADR-0037; `rejected` and `withdrawn` terminal; no `invalid` path since RFPs are SCA-side) |

**Entity roster (16 entities):**

| # | Entity | Notes |
|---|---|---|
| 1 | Project | SCA engagement. States: `active` / `closed` / `cancelled` (ADR-0037). Reopen permitted from both terminals. `close_project(project, rfp_file)` consumes ADR-0032 closure gate + transitions RFP `missing → saved` atomically; `cancel_project(project)` cascades RFA/pending-WA cleanup; `reopen_project` from `closed` cycles the RFP, from `cancelled` is state-flip only. Project is a Document-derivation source per ADR-0015: exactly one non-terminal RFP per project at any time. |
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
- **RFP (project-level)** — Request for Payment. SCA-generated document received when a project is submitted for payment; serves as the system-side closure receipt. New top-level `document_type` per ADR-0037, bespoke 4-state machine (`missing` / `saved` / `rejected` / `withdrawn`). One non-terminal RFP per project at any time. Distinct from CPR's internal RFP bucket (the contractor-side payment-request phase within the CPR cycling-family document) — same acronym, different schema level, different counterparty direction (SCA → us vs. contractor → us).
- **Non-terminal RFP** — an RFP in `missing` or `saved` state. The current open submission cycle for a project. Per-project invariant: exactly one at any time.
- **Terminal RFP** — an RFP in `rejected` or `withdrawn` state. Historical record of a closed-out submission cycle. Unbounded count per project (accumulates with each reopen-from-`closed` event).
- **Reopen-from-`closed` / reopen-from-`cancelled`** — the two `reopen_project` forms. From `closed`: requires `rfp_reason ∈ {rfp_rejected, rfp_withdrawn}`; cycles the RFP. From `cancelled`: pure state-flip; no structural reason captured (lifecycle capture + optional Note carry audit).

## Open questions

**For session 9 — immediate (Step 6c entry):**
- **Step 6c entry — Relationships & authorization.** Case 2 fit assessment applies (likely too large for one session; expect partitioning). Starting questions: (a) concrete role catalog (MVP scoped to project-manager / tracker role per ADR-0036's UserRole substrate; field staff post-MVP); (b) per-command authorization predicates across the full command surface from Step 6b ADRs (ADR-0012 carry-forward — substantial); (c) entity-to-entity relationship declarations (Document ↔ Deliverable M:M is pending formal declaration; every other entity-pair link too); (d) residual workflow items that may fold in given authorization dependencies — billing finalization flow trigger (`received → billed` for Sample Batch, ADR-0033 deferral) and `change_employee_role_rate` compound command shape (ADR-0035 deferral). The fit checklist may push some of (d) into a brief workflow-consolidation session before 6c proper.

**Carry-forwards worth re-checking when relevant:**
- **Billing finalization flow** (the `received → billed` Sample Batch trigger from ADR-0033): specific command and authorization at billing-design step (likely Step 6c or a workflow-consolidation pass).
- **Cross-project Sample Batch reassignment as a structured command**: in `post-mvp.md` alongside notifications.
- **`change_employee_role_rate` compound command** (candidate from ADR-0035): full spec deferred to workflow-consolidation step (or fold into Step 6c).
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

**Step 6b core scope complete — next session enters Step 6c (Relationships & authorization).** See `planning/steps.md` for Step 6c's brief. Case 2 (new step, no scoped prompt) applies — run the fit checklist; likely too large for one session and will need partitioning. Residual Step 6b workflow items (billing finalization flow trigger; `change_employee_role_rate` compound) may fold into 6c given their authorization dependencies, or may warrant a brief workflow-consolidation pass first.

### Prompt for the next session

> Resume work. Step 6b's core entity-lifecycle scope is complete: every entity with a lifecycle has a named state machine and named commands. Session 8 landed ADR-0037 (Project state machine + `close_project` / `cancel_project` / `reopen_project` commands + RFP as new bespoke `document_type` + Project as Document-derivation source + closure blocker registry entry #10).
>
> **Step 6c entry.** Apply Case 2 fit checklist from `planning/_workflow.md` to size the work. Initial scope spans:
> 1. **Concrete role catalog.** MVP scoped to project-manager / tracker role per ADR-0036's UserRole substrate. Field staff deferred to post-MVP. Enumerate the role(s); per-role description.
> 2. **Per-command authorization predicates** (ADR-0012 carry-forward). Every command across the Step 6b ADRs needs a predicate. The aggregated surface is substantial — strong partition candidate.
> 3. **Relationship declarations.** Cardinality + ownership for every entity-to-entity link. Document ↔ Deliverable M:M is pending formal declaration. All other entity-pair relationships need explicit declaration too.
> 4. **Residual Step 6b workflow items** that may fold in: billing finalization flow trigger for Sample Batch (`received → billed`, ADR-0033 deferral); `change_employee_role_rate` compound command shape (ADR-0035 deferral). May not fit; may warrant a brief workflow-consolidation pass before 6c proper.
>
> **Pose partition options first in chat under the STOP-AND-CONFIRM gate.** Likely shape: (i) workflow-consolidation pass (billing trigger + rate-change command); (ii) Step 6c-i (role catalog + relationship declarations); (iii) Step 6c-ii (authorization predicates per command). Or some collapse if the user judges one session can carry more.
>
> **State machines locked through session 8:**
> - With state machines: WA Code (6 states, ADR-0027), Deliverable (4 states, ADR-0029), WA (3 states, ADR-0030), RFA (5 states, ADR-0031), Sample Batch (2 states, ADR-0033), Lab Report `document_type` (3 states bespoke, ADR-0033), **Project (3 states, ADR-0037)**, **RFP `document_type` (4 states bespoke, ADR-0037)**.
> - Without state machines: EmployeeRole (temporal validity = state, ADR-0035), UserRole (row existence = grant, ADR-0036), DepFiling (no lifecycle, ADR-0023), School / Note / User / Employee / Contractor (no-history or audit-log entities, no concrete lifecycle).
>
> **Pattern menu through session 8:** 12 design patterns cumulative (unchanged count). RFP-as-closure-artifact and the per-Project non-terminal-RFP invariant are ADR-0037-specific shapes, not new general patterns.
>
> **Stack confirmed (no ADR yet, Step 8 will write):** backend Python/FastAPI/Ruff/SQLAlchemy/Pydantic/pytest; frontend Vite/React/TypeScript/TanStack Router/TanStack Query/openapi-ts/shadcn-ui/Storybook.
>
> **Process notes:**
> - Casual back-and-forth. Self-monitor context.
> - STOP-AND-CONFIRM gate applies — surface options in chat, await `approved`, only then write.
> - Apply the Case 2 fit checklist explicitly before sizing the session — Step 6c's full scope is unlikely to fit one context window.
> - Do not write to `domain-model.md` (that's Step 6d).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6a complete; Step 6b core scope complete; Step 6c next)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0037)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
