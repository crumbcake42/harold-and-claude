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

**Step 6c-i complete (session 11) — ADR-0040 and ADR-0041 written; role catalog + entity-pair relationships sweep complete (2026-05-13).**

Session 11 completed both items in Step 6c-i: role catalog (Item 1) and entity-pair relationship declarations (Item 2). Plus a substantial `tracker → coordinator` rename cascade across all planning files and prior ADR text, and an ADR-0018 amendment (Note polymorphism extended to history records).

**Major outputs:**

1. **ADR-0040 (role catalog + linear hierarchy + Note polymorphism extension + `tracker → coordinator` rename).** Four-role catalog under ADR-0036's UserRole substrate: `superadmin`, `admin`, `coordinator`, `auditor`. Linear hierarchy as an *emergent semantic property* of an explicit `(role, command) → permitted?` permission table — freeze-able when non-chain roles are introduced. Conservative grant authority: `superadmin` grants any; `admin` grants `coordinator`/`auditor` only; `coordinator`/`auditor` grant nothing. Superadmin's MVP-distinct surface = "can grant admin or superadmin" (role catalog hardcoded, no runtime role-CRUD). Deferred `reason`-field shape on grant/revoke audit events resolved by extending Note polymorphism (amends ADR-0018): new immutable subtype `audit_reason` attached to history records via optional `reason_text` command parameter. Rename `tracker → coordinator` cascades across all planning files and prior ADRs; non-role usage at ADR-0037 alternatives ("tracker tool") rephrased to "tracking tool"; existing vocabulary entry "Coordinator — office staff who manage work" consumed into the new role definition.

2. **ADR-0041 (entity-pair relationships — 8 gap resolutions).**
   - Time Entry → School: M:1 mandatory direct (`site_id`).
   - Sample Batch → School: M:1 mandatory direct (`site_id`); descriptive plain-text `sampling_locations` split from the structural site ref.
   - WA ↔ WA Code: M:N via new associative entity **WAAuthorization** (`(wa_id, wa_code_id)`, gains budget when budget tracking lands).
   - RFA → WA: M:1 mandatory direct (`amends_wa_id`); project derived via WA → Project.
   - User → Employee: 0..1 via nullable `User.employee_id?` (UNIQUE-constrained).
   - **Time Entry restructure:** drops EmployeeRole FK; Time Entry self-describes `employee_id`, `role_type`, `project_id`, `site_id`, `wa_code_id?`, etc. EmployeeRole becomes a derived/validated link. Amends ADR-0035 (drops FK + boundary invariant); amends ADR-0039 (blocker predicate generalized to "no EmployeeRole covers `(employee, role_type, date)`"; auto-reparent compound branch dissolves).
   - WA ↔ Contractor: M:N via new associative entity **ContractorEngagement** (`(wa_id, contractor_id, started_at, ended_at?)`, multiple rows per pair for stints, CPR derives per engagement). Project ↔ Contractor: derived.
   - **Document ↔ Deliverable redesigned as M:1** (not M:M as the handoff entity row had aspirationally listed). Document is single-scope via `(scope_type, scope_id)` discriminator+FK (`scope_type ∈ {project, deliverable, wa_code}`). Bundle is a query over scoped Documents + derived required Docs. Amends ADR-0014 + ADR-0015 (derivation chain clarified: WA Code → Deliverable → required Documents, not WA Code → Document directly).

3. **Cascading amendments in ADR-0041:** ADR-0014, ADR-0015, ADR-0020, ADR-0031, ADR-0033, ADR-0035, ADR-0039.

4. **Mis-attribution carry-forward (new this session):** WA mis-attributed to wrong project. Needs future compound `reassign_wa_project(wa, new_project)` + ADR-0030 amendment for `project_id` mutability on current WAs. Cascade reaches WA, WA Codes, Time Entries (direct project_id refs). Out of Step 6c-i scope; Step 6b-residual-2 or post-MVP.

5. **Roster bumps:** 16 → 18 entities (WAAuthorization + ContractorEngagement added).

**Step 6c-i is complete.** Step 6c-ii is next.

**Cumulative tables below reflect ADR-locked state through ADR-0041.**

**Per-`document_type` assignments (cumulative):**

