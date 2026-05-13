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

**Step 6b-residual (session 9) — Step 6c partition decided; ADR-0038 positions locked but unwritten; rate-change compound deferred (2026-05-12).**

Session opened in Case 2 (Step 6c had no scoped prompt). Fit checklist fired signals 1, 3, 4, 5, and 7; partitioned into three sub-sessions. `steps.md` and `handoff.md` were updated to reflect the partition. The first sub-session's deliberation then reframed its own scope rather than producing an ADR.

**Major outputs:**

1. **Step 6c partition (Approach A from partition options).** Three-way split:
   - **Step 6b-residual** — workflow consolidation (this session's intended scope; session 9 covered deliberation only for item 1, transcription + item 2 roll forward).
   - **Step 6c-i** — role catalog + relationship declarations.
   - **Step 6c-ii** — per-command authorization predicates (consumes ADR-0012 carry-forward).

2. **ADR-0033's `billed` state dropped (positions locked, ADR pending).** Original Step 6b-residual scope assumed `received → billed` had a separate billing-system trigger. User clarified mid-deliberation: (a) `billed` was conceived as marking closure-snapshot membership ("this batch was in a submitted payment package"), not billing-system finalization; (b) the in-MVP billing flow is a draft-invoice estimator with no state transitions — it aggregates rates, sample quantities, and WA flat fees on demand; (c) RFP rejection/withdrawal returns all submitted documents and the next submission is a blank slate. **Closure-snapshot membership is therefore not sticky and not per-entity-stateful.** It's derived from `Project.state == closed` + dismissed-flag at closure moment.

   **Position locked (Approach A from the cleanup options):** drop the `billed` state from ADR-0033 entirely. Sample Batch becomes stateless (joins EmployeeRole / DepFiling / Note / UserRole). Lifecycle capture pattern stays (covers `create_sample_batch` and `relink_sample_batch_wa_code` as discrete events without a state field).

3. **Project-state-driven immutability rule to be formalized in the same ADR.** Dropping `billed` only works if entity immutability is carried elsewhere. ADR-0037 currently says "no state changes on cancellation" but doesn't formalize "no mutations on entities attached to a `closed`-state project, except blocker-dismissal paths." That rule lands in the upcoming amending ADR, alongside the Sample Batch state cleanup. Whether it also earns a 13th design pattern entry decided at write time.

4. **ADR mechanics decided.** **Amend** ADR-0033 (project's established practice for partial revisions — six prior amendments across ADRs 0033, 0034, 0036 set the precedent), **not supersede**. Grep-precedent for traceability (no `Modified by:` header-annotation pattern starting now). Bundle Sample Batch state cleanup + project-state-driven immutability rule into one ADR (Approach A on the bundling fork).

5. **Side discussion: ADR file-management strategy.** User raised whether to compact amendments long-term to reduce reader load. Recommendation: don't compact mid-phase (loses deliberation context that actively informs current sessions). Consider one-time consolidation at Conceptualization → Implementation phase boundary (Step 9) — natural breakpoint, deliberation is settled, the consolidated record is the right artifact for implementation work. User accepted; no change to current practice.

6. **Carry-forward: `change_employee_role_rate` compound command.** Originally in session 9's scope; not reached. Rolls into session 10 after ADR-0038 transcription.

**Incomplete (rolling to session 10):**
- **ADR-0038 not written.** Positions locked; transcription is session 10's first task.
- **Rate-change compound not addressed.** Deliberation deferred to session 10 after ADR-0038 lands.

**Cumulative tables below remain unchanged** — they reflect ADR-locked state through ADR-0037. Sample Batch entity row and state-machine list update when ADR-0038 writes.

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

**For session 10 — immediate (Step 6b-residual continued):**

- **ADR-0038 transcription (positions locked in session 9 — no new deliberation, but draft chat-side before writing to confirm wording):**
  - Title naming for the dual-surface ADR (covers Sample Batch state cleanup + project-state-driven immutability rule).
  - Restate ADR-0033's Sample Batch state machine entry: no `state` field; lifecycle capture covers `create_sample_batch` and `relink_sample_batch_wa_code` as discrete events.
  - Write the project-state-driven immutability rule. Candidate phrasing: *"Commands on entities whose project membership puts them in a `closed` or `cancelled` project are rejected at command guard, except blocker-dismissal commands (per ADR-0032) and `reopen_project` (per ADR-0037)."* Confirm exception list during writing — sweep ADR-0037's `cancel_project` cascade (RFA withdrawal, draft-RFA hard-delete, pending-WA hard-delete) and ADR-0032's resolution-Note writes to make sure they're either pre-closure-only or fall under the dismissal exception.
  - Decide whether the immutability rule earns a 13th design pattern entry or just stands as a one-off ADR-0037 lifecycle consequence.
  - Cumulative-table updates in `handoff.md` after the ADR lands: Sample Batch entity row (drop "States: `received` / `billed` (ADR-0033)"); state-machine list (Sample Batch moves from "With state machines" to "Without state machines"); pattern menu if a 13th pattern is declared.

- **`change_employee_role_rate` compound command** (ADR-0035 carry-forward; deferred from session 9):
  - Parameter shape: `(role, new_rate, effective_date)` was sketched in ADR-0035; confirm sufficient or expand (e.g., explicit handle for the new row's `end_date`, default `NULL`).
  - Atomic sequence: close existing row at `effective_date − 1`, then create new row at `effective_date`. Confirm boundary arithmetic with closed-closed range semantics.
  - Guards: inherited disjoint-ranges-per-role-type from `edit_employee_role` + `create_employee_role`; no-orphan-future-Time-Entries from `close_employee_role`. Any new guards specific to the compound shape?
  - History capture: under lifecycle capture, does the compound emit one event or two (close + create)? Default expectation is two underlying events plus a logical compound marker, mirroring other compound commands (e.g., `close_project`).
  - Whether it earns its own ADR or folds into ADR-0038. Default lean: separate ADR (different surface area, different deliberation thread; bundling would muddy ADR-0038's "drop a state + formalize an immutability rule" scope).
  - Out-of-scope but adjacent: authorization predicate for the compound (lands in Step 6c-ii); UI/ergonomic wrapper concerns (implementation).

**Carry-forwards worth re-checking when relevant:**
- **Cross-project Sample Batch reassignment as a structured command**: in `post-mvp.md` alongside notifications.
- **Retroactive rate corrections via Time-Entry rate snapshot** (carry-forward from ADR-0035): reversible additive change post-MVP if signal emerges.
- **`reason` field shape on UserRole grant/revoke audit events** (free-text vs enum vs both): deferred to Step 6c-i alongside concrete role catalog.
- **Security-immediate revoke runtime semantics** (session invalidation on `revoke_user_role`): implementation concern, deferred to auth implementation step.

**Carried forward (deferred to later steps):**
- **WA ↔ WA Code budget tracking implementation** — Option B direction confirmed; design deferred until budget tracking is in scope.
- **Billing Rate entity/table** — temporal `(subtype, TAT) → rate` lookup. Likely Step 6d or later. Follows the temporal rate resolution template formalized in ADR-0035.
- **Concrete authorization roles and relationship declarations** — Step 6c-i. ADR-0036 establishes UserRole as the substrate; the role catalog and entity-pair relationship declarations are Step 6c-i's work.
- **Per-command authorization predicates** — Step 6c-ii (ADR-0012 carry-forward consumed there). Covers the full Step 6b + Step 6b-residual command surface.
- **Document → Deliverable M:M** — confirmed; formal relationship declaration in Step 6c-i.
- **Quarantine as a per-entity violation-handling pattern** — excluded from history-pattern menu (ADR-0013); remains deferred per ADR-0011. Step 6d.
- **Bulk import file-upload relaxation** — 6b or implementation.
- **Project structure for managing N `document_types`** — defer to implementation phase.
- **History implementation shape** (event store, append-only tables, temporal tables) — Step 8.
- **Persistence isolation for cross-entity invariants** — Step 8.
- Whether existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

## Next session

**Step 6b-residual continued (session 10) — write ADR-0038, then deliberate the rate-change compound.** Session 9 covered the Step 6c partition decision and locked positions for ADR-0038 (drop ADR-0033's `billed` state; formalize project-state-driven immutability) but did not write the ADR. Session 10 starts with the transcription, then takes up the deferred `change_employee_role_rate` compound. May complete in one session; may need session 11 if the rate-change deliberation runs long. Step 6c-i follows once Step 6b-residual fully closes.

### Prompt for the next session

> Resume work. Session 9 did two things: (a) partitioned Step 6c into a three-way split (Step 6b-residual → Step 6c-i → Step 6c-ii); (b) deliberated Step 6b-residual item 1 and reframed it — the "billing finalization trigger" turned out to rest on a misread of `billed`'s semantics. Positions for ADR-0038 are locked; the ADR was not written this session.
>
> **Session 10 has two tasks, in order:**
>
> 1. **Write ADR-0038** (positions locked in session 9 — transcription work, not new deliberation). Content:
>    - **Amend ADR-0033's Sample Batch state machine entry:** drop the `billed` terminal state. Sample Batch becomes stateless (joins EmployeeRole / DepFiling / Note / UserRole as "no state machine"). Lifecycle capture pattern stays (covers `create_sample_batch` and `relink_sample_batch_wa_code` as discrete events without a state field).
>    - **Formalize the project-state-driven immutability rule:** commands on entities attached to a project in `closed` or `cancelled` state are rejected at command guard, except blocker-dismissal commands (per ADR-0032) and `reopen_project` (per ADR-0037). Confirm the exception list while writing — sweep ADR-0037's `cancel_project` cascade and ADR-0032's resolution-Note writes to verify they're either pre-closure-only or fall under the dismissal exception.
>    - **Mechanics:** amendment to ADR-0033 (using project's "Amendments to other ADRs" pattern), grep-precedent traceability (no header annotation). ADR-0033's status stays `accepted`.
>    - **Pattern menu:** decide whether the immutability rule earns a 13th design pattern entry or just stands as a one-off ADR-0037 lifecycle consequence.
>    - **Update cumulative tables in `handoff.md` after the ADR lands:** Sample Batch entity row (drop "States: `received` / `billed` (ADR-0033)"); state-machine list (Sample Batch moves from "With state machines" to "Without state machines"); pattern menu if applicable; vocabulary section if needed.
>
> 2. **Deliberate `change_employee_role_rate` compound command** (deferred from session 9). Under STOP-AND-CONFIRM gate, surface one decision at a time:
>    - Parameter shape (`role`, `new_rate`, `effective_date` was sketched in ADR-0035; confirm or expand).
>    - Atomic sequence: close existing row at `effective_date − 1`, create new row at `effective_date`. Confirm boundary arithmetic against ADR-0035's closed-closed range semantics.
>    - Inherited guards (disjoint-ranges-per-role-type, no-orphan-future-Time-Entries) — confirm sufficient; identify any compound-specific guards.
>    - History-capture shape (one event vs. two underlying + compound marker — default expectation: two underlying events plus a logical compound marker, consistent with other compound commands like `close_project`).
>    - Whether it earns its own ADR (ADR-0039) or folds into ADR-0038. Default lean: separate ADR (different surface area, different deliberation thread).
>
> **State machines locked through session 8 (will change in session 10 once ADR-0038 lands):**
> - With state machines: WA Code (6 states, ADR-0027), Deliverable (4 states, ADR-0029), WA (3 states, ADR-0030), RFA (5 states, ADR-0031), **Sample Batch (2 states, ADR-0033) → becomes stateless after ADR-0038**, Lab Report `document_type` (3 states bespoke, ADR-0033), Project (3 states, ADR-0037), RFP `document_type` (4 states bespoke, ADR-0037).
> - Without state machines: EmployeeRole (temporal validity = state, ADR-0035), UserRole (row existence = grant, ADR-0036), DepFiling (no lifecycle, ADR-0023), School / Note / User / Employee / Contractor (no-history or audit-log entities), **Sample Batch (after ADR-0038)**.
>
> **Pattern menu through session 8:** 12 design patterns cumulative. May grow to 13 in session 10 if the project-state-driven immutability rule earns an entry.
>
> **Stack confirmed (no ADR yet, Step 8 will write):** backend Python/FastAPI/Ruff/SQLAlchemy/Pydantic/pytest; frontend Vite/React/TypeScript/TanStack Router/TanStack Query/openapi-ts/shadcn-ui/Storybook.
>
> **Process notes:**
> - Casual back-and-forth. Self-monitor context.
> - ADR-0038 transcription is mechanical (positions locked in session 9) — draft chat-side before writing to confirm wording, but no per-decision STOP-AND-CONFIRM gate for the transcription itself.
> - STOP-AND-CONFIRM gate applies fully to the rate-change compound deliberation.
> - Do not write to `domain-model.md` (that's Step 6d).
> - One topic per turn during back-and-forth.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6a complete; Step 6b core complete; Step 6b-residual in progress — session 9 deliberation done, ADR-0038 transcription + rate-change compound roll to session 10; Step 6c partitioned into 6c-i and 6c-ii)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0037)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
