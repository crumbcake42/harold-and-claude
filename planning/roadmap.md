# Roadmap

## File contract

**Holds:** Ordered implementation milestones with rough sizing (S/M/L) covering the MVP feature surface from `mvp.md`, the 7 command-shape carry-forwards, and the 5 implementation-phase carry-forwards from ADR-0051 + ADR-0052. Each milestone is a coherent unit of work that delivers a slice of the system and unblocks the next; the new Implementation-phase `steps.md` (created at phase transition) breaks each milestone into sessions.
**Update when:** A milestone is partitioned, merged, reordered, or completed; a carry-forward's landing milestone changes; a "not now" item is promoted to MVP and absorbed into a milestone. Substantive scope changes (e.g., adding a feature beyond `mvp.md`'s 6 must-haves) require a superseding ADR before editing.

The Step 9b output. Built on `mvp.md` (the 6 must-have features + the 7 command-shape carry-forwards + the carve-outs), `data-model.md` (the 21-entity conceptual model), `architecture.md` (the stack + data-layer pin), `domain-model.md` § Deferred (the carry-forward catalog), and ADR-0051 + ADR-0052 (the stack + persistence commitments). Sizing scale: **S** = small slice; **M** = medium slice; **L** = large slice. No week-estimates — the project hasn't started and pretending we know weeks-to-deliver is theater. Ordering is strictly sequential at the backend slice (M1 → M2 → M3 → M4 → M5 → M6); frontend work parallelizes opportunistically within milestones.

---

## Reading this file

The **Milestone table** is the spine — each row is one milestone with size, key contents, and upstream dependencies. The **Per-milestone expansions** below the table give a one-paragraph reading per milestone for readers who want more than the table cell carries. The **Carry-forward landing index** maps every command-shape and implementation-phase carry-forward to the milestone it lands in. **Pointers** at the end thread back to the source artifacts.

---

## Milestone table

