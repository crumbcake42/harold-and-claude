# Implementation Steps

## File contract

**Holds:** Ordered list of steps within the Implementation phase. Each step maps to a milestone from `planning/roadmap.md` (M0 → M8). The first step (M0 Foundations) opens with a full brief; subsequent steps carry short stubs pointing at the roadmap, with full briefs expanded as each step lands (Case 2 sizing per `_workflow.md`).
**Update when:** A step is opened (expand its stub into a full brief — Goal / In scope / Inputs / Outputs / Estimate / Done when); a step completes (mark complete inline; advance `handoff.md`'s next-session pointer); a step partitions (split per `_workflow.md`'s Case 2 protocol). Adding a feature beyond `mvp.md`'s 6 must-haves requires a superseding ADR before editing.

Ordered plan for the Implementation phase of `sca-tracker`. Each step maps 1:1 to a roadmap milestone; partitioning into sessions happens per-step via Case 2 sizing as the step opens. The carry-forward landing index in `roadmap.md` shows which command-shape and implementation-phase carry-forwards land in which step.

---

## Step 1 — M0 Foundations (L)

**Goal:** Stand up the plumbing the rest of the Implementation phase consumes — repo skeletons, CI, the `Command` base class + dispatcher carrying the `logic.md` pipeline, history infrastructure with dispatcher-enforced capture, the adapter boundary for Postgres-specific features, and the deferred ADR-0051 / ADR-0052 carry-forwards (PaaS pick, per-invariant isolation primitives, audit-log write timing).

**In scope:**

