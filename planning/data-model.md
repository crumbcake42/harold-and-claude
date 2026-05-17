# Data Model

## File contract

**Holds:** The conceptual data model for `sca-tracker` — per-entity attribute rosters for all 21 entities, history-surface assignments per ADR-0052, and the shape of the 9 per-entity history tables + 1 shared `command_audit_log`. Documentation rollup, not a decision artifact: every choice here is already pinned by an upstream ADR or by `domain-model.md`. **Conceptual only — not DDL.** Engine-specific column types are flagged "to be implemented with X" (JSONB, PostGIS, etc.), never specified.
**Update when:** A domain-shape ADR lands that adds / removes / renames an entity attribute, changes an entity's history surface, or changes the shape of a history table. The cross-entity relationship table lives in `domain-model.md` § Relationships — update there, not here. DDL belongs in the implementation phase, not this file.

---

## Reading this file

Cold-read order: `framework.md` (entity / value / four-kind state taxonomy / typed-ref shape) → `domain-model.md` (21-entity roster + relationship table + lifecycles + history-pattern assignments) → ADR-0052 (data-layer topology: per-entity history tables + shared audit log) → **this file**.

What's here: attribute lists per entity, kind tagging, outgoing reference lines, history-surface labels, history-table shapes. What's *not* here: the cross-entity relationship table (in `domain-model.md` § Relationships); lifecycle state machines (in `domain-model.md` § Lifecycles); authorization predicates (in `domain-model.md` § Authorization predicates + ADR-0047); DDL (implementation phase).

---

## Conventions

**Kind vocabulary** (per `framework.md` § State, with two structural additions for tabular use):

| Kind | Meaning |
|---|---|
| `intrinsic` | Fact the entity carries by being itself. Mutable, but mutations are explicit events; current value is authoritative. |
| `lifecycle` | The entity's named state field (or a date-range marker for range-typed entities). One per entity that has a lifecycle. |
| `derived` | Computable from other state. Never written directly. May be cached / materialized; reproducibility from inputs is required. |
| `reference` | A typed FK to another entity. Cardinality declared per relationship. Direct unless tagged `derived`. |
| `composite` | A discriminator + id pair (`(scope_type, scope_id)`, polymorphic `(entity_type, entity_id)`) that together resolve to a referent of varying type. |
| `identity` | The entity's surrogate UUID per `framework.md` § Identity. One row per entity. |
| `audit-metadata` | `created_at` / `created_by` / `updated_at` / `updated_by` columns the dispatcher writes uniformly. Per-entity rosters note "standard audit-metadata" rather than re-listing the four columns each time. |

**Type / notes idiom.** Language- and engine-agnostic: `UUID`, `text`, `integer`, `date`, `timestamp`, `date-range`, `boolean`, `enum: {...}`, `M:1 ref → Entity`, `0..1 ref → Entity`, `M:N via AssociativeEntity`. Engine-specific calls flagged inline: "to be implemented with JSONB" / "to be implemented with PostGIS" — these are implementation-phase choices noted for the carry-forward, not pinned here.

**Outgoing-references line.** After each entity's attribute table, a one-line summary of the entity's outgoing references (typed refs + derivations). Cross-entity authoritative listing remains in `domain-model.md` § Relationships; the line here is for in-place readability.

**State enum line.** For entities with a named lifecycle, the enum values are listed in one line below the attribute table; transitions are not duplicated here — pointer to `domain-model.md` § Lifecycles.

**History-surface label.** The last line of each entity's section names the history surface assigned by ADR-0052:
- `history table: <name>_history` (comprehensive) — full snapshot per command.
- `history table: <name>_history` (lifecycle) — transition record per lifecycle event.
- `command_audit_log (polymorphic)` — shared audit-log table; command metadata only, no state snapshot.
- `no history` — current row is the sole record.

**Derivation tag.** A `derived` attribute carries a one-line derivation rule in the `Type / notes` cell. Multi-step derivations cite the relationship chain (e.g., `via wa_code → WACode → WABundle`).

---

## Per-entity attributes

Entities appear in roster order (per `domain-model.md` § Entity roster). Each section is self-contained for read: attribute table → outgoing-references line → (state enum line, if stateful) → history-surface label.

### Project

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `name` | intrinsic | text — display name. |
| `project_number` | intrinsic | text, uniqueness-constrained natural key. |
| `state` | lifecycle | enum: `{active, closed, cancelled}`. |
| `closed_at` | intrinsic | timestamp, nullable — set on `close_project`. |
| `cancelled_at` | intrinsic | timestamp, nullable — set on `cancel_project`. |
| `contract` | derived | via `WABundle.contract_id` — `project.wabundle.contract`. |
| (standard audit-metadata) | audit-metadata | `created_at`, `created_by`, `updated_at`, `updated_by`. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete marker. |