| Pattern | document_types |
|---|---|
| Simple `missing → saved` | ACP13, ACP7, ACP15, ACP21, Emergency Notification, ACP8, VAR9 (all DepFiling docs — issued externally); COC; Daily Log |
| Cycling-family | CPR (RFA/RFP fork, 5 dates), FAMR (single-step review) |
| Bespoke | Lab Report (3 states: `missing`, `saved`, `invalid`; 4 transitions including `saved → invalid` for coordinator-discovered errors and `invalid → saved` for amended reports); RFP (4 states: `missing`, `saved`, `rejected`, `withdrawn`; SCA closure-receipt artifact per ADR-0037; `rejected` and `withdrawn` terminal; no `invalid` path since RFPs are SCA-side) |

**Entity roster (18 entities):**

| # | Entity | Notes |
|---|---|---|
| 1 | Project | SCA engagement. States: `active` / `closed` / `cancelled` (ADR-0037). Reopen permitted from both terminals. `close_project(project, rfp_file)` consumes ADR-0032 closure gate + transitions RFP `missing → saved` atomically; `cancel_project(project)` cascades RFA/pending-WA cleanup; `reopen_project` from `closed` cycles the RFP, from `cancelled` is state-flip only. Project is a Document-derivation source per ADR-0015: exactly one non-terminal RFP per project at any time. |
| 2 | School | = Site for MVP. |
| 3 | WA | Contract document; supersedable via self-reference (ADR-0016, ADR-0017). States: `pending` / `issued` / `superseded` (ADR-0030). Lists contractors via ContractorEngagement (ADR-0041); authorizes WA Codes via WAAuthorization (ADR-0041). |
| 4 | WA Code | Project-scoped line item (ADR-0020). States: `expected` / `pending_rfa` / `rfa_in_review` / `issued` / `budget_rfa_needed` (deferred) / `dismissed` (ADR-0027). Linked to WAs via WAAuthorization (ADR-0041). |
| 5 | User | Auth identity (username/password). 0..1 typed reference to Employee via nullable `employee_id` (UNIQUE-constrained per ADR-0041). |
| 6 | Employee | Person doing project work; linked to User via `User.employee_id?` (0..1 ↔ 0..1, ADR-0041). |
| 7 | EmployeeRole | Temporal work-license assignment: `(employee_id, role_type, rate, start_date, end_date?)` (ADR-0035). Full-day closed-closed range. Disjoint-ranges-per-`(employee, role_type)` invariant. Looked up by `(employee_id, role_type, date)` at rate-resolution / blocker / closure-gate time (no FK from Time Entry per ADR-0041). |
| 8 | UserRole | App-access role: `(user_id, role_type)` composite key (ADR-0036). No timestamps, no state. Grant creates row; revoke hard-deletes; audit on User's log. Drives authorization predicates per ADR-0012 + ADR-0040 role catalog. |
| 9 | Time Entry | Billable time record. Self-describing schema (ADR-0041 amends ADR-0035): `employee_id` (M:1 direct), `role_type` (enum), `project_id` (M:1 direct), `site_id` (M:1 direct), `wa_code_id` (M:1 mandatory at create, nullable via dismiss cascade), `date`, `on_site_range`, `off_site_sub_intervals` (ADR-0034). Sub-intervals ⊆ on-site range, pairwise disjoint. EmployeeRole is a derived/validated link; rate resolved at billing time. |
| 10 | Sample Batch | COC group. Carries sample type, TAT, composition `[{subtype, quantity}]`, `site_id` (M:1 mandatory direct per ADR-0041), `sampling_locations` (optional plain text per ADR-0041), employee reference (collector), collection time. WA Code reference (mandatory at create, nullable via dismiss cascade — chains from ADR-0033 blocker-9 dismissal or ADR-0039 Time-Entry-out-of-role-range dismissal). Stateless per ADR-0038. Document-derivation source (COC + Lab Report). |
| 11 | Document | Unified slot+file entity. Per-`document_type` lifecycle dispatch (ADR-0024). Single-scope via `(scope_type, scope_id)` discriminator+FK (`scope_type ∈ {project, deliverable, wa_code}`, ADR-0041). Derivation set: Deliverables (transitively WA Codes), DepFilings, Sample Batches, Project (ADR-0015 clarified by ADR-0041). Derivation fires on expected codes (ADR-0022). |
| 12 | Deliverable | SCA-portal submission package. Bundle is a query over scoped Documents: derived required Documents (from Deliverable) + user-added Documents scoped to this Deliverable + user-added Documents scoped to WA Codes that map to this Deliverable (ADR-0041 reframes earlier "M:M" framing as single-scope on Document side). States: `pending_rfa` / `outstanding` / `under_review` / `approved` (ADR-0029). `wasted` derived flag. |
| 13 | Contractor | On-site abatement (or other) third party. Admin-side roster. Linked to WAs via ContractorEngagement (ADR-0041). |
| 14 | RFA | Request for Amendment; carries pending WA edits. M:1 mandatory `amends_wa_id` direct typed ref to WA, set at auto-draft creation (post-WA-issuance), immutable for RFA lifetime (ADR-0041). Project derived via WA → Project. May be auto-created during WA issuance reconciliation. |
| 15 | Note | Polymorphic commentary; typed reference to any entity OR history record (ADR-0040). Subtypes `regular | blocker | resolution | audit_reason` (ADR-0032, ADR-0040). `authorship_class: 'user' | 'system'` + nullable `created_by`. Inter-Note `references` field. Regular Notes are creator-editable per ADR-0018; blocker, resolution, audit_reason Notes are immutable. Not deletable. |
| 16 | DepFiling | TRU-numbered regulatory filing bundle (ADR-0023). Project-scoped; editable `required_doc_types` set; Document-derivation source. No lifecycle. |
| 17 | WAAuthorization | Associative entity for WA ↔ WA Code M:N. Composite key `(wa_id, wa_code_id)`. No additional fields in MVP; gains budget when budget tracking lands. (ADR-0041) |
| 18 | ContractorEngagement | Associative entity for WA ↔ Contractor M:N with stint state. `(wa_id, contractor_id, started_at, ended_at?)`. Multiple rows per `(wa_id, contractor_id)` permitted when contractor closes CPR filing and is re-added. CPR Document derives per row. (ADR-0041) |