1. **Stale-scaffolding cleanup.** Per ADR-0001 + ADR-0051: the existing `backend/` and `frontend/` directories were scaffolded in an earlier pre-conceptualization pass and are treated as starting-from-zero. Clear or repurpose them at the start of this step; commit the deletion separately so the cleanup is auditable.
2. **PaaS vendor pick + managed-Postgres offering name.** ADR-0051 carry-forward. Neon was the dev default for both work machines; the production PaaS + managed-Postgres offering pick lands here as an ADR (likely ADR-0055).
3. **Backend repo skeleton.** Python 3.12+ on CPython + FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic + Ruff + Pytest per ADR-0051. Initial migration scaffold; project layout decisions; dependency pinning.
4. **Frontend repo skeleton.** TypeScript on Node + Vite + React + TanStack Router + TanStack Query + openapi-ts + Storybook + ESLint + Prettier per ADR-0051. FastAPI's OpenAPI schema generates typed TanStack Query hooks via openapi-ts; wire that pipeline.
5. **CI pipeline.** Integration test suite against Postgres (Neon ephemeral branch per PR or docker-compose Postgres in the runner per ADR-0051). Backend + frontend lint + test + typecheck on PR.
6. **`Command` base class + dispatcher.** Carry-forward from ADR-0051 + ADR-0052. Pipeline order from `logic.md`: auth (ADR-0012 predicate evaluation per ADR-0047) → lifecycle (ADR-0009) → apply → invariants (ADR-0010) → history (ADR-0008 / ADR-0052) → commit. No handler-level skip of history capture; the framework surface does not expose a skip path per ADR-0052.
7. **History infrastructure.** Per-entity append-only history tables (3 comprehensive — Document / WA / RFA; 6 lifecycle — Project / Sample Batch / Deliverable / EmployeeRole / WA Code / ContractorEngagement) + shared `command_audit_log` (polymorphic `(entity_type, entity_id)`) per ADR-0052. Common-metadata columns. Comprehensive-pattern `snapshot` JSONB; lifecycle-pattern `from_state` / `to_state` / `transition_name` / `state_context`. Reference snapshotting rule (typed-UUID refs only) per ADR-0013 + ADR-0052 § S5.
8. **Per-invariant isolation-primitive assignment.** ADR-0052 carry-forward. `SERIALIZABLE` default + `pg_try_advisory_xact_lock` opt-in. First per-invariant choices land as part of this step (subsequent invariants choose primitives as they're implemented in later milestones). Lands as an ADR (likely ADR-0056).
9. **Audit-log write timing.** ADR-0052 carry-forward. In-txn vs. post-commit pick. Lands as the same or a separate ADR.
10. **Adapter boundary for Postgres-specific features.** JSONB ops, advisory locks, `SERIALIZABLE` isolation live behind a documented adapter per ADR-0051. SQLite offline fallback path is buildable but **not production-equivalent** (acknowledged in ADR-0051; restate in code-level docs).

**Out of scope:**

- Domain-entity DDL (Employee, Project, etc.) — lands per-entity in M1+.
- File storage backend (M5).
- Per-invariant primitive choices for invariants that haven't been implemented yet (later milestones).

**Inputs:** `planning/mvp.md`, `planning/roadmap.md`, `planning/architecture.md`, `planning/data-model.md`, `planning/framework.md`, `planning/logic.md`, `planning/history-patterns.md`, `planning/decisions.md` (esp. ADR-0001, ADR-0051, ADR-0052), `planning/handoff.md`.

**Outputs:**

- Cleaned-up `backend/` + `frontend/` (cleanup commit separate from skeleton commits).
- Backend skeleton (FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic + Ruff + Pytest), runnable + tested.
- Frontend skeleton (Vite + React + TanStack Router + TanStack Query + openapi-ts + Storybook + ESLint + Prettier), runnable + tested.
- CI workflow(s) green on a sample integration test.
- `Command` base class + dispatcher implementation, with the full pipeline + dispatcher-enforced history write.
- History infrastructure: base `command_audit_log` migration; per-entity history-table generator / pattern (per-entity tables land as their entities do).
- Adapter boundary code (JSONB / advisory-lock / isolation wrappers).
- ADR(s) for PaaS pick + Postgres offering; per-invariant isolation primitives; audit-log write timing. Estimated 1–3 new ADRs starting at ADR-0055.

**Estimate:** L per `roadmap.md`. Multi-session — partition per Case 2 fit checklist when the step opens.

**Done when:**

- `backend/` + `frontend/` skeletons exist, green on CI, runnable locally.
- Dispatcher pipeline is implemented, with a sample command (could be a no-op for testing) flowing through auth → lifecycle → apply → invariants → history → commit.
- A sample entity's history table is written by the dispatcher; `command_audit_log` is wired.
- ADR(s) for the three deferred decisions (PaaS pick, isolation primitives, audit-log timing) are written.
- M1's first command (e.g., `create_employee`) can be implemented atop the foundation in the next milestone.

---

## Step 2 — M1 Roster + role administration (M)

**Brief:** Build the 7 roster entities (Employee / School / Contractor / User / EmployeeRole / UserRole / ContractorEngagement). Implement the admin CRUD class rule (`role >= admin` per ADR-0047). `grant_user_role` / `revoke_user_role` with the conservative grant authority parameterized predicate + `audit_reason` Note materialization (ADR-0040). EmployeeRole disjoint-ranges-per-`(employee, role_type, contract)` invariant (ADR-0045); `change_employee_role_rate` 4-branch compound with `contract` dim (ADR-0039 + ADR-0045). ContractorEngagement signatures + date defaults (carry-forward landing). Admin dashboard skeleton.

**Roadmap pointer:** `planning/roadmap.md` § M1.

---

## Step 3 — M2 Contract + Project + WABundle (M)

**Brief:** Build Contract (audit-log capture, derived validity, `code_flat_fee_schedule`), Project, WABundle, WABundleSite. `create_project` compound (Project + WABundle + sites + v0 pending WA atomically per ADR-0044 + ADR-0048). `edit_wabundle` admin-only with site-mgmt guards (ADR-0048). Project-state-driven immutability substrate (pattern #13 — applied in Step 7 / M6). Coordinator project-tracking dashboard skeleton.

**Roadmap pointer:** `planning/roadmap.md` § M2.

---

## Step 4 — M3 WA + WA Code + RFA cycle (L)

**Brief:** The largest state-machinery step. WA versioning (`version_seq`), WA Code with `level` + `school_id?` + bundle-sites invariant, WACodeAssignment (WACA), WACodeConf code-side static config. Generalized `issue_wa` (initial in-place v0 + SCA-direct branch + hard-gate). `dismiss_wa_code(reason_text?)` narrowed + cascade-keep-FK + cascade `write_off` Notes (ADR-0048 + ADR-0049). `removed` terminal cascade. RFA state machine + hybrid line items (`add` system-derived; `remove` via `add_rfa_line_item`). `approve_rfa` composition `(prior ∪ adds) \ removes` with polymorphic per-line-item resolution. Auto-draft regeneration + cancelled-project suppression. `reassign_wa_project` + school-subset guard + deeper mechanics (carry-forward). Revoke-line-item command (carry-forward). Smart-command-inference landing state (carry-forward).

**Roadmap pointer:** `planning/roadmap.md` § M3.

---

## Step 5 — M4 Time Entry + Sample Batch (M)

**Brief:** Time Entry self-describing schema (no `employee_role_id` FK; derived/validated lookup per ADR-0041 + ADR-0045). On-site/off-site invariants. Cross-project overlap predicate substrate (consumed by Step 7 / M6 blocker #8). Sample Batch (stateless per ADR-0038; lifecycle capture only). Derived COC + Lab Report Document scaffolding (full per-`document_type` dispatch lands in Step 6 / M5). `relink_sample_batch_wa_code` per ADR-0049 restatement.

**Roadmap pointer:** `planning/roadmap.md` § M4.

---

## Step 6 — M5 Documents + Deliverables + DepFilings (L)

**Brief:** Document single-scope via `(scope_type, scope_id)`. Per-`document_type` lifecycle dispatch (simple / cycling-family / bespoke per ADR-0024). 12 MVP document types (ACP{7,8,13,15,21}, VAR9, Emergency Notification, COC, Daily Log, CPR, FAMR, Lab Report, RFP). Deliverable + bundle query + lifecycle commands. DepFiling + TRU + editable `required_doc_types`. Document derivation rules (Deliverable, DepFiling, Sample Batch, Project). File storage adapter (architecture.md out-of-band; storage backend TBD — local vs S3-equivalent).

**Roadmap pointer:** `planning/roadmap.md` § M5.

---

## Step 7 — M6 Closure gate + blockers + write-off + project lifecycle terminals (L)

**Brief:** The hard-mechanics step. 10-entry registry implementation per ADR-0053. Predicate evaluation over not-written-off entities. Lazy materialization. Immutable Note subtypes (blocker / resolution / audit_reason / write_off). `default_resolve` generic + named compounds (`resolve_open_rfa`, `resolve_overlap`). Chain shape `te_batches_by_coverage` (entries #5, #8, #11, #12). `comment_blocker`, `dismiss_blocker`. `close_project` compound. `cancel_project` cascade. `reopen_project` both forms. Project-state-driven immutability rule applied (pattern #13). `revoke_write_off` (carry-forward). `split_entry` (carry-forward — load-bearing for #8). `resolve_overlap_paired` (carve-out — ships if `split_entry` mechanics land, else slips per ADR-0050). ADR-0031 auto-draft regeneration suppression at closure-gate (carry-forward).

**Roadmap pointer:** `planning/roadmap.md` § M6.

---

## Step 8 — M7 Reads + reporting (M)

**Brief:** Read APIs / query views. Audit-log UI (audit_reason Notes inline). Auditor dashboard (read-only with simple filters per ADR-0040). Project-status views. Closure-readiness panel (the unresolved-blocker batch surface). Draft-invoice estimator per ADR-0038 — reads `EmployeeRole.rate` via `(employee, role_type, contract, date)` lookup; reads `Contract.code_flat_fee_schedule[wa_code.code_type]`; aggregates over Time Entries + Sample Batches; unpriced surfacing for missing schedule entries (ADR-0045).

**Roadmap pointer:** `planning/roadmap.md` § M7.

---

## Step 9 — M8 Cutover prep + hardening (S–M)

**Brief:** Data import from current spreadsheets + SCA-portal exports. Error-path hardening. Office training. Cutover plan. First real project in the tool. Placeholder for post-MVP capture (stale-RFP signal etc. — tracked, not built).

**Roadmap pointer:** `planning/roadmap.md` § M8.

---

## Carry-forward landing index

See `planning/roadmap.md` § Carry-forward landing index for the full index. Summary:

- **M0 (Step 1):** Stale-scaffolding cleanup; PaaS vendor pick + Postgres offering; `Command` base class + dispatcher; per-invariant isolation primitives; audit-log write timing.
- **M1 (Step 2):** ContractorEngagement signatures + date defaults.
- **M3 (Step 4):** `reassign_wa_project` deeper mechanics; revoke-line-item command; smart-command-inference landing state.
- **M6 (Step 7):** `split_entry`; `revoke_write_off`; ADR-0031 auto-draft regeneration suppression at closure-gate; `resolve_overlap_paired` (conditional carve-out).
