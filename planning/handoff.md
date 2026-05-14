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

**Step 6c-iv-a — Contract entity + Project wiring. ✓ COMPLETE. ADR-0043 written. Case 3 entry; ran clean through all four scope topics. Step 6c-iv was Case-2-sized and split (Option A) earlier in the same session, before 6c-iv-a ran.**

Step 6c-iv-a was the Case 3 entry for the model half of Step 6c-iv (Option A split). All four scope topics were deliberated and approved in chat, then written up as **ADR-0043 — Contract entity, Project → Contract relationship, and contract-attachment model**:

- **Attachment model (the load-bearing fork) — lands split.** Employee rates stay **FK-side**: EmployeeRole keeps its own per-row `rate` and will gain a `contract_id` (the disjoint-ranges invariant restructure is 6c-iv-b). Code flat fees go **inline**: Contract carries a `code_flat_fee_schedule` — a non-temporal `{code_type, fee}` value collection, fixed for the contract's whole life. Asymmetry rationale: title rates vary by employee *and* contract (can't collapse into a contract-level table); code fees are genuinely per-`(code_type, contract)` (can).
- **Contract schema.** `id` (UUID per ADR-0005); `contract_number` (mandatory, uniqueness-constrained natural key); `start_date` + nullable `end_date`; `code_flat_fee_schedule`; optional `name` (when null, the display label derives as `C` + last 5 chars of `contract_number` — derived label, not a stored default). No counterparty field (SCA is the sole MVP client; additional clients indefinitely deferred). No contract value/ceiling (post-MVP, with budget tracking).
- **Lifecycle / history / delete.** No state machine — `pending` / `active` / `expired` derived from `(start_date, end_date?)` + clock (ADR-0035 precedent; early termination is an `end_date` edit). History pattern: **audit log** — fee-schedule corrections are near-zero and prior-value disputes don't arise (confirmed from 2+ years of operational experience). Delete policy: **soft delete**.
- **Project → Contract.** `Project.contract_id` — M:1, mandatory, direct typed ref. `create_project` gains a mandatory `contract` parameter (admin-side per ADR-0040; **amends ADR-0037**). No in-term validation at creation. **Immutable in MVP** — no mutation command.

Entity roster 18 → 19 (Contract added). Cumulative tables below refreshed.

**Out of scope of 6c-iv-a, unchanged → Step 6c-iv-b:** EmployeeRole contract-scoping (the `contract_id` addition + disjoint-ranges invariant restructure per-`(employee, role_type)` → per-`(employee, role_type, contract)` + rate-resolution lookup gaining the contract dimension + `change_employee_role_rate` dispatch impact); the WA Code default-flat-fee lookup mechanics; the blast-radius confirmation. 6c-iv-b amends ADR-0035 / 0039 / 0041 / 0020 / 0027.

**New post-MVP carry-forward (ADR-0043):** `reassign_project_contract` — a `role >= admin` compound to change a project's contract after creation, cascading rate resolution + flat-fee lookups across the project's work. Recorded in `post-mvp.md`.

**ADR numbering convention change:** with an unplanned session inserted, pre-assigned ADR numbers are now fragile — numbers are assigned at write time from here on. The write-off ADR took **ADR-0042** (next sequential); the Step 6c-ii predicate-table ADR is no longer pre-numbered (was "ADR-0042" in earlier plan text — those references are de-numbered to "the Step 6c-ii predicate-table ADR" throughout).

**Cluster predicates carried forward — clusters 6–7 (deliberated session 13):**

- **Cluster 6 — ContractorEngagement lifecycle.** `start_contractor_engagement`, `end_contractor_engagement` → `role ≥ coordinator`. Resolved as **named commands**, not implicit via CPR cycling-family lifecycle: the CPR Document *derives from* the engagement row (folding engagement into CPR lifecycle inverts the dependency); the timelines are independent (engagement can start before the CPR is drafted); multiple stints per `(wa_id, contractor_id)` need explicit open/close. Command-shape (signatures, pre-conditions) deferred to Step 6c-iii — ContractorEngagement sits in that restructure's blast radius. Date defaults captured for 6c-iii: `started_at` → row-creation date; `ended_at` → CPR-saved date (nullable, overridable).
- **Cluster 7 — Cross-project commands.** Two findings. (a) **No special cross-project predicate primitive needed.** The ADR-0040 carry-forward worried predicates might need to read "both projects' coordinator rosters," but MVP-flat (locked clarification 1) has no per-project rosters — plain `role ≥ coordinator` suffices. When per-project scoping lands post-MVP the qualifier is a localized edit. (b) **`split_entry` → explicit row, `role ≥ coordinator`.** It's ADR-0028-named and structurally not-CRUD (one record becomes two); its command-shape is undefined and carried forward — no natural home step (candidate: Step 6d or a residual). **Correction logged:** the session-12 handoff/prompt's "cross-project overlap dismissal (ADR-0028 family)" framing was wrong — blocker #8 is fix-only, there is no dismissal command. (The Step 6b-residual-2 reframe revisits this regardless.)