Values / lookups (not entities): Sample Type, Sample Subtype, Project Type, TAT options, status enums, `document_type` registry, DepFiling template constants.

**Per-entity history-pattern assignments:**

| Pattern | Entities |
|---|---|
| Comprehensive capture | Document, WA, RFA |
| Lifecycle capture | Project, Sample Batch, Deliverable, EmployeeRole, WA Code, ContractorEngagement |
| Audit log | Employee, User, Time Entry, Contractor, DepFiling |
| No history | School, Note, UserRole, WAAuthorization |

**Per-entity delete policy:**

| Policy | Entities | Notes |
|---|---|---|
| Soft delete (guarded hard-delete eligible) | Document, WA, RFA, Project, Sample Batch, Deliverable, EmployeeRole, Employee, User, Time Entry, Contractor, WA Code, DepFiling, ContractorEngagement | History-carrying or referenced by history records. |
| Hard delete | School, Note, UserRole, WAAuthorization | No history, no external history references. |

**Roles (per ADR-0040 — linear hierarchy with conservative grant authority):**

| Role | Description | Can grant |
|---|---|---|
| `superadmin` | System-level escape hatch; user-developer's role. Operationally distinct from admin only by grant authority. | any role |
| `admin` | Admin-dashboard access; manages static rosters (Employee, EmployeeRole, School, Contractor, User, UserRole grants below own level) and creates Project shells (`create_project`). | `coordinator`, `auditor` |
| `coordinator` | Project-tracking-dashboard access; manages project lifecycle (Time Entries, Sample Batches, Documents, Deliverables, RFAs, DepFilings, Notes, Project lifecycle commands). Replaces former `tracker` term. | nothing |
| `auditor` | Read-only views with simple filters. No command authority. | nothing |

Linear hierarchy is *emergent* — permission table authored as explicit `(role, command) → permitted?` rows (freeze-able when non-chain roles introduced). Effective permission = union of granted roles. Propagation default: adding a permission to a lower role propagates upward unless explicitly signaled otherwise.

