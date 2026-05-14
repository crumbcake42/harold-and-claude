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

**Step 6b-residual-2 sizing (session 14) — Case 2 entry: sized, split via Option A (14a model / 14b application); Fork 2 closed (item 5 dissolved). Large productive tangent — the `dismiss_wa_code` / WA-removal redesign — deliberated and captured into the Step 6c-iii brief. No ADRs written.**

Session 14 opened as the Case 2 entry for Step 6b-residual-2. The step tripped the fit checklist (Signal 3 — the brief itself flags >1 session), so it was split along the model/application dependency seam (**Option A**): **14a** = write-off model + binary reframe + nuclear guard + vocab reconciliation; **14b** = 11-blocker classification pass + per-blocker default-resolution commands. The split is written into `steps.md` → Step 6b-residual-2.

A productive tangent then dominated the session. Working the `dismiss_wa_code` cascade-shape question, the user surfaced that **RFAs can remove WA codes** — a missed use case. The redesign that followed (shape settled, no ADRs — it is deliberation queued for Step 6c-iii, now captured as Step 6c-iii item 6):
- **`dismiss_wa_code` narrowed** to `expected`/`pending_rfa` → `dismissed`; the `issued → dismissed` transition is dropped; it never hard-deletes (ADR-0027's delete-substitution is dropped — always transitions, even never-referenced codes; dismissed rows kept); optional `reason_text` → `audit_reason` Note (ADR-0040 pattern).
- **New `removed` terminal state** — `issued → removed`, for issued codes removed via an RFA removal line item or an SCA-direct corrected amendment.
- **RFA becomes a hybrid instrument** — line-item types `add | remove | budget`; additions stay system-derived, removals coordinator-authored; `approve_rfa` composition becomes `(prior ∪ adds) \ removes`; approve/reject/withdraw resolution is polymorphic on line-item type.
- **Third WA origin identified** — SCA-direct corrected amendment (externally-arrived amendment WA, no RFA behind it); needs diff-based reconciliation against the superseded WA. ADR-0030/0031 had enumerated only two origins.
- **Fork 2 (item 5) dissolved** — with the WA Code row kept on dismissal (not deleted), `wa_code`-scoped Documents never dangle, so there is no orphan cascade to design. Item 5 leaves Step 6b-residual-2 and folds into Step 6c-iii item 6 as a one-line confirmation.

No ADRs were written this session.

**Cluster predicates carried forward — clusters 6–7 (deliberated session 13):**

- **Cluster 6 — ContractorEngagement lifecycle.** `start_contractor_engagement`, `end_contractor_engagement` → `role ≥ coordinator`. Resolved as **named commands**, not implicit via CPR cycling-family lifecycle: the CPR Document *derives from* the engagement row (folding engagement into CPR lifecycle inverts the dependency); the timelines are independent (engagement can start before the CPR is drafted); multiple stints per `(wa_id, contractor_id)` need explicit open/close. Command-shape (signatures, pre-conditions) deferred to Step 6c-iii — ContractorEngagement sits in that restructure's blast radius. Date defaults captured for 6c-iii: `started_at` → row-creation date; `ended_at` → CPR-saved date (nullable, overridable).
- **Cluster 7 — Cross-project commands.** Two findings. (a) **No special cross-project predicate primitive needed.** The ADR-0040 carry-forward worried predicates might need to read "both projects' coordinator rosters," but MVP-flat (locked clarification 1) has no per-project rosters — plain `role ≥ coordinator` suffices. When per-project scoping lands post-MVP the qualifier is a localized edit. (b) **`split_entry` → explicit row, `role ≥ coordinator`.** It's ADR-0028-named and structurally not-CRUD (one record becomes two); its command-shape is undefined and carried forward — no natural home step (candidate: Step 6d or a residual). **Correction logged:** the session-12 handoff/prompt's "cross-project overlap dismissal (ADR-0028 family)" framing was wrong — blocker #8 is fix-only, there is no dismissal command. (The Step 6b-residual-2 reframe revisits this regardless.)

**Blocker-resolution model reframe — Step 6b-residual-2, sized & split (session 14):**

Step 6b-residual-2 replaces ADR-0032's fix-only/dismissable binary with the `write-off` model (every blocker has a fix path plus, where coherent, a **default-resolution** command that writes off the conflicting entities). Sized session 14 as a Case 2 entry and split via **Option A** into **14a** (write-off model + binary reframe + nuclear guard + vocab reconciliation) and **14b** (11-blocker classification pass + per-blocker default-resolution commands). New test for the binary: "does a coherent default-resolution exist?" — expected to shrink rather than vanish, with #10 (non-terminal RFP not `saved` at closure) the candidate lone fix-only survivor. Session-14 note: a write-off's reason is not always blocker-registry-derived (an `expected`-code abandonment via `dismiss_wa_code` produces one) — the 14a model must allow non-blocker reasons. Full brief in `steps.md` → Step 6b-residual-2.

**`write-off` term — locked (session 13):**

`write-off` / `written-off` is the locked umbrella term for the accept-path exclusion: an entity that exists but doesn't count (toward billing/conflicts). It **carries a reason**, drawn from the blocker registry (which blocker's default-resolution produced the write-off) — audit/reporting-useful. `write-off` likely **subsumes `non_billable`** (ADR-0027). It does **not** replace `wasted` (ADR-0029 Deliverable derived flag) or `invalid` (ADR-0033 Lab Report state) — those are distinct concepts at different structural levels, not write-off reason-codes; whether they fold in at all is a Step 6b-residual-2 question, not settled. Runner-up term rejected: `excluded` (vaguer — excluded from *what*).