| # | Milestone | Size | Key contents | Depends on |
|---|---|---|---|---|
| **M0** | Foundations | L | Stale-scaffolding cleanup; backend + frontend repo skeletons; CI; `Command` base class + dispatcher with the logic.md pipeline; history infrastructure (per-entity tables + `command_audit_log` + dispatcher-enforced capture); per-invariant isolation-primitive assignment; audit-log write timing; adapter boundary for Postgres-specific features. *(PaaS vendor pick + managed-Postgres offering deferred per ADR-0055 — lands at user-triggered circle-back or M8.)* | — |
| **M1** | Roster + role administration (feature #6) | M | Employee / School / Contractor / User / EmployeeRole / UserRole / ContractorEngagement; admin CRUD class rule; `grant_user_role` / `revoke_user_role` parameterized + `audit_reason` Notes; EmployeeRole disjoint-ranges per `(employee, role_type, contract)`; `change_employee_role_rate` compound; ContractorEngagement signatures + date defaults; admin dashboard skeleton. | M0 |
| **M2** | Contract + Project + WABundle (parts of features #1, #2) | M | Contract; Project shell; WABundle + WABundleSite; `create_project` compound; `edit_wabundle` admin-only with site-mgmt guards; project-state-driven immutability substrate (pattern #13 — applied in M6); coordinator project-tracking dashboard skeleton. | M0, M1 |
| **M3** | WA + WA Code + RFA cycle (feature #2) | L | WA versioning via `version_seq`; WA Code with `level` + `school_id?` + bundle-sites invariant; WACodeAssignment (WACA); WACodeConf code-side static config; generalized `issue_wa` (initial in-place v0 + SCA-direct branch + hard-gate); `dismiss_wa_code(reason_text?)` narrowed + cascade-keep-FK + cascade `write_off` Notes; `removed` terminal cascade; RFA state machine + hybrid line items (`add` system-derived; `remove` via `add_rfa_line_item`); `approve_rfa` composition `(prior ∪ adds) \ removes`; auto-draft regeneration with cancelled-project suppression; `reassign_wa_project` + school-subset guard (deeper mechanics); revoke-line-item command (carry-forward landing); smart-command-inference landing state (carry-forward landing). | M0, M2 |
| **M4** | Time Entry + Sample Batch (feature #3) | M | Time Entry self-describing schema; EmployeeRole derived/validated lookup `(employee, role_type, contract, date)`; on-site/off-site invariants; cross-project overlap predicate substrate (consumed by M6 #8); Sample Batch (stateless, lifecycle capture only); derived COC + Lab Report Document scaffolding (per-document-type dispatch lands in M5); `relink_sample_batch_wa_code` per ADR-0049 restatement. | M0, M3 |
| **M5** | Documents + Deliverables + DepFilings (feature #4) | L | Document single-scope via `(scope_type, scope_id)`; per-`document_type` lifecycle dispatch (simple / cycling-family / bespoke); 12 MVP document types (ACP{7,8,13,15,21}, VAR9, Emergency Notification, COC, Daily Log, CPR, FAMR, Lab Report, RFP); Deliverable + bundle query + lifecycle commands; DepFiling + TRU + editable `required_doc_types`; document derivation rules across all four sources (Deliverable, DepFiling, Sample Batch, Project); file storage adapter (storage backend TBD — local vs S3-equivalent). | M0, M2, M3, M4 |
| **M6** | Closure gate + blockers + write-off + project lifecycle terminals (feature #5) | L | 10-entry registry implementation; predicate evaluation over not-written-off entities; lazy materialization; immutable Note subtypes (`blocker` / `resolution` / `audit_reason` / `write_off`); `default_resolve` generic + named compounds (`resolve_open_rfa`, `resolve_overlap`); chain shape `te_batches_by_coverage`; `comment_blocker`, `dismiss_blocker`; `close_project` compound (gate check + RFP `missing → saved`); `cancel_project` cascade; `reopen_project` both forms; project-state-driven immutability rule applied (pattern #13); `revoke_write_off` (carry-forward landing); `split_entry` (carry-forward landing — load-bearing for #8); `resolve_overlap_paired` (carve-out — ships if `split_entry` mechanics land, else slips per ADR-0050); ADR-0031 auto-draft regeneration suppression at closure-gate (carry-forward landing). | M0, M3, M4, M5 |
| **M7** | Reads + reporting | M | Read APIs / query views; audit-log UI (audit_reason Notes inline); auditor dashboard (read-only with simple filters); project-status views; closure-readiness panel (unresolved-blocker batch surface); draft-invoice estimator (ADR-0038 reads — rates + flat fees + sample/time aggregation; unpriced surfacing for missing `code_flat_fee_schedule` entries). | M0–M6 |
| **M8** | Cutover prep + hardening | S–M | Data import from current spreadsheets + SCA-portal exports; error-path hardening; office training; cutover plan; first real project in the tool; placeholder for post-MVP capture (stale-RFP signal etc. — tracked, not built). PaaS vendor pick + provisioning + deploy wiring + CI ephemeral-DB wiring (deferred from M0 per ADR-0055, unless user-triggered earlier). | M0–M7 |

---

## Per-milestone expansion

### M0 — Foundations

The plumbing slice. Cleans up the stale `backend/` and `frontend/` directories per ADR-0001 + ADR-0051 (the directories were scaffolded in an earlier pass and are explicitly treated as starting-from-zero by the conceptualization phase). Stands up the backend repo (FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic + Ruff + Pytest) and the frontend repo (Vite + React + TanStack Router + TanStack Query + openapi-ts + Storybook + ESLint + Prettier). Wires CI to run the integration test suite against Postgres (docker-compose in the runner). Designs and implements the `Command` base class + dispatcher carrying the logic.md pipeline (auth → lifecycle → apply → invariants → history → commit) — the carry-forward from ADR-0051. Stands up the history infrastructure per ADR-0052's per-entity append-only tables + the shared `command_audit_log`, with capture enforced in the dispatcher (no handler-level skip). Resolves the two deferred ADR-0052 questions: per-invariant isolation-primitive assignment (`SERIALIZABLE` default vs. `pg_try_advisory_xact_lock` opt-in, per invariant) and audit-log write timing (in-txn vs. post-commit). Establishes the adapter boundary for Postgres-specific features (JSONB ops, advisory locks, `SERIALIZABLE`) so the SQLite offline fallback path stays buildable per ADR-0051 — explicitly not production-equivalent. **PaaS vendor pick + managed-Postgres offering deferred per ADR-0055** — dev posture (Neon free-tier branches per machine + local) is the working environment through MVP build-out; vendor pick lands at user-triggered circle-back or at M8 cutover prep.

### M1 — Roster + role administration

The roster slice. Builds the 7 entities with no project dependencies: Employee, School, Contractor, User, EmployeeRole, UserRole, ContractorEngagement. Implements the admin CRUD class rule from ADR-0047 (`role >= admin` covers `create_*` / `edit_*` / `*_delete` on Employee / School / Contractor / User; UserRole and EmployeeRole have explicit non-class rows). UserRole grant/revoke ships with the conservative grant authority parameterized predicate per ADR-0040 + ADR-0047, with optional `reason_text` materializing an `audit_reason` Note on the grant/revoke history row per ADR-0040. EmployeeRole carries `(employee, role_type, contract, rate, start_date, end_date?)` with the disjoint-ranges-per-`(employee, role_type, contract)` invariant per ADR-0045; `change_employee_role_rate` lands as the 4-branch compound per ADR-0039 + ADR-0045 (signature includes `contract`). ContractorEngagement signatures + pre-conditions land here — the carry-forward from `mvp.md` § Command-shape carry-forwards. Frontend ships the admin dashboard skeleton (roster lists + grant/revoke flows + EmployeeRole rate management). M1 has no domain dependencies beyond M0's plumbing.

### M2 — Contract + Project + WABundle

The project-shell slice. Builds Contract (with `code_flat_fee_schedule`, audit-log capture per ADR-0043, derived validity status per `(start_date, end_date?)` + clock), Project, WABundle, and WABundleSite (associative entity per ADR-0048). `create_project` is the compound from ADR-0044 + ADR-0048 (creates Project + WABundle + sites + v0 pending WA atomically; admin-side per ADR-0040). `edit_wabundle` is admin-only with site-mgmt guards per ADR-0048 (add unconditional; remove guarded by no-referencing-codes). Project-state-driven immutability per ADR-0038 + design pattern #13 is implemented as substrate at this milestone (the rule itself is applied in M6 once `close_project` / `cancel_project` exist). Frontend ships the coordinator project-tracking dashboard skeleton (project list + project detail view). M2 depends on M0's plumbing + M1's Contract / User roster.

### M3 — WA + WA Code + RFA cycle

The amendment-cycle slice. The largest state-machinery milestone. WA carries `version_seq` (0-based per bundle) + the `pending / issued / superseded` state machine per ADR-0030 + per-version `issued_date` + `initialization_date` per ADR-0044. WA Code is single-table with `level` (`project` / `building`) discriminator + nullable `school_id` per ADR-0048; the bundle-sites containment invariant fires on building-level codes. WACodeAssignment (WACA, renamed from WAAuthorization per ADR-0048) is the associative entity for WA ↔ WA Code; WACodeConf is the code-side static catalog of `code_type_id` + display name + `default_level`. `issue_wa` is the generalized command from ADR-0049 — dispatches on `bundle.head_version_seq IS NULL` to either the initial path (in-place on v0, reconciles expected codes per ADR-0022) or the SCA-direct branch (produces v_{n+1} via diff reconciliation, hard-gated against `in_review` RFAs). `dismiss_wa_code(reason_text?)` is narrowed to `{expected, pending_rfa}` per ADR-0049; the `removed` terminal is reached from `issued` only via RFA-remove or SCA-direct; both removal paths share the keep-FK cascade emitting `write_off` Notes on referencing TE / SB per ADR-0048 + ADR-0049. RFA carries the `draft / in_review / approved / rejected / withdrawn` state machine + hybrid line items (`add` system-derived per ADR-0031; `remove` coordinator-authored via `add_rfa_line_item` per ADR-0049). `approve_rfa` composes the next WA version's code set as `(prior ∪ adds) \ removes` with polymorphic per-line-item resolution. Auto-draft regeneration is suppressed on cancelled projects per ADR-0037. `reassign_wa_project` lands with the school-subset guard + deeper mechanics from the ADR-0048 carry-forward (`version_seq` integration in target chain, source-bundle bookkeeping, single-WA-only-in-bundle edge case). The revoke-line-item command lands here (ADR-0049 carry-forward). The smart-command-inference landing state for post-issuance auto-generated codes resolves here (ADR-0049 carry-forward).

**Frontend carry-in — Contract fee-schedule editor.** Once `WACodeConf` exists, upgrade Contract's `FeeScheduleEditor` (Step 2.2c built it free-form, before any code-type catalog): replace the free-form JSONB editor with a table — one row per project-level code type, `code` + description rendered read-only from the `WACodeConf` catalog, one nullable flat-rate input per row; a blank row stays absent from `code_flat_fee_schedule` (unpriced per ADR-0045). `WACodeConf` is code-side static config, not a DB entity (ADR-0048) — it reaches the frontend via an API/static export. Open at M3: whether building-level code types are priced here too, or the table is project-level only.

### M4 — Time Entry + Sample Batch

The day-to-day-capture slice. Time Entry self-describes `(employee_id, role_type, project_id, site_id, wa_code_id, date, on_site_range, off_site_sub_intervals)` per ADR-0034 + ADR-0041 — no `employee_role_id` FK; EmployeeRole resolution is a derived/validated lookup by `(employee, role_type, contract, date)` per ADR-0045. Write-time invariants: `on_site_range.start < on_site_range.end`; each sub-interval entirely within `on_site_range`, pairwise disjoint, positive duration. The cross-project overlap predicate substrate lands here (derived; consumed by M6's blocker #8). Sample Batch is stateless per ADR-0038 (lifecycle capture only — `create_sample_batch` and `relink_sample_batch_wa_code` events); derived COC (Document created `saved`) + Lab Report (Document created `missing`) scaffolding lands here; full per-`document_type` lifecycle dispatch lands in M5. `relink_sample_batch_wa_code` permitted-state set per ADR-0049's restatement (`{current code dismissed OR removed, batch trips #9}`; the `wa_code IS null` branch is dropped post-cascade-keep-FK).

### M5 — Documents + Deliverables + DepFilings

The evidence slice. Document is single-scope via `(scope_type, scope_id)` per ADR-0041 (`scope_type ∈ {project, deliverable, wa_code}`); per-`document_type` lifecycle dispatch follows ADR-0024's three-pattern menu (simple `missing → saved` for most types; cycling-family for CPR + FAMR; bespoke for Lab Report and RFP). The 12 MVP document types: ACP{7,8,13,15,21}, VAR9, Emergency Notification (all DepFiling-issued externally, simple lifecycle); COC (simple, created `saved`); Daily Log (simple); CPR (cycling-family, 2 buckets, 5 tracking dates per ADR-0024); FAMR (cycling-family, single-step review); Lab Report (bespoke 3-state with `invalid` for coordinator-discovered errors per ADR-0033); RFP (bespoke 4-state with `rejected` / `withdrawn` terminals per ADR-0037). Deliverable's bundle is a derived query (derived-required + user-added at Deliverable scope + user-added at contained WA-Code scope), frozen at `submit_deliverable`, re-opens on reject per ADR-0029 + ADR-0041; lifecycle commands ship the full set (`submit_deliverable`, `approve_deliverable`, `reject_deliverable`, `withdraw_deliverable`). DepFiling carries TRU + editable `required_doc_types` per ADR-0023. Document derivation rules apply across all four sources (Deliverable, DepFiling, Sample Batch, Project for RFP). File storage adapter lands here — the architecture.md-flagged out-of-band concern; storage backend (local filesystem during dev; S3-equivalent in production) is an implementation-phase pick.

### M6 — Closure gate + blockers + write-off + project lifecycle terminals

The hard-mechanics slice. The most-deliberated piece of the conceptualization phase, landing as one implementation milestone. The 10-entry registry from ADR-0053 (consolidates ADR-0032) is implemented as a predicate engine evaluating each entry's condition over the not-written-off entity set. Lazy materialization fires on coordinator engagement (`comment_blocker`, `dismiss_blocker`, default-resolve) — a system-authored `blocker` Note materializes with `surfaced_at` backfilled. Immutable Note subtypes (`blocker`, `resolution`, `audit_reason`, `write_off`) enforce no-edit-after-write at the dispatcher layer. The default-resolution family ships per ADR-0046: `default_resolve(blocker, justification)` generic (covers 7 of 9 `has-default-resolution` entries); `resolve_open_rfa(rfa, justification)` named compound for #7; `resolve_overlap(blocker_note, justification)` single-side compound for #8. The chain shape `te_batches_by_coverage` lands once and is invoked by registry entries #5, #8, #11, #12 — chained Sample Batches receive direct `write_off` Notes inheriting the primary's justification. The nuclear-option guard from ADR-0042 ships: default-resolution commands are never autonomously system-initiated; mandatory justification per invocation, stamped on every `write_off` Note. `close_project` compound (gate check + RFP `missing → saved` atomic) per ADR-0037; `cancel_project` cascade (pending-WA hard-delete + `in_review` RFA auto-withdraw + empty-draft RFA hard-delete + cancelled-state RFA auto-draft suppression) per ADR-0037; `reopen_project` from `closed` (with `rfp_reason ∈ {rfp_rejected, rfp_withdrawn}` cycling the RFP) and from `cancelled` (pure flip) per ADR-0037. Project-state-driven immutability per ADR-0038 + pattern #13 applies. Four command-shape carry-forwards land here: `revoke_write_off` (predicate settled in ADR-0047, shape landing here), `split_entry` (load-bearing for #8 — split-point ergonomics + field-inheritance + batch reassignment at boundary + half-open interval semantics from ADR-0042), the ADR-0031 auto-draft regeneration suppression at closure-gate edge case, and conditionally `resolve_overlap_paired` (the `mvp.md` § Carve-outs item — ships if `split_entry`'s mechanics land in this milestone; slips post-MVP if not).

### M7 — Reads + reporting

The query slice. Read APIs / query views over the rolled-up domain — every entity supports its primary list / detail surfaces. Audit-log UI surfaces `audit_reason` Notes inline on grant/revoke history rows per ADR-0040. Auditor dashboard ships with the read-only-with-simple-filters surface per ADR-0040 — no command authority, no editing. Project-status views (the coordinator's day-to-day surface). Closure-readiness panel (the unresolved-blocker batch surface that `close_project`'s gate check consumes — coordinator sees what's blocking closure for a project, can engage with any blocker from this surface). Draft-invoice estimator per ADR-0038 — reads `EmployeeRole.rate` via the `(employee, role_type, contract, date)` lookup, reads `Contract.code_flat_fee_schedule[wa_code.code_type]` for flat fees, aggregates over Time Entries + Sample Batches; unpriced code types surface explicitly per ADR-0045 (no derived "unpriced code" signal, no closure blocker — the estimator itself shows the gap).

### M8 — Cutover prep + hardening

The end-game slice. **PaaS vendor pick + provisioning + deploy wiring + CI ephemeral-DB wiring lands here unless user-triggered earlier** (deferred from M0 per ADR-0055). Canvass shape per the deferred Step-1.2 framing: filter-first (managed Postgres 15+, monolith container target, single region, monthly cost ceiling, ops-familiarity floor); candidate slate (Render / Fly.io / Railway managed bundles; Neon-prod paired with an app PaaS; AWS / GCP / Azure if filters survive). Data import: existing project tracking lives in spreadsheets + SCA portal exports; the cutover step ingests this state into the MVP's entity surface (likely a one-shot import script + manual reconciliation rather than a sustained integration path). Error-path hardening — review of every command's failure modes, surfaces actionable rejection messages, ensures the audit log carries enough context for forensics. Office training — walk-throughs of the coordinator workflows for the team that's about to start using the tool. Cutover plan — when the first real project lands in the tool, when the spreadsheets retire. Placeholder for post-MVP capture: stale-RFP signal, structured blocker assignment + notifications, per-page Daily Log assignment, WACA budget fields + draft invoice generation against budgets, Billing Rate entity, etc. — these are tracked in `mvp.md` § Not now and surface here only as a "what we deliberately deferred" inventory for the post-MVP retrospective.

---

## Carry-forward landing index

### Command-shape carry-forwards (from `mvp.md` § Command-shape carry-forwards)

| Carry-forward | Source ADR | Lands in |
|---|---|---|
| `split_entry(time_entry, split_point[, second_split_point])` | ADR-0028 / ADR-0042 / ADR-0046 / ADR-0047 | **M6** |
| `revoke_write_off(write_off_note, ...)` | ADR-0042 / ADR-0046 / ADR-0049 / ADR-0047 | **M6** |
| Revoke-line-item command | ADR-0049 | **M3** |
| `reassign_wa_project` deeper mechanics | ADR-0048 | **M3** |
| ContractorEngagement signatures + date defaults | ADR-0041 / ADR-0047 | **M1** |
| ADR-0031 auto-draft regeneration suppression at closure-gate | ADR-0031 / ADR-0046 / ADR-0047 | **M6** |
| Smart-command-inference landing state | ADR-0049 | **M3** |

### Implementation-phase carry-forwards (from ADR-0051 + ADR-0052)

| Carry-forward | Source ADR | Lands in |
|---|---|---|
| `backend/` + `frontend/` stale-scaffolding cleanup | ADR-0001 + ADR-0051 | **M0** |
| PaaS vendor pick + managed-Postgres offering name | ADR-0051 / ADR-0055 | **M8** (deferred per ADR-0055 from M0; user-triggered circle-back may pull earlier) |
| `Command` base class + dispatcher concrete design | ADR-0051 + ADR-0052 | **M0** |
| Per-invariant isolation-primitive assignment (`SERIALIZABLE` vs `pg_try_advisory_xact_lock`) | ADR-0052 | **M0** (substrate; per-invariant decisions span milestones as invariants land) |
| Audit-log write timing (in-txn vs post-commit) | ADR-0052 | **M0** |
| CI ephemeral-PR DB wiring against chosen vendor | ADR-0055 | **M8** (bundled with vendor pick) |
| Connection-pooling decision (vendor-pooler vs SQLAlchemy pool only) | ADR-0055 | **M8** (bundled with vendor pick) |

### MVP carve-out tracking

| Carve-out | Slip condition | Lands in |
|---|---|---|
| `resolve_overlap_paired` (blocker #8 joint compound) | If `split_entry` mechanics are heavier than estimated and don't land in M6, this slips post-MVP per ADR-0050. `resolve_overlap` (single-side) ships either way. | **M6** (conditional) |

---

## Ordering rationale

- **Strictly sequential at the backend slice.** M1 → M2 → M3 → M4 → M5 → M6 is the dependency chain; each milestone needs its predecessors' entities and commands. Frontend work parallelizes opportunistically within milestones (admin dashboard inside M1; project-tracking dashboard skeleton inside M2; etc.), but the backend ordering is non-negotiable.
- **M0 lands first because everything depends on the dispatcher + history infrastructure.** The `Command` base class + dispatcher + per-entity history-table writes are framework-enforced per ADR-0008 / ADR-0052; no domain command can ship before the framework that captures it.
- **M1 (Roster) before M2 (Project) because Contract is admin-roster CRUD.** Per ADR-0047 Cluster 1, Contract creation is admin-side. M2's `create_project` needs an existing Contract row to bind the WABundle to.
- **M3 (WA cycle) before M4 (TE / SB) because TE / SB reference WA Code.** Both entities carry `wa_code_id` mandatory at create (ADR-0048 + ADR-0049 cascade-keep-FK); the WA Code lifecycle must exist before TE / SB can fire `create_*`.
- **M5 (Documents) after M3 + M4 because Documents derive from multiple sources.** Document derivation per ADR-0041 fires off Deliverables (transitively WA Codes — M3), DepFilings (M5 internal — DepFiling is built here too), Sample Batches (M4), and Project (M2 — for RFP). Per-`document_type` lifecycle dispatch can't ship without the full source set wired.
- **M6 (Closure gate) lands after M5 because every registry entry references a M3 / M4 / M5 entity.** The 10-entry registry can't be implemented honestly until all the entities its predicates reference exist. `close_project` / `cancel_project` / `reopen_project` are the project-lifecycle terminals consuming the closure gate.
- **M7 (Reads) lands after the write surface is complete.** Read APIs / dashboards / draft-invoice estimator are slice-on-top of the write surface; they don't gate any write path.
- **M8 (Cutover) is the end-game.** Data import, hardening, training, cutover plan. No domain features land in M8 — anything new requires roadmap amendment.

---

## Sizing notes

- **L milestones (M0, M3, M5, M6).** Each contains a tightly-coupled cluster that resists partition at the roadmap level. M0's plumbing decisions all interact (dispatcher pipeline + history capture + isolation primitives); M3's WA-RFA-cycle state machinery is interlocked across WA / WA Code / RFA / cascades; M5's per-`document_type` dispatch + file storage + derivation rules ship as one slice; M6's closure-gate machinery + write-off model + project-lifecycle terminals are the densest domain-deliberation cluster in the conceptualization phase. These will partition into many implementation-phase sessions via the new `steps.md`; the milestone-level shape stays L because the dependency cluster is real.
- **M milestones (M1, M2, M4, M7).** Bounded entity counts, well-understood substrate, moderate state-machinery.
- **S–M milestone (M8).** Mostly process work (data import, training, cutover); coding surface is small. Sizing depends on data-import scope (one-shot script vs. sustained sync) and office training depth.

---

## Pointers

- **Source ADR:** the Step 9b phase-transition ADR (in `decisions.md`).
- **MVP scope (drives roadmap inputs):** `planning/mvp.md` — 6 must-have features + 7 command-shape carry-forwards + `resolve_overlap_paired` carve-out + categorized "not now" list.
- **Conceptual data model:** `planning/data-model.md` — 21-entity roster + attributes + history-table topology.
- **Domain rollup:** `planning/domain-model.md` — 21 entities + 14 design patterns + 10-entry blocker registry + four-role chain + carry-forward catalog (§ Deferred / open questions).
- **Architecture sketch:** `planning/architecture.md` — component diagram + data flow + out-of-band concerns (file storage, background jobs, notifications, auth).
- **Stack pin:** ADR-0051 in `planning/decisions.md` — Python/FastAPI + TypeScript/React + PaaS-monolith.
- **Data-layer pin:** ADR-0052 in `planning/decisions.md` — PostgreSQL + per-entity history tables + `command_audit_log`.
- **Consolidated blocker model:** ADR-0053 in `planning/decisions.md` — current blocker-and-resolution model (supersedes ADR-0032).
- **Decisions log:** `planning/decisions.md` — ADR-0001 through ADR-0053 (Conceptualization phase).
- **Framework substrate:** `planning/framework.md`.
- **Logic substrate:** `planning/logic.md`.
- **History menu:** `planning/history-patterns.md`.
- **Phase roster:** `planning/phases.md`.
- **Step list (current phase):** `planning/steps.md`.
- **Handoff:** `planning/handoff.md`.
- **Workflow protocol:** `planning/_workflow.md`.
