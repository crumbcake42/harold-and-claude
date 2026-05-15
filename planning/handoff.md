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

**Session 15 — Step 6c-ii predicate-table ADR write. ✓ COMPLETE (2026-05-15, ADR-0047).** Case 3 scoped — deliberation already done in chat across sessions 12–13; this session was the ADR write itself. Pure ADR write; no cumulative-table changes (no entity / role / pattern / blocker-registry deltas). **Step 6c-ii is now closed.**

**ADR-0047 — Per-command authorization predicate table; class-rule clauses for unnamed commands; non-uniform predicates called out.** Per-`(role, command)` predicate table for the full Step 6b + Step 6b-residual + Step 6b-residual-2 + Step 6c command surface; resolves ADR-0012's per-command-predicate enumeration carry-forward. **Two row types:** (a) explicit per-command rows for ADR-named commands; (b) class-rule clauses for unnamed commands grouped by entity scope. **Three class rules** — Cluster 1 admin-roster CRUD on {Employee, School, Contractor, User} → `role >= admin`; Cluster 4 Time Entry CRUD + DepFiling CRUD + per-`document_type` lifecycle dispatch (ADR-0024) → `role >= coordinator`. **Non-uniform rows called out explicitly:** `grant_user_role` / `revoke_user_role` parameterized per ADR-0040 grant authority (target ∈ {coordinator, auditor} → `role >= admin`; target ∈ {admin, superadmin} → `role == superadmin`); `edit_note` creator-only (`caller == note.created_by`, non-chain — superadmin not exempt — applies to `regular` Notes only, audit Note subtypes are immutable regardless); `edit_wabundle` `role >= admin` per ADR-0044 (sits among WA-domain commands that are otherwise `role >= coordinator`). **Four locked clarifications codified** in the ADR itself: MVP-flat coordinator scoping; project-state immutability stays a pre-condition (ADR-0038, not in auth predicate); no system-caller primitive in the predicate vocabulary; `dismiss_wa_code` cascade-shape scope-flagged (Step 6c-iii-b's concern). **Cascade rule, propagation rule, evaluation-order rule** all codified. Amends ADR-0012, ADR-0040.

**`revoke_write_off` inclusion decision.** Included in the table at `role >= coordinator` (not deferred alongside its command-shape work). Symmetry with the default-resolution family (same actor class produces and lifts write-offs → cleaner audit forensics); predicate independent of the shape's parameters and guards. Scope at this turn: scenario (a) — the general "lift a write-off" primitive (e.g., a Sample Batch written off when COC was broken, later restored when COC and Lab Report arrive). Scenario (b) — misattribution-on-closed-project recovery — documented in the ADR as a layered post-MVP compound that needs `revoke_write_off` + ADR-0038 closed-project exception + the post-MVP cross-project Sample Batch reassignment command.

**`split_entry` inclusion.** Included at `role >= coordinator` per cluster 7's pre-decided explicit-row treatment. Same rationale — the predicate is settled here; shape (split-point ergonomics, field-inheritance for `daily_log` / `wa_code` / off-site sub-intervals on resulting sub-entries, batch reassignment at boundary) is undefined and remains a carry-forward.

**Carry-forwards surfaced this session (folded into ADR-0047):**
- `revoke_write_off` command shape — still no home step (unchanged from ADR-0042 / ADR-0046).
- `split_entry` command shape — load-bearing for ADR-0046's `resolve_overlap` / `resolve_overlap_paired` compounds; when settled, those compound specs should be re-validated.
- ADR-0031 auto-draft regeneration suppression at closure-gate — flagged for ADR-0031 follow-up; not a predicate-table concern unless an amendment changes the user-facing surface.
- Step 6c-iii-b commands (WA-removal model — `dismiss_wa_code` narrowing, `removed` terminal, RFA hybrid line items, third WA origin) inherit `role >= coordinator` from class rules; non-uniform predicates land as explicit rows by amendment to ADR-0047 when those commands are introduced.
- Post-MVP per-project coordinator scoping triggers the chain-freeze (project-scoped rows become non-chain `role >= coordinator AND assigned_to(target.project)`); localized edit.
- Future non-chain roles (e.g., "rate-only admin," "external SCA-contact role"): each appends a column without refactoring existing rows.

**Cluster-predicate carry-forward blocks consumed.** The cluster-1–7 predicate state from sessions 12–13 plus the four locked clarifications, previously carried in this handoff for the predicate-table ADR write, are now fully encoded in ADR-0047. Those blocks have been removed from this summary on session-close — ADR-0047 is the source of truth.

**Restructure session backlog (Step 6c-iii-b — remainder after Step 6c-iii-a):**