**Locked clarifications carried from session 12 (still binding for ADR-0042):**

1. **Project-scoped predicate form is MVP-flat: plain `role ≥ coordinator`.** No `assigned_to(project)` qualifier in MVP — per-project coordinator scoping is post-MVP per ADR-0040. Adding the qualifier later is a localized edit to project-scoped rows.
2. **Project-state immutability (ADR-0038 pattern #13) stays a pre-condition, NOT in the auth predicate.** Target-state-based, not caller-based; conflating muddies the static-analysis story ADR-0012 cites.
3. **No system-caller primitive in the predicate vocabulary.** Cascade effects inherit auth from the user-facing command that initiated them. The predicate table enumerates user-facing commands only.
4. **`dismiss_wa_code` cascade-shape question stays scope-flagged.** ADR-0042 predicates the user-facing `dismiss_wa_code` command only; cascade-shape design is now a candidate fold-in for Step 6b-residual-2.

**Cluster predicates carried from session 12 (clusters 1–5 — ADR-0042 will write these):**

- **Cluster 1 — Admin-side commands.** Explicit predicates: `create_employee_role`, `edit_employee_role`, `close_employee_role`, `change_employee_role_rate`, `create_project` → all `role ≥ admin`. `grant_user_role` / `revoke_user_role` are *parameterized* per ADR-0040 grant authority: `target ∈ {coordinator, auditor}` → `role ≥ admin`; `target ∈ {admin, superadmin}` → `role == superadmin`. **Class rule:** un-named admin-roster CRUD on {Employee, School, Contractor, User} → `role ≥ admin`.
- **Cluster 2 — Project lifecycle.** `close_project`, `cancel_project`, `reopen_project` (both forms) → `role ≥ coordinator`. Uniform. Pre-conditions (ADR-0032 closure gate, ADR-0038 project-state guards) live outside the auth predicate per locked clarification (2).
- **Cluster 3 — WA / WA Code / RFA.** `issue_wa`, `dismiss_wa_code`, `submit_rfa`, `approve_rfa` (manual path), `reject_rfa` (manual path), `withdraw_rfa` → `role ≥ coordinator`. WAAuthorization is composite-key-only, no commands. **Class-rule pattern:** ADR-0042 has two row types — explicit per-command rows for ADR-named commands, plus class-rule clauses for unnamed commands grouped by entity scope.
- **Cluster 4 — Sample Batch / Document / Deliverable / DepFiling / Time Entry.** `create_sample_batch`, `edit_sample_batch_composition`, `relink_sample_batch_wa_code`, `edit_document_scope`, `submit_deliverable`, `approve_deliverable` (manual path), `reject_deliverable` (manual path), `withdraw_deliverable` → all `role ≥ coordinator`. Per-`document_type` lifecycle dispatch commands (ADR-0024), Time Entry CRUD, and DepFiling CRUD + `edit_dep_filing_required_doc_types` fall under class rule. (`split_entry` is named in cluster 7 and gets its own explicit row.)
- **Cluster 5 — Note / blocker.** `create_note`, `dismiss_blocker`, `comment_blocker` → `role ≥ coordinator`. **`edit_note` non-uniform:** predicate is `caller == note.created_by` (relationship-based, orthogonal to linear-hierarchy propagation — even superadmin cannot edit other users' notes).

**Restructure session backlog (Step 6c-iii — extended session 14):**

Surfaced during the WAAuthorization naming discussion. User pushed back on three points: (a) WA Code instance vs. the underlying code-type *config* are different things — codes are static enough to be code-side configuration; (b) reassignment is *not* rare — amendments are routine (2–3 per WA) and inter-project WA shuffling is exactly the disorder this app mitigates; (c) WA's contractual lifecycle is independent of project assignment — "this WA was issued for this project" is a reconciliation between two independent histories. Backlog items: (1) introduce **WABundle** entity (working name) parallel to Project — SCA's contractual identity, WA chain + line items, WA Codes live on the bundle; the bundle gets *assigned* to a project. (2) **WACodeConf** as code-side static config for code types. (3) Rename **WAAuthorization** → likely `WACodeAssignment` (post-MVP budget priority). (4) **`reassign_wa_project(wa, new_project, move_work: bool)`** compound — `move_work` flag controls whether related Time Entries / Sample Batches follow the WA; default TBD. (5) **Time Entry / Sample Batch keep direct `project_id`** (settled session 12) — empirical-truth principle. (6) Post-MVP priorities locked: (a) budget tracking on WACodeAssignment, (b) draft invoice generation. **ADR amendments expected at 6c-iii:** ADR-0020, ADR-0027, ADR-0030, ADR-0031, ADR-0041. Mis-attribution `reassign_wa_project` carry-forward folds in here. **Session-14 addition (item 6) — WA Code removal model:** `dismiss_wa_code` narrowed to `expected`/`pending_rfa` → `dismissed` (no hard-delete, optional `reason_text` → `audit_reason` Note); new `removed` terminal for issued-code removal; RFA becomes a hybrid instrument (`add`/`remove`/`budget` line-item types, additions system-derived + removals coordinator-authored, `approve_rfa` composition `(prior ∪ adds) \ removes`); third WA origin identified (SCA-direct corrected amendment, needs diff-based reconciliation); shared removal cascade across three triggers. Touchpoints: ADR-0027/0029/0030/0031/0033. Step 6b-residual-2's item 5 (WA-Code-scoped Document orphan cascade) dissolved here. This addition likely pushes 6c-iii past one window — Case 2 sizing when it is reached. Full brief in `steps.md` → Step 6c-iii.

**Cumulative tables remain ADR-locked through ADR-0041** — no entity / pattern / vocabulary changes landed as ADRs this session (`write-off` is chat-locked but its model is Step 6b-residual-2's output, so it is not yet in the cumulative vocabulary table). Tables below carry forward unchanged.

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

**For session 14a — write-off model (Step 6b-residual-2, model half):**

- **Reframe the fix-only/dismissable binary — abstract.** New test: "does a coherent default-resolution exist?" not "is there a real-world acceptance path?" Decide the reframed binary structure. Do NOT do the per-blocker classification pass — that is 14b.
- **Formalize the `write-off` model.** Umbrella state/concept: an entity that exists but doesn't count (toward billing/conflicts), carrying a **reason**. The reason is not always blocker-registry-derived (see Last session summary) — the model must allow non-blocker reasons.
- **Nuclear-option guard shape.** Default-resolutions are destructive; the guard — require a justification Note (ADR-0032 dismissal-Note precedent), never auto-invoke. Confirm shape.
- **`write-off` vs. existing vocab.** Confirm `write-off` subsumes `non_billable` (ADR-0027); decide whether `wasted` (ADR-0029) / `invalid` (ADR-0033) fold in or stay distinct.

**For session 14b — application (Step 6b-residual-2, enumerative half):**

- **11-blocker classification pass.** Each registry blocker: does a coherent default-resolution exist (→ has-default-resolution) or not (→ genuinely fix-only)? #10 (non-terminal RFP not `saved`) is the candidate lone survivor of the fix-only category.
- **Per-blocker default-resolution command definitions.** For each blocker with a default-resolution: define the command. Cross-project overlap is the worked example (split the overlapped span out of both Time Entries, write off the slivers).

**Deferred behind Step 6b-residual-2:**
- **ADR-0042 write** — all seven predicate clusters are deliberated (see Last session summary); the per-`(role, command)` table is written *after* the reframe settles the command surface. STOP-AND-CONFIRM gate applies fully to the write.
- **`split_entry` command-shape** — predicate is `role ≥ coordinator` (explicit row in ADR-0042); the command's actual shape (split point, re-assignment behavior) is undefined and has no natural home step. Candidate: Step 6d or a residual.

**Carry-forwards worth re-checking when relevant:**
- **Mis-attribution `reassign_wa_project(wa, new_project, move_work)` compound** — part of Step 6c-iii restructure scope. Optional `move_work` flag forces explicit intent; default value TBD.
- **ContractorEngagement command-shape** — `start_contractor_engagement` / `end_contractor_engagement` predicates are `role ≥ coordinator` (session 13); signatures + pre-conditions deferred to Step 6c-iii (ContractorEngagement is in that restructure's blast radius). Date defaults: `started_at` → row-creation date; `ended_at` → CPR-saved date (nullable).
- **Cross-project Sample Batch reassignment as a structured command**: in `post-mvp.md` alongside notifications.
- **Retroactive rate corrections via Time-Entry rate snapshot** (carry-forward from ADR-0035): reversible additive change post-MVP if signal emerges.
- **Security-immediate revoke runtime semantics** (session invalidation on `revoke_user_role`): implementation concern, deferred to auth implementation step.

**Carried forward (deferred to later steps):**
- **WACodeAssignment budget fields** (current name: WAAuthorization budget fields) — added when budget tracking design lands; immediate post-MVP per user signal.
- **Draft invoice generation against budgets** — second post-MVP priority.
- **Billing Rate entity/table** — temporal `(subtype, TAT) → rate` lookup. Likely Step 6d or later. Follows the temporal rate resolution template formalized in ADR-0035 / ADR-0041.
- **WA / WA Code / WAAuthorization rename + WABundle introduction** — Step 6c-iii (after ADR-0042). Full backlog in Last session summary.
- **Quarantine as a per-entity violation-handling pattern** — excluded from history-pattern menu (ADR-0013); remains deferred per ADR-0011. Step 6d.
- **Bulk import file-upload relaxation** — 6b or implementation.
- **Project structure for managing N `document_types`** — defer to implementation phase.
- **History implementation shape** (event store, append-only tables, temporal tables) — Step 8.
- **Persistence isolation for cross-entity invariants** — Step 8.
- Whether existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

## Next session

**Step 6b-residual-2 / session 14a — write-off model.** The model half of the Option A split (see Last session summary): formalize the `write-off` model, reframe the fix-only/dismissable binary (abstract), specify the nuclear-option guard, reconcile vocab against `non_billable` / `wasted` / `invalid`. This is a **Case 3 entry** — scoped prompt below.

### Prompt for the next session

> Resume work. Next is **Step 6b-residual-2 / session 14a — write-off model**, the model half of the Option A split agreed session 14. This is a **Case 3 entry** — scoped below; read `steps.md` → Step 6b-residual-2 (the Session partition block) for the full split rationale.
>
> **Why this step exists:** Step 6c-ii session 13, working cluster 7 (cross-project commands), surfaced that ADR-0032's **fix-only/dismissable binary is partly dishonest** — a mechanical acceptance path always exists (mutate the conflicting data until the derived condition dissolves), and ADR-0028 calling cross-project overlap "fix-only" just pushed that mutation off-system into manual edits. The fix: bring it on-system as a defined per-blocker **default-resolution** command.
>
> **Scope of 14a (the conceptual half — NOT the 11-blocker pass, that is 14b):**
> 1. **Reframe the fix-only/dismissable binary — abstract.** New test: not "is there a real-world acceptance path?" but "does a coherent default-resolution exist?" Decide the reframed binary structure (expected to shrink, not vanish — #10, non-terminal RFP not `saved` at closure, is the candidate lone fix-only survivor: the saved RFP *is* what closure means; no entity to write off). Do NOT do the per-blocker classification pass — that is 14b.
> 2. **Formalize the `write-off` model.** `write-off` / `written-off` (term locked session 13) = umbrella state/concept: an entity that exists but doesn't count (toward billing/conflicts). Carries a **reason**. Session-14 finding: the reason is NOT always blocker-registry-derived — an `expected`-code abandonment via `dismiss_wa_code` produces a write-off with reason "code abandoned pre-issuance," not a blocker. The model must allow non-blocker reasons.
> 3. **Nuclear-option guard.** Default-resolutions are destructive; guard them — require a justification Note (ADR-0032 dismissal-Note precedent), never auto-invoke. Confirm shape.
> 4. **Vocab reconciliation.** `write-off` likely subsumes `non_billable` (ADR-0027); decide whether `wasted` (ADR-0029) / `invalid` (ADR-0033 Lab Report state) fold in or stay distinct.
>
> **Out of scope for 14a (→ 14b):** the one-by-one classification pass over all 11 registry blockers; per-blocker default-resolution command definitions.
>
> **Outputs:** an ADR (or the model-half of one) for the `write-off` model + binary reframe + nuclear guard; likely a vocab-reconciliation amendment to ADR-0027. The registry reclassification and per-blocker commands wait for 14b. Updated cumulative tables in `handoff.md` as needed (vocabulary; the pattern menu may gain a 14th entry — write-off / default-resolution).
>
> **Sequencing — do not lose this:** Execution order is **14a → 14b → ADR-0042 write (closes Step 6c-ii) → Step 6c-iii (rename + restructure) → Step 6d**. ADR-0042's predicate deliberation is *already done* — all seven clusters agreed in chat (clusters 1–5 session 12, clusters 6–7 session 13; see carried-forward cluster predicates above). ADR-0042 is purely a write, gated behind 14a+14b because the reframe adds a default-resolution command family ADR-0042 must enumerate.
>
> **State machines locked through ADR-0041:**
> - With state machines: WA Code (6 states, ADR-0027), Deliverable (4 states, ADR-0029), WA (3 states, ADR-0030), RFA (5 states, ADR-0031), Lab Report `document_type` (3 states bespoke, ADR-0033), Project (3 states, ADR-0037), RFP `document_type` (4 states bespoke, ADR-0037).
> - Without state machines: EmployeeRole (temporal validity, ADR-0035), UserRole (row existence, ADR-0036), DepFiling (no lifecycle, ADR-0023), Sample Batch (stateless per ADR-0038), WAAuthorization (immutable, ADR-0041), ContractorEngagement (stint markers, ADR-0041), School / Note / User / Employee / Contractor.
> - *Not yet ADR-locked (session-14 deliberation, queued for Step 6c-iii item 6):* WA Code gains a `removed` state and `dismiss_wa_code` narrows to `expected`/`pending_rfa`. The 6-state count above is unchanged until 6c-iii writes it.
>
> **Roster:** 18 entities through ADR-0041.
> **Roles (ADR-0040):** superadmin / admin / coordinator / auditor; linear hierarchy emergent from explicit `(role, command) → permitted?` table.
> **Pattern menu:** 13 design patterns cumulative through ADR-0038 — the reframe may add a 14th (write-off / default-resolution).
> **Blocker registry:** 11 entries through ADR-0041 — this step reclassifies them.
> **Stack confirmed (no ADR yet, Step 8 will write):** backend Python/FastAPI/Ruff/SQLAlchemy/Pydantic/pytest; frontend Vite/React/TypeScript/TanStack Router/TanStack Query/openapi-ts/shadcn-ui/Storybook.
>
> **Process notes:**
> - Casual back-and-forth. Self-monitor context. One topic per turn.
> - STOP-AND-CONFIRM gate applies fully to all reframe deliberations and to every ADR write.
> - Do not write to `domain-model.md` (that's Step 6d).
> - **Permission propagation rule:** adding a permission to a lower role propagates upward in the chain by default; non-chain changes require explicit user signal.
> - **Recommendation strength:** state confidence on recommendations; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).
> - **Session 14's WA-removal work is captured in `steps.md` → Step 6c-iii item 6** — not part of 14a; do not re-deliberate it.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6a complete; Step 6b core complete; Step 6b-residual complete; Step 6c-i complete; Step 6c-ii deliberation complete sessions 12–13, ADR-0042 write deferred; Step 6b-residual-2 sized & split session 14 — Option A: 14a write-off model next, then 14b application; then ADR-0042 write closes 6c-ii; Step 6c-iii rename+restructure+WA-removal-model after; Step 6d after)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0041)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