**Design patterns (cumulative):**
1. Temporal rate resolution. *Formalized structurally in ADR-0035: temporal record carrying value + lookup by `(entity, type, date)`; under ADR-0041 the lookup mechanic is preserved while the FK from Time Entry is dropped.*
2. Pre-conditional lifecycle gating.
3. Derived blocking status.
4. Smart command inference.
5. Compound cascading commands.
6. WA issuance reconciliation.
7. Parameterized cycling state machine.
8. Set-based derivation extended.
9. **Delete-or-dismiss gate.** Entities with no external references hard-delete; entities with references use the dismiss cascade.
10. **Derived wasted flag.** A finalized or submitted entity retroactively invalidated by a downstream action is flagged rather than mutated.
11. **Blocker-as-Note with lazy materialization.** System-derived blockers stay derived (registry scan) until a coordinator engages (comment or dismissal). First engagement materializes a blocker Note (system-authored) with `surfaced_at` backfilled from entity history. Dismissable vs fix-only classification per registry. Cross-project blockers materialize as paired Notes linked via `paired_blocker_ref`. (ADR-0032)
12. **Chain-dismissal.** When dismissing one blocker structurally causes another's condition to fire, the secondary materializes as already-dismissed atomically; the secondary's resolution Note `references` the primary dismissal Note. (ADR-0032; two concrete instances — ADR-0033 sample-collection-coverage → batch-orphan; ADR-0039 Time-Entry-out-of-role-range → batch-orphan via wa_code-null on collected batches.)
13. **Project-state-driven immutability.** Entities whose project membership puts them in a parent project's "freezing" terminal state are immutable at command guard, with declared exceptions for commentary-only paths and parent-reopen escape hatches. Project's `closed` is the freezing terminal (billed-work snapshot); `cancelled` is the non-freezing terminal (abandoned work, available for reassignment). (ADR-0038)

**Vocabulary (cumulative):**
- **Coordinator** — the app's user with project-tracking-dashboard access; job title "project manager"; function: tracking. Consumes the former placeholder entry "office staff who manage work, not an app user in MVP" — those people are now defined as app users via this role (ADR-0040).
- **Project / School / WA / WA Code** — as before. School = site = building for MVP. Sample collection codes are school-scoped (e.g., "asbestos sampling at school A"); a WA may authorize work across multiple schools and carry multiple sample-collection codes (one per `(sample_type, school)`).
- **FAMR** — Final Air Monitoring Report. Cycling-family doc with single-step review.
- **CPR** — Contractor Package Record. Cycling-family doc with 2 buckets (RFA, RFP), 5 tracking dates. Derived per ContractorEngagement (ADR-0041).
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
- **Engagement** — A coordinator writing a comment about a blocker or dismissing it. The trigger for lazy materialization of system-derived blockers.
- **Chain-dismissal** — When dismissing one blocker structurally causes another's condition to fire, the secondary is materialized as already-dismissed atomically. Linked via the resolution Note's `references` field.
- **On-site range / off-site sub-interval (Time Entry)** — `on_site_range` is the parent range of an entry; `off_site_sub_intervals` are project-committed time-away spans within the on-site range (currently always lab delivery). Sub-intervals are pairwise disjoint, entirely within on-site range, positive-duration. (ADR-0034)
- **Gross on-site range** — the full `on_site_range` of a Time Entry, inclusive of off-site sub-intervals. Represents *project commitment*. Used by the cross-project overlap predicate (ADR-0028 amendment).
- **Net on-site time** — `on_site_range` minus the union of off-site sub-intervals. Represents *physical presence at the parent project's site*. Used by blocker #9 (sample collection coverage).
- **RFP (project-level)** — Request for Payment. SCA-generated document received when a project is submitted for payment; serves as the system-side closure receipt. New top-level `document_type` per ADR-0037, bespoke 4-state machine (`missing` / `saved` / `rejected` / `withdrawn`). One non-terminal RFP per project at any time. Distinct from CPR's internal RFP bucket (the contractor-side payment-request phase within the CPR cycling-family document) — same acronym, different schema level, different counterparty direction (SCA → us vs. contractor → us).
- **Non-terminal RFP** — an RFP in `missing` or `saved` state. The current open submission cycle for a project. Per-project invariant: exactly one at any time.
- **Terminal RFP** — an RFP in `rejected` or `withdrawn` state. Historical record of a closed-out submission cycle. Unbounded count per project (accumulates with each reopen-from-`closed` event).
- **Reopen-from-`closed` / reopen-from-`cancelled`** — the two `reopen_project` forms. From `closed`: requires `rfp_reason ∈ {rfp_rejected, rfp_withdrawn}`; cycles the RFP. From `cancelled`: pure state-flip; no structural reason captured (lifecycle capture + optional Note carry audit).
- **WAAuthorization** — associative entity for WA ↔ WA Code (composite key `(wa_id, wa_code_id)`, ADR-0041). Gains budget when budget tracking lands.
- **ContractorEngagement** — associative entity for WA ↔ Contractor with stint markers (`started_at`, `ended_at?`, ADR-0041). Multiple rows per `(wa_id, contractor_id)` allowed for repeat engagements; CPR derives per row.
- **`audit_reason` (Note subtype)** — immutable Note subtype attached to history records via optional `reason_text` on grant/revoke commands (ADR-0040).
- **`amends_wa_id`** — RFA's mandatory direct typed reference to the WA being amended; set at auto-draft creation, immutable for RFA lifetime (ADR-0041).
- **`scope_type` / `scope_id` (Document)** — single-scope discriminator + FK on Document; `scope_type ∈ {project, deliverable, wa_code}` (ADR-0041).
- **`site_id` (Time Entry, Sample Batch)** — M:1 mandatory direct typed reference to School; the structural site-of-work link (ADR-0041).
- **`sampling_locations` (Sample Batch)** — optional plain-text field describing specific spots within the site where samples were collected (ADR-0041).
- **Derived/validated link** — a relationship resolved by lookup rather than FK. Used in ADR-0041 for Time Entry ↔ EmployeeRole: rate / blocker / closure-gate logic looks up the covering EmployeeRole row from `(employee_id, role_type, date)` at use time.

