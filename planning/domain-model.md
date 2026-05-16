# Domain Model

## File contract

**Holds:** The rolled-up domain projection — the entities, relationships, lifecycles, authorization predicates, history patterns, design patterns, blocker registry, and vocabulary that map `framework.md` / `logic.md` / `history-patterns.md` onto the SCA-tracker domain. Standalone reference for a framework-aware reader.
**Update when:** A domain-shape ADR lands in `decisions.md` (entity added/removed/renamed; relationship shape changes; lifecycle/state-machine change; predicate row added/changed; design pattern added/retired; vocabulary term added/revised). The handoff's cumulative tables are the in-flight working surface during a session; this file is the post-session source of truth between sessions.

The Conceptualization-phase output for Step 6d (per `steps.md`). Built on the cumulative state at the close of Steps 6a–6c — ADR-0001 through ADR-0049. Pointers to the source ADRs run throughout; consult `decisions.md` for the full deliberation behind each entry.

Read order if you're cold: `framework.md` (four-kind state taxonomy, entity / value / relationship distinction, UUID identity) → `logic.md` (commands, mandatory capture, lifecycle + invariant + authorization pipeline) → `history-patterns.md` (per-entity history menu, selection criteria) → **this file**.

---

## Entity roster (21 entities)

Each entity is named, summarized in one line, and tagged with its lifecycle shape (state machine summary or "no lifecycle"), its history pattern (per `history-patterns.md`), and its delete policy. Detailed lifecycle state machines, schema fields, and command surface are pointed at the relevant ADR(s); the cumulative tables in prior sessions' `handoff.md` carry the working-state expansion.

| # | Entity | One-line essence | Lifecycle | History pattern | Delete policy | Key ADRs |
|---|---|---|---|---|---|---|
| 1 | **Project** | SCA engagement; the top-level work unit. | `active` / `closed` / `cancelled` (reopen from either terminal) | Lifecycle capture | Soft delete | 0037, 0038, 0044 |
| 2 | **School** | Site / building. Lookup-like; rarely changes. | No lifecycle | No history | Hard delete | (substrate) |
| 3 | **WA** | A *version* of a Work Authorization within a WABundle; the SCA-issued document. | `pending` → `issued` → `superseded` (v0 in-place at initial issuance; v1+ are new rows) | Comprehensive capture | Soft delete | 0017, 0030, 0044, 0048, 0049 |
| 4 | **WA Code** | A bundle-scoped line item (project-level or building-level). | `expected` / `pending_rfa` / `rfa_in_review` / `issued` / `budget_rfa_needed` (deferred) / `dismissed` / `removed` | Lifecycle capture | Soft delete | 0020, 0027, 0048, 0049 |
| 5 | **User** | Auth identity (username/password); optionally linked 0..1 to Employee. | No lifecycle | Audit log | Soft delete | 0036, 0040, 0041 |
| 6 | **Employee** | Person doing project work. | No lifecycle | Audit log | Soft delete | 0035, 0041 |
| 7 | **EmployeeRole** | Temporal work-license + rate-carrier on `(employee, role_type, contract)`. | Range-typed (start/end dates); no named states | Lifecycle capture | Soft delete | 0035, 0045 |
| 8 | **UserRole** | App-access grant `(user_id, role_type)`. | No lifecycle | No history | Hard delete (audit on User) | 0036, 0040 |
| 9 | **Time Entry** | A billable time record for one `(employee, role_type, site, date)` with on-site range + off-site sub-intervals. | No named lifecycle (data only) | Audit log | Soft delete | 0028, 0034, 0035, 0041, 0042, 0048 |
| 10 | **Sample Batch** | A COC group: sample type + TAT + composition, with collection time and site. | No named lifecycle (stateless per ADR-0038) | Lifecycle capture | Soft delete | 0033, 0038, 0041, 0048 |
| 11 | **Document** | Unified slot-and-file entity; per-`document_type` lifecycle dispatch; single-scope (`project | deliverable | wa_code`). | Per-`document_type` (see § Document types) | Comprehensive capture | Soft delete | 0014, 0015, 0024, 0037, 0041 |
| 12 | **Deliverable** | SCA-portal submission package; bundle is a query over scoped Documents. | `pending_rfa` / `outstanding` / `under_review` / `approved` (`wasted` derived) | Lifecycle capture | Soft delete | 0022, 0029, 0042 |
| 13 | **Contractor** | On-site abatement (or other) third-party. Admin roster. | No lifecycle | Audit log | Soft delete | 0041 |
| 14 | **RFA** | Request for Amendment — coordinator-authored pending WA edits, hybrid `add | remove | budget` line items. | `draft` / `in_review` / `approved` / `rejected` / `withdrawn` | Comprehensive capture | Soft delete | 0031, 0041, 0049 |
| 15 | **Note** | Polymorphic commentary; typed reference to any entity OR history record. Subtypes: `regular | blocker | resolution | audit_reason | write_off`. | No state machine (immutable subtypes; `regular` editable) | No history | Hard delete (Notes are not deletable in domain — see § Note semantics) | 0018, 0032, 0040, 0042 |
| 16 | **DepFiling** | TRU-numbered regulatory filing bundle. Project-scoped; editable `required_doc_types`. | No named lifecycle | Audit log | Soft delete | 0023 |
| 17 | **WACodeAssignment (WACA)** | Associative entity for WA ↔ WA Code M:N. | (associative; no lifecycle) | No history | Hard delete | 0041, 0048 |
| 18 | **ContractorEngagement** | Associative entity for WA ↔ Contractor M:N with stint `(started_at, ended_at?)`. | Range-typed (engagement opens, engagement closes) | Lifecycle capture | Soft delete | 0041 |
| 19 | **Contract** | The contractual basis a project is opened against. `start_date` / `end_date?`, `code_flat_fee_schedule`. | No state machine (`pending` / `active` / `expired` derived from dates) | Audit log | Soft delete | 0043, 0044, 0045 |
| 20 | **WABundle** | Contractual-identity entity above the WA version chain. 1:1 with Project; holds the WA chain. | No state machine (contract `expected` derived from `wa_number IS NULL`) | Audit log | Soft delete | 0044, 0048 |
| 21 | **WABundleSite** | Associative entity for WABundle ↔ School M:N. | (associative; no lifecycle) | No history | Hard delete | 0048 |

**Value types and lookups (not entities):** Sample Type, Sample Subtype, Project Type, TAT options, status enums, `document_type` registry, DepFiling template constants, `WACodeConf` code-type catalog (code-side static config per ADR-0048: `code_type_id` / `name` / `default_level`).

### Notes on selected entities

The roster row is the summary; the schema and command surfaces are anchored in the ADRs listed. A handful of entities are intricate enough to warrant per-entity expansion here.