Surfaced during the WAAuthorization naming discussion. User pushed back on three points: (a) WA Code instance vs. the underlying code-type *config* are different things — codes are static enough to be code-side configuration; (b) reassignment is *not* rare — amendments are routine (2–3 per WA) and inter-project WA shuffling is exactly the disorder this app mitigates; (c) WA's contractual lifecycle is independent of project assignment — "this WA was issued for this project" is a reconciliation between two independent histories. Backlog items: (1) **DONE in Step 6c-iii-a (ADR-0044)** — WABundle entity introduced (Project ↔ WABundle 1:1; WA → WABundle M:1); what remains for 6c-iii-b is reparenting **WA Codes** onto the bundle (they stay project-scoped per ADR-0020 until then). (2) **WACodeConf** as code-side static config for code types. (3) Rename **WAAuthorization** → likely `WACodeAssignment` (post-MVP budget priority). (4) **`reassign_wa_project(wa, new_project, move_work: bool)`** compound — `move_work` flag controls whether related Time Entries / Sample Batches follow the WA; default TBD. (5) **Time Entry / Sample Batch keep direct `project_id`** (settled session 12) — empirical-truth principle. (6) Post-MVP priorities locked: (a) budget tracking on WACodeAssignment, (b) draft invoice generation. **ADR amendments expected at 6c-iii:** ADR-0020, ADR-0027, ADR-0030, ADR-0031, ADR-0041. Mis-attribution `reassign_wa_project` carry-forward folds in here. **Session-14 addition (item 6) — WA Code removal model:** `dismiss_wa_code` narrowed to `expected`/`pending_rfa` → `dismissed` (no hard-delete, optional `reason_text` → `audit_reason` Note); new `removed` terminal for issued-code removal; RFA becomes a hybrid instrument (`add`/`remove`/`budget` line-item types, additions system-derived + removals coordinator-authored, `approve_rfa` composition `(prior ∪ adds) \ removes`); third WA origin identified (SCA-direct corrected amendment, needs diff-based reconciliation); shared removal cascade across three triggers. Touchpoints: ADR-0027/0029/0030/0031/0033. Step 6b-residual-2's item 5 (WA-Code-scoped Document orphan cascade) dissolved here. This addition likely pushes 6c-iii past one window — Case 2 sizing when it is reached. Full brief in `steps.md` → Step 6c-iii.

**Cumulative tables — ADR-locked through ADR-0047.** ADR-0047 (session 15 — Step 6c-ii) writes the per-`(role, command)` authorization predicate table for the full command surface and resolves ADR-0012's per-command-predicate enumeration carry-forward. No cumulative-table deltas this session — entity roster, history-pattern / delete-policy assignments, role catalog, design-pattern menu, and blocker registry are all unchanged. The role catalog's propagation rule (adding a permission to a lower role propagates upward unless explicitly signaled) is restated below as a reminder.

**Per-`document_type` assignments (cumulative):**

| Pattern | document_types |
|---|---|
| Simple `missing → saved` | ACP13, ACP7, ACP15, ACP21, Emergency Notification, ACP8, VAR9 (all DepFiling docs — issued externally); COC; Daily Log |
| Cycling-family | CPR (RFA/RFP fork, 5 dates), FAMR (single-step review) |
| Bespoke | Lab Report (3 states: `missing`, `saved`, `invalid`; 4 transitions including `saved → invalid` for coordinator-discovered errors and `invalid → saved` for amended reports); RFP (4 states: `missing`, `saved`, `rejected`, `withdrawn`; SCA closure-receipt artifact per ADR-0037; `rejected` and `withdrawn` terminal; no `invalid` path since RFPs are SCA-side) |

**Entity roster (20 entities):**