## Open questions

**For session 12 — immediate (Step 6c-ii):**

- **Per-command authorization predicates** across the full Step 6b core + Step 6b-residual + Step 6c-i ADR surface. Substrate = role catalog (ADR-0040) + relationships (ADR-0041).
  - Default predicate template for project-scoped commands: "any coordinator on the project" (with linear-hierarchy propagation — admin/superadmin inherit per the explicit permission table).
  - Non-uniform predicates called out explicitly: cross-project commands (Time Entry cross-project overlap dismissal, etc.) need predicates reading both projects' coordinator rosters; grant/revoke meta-commands per ADR-0040 conservative grant authority; admin-side commands (`create_project`, all roster CRUD on Employee/EmployeeRole/School/Contractor/User/UserRole).

- **Cascade behavior on `dismiss_wa_code` for WA-Code-scoped Documents** (carry-forward from ADR-0041): cascade specifics — null `scope_id`, surface a derived blocker, or cascade-delete? May surface during predicate work or punt to Step 6b-residual-2.

**Carry-forwards worth re-checking when relevant:**
- **Mis-attribution `reassign_wa_project` compound + ADR-0030 amendment for current-WA `project_id` mutability** (new this session): out of scope for Step 6c-ii unless predicates surface it; Step 6b-residual-2 or post-MVP.
- **Cross-project Sample Batch reassignment as a structured command**: in `post-mvp.md` alongside notifications.
- **Retroactive rate corrections via Time-Entry rate snapshot** (carry-forward from ADR-0035): reversible additive change post-MVP if signal emerges.
- **Security-immediate revoke runtime semantics** (session invalidation on `revoke_user_role`): implementation concern, deferred to auth implementation step.

**Carried forward (deferred to later steps):**
- **WAAuthorization budget fields** — added when budget tracking design lands (continues ADR-0041 carry-forward of the prior `WA ↔ WA Code budget tracking` deferral).
- **ContractorEngagement lifecycle commands** (`start_contractor_engagement`, `end_contractor_engagement` or equivalents) and CPR-derivation rule per engagement: Step 6b-residual-2 if not already implicit via CPR cycling-family doc_type lifecycle (ADR-0024).
- **Billing Rate entity/table** — temporal `(subtype, TAT) → rate` lookup. Likely Step 6d or later. Follows the temporal rate resolution template formalized in ADR-0035 / ADR-0041.
- **Per-command authorization predicates** — Step 6c-ii (ADR-0012 carry-forward consumed there). Covers the full Step 6b + Step 6b-residual + Step 6c-i command surface.
- **Quarantine as a per-entity violation-handling pattern** — excluded from history-pattern menu (ADR-0013); remains deferred per ADR-0011. Step 6d.
- **Bulk import file-upload relaxation** — 6b or implementation.
- **Project structure for managing N `document_types`** — defer to implementation phase.
- **History implementation shape** (event store, append-only tables, temporal tables) — Step 8.
- **Persistence isolation for cross-entity invariants** — Step 8.
- Whether existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