**Project (1).** The top of the domain ownership tree. State machine `active` / `closed` / `cancelled` (ADR-0037); reopen permitted from both terminals (`reopen_project(project)` is one command, branching by source state). `close_project(project, rfp_file)` consumes the closure gate (ADR-0032 + the blocker registry) and transitions RFP `missing → saved` atomically. `cancel_project(project)` cascades RFA / pending-WA cleanup. **Project ↔ WABundle is 1:1** (ADR-0044); Contract derives via `Project → WABundle → Contract` — there is no `Project.contract_id`. `create_project` is a Project + WABundle + v0-WA compound (ADR-0044); ADR-0048 added `sites: [School]` as a `create_project` parameter, declared at bundle creation.

**WA / WABundle / WA Code (3, 20, 4).** The work-authorization triangle. **WABundle** is the contractual-identity entity — 1:1 with Project, holds the WA version chain, carries `contract_id` (required at create), the SCA-supplied `(wa_number, service_id, job_number)` (nullable pre-issuance, populated at first issuance), and `sites` (M:N → School via WABundleSite, ADR-0048). **WA** is a *version* within the bundle: `wabundle_id` + `version_seq` (0-based, unique per bundle; replaces ADR-0017's `supersedes` self-reference); v0 transitions `pending → issued` **in-place** at initial issuance (ADR-0048; no new WA row), v1+ are new rows. Per-WA `issued_date` + `initialization_date` (null while `pending`, set at issuance). **WA Code** is the line item — reparented onto WABundle (ADR-0048), not onto WA or Project; carries `level: 'project' | 'building'` (required, denormalized from `WACodeConf[code_type].default_level`, fixed thereafter) and a nullable `school_id` (non-null iff `level = 'building'`, constrained to `wabundle.sites`). Project derives via `WA Code → WABundle → Project`. WA Code links to WAs through **WACodeAssignment** (WACA, ADR-0048 rename of WAAuthorization).

**WA Code lifecycle (post-ADR-0048/0049):**
- `expected` — auto-generated from coordinator activity (a TE / SB references an `(sample_type, school)` that doesn't exist on the bundle yet) or smart-command inference.
- `pending_rfa` — added to a `draft` RFA but not yet submitted.
- `rfa_in_review` — RFA submitted; SCA portal review pending.
- `issued` — present on an `issued` WA. Reached from `pending` (v0 in-place issuance), from `rfa_in_review` on `approve_rfa`, or from the SCA-direct branch of `issue_wa`.
- `budget_rfa_needed` — deferred behind budget tracking.
- `dismissed` — terminal. Entered from `{expected, pending_rfa}` only via `dismiss_wa_code(code, reason_text?)` (ADR-0049 narrowing). Means "never made it onto a WA."
- `removed` — terminal. Entered from `issued` only, via (a) `approve_rfa` resolving a `remove`-target line item, or (b) `issue_wa`'s SCA-direct branch diffing a code as dropped. Means "was on an issued WA, taken off after the fact." Distinct from `dismissed`.

Removal across three triggers (`dismiss_wa_code` / `approve_rfa` remove-target / `issue_wa` SCA-direct dropped-code) shares a single cascade under **cascade-keep-FK** (ADR-0049 §5; see § Design patterns #14).

**Time Entry (9) and Sample Batch (10).** Both are work records under WA Codes; both dropped direct `project_id` in ADR-0048 — project now derives via `wa_code → WACode → WABundle → Project`. Both carry `wa_code_id` (M:1 **mandatory at create and post-cascade per cascade-keep-FK**: the dismissal / removal cascade emits a `write_off` Note but does not null the FK). Both carry direct `site_id` (M:1 mandatory, ADR-0041). Time Entry self-describes `(employee, role_type, site, date, on_site_range, off_site_sub_intervals)` with EmployeeRole as a **derived/validated link** (lookup by `(employee, role_type, contract, date)` at rate / blocker / closure-gate time, ADR-0035 + ADR-0041 + ADR-0045 — no FK from Time Entry). Sample Batch is stateless (ADR-0038): no lifecycle of its own; its membership in a Deliverable + Lab Report drives the workflow.

**Document (11) and Deliverable (12).** **Document** is the unified slot-and-file entity (ADR-0014); per-`document_type` lifecycle dispatch (ADR-0024 menu — simple `missing → saved` for most types; cycling-family for CPR / FAMR; bespoke for Lab Report and RFP); single-scope via `(scope_type, scope_id)` with `scope_type ∈ {project, deliverable, wa_code}` (ADR-0041). Derivation sources: Deliverables (transitively WA Codes), DepFilings (direct), Sample Batches (COC + Lab Report, direct), Project (RFP, direct, ADR-0037). **Deliverable** is the SCA-portal submission package: its "bundle" is a *query* over scoped Documents (derived required + user-added at the Deliverable scope + user-added at the contained WA-Code scope, ADR-0041). Bundle is frozen at `submit_deliverable` and re-opens on rejection.

**RFA (14).** Hybrid instrument post-ADR-0049: line items typed `add | remove | budget` (budget deferred). `submit_rfa` transitions only add-target codes to `rfa_in_review`. `approve_rfa` composition: `(prior WA's codes ∪ add-target line items) \ remove-target line items`; polymorphic resolution applies add-targets per ADR-0031 and transitions remove-targets `issued → removed` (firing the shared cascade). `add_rfa_line_item(bundle, code, type: add | remove)` is the coordinator-facing surface for hybrid-RFA authoring (find-or-create draft, guard `type = remove ⇒ code.state = issued`, reject add+remove or duplicate-remove on one cycle). `amends_wa_id` is the M:1 mandatory direct ref to the WA being amended (ADR-0041); set at auto-draft creation, immutable for RFA lifetime.

**Note (15) and the Note-subtype family.** Polymorphic commentary; typed reference to any entity OR history record (ADR-0040). Subtypes: `regular` (editable by creator per ADR-0018, immutable to all other callers including superadmin), `blocker` (system-authored, immutable), `resolution` (immutable), `audit_reason` (immutable; attached to grant/revoke history records carrying optional `reason_text`), `write_off` (immutable; carries free-text `reason` synthesized from the originating event + `references` pointer to the primary cause record). Inter-Note `references` field for chaining. **Notes are not deletable** at the domain level (the "hard delete" row in the roster table reflects the technical primitive; the domain commands never call it).

**Contract (19).** The contractual basis a project is opened against (ADR-0043). Schema: `contract_number` (uniqueness-constrained natural key), `start_date` / `end_date?`, `code_flat_fee_schedule` (inline non-temporal `{code_type, fee}` collection), optional `name` (null → derived display label `C` + last 5 chars of `contract_number`). No state machine; validity (`pending` / `active` / `expired`) derived from dates. Re-attached to the WABundle by ADR-0044 (`WABundle.contract_id`, M:1, required at create; `Project.contract_id` removed). Employee rates are FK-side (`EmployeeRole.contract_id`, ADR-0045); code default flat fees inline here.

### Document types (per-`document_type` lifecycle dispatch)

Document carries a per-`document_type` lifecycle (ADR-0024 menu). Assignments at the close of Step 6c:

| Pattern | `document_type` |
|---|---|
| Simple `missing → saved` | ACP13, ACP7, ACP15, ACP21, Emergency Notification, ACP8, VAR9 (DepFiling-issued externally); COC; Daily Log |
| Cycling-family | CPR (RFA/RFP fork, 5 tracking dates); FAMR (single-step review) |
| Bespoke | Lab Report (3 states: `missing`, `saved`, `invalid`; 4 transitions including `saved → invalid` for coordinator-discovered errors and `invalid → saved` for amended reports); RFP (4 states: `missing`, `saved`, `rejected`, `withdrawn`; SCA closure-receipt artifact per ADR-0037; `rejected` and `withdrawn` terminal) |

---

## Relationships

The post-ADR-0048/0049 relationship table, rolled up from ADR-0041 with subsequent amendments (ADR-0044 re-attaches Contract to WABundle; ADR-0048 reparents WA Code onto WABundle, adds WABundleSite, drops direct `project_id` from TE / SB; ADR-0049 keeps the `wa_code` FK on referencing records under cascade-keep-FK).

| From → To | Cardinality | Kind | Source ADRs |
|---|---|---|---|
| Project ↔ WABundle | 1:1 (`WABundle.project_id` UNIQUE) | typed ref | 0044 |
| WABundle → Contract | M:1 required (`contract_id`) | typed ref | 0044 |
| WABundle → School | M:N via `WABundleSite` | associative entity | 0048 |
| WABundle → WA | 1:N (WA-side `wabundle_id`, with `version_seq` unique per bundle) | typed ref | 0044 |
| WA → WABundle | M:1 required | typed ref | 0044 |
| WA → Project | derived (via WABundle) | derived | 0044 |
| WA ↔ WA Code | M:N via `WACodeAssignment` (WACA) | associative entity | 0041, 0048 |
| WA ↔ Contractor | M:N via `ContractorEngagement` (stint markers) | associative entity | 0041 |
| WA Code → WABundle | M:1 required (`wabundle_id`) | typed ref | 0048 |
| WA Code → School | nullable M:1 (`school_id`; non-null iff `level = 'building'`, constrained to `wabundle.sites`) | typed ref | 0048 |
| WA Code → Project | derived (via WABundle) | derived | 0048 |
| WA Code → Deliverable | M:1 (codes share Deliverables) | derivation | 0022 |
| Time Entry → Employee | M:1 mandatory direct | typed ref | 0041 |
| Time Entry → School | M:1 mandatory direct (`site_id`) | typed ref | 0041 |
| Time Entry → WA Code | M:1 mandatory at create **and post-cascade** (cascade-keep-FK) | typed ref | 0020, 0048, 0049 |
| Time Entry → Project | derived (via WA Code → WABundle) | derived | 0048 |
| Time Entry → Daily Log (Document) | M:1 nullable (`daily_log`) | typed ref | 0026 |
| Time Entry ↔ EmployeeRole | derived/validated (lookup by `(employee, role_type, contract, date)`) | derived | 0041, 0045 |
| Sample Batch → WA Code | M:1 mandatory at create **and post-cascade** (cascade-keep-FK) | typed ref | 0033, 0048, 0049 |
| Sample Batch → Employee | M:1 direct (collector) | typed ref | 0033 |
| Sample Batch → School | M:1 mandatory direct (`site_id`) | typed ref | 0041 |
| Sample Batch → Project | derived (via WA Code → WABundle) | derived | 0048 |
| Sample Batch → Document (COC, Lab Report) | 1:1 derivation each | derivation | 0033 |
| Deliverable → Document (required) | 1:N derivation | derivation | 0015, 0041 |
| Document → scope | M:1 (`scope_type ∈ {project, deliverable, wa_code}`, `scope_id`) | typed ref + discriminator | 0041 |
| WA Code → Document | indirect via Deliverable | derivation chain | 0015, 0041 |
| DepFiling → Project | M:1 | typed ref | 0023 |
| DepFiling → Document | 1:N derivation (editable `required_doc_types`) | derivation | 0023 |
| Project → RFP Document | 1:N derivation (1 non-terminal + unbounded terminal) | derivation | 0037 |
| Project ↔ Contractor | derived (via `ContractorEngagement` → WA → Project) | derived | 0041 |
| EmployeeRole → Employee | M:1 (composite key) | typed ref | 0035 |
| EmployeeRole → Contract | M:1 mandatory (`contract_id`) | typed ref | 0045 |
| UserRole → User | M:1 (composite key) | typed ref | 0036 |
| User → Employee | 0..1 (`employee_id?`, UNIQUE) | typed ref | 0041 |
| RFA → WA | M:1 mandatory direct (`amends_wa_id`) | typed ref | 0041 |
| RFA → WA Code | M:N (line-item targets, polymorphic `add | remove | budget`) | targets | 0031, 0049 |
| RFA → Project | derived (via WA) | derived | 0041 |
| Note → entity OR history record | polymorphic typed ref | per subtype | 0018, 0032, 0040 |
| Note → Note | nullable `references` | typed ref | 0032 |
| `WACodeAssignment` → WA, → WA Code | composite key `(wa_id, wa_code_id)` | associative entity | 0041, 0048 |
| `ContractorEngagement` → WA, → Contractor | composite + stint markers | associative entity | 0041 |
| `WABundleSite` → WABundle, → School | composite key | associative entity | 0048 |

**Reading conventions:**
- *Typed ref* = an FK with a declared cardinality (per `framework.md` § Relationships). Direct unless tagged "derived."
- *Derived* = no stored FK; computed by following declared relationships. Reads only — no write surface.
- *Associative entity* = the relationship itself carries identity or state, so it is promoted to a row in the roster (per `framework.md` promotion rules and ADR-0004).
- *Derivation* (as a kind, distinct from "derived") = system-generated entity / record relationship per a declared rule (e.g., Sample Batch derives a COC Document at creation per ADR-0033).

**Contract-resolution path:** `entity → wa_code → WACode → WABundle → contract` for TE / SB; `WACode → WABundle → contract` for direct bundle-holders; `EmployeeRole → contract` direct. Always resolves — `create_project` guarantees a WABundle with a required `contract_id` (ADR-0044). Money values (rates, flat fees) derived through the live `WABundle.contract_id`, never snapshotted.

---

## Lifecycles

Per-entity state machines, summarized. The state vocabulary, valid transitions, and command surface for each are anchored at the source ADR; this section names them and gives the readable shape.

**Project (ADR-0037).**

```
active ─ close_project ─→ closed
       ╲ cancel_project ─→ cancelled
closed ─ reopen_project(rfp_reason ∈ {rfp_rejected, rfp_withdrawn}) ─→ active  (cycles the RFP)
cancelled ─ reopen_project ─→ active  (pure state-flip)
```

Per-project invariant: exactly one non-terminal RFP at any time (ADR-0037). `closed` is the freezing terminal (project-state-driven immutability, ADR-0038; pattern #13); `cancelled` is the non-freezing terminal (abandoned work, available for reassignment).

**WA (ADR-0030, ADR-0044, ADR-0048, ADR-0049).** Per-WA-version state:

```
pending ─ issue_wa (initial path, v0 in-place) ─→ issued
issued ─ (next version supersedes via approve_rfa or issue_wa SCA-direct branch) ─→ superseded
```

The bundle's head WA is `max(version_seq)` among non-superseded rows. `issue_wa` is the **generalized** issuance command (ADR-0049) — dispatches on `bundle.head_version_seq IS NULL`: **initial path** (no head) is v0 in-place with ADR-0022 expected-code reconciliation; **SCA-direct path** (head exists) writes a new WA at `version_seq = head + 1` and diffs against the head's code set. SCA-direct branch is hard-gated against `in_review` RFAs on the bundle (`reject_rfa` / `withdraw_rfa` first; `draft` doesn't gate). `approve_rfa` is the firm-initiated amendment path; same WA-version production semantics on success.

**WA Code (ADR-0027, ADR-0048, ADR-0049).** Detailed in § Entity roster notes above. Key transitions:

```
expected ─ rfa_drafted ─→ pending_rfa
pending_rfa ─ submit_rfa ─→ rfa_in_review
rfa_in_review ─ approve_rfa ─→ issued (or pending_rfa on rollback per ADR-0031)
expected | pending_rfa ─ dismiss_wa_code ─→ dismissed   (terminal; ADR-0049 narrowing)
issued ─ approve_rfa (remove-target) ─→ removed         (terminal; ADR-0049)
issued ─ issue_wa SCA-direct (dropped) ─→ removed       (terminal; ADR-0049)
```

`dismissed` and `removed` are both terminal and both trigger the shared removal cascade (see § Design patterns #14, cascade-keep-FK). Pattern #9 (delete-or-dismiss) no longer fires on WA Code post-ADR-0049 (`dismiss_wa_code` always transitions; the empty-draft hard-delete branch is RFA-side).

**RFA (ADR-0031, ADR-0049).**

```
(auto-created or `add_rfa_line_item` → ) draft
draft ─ submit_rfa ─→ in_review
in_review ─ approve_rfa ─→ approved   (terminal)
in_review ─ reject_rfa ─→ rejected    (terminal)
draft | in_review ─ withdraw_rfa ─→ withdrawn  (terminal)
```

Empty `draft` RFAs hard-delete (ADR-0031). Add-target line items system-derived; remove-target line items coordinator-authored via `add_rfa_line_item`. Hybrid composition on `approve_rfa`: `(prior WA's codes ∪ adds) \ removes`.

**Deliverable (ADR-0029).**

```
pending_rfa ─→ outstanding (when the WA Code is issued; derivation per ADR-0022)
outstanding ─ submit_deliverable ─→ under_review
under_review ─ approve_deliverable ─→ approved (terminal)
under_review ─ reject_deliverable ─→ outstanding (re-opens bundle)
under_review ─ withdraw_deliverable ─→ outstanding
```

`wasted` is a **derived label** (ADR-0042 reframe of ADR-0029's flag): a Deliverable is wasted iff it carries a `write_off` Note. Trigger extends to `WA Code dismissed OR removed` (ADR-0029 trigger extended by ADR-0049).

**Document (per-`document_type` dispatch, ADR-0024).** State sets per § Document types above. Save / cycle / state-transition commands are all `role >= coordinator` (ADR-0047 class rule).

**EmployeeRole and ContractorEngagement.** Both are **range-typed** entities — they don't have named states; their lifecycle is the open/close of a date range. EmployeeRole: open on create (`started_at` set), close via `close_employee_role` (`ended_at` set; ADR-0035). ContractorEngagement: open on `start_contractor_engagement` (`started_at` defaults to row-creation date), close on `end_contractor_engagement` (`ended_at` defaults to CPR-saved date, nullable, overridable — ADR-0041 + handoff carry-forward).

**Sample Batch.** Stateless (ADR-0038): no lifecycle of its own. Workflow advances through its derived Documents (COC, Lab Report) and its containment in a Deliverable.

**Stateless and lifeless entities.** Time Entry, Sample Batch, Employee, User, UserRole, Contractor, DepFiling, Contract, WABundle, WACodeAssignment, WABundleSite, Note, School all have no named lifecycle (their state is intrinsic and/or derived). For each, the framework's degenerate-single-state state machine applies (per `logic.md` § Lifecycle specification).

---

## Authorization predicates

The full per-`(role, command)` predicate table is **ADR-0047** — that ADR is the source of truth; this section gives the rolled-up readable shape and points at the table by cluster. Role catalog (ADR-0040): `superadmin` → `admin` → `coordinator` → `auditor` (linear chain in MVP; chain freezes when a non-chain role lands). Propagation default: adding a permission to a lower chain role propagates upward.

### Class rules (the long-tail compression)

Unnamed CRUD commands grouped by entity scope inherit a uniform class predicate:

| Surface | Predicate |
|---|---|
| Admin-roster CRUD on {Employee, School, Contractor, User} | `role >= admin` |
| EmployeeRole lifecycle (`create`, `edit`, `close`, `change_employee_role_rate`) | `role >= admin` |
| WA-domain commands (WA / WA Code / RFA — lifecycle + edit), except `edit_wabundle` | `role >= coordinator` |
| Time Entry CRUD | `role >= coordinator` |
| Sample Batch CRUD + composition + relink | `role >= coordinator` |
| Document save / cycle / per-`document_type` lifecycle dispatch (ADR-0024) | `role >= coordinator` |
| Deliverable lifecycle (submit / approve / reject / withdraw) | `role >= coordinator` |
| DepFiling CRUD + `edit_dep_filing_required_doc_types` | `role >= coordinator` |
| Note authoring (`create_note`) | `role >= coordinator` |
| Blocker user-facing commands (`dismiss_blocker`, `comment_blocker`) | `role >= coordinator` |
| ContractorEngagement (`start_*` / `end_*`) | `role >= coordinator` |
| Default-resolution family (`default_resolve`, `resolve_overlap[_paired]`, `resolve_open_rfa`) | `role >= coordinator` |
| Write-off lift (`revoke_write_off`) | `role >= coordinator` |
| Split / cross-project (`split_entry`) | `role >= coordinator` |

### Non-uniform rows (explicitly off-chain)

| Command | Predicate | Why non-uniform |
|---|---|---|
| `grant_user_role(user, role_type, reason_text?)` | `target_role ∈ {coordinator, auditor}` → `role >= admin`; `target_role ∈ {admin, superadmin}` → `role == superadmin` | ADR-0040 conservative grant authority |
| `revoke_user_role(user, role_type, reason_text?)` | Mirrors `grant_user_role` | ADR-0040 (revoke authority = grant authority for that target role) |
| `edit_wabundle(wabundle, fields)` | `role >= admin` | ADR-0044 — admin-side correction of a WABundle's contractual identity (`contract_id`, `wa_number`, `service_id`, `job_number`, `sites`); coordinator-side path is `issue_wa` for SCA-supplied facts |
| `edit_note(note, new_text)` | `caller == note.created_by` | ADR-0018 — Note authorship is the audit story; even `superadmin` cannot edit another user's Note. Applies only to `regular` Notes (other subtypes are immutable) |

### Locked clarifications (ADR-0047)

1. **MVP-flat coordinator scoping.** Project-scoped predicates are plain `role >= coordinator` — no `assigned_to(project)` qualifier. Per-project coordinator scoping is post-MVP and triggers chain-freeze.
2. **Project-state immutability stays a pre-condition.** ADR-0038's freezing-terminal guard is target-state-based, evaluated outside the auth predicate.
3. **No system-caller primitive.** Cascade effects inherit auth from the initiating user-facing command; the table enumerates user-facing commands only.
4. **`dismiss_wa_code` covers the user-facing command.** Cascade shape (ADR-0049 §5, cascade-keep-FK + `write_off` Notes) is separate from the predicate.

### Pipeline position

Per `logic.md` § Authorization: the predicate is evaluated first in the pipeline — before lifecycle (ADR-0009), before invariants (ADR-0010), before history capture (ADR-0008). Unauthorized commands fail with no state mutation and no history record.

---

## History patterns per entity

Rolled up from per-entity assignments across ADR-0006 + the entity-introducing ADRs. Choice criteria per `history-patterns.md` § Selection criteria.

| Pattern | Entities | Rationale |
|---|---|---|
| **Comprehensive capture** | Document, WA, RFA | Each is a high-stakes accountability surface where exact past state must be reconstructable (Document for per-`document_type` lifecycle dispatch + SCA portal evidence; WA for per-version dispute; RFA for line-item audit on the amendment cycle). |
| **Lifecycle capture** | Project, Sample Batch, Deliverable, EmployeeRole, WA Code, ContractorEngagement | Lifecycle transitions are the accountable events; attribute edits between transitions are low-stakes (Sample Batch: stateless per ADR-0038, but its derivation events are captured at the parent batch's lifecycle records; included here for consistency with its referenced derivations). |
| **Audit log** | Employee, User, Time Entry, Contractor, DepFiling, Contract, WABundle | Operational observability without per-state-reconstruction guarantees. Time Entry is data-rich but the historic facts are anchored by the Time Entry's date / range — not a state-machine entity. |
| **No history** | School, Note, UserRole, WACodeAssignment, WABundleSite | Lookup-like or associative; current row is sole record. Note's authorship audit is captured by its immutable subtypes (`audit_reason`, `write_off`, `blocker`, `resolution`); `regular` Note edits are creator-only with no separate history beyond the entity record. UserRole grants/revokes audit on User's audit log (ADR-0036 + ADR-0040). |

---

## Delete policy per entity

Soft-delete eligibility tracks history-carrying or external-history-references status. Hard delete is reserved for entities with no history and no external history references.

| Policy | Entities | Notes |
|---|---|---|
| Soft delete (guarded hard-delete eligible) | Document, WA, RFA, Project, Sample Batch, Deliverable, EmployeeRole, Employee, User, Time Entry, Contractor, WA Code, DepFiling, ContractorEngagement, Contract, WABundle | History-carrying or referenced by history records. Hard delete eligible only when an ADR-named guard clears (e.g., empty-draft RFA hard-delete per ADR-0031). |
| Hard delete | School, Note, UserRole, WACodeAssignment, WABundleSite | No history, no external history references. **Note's "hard delete" primitive is not exercised at the domain level** — Notes are not deletable through the command surface (ADR-0018). |

---

## Design patterns

Fourteen cross-cutting patterns recur across the entity surface. Each is anchored to the ADR that first formalized it; downstream ADRs refine.

1. **Temporal rate resolution** (ADR-0035). A temporal record carries a value + a date range; lookup resolves the value by `(entity, type, date)` at use time. Used for EmployeeRole rates (ADR-0035 + ADR-0045's `contract` axis).
2. **Pre-conditional lifecycle gating** (ADR-0009). A command declaring a lifecycle transition is gated by the entity's state machine before the transition fires.
3. **Derived blocking status** (ADR-0032). Closure-readiness, conflict, and constraint failures are computed (over the not-written-off entity set, post-ADR-0042) rather than persisted as primary state.
4. **Smart command inference.** A coordinator command that references an `(sample_type, school)` not yet on a WABundle auto-generates the missing WA Code on the bundle (in `expected` or `pending_rfa` depending on context; landing state is implementation-phase).
5. **Compound cascading commands.** A user-facing command may atomically execute a sequence of sub-commands (`close_project` = closure-gate + RFP transition + Project state change; `create_project` = Project + WABundle + v0-WA per ADR-0044; resolution-family commands per ADR-0046). Cascade effects inherit auth from the user-facing command (ADR-0047 locked clarification 3).
6. **WA issuance reconciliation** (ADR-0022). On `issue_wa`, the head WA's actual code set is diffed against the bundle's expected codes; missing-from-issued auto-generates `expected` (or `pending_rfa`) entries.
7. **Parameterized cycling state machine** (ADR-0024 menu, CPR family). A document type with multiple buckets and a cycle of tracking dates parameterizes the same lifecycle scaffold.
8. **Set-based derivation extended** (ADR-0029, ADR-0042). A flag like Deliverable's `wasted` is derived from the entity's relationships and notes, not persisted as primary state.
9. **Delete-or-dismiss gate.** Entities with no external references hard-delete; entities with references use the dismiss cascade. Post-ADR-0049, no longer exercised by WA Code (which always uses dismiss / removal under cascade-keep-FK); the pattern stands for other entities.
10. **Derived wasted flag** (ADR-0029, ADR-0042 reframe). A finalized or submitted entity retroactively invalidated by a downstream action is flagged via a `write_off` Note rather than mutated.
11. **Blocker-as-Note with lazy materialization** (ADR-0032). System-derived blockers stay derived (registry scan) until a coordinator engages (comment or default-resolution / dismissal). First engagement materializes a `blocker` Note (system-authored) with `surfaced_at` backfilled from entity history. Cross-project blockers materialize as paired Notes linked via `paired_blocker_ref`.
12. **Chain-dismissal** (ADR-0032, reframed by ADR-0046). When resolving one blocker structurally implies secondary entities should also leave the not-written-off domain, the registry entry declares a `chain` shape; resolution atomically emits direct `write_off` Notes on the chained entities. The MVP-named chain is `te_batches_by_coverage` (#5, #8, #11, #12 — per registry below).
13. **Project-state-driven immutability** (ADR-0038). Entities whose project membership puts them in a parent project's *freezing* terminal state (`closed`) are immutable at command guard, with declared exceptions for commentary-only paths and parent-reopen escape hatches. `cancelled` is the non-freezing terminal.
14. **Write-off / default-resolution** (ADR-0042). An entity that exists but should not count (toward billing, conflicts) is excluded by an immutable `write_off` Note carrying a reason — derived predicates compute over not-written-off entities, so exclusion dissolves the conditions the entity participated in. Produced by a guarded coordinator-initiated **default-resolution** command (the nuclear option for resolving a blocker — mandatory justification, never auto-invoked) or as a reason-inheriting cascade of another command. Reversible only by an explicit superseding command (`revoke_write_off`). Subsumes pattern #10.

   **Cascade-keep-FK refinement (ADR-0048 + ADR-0049 §5).** The `dismiss_wa_code` / removal cascade keeps the `wa_code` FK on referencing Time Entries / Sample Batches (the dismissed / removed WA Code row is retained per pattern #14's substrate; the FK still resolves bundle → project) and emits an immutable `write_off` Note on each referencing record. Retires ADR-0027's original "null `wa_code`" cascade step in full. Triggered across three command surfaces (`dismiss_wa_code`, `approve_rfa` remove-target, `issue_wa` SCA-direct dropped-code) under uniform per-trigger mechanics. Blockers #1 (TE `wa_code = null`) and #2 (SB `wa_code = null`) become unfireable predicates — formally removed by ADR-0049 §6.

---

## Blocker registry

The 10-entry blocker registry (post-ADR-0049 trim; gap-preserving numbering retained for trace continuity with ADR-0032 / ADR-0046).

| # | Blocker | Classification | Target | Command shape | Compound names | Chain |
|---|---|---|---|---|---|---|
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

9 `has-default-resolution` + 1 `fix-only` (#10 — coherence-test failure, closure-definitional). **Formal removal of #1 (TE `wa_code = null`) and #2 (SB `wa_code = null`) per ADR-0049 §6** — both unfireable post-ADR-0048 (`wa_code = null` no longer a producible state under cascade-keep-FK + WABundle-always-present + missing-derived auto-generation). #4 flagged in `post-mvp.md` as drop-candidate if MVP operation confirms it cannot fire in practice.

**The `te_batches_by_coverage` chain shape.** For a target Time Entry `TE`, the chained set is `{ batch : batch.employee == TE.employee AND batch.collection_time ∈ TE.on_site_range }` (half-open per `split_entry`'s carry-forward). Each chained batch receives a direct `write_off` Note inheriting the primary's `justification`, `references` the primary blocker Note. Used by #5, #8 (per sliver), #11, #12.

**Default-resolution command family** — uniform `role >= coordinator` (ADR-0047):
- `default_resolve(blocker, justification)` — the generic Hybrid-shape command covering the 8 `has-default-resolution` entries with `command_shape: generic`. Materializes the blocker if derived-only, writes off the registry-declared target, emits chained `write_off` Notes if a chain is declared, writes one `resolution` Note (`resolution_kind: default_resolution`).
- `resolve_overlap(blocker_note, justification)` — single-side compound for #8.
- `resolve_overlap_paired(paired_blocker_note, justification)` — joint compound for #8.
- `resolve_open_rfa(rfa, justification)` — named compound for #7. Invokes `withdraw_rfa` → cascade `dismiss_wa_code` on returned codes → cascade `write_off` Notes via the existing cascade-keep-FK → auto-draft regeneration empties naturally (empty-draft hard-deletes per ADR-0031). MVP scope: add/remove-RFA case only (budget-RFA case is `fix-only`-shaped if introduced).

---

## Vocabulary

Stabilized vocabulary at the close of Step 6c. Terms are grouped by domain area; entries link to source ADRs.

### Roles and authorization

- **Coordinator** — the app's user with project-tracking-dashboard access; job title "project manager"; function: tracking. ADR-0040.
- **Admin / Superadmin / Auditor** — see § Authorization predicates and ADR-0040 for the catalog and grant authority.

### Project and contract

- **Project** — SCA engagement. 1:1 with a WABundle (ADR-0044). States `active` / `closed` / `cancelled`.
- **WABundle** — contractual-identity entity above the WA version chain. Holds `contract_id` + SCA-supplied `(wa_number, service_id, job_number)` + `sites`. No state machine. ADR-0044, ADR-0048.
- **`wa_number` / `service_id` / `job_number`** — three SCA-supplied uniqueness-constrained natural keys; nullable pre-issuance, populated by `issue_wa`. `wa_number` is the human-facing key; `job_number` is SCA's WA id (distinct from the project number).
- **WABundle.sites** — the curated set of schools the WABundle has declared in scope (ADR-0048), via the WABundleSite associative entity. Drives the building-level WA Code containment invariant and the school-subset guard on `reassign_wa_project`.
- **Contract** — the contractual basis a project is opened against. Carries `contract_number`, `start_date` / `end_date?`, `code_flat_fee_schedule`. Re-attached to the WABundle by ADR-0044. ADR-0043.
- **`code_flat_fee_schedule`** — inline non-temporal `{code_type, fee}` collection on Contract. Default flat fee per WA code type. A code type absent from the schedule resolves to null/unpriced — no blocker (ADR-0045).
- **Contract-resolution path** — the shared derivation by which an entity resolves its governing Contract. See § Relationships.

### WA and WA Codes

- **WA** — a *version* within a WABundle. `version_seq` is a 0-based integer, unique per bundle; the head WA is `max(version_seq)`. v0 is initial, v1+ are amendment-issued. v0 `pending → issued` operates **in-place** per ADR-0048; v1+ are new rows.
- **`issued_date` / `initialization_date` (WA)** — per-WA-version date fields, null while `pending`, populated at issuance. `issued_date` = when SCA issued the document; `initialization_date` = when work under the WA is authorized to begin. The head WA's `initialization_date` drives blocker #12 (Time Entry dated before head WA's `initialization_date`).
- **Generalized `issue_wa(bundle, payload)`** — ADR-0049. Same command for initial issuance and SCA-direct corrected amendment; dispatches on `bundle.head_version_seq IS NULL`. Initial path: v0 in-place. SCA-direct path: new WA at `version_seq = head + 1`, diff against head WA's codes, hard-gated against `in_review` RFAs.
- **WA Code** — bundle-scoped line item. `level: 'project' | 'building'` (required, denormalized from `WACodeConf[code_type].default_level`); `school_id` non-null iff `level = 'building'`; `school_id ∈ wabundle.sites`. ADR-0020, ADR-0048.
- **Project-level WA Code** — `level = 'project'`; applies across the whole project, no school binding (e.g., supervision). `school_id` null.
- **Building-level WA Code** — `level = 'building'`; applies at a specific school. Sample-collection codes are one species of building-level code, not a distinct class.
- **`removed` (WA Code terminal)** — ADR-0049. `issued → removed` only, via `approve_rfa` remove-target or `issue_wa` SCA-direct dropped-code. Distinct from `dismissed` ("never made it onto a WA"). Triggers the shared removal cascade.
- **`dismiss_wa_code(wa_code, reason_text?)`** — narrowed to `{expected, pending_rfa}` targets only (ADR-0049). Always transitions; optional `reason_text` → `audit_reason` Note on the lifecycle record. `role >= coordinator`.
- **WACodeAssignment (WACA)** — associative entity for WA ↔ WA Code (composite key `(wa_id, wa_code_id)`). ADR-0041 + ADR-0048 rename — formerly WAAuthorization. Gains budget when budget tracking lands.
- **WABundleSite** — associative entity for WABundle ↔ School M:N (ADR-0048).
- **`WACodeConf`** — code-side static config for the WA-code-type catalog. Entry shape: `{ code_type_id, name, default_level }`. ADR-0048; not a DB entity in MVP.
- **`default_level` (WACodeConf entry)** — `'project' | 'building'`. Sets the immutable level of WA Code instances created from this type.
- **Third WA origin** — ADR-0049 vocabulary. The three ways an `issued` WA enters the model: (a) initial issuance, (b) RFA-driven amendment via `approve_rfa`, (c) SCA-direct corrected amendment via `issue_wa` SCA-direct branch.
- **`reassign_wa_project(wa, new_project)`** — compound command (ADR-0048) that moves a misfiled WA to its correct project. Guard: `moving_wa.codes.school_id ⊆ target_project.wabundle.sites`. `role >= coordinator`. Deeper mechanics (version_seq integration, source-bundle bookkeeping) are implementation-phase.
- **`edit_wabundle`** — `role >= admin` command for post-issuance corrections to WABundle metadata. Distinct from `issue_wa`. ADR-0044.

### RFA

- **RFA** — Request for Amendment. Carries pending WA edits. Hybrid instrument: line items typed `add | remove | budget` (budget deferred). ADR-0031 + ADR-0049.
- **`amends_wa_id`** — RFA's mandatory direct typed ref to the WA being amended; set at auto-draft creation, immutable for RFA lifetime. ADR-0041.
- **RFA line-item types (`add | remove | budget`)** — ADR-0049 hybrid discriminator. `add`: system-derived (ADR-0031). `remove`: coordinator-authored via `add_rfa_line_item`. `budget`: deferred.
- **`add_rfa_line_item(bundle, code, type: add | remove)`** — coordinator-facing command for hybrid-RFA line-item authoring. Find-or-create draft semantics. ADR-0049.

### Time Entry and Sample Batch

- **On-site range / off-site sub-interval (Time Entry)** — `on_site_range` is the parent range of an entry; `off_site_sub_intervals` are project-committed time-away spans within it (currently always lab delivery). Sub-intervals are pairwise disjoint, entirely within on-site range, positive-duration. ADR-0034.
- **Gross on-site range** — full `on_site_range`, inclusive of off-site sub-intervals. Represents project commitment. Used by the cross-project overlap predicate.
- **Net on-site time** — `on_site_range` minus off-site sub-intervals. Represents physical presence. Used by blocker #9.
- **Derived/validated link** — a relationship resolved by lookup rather than FK. Used for Time Entry ↔ EmployeeRole: lookup row from `(employee_id, role_type, contract, date)` at use time. ADR-0041, ADR-0045.
- **`site_id` (Time Entry, Sample Batch)** — M:1 mandatory direct typed reference to School. ADR-0041.
- **`sampling_locations` (Sample Batch)** — optional plain-text field describing specific spots within the site. ADR-0041.

### Documents and Deliverables

- **Document** — unified slot-and-file entity. Single-scope via `(scope_type, scope_id)`, `scope_type ∈ {project, deliverable, wa_code}`. Per-`document_type` lifecycle dispatch. ADR-0014, ADR-0041.
- **`scope_type` / `scope_id`** — single-scope discriminator + FK on Document. ADR-0041.
- **Deliverable** — SCA-portal submission package. Bundle is a query over scoped Documents. ADR-0029, ADR-0041.
- **CPR** — Contractor Package Record. Cycling-family doc with 2 buckets (RFA, RFP), 5 tracking dates. Derived per ContractorEngagement.
- **FAMR** — Final Air Monitoring Report. Cycling-family doc with single-step review.
- **COC** — Chain of Custody. Simple `missing → saved`. Derived from Sample Batch; created in `saved` state.
- **Lab Report** — Bespoke 3-state document type (`missing`, `saved`, `invalid`). Derived from Sample Batch; created in `missing`.
- **DepFiling** — Regulatory filing bundle, TRU-numbered. New entity per ADR-0023.
- **TRU** — Unique identifier the regulator assigns to a DepFiling. Natural key on DepFiling.
- **ACP / VAR** — Document-type prefixes for regulatory forms (ACP13, ACP7, ACP15, ACP21, ACP8, VAR9, etc.). All simple `missing → saved`.
- **RFP (project-level)** — Request for Payment. SCA-generated; closure-receipt artifact. Per-project invariant: exactly one non-terminal RFP at any time. ADR-0037. Distinct from CPR's internal RFP bucket (the contractor-side payment-request phase within the CPR cycling-family document).
- **Non-terminal RFP** — an RFP in `missing` or `saved` state.
- **Terminal RFP** — an RFP in `rejected` or `withdrawn` state. Accumulates with each reopen-from-`closed` event.
- **TAT** — Turnaround time for sample analysis.

### Blockers and write-offs

- **Blocker** — A structural condition (registry entry from ADR-0032) or user-flagged Note declaring something is held up. Every registry blocker has a structural-fix path. Property: **has-default-resolution** vs. **fix-only** (ADR-0042 reframe).
- **Materialized blocker** — A blocker that exists as a persisted Note record. System-derived blockers materialize on first user engagement (pattern #11).
- **Engagement** — A coordinator writing a comment about a blocker or invoking its default-resolution / dismissal. Triggers lazy materialization.
- **Write-off / written-off** — an entity that exists and is retained (audit-preserved) but does not count toward billing aggregation or blocker/conflict derivation. Recorded by an immutable `write_off` Note. Derived status. ADR-0042.
- **Default-resolution** — guarded coordinator-initiated command that resolves a blocker by writing off the conflicting entities. The "nuclear option." A blocker **has-default-resolution** iff a coherent one exists. ADR-0042, ADR-0046.
- **Cascade write-off** — a write-off produced as a side effect of a non-default-resolution command (e.g. `dismiss_wa_code`'s cascade on referencing Time Entries / Sample Batches). Inherits `reason` from the initiating command. Post-ADR-0048: keeps the `wa_code` FK (cascade-keep-FK principle).
- **`revoke_write_off`** — explicit command that lifts a write-off by writing an immutable superseding Note. `role >= coordinator`. Command shape is a carry-forward. ADR-0042.
- **`resolution_kind`** — discriminator on resolution Notes; values `structural_fix | default_resolution | dismissal`. ADR-0042.
- **Chain-dismissal** — when resolving one blocker structurally implies secondary entities should also leave the not-written-off domain. MVP-named chain: `te_batches_by_coverage`. ADR-0032, ADR-0046.
- **`te_batches_by_coverage`** — named chain shape for #5, #8, #11, #12.
- **`default_resolve(blocker, justification)`** — generic Hybrid-shape default-resolution command for the 8 `has-default-resolution` entries with `command_shape: generic`.
- **`resolve_overlap` / `resolve_overlap_paired` / `resolve_open_rfa`** — named compound default-resolution commands. ADR-0046.
- **Fork A** — narrow relink-gate relaxation on `relink_sample_batch_wa_code`: the gate's permitted-state set extends from `{wa_code IS null, current code dismissed}` to `{wa_code IS null, current code dismissed, batch trips #9}`. ADR-0046.
- **Wasted** — a derived reporting label for a written-off Deliverable. No longer an independently-derived flag — "wasted" ⟺ the Deliverable has a `write_off` Note. ADR-0042 reframe of ADR-0029.
- **Limbo chain** — WA `pending` → WA Code `expected` → Deliverable `pending_rfa`. Resolves atomically when `issue_wa` fires.
- **Cascade-keep-FK principle** — under ADR-0048 + ADR-0049, the dismissal / removal cascade keeps the `wa_code` FK on referencing Time Entries and Sample Batches and emits an immutable `write_off` Note on each. Retires ADR-0027's original "null `wa_code`" cascade step. Full mechanics per ADR-0049 §5. See § Design patterns #14.

### Cross-cutting

- **`audit_reason` (Note subtype)** — immutable Note subtype attached to history records via optional `reason_text` on grant/revoke commands. ADR-0040.
- **Reopen-from-`closed` / reopen-from-`cancelled`** — the two `reopen_project` forms. From `closed`: requires `rfp_reason ∈ {rfp_rejected, rfp_withdrawn}`; cycles the RFP. From `cancelled`: pure state-flip; no structural reason captured.
- **Propagation default** — adding a permission to a lower chain role propagates upward unless explicitly signaled otherwise. ADR-0040.
- **MVP-flat coordinator scoping** — project-scoped predicates are plain `role >= coordinator` in MVP; per-project scoping is post-MVP and triggers chain-freeze.

---

## Deferred / open questions

### Quarantine pattern — confirmed deferred

Quarantine — applying a command but isolating the affected entity in a side state outside its normal lifecycle — was flagged in ADR-0011 as not the framework default and not commissioned at the framework level, and clarified in `history-patterns.md` as a violation-handling pattern (not a history pattern). Through 49 ADRs, no entity has surfaced a concrete need: data ingestion, bulk imports, and eventual-consistency cases that quarantine would address have not appeared in MVP scope, and command rejection (the framework default) has carried all violation handling so far without strain.

**Decision at Step 6d: keep quarantine deferred.** No entity carries it. The pattern remains available as a future per-entity declaration if a concrete domain need surfaces (likely candidates if any do: bulk-import surfaces for Sample Batch, lab-report ingest for Lab Report). Re-evaluate at the implementation phase if a real workflow emerges; no new ADR is required by Step 6d to record this status — ADR-0011 + ADR-0013 + `history-patterns.md` § Cross-cutting concerns already establish it as available-but-uncommissioned.

### Command-shape carry-forwards (implementation-phase or residual)

These commands have predicate-table rows (ADR-0047) but undefined signatures and guards. They are tracked here for completeness; implementation-phase work or residual sessions will land their shapes.

- **`split_entry(time_entry, split_point[, second_split_point])`** — predicate `role >= coordinator`. Shape (split-point ergonomics, field-inheritance for `daily_log` / `wa_code` / off-site sub-intervals on resulting sub-entries, batch reassignment at boundary) undefined. Half-open interval semantics from ADR-0042 belong with this command. Load-bearing for ADR-0046's `resolve_overlap` / `resolve_overlap_paired`.
- **`revoke_write_off(write_off_note, ...)`** — predicate `role >= coordinator`. Parameters and guards undefined. Misattribution-on-closed-project recovery (scenario (b)) needs `revoke_write_off` + an ADR-0038 closed-project exception + the post-MVP cross-project Sample Batch reassignment command.
- **Revoke-line-item command** (ADR-0049 carry-forward) — rescinding a coordinator-authored `remove` line item before approval. Symmetric with the empty-draft hard-delete on a coordinator-opened draft. Parameters and guards undefined.
- **`reassign_wa_project` deeper mechanics** (ADR-0048 carry-forward) — `version_seq` integration in target chain, source-bundle bookkeeping, single-WA-only-in-bundle edge case, audit-trail shape on both sides. Implementation-phase.
- **ContractorEngagement command-shape** — `start_contractor_engagement` / `end_contractor_engagement` predicates settled (ADR-0047 `role >= coordinator`); signatures and pre-conditions deferred. Date defaults: `started_at` → row-creation date; `ended_at` → CPR-saved date (nullable, overridable).
- **ADR-0031 auto-draft regeneration suppression at closure-gate** — the bare `withdraw_rfa` structural-fix path during closure-gate can loop (`withdraw → fresh draft regenerates → #7 re-fires`). The `resolve_open_rfa` compound resolves itself. Implementation-phase or a residual.
- **Smart-command-inference state for post-issuance auto-generated codes** (ADR-0049 carry-forward) — when a TE / SB references an `(sample_type, school)` that doesn't exist on the bundle's head WA, landing state (`expected` vs. `pending_rfa`) is implementation-phase. The SCA-direct branch's reconciliation handles either case.

### Step-deferred items (not Step 6d's concern)

Conceptualization-phase scope ends here; these flow past Step 6d:

- **MVP feature cut** — Step 7.
- **Stack / architecture / persistence** — Step 8. Includes the history implementation shape (event store vs. append-only tables vs. temporal tables, per `framework.md` deferred list); persistence isolation for cross-entity invariants; backend / frontend directory disposition.
- **Conceptual data model + DDL** — Step 9.
- **Phase-transition ADR + ADR consolidation pass** — Step 9 (pre-transition consolidation: scan `decisions.md` for ADRs with 2+ amendments and consolidate per `steps.md`).

### Post-MVP

Tracked in `post-mvp.md`. Headline items:

- **Per-project coordinator scoping** — triggers chain-freeze on ADR-0047 (project-scoped rows become `role >= coordinator AND assigned_to(target.project)`).
- **Future non-chain roles** — each appends a column to ADR-0047's table without refactoring existing rows.
- **WACA budget fields** — added when budget tracking design lands (immediate post-MVP per user signal).
- **Draft invoice generation against budgets** — second post-MVP priority.
- **Billing Rate entity/table** — temporal `(subtype, TAT) → rate` lookup. Follows the temporal rate resolution template (pattern #1).
- **WACodeConf evolution to DB entity** — option if catalog churn rises beyond rare; `code_type_id` keys stable across migration.
- **`level` mutation on WA Code** — not supported in MVP (would require changing code type).
- **Cross-project Sample Batch reassignment** as a structured command.
- **Retroactive rate corrections via Time Entry rate snapshot** — reversible additive change post-MVP if signal emerges.
- **Security-immediate revoke runtime semantics** — session invalidation on `revoke_user_role`. Implementation concern; deferred to auth implementation step.

---

## Pointers

- **Framework substrate:** `framework.md` (entity / value / relationship; four-kind state taxonomy; UUID identity)
- **Logic substrate:** `logic.md` (commands; mandatory capture; lifecycle + invariant + authorization pipeline)
- **History menu:** `history-patterns.md` (per-entity history patterns; selection criteria; reference snapshotting; promotion)
- **ADR log:** `decisions.md` — ADR-0001 through ADR-0049 (Conceptualization phase)
- **Handoff:** `planning/handoff.md` (between-session state; cumulative working tables; this file's content is the post-session source of truth, the handoff carries the in-flight working state)
- **Step list:** `planning/steps.md` (current phase)
- **Phase roster:** `planning/phases.md`
- **Post-MVP catalog:** `planning/post-mvp.md`
- **Session conventions:** `planning/sessions.md`
- **File rules registry (generated):** `planning/_file-rules.md`