| # | Entity | Notes |
|---|---|---|
| 1 | Project | SCA engagement. States: `active` / `closed` / `cancelled` (ADR-0037). Reopen permitted from both terminals. `close_project(project, rfp_file)` consumes ADR-0032 closure gate + transitions RFP `missing → saved` atomically; `cancel_project(project)` cascades RFA/pending-WA cleanup; `reopen_project` from `closed` cycles the RFP, from `cancelled` is state-flip only. Project is a Document-derivation source per ADR-0015: exactly one non-terminal RFP per project at any time. **Project ↔ WABundle 1:1 (ADR-0044)**; contract derives via `Project → WABundle → Contract` — no `Project.contract_id` (removed by ADR-0044). `create_project` is a Project + WABundle + v0-WA compound. |
| 2 | School | = Site for MVP. |
| 3 | WA | A **version** within a WABundle (ADR-0044): `wabundle_id` M:1, `version_seq` 0-based unique-per-bundle (replaces ADR-0017's `supersedes`; v0 initial, v1+ later). States: `pending` / `issued` / `superseded` (ADR-0030). WA → Project derived via the bundle. Per-version `issued_date` + `initialization_date` (null while `pending`, set at issuance). Lists contractors via ContractorEngagement (ADR-0041); authorizes WA Codes via WAAuthorization (ADR-0041). |
| 4 | WA Code | Project-scoped line item (ADR-0020). States: `expected` / `pending_rfa` / `rfa_in_review` / `issued` / `budget_rfa_needed` (deferred) / `dismissed` (ADR-0027). Linked to WAs via WAAuthorization (ADR-0041). Default flat fee is a contract-derived read-time value — `Contract.code_flat_fee_schedule[code_type]` via the contract-resolution path (ADR-0045); distinct from the per-`(WA, code)` `budget`. |
| 5 | User | Auth identity (username/password). 0..1 typed reference to Employee via nullable `employee_id` (UNIQUE-constrained per ADR-0041). |
| 6 | Employee | Person doing project work; linked to User via `User.employee_id?` (0..1 ↔ 0..1, ADR-0041). |
| 7 | EmployeeRole | Temporal work-license assignment + rate-carrier: `(id, employee_id, role_type, contract_id, rate, start_date, end_date?)` (ADR-0035; `contract_id` mandatory M:1 → Contract per ADR-0045). Full-day closed-closed range. Disjoint-ranges-per-`(employee, role_type, contract)` invariant (ADR-0045 — was per-`(employee, role_type)`; rows on different contracts may overlap in time). Looked up by `(employee_id, role_type, contract, date)` at rate-resolution / blocker / closure-gate time (no FK from Time Entry per ADR-0041; `contract` resolved via the contract-resolution path `→ project → WABundle → contract`). |
| 8 | UserRole | App-access role: `(user_id, role_type)` composite key (ADR-0036). No timestamps, no state. Grant creates row; revoke hard-deletes; audit on User's log. Drives authorization predicates per ADR-0012 + ADR-0040 role catalog. |
| 9 | Time Entry | Billable time record. Self-describing schema (ADR-0041 amends ADR-0035): `employee_id` (M:1 direct), `role_type` (enum), `project_id` (M:1 direct), `site_id` (M:1 direct), `wa_code_id` (M:1 mandatory at create, nullable via dismiss cascade), `date`, `on_site_range`, `off_site_sub_intervals` (ADR-0034). Sub-intervals ⊆ on-site range, pairwise disjoint. EmployeeRole is a derived/validated link, looked up by `(employee, role_type, contract, date)` (ADR-0045); rate resolved at billing time. |
| 10 | Sample Batch | COC group. Carries sample type, TAT, composition `[{subtype, quantity}]`, `site_id` (M:1 mandatory direct per ADR-0041), `sampling_locations` (optional plain text per ADR-0041), employee reference (collector), collection time. WA Code reference (mandatory at create, nullable via `dismiss_wa_code` cascade — ADR-0027 + ADR-0042 amendment: nulling produces a cascade `write_off` Note on the batch). Stateless per ADR-0038. Document-derivation source (COC + Lab Report). |
| 11 | Document | Unified slot+file entity. Per-`document_type` lifecycle dispatch (ADR-0024). Single-scope via `(scope_type, scope_id)` discriminator+FK (`scope_type ∈ {project, deliverable, wa_code}`, ADR-0041). Derivation set: Deliverables (transitively WA Codes), DepFilings, Sample Batches, Project (ADR-0015 clarified by ADR-0041). Derivation fires on expected codes (ADR-0022). |
| 12 | Deliverable | SCA-portal submission package. Bundle is a query over scoped Documents: derived required Documents (from Deliverable) + user-added Documents scoped to this Deliverable + user-added Documents scoped to WA Codes that map to this Deliverable (ADR-0041 reframes earlier "M:M" framing as single-scope on Document side). States: `pending_rfa` / `outstanding` / `under_review` / `approved` (ADR-0029). `wasted` derived flag. |
| 13 | Contractor | On-site abatement (or other) third party. Admin-side roster. Linked to WAs via ContractorEngagement (ADR-0041). |
| 14 | RFA | Request for Amendment; carries pending WA edits. M:1 mandatory `amends_wa_id` direct typed ref to WA, set at auto-draft creation (post-WA-issuance), immutable for RFA lifetime (ADR-0041). Project derived via WA → Project. May be auto-created during WA issuance reconciliation. |
| 15 | Note | Polymorphic commentary; typed reference to any entity OR history record (ADR-0040). Subtypes `regular | blocker | resolution | audit_reason | write_off` (ADR-0032, ADR-0040, ADR-0042). `authorship_class: 'user' | 'system'` + nullable `created_by`. Inter-Note `references` field. Regular Notes are creator-editable per ADR-0018; blocker, resolution, audit_reason, write_off Notes are immutable. Not deletable. |
| 16 | DepFiling | TRU-numbered regulatory filing bundle (ADR-0023). Project-scoped; editable `required_doc_types` set; Document-derivation source. No lifecycle. |
| 17 | WAAuthorization | Associative entity for WA ↔ WA Code M:N. Composite key `(wa_id, wa_code_id)`. No additional fields in MVP; gains budget when budget tracking lands. (ADR-0041) |
| 18 | ContractorEngagement | Associative entity for WA ↔ Contractor M:N with stint state. `(wa_id, contractor_id, started_at, ended_at?)`. Multiple rows per `(wa_id, contractor_id)` permitted when contractor closes CPR filing and is re-added. CPR Document derives per row. (ADR-0041) |
| 19 | Contract | Contractual basis a project is opened against (ADR-0043). Schema: `contract_number` (uniqueness-constrained natural key), `start_date` / `end_date?`, `code_flat_fee_schedule` (inline non-temporal `{code_type, fee}` collection), optional `name` (null → derived display label `C` + last 5 chars of `contract_number`). No state machine — `pending` / `active` / `expired` derived from dates. Audit log; soft delete. Employee rates are FK-side (EmployeeRole carries a mandatory `contract_id` per ADR-0045); code default flat fees inline here. **Re-attached to the WABundle by ADR-0044**: `WABundle.contract_id` M:1 required (was `Project.contract_id`); mutable via `issue_wa` / `edit_wabundle`. |
| 20 | WABundle | Contractual-identity entity above the WA version chain (ADR-0044). Schema: `id`, `contract_id` (M:1 → Contract, required at create), `project_id` (M:1 → Project, UNIQUE — 1:1), `wa_number` / `service_id` / `job_number` (each uniqueness-constrained; nullable pre-issuance, required once a WA is issued — `issue_wa` populates them; `wa_number` is the human-facing natural key; `job_number` is SCA's WA id, distinct from the project number). Holds the WA chain (WA → WABundle M:1). No state machine — contract `expected` status derived (`wa_number IS NULL`). Audit log; soft delete. `edit_wabundle` (`role >= admin`) corrects metadata post-issuance. |

Values / lookups (not entities): Sample Type, Sample Subtype, Project Type, TAT options, status enums, `document_type` registry, DepFiling template constants.

**Per-entity history-pattern assignments:**

| Pattern | Entities |
|---|---|
| Comprehensive capture | Document, WA, RFA |
| Lifecycle capture | Project, Sample Batch, Deliverable, EmployeeRole, WA Code, ContractorEngagement |
| Audit log | Employee, User, Time Entry, Contractor, DepFiling, Contract, WABundle |
| No history | School, Note, UserRole, WAAuthorization |

**Per-entity delete policy:**

| Policy | Entities | Notes |
|---|---|---|
| Soft delete (guarded hard-delete eligible) | Document, WA, RFA, Project, Sample Batch, Deliverable, EmployeeRole, Employee, User, Time Entry, Contractor, WA Code, DepFiling, ContractorEngagement, Contract, WABundle | History-carrying or referenced by history records. |
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

11 `has-default-resolution` + 1 `fix-only` (#10 — coherence-test failure, closure-definitional). #4 flagged in `post-mvp.md` as drop-candidate if MVP operation confirms it cannot fire in practice.

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
- **Blocker** — A structural condition (registry entry from ADR-0032) or user-flagged Note declaring something is held up. Every registry blocker has a structural-fix path; the ADR-0042 reframe replaces the dismissable/fix-only binary with the derived property **has-default-resolution** vs. **fix-only**. The 12-entry registry is reclassified by ADR-0046: 11 `has-default-resolution`, 1 `fix-only` (#10).
- **Materialized blocker** — A blocker that exists as a persisted Note record (vs purely-derived, registry-only). System-derived blockers materialize on first user engagement.
- **Engagement** — A coordinator writing a comment about a blocker or invoking its default-resolution / dismissal. The trigger for lazy materialization of system-derived blockers.
- **Chain-dismissal (post-ADR-0046)** — When resolving one blocker structurally implies secondary entities should also leave the not-written-off domain, the registry entry declares a `chain` shape; resolution atomically emits direct `write_off` Notes on the chained entities, each inheriting the primary's `justification`, `references` the primary blocker Note. The MVP-named chain shape is `te_batches_by_coverage` (#5, #8, #11, #12 — see below). The older "null `wa_code` + materialize #2 + auto-dismiss #2" mechanic from ADR-0033 / ADR-0039 is superseded.
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
- **Contract** — the contractual basis a project is opened against (ADR-0043). Carries a `contract_number` (uniqueness-constrained natural key), a `start_date` / `end_date?` term, an inline non-temporal `code_flat_fee_schedule`, and an optional `name`. No state machine — validity (`pending` / `active` / `expired`) is derived from the term + clock. Employee billing rates are contract-scoped FK-side (EmployeeRole carries a mandatory `contract_id`, ADR-0045); code default flat fees are contract-defined inline. **Re-attached to the WABundle by ADR-0044**: the contract reference is `WABundle.contract_id` (M:1, required at create) — `Project.contract_id` removed, `Project → Contract` derives via the bundle. Mutable: `issue_wa` sets/confirms it at issuance, `edit_wabundle` (`role >= admin`) corrects it after.
- **`code_flat_fee_schedule` (Contract)** — an inline value collection of `{code_type, fee}` pairs on Contract: the default flat fee per WA code type for that contract. Non-temporal — fixed once for the contract's whole life. The code-type catalog itself (`WACodeConf`) is Step 6c-iii's work. (ADR-0043). A code type absent from the schedule resolves to null/unpriced — no blocker (ADR-0045).
- **Contract-resolution path** — the shared derivation `entity → project → WABundle → contract` by which a Time Entry or WA Code resolves its governing Contract (ADR-0045). Always resolves — `create_project` guarantees a WABundle with a required `contract_id` (ADR-0044). Cited by both consumers — EmployeeRole rate resolution and the WA Code default-flat-fee lookup; money values (rates, flat fees) are derived through the live `WABundle.contract_id`, never snapshotted (the basis for ADR-0044 dissolving `reassign_project_contract`).
- **`audit_reason` (Note subtype)** — immutable Note subtype attached to history records via optional `reason_text` on grant/revoke commands (ADR-0040).
- **`amends_wa_id`** — RFA's mandatory direct typed reference to the WA being amended; set at auto-draft creation, immutable for RFA lifetime (ADR-0041).
- **`scope_type` / `scope_id` (Document)** — single-scope discriminator + FK on Document; `scope_type ∈ {project, deliverable, wa_code}` (ADR-0041).
- **`site_id` (Time Entry, Sample Batch)** — M:1 mandatory direct typed reference to School; the structural site-of-work link (ADR-0041).
- **`sampling_locations` (Sample Batch)** — optional plain-text field describing specific spots within the site where samples were collected (ADR-0041).
- **Derived/validated link** — a relationship resolved by lookup rather than FK. Used in ADR-0041 for Time Entry ↔ EmployeeRole: rate / blocker / closure-gate logic looks up the covering EmployeeRole row from `(employee_id, role_type, contract, date)` at use time (the `contract` dimension added by ADR-0045, resolved via the contract-resolution path).
- **WABundle** — the contractual-identity entity above the WA version chain (ADR-0044). 1:1 with Project; holds the WA chain (WA → WABundle M:1). Carries `contract_id` (required at create), `wa_number` / `service_id` / `job_number` (SCA-supplied; `job_number` is SCA's WA id, distinct from the project number, which is our own tracking id; all three nullable pre-issuance, required at issuance). Audit log, soft delete, no state machine.
- **Version / `version_seq` (WA)** — a specific WA within a WABundle. `version_seq` is a 0-based integer, unique per bundle; the head WA is the max `version_seq`. v0 is the initial WA, v1+ are later versions (an approved RFA produces the next version). Replaces ADR-0017's `supersedes` self-reference; `version_type` becomes derivable (`initial ⟺ version_seq == 0`). (ADR-0044)
- **`issued_date` / `initialization_date` (WA)** — per-WA-version date fields, null while `pending`, populated at issuance. `issued_date` = when SCA issued the document; `initialization_date` = the date work under the WA is authorized to begin from (supersedes ADR-0017's `effective_date`). A new WA version may revise both. The head WA's `initialization_date` drives the WA-initialization closure blocker (ADR-0044): a Time Entry dated before it is blocked; null ⇒ never fires. Changed post-issuance only by issuing a new WA version. (ADR-0044)
- **`edit_wabundle`** — `role >= admin` command for post-issuance corrections to WABundle metadata (`contract_id`, `wa_number`, `service_id`, `job_number`). Distinct from `issue_wa`, which (coordinator) sets/confirms those four SCA-supplied facts at issuance. Non-uniform predicate — carry-forward for the Step 6c-ii predicate-table ADR. (ADR-0044)
- **`default_resolve(blocker, justification)`** — the generic Hybrid-shape default-resolution command for the 8 `has-default-resolution` registry entries declaring `command_shape: generic` (#1, #2, #3, #4, #5, #6, #9, #11, #12). Materializes the blocker if derived-only, writes off the registry-declared target entity, emits chained `write_off` Notes if a `chain` is declared, writes one `resolution` Note (`resolution_kind: default_resolution`). `role >= coordinator`. (ADR-0046)
- **`resolve_overlap(blocker_note, justification)`** — single-side named compound for #8 (cross-project time overlap). Splits the engaging side's Time Entry at the overlap boundaries, writes off the resulting sliver, chains to batches via `te_batches_by_coverage`; the other side's paired blocker resolves derivationally via ADR-0032's auto-`structural_fix` Note. (ADR-0046)
- **`resolve_overlap_paired(paired_blocker_note, justification)`** — joint named compound for #8. Splits both Time Entries at the overlap boundaries, writes off both slivers, chains to batches on both sides; emits `resolution` Notes (`resolution_kind: default_resolution`) on both materialized paired blocker Notes. Audit-symmetric across both projects. (ADR-0046)
- **`resolve_open_rfa(rfa, justification)`** — named compound for #7 (open `draft`/`in_review` RFA at closure, MVP add/remove-RFA case only). Invokes `withdraw_rfa` → cascade `dismiss_wa_code` on returned codes → cascade `write_off` Notes on referencing Time Entries / Sample Batches via the existing ADR-0027 + ADR-0042 reference-nulling cascade → auto-draft regeneration empties itself naturally (empty-draft hard-deletes per ADR-0031). `role >= coordinator`. Out of scope MVP: budget-RFA case (would be `fix-only` if introduced; reclassification deferred behind budget tracking). (ADR-0046)
- **`te_batches_by_coverage`** — named chain shape. For a target Time Entry `TE`, the chained set is `{ batch : batch.employee == TE.employee AND batch.collection_time ∈ TE.on_site_range }` (half-open per `split_entry`'s carry-forward). Each chained batch receives a direct `write_off` Note inheriting the primary's `justification`, `references` the primary blocker Note. Used by #5, #8 (per sliver), #11, #12. The MVP-named chain shape under pattern #12. (ADR-0046)
- **Fork A** — the narrow relink-gate relaxation on ADR-0033's `relink_sample_batch_wa_code`: gate's permitted-state set extends from `{wa_code IS null, current code dismissed}` to `{wa_code IS null, current code dismissed, batch trips #9}`. Unblocks misfile recovery for healthy-`wa_code` batches without a write-off-then-relink dance. Composes independently with the planned `removed`-branch amendment from Step 6c-iii-b. (ADR-0046)

## Open questions

*(Step 6c-ii open questions — per-`(role, command)` predicate table + class-rule clauses + non-uniform predicate call-outs + `revoke_write_off` inclusion + `split_entry` inclusion + four locked clarifications codified — all resolved in ADR-0047; **Step 6c-ii is complete**. Step 6b-residual-2 open questions resolved in ADR-0046 (14b) and ADR-0042 (14a); **Step 6b-residual-2 is complete**. Step 6c-iv-b's — EmployeeRole `contract_id` cardinality + disjoint-ranges restructure + rate-resolution path + WA Code default-flat-fee lookup + blast-radius bound — in ADR-0045; **Step 6c-iv is complete**. Step 6c-iii-a's — WABundle definition, WA restructure, contract re-attachment, WA-initialization closure blocker — in ADR-0044. Step 6c-iv-a's — Contract attachment-model fork, attributes/identity, lifecycle/history/delete, Project → Contract wiring — in ADR-0043.)*

**For the next session — Step 6c-iii-b (WA-domain restructure remainder):**

The Step 6c-iii-b session covers the WA-domain restructure deferred behind Step 6c-iii-a (WABundle entity, ADR-0044) and the Step 6c-ii predicate-table ADR (ADR-0047). Six items in scope per `steps.md` § Step 6c-iii-b — paraphrased here:

1. **WA Code reparenting onto the WABundle** (replaces ADR-0020's project-scoping). Project ↔ WABundle is 1:1 (ADR-0044), so the move is mechanical but touches ADR-0020 and the `code → contract` resolution path (currently `code → project → WABundle → contract` per ADR-0045; the reparent shortens to `code → WABundle → contract`).
2. **`WACodeConf` as code-side static config** for the code-type catalog. Possibly code-side rather than a DB entity. Step 6c-iv-b's WA Code default flat fee against contract (ADR-0045) inherits whatever shape lands here.
3. **Rename `WAAuthorization`** to a name aligned with the new shape and the immediate-post-MVP budget priority. Top contender `WACodeAssignment`.
4. **`reassign_wa_project(wa, new_project, move_work: bool)`** compound — `move_work` flag controls whether related Time Entries / Sample Batches follow the WA or stay on the original project. Default value settled here. Mis-attribution carry-forward folds in.
5. **Confirm Time Entry / Sample Batch keep direct `project_id`** (settled session 12 per the empirical-truth principle) and surface in the relationship table refresh.
6. **WA Code removal model + `dismiss_wa_code` narrowing + third WA origin** (deliberated session 14, productive tangent off Step 6b-residual-2 sizing; shape is settled, this step writes it up). Includes: `dismiss_wa_code` narrowed to `expected`/`pending_rfa` targets only (drops the `issued → dismissed` transition, drops ADR-0027's delete-substitution; optional `reason_text` → `audit_reason` Note); new `removed` terminal state for issued-code removal; RFA becomes a hybrid instrument (`add` / `remove` / `budget` line-item types, additions system-derived + removals coordinator-authored, `approve_rfa` composition `(prior ∪ adds) \ removes`); third WA origin (SCA-direct corrected amendment, needs diff-based reconciliation); shared removal cascade across three triggers (`dismiss_wa_code`, `approve_rfa` removal line items, SCA-direct amendment path).

**Sizing watch.** The session-14 addition of item 6 (WA Code removal model) likely pushes 6c-iii-b past one window. Run Case 2 sizing at the head of the session — `_workflow.md` Case 2 fit checklist.

**Predicate-table amendment expectation.** Any new commands introduced by 6c-iii-b inherit `role >= coordinator` from class rules (Cluster 3 named-WA-domain class rule for WA / WA Code / RFA-adjacent commands, Cluster 4 for SBatch / Document / Deliverable / DepFiling / TE — see ADR-0047). Non-uniform predicates land as explicit-row amendments to ADR-0047 when introduced. `dismiss_wa_code`'s `reason_text?` parameter is a signature change, not a predicate change.

**Touchpoints / amendments expected at 6c-iii-b:** ADR-0020 (WA Code scoping rationale; reparenting onto WABundle), ADR-0027 (WA Code state machine — `dismissed` kept, `removed` added, `dismiss_wa_code` narrowed, delete-substitution dropped, design pattern #9's hard-delete branch no longer exercised by WA Code), ADR-0029 (`wasted` flag re-derivation — extend trigger `dismissed` → `dismissed OR removed`), ADR-0030 (WA's project relationship via bundle + third WA origin / `issue_wa` generalization), ADR-0031 (RFA's bundle-vs-project routing + hybrid line-item model), ADR-0033 (relink guard gains a `removed` branch; composes independently with Fork A from ADR-0046), ADR-0041 (relationship table refresh).

**Deferred behind Step 6c-iii-b:**
- **`split_entry` command-shape** — predicate is `role >= coordinator` (explicit row in ADR-0047); the command's actual shape (split point, field-inheritance for `daily_log` / `wa_code` / off-site sub-intervals on resulting sub-entries, batch reassignment at boundary) is undefined and has no natural home step. **Load-bearing for ADR-0046's `resolve_overlap` / `resolve_overlap_paired` compounds** — when settled, those compound specs should be re-validated. Candidate: Step 6d or a residual. ADR-0042 carry-forward — half-open interval semantics: Time Entry ranges are `[start, end)`.
- **`revoke_write_off` command shape** — predicate is `role >= coordinator` (explicit row in ADR-0047, scenario (a)); parameters and guards undefined; no home step yet (candidate: alongside `split_entry`). Scenario (b) — misattribution-on-closed-project recovery — needs `revoke_write_off` + ADR-0038 closed-project exception + the post-MVP cross-project Sample Batch reassignment command; layered, post-MVP.
- **ADR-0031 gap — auto-draft regeneration suppression at closure-gate.** Suppressed on cancelled projects but silent on projects in closure-gate evaluation. ADR-0046's `resolve_open_rfa` compound resolves itself; the bare `withdraw_rfa` structural-fix path during closure-gate can loop. Flagged for ADR-0031 follow-up; may fold into 6c-iii-b if the RFA hybrid-line-item model rewrites that ADR enough that the gap can be closed cheaply.

**Carry-forwards worth re-checking when relevant:**
- ~~**`reassign_project_contract` (post-MVP)**~~ — **dissolved by ADR-0044.** Already removed from `post-mvp.md`.
- **ContractorEngagement command-shape** — `start_contractor_engagement` / `end_contractor_engagement` predicates are `role >= coordinator` (ADR-0047); signatures + pre-conditions deferred to Step 6c-iii-b (ContractorEngagement is in that restructure's blast radius). Date defaults: `started_at` → row-creation date; `ended_at` → CPR-saved date (nullable, overridable).
- **Cross-project Sample Batch reassignment as a structured command**: in `post-mvp.md` alongside notifications.
- **Retroactive rate corrections via Time-Entry rate snapshot** (carry-forward from ADR-0035): reversible additive change post-MVP if signal emerges.
- **Security-immediate revoke runtime semantics** (session invalidation on `revoke_user_role`): implementation concern, deferred to auth implementation step.

**Carried forward (deferred to later steps):**
- **WACodeAssignment budget fields** (current name: WAAuthorization budget fields) — added when budget tracking design lands; immediate post-MVP per user signal.
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

**Step 6c-iii-b — WA-domain restructure remainder (WA Code reparenting onto WABundle, `WACodeConf`, `WAAuthorization` rename, `reassign_wa_project` compound, WA Code removal model + `dismiss_wa_code` narrowing + third WA origin).** Fresh **Case 2 sizing required** entry — the brief in `steps.md` carries six items, and the session-14 addition of item 6 (WA Code removal model) likely pushes scope past one window. Run the Case 2 fit checklist at the head of the session before proposing deliberation order; split into 6c-iii-b-i / 6c-iii-b-ii if a signal fires. Brief in `steps.md` → Step 6c-iii-b. Execution order going forward: 14a ✓ → 6c-iv-a ✓ → 6c-iii-a ✓ → 6c-iv-b ✓ → 14b ✓ → 6c-ii ✓ → **Step 6c-iii-b** → 6d.

### Prompt for the next session

> Resume work. Next is **Step 6c-iii-b — WA-domain restructure remainder**, a **fresh Case 2 sizing** entry (six items in the brief — the session-14 addition of item 6 likely pushes scope past one window). Per `_workflow.md` Case 2: read the step brief in `steps.md` → § Step 6c-iii-b; run the seven-signal fit checklist; if any signal fires, surface partitioning options in chat (do not write to `steps.md` until consensus). On consensus → fall through to Case 3 for the first sub-step. If the checklist clears, fall through to Case 3 for the whole step.
>
> **Read first:** this prompt + the Open questions block above (Step 6c-iii-b restatement of the six items, deferred items, touchpoints) + this handoff's **Restructure session backlog** block (Step 6c-iii-b detail surfaced session 12 + session-14 item-6 addition). From `decisions.md`: **ADR-0044** (WABundle entity — the reparent target), **ADR-0046** (write-off model + per-blocker default-resolution commands — the reference-nulling cascade in item 6 inherits write-off semantics), **ADR-0042** (write-off model substrate), **ADR-0047** (predicate table — new commands inherit class rules; non-uniform predicates land as amendments to ADR-0047 if any emerge). Step 6b core ADRs to amend: **ADR-0020** (WA Code scoping), **ADR-0027** (WA Code state machine), **ADR-0029** (`wasted` re-derivation), **ADR-0030** (WA state machine + third WA origin / `issue_wa` generalization), **ADR-0031** (RFA state machine + hybrid line-item model), **ADR-0033** (relink-guard `removed` branch), **ADR-0041** (relationships).
>
> **Six items in scope (full text in `steps.md` → Step 6c-iii-b):**
> 1. WA Code reparenting onto WABundle (replaces ADR-0020's project-scoping).
> 2. `WACodeConf` as code-side static config for code types.
> 3. Rename `WAAuthorization` → likely `WACodeAssignment`.
> 4. `reassign_wa_project(wa, new_project, move_work: bool)` compound — `move_work` default value settled here.
> 5. Confirm Time Entry / Sample Batch keep direct `project_id`.
> 6. WA Code removal model — `dismiss_wa_code` narrowed (`expected`/`pending_rfa` targets only, optional `reason_text` → `audit_reason` Note); new `removed` terminal for issued-code removal; RFA hybrid line items (`add` / `remove` / `budget`-deferred); third WA origin (SCA-direct corrected amendment with diff-based reconciliation); shared removal cascade across three triggers.
>
> **Sizing watch — signals to test against `_workflow.md` Case 2 checklist:**
> - **Signal 1 (independently-deliberable decisions):** items 1–5 are coupled (the WABundle restructure surface) — likely one decision. Item 6 is independently deliberable (own state-machine work, own cascade design, own touchpoints). Likely 2 signals on this axis.
> - **Signal 2 (artifacts to draft):** one or two ADRs depending on whether item 6 lands as a separate ADR or a section of the restructure ADR.
> - **Signal 3 (duration estimate):** the brief itself flags >60 min for item 6 alone given the cascade design and 5+ amendments.
> - **Signal 5 (cross-concern reach):** items 1–5 are entity/relationship work; item 6 is state-machine + command surface + RFA model — different concern axes.
>
> If any signal fires, propose a split (likely 6c-iii-b-i = items 1–5, 6c-iii-b-ii = item 6) in chat before writing to `steps.md`. STOP-AND-CONFIRM gate applies to both the partition and any subsequent ADR writes.
>
> **Out of scope — do not pull in:**
> - Budget tracking on `WACodeAssignment` (post-MVP per session 14 user signal).
> - Draft invoice generation (post-MVP, second priority).
> - `split_entry` / `revoke_write_off` command shapes (predicates landed in ADR-0047; shape design carries forward).
> - Per-project coordinator scoping (post-MVP; triggers ADR-0047 chain-freeze when it lands).
>
> **Sequencing:** 14a ✓ → 6c-iv-a ✓ → 6c-iii-a ✓ → 6c-iv-b ✓ → 14b ✓ → 6c-ii ✓ → **Step 6c-iii-b (this session, Case 2 sizing first)** → 6d. ADR number at write time: next is ADR-0048.
>
> **Reference (full detail in the cumulative tables):** 20 entities; 14 design patterns; roles superadmin / admin / coordinator / auditor with the predicate table in ADR-0047; 12-entry blocker registry post-ADR-0046 (11 has-default-resolution + 1 fix-only). State machines locked through ADR-0045 — item 6 of 6c-iii-b reopens WA Code's state machine to add `removed` and narrow `dismiss_wa_code`.
>
> **Process notes:**
> - **Case 2 sizing is the first deliverable.** STOP-AND-CONFIRM gate applies to any `steps.md` partition write.
> - Casual back-and-forth applies if any decision needs re-airing.
> - Do not write to `domain-model.md` (that's Step 6d).
> - **Permission propagation rule:** adding a permission to a lower role propagates upward in the chain by default; non-chain changes require explicit user signal.
> - **Recommendation strength:** state confidence on recommendations; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6a complete; Step 6b core complete; Step 6b-residual complete; Step 6c-i complete; Step 6c-ii complete — ADR-0047 (per-command authorization predicate table); Step 6b-residual-2 complete — 14a ADR-0042 (write-off model) + 14b ADR-0046 (registry reclassification + per-blocker default-resolution commands); Step 6c-iii split into 6c-iii-a + 6c-iii-b; Step 6c-iii-a complete — ADR-0044; Step 6c-iv split Option A into 6c-iv-a + 6c-iv-b; Step 6c-iv complete — 6c-iv-a (ADR-0043) + 6c-iv-b (ADR-0045 contract-scoping retrofit); **next: Step 6c-iii-b** (Case 2 sizing first — rename + WA Code reparenting + WA-removal-model remainder, likely splits into 6c-iii-b-i / 6c-iii-b-ii), then Step 6d)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0047)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