## Next session

**Step 6c-ii (session 12) — per-command authorization predicates.** Step 6c-i is complete. Step 6c-ii writes per-`(role, command)` authorization predicates across all Step 6b + 6b-residual + 6c-i ADRs using the role catalog (ADR-0040) and relationship/entity substrate (ADR-0041).

### Prompt for the next session

> Resume work. Step 6c-i closed in session 11 with ADR-0040 (role catalog: superadmin/admin/coordinator/auditor; linear hierarchy with conservative grant authority; Note polymorphism extended to history records via new `audit_reason` subtype; `tracker → coordinator` rename) and ADR-0041 (entity-pair relationships: 8 gap resolutions including Time Entry restructure to self-describing schema, Document single-scope, two new associative entities WAAuthorization and ContractorEngagement, RFA `amends_wa_id` direct ref, Document derivation chain clarification).
>
> **Session 12 scope (Step 6c-ii):**
>
> Write per-`(role, command)` authorization predicates across the full Step 6b core + Step 6b-residual + Step 6c-i ADR surface. Substrate is the role catalog (ADR-0040) + relationships (ADR-0041).
>
> Default predicate template for project-scoped commands: "any coordinator on the project" (with linear-hierarchy propagation: admin/superadmin inherit per the explicit table). Non-uniform predicates (cross-project commands, grant/revoke meta-commands per ADR-0040 conservative grant authority, admin-side commands like `create_project` or roster CRUD) called out explicitly.
>
> **Outputs:** ADR for the per-`(role, command)` predicate table.
>
> **State machines locked through session 11:**
> - With state machines: WA Code (6 states, ADR-0027), Deliverable (4 states, ADR-0029), WA (3 states, ADR-0030), RFA (5 states, ADR-0031), Lab Report `document_type` (3 states bespoke, ADR-0033), Project (3 states, ADR-0037), RFP `document_type` (4 states bespoke, ADR-0037).
> - Without state machines: EmployeeRole (temporal validity, ADR-0035), UserRole (row existence, ADR-0036), DepFiling (no lifecycle, ADR-0023), Sample Batch (stateless per ADR-0038), WAAuthorization (immutable, ADR-0041), ContractorEngagement (stint markers, ADR-0041), School / Note / User / Employee / Contractor.
>
> **Roster (18 entities through ADR-0041):** Original 16 + WAAuthorization (no history, hard delete) + ContractorEngagement (lifecycle capture, soft delete).
>
> **Roles (per ADR-0040):**
> - `superadmin`: grants any role; otherwise functionally admin in MVP (role catalog hardcoded, no runtime role-CRUD).
> - `admin`: admin-dashboard access; manages static rosters + creates Projects. Grants coordinator/auditor.
> - `coordinator`: project-tracking-dashboard access; manages project lifecycle.
> - `auditor`: read-only views with simple filters; no command authority.
> - Linear hierarchy is emergent; permission table authored as explicit `(role, command)` rows (freeze-able when non-chain roles are introduced).
>
> **Pattern menu through session 11:** 13 design patterns cumulative. No new patterns this session.
>
> **Blocker registry through session 11:** 11 entries. ADR-0039's entry (Time-Entry-out-of-role-range) generalized in ADR-0041 to "no EmployeeRole covers `(employee, role_type, date)`."
>
> **Stack confirmed (no ADR yet, Step 8 will write):** backend Python/FastAPI/Ruff/SQLAlchemy/Pydantic/pytest; frontend Vite/React/TypeScript/TanStack Router/TanStack Query/openapi-ts/shadcn-ui/Storybook.
>
> **Process notes:**
> - Casual back-and-forth. Self-monitor context. One topic per turn.
> - STOP-AND-CONFIRM gate applies fully to all predicate deliberations.
> - Do not write to `domain-model.md` (that's Step 6d).
> - **Permission propagation rule** (memory `feedback_permission_propagation`): adding a permission to a lower role propagates upward in the chain by default; non-chain changes require explicit user signal.
> - **Recommendation strength** (memory `feedback_recommendation_strength`): state confidence on recommendations; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6a complete; Step 6b core complete; Step 6b-residual complete; Step 6c-i complete; Step 6c-ii next; Step 6d after)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0041)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
