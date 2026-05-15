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

**Session 16 — Step 6c-iii-b-i ADR write. ✓ COMPLETE (2026-05-15, ADR-0048).** Case-2 sized parent Step 6c-iii-b at session head (signals 1, 3, 5 fired) → split along the item-cluster seam into **6c-iii-b-i** (items 1–5, restructure surface — this session) + **6c-iii-b-ii** (item 6, WA Code removal model — next session). Substantive deliberation across items 1, 2, 4, 5; rename (item 3) settled quickly.

**ADR-0048 — WABundle restructure surface: WA Code reparenting onto bundle, single-table `level` discriminator, project derivation through `wa_code`, WABundle.sites invariant, WACodeAssignment rename, code-side WACodeConf.** Six coupled decisions:

1. **WA Code reparented onto WABundle.** `WACode.wabundle_id` (M:1 required) replaces `WACode.project_id`. WA Code → Project becomes derived (`WA Code → WABundle → Project`). Contract-resolution path shortens from `code → project → WABundle → contract` to `code → WABundle → contract`.
2. **Single-table `WACode` with explicit `level` discriminator.** Two flavors — **project-level** (e.g., supervision) + **building-level** (e.g., asbestos sampling at school X; sample-collection codes are one species) — share the entire WA Code substrate. Modelled as one table with `level: enum('project','building')` (required, non-default) and a nullable `school_id`. DB CHECK couples them: `level = 'building' ⟺ school_id IS NOT NULL`. The single-vs-two-table fork emerged in chat (user's nervousness on naked-nullable-as-discriminator was tracking the implicit-discriminator smell); explicit `level` dissolves it.
3. **WABundle gains `sites` (M:N → School) via WABundleSite — new associative entity, roster #21.** Building-level WA Codes constrained `school_id ∈ wabundle.sites`. Sites are *intentionally curated* (not auto-grown from code creation), so the school-subset guard on `reassign_wa_project` has real bite. `create_project` (ADR-0044 compound) gains a `sites: [School]` parameter; `edit_wabundle` (`role >= admin`) gains site management — add unconditionally; remove guarded (fails if any WA Code under the bundle references that school).
4. **TE / SB drop direct `project_id`; project derives through `wa_code → WACode → WABundle → Project`.** Substantive reframe of brief's item 5 — calibration had it as mechanical confirmation; user pushback at calibration reframed it as the load-bearing decision. The historical fact on TE / SB is `(employee, date, site)`; project is a downstream organizational fact. **Cascade-keep-FK principle** stated here as the direct consequence: the `dismiss_wa_code` / removal cascade (ADR-0042 / ADR-0046) no longer nulls `wa_code` on referencing TE / SB — it keeps the reference (now pointing at a `dismissed` / `removed` code, which still resolves bundle → project) and emits a `write_off` Note on the referencing record. With WABundle always present (ADR-0044) + missing-derived auto-generation (ADR-0022), **`wa_code = null` becomes unproducible**; **blockers #1 (TE `wa_code = null`) and #2 (SB `wa_code = null`) become unfireable predicates**. Formal registry removal + full cascade mechanics deferred to 6c-iii-b-ii's ADR.
5. **`WACodeConf` as code-side static config** (Python module / dataclass list). Minimum entry: `code_type_id`, `name`, `default_level`. Empirical churn rate is rare (session-12 user signal); DB-entity machinery (admin CRUD, history, seeding) doesn't earn its keep in MVP. `WACode.level` denormalized from `WACodeConf[code_type].default_level` at creation, fixed thereafter. Migration to DB entity remains a future option if churn rises (`code_type_id` keys are stable across the migration).
6. **`WAAuthorization` → `WACodeAssignment` (shorthand WACA).** Naming-only rename — M:N composite key `(wa_id, wa_code_id)` unchanged; future budget tracking lands on this entity. All prior ADR references to WAAuthorization read as WACodeAssignment going forward.
7. **`reassign_wa_project(wa, new_project)` interface + school-subset guard.** `move_work` flag dissolved — under project-derivation, TE / SB referencing the WA's codes automatically inherit the new project via their `wa_code` reference. Guard: `moving_wa.codes.school_id ⊆ target_project.wabundle.sites` (building-level only; project-level codes have null school and are unconstrained). Predicate inherits ADR-0047 Cluster 3 class rule (`role >= coordinator`). Deep mechanics (version_seq integration in target chain, source-bundle gap handling, single-WA-only-in-bundle edge case, audit-trail shape) deferred to implementation phase — interface + guard + work-follows principle are fixed; bookkeeping is not.
8. **v0 in-place issuance (Fork B) clarified.** ADR-0030's `pending → issued` for v0 operates in-place; no new WA row at initial issuance. ADR-0044's per-version-date-fields language was already implicit in-place; restated explicitly. Audit captured by WA's comprehensive-capture history pattern.

**Reframes vs. brief (worth noting):**
- Item 5 expected mechanical → became the load-bearing decision (project-derivation through wa_code).
- Item 1 expected mechanical → needed coupled fork on single-table-with-discriminator + WABundle.sites declaration.
- Item 4 simplified — `move_work` flag dissolved as a direct consequence of (4).
- `WACodeState` was floated as a rename alternative; rejected (overloads "state" with WA Code's own state machine; loses budget-direction signal).

**Amendments touched:** ADR-0020 (WA Code scoping + `level` / `school_id`), ADR-0027 (cascade step 2 retired — full restate in 6c-iii-b-ii), ADR-0030 (v0 in-place issuance clarified), ADR-0041 (rename + relationship-table refresh), ADR-0042 / ADR-0046 (cascade-keep-FK principle; full mechanics in 6c-iii-b-ii), ADR-0044 (WABundle.sites + WABundleSite + `create_project` signature + `edit_wabundle` site management), ADR-0045 (contract-resolution path shortens).

**Entity roster 20 → 21.** WABundleSite added (associative entity, ADR-0041 convention). WA Code gains `level` + `school_id?`. WAAuthorization renamed WACodeAssignment (WACA). Vocabulary expanded — see § Vocabulary below.

**Carry-forwards surfaced this session:**
- Blocker registry trim (remove #1, #2) — lands in 6c-iii-b-ii's ADR (the registry's source of truth for that pass).
- Full cascade mechanics restatement — lands in 6c-iii-b-ii's ADR (`dismiss_wa_code` narrowing, `removed` terminal, RFA hybrid line items, third WA origin all need the keep-FK cascade re-articulated).
- `reassign_wa_project` deeper mechanics (version_seq integration, source-bundle gap handling, single-WA-only-in-bundle edge case) — implementation phase.
- WACodeConf evolution to DB entity if catalog churn rises — keys (`code_type_id`) stable across migration; carry-forward, not deferred work.
- `level` mutation on a WA Code — not supported in MVP (would require changing code type); flagged.

**Per-`document_type` assignments (cumulative):**

| Pattern | document_types |
|---|---|
| Simple `missing → saved` | ACP13, ACP7, ACP15, ACP21, Emergency Notification, ACP8, VAR9 (all DepFiling docs — issued externally); COC; Daily Log |
| Cycling-family | CPR (RFA/RFP fork, 5 dates), FAMR (single-step review) |
| Bespoke | Lab Report (3 states: `missing`, `saved`, `invalid`; 4 transitions including `saved → invalid` for coordinator-discovered errors and `invalid → saved` for amended reports); RFP (4 states: `missing`, `saved`, `rejected`, `withdrawn`; SCA closure-receipt artifact per ADR-0037; `rejected` and `withdrawn` terminal; no `invalid` path since RFPs are SCA-side) |

**Entity roster (21 entities):**

| # | Entity | Notes |
|---|---|---|
| 1 | Project | SCA engagement. States: `active` / `closed` / `cancelled` (ADR-0037). Reopen permitted from both terminals. `close_project(project, rfp_file)` consumes ADR-0032 closure gate + transitions RFP `missing → saved` atomically; `cancel_project(project)` cascades RFA/pending-WA cleanup; `reopen_project` from `closed` cycles the RFP, from `cancelled` is state-flip only. Project is a Document-derivation source per ADR-0015: exactly one non-terminal RFP per project at any time. **Project ↔ WABundle 1:1 (ADR-0044)**; contract derives via `Project → WABundle → Contract` — no `Project.contract_id` (removed by ADR-0044). `create_project` is a Project + WABundle + v0-WA compound. |
| 2 | School | = Site for MVP. |
| 3 | WA | A **version** within a WABundle (ADR-0044): `wabundle_id` M:1, `version_seq` 0-based unique-per-bundle (replaces ADR-0017's `supersedes`; v0 initial, v1+ later). States: `pending` / `issued` / `superseded` (ADR-0030; v0 `pending → issued` operates **in-place per ADR-0048** — no new row at initial issuance). WA → Project derived via the bundle. Per-version `issued_date` + `initialization_date` (null while `pending`, set at issuance). Lists contractors via ContractorEngagement (ADR-0041); authorizes WA Codes via WACodeAssignment / WACA (ADR-0041 + ADR-0048 rename — formerly WAAuthorization). |
| 4 | WA Code | Bundle-scoped line item (ADR-0048 reparents from project per ADR-0020). Schema: `wabundle_id` (M:1 → WABundle, required), `code_type` (string identifier keyed against `WACodeConf`), **`level` (enum `'project' | 'building'`, required, denormalized from `WACodeConf[code_type].default_level` at creation, fixed thereafter)**, **`school_id` (nullable M:1 → School; non-null iff `level = 'building'`, constrained to `wabundle.sites` per ADR-0048's WABundle.sites invariant)**. States: `expected` / `pending_rfa` / `rfa_in_review` / `issued` / `budget_rfa_needed` (deferred) / `dismissed` (ADR-0027; **`removed` terminal added by 6c-iii-b-ii's ADR**). Linked to WAs via WACodeAssignment / WACA (ADR-0041 + ADR-0048). Default flat fee is a contract-derived read-time value — `Contract.code_flat_fee_schedule[code_type]` via the shortened contract-resolution path `code → WABundle → contract` (ADR-0045 + ADR-0048); distinct from the per-`(WA, code)` `budget` on WACA. |
| 5 | User | Auth identity (username/password). 0..1 typed reference to Employee via nullable `employee_id` (UNIQUE-constrained per ADR-0041). |
| 6 | Employee | Person doing project work; linked to User via `User.employee_id?` (0..1 ↔ 0..1, ADR-0041). |
| 7 | EmployeeRole | Temporal work-license assignment + rate-carrier: `(id, employee_id, role_type, contract_id, rate, start_date, end_date?)` (ADR-0035; `contract_id` mandatory M:1 → Contract per ADR-0045). Full-day closed-closed range. Disjoint-ranges-per-`(employee, role_type, contract)` invariant (ADR-0045 — was per-`(employee, role_type)`; rows on different contracts may overlap in time). Looked up by `(employee_id, role_type, contract, date)` at rate-resolution / blocker / closure-gate time (no FK from Time Entry per ADR-0041; `contract` resolved via the contract-resolution path `→ project → WABundle → contract`). |
| 8 | UserRole | App-access role: `(user_id, role_type)` composite key (ADR-0036). No timestamps, no state. Grant creates row; revoke hard-deletes; audit on User's log. Drives authorization predicates per ADR-0012 + ADR-0040 role catalog. |
| 9 | Time Entry | Billable time record. Schema (ADR-0041 amends ADR-0035; **ADR-0048 drops direct `project_id`**): `employee_id` (M:1 direct), `role_type` (enum), `site_id` (M:1 direct), `wa_code_id` (M:1 **mandatory at create and post-cascade per ADR-0048's keep-FK principle** — cascade emits a `write_off` Note but no longer nulls the FK), `date`, `on_site_range`, `off_site_sub_intervals` (ADR-0034). **Project derives via `wa_code → WACode → WABundle → Project` (ADR-0048).** Sub-intervals ⊆ on-site range, pairwise disjoint. EmployeeRole is a derived/validated link, looked up by `(employee, role_type, contract, date)` (ADR-0045); rate resolved at billing time. |
| 10 | Sample Batch | COC group. Carries sample type, TAT, composition `[{subtype, quantity}]`, `site_id` (M:1 mandatory direct per ADR-0041), `sampling_locations` (optional plain text per ADR-0041), employee reference (collector), collection time. WA Code reference (M:1 **mandatory at create and post-cascade per ADR-0048's keep-FK principle** — `dismiss_wa_code` / removal cascade emits a `write_off` Note on the batch per ADR-0042 + ADR-0046, but no longer nulls the FK; full cascade mechanics in 6c-iii-b-ii's ADR). **Project derives via `wa_code → WACode → WABundle → Project` (ADR-0048; was direct `project_id` per ADR-0041)**. Stateless per ADR-0038. Document-derivation source (COC + Lab Report). |
| 11 | Document | Unified slot+file entity. Per-`document_type` lifecycle dispatch (ADR-0024). Single-scope via `(scope_type, scope_id)` discriminator+FK (`scope_type ∈ {project, deliverable, wa_code}`, ADR-0041). Derivation set: Deliverables (transitively WA Codes), DepFilings, Sample Batches, Project (ADR-0015 clarified by ADR-0041). Derivation fires on expected codes (ADR-0022). |
| 12 | Deliverable | SCA-portal submission package. Bundle is a query over scoped Documents: derived required Documents (from Deliverable) + user-added Documents scoped to this Deliverable + user-added Documents scoped to WA Codes that map to this Deliverable (ADR-0041 reframes earlier "M:M" framing as single-scope on Document side). States: `pending_rfa` / `outstanding` / `under_review` / `approved` (ADR-0029). `wasted` derived flag. |
| 13 | Contractor | On-site abatement (or other) third party. Admin-side roster. Linked to WAs via ContractorEngagement (ADR-0041). |
| 14 | RFA | Request for Amendment; carries pending WA edits. M:1 mandatory `amends_wa_id` direct typed ref to WA, set at auto-draft creation (post-WA-issuance), immutable for RFA lifetime (ADR-0041). Project derived via WA → Project. May be auto-created during WA issuance reconciliation. |
| 15 | Note | Polymorphic commentary; typed reference to any entity OR history record (ADR-0040). Subtypes `regular | blocker | resolution | audit_reason | write_off` (ADR-0032, ADR-0040, ADR-0042). `authorship_class: 'user' | 'system'` + nullable `created_by`. Inter-Note `references` field. Regular Notes are creator-editable per ADR-0018; blocker, resolution, audit_reason, write_off Notes are immutable. Not deletable. |
| 16 | DepFiling | TRU-numbered regulatory filing bundle (ADR-0023). Project-scoped; editable `required_doc_types` set; Document-derivation source. No lifecycle. |
| 17 | WACodeAssignment (WACA) | Associative entity for WA ↔ WA Code M:N. Composite key `(wa_id, wa_code_id)`. No additional fields in MVP; gains budget when budget tracking lands. (ADR-0041 + ADR-0048 rename — formerly WAAuthorization. Shorthand: **WACA**.) |
| 18 | ContractorEngagement | Associative entity for WA ↔ Contractor M:N with stint state. `(wa_id, contractor_id, started_at, ended_at?)`. Multiple rows per `(wa_id, contractor_id)` permitted when contractor closes CPR filing and is re-added. CPR Document derives per row. (ADR-0041) |
| 19 | Contract | Contractual basis a project is opened against (ADR-0043). Schema: `contract_number` (uniqueness-constrained natural key), `start_date` / `end_date?`, `code_flat_fee_schedule` (inline non-temporal `{code_type, fee}` collection), optional `name` (null → derived display label `C` + last 5 chars of `contract_number`). No state machine — `pending` / `active` / `expired` derived from dates. Audit log; soft delete. Employee rates are FK-side (EmployeeRole carries a mandatory `contract_id` per ADR-0045); code default flat fees inline here. **Re-attached to the WABundle by ADR-0044**: `WABundle.contract_id` M:1 required (was `Project.contract_id`); mutable via `issue_wa` / `edit_wabundle`. |
| 20 | WABundle | Contractual-identity entity above the WA version chain (ADR-0044). Schema: `id`, `contract_id` (M:1 → Contract, required at create), `project_id` (M:1 → Project, UNIQUE — 1:1), `wa_number` / `service_id` / `job_number` (each uniqueness-constrained; nullable pre-issuance, required once a WA is issued — `issue_wa` populates them; `wa_number` is the human-facing natural key; `job_number` is SCA's WA id, distinct from the project number). **`sites` (M:N → School via WABundleSite, ADR-0048)** — declared intentionally; constrains building-level WA Codes (`code.school_id ∈ wabundle.sites`). Holds the WA chain (WA → WABundle M:1). No state machine — contract `expected` status derived (`wa_number IS NULL`). Audit log; soft delete. `create_project` (compound) gains a `sites: [School]` parameter (ADR-0048). `edit_wabundle` (`role >= admin`) corrects bundle metadata post-issuance **and manages sites — add unconditionally, remove guarded (fails if any WA Code under the bundle references the school) (ADR-0048)**. |
| 21 | WABundleSite | Associative entity for WABundle ↔ School M:N (ADR-0048). Composite key `(wabundle_id, school_id)`; no additional fields. Drives the building-level WA Code containment invariant (`WACode.level = 'building' ⇒ WACode.school_id ∈ wabundle.sites`). Declared at `create_project`; editable via `edit_wabundle` (admin). |

Values / lookups (not entities): Sample Type, Sample Subtype, Project Type, TAT options, status enums, `document_type` registry, DepFiling template constants, **`WACodeConf` code-type catalog (code-side static config per ADR-0048: `code_type_id` / `name` / `default_level` per entry; default flat fee per code type lives on `Contract.code_flat_fee_schedule[code_type]` per ADR-0045)**.

**Per-entity history-pattern assignments:**

| Pattern | Entities |
|---|---|
| Comprehensive capture | Document, WA, RFA |
| Lifecycle capture | Project, Sample Batch, Deliverable, EmployeeRole, WA Code, ContractorEngagement |
| Audit log | Employee, User, Time Entry, Contractor, DepFiling, Contract, WABundle |
| No history | School, Note, UserRole, WACodeAssignment, WABundleSite |

**Per-entity delete policy:**

| Policy | Entities | Notes |
|---|---|---|
| Soft delete (guarded hard-delete eligible) | Document, WA, RFA, Project, Sample Batch, Deliverable, EmployeeRole, Employee, User, Time Entry, Contractor, WA Code, DepFiling, ContractorEngagement, Contract, WABundle | History-carrying or referenced by history records. |
| Hard delete | School, Note, UserRole, WACodeAssignment, WABundleSite | No history, no external history references. |

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
11. **Blocker-as-Note with lazy materialization.** System-derived blockers stay derived (registry scan) until a coordinator engages (comment or default-resolution / dismissal). First engagement materializes a blocker Note (system-authored) with `surfaced_at` backfilled from entity history. `has-default-resolution | fix-only` classification per registry (ADR-0042/ADR-0046 reframe of the original dismissable/fix-only binary). Cross-project blockers materialize as paired Notes linked via `paired_blocker_ref`. (ADR-0032)
12. **Chain-dismissal.** When resolving one blocker structurally implies secondary entities should also leave the not-written-off domain, the registry entry declares a `chain` shape; resolution atomically emits direct `write_off` Notes on the chained entities, each inheriting the primary's `justification`, `references` the primary blocker Note. (ADR-0032 framework; ADR-0046 reframe via the named chain `te_batches_by_coverage`. Four concrete instances on that chain — #5, #8, #11, #12. ADR-0033's #9 chain-dismissal instance dissolved by ADR-0046; ADR-0039's #11 chain reframed by ADR-0046.)
13. **Project-state-driven immutability.** Entities whose project membership puts them in a parent project's "freezing" terminal state are immutable at command guard, with declared exceptions for commentary-only paths and parent-reopen escape hatches. Project's `closed` is the freezing terminal (billed-work snapshot); `cancelled` is the non-freezing terminal (abandoned work, available for reassignment). (ADR-0038)
14. **Write-off / default-resolution.** An entity that exists but should not count (toward billing, conflicts) is excluded by an immutable `write_off` Note carrying a reason, rather than deleted or mutated; derived predicates compute over not-written-off entities, so exclusion dissolves the conditions the entity participated in. Produced by a guarded, coordinator-initiated **default-resolution** command (the nuclear option for resolving a blocker — mandatory justification, never auto-invoked) or as a reason-inheriting cascade of another command. Reversible only by an explicit superseding command (`revoke_write_off`). Subsumes pattern #10 (`wasted` is now an instance). (ADR-0042)

**Blocker registry (post-ADR-0046 reclassification, 12 entries):**

| # | Blocker | Classification | Target | Command shape | Compound names | Chain |
|---|---|---|---|---|---|---|
| 1 | Time Entry `wa_code = null` | has-default-resolution | Time Entry | generic | — | — |
| 2 | Sample Batch `wa_code = null` | has-default-resolution | Sample Batch | generic | — | — |
| 3 | Sample Batch Lab Report ∈ {`missing`, `invalid`} at closure | has-default-resolution | Sample Batch | generic | — | — |
| 4 | Sample Batch COC `missing` at closure | has-default-resolution | Sample Batch | generic | — | — |
| 5 | Time Entry no `daily_log` at closure | has-default-resolution | Time Entry | generic | — | `te_batches_by_coverage` |
| 6 | DepFiling required-doc `missing` at closure | has-default-resolution | DepFiling | generic | — | — |
| 7 | Open `draft`/`in_review` RFA at closure (add/remove RFA, MVP) | has-default-resolution | RFA | named-compound | [`resolve_open_rfa`] | — |
| 8 | Cross-project time overlap on Employee | has-default-resolution | (paired Time Entries) | named-compound | [`resolve_overlap`, `resolve_overlap_paired`] | `te_batches_by_coverage` |
| 9 | Sample collection time not in employee net on-site time | has-default-resolution | Sample Batch | generic | — | — |
| 10 | Project's non-terminal RFP not in `saved` state at closure | **fix-only** | — | — | — | — |
| 11 | Time Entry `(employee, role_type, contract, date)` not covered by EmployeeRole | has-default-resolution | Time Entry | generic | — | `te_batches_by_coverage` |
| 12 | Time Entry dated before head WA's `initialization_date` | has-default-resolution | Time Entry | generic | — | `te_batches_by_coverage` |

11 `has-default-resolution` + 1 `fix-only` (#10 — coherence-test failure, closure-definitional). **Post-ADR-0048: blockers #1 and #2 are unfireable predicates** — `wa_code = null` is no longer a producible state under the cascade-keep-FK principle + missing-derived auto-generation (ADR-0048 §4). Formal registry removal lands in 6c-iii-b-ii's ADR (the registry's source of truth for that pass); rows kept here until then for trace continuity. #4 flagged in `post-mvp.md` as drop-candidate if MVP operation confirms it cannot fire in practice.

**Vocabulary (cumulative):**
- **Coordinator** — the app's user with project-tracking-dashboard access; job title "project manager"; function: tracking. Consumes the former placeholder entry "office staff who manage work, not an app user in MVP" — those people are now defined as app users via this role (ADR-0040).
- **Project / School / WA / WA Code** — as before. School = site = building for MVP. **Post-ADR-0048: WA Codes carry an explicit `level: 'project' | 'building'` discriminator with a nullable `school_id` (non-null iff `level = 'building'`)**; sample-collection codes are one species of building-level code, not a distinct class. A WA may authorize work across multiple schools and carry multiple building-level codes (one per `(sample_type, school)` for sample-collection; analogous for other building-level types). The school must be present in the parent `WABundle.sites` (see below).
- **Project-level WA Code** — `level = 'project'` per ADR-0048; applies across the whole project, no school binding (e.g., supervision). `school_id` is null; unconstrained by WABundle.sites.
- **Building-level WA Code** — `level = 'building'` per ADR-0048; applies at a specific school within the project (sample-collection codes are one example). `school_id` is non-null and constrained to `wabundle.sites`. Mutation of `level` is not supported in MVP (would require changing code type).
- **`level` (WA Code)** — required enum discriminator (`'project' | 'building'`) on WA Code per ADR-0048. Denormalized from `WACodeConf[code_type].default_level` at creation, fixed thereafter. Application-layer invariant: `WACode.level == WACodeConf[WACode.code_type].default_level`.
- **WABundle.sites** — the set of schools the WABundle has declared in scope (ADR-0048), via the WABundleSite associative entity. Curated intentionally — declared at `create_project`, mutated via `edit_wabundle` (admin: add unconditionally, remove guarded). Drives the building-level WA Code containment invariant and the school-subset guard on `reassign_wa_project`.
- **WABundleSite** — associative entity for WABundle ↔ School M:N (ADR-0048). Composite key `(wabundle_id, school_id)`, no other fields, no history, hard-delete.
- **`reassign_wa_project(wa, new_project)`** — compound command (ADR-0048) that moves a misfiled WA to its correct project. Predicate inherits ADR-0047 Cluster 3 class rule (`role >= coordinator`). Guard: `moving_wa.codes.school_id ⊆ target_project.wabundle.sites` (building-level codes only). Work follows automatically via project-derivation through `wa_code` — no `move_work` flag. Deeper mechanics (version_seq integration, source-bundle bookkeeping) are implementation-phase concerns.
- **`WACodeConf`** — code-side static config for the WA-code-type catalog (ADR-0048; rejects DB-entity modeling for MVP). Entry shape: `{ code_type_id (string), name (display label), default_level ('project' | 'building') }`. Other attributes may be added in-file. Default flat fee per code type lives on `Contract.code_flat_fee_schedule[code_type_id]` per ADR-0045, keyed by the same `code_type_id`. Adding a code type requires a code deployment; migration to a DB entity remains a future option if churn rises (keys stable across migration).
- **`default_level` (WACodeConf entry)** — `'project' | 'building'` field on each WACodeConf entry per ADR-0048. Sets the immutable level of WA Code instances created from this type.
- **Cascade-keep-FK principle** — under ADR-0048, the `dismiss_wa_code` / removal cascade (ADR-0042 / ADR-0046) **keeps** the `wa_code` FK on referencing Time Entries and Sample Batches (the dismissed / removed WA Code row is retained per the design pattern #14 substrate; the FK still resolves) and emits a `write_off` Note on each referencing record. Retires ADR-0027's original "null `wa_code`" cascade step. The principle is stated in ADR-0048; the full cascade mechanics — what the cascade does *instead* of nulling, the `write_off` Note shape on referencing records, the closure-blocker shape for cascade-written-off TE / SB, blocker registry trim removing #1 and #2 — land in 6c-iii-b-ii's ADR.
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
- **Blocker** — A structural condition (registry entry from ADR-0032) or user-flagged Note declaring something is held up. Every registry blocker has a structural-fix path; the ADR-0042 reframe replaces the dismissable/fix-only binary with the derived property **has-default-resolution** vs. **fix-only**. The 12-entry registry is reclassified by ADR-0046: 11 `has-default-resolution`, 1 `fix-only` (#10).
- **Materialized blocker** — A blocker that exists as a persisted Note record (vs purely-derived, registry-only). System-derived blockers materialize on first user engagement.
- **Engagement** — A coordinator writing a comment about a blocker or invoking its default-resolution / dismissal. The trigger for lazy materialization of system-derived blockers.
- **Chain-dismissal (post-ADR-0046)** — When resolving one blocker structurally implies secondary entities should also leave the not-written-off domain, the registry entry declares a `chain` shape; resolution atomically emits direct `write_off` Notes on the chained entities, each inheriting the primary's `justification`, `references` the primary blocker Note. The MVP-named chain shape is `te_batches_by_coverage` (#5, #8, #11, #12 — see below). The older "null `wa_code` + materialize #2 + auto-dismiss #2" mechanic from ADR-0033 / ADR-0039 is superseded.
- **Write-off / written-off** — an entity that exists and is retained (audit-preserved) but does not count toward billing aggregation or blocker/conflict derivation. Recorded by an immutable `write_off` Note on the entity carrying a `reason`; "written off" is a derived status (`∃ write_off Note not superseded by a `revoke_write_off`). A marker orthogonal to state machines. Subsumes the retired `non_billable` flag. (ADR-0042)
- **Default-resolution** — a guarded, coordinator-initiated command that resolves a blocker by writing off the conflicting entities (so the blocker's predicate, computed over not-written-off entities, stops holding). The "nuclear option" alongside the always-available structural-fix path: never auto-invoked, requires a mandatory justification. A blocker **has-default-resolution** iff a coherent one exists — the coherence test: the condition dissolves by *excluding* a well-defined entity set, not by *creating/correcting* something. (ADR-0042)
- **Cascade write-off** — a write-off produced as a side effect of a non-default-resolution command (e.g. `dismiss_wa_code`'s downstream effect on referencing Time Entries / Sample Batches). Not separately guarded; inherits its `reason` from the initiating command — the reason the write-off model admits non-blocker reasons. **Post-ADR-0048: the cascade keeps the `wa_code` FK on referencing records (cascade-keep-FK principle); it emits a `write_off` Note but no longer nulls the reference.** Full mechanics restated in 6c-iii-b-ii's ADR. (ADR-0042 + ADR-0048)
- **`revoke_write_off`** — explicit command that lifts a write-off by writing an immutable superseding Note (Notes are not deletable); re-includes the entity in billing and blocker-derivation. Command shape is a carry-forward. (ADR-0042)
- **`resolution_kind`** — discriminator on resolution Notes; under ADR-0042 the value set is `structural_fix | default_resolution | dismissal`, where `dismissal` is retained only for free-form user-flagged blockers (registry blockers resolve via `structural_fix` or `default_resolution`).
- **On-site range / off-site sub-interval (Time Entry)** — `on_site_range` is the parent range of an entry; `off_site_sub_intervals` are project-committed time-away spans within the on-site range (currently always lab delivery). Sub-intervals are pairwise disjoint, entirely within on-site range, positive-duration. (ADR-0034)
- **Gross on-site range** — the full `on_site_range` of a Time Entry, inclusive of off-site sub-intervals. Represents *project commitment*. Used by the cross-project overlap predicate (ADR-0028 amendment).
- **Net on-site time** — `on_site_range` minus the union of off-site sub-intervals. Represents *physical presence at the parent project's site*. Used by blocker #9 (sample collection coverage).
- **RFP (project-level)** — Request for Payment. SCA-generated document received when a project is submitted for payment; serves as the system-side closure receipt. New top-level `document_type` per ADR-0037, bespoke 4-state machine (`missing` / `saved` / `rejected` / `withdrawn`). One non-terminal RFP per project at any time. Distinct from CPR's internal RFP bucket (the contractor-side payment-request phase within the CPR cycling-family document) — same acronym, different schema level, different counterparty direction (SCA → us vs. contractor → us).
- **Non-terminal RFP** — an RFP in `missing` or `saved` state. The current open submission cycle for a project. Per-project invariant: exactly one at any time.
- **Terminal RFP** — an RFP in `rejected` or `withdrawn` state. Historical record of a closed-out submission cycle. Unbounded count per project (accumulates with each reopen-from-`closed` event).
- **Reopen-from-`closed` / reopen-from-`cancelled`** — the two `reopen_project` forms. From `closed`: requires `rfp_reason ∈ {rfp_rejected, rfp_withdrawn}`; cycles the RFP. From `cancelled`: pure state-flip; no structural reason captured (lifecycle capture + optional Note carry audit).
- **WACodeAssignment (WACA)** — associative entity for WA ↔ WA Code (composite key `(wa_id, wa_code_id)`, ADR-0041 + ADR-0048 rename — formerly WAAuthorization). Shorthand: **WACA**. Gains budget when budget tracking lands. All prior ADR references to WAAuthorization read as WACodeAssignment going forward.
- **ContractorEngagement** — associative entity for WA ↔ Contractor with stint markers (`started_at`, `ended_at?`, ADR-0041). Multiple rows per `(wa_id, contractor_id)` allowed for repeat engagements; CPR derives per row.
- **Contract** — the contractual basis a project is opened against (ADR-0043). Carries a `contract_number` (uniqueness-constrained natural key), a `start_date` / `end_date?` term, an inline non-temporal `code_flat_fee_schedule`, and an optional `name`. No state machine — validity (`pending` / `active` / `expired`) is derived from the term + clock. Employee billing rates are contract-scoped FK-side (EmployeeRole carries a mandatory `contract_id`, ADR-0045); code default flat fees are contract-defined inline. **Re-attached to the WABundle by ADR-0044**: the contract reference is `WABundle.contract_id` (M:1, required at create) — `Project.contract_id` removed, `Project → Contract` derives via the bundle. Mutable: `issue_wa` sets/confirms it at issuance, `edit_wabundle` (`role >= admin`) corrects it after.
- **`code_flat_fee_schedule` (Contract)** — an inline value collection of `{code_type, fee}` pairs on Contract: the default flat fee per WA code type for that contract. Non-temporal — fixed once for the contract's whole life. The code-type catalog itself (`WACodeConf`) is **code-side static config per ADR-0048**. (ADR-0043). A code type absent from the schedule resolves to null/unpriced — no blocker (ADR-0045).
- **Contract-resolution path** — the shared derivation by which an entity resolves its governing Contract. **Post-ADR-0048 the path shortens for direct-bundle-holders**: `WACode → WABundle → contract` (was `code → project → WABundle → contract` per ADR-0045). For Time Entry / Sample Batch (which dropped direct `project_id`): `entity → wa_code → WACode → WABundle → contract`. For EmployeeRole rate resolution: same shape via the entity's project's WABundle. Always resolves — `create_project` guarantees a WABundle with a required `contract_id` (ADR-0044). Money values (rates, flat fees) derived through the live `WABundle.contract_id`, never snapshotted (the basis for ADR-0044 dissolving `reassign_project_contract`).
- **`audit_reason` (Note subtype)** — immutable Note subtype attached to history records via optional `reason_text` on grant/revoke commands (ADR-0040).
- **`amends_wa_id`** — RFA's mandatory direct typed reference to the WA being amended; set at auto-draft creation, immutable for RFA lifetime (ADR-0041).
- **`scope_type` / `scope_id` (Document)** — single-scope discriminator + FK on Document; `scope_type ∈ {project, deliverable, wa_code}` (ADR-0041).
- **`site_id` (Time Entry, Sample Batch)** — M:1 mandatory direct typed reference to School; the structural site-of-work link (ADR-0041).
- **`sampling_locations` (Sample Batch)** — optional plain-text field describing specific spots within the site where samples were collected (ADR-0041).
- **Derived/validated link** — a relationship resolved by lookup rather than FK. Used in ADR-0041 for Time Entry ↔ EmployeeRole: rate / blocker / closure-gate logic looks up the covering EmployeeRole row from `(employee_id, role_type, contract, date)` at use time (the `contract` dimension added by ADR-0045, resolved via the contract-resolution path).
- **WABundle** — the contractual-identity entity above the WA version chain (ADR-0044). 1:1 with Project; holds the WA chain (WA → WABundle M:1). Carries `contract_id` (required at create), `wa_number` / `service_id` / `job_number` (SCA-supplied; `job_number` is SCA's WA id, distinct from the project number, which is our own tracking id; all three nullable pre-issuance, required at issuance), **and `sites` (M:N → School via WABundleSite per ADR-0048)** which scopes building-level WA Codes. Audit log, soft delete, no state machine.
- **Version / `version_seq` (WA)** — a specific WA within a WABundle. `version_seq` is a 0-based integer, unique per bundle; the head WA is the max `version_seq`. v0 is the initial WA, v1+ are later versions (an approved RFA produces the next version). Replaces ADR-0017's `supersedes` self-reference; `version_type` becomes derivable (`initial ⟺ version_seq == 0`). **v0 `pending → issued` (initial issuance) operates in-place per ADR-0048 — no new WA row is created at initial issuance; v1+ amendment-issued WAs are new rows.** (ADR-0044 + ADR-0048)
- **`issued_date` / `initialization_date` (WA)** — per-WA-version date fields, null while `pending`, populated at issuance. `issued_date` = when SCA issued the document; `initialization_date` = the date work under the WA is authorized to begin from (supersedes ADR-0017's `effective_date`). A new WA version may revise both. The head WA's `initialization_date` drives the WA-initialization closure blocker (ADR-0044): a Time Entry dated before it is blocked; null ⇒ never fires. Changed post-issuance only by issuing a new WA version. (ADR-0044)
- **`edit_wabundle`** — `role >= admin` command for post-issuance corrections to WABundle metadata (`contract_id`, `wa_number`, `service_id`, `job_number`). Distinct from `issue_wa`, which (coordinator) sets/confirms those four SCA-supplied facts at issuance. Non-uniform predicate — carry-forward for the Step 6c-ii predicate-table ADR. (ADR-0044)
- **`default_resolve(blocker, justification)`** — the generic Hybrid-shape default-resolution command for the 8 `has-default-resolution` registry entries declaring `command_shape: generic` (#1, #2, #3, #4, #5, #6, #9, #11, #12). Materializes the blocker if derived-only, writes off the registry-declared target entity, emits chained `write_off` Notes if a `chain` is declared, writes one `resolution` Note (`resolution_kind: default_resolution`). `role >= coordinator`. (ADR-0046)
- **`resolve_overlap(blocker_note, justification)`** — single-side named compound for #8 (cross-project time overlap). Splits the engaging side's Time Entry at the overlap boundaries, writes off the resulting sliver, chains to batches via `te_batches_by_coverage`; the other side's paired blocker resolves derivationally via ADR-0032's auto-`structural_fix` Note. (ADR-0046)
- **`resolve_overlap_paired(paired_blocker_note, justification)`** — joint named compound for #8. Splits both Time Entries at the overlap boundaries, writes off both slivers, chains to batches on both sides; emits `resolution` Notes (`resolution_kind: default_resolution`) on both materialized paired blocker Notes. Audit-symmetric across both projects. (ADR-0046)
- **`resolve_open_rfa(rfa, justification)`** — named compound for #7 (open `draft`/`in_review` RFA at closure, MVP add/remove-RFA case only). Invokes `withdraw_rfa` → cascade `dismiss_wa_code` on returned codes → cascade `write_off` Notes on referencing Time Entries / Sample Batches via the existing ADR-0027 + ADR-0042 reference-nulling cascade → auto-draft regeneration empties itself naturally (empty-draft hard-deletes per ADR-0031). `role >= coordinator`. Out of scope MVP: budget-RFA case (would be `fix-only` if introduced; reclassification deferred behind budget tracking). (ADR-0046)
- **`te_batches_by_coverage`** — named chain shape. For a target Time Entry `TE`, the chained set is `{ batch : batch.employee == TE.employee AND batch.collection_time ∈ TE.on_site_range }` (half-open per `split_entry`'s carry-forward). Each chained batch receives a direct `write_off` Note inheriting the primary's `justification`, `references` the primary blocker Note. Used by #5, #8 (per sliver), #11, #12. The MVP-named chain shape under pattern #12. (ADR-0046)
- **Fork A** — the narrow relink-gate relaxation on ADR-0033's `relink_sample_batch_wa_code`: gate's permitted-state set extends from `{wa_code IS null, current code dismissed}` to `{wa_code IS null, current code dismissed, batch trips #9}`. Unblocks misfile recovery for healthy-`wa_code` batches without a write-off-then-relink dance. Composes independently with the planned `removed`-branch amendment from Step 6c-iii-b. (ADR-0046)

## Open questions

*(Step 6c-iii-b-i's open questions — WA Code reparenting + single-table `level` discriminator vs. two-table fork + WABundle.sites declaration + TE / SB project derivation through `wa_code` + cascade-keep-FK principle + WACodeConf placement + WAAuthorization rename + `reassign_wa_project` interface + v0 in-place issuance — **all resolved in ADR-0048; Step 6c-iii-b-i is complete**. Step 6c-ii's, Step 6b-residual-2's, Step 6c-iv-a/b's, Step 6c-iii-a's open questions resolved in ADR-0047 / ADR-0046 / ADR-0042 / ADR-0045 / ADR-0043 / ADR-0044 respectively.)*

**For the next session — Step 6c-iii-b-ii (WA Code removal model — item 6 of original Step 6c-iii-b):**

The Step 6c-iii-b-ii session writes up item 6 of the original Step 6c-iii-b brief — the WA Code removal model + `dismiss_wa_code` narrowing + new `removed` terminal + RFA hybrid line-item model + third WA origin + shared removal cascade. Shape was deliberated session 14 (productive tangent off Step 6b-residual-2 sizing); 6c-iii-b-i's ADR-0048 already fixed the **cascade-keep-FK principle** that the cascade design now inherits. This session is the write-up.

**Items in scope (full brief in `steps.md` → Step 6c-iii-b-ii):**

1. **`dismiss_wa_code` narrowing.** Valid targets: `expected` / `pending_rfa` only — drop the `issued → dismissed` transition. Stays a state-transition command, never hard-deletes (ADR-0027's delete-substitution dropped — always transitions, even for never-referenced codes). Optional `reason_text` → `audit_reason` Note via ADR-0040's existing pattern, attached to the WA Code's lifecycle-capture record.
2. **New `removed` terminal state.** `issued → removed`, reached via an RFA removal line item or an SCA-direct corrected amendment. Distinct from `dismissed` ("never made it onto a WA").
3. **RFA as a hybrid instrument.** Line items typed `add | remove | budget` (budget deferred behind budget tracking). Additions stay system-derived; removals are coordinator-authored — scopes ADR-0031's "coordinator cannot manually add or remove line items" to additions only. Consequences: draft creation no longer purely system-triggered (a coordinator adding a removal opens a draft); `approve_rfa` composition becomes `(prior ∪ adds) \ removes`; resolution polymorphic on line-item type (add-targets → `issued` / `pending_rfa`; remove-targets → `removed` / `issued`).
4. **Third WA origin.** SCA-direct corrected amendment — an externally-arrived amendment WA with no RFA behind it. Diff-based reconciliation against the superseded WA (codes added → `issued`; codes dropped → `removed` + cascade; unchanged → `issued`). Likely shape: one externally-received-WA path branching on the version-chain marker, with `approve_rfa` staying the separate firm-initiated path.
5. **Shared removal cascade.** Invoked from three triggers (`dismiss_wa_code`, `approve_rfa` removal line items, SCA-direct amendment path). **Inherits ADR-0048's cascade-keep-FK principle**: keep the `wa_code` FK on referencing TE / SB (the dismissed / removed code stays referenceable in its terminal state), emit a `write_off` Note on each referencing record, closure-blocker shape per ADR-0042 / ADR-0046.
6. **Blocker registry trim — formal removal of #1 and #2** ("TE `wa_code = null`," "SB `wa_code = null`"). Both are unfireable post-ADR-0048; registry drops to 10 entries. ADR-0046's `default_resolve` Hybrid command's dispatch rows for these blockers are retired alongside; ADR-0047's predicate-table coverage stays intact via the generic `default_resolve` row.

**Predicate-table amendment expectation.** Any new commands introduced by 6c-iii-b-ii inherit `role >= coordinator` from ADR-0047's Cluster 3 / 4 class rules. Non-uniform predicates land as explicit-row amendments to ADR-0047 when introduced. `dismiss_wa_code`'s `reason_text?` parameter is a signature change, not a predicate change. Same applies to any new SCA-direct-amendment command.

**Touchpoints / amendments expected at 6c-iii-b-ii:** ADR-0027 (state machine — `dismissed` kept, `removed` added, `dismiss_wa_code` narrowed, delete-substitution dropped, full cascade restatement under keep-FK; design pattern #9's hard-delete branch no longer exercised by WA Code), ADR-0029 (`wasted` flag re-derivation — extend trigger `dismissed` → `dismissed OR removed`), ADR-0030 (third WA origin / `issue_wa` generalization for SCA-direct amendments), ADR-0031 (RFA hybrid line-item model — `add` / `remove`, coordinator-authored removals, polymorphic resolution, `approve_rfa` composition), ADR-0033 (`relink_sample_batch_wa_code` guard gains a `removed` branch; composes independently with Fork A from ADR-0046), ADR-0042 / ADR-0046 (full cascade restatement under keep-FK principle; registry trim removing #1 and #2). Sizing check: this is a single coherent decision cluster; should fit one window.

**Deferred behind Step 6c-iii-b-ii:**
- **`split_entry` command-shape** — predicate is `role >= coordinator` (explicit row in ADR-0047); shape (split point, field-inheritance for `daily_log` / `wa_code` / off-site sub-intervals on resulting sub-entries, batch reassignment at boundary) is undefined; no natural home step. Load-bearing for ADR-0046's `resolve_overlap` / `resolve_overlap_paired` compounds — when settled, those specs should be re-validated. Candidate: Step 6d or a residual. ADR-0042 carry-forward — half-open interval semantics: Time Entry ranges are `[start, end)`.
- **`revoke_write_off` command shape** — predicate `role >= coordinator` (ADR-0047, scenario (a)); parameters and guards undefined; no home step (candidate: alongside `split_entry`). Scenario (b) — misattribution-on-closed-project recovery — needs `revoke_write_off` + ADR-0038 closed-project exception + the post-MVP cross-project Sample Batch reassignment command; layered, post-MVP.
- **`reassign_wa_project` deeper mechanics** — version_seq integration in the target chain, source-bundle bookkeeping after a move, single-WA-only-in-bundle edge case, audit-trail shape on both sides. Interface + guard + work-follows fixed in ADR-0048; bookkeeping is implementation-phase.
- **ADR-0031 gap — auto-draft regeneration suppression at closure-gate.** Suppressed on cancelled projects but silent on projects in closure-gate evaluation. ADR-0046's `resolve_open_rfa` compound resolves itself; the bare `withdraw_rfa` structural-fix path during closure-gate can loop. Flagged for ADR-0031 follow-up; may fold into 6c-iii-b-ii if the RFA hybrid-line-item model rewrites that ADR enough that the gap can be closed cheaply.

**Carry-forwards worth re-checking when relevant:**
- ~~**`reassign_project_contract` (post-MVP)**~~ — dissolved by ADR-0044. Already removed from `post-mvp.md`.
- **ContractorEngagement command-shape** — `start_contractor_engagement` / `end_contractor_engagement` predicates are `role >= coordinator` (ADR-0047); signatures + pre-conditions still deferred (no longer "behind Step 6c-iii-b" since the restructure surface landed). Candidate: implementation phase or a future residual. Date defaults: `started_at` → row-creation date; `ended_at` → CPR-saved date (nullable, overridable).
- **Cross-project Sample Batch reassignment as a structured command** — in `post-mvp.md` alongside notifications.
- **Retroactive rate corrections via Time-Entry rate snapshot** (carry-forward from ADR-0035): reversible additive change post-MVP if signal emerges.
- **Security-immediate revoke runtime semantics** (session invalidation on `revoke_user_role`): implementation concern, deferred to auth implementation step.
- **WACodeConf evolution to DB entity** (ADR-0048 carry-forward) — option if catalog churn rises beyond rare; keys (`code_type_id`) stable across migration.
- **`level` mutation on WA Code** (ADR-0048 carry-forward) — not supported in MVP; flagged.

**Carried forward (deferred to later steps):**
- **WACodeAssignment / WACA budget fields** — added when budget tracking design lands; immediate post-MVP per user signal.
- **Draft invoice generation against budgets** — second post-MVP priority.
- **Billing Rate entity/table** — temporal `(subtype, TAT) → rate` lookup. Likely Step 6d or later. Follows the temporal rate resolution template formalized in ADR-0035 / ADR-0041.
- **Quarantine as a per-entity violation-handling pattern** — excluded from history-pattern menu (ADR-0013); remains deferred per ADR-0011. Step 6d.
- **Bulk import file-upload relaxation** — 6b or implementation.
- **Project structure for managing N `document_types`** — defer to implementation phase.
- **History implementation shape** (event store, append-only tables, temporal tables) — Step 8.
- **Persistence isolation for cross-entity invariants** — Step 8.
- **Post-MVP per-project coordinator scoping** triggers the chain-freeze on ADR-0047's table (project-scoped rows become non-chain `role >= coordinator AND assigned_to(target.project)`).
- **Future non-chain roles** (rate-only admin, external SCA-contact role): each appends a column to ADR-0047's table without refactoring existing rows.
- Whether existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

## Next session

**Step 6c-iii-b-ii — WA Code removal model (item 6 of original Step 6c-iii-b): `dismiss_wa_code` narrowing + new `removed` terminal + RFA hybrid line-item model + third WA origin + shared removal cascade restated under cascade-keep-FK + blocker registry trim (#1, #2 formal removal).** Case-3 scoped — shape settled in chat across sessions 12 / 14; this session is the ADR write-up. The cascade-keep-FK principle inherited from ADR-0048 §4 lets the cascade design land cleanly. Brief in `steps.md` → Step 6c-iii-b-ii. Execution order going forward: 14a ✓ → 6c-iv-a ✓ → 6c-iii-a ✓ → 6c-iv-b ✓ → 14b ✓ → 6c-ii ✓ → 6c-iii-b-i ✓ → **Step 6c-iii-b-ii** → 6d. ADR number at write time: next is **ADR-0049**.

### Prompt for the next session

> Resume work. Next is **Step 6c-iii-b-ii — WA Code removal model**. **Case 3 scoped** — shape was deliberated session 14 and the cascade substrate (keep-FK principle) was fixed by ADR-0048 §4. This session writes the ADR. Per `_workflow.md` Case 3: read the brief in `steps.md` → § Step 6c-iii-b-ii; read this prompt + the **Open questions** block above (item enumeration, touchpoints, deferred items); enter planning mode (STOP-AND-CONFIRM gate applies); on `approved` proceed to the ADR write.
>
> **Read first:** this prompt + the Open questions block above. From `decisions.md`:
> - **ADR-0048** (Step 6c-iii-b-i — establishes the cascade-keep-FK principle as a consequence of project-derivation through `wa_code`; this session writes the full cascade mechanics).
> - **ADR-0027** (WA Code state machine — to amend: drop `issued → dismissed`, add `removed` terminal, narrow `dismiss_wa_code`, drop delete-substitution, retire the "null wa_code" cascade step in full, restate cascade under keep-FK).
> - **ADR-0029** (`wasted` derivation — to amend: extend trigger `dismissed` → `dismissed OR removed`).
> - **ADR-0030** (WA state machine + origins — to amend: third WA origin / `issue_wa` generalization for SCA-direct corrected amendments).
> - **ADR-0031** (RFA state machine — to amend: hybrid line-item model `add | remove`, coordinator-authored removals, polymorphic resolution, `approve_rfa` composition `(prior ∪ adds) \ removes`).
> - **ADR-0033** (relink guard — to amend: gains a `removed` branch; composes independently with Fork A from ADR-0046).
> - **ADR-0042 / ADR-0046** (write-off model + registry — to amend: full cascade restatement under keep-FK; formal removal of registry entries #1 and #2; ADR-0046's `default_resolve` dispatch rows for #1 / #2 retired).
> - **ADR-0044** (WABundle — referenced for the SCA-direct amendment path; possibly amended for routing).
>
> **Items in scope (full brief in `steps.md` → Step 6c-iii-b-ii):**
> 1. `dismiss_wa_code` narrowed (`expected` / `pending_rfa` only; no `issued → dismissed`; delete-substitution dropped; optional `reason_text` → `audit_reason` Note).
> 2. New `removed` terminal state (`issued → removed`); distinct from `dismissed`.
> 3. RFA hybrid instrument (line items typed `add | remove | budget`; budget deferred; additions system-derived, removals coordinator-authored; polymorphic resolution; `approve_rfa` composition `(prior ∪ adds) \ removes`).
> 4. Third WA origin (SCA-direct corrected amendment; diff-based reconciliation; one externally-received-WA path branching on version-chain marker; `approve_rfa` stays separate).
> 5. Shared removal cascade across three triggers; inherits cascade-keep-FK from ADR-0048 §4; full mechanics + closure-blocker shape restated here.
> 6. Blocker registry trim — formal removal of #1 and #2 from the 12-entry list (registry drops to 10); ADR-0046's dispatch retires the corresponding rows; ADR-0047 predicate coverage stays intact via the generic `default_resolve` row.
>
> **Sizing.** Single coherent decision cluster (one ADR); should fit one window. Run a quick fit check at session head; if any signal fires unexpectedly, partition (e.g., RFA hybrid line items vs. third WA origin) before writing.
>
> **Predicate-table amendment expectation.** Any new commands introduced here inherit `role >= coordinator` from ADR-0047's Cluster 3 / 4 class rules. If a non-uniform predicate emerges (e.g., the SCA-direct-amendment command), add an explicit row to ADR-0047 by amendment. `dismiss_wa_code`'s `reason_text?` parameter is a signature change, not a predicate change.
>
> **Out of scope — do not pull in:**
> - Budget tracking on WACA (post-MVP; budget-typed RFA line items are flagged but deferred).
> - Draft invoice generation (post-MVP).
> - `split_entry` / `revoke_write_off` command shapes (predicates landed in ADR-0047; shape design carries forward).
> - `reassign_wa_project` version_seq mechanics (ADR-0048 carry-forward to implementation phase).
> - Per-project coordinator scoping (post-MVP; triggers ADR-0047 chain-freeze when it lands).
>
> **Sequencing:** 14a ✓ → 6c-iv-a ✓ → 6c-iii-a ✓ → 6c-iv-b ✓ → 14b ✓ → 6c-ii ✓ → 6c-iii-b-i ✓ → **Step 6c-iii-b-ii (this session)** → 6d.
>
> **Reference (full detail in the cumulative tables):** 21 entities (post-ADR-0048); 14 design patterns; roles superadmin / admin / coordinator / auditor with the predicate table in ADR-0047; 12-entry blocker registry post-ADR-0046 (11 has-default-resolution + 1 fix-only — this session formally trims to 10 by removing #1 / #2, which are already flagged unfireable post-ADR-0048). State machines locked through ADR-0048 — this session reopens WA Code's state machine to add `removed` and narrow `dismiss_wa_code`, and reopens RFA's line-item model.
>
> **Process notes:**
> - STOP-AND-CONFIRM gate applies to any ADR write — propose positions in chat first, wait for `approved`.
> - Casual back-and-forth applies if any decision needs re-airing.
> - Do not write to `domain-model.md` (that's Step 6d).
> - **Permission propagation rule:** adding a permission to a lower role propagates upward in the chain by default; non-chain changes require explicit user signal.
> - **Recommendation strength:** state confidence on recommendations; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6a complete; Step 6b core complete; Step 6b-residual complete; Step 6c-i complete; Step 6c-ii complete — ADR-0047 (per-command authorization predicate table); Step 6b-residual-2 complete — 14a ADR-0042 (write-off model) + 14b ADR-0046 (registry reclassification + per-blocker default-resolution commands); Step 6c-iii split into 6c-iii-a + 6c-iii-b; Step 6c-iii-a complete — ADR-0044; Step 6c-iv split Option A into 6c-iv-a + 6c-iv-b; Step 6c-iv complete — 6c-iv-a (ADR-0043) + 6c-iv-b (ADR-0045 contract-scoping retrofit); Step 6c-iii-b split 2026-05-15 (signals 1/3/5) into 6c-iii-b-i + 6c-iii-b-ii; Step 6c-iii-b-i complete — ADR-0048 (WABundle restructure surface — WA Code reparenting + `level` discriminator + WABundle.sites + project-derivation-through-`wa_code` + cascade-keep-FK + WACodeAssignment rename + WACodeConf); **next: Step 6c-iii-b-ii** (WA Code removal model — item 6), then Step 6d)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0048)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
