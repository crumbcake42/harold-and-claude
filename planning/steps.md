# Implementation Steps

## File contract

**Holds:** Ordered list of steps within the Implementation phase. Each step maps to a milestone from `planning/roadmap.md` (M0 → M8). The first step (M0 Foundations) opens with a full brief; subsequent steps carry short stubs pointing at the roadmap, with full briefs expanded as each step lands (Case 2 sizing per `_workflow.md`).
**Update when:** A step is opened (expand its stub into a full brief — Goal / In scope / Inputs / Outputs / Estimate / Done when); a step completes (mark complete inline; advance `handoff.md`'s next-session pointer); a step partitions (split per `_workflow.md`'s Case 2 protocol). Adding a feature beyond `mvp.md`'s 6 must-haves requires a superseding ADR before editing.

Ordered plan for the Implementation phase of `sca-tracker`. Each step maps 1:1 to a roadmap milestone; partitioning into sessions happens per-step via Case 2 sizing as the step opens. The carry-forward landing index in `roadmap.md` shows which command-shape and implementation-phase carry-forwards land in which step.

---

## Step 1 — M0 Foundations (L)

**Partitioned 2026-05-17 (Option A — substrate-then-decisions, 5 sub-steps).** Case 2 fit checklist fired signals 1, 2, 3, 4, 5; partition required. Option A chosen because (a) M0.1 is mechanical with no deliberation overhead — lets the implementation branch get a cheap first commit (and gives Claude auto mode an easy "no-decisions" first attempt at the workplan); (b) decision sub-steps land in dependency order (PaaS picks Postgres flavor → primitives bind to that flavor → dispatcher consumes the primitives → adapter wraps the Postgres specifics). Option B (decisions-first) rejected — delays mechanical-confidence-building and stacks 2–3 sessions of pure deliberation before any code lands. Option C (3-step coarser partition) rejected — bundles 2–3 substantive decisions in one session, risking the stacking-decisions anti-pattern.

**Goal:** Stand up the plumbing the rest of the Implementation phase consumes — repo skeletons, CI, the `Command` base class + dispatcher carrying the `logic.md` pipeline, history infrastructure with dispatcher-enforced capture, the adapter boundary for Postgres-specific features, and the deferred ADR-0051 / ADR-0052 carry-forwards (PaaS pick, per-invariant isolation primitives, audit-log write timing).

**Sub-step roster:**

| Sub-step | Title | Size | Branch | ADRs expected |
|---|---|---|---|---|
| **1.1** | M0.1 Scaffolding (cleanup + repo skeletons + CI) | M | `m0/01-scaffolding` | none — mechanical |
| **1.2** | M0.2 PaaS vendor pick + managed-Postgres offering | S | `m0/02-paas-pick` | ADR-0055 |
| **1.3** | M0.3 Data-layer primitives (isolation + audit-log timing) | S–M | `m0/03-data-layer-primitives` | ADR-0056 (possibly two) |
| **1.4** | M0.4 `Command` base class + dispatcher + history infrastructure | L | `m0/04-dispatcher-and-history` | ADR-0057 if dispatcher design surfaces ADR-worthy decisions |
| **1.5** | M0.5 Adapter boundary for Postgres-specific features + integration check | S | `m0/05-adapter-boundary` | none expected |

**Execution order:** 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → (Step 1 ✓; merge `m0/foundations` → `dev` with `--no-ff`; tag `m0-complete` on dev). Each sub-step branch off `m0/foundations`; sub-step merges back into `m0/foundations` with FF. Step 2 (M1 Roster) follows.

**Inputs:** `planning/mvp.md`, `planning/roadmap.md` § M0, `planning/architecture.md`, `planning/data-model.md`, `planning/framework.md`, `planning/logic.md`, `planning/history-patterns.md`, `planning/decisions.md` (esp. ADR-0001, ADR-0051, ADR-0052), `planning/handoff.md`.