**Outgoing references:** WABundle (1:1, FK on WABundle side per `WABundle.project_id` UNIQUE); RFP Documents (1:N derivation, ADR-0037); via WABundle → Contract, → WAs, → WA Codes, → Schools; via `ContractorEngagement` → Contractors (derived). See `domain-model.md` § Relationships.

**State enum:** `active | closed | cancelled`. Transitions per `domain-model.md` § Lifecycles (close / cancel / reopen-from-closed / reopen-from-cancelled). `closed` is the freezing terminal (pattern #13); `cancelled` is non-freezing.

**History surface:** `project_history` (lifecycle).

---

### School

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `name` | intrinsic | text. |
| (other identifying attributes — e.g., DOE building number, address) | intrinsic | not pinned by any ADR; implementation-phase scope. Lookup-like, low churn (`domain-model.md`). |
| (standard audit-metadata) | audit-metadata | `created_at`, `created_by`, `updated_at`, `updated_by`. |

**Outgoing references:** none direct. Referenced by Time Entry (`site_id`), Sample Batch (`site_id`), WA Code (`school_id`, nullable), WABundleSite (associative).

**State enum:** (none — no lifecycle.)

**History surface:** no history.

---

### WA

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `wabundle_id` | reference | M:1 → WABundle, required. |
| `version_seq` | intrinsic | integer (0-based); unique per `(wabundle_id, version_seq)`. v0 in-place at initial issuance; v1+ are new rows (ADR-0048 / ADR-0049). |
| `state` | lifecycle | enum: `{pending, issued, superseded}`. |
| `issued_date` | intrinsic | date, nullable; populated at issuance (the date SCA issued the document). |
| `initialization_date` | intrinsic | date, nullable; populated at issuance (the date work under this WA is authorized to begin — drives blocker #12). |
| (standard audit-metadata) | audit-metadata | as standard. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete. |

**Outgoing references:** WABundle (M:1 required); WA Codes (M:N via `WACodeAssignment`); Contractors (M:N via `ContractorEngagement`); via WABundle → Project (derived); via WABundle → Schools / Contract (derived).

**State enum:** `pending | issued | superseded`. Transitions per `domain-model.md` § Lifecycles (initial path: in-place `pending → issued` on v0; SCA-direct / RFA paths: new WA rows, older heads transition to `superseded`).

**History surface:** `wa_history` (comprehensive).

---

### WA Code

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `wabundle_id` | reference | M:1 → WABundle, required (ADR-0048 reparent). |
| `code_type` | intrinsic | text — references the `WACodeConf` catalog entry (`code_type_id`). `WACodeConf` is code-side static config, not a DB entity in MVP (ADR-0048). |
| `level` | intrinsic | enum: `{project, building}`. Denormalized from `WACodeConf[code_type].default_level` at creation; immutable thereafter. |
| `school_id` | reference | 0..1, M:1 → School. Non-null iff `level = 'building'`. Constrained to `wabundle.sites`. |
| `state` | lifecycle | enum: `{expected, pending_rfa, rfa_in_review, issued, budget_rfa_needed, dismissed, removed}`. `budget_rfa_needed` deferred behind budget tracking. |
| (standard audit-metadata) | audit-metadata | as standard. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete. Terminal-state rows (`dismissed` / `removed`) retained per cascade-keep-FK (ADR-0049 §5 + pattern #14). |

**Outgoing references:** WABundle (M:1 required); School (0..1); WAs (M:N via `WACodeAssignment`); Deliverable (M:1 derivation, ADR-0022 — codes share Deliverables); via WABundle → Project (derived).

**State enum:** as above. Transitions per `domain-model.md` § Lifecycles. Three terminal-entering paths (`dismiss_wa_code`, `approve_rfa` remove-target, `issue_wa` SCA-direct dropped-code) all fire the shared removal cascade.

**History surface:** `wa_code_history` (lifecycle).

---

### User

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `username` | intrinsic | text, uniqueness-constrained. |
| `password_hash` | intrinsic | text — hashing scheme TBD at implementation kickoff (carry-forward from ADR-0051's auth-mechanism deferral). |
| `employee_id` | reference | 0..1, M:1 → Employee, UNIQUE (ADR-0041). Null for non-Employee Users (superadmin, external auditor). |
| (standard audit-metadata) | audit-metadata | as standard. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete. |

**Outgoing references:** Employee (0..1, UNIQUE); UserRoles (1:N back-link via `UserRole.user_id`).

**State enum:** (none — no lifecycle.)

**History surface:** `command_audit_log` (polymorphic). Includes UserRole grant / revoke events per ADR-0036 + ADR-0040 (`(user_id, role_type, actor, timestamp, reason_text?)` carried in `command_payload`).

---

### Employee

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `name` | intrinsic | text. |
| (other HR attributes — e.g., email, phone, hire date) | intrinsic | not pinned by any ADR; admin-roster CRUD scope; implementation-phase concretization. |
| (standard audit-metadata) | audit-metadata | as standard. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete. |

**Outgoing references:** none direct. Referenced by User (`employee_id?`, UNIQUE), EmployeeRoles (1:N back-link), Time Entries (`employee_id`), Sample Batches (`employee_id`, collector).

**State enum:** (none — no lifecycle.)

**History surface:** `command_audit_log` (polymorphic).

---

### EmployeeRole

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `employee_id` | reference | M:1 → Employee, required. |
| `role_type` | intrinsic | enum (operational role catalog — `TechRole`, `ProjectLead`, etc. per ADR-0035. Code-side. **Distinct from** the auth-chain catalog `{superadmin, admin, coordinator, auditor}` on UserRole — auth membership and operational rate-carrier role are separate dimensions). |
| `contract_id` | reference | M:1 → Contract, required (ADR-0045). |
| `rate` | intrinsic | money-typed (representation TBD — implementation phase; likely `decimal(precision, scale)`). |
| `started_at` | lifecycle | date — range-open marker; full-day semantics, closed-closed `[started_at, ended_at]` (ADR-0035). |
| `ended_at` | lifecycle | date, nullable — range-close marker; null while open-ended. |
| (standard audit-metadata) | audit-metadata | as standard. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete. |

**Invariants (per ADR-0035, write-time):** within a single `(employee_id, role_type)` pair, date ranges must be pairwise disjoint. Different `role_type` values may overlap freely.

**Outgoing references:** Employee (M:1 required); Contract (M:1 required). Referenced by Time Entry via `(employee, role_type, contract, date)` lookup — a derived/validated link, no FK from Time Entry (ADR-0041 + ADR-0045).

**State enum:** (none — range-typed entity; no named states. Lifecycle events: open / close / rate-change per `domain-model.md` § Lifecycles.)

**History surface:** `employee_role_history` (lifecycle).

---

### UserRole

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID (surrogate per `framework.md` § Identity; composite uniqueness on `(user_id, role_type)`). |
| `user_id` | reference | M:1 → User, required. Composite-key component. |
| `role_type` | intrinsic | enum: `{superadmin, admin, coordinator, auditor}` (the auth-chain catalog, ADR-0040). Composite-key component. |

**Outgoing references:** User (M:1 required).

**State enum:** (none — atemporal current-state relation per ADR-0036; no timestamps, no state field. Grant creates; revoke hard-deletes; re-grant creates fresh.)

**History surface:** no history. Grant / revoke audit (carrying `(user_id, role_type, actor, timestamp, reason_text?)`) lives on **User's** `command_audit_log` (ADR-0036 + ADR-0040); optional `reason_text` → `audit_reason` Note on that history record.

---

### Time Entry

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `employee_id` | reference | M:1 → Employee, required, direct (ADR-0041). |
| `role_type` | intrinsic | enum (operational role catalog; matches EmployeeRole.role_type) — self-described, no FK (ADR-0041). |
| `site_id` | reference | M:1 → School, required, direct (ADR-0041). |
| `wa_code_id` | reference | M:1 → WA Code, required at create **and post-cascade** (cascade-keep-FK per ADR-0048 + ADR-0049 §5). |
| `date` | intrinsic | date. |
| `on_site_range` | intrinsic | time range `(start_time, end_time)` on `date`. Gross commitment span (ADR-0034). |
| `off_site_sub_intervals` | intrinsic | list of disjoint `(start_time, end_time)` pairs, each entirely within `on_site_range`, pairwise disjoint, positive duration (ADR-0034). To be implemented with JSONB-backed list (representation TBD — implementation phase; alternative: side table). |
| `daily_log_id` | reference | 0..1, M:1 → Document (where `document_type = 'daily_log'`), nullable (ADR-0026). |
| `employee_role` | derived | lookup `(employee_id, role_type, contract, date)` → EmployeeRole row. Contract resolved via `wa_code → WACode → WABundle → contract`. No FK; resolved at rate / blocker / closure-gate time (ADR-0041 + ADR-0045). |
| `project` | derived | via `wa_code → WACode → WABundle → project` (ADR-0048). |
| `net_on_site_time` | derived | `on_site_range` minus `⋃ off_site_sub_intervals` (set of disjoint intervals; ADR-0034). |
| (standard audit-metadata) | audit-metadata | as standard. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete. |
| `write_off_status` | derived | "this Time Entry has a non-revoked `write_off` Note" (ADR-0042 pattern #14). |

**Outgoing references:** Employee (M:1 required); School (M:1 required); WA Code (M:1 required, kept post-cascade); Document daily-log (0..1); EmployeeRole (derived/validated, no FK); Project (derived via WA Code → WABundle).

**State enum:** (none — data-only; no lifecycle.)

**History surface:** `command_audit_log` (polymorphic).

---

### Sample Batch

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `wa_code_id` | reference | M:1 → WA Code, required at create **and post-cascade** (cascade-keep-FK per ADR-0048 + ADR-0049 §5). |
| `employee_id` | reference | M:1 → Employee, direct — the collector (ADR-0033). |
| `site_id` | reference | M:1 → School, required, direct (ADR-0041). |
| `sample_type` | intrinsic | enum (sample-type catalog — code-side). |
| `tat` | intrinsic | enum (TAT options — code-side). |
| `composition` | intrinsic | structured value `[{subtype, quantity}]`. Batch composition invariant (ADR-0019): PCM/TEM batches require a single subtype; Bulk batches allow mixed subtypes. To be implemented with JSONB-backed list (representation TBD — implementation phase). |
| `collection_time` | intrinsic | timestamp — when the batch was collected on `site_id`. Half-open membership in Time Entry ranges per ADR-0042's `split_entry` carry-forward. |
| `sampling_locations` | intrinsic | text, optional — descriptive plain-text within the site (ADR-0041). |
| `project` | derived | via `wa_code → WACode → WABundle → project` (ADR-0048). |
| `coc_document` | derived | 1:1 — Sample Batch derives a COC Document at creation in `saved` state (ADR-0033). |
| `lab_report_document` | derived | 1:1 — Sample Batch derives a Lab Report Document at creation in `missing` state (ADR-0033). |
| (standard audit-metadata) | audit-metadata | as standard. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete. |
| `write_off_status` | derived | "this Sample Batch has a non-revoked `write_off` Note" (ADR-0042 pattern #14). |

**Outgoing references:** WA Code (M:1 required, kept post-cascade); Employee (M:1, collector); School (M:1 required); derived 1:1 to COC + Lab Report Documents; Project (derived).

**State enum:** (none — stateless per ADR-0038; workflow advances through derived Documents and Deliverable containment.)

**History surface:** `sample_batch_history` (lifecycle — records derivation events at the parent batch's lifecycle records per `domain-model.md`).

---

### Document

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `document_type` | intrinsic | enum (`document_type` registry; per-type lifecycle dispatched per ADR-0024 — simple / cycling-family / bespoke). Code-side registry. |
| `scope_type` | composite | enum: `{project, deliverable, wa_code}` — single-scope discriminator (ADR-0041). |
| `scope_id` | composite | UUID — FK to the appropriate scope entity (resolved by `scope_type`). Together with `scope_type` forms the Document's scope ref. |
| `state` | lifecycle | per-`document_type` enum (dispatched per ADR-0024). Simple: `{missing, saved}`. Cycling-family (CPR / FAMR): parameterized; cycle of tracking dates. Bespoke (Lab Report: `{missing, saved, invalid}`; RFP: `{missing, saved, rejected, withdrawn}` — ADR-0037). |
| `state_data` | intrinsic | per-`document_type` data carrier (cycling-family tracking dates, etc.). To be implemented with JSONB-backed object (representation TBD — implementation phase). |
| `file_ref` | intrinsic | external object-storage reference (URL / key), nullable while `state ∈ pre-save`. Object storage choice deferred to implementation kickoff per `architecture.md`. |
| (standard audit-metadata) | audit-metadata | as standard. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete. |

**Outgoing references:** scope entity via `(scope_type, scope_id)` — Project | Deliverable | WA Code; derived back-pointers from DepFiling (1:N derivation), Sample Batch (1:1 derivation for COC + Lab Report), Project (1:N for RFP).

**State enum:** dispatched per `document_type` (see Notes on selected entities in `domain-model.md` § Entity roster). Per-type lifecycle definitions live in `domain-model.md` § Lifecycles + ADR-0024 + ADR-0037 (RFP).

**History surface:** `document_history` (comprehensive). Snapshot per command captures the full Document row including per-type `state_data`.

---

### Deliverable

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `state` | lifecycle | enum: `{pending_rfa, outstanding, under_review, approved}`. |
| `bundle_snapshot` | intrinsic | nullable structured value — frozen Document-bundle query result at `submit_deliverable`; cleared on rejection re-open. To be implemented with JSONB-backed object (representation TBD — implementation phase). |
| `submitted_at` | intrinsic | timestamp, nullable — set on `submit_deliverable`. |
| `approved_at` | intrinsic | timestamp, nullable — set on `approve_deliverable`. |
| `wasted` | derived | "this Deliverable has a non-revoked `write_off` Note" (ADR-0042 reframe of ADR-0029; pattern #14). Trigger: WA Code dismissed OR removed (ADR-0049 extension). |
| (standard audit-metadata) | audit-metadata | as standard. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete. |

**Outgoing references:** required Documents (1:N derivation, ADR-0015 + ADR-0041 — derived required + user-added at Deliverable scope + user-added at contained WA-Code scope); WA Codes (M:1 derivation reverse — codes map to Deliverables, ADR-0022).

**State enum:** `pending_rfa | outstanding | under_review | approved`. Transitions per `domain-model.md` § Lifecycles. `pending_rfa → outstanding` is derivation-driven (when the WA Code is issued, ADR-0022).

**History surface:** `deliverable_history` (lifecycle).

---

### Contractor

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `name` | intrinsic | text. |
| (other roster attributes — e.g., contact info, license number) | intrinsic | not pinned by any ADR; admin-roster CRUD scope; implementation-phase concretization. |
| (standard audit-metadata) | audit-metadata | as standard. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete. |

**Outgoing references:** none direct. Referenced by `ContractorEngagement` (M:N with WA via stint markers).

**State enum:** (none — no lifecycle.)

**History surface:** `command_audit_log` (polymorphic).

---

### RFA

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `amends_wa_id` | reference | M:1 → WA, required, direct (ADR-0041). Set at auto-draft creation; immutable for RFA lifetime. |
| `state` | lifecycle | enum: `{draft, in_review, approved, rejected, withdrawn}`. |
| `submitted_at` | intrinsic | timestamp, nullable — set on `submit_rfa`. |
| `decided_at` | intrinsic | timestamp, nullable — set on `approve_rfa` / `reject_rfa` / `withdraw_rfa`. |
| `project` | derived | via `amends_wa_id → wa.wabundle.project` (ADR-0041 + ADR-0044). |
| (standard audit-metadata) | audit-metadata | as standard. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete. Empty `draft` RFAs hard-delete (ADR-0031). |

**RFA line items** (M:N target shape from RFA to WA Code, ADR-0031 + ADR-0049 — separate row in the line-item table, not an attribute of RFA proper):

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `rfa_id` | reference | M:1 → RFA, required. |
| `wa_code_id` | reference | M:1 → WA Code, required (the target code). |
| `line_item_type` | intrinsic | enum: `{add, remove, budget}`. `budget` deferred. |
| (line-item-specific payload — e.g., budget amount for `budget` type when introduced) | intrinsic | shape TBD per future ADR. |

**Outgoing references:** WA (M:1 required, `amends_wa_id`); WA Codes (M:N via line items); via WA → WABundle → Project (derived).

**State enum:** `draft | in_review | approved | rejected | withdrawn`. Transitions per `domain-model.md` § Lifecycles.

**History surface:** `rfa_history` (comprehensive). Line items are part of the RFA's snapshot.

---

### Note

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `subtype` | intrinsic | enum: `{regular, blocker, resolution, audit_reason, write_off}`. Note-internal discriminator (ADR-0018 base; `blocker` / `resolution` added by ADR-0032; `audit_reason` by ADR-0040; `write_off` by ADR-0042). |
| `target_type` | composite | enum: `{<entity_type>, history_record}` — polymorphic target discriminator. Extended from "any entity" to "any entity OR any history record" by ADR-0040. |
| `target_id` | composite | UUID — FK to the target (entity row OR history row); no DB-level FK (polymorphic). |
| `message` | intrinsic | text — commentary body. Mandatory for `regular`; semantics per subtype below. |
| `authorship_class` | intrinsic | enum: `{user, system}` (ADR-0032). System-authored Notes are `blocker` (materialized), `resolution` (structural-fix), and cascade-emitted `write_off`. |
| `created_by` | reference | M:1 → User; nullable iff `authorship_class = 'system'` (ADR-0032). |
| `created_at` | intrinsic | timestamp. |
| `edited_at` | intrinsic | timestamp, nullable — set on `edit_note` (only `regular` subtype is editable; creator-only, ADR-0018). |
| `references` | reference | 0..1 → Note — inter-Note reference (ADR-0032). Used by `resolution.blocker_ref`, `blocker.paired_blocker_ref`, `write_off.references` (originating blocker/resolution Note). |

**Per-subtype extra fields** (additive; null when not applicable):

| Subtype | Extra fields |
|---|---|
| `regular` | (none). |
| `blocker` | `blocker_type` (registry key string, nullable for user-flagged), `surfaced_at` (timestamp; backfilled from underlying entity history for system-authored), `paired_blocker_ref` (via `references`, for cross-project blockers). |
| `resolution` | `blocker_ref` (via `references`, required), `resolution_kind` enum: `{structural_fix, default_resolution, dismissal}` (ADR-0042). |
| `audit_reason` | `reason_text` carried as `message`; attached via `target_type = history_record` to a grant/revoke history row (ADR-0040). |
| `write_off` | `reason` (mandatory text — supplied by default-resolution justification or inherited from cascade originator); `references` points at the originating blocker/resolution Note (nullable for non-blocker causes — e.g., `dismiss_wa_code` cascade). Immutable (ADR-0042). |

**Outgoing references:** target entity OR history record (polymorphic, no DB FK); optional `references → Note`; `created_by → User` (nullable).

**State enum:** (none — no lifecycle. Subtypes are immutable except `regular`, which is editable by creator only.)

**History surface:** no history. Notes are not deletable through the command surface (ADR-0018; the "hard delete" primitive is not exercised).

---

### DepFiling

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `project_id` | reference | M:1 → Project, required (ADR-0023). |
| `tru_number` | intrinsic | text — regulator-assigned natural key. |
| `required_doc_types` | intrinsic | set of `document_type` values — editable per-instance (`edit_dep_filing_required_doc_types`). Seeded at creation from a code-side template (Regular: `[ACP13, ACP7, ACP15, ACP21]`; Emergency: `[Emergency Notification, ACP13, ACP7, ACP15, ACP21]` per ADR-0023). To be implemented with JSONB-backed list (representation TBD — implementation phase). |
| `completeness` | derived | "every doc_type in `required_doc_types` has a corresponding Document in `saved` state" — predicate over derived Documents (ADR-0023). |
| (standard audit-metadata) | audit-metadata | as standard. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete. |

**Outgoing references:** Project (M:1 required); Documents (1:N derivation per `required_doc_types`, ADR-0023).

**State enum:** (none — no lifecycle; completeness is derived.)

**History surface:** `command_audit_log` (polymorphic).

---

### WACodeAssignment (WACA)

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID (surrogate; composite uniqueness on `(wa_id, wa_code_id)`). |
| `wa_id` | reference | M:1 → WA, required. Composite-key component. |
| `wa_code_id` | reference | M:1 → WA Code, required. Composite-key component. |
| (budget fields) | intrinsic | added when budget tracking design lands (post-MVP per ADR-0041 + `domain-model.md` § Post-MVP). |

**Outgoing references:** WA (M:1 required); WA Code (M:1 required).

**State enum:** (none — associative entity; no lifecycle.)

**History surface:** no history. Rows are immutable in MVP (per ADR-0041 — WA's supersession-immutability covers the assignment surface). Hard delete on WA hard-delete cascade.

---

### ContractorEngagement

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `wa_id` | reference | M:1 → WA, required. |
| `contractor_id` | reference | M:1 → Contractor, required. Note: **multiple rows per `(wa_id, contractor_id)` permitted** (re-engagement after CPR close per ADR-0041) — natural-key uniqueness is on `(wa_id, contractor_id, started_at)` not the pair. |
| `started_at` | lifecycle | date — range-open marker. Defaults to row-creation date (carry-forward from ADR-0041 + handoff). |
| `ended_at` | lifecycle | date, nullable — range-close marker. Defaults to CPR-saved date when closed (nullable, overridable). |
| (standard audit-metadata) | audit-metadata | as standard. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete (referenced by derived CPR Documents). |

**Outgoing references:** WA (M:1 required); Contractor (M:1 required); derived 1:1 CPR Document per engagement (ADR-0041).

**State enum:** (none — range-typed entity; no named states. Lifecycle events: `engagement_started` on create, `engagement_ended` on close.)

**History surface:** `contractor_engagement_history` (lifecycle).

---

### Contract

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID (ADR-0043). |
| `contract_number` | intrinsic | text, uniqueness-constrained natural key (mandatory). |
| `name` | intrinsic | text, optional. Null → display label derives as `'C'` + last 5 chars of `contract_number` (derived label, not a stored default). |
| `start_date` | intrinsic | date. |
| `end_date` | intrinsic | date, nullable. |
| `code_flat_fee_schedule` | intrinsic | non-temporal collection of `{code_type, fee}` pairs (ADR-0043). To be implemented with JSONB-backed list (representation TBD — implementation phase; alternative: side table). A code type absent from the schedule resolves to null/unpriced (no blocker per ADR-0045). |
| `validity` | derived | enum-valued derivation: `pending` (today < start_date) / `active` (start_date ≤ today ≤ end_date ?? +∞) / `expired` (end_date < today). Computed from `(start_date, end_date?)` + clock (ADR-0043). |
| (standard audit-metadata) | audit-metadata | as standard. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete. |

**Outgoing references:** none direct. Referenced by WABundle (`contract_id`, M:1 required, ADR-0044), EmployeeRole (`contract_id`, M:1 required, ADR-0045).

**State enum:** (none — no state machine; `validity` is derived from dates per ADR-0043.)

**History surface:** `command_audit_log` (polymorphic).

---

### WABundle

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID. |
| `project_id` | reference | M:1 → Project, required, UNIQUE (enforces Project ↔ WABundle 1:1, ADR-0044). |
| `contract_id` | reference | M:1 → Contract, required at create (ADR-0044). |
| `wa_number` | intrinsic | text, uniqueness-constrained natural key; nullable pre-issuance, populated at first WA issuance (ADR-0044). |
| `service_id` | intrinsic | text, uniqueness-constrained natural key; nullable pre-issuance, populated at first WA issuance. |
| `job_number` | intrinsic | text, uniqueness-constrained natural key; nullable pre-issuance, populated at first WA issuance. SCA's WA id, distinct from the project number. |
| `head_version_seq` | derived | `max(wa.version_seq)` over non-superseded WAs in the bundle; null when no WA exists yet (drives `issue_wa` initial-vs-SCA-direct dispatch per ADR-0049). |
| `issuance_phase` | derived | `expected` iff `wa_number IS NULL`; otherwise `issued`. Per `domain-model.md` § Entity roster ("contract `expected` derived from `wa_number IS NULL`"). Distinct from the **Contract** entity's `validity` (`pending/active/expired` from contract dates) — this attribute tracks the WABundle's bundle-of-WAs phase. |
| (standard audit-metadata) | audit-metadata | as standard. |
| `deleted_at` | intrinsic | timestamp, nullable — soft-delete. |

**Outgoing references:** Project (M:1 required, UNIQUE); Contract (M:1 required); Schools (M:N via `WABundleSite`); WAs (1:N back-link via `WA.wabundle_id`); WA Codes (1:N back-link via `WACode.wabundle_id`, ADR-0048).

**State enum:** (none — no state machine; `issuance_phase` is derived per above.)

**History surface:** `command_audit_log` (polymorphic).

---

### WABundleSite

| Attribute | Kind | Type / notes |
|---|---|---|
| `id` | identity | UUID (surrogate; composite uniqueness on `(wabundle_id, school_id)`). |
| `wabundle_id` | reference | M:1 → WABundle, required. Composite-key component. |
| `school_id` | reference | M:1 → School, required. Composite-key component. |

**Outgoing references:** WABundle (M:1 required); School (M:1 required).

**State enum:** (none — associative entity; no lifecycle.)

**History surface:** no history. Hard delete (no incoming history references; bundle.sites changes audited on WABundle's `command_audit_log`).

---

## History tables

Per ADR-0052: 9 per-entity append-only history tables (3 comprehensive + 6 lifecycle) + 1 shared `command_audit_log` for the 7 audit-log entities + nothing for the 5 no-history entities. All history rows written by the dispatcher in the same Postgres transaction as the entity mutation (carry-forward from ADR-0008 + ADR-0051 + ADR-0052). DDL is implementation-phase; this section names shape, not columns at SQL precision.

### Common metadata (all history rows)

Every history row — comprehensive, lifecycle, or `command_audit_log` — carries the same metadata columns (ADR-0052 §S1):

| Column | Type / notes |
|---|---|
| `id` | UUID (surrogate, per history row). |
| `entity_id` | UUID — the referenced entity's identity. Not a DB-level FK on `command_audit_log` (polymorphic); is a FK on per-entity history tables. |
| `command_name` | text — the dispatched command (`close_project`, `issue_wa`, ...). |
| `command_payload` | JSONB-backed object — the command's input payload. |
| `actor_user_id` | UUID — the dispatching user. |
| `committed_at` | timestamp — transaction commit time. |
| `sequence_no` | integer (per entity, gap-free) — ordering within the entity's history. |

### Comprehensive history tables (3) — ADR-0052 §S2

| Table | Subject entity | Extra columns beyond common metadata |
|---|---|---|
| `document_history` | Document | `snapshot` JSONB-backed — full entity row at the post-command point. |
| `wa_history` | WA | `snapshot` JSONB-backed. |
| `rfa_history` | RFA | `snapshot` JSONB-backed. |

Snapshot reconstructs the entity row at any sequence_no by reading the latest snapshot at or before that point. Schema evolution: most entity-column changes are absorbed by the JSONB-backed snapshot without an Alembic migration on the history table (ADR-0052 §S7).

### Lifecycle history tables (6) — ADR-0052 §S3

| Table | Subject entity | Extra columns beyond common metadata |
|---|---|---|
| `project_history` | Project | `from_state`, `to_state`, `transition_name`, `state_context` JSONB-backed. |
| `sample_batch_history` | Sample Batch | as above. |
| `deliverable_history` | Deliverable | as above. |
| `employee_role_history` | EmployeeRole | as above (range-typed: transitions are open / close / rate-change). |
| `wa_code_history` | WA Code | as above. |
| `contractor_engagement_history` | ContractorEngagement | as above (range-typed: open / close). |

`from_state` is nullable (create-time transition has no prior state). `state_context` carries any per-transition data not captured by the common metadata (e.g., the `reason_text` on `dismiss_wa_code`, the closure-cascade summary on `close_project`).

### `command_audit_log` (1) — ADR-0052 §S4

Single shared table with polymorphic `(entity_type, entity_id)` reference. Used by the 7 audit-log entities: Employee, User, Time Entry, Contractor, DepFiling, Contract, WABundle.

| Column | Type / notes |
|---|---|
| Common metadata | All seven columns above; `entity_id` here is the polymorphic referent (no DB-level FK). |
| `entity_type` | enum: {`employee`, `user`, `time_entry`, `contractor`, `dep_filing`, `contract`, `wabundle`} — the discriminator. |

Command metadata only — no state snapshot column. Reconstruction of past state for an audit-log entity is **not** guaranteed; the audit log answers "who did what when," not "what did the row look like then." Timing (in-txn vs. post-commit) deferred to implementation phase (ADR-0052 §S4).

### No history (5 entities) — ADR-0052 §S5

School, Note, UserRole, WACodeAssignment, WABundleSite. No history infrastructure — current row is the sole record. Note's "no history" is consistent with its immutable-subtype design (per `domain-model.md` § Note semantics): `regular` Notes are editable only by creator; all other subtypes are immutable; the entity record itself is the audit story. UserRole grants/revokes audit on User's `command_audit_log` row (per ADR-0036 + ADR-0040).

### Reference snapshotting (ADR-0052 §S6, restating ADR-0013)

Typed UUID references in `snapshot` / `state_context` JSONB are stored as-is (the UUID). At read time, dereferencing a snapshotted UUID returns the *current* row — history rows do not deep-copy referenced entities. The framework's no-natural-key rule (`framework.md` § Identity) keeps this safe: a rename of the referent does not break the historical reference.

---

## Pointers

- **Framework substrate:** `framework.md` (entity / value / four-kind state taxonomy; UUID identity; typed-ref shape; derived-fields rule).
- **Domain model rollup:** `domain-model.md` (21-entity roster + cross-entity relationship table + per-entity lifecycles + authorization predicates + design patterns + blocker registry + vocabulary).
- **Architecture sketch:** `architecture.md` (component diagram + boundary semantics + 10-step successful-command data flow).
- **Decisions log:** `decisions.md` — esp. ADR-0052 (data layer), ADR-0051 (runtime stack), ADR-0044 / 0045 / 0048 (WABundle / Contract / WA Code cluster), ADR-0032 / 0042 / 0046 / 0049 (blocker / write-off / removal cluster), ADR-0035 / 0041 (EmployeeRole + Time Entry temporal model), ADR-0018 + Note amendments across the cluster.
- **Step list:** `planning/steps.md` § Step 9a (this file's brief) + § Step 9b (next step: consolidation + `roadmap.md` + phase-transition ADR).
- **Handoff:** `planning/handoff.md`.