**Blocker-resolution model reframe — Step 6b-residual-2: session 14a complete (ADR-0042), session 14b remaining:**

14a settled the model — the `write-off` model, the `has-default-resolution | fix-only` binary reframe, the nuclear guard, and vocab reconciliation — all in **ADR-0042** (see Last session summary). **Session 14b remains:** the one-by-one classification pass over all 11 registry blockers (`has-default-resolution` vs. `fix-only` — #10, non-terminal RFP not `saved`, is the candidate lone fix-only survivor) plus per-blocker default-resolution command definitions. 14b amends ADR-0032's registry and ADR-0028 (cross-project overlap gains a default-resolution); chain-dismissal instances (ADR-0033/0039) gain `write_off`-Note emission. 14b is deferred behind the inserted Step 6c-iv. Full brief in `steps.md` → Step 6b-residual-2.

**Locked clarifications carried from session 12 (still binding for the Step 6c-ii predicate-table ADR):**

1. **Project-scoped predicate form is MVP-flat: plain `role ≥ coordinator`.** No `assigned_to(project)` qualifier in MVP — per-project coordinator scoping is post-MVP per ADR-0040. Adding the qualifier later is a localized edit to project-scoped rows.
2. **Project-state immutability (ADR-0038 pattern #13) stays a pre-condition, NOT in the auth predicate.** Target-state-based, not caller-based; conflating muddies the static-analysis story ADR-0012 cites.
3. **No system-caller primitive in the predicate vocabulary.** Cascade effects inherit auth from the user-facing command that initiated them. The predicate table enumerates user-facing commands only.
4. **`dismiss_wa_code` cascade-shape question stays scope-flagged.** The Step 6c-ii predicate-table ADR predicates the user-facing `dismiss_wa_code` command only; cascade-shape design is now a candidate fold-in for Step 6b-residual-2.

**Cluster predicates carried from session 12 (clusters 1–5 — the Step 6c-ii predicate-table ADR will write these):**

- **Cluster 1 — Admin-side commands.** Explicit predicates: `create_employee_role`, `edit_employee_role`, `close_employee_role`, `change_employee_role_rate`, `create_project` → all `role ≥ admin`. `grant_user_role` / `revoke_user_role` are *parameterized* per ADR-0040 grant authority: `target ∈ {coordinator, auditor}` → `role ≥ admin`; `target ∈ {admin, superadmin}` → `role == superadmin`. **Class rule:** un-named admin-roster CRUD on {Employee, School, Contractor, User} → `role ≥ admin`.
- **Cluster 2 — Project lifecycle.** `close_project`, `cancel_project`, `reopen_project` (both forms) → `role ≥ coordinator`. Uniform. Pre-conditions (ADR-0032 closure gate, ADR-0038 project-state guards) live outside the auth predicate per locked clarification (2).
- **Cluster 3 — WA / WA Code / RFA.** `issue_wa`, `dismiss_wa_code`, `submit_rfa`, `approve_rfa` (manual path), `reject_rfa` (manual path), `withdraw_rfa` → `role ≥ coordinator`. WAAuthorization is composite-key-only, no commands. **Class-rule pattern:** the predicate-table ADR has two row types — explicit per-command rows for ADR-named commands, plus class-rule clauses for unnamed commands grouped by entity scope.
- **Cluster 4 — Sample Batch / Document / Deliverable / DepFiling / Time Entry.** `create_sample_batch`, `edit_sample_batch_composition`, `relink_sample_batch_wa_code`, `edit_document_scope`, `submit_deliverable`, `approve_deliverable` (manual path), `reject_deliverable` (manual path), `withdraw_deliverable` → all `role ≥ coordinator`. Per-`document_type` lifecycle dispatch commands (ADR-0024), Time Entry CRUD, and DepFiling CRUD + `edit_dep_filing_required_doc_types` fall under class rule. (`split_entry` is named in cluster 7 and gets its own explicit row.)
- **Cluster 5 — Note / blocker.** `create_note`, `dismiss_blocker`, `comment_blocker` → `role ≥ coordinator`. **`edit_note` non-uniform:** predicate is `caller == note.created_by` (relationship-based, orthogonal to linear-hierarchy propagation — even superadmin cannot edit other users' notes).

**Restructure session backlog (Step 6c-iii — extended session 14):**

Surfaced during the WAAuthorization naming discussion. User pushed back on three points: (a) WA Code instance vs. the underlying code-type *config* are different things — codes are static enough to be code-side configuration; (b) reassignment is *not* rare — amendments are routine (2–3 per WA) and inter-project WA shuffling is exactly the disorder this app mitigates; (c) WA's contractual lifecycle is independent of project assignment — "this WA was issued for this project" is a reconciliation between two independent histories. Backlog items: (1) introduce **WABundle** entity (working name) parallel to Project — SCA's contractual identity, WA chain + line items, WA Codes live on the bundle; the bundle gets *assigned* to a project. (2) **WACodeConf** as code-side static config for code types. (3) Rename **WAAuthorization** → likely `WACodeAssignment` (post-MVP budget priority). (4) **`reassign_wa_project(wa, new_project, move_work: bool)`** compound — `move_work` flag controls whether related Time Entries / Sample Batches follow the WA; default TBD. (5) **Time Entry / Sample Batch keep direct `project_id`** (settled session 12) — empirical-truth principle. (6) Post-MVP priorities locked: (a) budget tracking on WACodeAssignment, (b) draft invoice generation. **ADR amendments expected at 6c-iii:** ADR-0020, ADR-0027, ADR-0030, ADR-0031, ADR-0041. Mis-attribution `reassign_wa_project` carry-forward folds in here. **Session-14 addition (item 6) — WA Code removal model:** `dismiss_wa_code` narrowed to `expected`/`pending_rfa` → `dismissed` (no hard-delete, optional `reason_text` → `audit_reason` Note); new `removed` terminal for issued-code removal; RFA becomes a hybrid instrument (`add`/`remove`/`budget` line-item types, additions system-derived + removals coordinator-authored, `approve_rfa` composition `(prior ∪ adds) \ removes`); third WA origin identified (SCA-direct corrected amendment, needs diff-based reconciliation); shared removal cascade across three triggers. Touchpoints: ADR-0027/0029/0030/0031/0033. Step 6b-residual-2's item 5 (WA-Code-scoped Document orphan cascade) dissolved here. This addition likely pushes 6c-iii past one window — Case 2 sizing when it is reached. Full brief in `steps.md` → Step 6c-iii.

**Cumulative tables — ADR-locked through ADR-0043.** ADR-0043 (Step 6c-iv-a) adds the Contract entity, reflected in the tables below: the entity roster grows 18 → 19; Contract joins the audit-log history tier and the soft-delete delete-policy tier; the vocabulary gains Contract and `code_flat_fee_schedule`. No state-machine, pattern-menu, or role changes — Contract has no state machine (validity derived from dates), and the EmployeeRole / WA Code retrofit is Step 6c-iv-b.

**Per-`document_type` assignments (cumulative):**

| Pattern | document_types |
|---|---|
| Simple `missing → saved` | ACP13, ACP7, ACP15, ACP21, Emergency Notification, ACP8, VAR9 (all DepFiling docs — issued externally); COC; Daily Log |
| Cycling-family | CPR (RFA/RFP fork, 5 dates), FAMR (single-step review) |
| Bespoke | Lab Report (3 states: `missing`, `saved`, `invalid`; 4 transitions including `saved → invalid` for coordinator-discovered errors and `invalid → saved` for amended reports); RFP (4 states: `missing`, `saved`, `rejected`, `withdrawn`; SCA closure-receipt artifact per ADR-0037; `rejected` and `withdrawn` terminal; no `invalid` path since RFPs are SCA-side) |

**Entity roster (19 entities):**

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
| 15 | Note | Polymorphic commentary; typed reference to any entity OR history record (ADR-0040). Subtypes `regular | blocker | resolution | audit_reason | write_off` (ADR-0032, ADR-0040, ADR-0042). `authorship_class: 'user' | 'system'` + nullable `created_by`. Inter-Note `references` field. Regular Notes are creator-editable per ADR-0018; blocker, resolution, audit_reason, write_off Notes are immutable. Not deletable. |
| 16 | DepFiling | TRU-numbered regulatory filing bundle (ADR-0023). Project-scoped; editable `required_doc_types` set; Document-derivation source. No lifecycle. |
| 17 | WAAuthorization | Associative entity for WA ↔ WA Code M:N. Composite key `(wa_id, wa_code_id)`. No additional fields in MVP; gains budget when budget tracking lands. (ADR-0041) |
| 18 | ContractorEngagement | Associative entity for WA ↔ Contractor M:N with stint state. `(wa_id, contractor_id, started_at, ended_at?)`. Multiple rows per `(wa_id, contractor_id)` permitted when contractor closes CPR filing and is re-added. CPR Document derives per row. (ADR-0041) |
| 19 | Contract | Contractual basis a project is opened against (ADR-0043). Schema: `contract_number` (uniqueness-constrained natural key), `start_date` / `end_date?`, `code_flat_fee_schedule` (inline non-temporal `{code_type, fee}` collection), optional `name` (null → derived display label `C` + last 5 chars of `contract_number`). No state machine — `pending` / `active` / `expired` derived from dates. Audit log; soft delete. Employee rates are FK-side (EmployeeRole gains `contract_id` in 6c-iv-b); code default flat fees inline here. `Project → Contract` M:1 mandatory, immutable in MVP. |

Values / lookups (not entities): Sample Type, Sample Subtype, Project Type, TAT options, status enums, `document_type` registry, DepFiling template constants.

**Per-entity history-pattern assignments:**

| Pattern | Entities |
|---|---|
| Comprehensive capture | Document, WA, RFA |
| Lifecycle capture | Project, Sample Batch, Deliverable, EmployeeRole, WA Code, ContractorEngagement |
| Audit log | Employee, User, Time Entry, Contractor, DepFiling, Contract |
| No history | School, Note, UserRole, WAAuthorization |

**Per-entity delete policy:**

| Policy | Entities | Notes |
|---|---|---|
| Soft delete (guarded hard-delete eligible) | Document, WA, RFA, Project, Sample Batch, Deliverable, EmployeeRole, Employee, User, Time Entry, Contractor, WA Code, DepFiling, ContractorEngagement, Contract | History-carrying or referenced by history records. |
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
14. **Write-off / default-resolution.** An entity that exists but should not count (toward billing, conflicts) is excluded by an immutable `write_off` Note carrying a reason, rather than deleted or mutated; derived predicates compute over not-written-off entities, so exclusion dissolves the conditions the entity participated in. Produced by a guarded, coordinator-initiated **default-resolution** command (the nuclear option for resolving a blocker — mandatory justification, never auto-invoked) or as a reason-inheriting cascade of another command. Reversible only by an explicit superseding command (`revoke_write_off`). Subsumes pattern #10 (`wasted` is now an instance). (ADR-0042)

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
- **Wasted** — a derived reporting *label* for a written-off Deliverable (ADR-0042 reframe of ADR-0029): the Deliverable's WA Code was dismissed/removed after documents were prepared or a submission attempted. No longer an independently-derived flag — "wasted" ⟺ the Deliverable has a `write_off` Note. Entity stays in its current state.
- **Limbo chain** — WA `pending` → WA Code `expected` → Deliverable `pending_rfa`. Resolves atomically when `issue_wa` fires.
- **Blocker** — A structural condition (registry entry from ADR-0032) or user-flagged Note declaring something is held up. Every registry blocker has a structural-fix path; the ADR-0042 reframe replaces the dismissable/fix-only binary with the derived property **has-default-resolution** vs. **fix-only** (per-blocker classification pass is session 14b).
- **Materialized blocker** — A blocker that exists as a persisted Note record (vs purely-derived, registry-only). System-derived blockers materialize on first user engagement.
- **Engagement** — A coordinator writing a comment about a blocker or dismissing it. The trigger for lazy materialization of system-derived blockers.
- **Chain-dismissal** — When dismissing one blocker structurally causes another's condition to fire, the secondary is materialized as already-dismissed atomically. Linked via the resolution Note's `references` field. Under ADR-0042 the secondary's resolution now also emits `write_off` Notes for the affected entities.
- **Write-off / written-off** — an entity that exists and is retained (audit-preserved) but does not count toward billing aggregation or blocker/conflict derivation. Recorded by an immutable `write_off` Note on the entity carrying a `reason`; "written off" is a derived status (`∃ write_off Note not superseded by a `revoke_write_off`). A marker orthogonal to state machines. Subsumes the retired `non_billable` flag. (ADR-0042)
- **Default-resolution** — a guarded, coordinator-initiated command that resolves a blocker by writing off the conflicting entities (so the blocker's predicate, computed over not-written-off entities, stops holding). The "nuclear option" alongside the always-available structural-fix path: never auto-invoked, requires a mandatory justification. A blocker **has-default-resolution** iff a coherent one exists — the coherence test: the condition dissolves by *excluding* a well-defined entity set, not by *creating/correcting* something. (ADR-0042)
- **Cascade write-off** — a write-off produced as a side effect of a non-default-resolution command (e.g. `dismiss_wa_code` nulling `wa_code` on referencing records). Not separately guarded; inherits its `reason` from the initiating command — the reason the write-off model admits non-blocker reasons. (ADR-0042)
- **`revoke_write_off`** — explicit command that lifts a write-off by writing an immutable superseding Note (Notes are not deletable); re-includes the entity in billing and blocker-derivation. Command shape is a carry-forward. (ADR-0042)
- **`resolution_kind`** — discriminator on resolution Notes; under ADR-0042 the value set is `structural_fix | default_resolution | dismissal`, where `dismissal` is retained only for free-form user-flagged blockers (registry blockers resolve via `structural_fix` or `default_resolution`).
- **On-site range / off-site sub-interval (Time Entry)** — `on_site_range` is the parent range of an entry; `off_site_sub_intervals` are project-committed time-away spans within the on-site range (currently always lab delivery). Sub-intervals are pairwise disjoint, entirely within on-site range, positive-duration. (ADR-0034)
- **Gross on-site range** — the full `on_site_range` of a Time Entry, inclusive of off-site sub-intervals. Represents *project commitment*. Used by the cross-project overlap predicate (ADR-0028 amendment).
- **Net on-site time** — `on_site_range` minus the union of off-site sub-intervals. Represents *physical presence at the parent project's site*. Used by blocker #9 (sample collection coverage).
- **RFP (project-level)** — Request for Payment. SCA-generated document received when a project is submitted for payment; serves as the system-side closure receipt. New top-level `document_type` per ADR-0037, bespoke 4-state machine (`missing` / `saved` / `rejected` / `withdrawn`). One non-terminal RFP per project at any time. Distinct from CPR's internal RFP bucket (the contractor-side payment-request phase within the CPR cycling-family document) — same acronym, different schema level, different counterparty direction (SCA → us vs. contractor → us).
- **Non-terminal RFP** — an RFP in `missing` or `saved` state. The current open submission cycle for a project. Per-project invariant: exactly one at any time.
- **Terminal RFP** — an RFP in `rejected` or `withdrawn` state. Historical record of a closed-out submission cycle. Unbounded count per project (accumulates with each reopen-from-`closed` event).
- **Reopen-from-`closed` / reopen-from-`cancelled`** — the two `reopen_project` forms. From `closed`: requires `rfp_reason ∈ {rfp_rejected, rfp_withdrawn}`; cycles the RFP. From `cancelled`: pure state-flip; no structural reason captured (lifecycle capture + optional Note carry audit).
- **WAAuthorization** — associative entity for WA ↔ WA Code (composite key `(wa_id, wa_code_id)`, ADR-0041). Gains budget when budget tracking lands.
- **ContractorEngagement** — associative entity for WA ↔ Contractor with stint markers (`started_at`, `ended_at?`, ADR-0041). Multiple rows per `(wa_id, contractor_id)` allowed for repeat engagements; CPR derives per row.
- **Contract** — the contractual basis a project is opened against (ADR-0043). Carries a `contract_number` (uniqueness-constrained natural key), a `start_date` / `end_date?` term, an inline non-temporal `code_flat_fee_schedule`, and an optional `name`. No state machine — validity (`pending` / `active` / `expired`) is derived from the term + clock. Employee billing rates are contract-scoped FK-side (EmployeeRole gains `contract_id`, 6c-iv-b); code default flat fees are contract-defined inline. `Project → Contract` is M:1 mandatory, set at `create_project`, immutable in MVP.
- **`code_flat_fee_schedule` (Contract)** — an inline value collection of `{code_type, fee}` pairs on Contract: the default flat fee per WA code type for that contract. Non-temporal — fixed once for the contract's whole life. The code-type catalog itself (`WACodeConf`) is Step 6c-iii's work. (ADR-0043)
- **`audit_reason` (Note subtype)** — immutable Note subtype attached to history records via optional `reason_text` on grant/revoke commands (ADR-0040).
- **`amends_wa_id`** — RFA's mandatory direct typed reference to the WA being amended; set at auto-draft creation, immutable for RFA lifetime (ADR-0041).
- **`scope_type` / `scope_id` (Document)** — single-scope discriminator + FK on Document; `scope_type ∈ {project, deliverable, wa_code}` (ADR-0041).
- **`site_id` (Time Entry, Sample Batch)** — M:1 mandatory direct typed reference to School; the structural site-of-work link (ADR-0041).
- **`sampling_locations` (Sample Batch)** — optional plain-text field describing specific spots within the site where samples were collected (ADR-0041).
- **Derived/validated link** — a relationship resolved by lookup rather than FK. Used in ADR-0041 for Time Entry ↔ EmployeeRole: rate / blocker / closure-gate logic looks up the covering EmployeeRole row from `(employee_id, role_type, date)` at use time.

## Open questions

**For Step 6c-iv-b — contract-scoping retrofit (NEXT — Case 3 entry):**

- **Attachment model is settled (ADR-0043):** employee rates FK-side, code default flat fees inline on Contract's `code_flat_fee_schedule`. 6c-iv-b applies it — it does not re-open the Contract entity definition.
- **EmployeeRole contract-scoping.** EmployeeRole gains `contract_id`; disjoint-ranges invariant moves from per-`(employee, role_type)` to per-`(employee, role_type, contract)`; rate-resolution lookup gains the contract dimension (resolved Time Entry → project → contract); `change_employee_role_rate` (ADR-0039) dispatch keys on `(employee, role_type, contract)`. Amends ADR-0035 / 0039 / 0041.
- **WA Code default flat fee against contract.** Looked up by `code_type` + (project →) contract against Contract's `code_flat_fee_schedule`; defines the contract side that Step 6c-iii's `WACodeConf` inherits. Amends ADR-0020 / 0027.
- **Confirm blast-radius bound:** the code → required-docs / Deliverables / Sample-Batches derivation logic is unaffected (user-stated).

*(Step 6c-iv-a's open questions — attachment model, Contract attributes/identity, lifecycle/history/delete, Project → Contract wiring — are all resolved in ADR-0043. Session 14a's — binary reframe, write-off model, nuclear guard, vocab reconciliation — in ADR-0042.)*

**For session 14b — application (Step 6b-residual-2, enumerative half — deferred behind Step 6c-iv):**

- **11-blocker classification pass.** Each registry blocker: does a coherent default-resolution exist (→ has-default-resolution) or not (→ genuinely fix-only)? #10 (non-terminal RFP not `saved`) is the candidate lone survivor of the fix-only category.
- **Per-blocker default-resolution command definitions.** For each blocker with a default-resolution: define the command. Cross-project overlap is the worked example (split the overlapped span out of both Time Entries, write off the slivers).

**Deferred behind Step 6b-residual-2 and Step 6c-iv:**
- **Step 6c-ii predicate-table ADR write** — all seven predicate clusters are deliberated (see the carried-forward cluster blocks above); the per-`(role, command)` table is written *after* the reframe (14a/14b) and Step 6c-iv settle the command surface. STOP-AND-CONFIRM gate applies fully to the write.
- **`split_entry` command-shape** — predicate is `role ≥ coordinator` (explicit row in the predicate-table ADR); the command's actual shape (split point, re-assignment behavior) is undefined and has no natural home step. Candidate: Step 6d or a residual. ADR-0042 carry-forward — half-open interval semantics: Time Entry ranges are `[start, end)`; a boundary instant (and a sample collected at it) belongs to the entry *starting* at the boundary; gross duration is plain `end − start` (exclusive end is a limit, not "one unit prior"). Refines ADR-0034.
- **`revoke_write_off` command shape** — lifts a write-off via an immutable superseding Note (ADR-0042). Parameters and guards undefined; no home step yet (candidate: alongside `split_entry`).

**Carry-forwards worth re-checking when relevant:**
- **Mis-attribution `reassign_wa_project(wa, new_project, move_work)` compound** — part of Step 6c-iii restructure scope. Optional `move_work` flag forces explicit intent; default value TBD.
- **`reassign_project_contract` (post-MVP)** — compound to change a project's contract after creation; cascades rate resolution + flat-fee lookups across the project's work; `role >= admin`. In `post-mvp.md`. (ADR-0043 — `Project.contract_id` is immutable in MVP.)
- **ContractorEngagement command-shape** — `start_contractor_engagement` / `end_contractor_engagement` predicates are `role ≥ coordinator` (session 13); signatures + pre-conditions deferred to Step 6c-iii (ContractorEngagement is in that restructure's blast radius). Date defaults: `started_at` → row-creation date; `ended_at` → CPR-saved date (nullable).
- **Cross-project Sample Batch reassignment as a structured command**: in `post-mvp.md` alongside notifications.
- **Retroactive rate corrections via Time-Entry rate snapshot** (carry-forward from ADR-0035): reversible additive change post-MVP if signal emerges.
- **Security-immediate revoke runtime semantics** (session invalidation on `revoke_user_role`): implementation concern, deferred to auth implementation step.

**Carried forward (deferred to later steps):**
- **WACodeAssignment budget fields** (current name: WAAuthorization budget fields) — added when budget tracking design lands; immediate post-MVP per user signal.
- **Draft invoice generation against budgets** — second post-MVP priority.
- **Billing Rate entity/table** — temporal `(subtype, TAT) → rate` lookup. Likely Step 6d or later. Follows the temporal rate resolution template formalized in ADR-0035 / ADR-0041.
- **WA / WA Code / WAAuthorization rename + WABundle introduction** — Step 6c-iii (after the Step 6c-ii predicate-table ADR). Full backlog in the Restructure-session-backlog block of the Last session summary.
- **Quarantine as a per-entity violation-handling pattern** — excluded from history-pattern menu (ADR-0013); remains deferred per ADR-0011. Step 6d.
- **Bulk import file-upload relaxation** — 6b or implementation.
- **Project structure for managing N `document_types`** — defer to implementation phase.
- **History implementation shape** (event store, append-only tables, temporal tables) — Step 8.
- **Persistence isolation for cross-entity invariants** — Step 8.
- Whether existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

## Next session

**Step 6c-iv-b — Contract-scoping retrofit.** Step 6c-iv-a complete (ADR-0043 — Contract entity, Project → Contract, attachment model). Next is **6c-iv-b** — apply ADR-0043's attachment model: EmployeeRole gains `contract_id` + the disjoint-ranges invariant restructure; the WA Code default-flat-fee lookup; the blast-radius confirmation. **Case 3 entry** — scoped prompt below. Brief in `steps.md` → Step 6c-iv / Step 6c-iv-b.

### Prompt for the next session

> Resume work. Next is **Step 6c-iv-b — Contract-scoping retrofit**, a **Case 3 entry** (scoped). Per `_workflow.md` Case 3: read this prompt + Open questions, read `decisions.md` (ADR-0043 — the just-written Contract ADR — load-bearing; ADR-0035 / 0039 / 0041 for EmployeeRole + rate-change + relationships; ADR-0020 / 0027 for WA Code), then enter planning mode — draft a session plan in chat, wait for explicit approval. STOP-AND-CONFIRM gate applies fully; do not touch files until approved.
>
> **Why this step exists:** Step 6c-iv (Contract entity, new requirement 2026-05-14) was split Option A. 6c-iv-a (done — ADR-0043) introduced Contract and fixed the **attachment model**: employee rates FK-side, code default flat fees inline on Contract's `code_flat_fee_schedule`. **6c-iv-b is the application half** — it retrofits EmployeeRole and WA Code to that model.
>
> **Scope of 6c-iv-b (items 3 + 4 + 5 of the shared brief in `steps.md` → Step 6c-iv):**
> 1. **EmployeeRole contract-scoping** — EmployeeRole gains `contract_id`; the disjoint-ranges invariant moves from per-`(employee, role_type)` to per-`(employee, role_type, contract)` (an employee can hold the same role at different rates on different contracts, overlapping in time); the rate-resolution lookup gains the contract dimension (contract resolved Time Entry → project → contract); `change_employee_role_rate` (ADR-0039) dispatch keys on `(employee, role_type, contract)`. Amends ADR-0035 / 0039 / 0041.
> 2. **WA Code default flat fee** — looked up by `code_type` + (project →) contract against Contract's `code_flat_fee_schedule`; defines the contract side that Step 6c-iii's `WACodeConf` inherits. Amends ADR-0020 / 0027.
> 3. **Confirm blast-radius bound** — the code → required-docs / Deliverables / Sample-Batches derivation logic is unaffected (user-stated). Do not re-litigate.
>
> **Output:** the retrofit ADR (amends ADR-0035 / 0039 / 0041 / 0020 / 0027); updated cumulative tables (EmployeeRole entity row gains `contract_id` + the restructured invariant).
>
> **Out of scope of 6c-iv-b — do not pull in:** the Contract entity definition itself is settled by ADR-0043 — do not re-open it. Session 14b and the WA-removal work (Step 6c-iii item 6) are not part of Step 6c-iv.
>
> **Sequencing — do not lose this:** execution order is **session 14a (done — ADR-0042) → 6c-iv-a (done — ADR-0043) → 6c-iv-b → session 14b → Step 6c-ii predicate-table ADR → Step 6c-iii → Step 6d**. ADR numbers are assigned at write time — no pre-assignment. The Step 6c-ii predicate clusters are all deliberated (see the carried-forward cluster blocks in the Last session summary); that ADR is a write, gated behind 14b.
>
> **State machines locked through ADR-0043:**
> - With state machines: WA Code (6 states, ADR-0027), Deliverable (4 states, ADR-0029), WA (3 states, ADR-0030), RFA (5 states, ADR-0031), Lab Report `document_type` (3 states bespoke, ADR-0033), Project (3 states, ADR-0037), RFP `document_type` (4 states bespoke, ADR-0037).
> - Without state machines: EmployeeRole (temporal validity, ADR-0035), UserRole (row existence, ADR-0036), DepFiling (no lifecycle, ADR-0023), Sample Batch (stateless per ADR-0038), WAAuthorization (immutable, ADR-0041), ContractorEngagement (stint markers, ADR-0041), **Contract (validity derived from dates, ADR-0043)**, School / Note / User / Employee / Contractor.
> - *Not yet ADR-locked (session-14 deliberation, queued for Step 6c-iii item 6):* WA Code gains a `removed` state and `dismiss_wa_code` narrows to `expected`/`pending_rfa`. The 6-state count above is unchanged until 6c-iii writes it.
>
> **Roster:** 19 entities through ADR-0043 (Contract is #19).
> **Roles (ADR-0040):** superadmin / admin / coordinator / auditor; linear hierarchy emergent from explicit `(role, command) → permitted?` table.
> **Pattern menu:** 14 design patterns cumulative through ADR-0042 (#14 — write-off / default-resolution). ADR-0043 added no pattern.
> **Blocker registry:** 11 entries; the ADR-0042 reframe replaces the dismissable/fix-only binary with `has-default-resolution | fix-only` — the per-blocker reclassification pass is session 14b.
> **Stack confirmed (no ADR yet, Step 8 will write):** backend Python/FastAPI/Ruff/SQLAlchemy/Pydantic/pytest; frontend Vite/React/TypeScript/TanStack Router/TanStack Query/openapi-ts/shadcn-ui/Storybook.
>
> **Process notes:**
> - Casual back-and-forth. Self-monitor context. One topic per turn.
> - STOP-AND-CONFIRM gate applies fully to all deliberations and to every ADR write.
> - Do not write to `domain-model.md` (that's Step 6d).
> - **Permission propagation rule:** adding a permission to a lower role propagates upward in the chain by default; non-chain changes require explicit user signal.
> - **Recommendation strength:** state confidence on recommendations; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).
> - **Session 14b and the WA-removal work (Step 6c-iii item 6) are not part of Step 6c-iv-b** — do not pull them in.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6a complete; Step 6b core complete; Step 6b-residual complete; Step 6c-i complete; Step 6c-ii deliberation complete sessions 12–13, predicate-table ADR write deferred; Step 6b-residual-2 session 14a complete — ADR-0042 write-off model — 14b application remaining; Step 6c-iv split Option A into 6c-iv-a + 6c-iv-b; **Step 6c-iv-a complete — ADR-0043 Contract entity + attachment model; Step 6c-iv-b (contract-scoping retrofit) next**, then 14b, then the Step 6c-ii predicate-table ADR, then Step 6c-iii rename+restructure+WA-removal-model, then Step 6d)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0043)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