**Done when:** All 5 sub-steps complete; M1 can begin (M0 dispatcher + history infrastructure can host M1's first command, e.g., `create_employee`).

---

### Step 1.1 — M0.1 Scaffolding (M)

**Goal:** Land the mechanical scaffolding — clean the stale `backend/` and `frontend/` directories, stand up the backend + frontend repo skeletons per ADR-0051, wire CI. No deliberation, no ADRs.

**In scope:**

1. **Stale-scaffolding cleanup.** Per ADR-0001 + ADR-0051: clear the existing `backend/` and `frontend/` directories. Commit the deletion separately so the cleanup is auditable in the log.
2. **Backend repo skeleton.** Python 3.12+ on CPython + FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic + Ruff + Pytest per ADR-0051. Initial migration scaffold (no domain entities yet — just the Alembic baseline). Project layout decisions for where commands / entities / handlers / dispatcher will live (light decisions; surface at session head if any are non-obvious). Dependency pinning.
3. **Frontend repo skeleton.** TypeScript on Node + Vite + React + TanStack Router + TanStack Query + openapi-ts + Storybook + ESLint + Prettier per ADR-0051. Wire the openapi-ts pipeline (FastAPI OpenAPI schema → typed TanStack Query hooks) so the contract is enforced from M1 onward.
4. **CI pipeline.** Backend + frontend lint + test + typecheck on PR. Integration test suite against Postgres (docker-compose Postgres in the runner for now; Neon ephemeral-branch wiring waits until M0.2 picks the PaaS).

**Out of scope:**

- PaaS vendor pick — M0.2 (Step 1.2).
- Per-invariant isolation primitives + audit-log write timing — M0.3 (Step 1.3).
- `Command` base class + dispatcher + history infrastructure — M0.4 (Step 1.4).
- Adapter boundary code — M0.5 (Step 1.5).
- Any domain entity, command, or handler — M1+.

**Inputs:** ADR-0001 (stale-scaffolding); ADR-0051 (runtime stack); `architecture.md` § component diagram; `roadmap.md` § M0; `planning/handoff.md`.

**Outputs:**

- Cleaned `backend/` and `frontend/` directories (cleanup commit separate from skeleton commits).
- Backend skeleton: runnable `uvicorn` server with a healthcheck endpoint; Alembic baseline migration in place; `pytest` runs green on a sample test; `ruff check` clean.
- Frontend skeleton: runnable `vite` dev server with a sample TanStack-routed page; `tsc --noEmit` clean; ESLint + Prettier clean; Storybook scaffolding runnable; openapi-ts pipeline wired against a placeholder OpenAPI schema.
- CI workflow(s): green on the sample tests + lint + typecheck. docker-compose Postgres in the runner.
- No ADRs.

**Estimate:** M.

**Done when:**

- Both skeletons start locally with a single command (e.g., `make dev` or equivalent).
- CI is green on a PR-style integration test run.
- The openapi-ts pipeline successfully regenerates the frontend client from a sample backend OpenAPI schema.
- The `backend/` and `frontend/` directories contain only the new skeletons (no leftover stale-scaffolding files).
- Repository is ready for M0.2's PaaS pick to land without scaffolding changes.

---

### Step 1.2 — M0.2 PaaS vendor pick + managed-Postgres offering (S)

**Brief:** Pick the production PaaS vendor + managed-Postgres offering (ADR-0055). Candidates to canvass: managed PaaS bundles (Render / Fly.io / Railway); AWS (RDS + EB / Lightsail); GCP (Cloud SQL + Cloud Run); Azure equivalents; stay-on-Neon (production-tier). Trade-offs: managed-bundle simplicity vs. cloud-vendor integration depth vs. cost vs. ops familiarity. Neon is the dev default per ADR-0051; the production pick may or may not be the same.

**Roadmap pointer:** `planning/roadmap.md` § M0 item 2.

**Branch:** `m0/02-paas-pick` off `m0/foundations`.

---

### Step 1.3 — M0.3 Data-layer primitives (S–M)

**Brief:** Resolve ADR-0052's two deferred carry-forwards as a coupled pair (both are data-layer enforcement-mechanism decisions): per-invariant isolation-primitive assignment (`SERIALIZABLE` default + `pg_try_advisory_xact_lock` opt-in; first per-invariant choices land here — likely candidates per `domain-model.md` § Design patterns #3 closure-readiness cluster + EmployeeRole disjoint-ranges per ADR-0045); audit-log write timing (in-txn vs. post-commit). Lands as ADR-0056 (possibly two).

**Roadmap pointer:** `planning/roadmap.md` § M0 items 8–9.

**Branch:** `m0/03-data-layer-primitives` off `m0/foundations`.

---

### Step 1.4 — M0.4 `Command` base class + dispatcher + history infrastructure (L)

**Brief:** The load-bearing substrate. Implement the `Command` base class + dispatcher per ADR-0051 + ADR-0052, with the `logic.md` pipeline: auth (ADR-0012 predicate eval per ADR-0047) → lifecycle (ADR-0009) → apply → invariants (ADR-0010) → history (ADR-0008 / ADR-0052) → commit. No handler-level skip of history capture; framework surface does not expose a skip path. History infrastructure per ADR-0052: per-entity append-only tables generator (3 comprehensive — Document / WA / RFA; 6 lifecycle — Project / Sample Batch / Deliverable / EmployeeRole / WA Code / ContractorEngagement) + shared `command_audit_log` (polymorphic `(entity_type, entity_id)`) with timing per M0.3. Common-metadata columns; comprehensive-pattern `snapshot` JSONB; lifecycle-pattern `from_state` / `to_state` / `transition_name` / `state_context`; reference-snapshotting rule (typed-UUID refs only) per ADR-0013 + ADR-0052 § S5. ADR-0057 if dispatcher design surfaces ADR-worthy decisions. Likely needs Case 2 partitioning itself when opened.

**Roadmap pointer:** `planning/roadmap.md` § M0 items 6–7.

**Branch:** `m0/04-dispatcher-and-history` off `m0/foundations`.

---

### Step 1.5 — M0.5 Adapter boundary for Postgres-specific features (S)

**Brief:** Wrap the Postgres-specific features (JSONB ops; advisory locks per M0.3 choice; `SERIALIZABLE` isolation) behind a documented adapter per ADR-0051. SQLite offline-fallback path uses degraded equivalents; buildable but **not production-equivalent** (acknowledged in ADR-0051 + ADR-0052; restate in code-level docs). Integration check: a sample command flows through the full pipeline (dispatcher → invariants under chosen isolation → history write at chosen timing → commit) via the adapter; both Postgres and SQLite paths build (Postgres production-equivalent; SQLite degraded).

**Roadmap pointer:** `planning/roadmap.md` § M0 item 10.

**Branch:** `m0/05-adapter-boundary` off `m0/foundations`.

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
