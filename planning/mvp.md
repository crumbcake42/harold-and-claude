# MVP Scope

## File contract

**Holds:** The MVP feature cut — ≤7 must-have features (each one sentence + brief expansion), the defensible "not now" list with per-item rationale, the in-MVP carve-outs that may slip, and the in-MVP command-shape carry-forwards whose mechanics land in the implementation phase (distinct from "not now").
**Update when:** A must-have is added or cut; a "not now" item is promoted to MVP; an in-MVP carve-out is resolved (kept or slipped); a command-shape carry-forward's mechanics are settled (move out of the carry-forward list). Source decision is ADR-0050; substantive shape changes require a superseding ADR before editing.

The Step 7 output. Built on the rolled-up domain in `planning/domain-model.md` (21 entities, 14 design patterns, 10-entry blocker registry, four-role authorization chain). The framing decision (D1) is **the MVP must be usable for new projects at introduction at the user's office**; the must-have list is "the model that covers what the office tracks today," and "not now" is "speculative surface no one at the office uses today."

---

## Must-have features (6 — under the ≤7 ceiling)

Notes commentary is folded into the closure-gate cluster as substrate (its load-bearing surfaces are the immutable Note subtypes for `write_off` / `blocker` / `resolution` / `audit_reason`, already implied by feature #5 and #6). Each feature's one-sentence statement is bolded; the expansion names the entities, commands, and ADR pointers it covers.

### 1. Project lifecycle

**`create_project` opens a Project + WABundle + v0-WA against a Contract; `close_project` consumes the closure gate and transitions RFP `missing → saved`; `cancel_project` cascades open RFA / pending-WA cleanup; `reopen_project` returns from either terminal (cycles the RFP from `closed`, pure flip from `cancelled`).**

Entities: Project (ADR-0037), Contract (ADR-0043), WABundle (ADR-0044). State machine `active` / `closed` / `cancelled` per ADR-0037. `create_project` is a compound (ADR-0044) — Project + WABundle + v0-WA + WABundleSite rows (ADR-0048's `sites` parameter). `close_project` invokes the closure gate (feature #5) and transitions the project's non-terminal RFP atomically. `cancel_project` cascades open RFA / pending-WA cleanup per the cascade-keep-FK principle (feature #2). `reopen_project` from `closed` requires `rfp_reason ∈ {rfp_rejected, rfp_withdrawn}` and cycles the RFP; from `cancelled` is a pure state flip. Project-state-driven immutability per ADR-0038 + design pattern #13.

### 2. WA + WA Codes + RFA cycle

**WA versioning under a WABundle (initial v0 in-place via `issue_wa`; amendment via `approve_rfa`; SCA-direct corrected amendment via generalized `issue_wa`); WA Code lifecycle `expected` / `pending_rfa` / `rfa_in_review` / `issued` / `dismissed` / `removed` with cascade-keep-FK on referencing Time Entries / Sample Batches; RFA `draft` / `in_review` / `approved` / `rejected` / `withdrawn` with hybrid `add` / `remove` line items.**

Entities: WA (ADR-0017, 0030, 0044, 0048, 0049), WA Code (ADR-0020, 0027, 0048, 0049), WACodeAssignment (ADR-0048 rename of WAAuthorization), RFA (ADR-0031, 0049). WA versioning: `version_seq` 0-based per bundle (ADR-0044), v0 transitions in-place at initial issuance (ADR-0048), v1+ are new rows. `issue_wa` is the generalized issuance command (ADR-0049) — dispatches on `bundle.head_version_seq IS NULL` (initial path with ADR-0022 reconciliation; SCA-direct path with diff reconciliation, hard-gated against `in_review` RFAs). WA Code's `level` (`project` / `building`) is required at create, denormalized from `WACodeConf[code_type].default_level`, immutable thereafter (ADR-0048). `dismiss_wa_code(wa_code, reason_text?)` narrowed to `{expected, pending_rfa}` targets (ADR-0049). `removed` reached from `issued` only via RFA-remove or SCA-direct dropped-code; both share the keep-FK removal cascade with `dismiss_wa_code` (ADR-0049 §5). RFA hybrid line items: `add` system-derived (ADR-0031), `remove` coordinator-authored via `add_rfa_line_item(bundle, code, type)` (ADR-0049); composition on approve `(prior ∪ adds) \ removes`.

### 3. Time Entries + Sample Batches

**Time Entry self-describes `(employee, role_type, site, date, on_site_range, off_site_sub_intervals)` against a WA Code; Sample Batch carries collection time + composition + TAT against a WA Code; both derive their evidence Documents (Daily Log link on Time Entry; COC + Lab Report on Sample Batch) and feed the cross-project overlap predicate.**

Entities: Time Entry (ADR-0034, 0041, 0042, 0048), Sample Batch (ADR-0033, 0038, 0048). Both carry `wa_code_id` (M:1 mandatory at create and post-cascade per cascade-keep-FK, ADR-0049 §5) and `site_id` (M:1 mandatory direct, ADR-0041); project derives via `wa_code → WACode → WABundle → Project` (ADR-0048). Time Entry's EmployeeRole link is a derived/validated lookup by `(employee, role_type, contract, date)` at use time (ADR-0035 + ADR-0045 — no FK). Off-site sub-intervals are pairwise disjoint within the parent `on_site_range`, positive-duration (ADR-0034). Gross on-site range drives the cross-project overlap predicate (blocker #8); net on-site time drives blocker #9. Sample Batch is stateless (ADR-0038) — workflow advances through derived Documents (COC created `saved`, Lab Report created `missing`, ADR-0033) and Deliverable containment. `relink_sample_batch_wa_code` permitted-state set settled at ADR-0049's restatement.

### 4. Documents + Deliverables + DepFilings

**Document per-`document_type` lifecycle dispatch (simple `missing → saved` for most types; cycling-family for CPR / FAMR; bespoke for Lab Report and RFP); Deliverable bundle as a derived query over scoped Documents + `submit_deliverable` / `approve_deliverable` / `reject_deliverable` / `withdraw_deliverable`; DepFiling with TRU + editable `required_doc_types` for regulatory filing.**

Entities: Document (ADR-0014, 0015, 0024, 0037, 0041), Deliverable (ADR-0022, 0029, 0041, 0042), DepFiling (ADR-0023). Document is the unified slot-and-file entity, single-scope via `(scope_type, scope_id)` with `scope_type ∈ {project, deliverable, wa_code}` (ADR-0041). `document_type`s in MVP: ACP{7,8,13,15,21}, VAR9, Emergency Notification (DepFiling-issued externally); COC; Daily Log; CPR (cycling-family, 2 buckets, 5 tracking dates); FAMR (single-step review); Lab Report (bespoke 3-state with `invalid` for coordinator-discovered errors); RFP (bespoke 4-state, `rejected` / `withdrawn` terminal). Deliverable's bundle is a query over scoped Documents (derived-required + user-added at the Deliverable + user-added at contained WA-Code scope); frozen at `submit_deliverable`, re-opens on reject. DepFiling is TRU-numbered, project-scoped, with editable `required_doc_types` driving Document derivation.

### 5. Closure gate + blockers + write-off

**10-entry blocker registry derived over not-written-off entities (9 has-default-resolution + 1 fix-only); lazy materialization on coordinator engagement; default-resolution family (`default_resolve` + named compounds `resolve_open_rfa` / `resolve_overlap` / `resolve_overlap_paired`*); write-off Note subtype + `revoke_write_off`; chain-dismissal `te_batches_by_coverage`; polymorphic Notes substrate (immutable system subtypes + creator-editable `regular`).**

ADRs: 0032 (registry + materialization), 0042 (write-off model + nuclear-guard), 0046 (registry classification + per-blocker commands), 0018 (Note authorship + edit), 0040 (Note polymorphism + subtypes), 0049 (registry trim to 10 entries post-cascade-keep-FK). Closure gate fires on `close_project` against the live registry over the not-written-off entity set (design pattern #3 + #14). Lazy materialization (pattern #11): derived blockers stay derived until a coordinator comments, dismisses, or default-resolves; first engagement materializes a system-authored `blocker` Note with `surfaced_at` backfilled. Default-resolution is the nuclear option (guarded, mandatory justification, never auto-invoked); writes a `write_off` Note on the conflicting entity (and chained entities via the registry's `chain` field). Chain `te_batches_by_coverage` covers blockers #5, #8, #11, #12 (writes direct `write_off` Notes on `{ batch : batch.employee == TE.employee AND batch.collection_time ∈ TE.on_site_range }`). `revoke_write_off` lifts a write-off via immutable superseding Note (predicate settled, parameters carry-forward — see § Command-shape carry-forwards). Notes commentary: `regular` subtype creator-editable (ADR-0018, even `superadmin` cannot edit another user's Note); `references` chains Notes; polymorphic typed ref to any entity OR history record (ADR-0040). *Carve-out: `resolve_overlap_paired` may slip — see § Carve-outs.*

### 6. Roster + role administration

**Admin-side CRUD on Employee / School / Contractor / User; EmployeeRole with temporal rates keyed on `(employee, role_type, contract)`; UserRole `grant_user_role` / `revoke_user_role` with conservative grant authority (target-role-parameterized per ADR-0040); ContractorEngagement `start_contractor_engagement` / `end_contractor_engagement` with date defaults.**

Entities: Employee (ADR-0035), School (substrate), Contractor (ADR-0041), User (ADR-0036), EmployeeRole (ADR-0035, 0045), UserRole (ADR-0036, 0040), ContractorEngagement (ADR-0041). Class rule `role >= admin` covers the admin-roster CRUD cluster (ADR-0047 Cluster 1). EmployeeRole is range-typed (no states; lifecycle is `started_at` / `ended_at` open/close); disjoint-ranges invariant per `(employee, role_type, contract)` (ADR-0045); rate-resolution lookup `(employee, role_type, contract, date)` via the contract-resolution path. `change_employee_role_rate` (ADR-0039) compound — close existing row, create new — gains a `contract` parameter (ADR-0045). UserRole grant/revoke (ADR-0040): grant authority by target role — `target_role ∈ {coordinator, auditor}` → `role >= admin`; `target_role ∈ {admin, superadmin}` → `role == superadmin` (ADR-0047). Optional `reason_text` on grant/revoke lands as `audit_reason` Note. ContractorEngagement (range-typed): `started_at` defaults to row-creation date; `ended_at` nullable, defaults to CPR-saved date, overridable.

---

## Not now

The defensible "not now" list, source-tagged. Items are out of MVP because they are speculative (no one at the office uses them today), defer behind other MVP features (e.g., budget tracking), or require integrations the MVP scope does not include. The post-MVP catalog in `post-mvp.md` is folded in here verbatim; `post-mvp.md` itself can be retired once this list lands (its holding-pen role is consumed by this section).

### Post-MVP feature candidates (formerly `post-mvp.md`)

- **Per-page Daily Log assignment.** Associate Daily Log pages with specific Time Entries / Sample Batches for a side-by-side review UI. *Reason for "not now":* nice-to-have audit UX; no operational blocker today — Time Entry / Sample Batch capture works without per-page anchoring.
- **Track-this pin for blockers (notification-coupled).** "Track this" engagement on derived blockers that materializes the Note without commentary. *Reason for "not now":* without notifications, equivalent to "the panel already shows this"; value collapses. Comes back with the notifications batch.
- **Structured blocker assignment + notifications.** `assigned_to: nullable User` field on blocker Notes, `(re)assign_blocker` commands, my-blockers queryable view, reassignment audit chain. *Reason for "not now":* Note conventions ("Sarah, please push this") cover ~70–80% of operational value at MVP; structural assignment is high-leverage only with notifications.
- **Structured cross-project Sample Batch reassignment.** `reassign_sample_batch_project(batch, new_project, new_wa_code)` as a one-atomic-act command. *Reason for "not now":* MVP handles via `dismiss #9` chain + `relink_sample_batch_wa_code` (auditable, two acts); the structured command's gain is notification-coupled.
- **SCA-side RFP rejection notification.** Automated `reopen_project(project, rfp_reason='rfp_rejected')` on SCA portal signal. *Reason for "not now":* requires SCA portal integration (event ingest) — out of MVP scope; manual `reopen_project` covers it.
- **Stale-RFP signal (long-tail SCA non-response).** Derived signal on a project with an RFP `saved` for an extended period without SCA acknowledgement. *Reason for "not now":* operational-policy threshold; not a closure blocker; queryable view value emerges once a backlog of MVP closures exists.
- **Drop blocker #4 if operationally confirmed unfireable.** Sample Batch COC `missing` at closure (ADR-0032 / ADR-0046). *Reason for "not now":* defensive registry entry; COC is created in `saved` state at batch creation (ADR-0033) and has no command-surface path to regress. Drop reversibly post-MVP if operation confirms.
- **WA-file upload at `approve_rfa` (UX bundling).** Compress `approve_rfa` + WA-file upload into one flow. *Reason for "not now":* purely UX — no model-side change; two-act path (approve produces version; upload against version's Document slot) is functional.

### Authorization / role surface

- **Per-project coordinator scoping.** Project-scoped predicates become `role >= coordinator AND assigned_to(target.project)` (triggers chain-freeze on ADR-0047). *Reason for "not now":* MVP is small-team — all coordinators see all projects per ADR-0047's locked clarification (1). Per-project scoping adds an assignment surface (the assignment entity itself, the assign/unassign commands, the admin UI) without immediate operational gain at MVP team size.
- **Future non-chain roles.** Each appends a column to ADR-0047's table without refactoring existing rows. *Reason for "not now":* the four-role chain (`superadmin` → `admin` → `coordinator` → `auditor`) covers MVP operational reality. Field-staff role (deferred per Step 6c-i framing) is the obvious first non-chain candidate when MVP demonstrates field-side workflows are worth modeling.
- **Security-immediate revoke runtime.** Session invalidation on `revoke_user_role` (auth-implementation concern). *Reason for "not now":* MVP gets revoke audit + next-request authorization check; immediate session kill is an auth-implementation feature, not a domain decision.

### Billing-adjacent

- **WACA budget fields.** Quantity / dollar caps on WACodeAssignment rows for the budget-tracking line. *Reason for "not now":* immediate post-MVP priority per user signal; depends on the budget-tracking design pass. WACA carries the foreign keys today; budget fields append when that pass lands.
- **Draft invoice generation against budgets.** Second post-MVP billing priority. *Reason for "not now":* depends on WACA budget fields + Billing Rate entity below.
- **Billing Rate entity (temporal `(subtype, TAT) → rate`).** Follows the temporal rate resolution template (design pattern #1, ADR-0035 + ADR-0045). *Reason for "not now":* MVP captures Sample Batch composition + TAT operationally but does not aggregate to billing-rate dollars; the Billing Rate table lands with the draft-invoice pass.
- **Retroactive rate corrections via Time Entry rate snapshot.** Reversible additive change post-MVP. *Reason for "not now":* MVP's read-time rate resolution via EmployeeRole is honest for current operation; snapshotting is a recovery feature for misattribution scenarios. Add if operational signal emerges.

### Model / config evolution

- **`WACodeConf` evolution to a DB entity.** *Reason for "not now":* MVP keeps `WACodeConf` as code-side static config (ADR-0048) — appropriate for the rare-churn catalog. `code_type_id` stays stable across the migration if/when churn rises.
- **`level` mutation on WA Code.** Would require changing code type. *Reason for "not now":* `level` is denormalized from `WACodeConf[code_type].default_level` and fixed at create (ADR-0048); mutation is a config-evolution problem with low operational signal.

### Dissolved (for the record, not in `mvp.md`'s carry-forward surface)

- **`reassign_project_contract`.** Dissolved by ADR-0044 — with Contract re-attached to the WABundle and made mutable in MVP via `edit_wabundle` / `issue_wa`, and money values derived at read time, there is no heavy cascade to defer.

---

## Carve-outs (in MVP, may slip)

Single-item flag — features inside MVP that depend on an unresolved upstream and may slip post-MVP if the upstream doesn't land. Distinct from "not now" (these are *targeted* for MVP); distinct from carry-forwards (those are *targeted and load-bearing*, mechanics pinned in implementation phase).

- **`resolve_overlap_paired` (blocker #8 joint compound).** ADR-0046's joint-side default-resolution for cross-project time overlap. *Slip condition:* depends on `split_entry`'s mechanics (split-point ergonomics, field-inheritance across sub-entries, batch reassignment at boundary, half-open interval semantics per ADR-0042) landing in early implementation. If `split_entry` mechanics get pushed, `resolve_overlap_paired` slips with it; `resolve_overlap` (single-side) ships either way. Recovery without `_paired`: each side runs `resolve_overlap` independently — auditable, less ergonomic.

---

## Command-shape carry-forwards (in MVP, mechanics in implementation phase)

These commands have predicate-table rows in ADR-0047 (so they ship in MVP); their full signatures and guards are pinned in the implementation phase. Listed here to mark them as **in MVP but not yet shape-complete** — distinct from "not now."

- **`split_entry(time_entry, split_point[, second_split_point])`.** Predicate `role >= coordinator`. Shape (split-point ergonomics, field-inheritance for `daily_log` / `wa_code` / off-site sub-intervals on resulting sub-entries, batch reassignment at boundary) undefined. Half-open interval semantics from ADR-0042 belong with this command. Load-bearing for ADR-0046's `resolve_overlap` / `resolve_overlap_paired` (the latter is also flagged in § Carve-outs).
- **`revoke_write_off(write_off_note, ...)`.** Predicate `role >= coordinator`. Parameters and guards undefined. Misattribution-on-closed-project recovery (scenario (b)) needs `revoke_write_off` + an ADR-0038 closed-project exception + the post-MVP cross-project Sample Batch reassignment command.
- **Revoke-line-item command** (ADR-0049 carry-forward). Rescinding a coordinator-authored `remove` line item before approval. Symmetric with the empty-draft hard-delete on a coordinator-opened draft. Parameters and guards undefined.
- **`reassign_wa_project` deeper mechanics** (ADR-0048 carry-forward). `version_seq` integration in target chain, source-bundle bookkeeping, single-WA-only-in-bundle edge case, audit-trail shape on both sides.
- **ContractorEngagement command-shape.** `start_contractor_engagement` / `end_contractor_engagement` predicates settled (ADR-0047 `role >= coordinator`); signatures and pre-conditions deferred. Date defaults: `started_at` → row-creation date; `ended_at` → CPR-saved date (nullable, overridable).
- **ADR-0031 auto-draft regeneration suppression at closure-gate.** The bare `withdraw_rfa` structural-fix path during closure-gate can loop (`withdraw → fresh draft regenerates → #7 re-fires`). The `resolve_open_rfa` compound resolves itself; the bare-withdraw loop suppression is an edge-case fix for the structural-fix path.
- **Smart-command-inference state for post-issuance auto-generated codes** (ADR-0049 carry-forward). When a TE / SB references an `(sample_type, school)` that doesn't exist on the bundle's head WA, the landing state (`expected` vs. `pending_rfa`) is implementation-phase; the SCA-direct branch's reconciliation handles either case.

---

## Pointers

- **Source decision:** ADR-0050 in `planning/decisions.md`.
- **Rolled-up domain:** `planning/domain-model.md` (21 entities, 14 design patterns, 10-entry blocker registry, four-role chain, full vocabulary).
- **Framework substrate:** `planning/framework.md`.
- **Logic substrate:** `planning/logic.md`.
- **History menu:** `planning/history-patterns.md`.
- **ADR log:** `planning/decisions.md` — ADR-0001 through ADR-0050 (Conceptualization phase).
- **Step list:** `planning/steps.md` — Step 7 ✓ complete; next Step 8 (stack & architecture).
- **Handoff:** `planning/handoff.md` — current between-session state.
- **Phase roster:** `planning/phases.md`.
- **Post-MVP holding pen:** `planning/post-mvp.md` — fully consumed by § Not now above; retain for record but no longer the active holding pen.
