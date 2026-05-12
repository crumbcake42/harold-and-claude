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

**Step 6b (continued, session 4) — Block B entity lifecycles: WA Code, Deliverable, WA (2026-05-12).** Closed out all Block B lifecycle items for WA Code, Deliverable, and WA. Confirmed stack context. Resolved blocked-as-flag implicitly. Session wrapped cleanly; no incomplete scope.

**Major outputs:**

1. **Stack confirmed (Step 8 will write ADRs).** Backend: Python / FastAPI / Ruff / SQLAlchemy / Pydantic / pytest. Frontend: Vite / React / TypeScript / TanStack Router / TanStack Query / openapi-ts / shadcn-ui / Storybook.

2. **Closure-blocker acknowledgement pattern (ADR-0027).** Per-record `acknowledged: bool` flag on Time Entry and Sample Batch. Can be set ad-hoc or batch at project closure. General pattern: any structural closure invariant the tracker may knowingly override is resolved by a flag on the blocking record, not on Project.

3. **WA Code state machine (ADR-0027).** Six states: `expected`, `pending_rfa`, `rfa_in_review`, `issued`, `budget_rfa_needed` (deferred placeholder), `dismissed`. `rfa_in_review` is locked — RFA must resolve (approve, reject, or withdraw) before dismissal is permitted. `dismiss_wa_code` compound cascade: nulls `wa_code` on referencing Time Entries and Sample Batches; derives `non_billable` flag; creates closure blocker unless `acknowledged`. Delete substituted for dismiss when code is unreferenced.

4. **Cross-project time conflict (ADR-0028).** Derived blocker — same employee, overlapping time range, different projects. Neither project may close until resolved structurally. No conflict entity; dissolves automatically. `acknowledged` flag does not apply; conflict must be resolved.

5. **Deliverable state machine (ADR-0029).** Four states: `pending_rfa`, `outstanding`, `under_review`, `approved`. Rejection and withdrawal from `under_review` return to `outstanding`. `wasted` is a derived flag (WA Code dismissed after documents prepared or submission attempted). `outstanding` Deliverable with no prepared documents hard-deleted on WA Code dismissal. `submit_deliverable` guarded: all bundled Documents must be `saved`.

6. **WA state machine (ADR-0030).** Three states: `pending`, `issued`, `superseded`. `issue_wa` compound command: transitions WA to `issued`, runs WA Code reconciliation (ADR-0022), cascades limbo chain resolution atomically. `superseded` is immutable — no commands or RFA filings accepted. `pending` WA with no referenced work hard-deleted on project cancellation.

7. **WA ↔ WA Code budget tracking direction confirmed (deferred implementation).** Option B: WA Codes mutate in place; approved RFAs serve as the diff/audit trail for budget history. Deferred to budget tracking implementation. No ADR yet.

8. **Blocked-as-flag resolved implicitly.** Collapses to: state machine guards (structural blocking), per-record `acknowledged` flag (closure-gate overrides), derived cross-project blocker (must resolve). No general `is_blocked` flag needed.

**Per-`document_type` assignments (cumulative):**

| Pattern | document_types |
|---|---|
| Simple `missing → saved` | ACP13, ACP7, ACP15, ACP21, Emergency Notification, ACP8, VAR9 (all DepFiling docs — issued externally); COC; Daily Log |
| Cycling-family | CPR (RFA/RFP fork, 5 dates), FAMR (single-step review) |

**Entity roster (16 entities):**

| # | Entity | Notes |
|---|---|---|
| 1 | Project | SCA engagement. |
| 2 | School | = Site for MVP. |
| 3 | WA | Contract document; supersedable via self-reference (ADR-0016, ADR-0017). States: `pending` / `issued` / `superseded` (ADR-0030). |
| 4 | WA Code | Project-scoped line item (ADR-0020). States: `expected` / `pending_rfa` / `rfa_in_review` / `issued` / `budget_rfa_needed` (deferred) / `dismissed` (ADR-0027). |
| 5 | User | Auth identity (username/password). |
| 6 | Employee | Person doing project work; linked to User via typed reference (0..1 ↔ 0..1). |
| 7 | EmployeeRole | Temporal work-license assignment with `(role_type, rate, start_date, end_date?)`. |
| 8 | UserRole | App-access role with grant/revoke timestamps; drives ADR-0012 authorization predicates. |
| 9 | Time Entry | Billable hours record. Employee + site + date + hours + WA Code reference (mandatory). `acknowledged: bool` for non-billable closure override. |
| 10 | Sample Batch | COC group. Carries sample type, TAT, location(s), composition `[{subtype, quantity}]`. WA Code reference (mandatory). `acknowledged: bool` for non-billable closure override. |
| 11 | Document | Unified slot+file entity. Per-`document_type` lifecycle dispatch (ADR-0024). Derivation set spans WA Codes, DepFilings, project events. Derivation fires on expected codes (ADR-0022). |
| 12 | Deliverable | SCA-portal submission package; bundles Documents (M:M). States: `pending_rfa` / `outstanding` / `under_review` / `approved` (ADR-0029). `wasted` derived flag. |
| 13 | Contractor | On-site abatement (or other) third party. |
| 14 | RFA | Request for Amendment; carries pending WA edits. May be auto-created during WA issuance reconciliation. |
| 15 | Note | Polymorphic commentary; typed reference to any entity. Creator-only edits. Not deletable. |
| 16 | DepFiling | TRU-numbered regulatory filing bundle (ADR-0023). Project-scoped; editable `required_doc_types` set; Document-derivation source. No lifecycle. |

Values / lookups (not entities): Sample Type, Sample Subtype, Project Type, TAT options, status enums, `document_type` registry, DepFiling template constants.

**Per-entity history-pattern assignments:**

| Pattern | Entities |
|---|---|
| Comprehensive capture | Document, WA, RFA |
| Lifecycle capture | Project, Sample Batch, Deliverable, EmployeeRole, UserRole, WA Code |
| Audit log | Employee, User, Time Entry, Contractor, DepFiling |
| No history | School, Note |

**Per-entity delete policy:**

| Policy | Entities | Notes |
|---|---|---|
| Soft delete (guarded hard-delete eligible) | Document, WA, RFA, Project, Sample Batch, Deliverable, EmployeeRole, UserRole, Employee, User, Time Entry, Contractor, WA Code, DepFiling | History-carrying or referenced by history records. |
| Hard delete | School, Note | No history, no external history references. |

**Design patterns (cumulative):**
1. Temporal rate resolution.
2. Pre-conditional lifecycle gating.
3. Derived blocking status.
4. Smart command inference.
5. Compound cascading commands.
6. WA issuance reconciliation.
7. Parameterized cycling state machine.
8. Set-based derivation extended.
9. **Delete-or-dismiss gate.** Entities with no external references hard-delete; entities with references use the dismiss cascade. Gate: check for references before choosing path.
10. **Derived wasted flag.** A finalized or submitted entity retroactively invalidated by a downstream action is flagged rather than mutated. Flag is derived; entity retains its last persisted state.

**Vocabulary (cumulative):**
- **Tracker** — the app's user (job title: "project manager"; function: tracking).
- **Coordinator** — office staff who manage work. Not an app user in MVP.
- **Project / School / WA / WA Code** — as before.
- **FAMR** — Final Air Monitoring Report. Cycling-family doc with single-step review.
- **CPR** — Contractor Package Record. Cycling-family doc with 2 buckets (RFA, RFP), 5 tracking dates.
- **TAT** — Turnaround time for sample analysis.
- **COC** — Chain of Custody. Simple `missing → saved` per ADR-0024 menu.
- **DepFiling** — Regulatory filing bundle, TRU-numbered. New entity (ADR-0023).
- **TRU** — Unique identifier the regulator assigns to a DepFiling. Natural key on DepFiling.
- **ACP / VAR** — Document-type prefixes for regulatory forms (ACP13, ACP7, ACP15, ACP21, ACP8, VAR9, etc.). All simple `missing → saved`.
- **Wasted** — derived flag on Deliverable: WA Code dismissed after documents prepared or submission attempted. Entity stays in current state; flag signals retroactive invalidity.
- **Limbo chain** — WA `pending` → WA Code `expected` → Deliverable `pending_rfa`. Resolves atomically when `issue_wa` fires.

## Open questions

**For session 5 (main scope — remaining entity lifecycles):**
- **Project lifecycle** — substantial. State machine (at minimum `active → closed`; possibly `on_hold`). Closure invariants span: DepFiling completeness, WA Code states (no open RFAs), Daily Log coverage (or `acknowledged`), Deliverable status, cross-project time conflicts resolved, non-billable Time Entries and Sample Batches acknowledged.
- **RFA lifecycle** — submission, in-review, approved, rejected, withdrawn. Triggers WA Code transitions (`pending_rfa → rfa_in_review`, `rfa_in_review → issued/pending_rfa`). Triggers WA supersession on approval.
- **Sample Batch lifecycle** — collection, lab handoff, results received, billing. WA Code reference mandatory; non-billable pattern applies.
- **EmployeeRole lifecycle** — temporal grant/revoke; `start_date` / `end_date?` pattern.
- **UserRole lifecycle** — grant/revoke with timestamps; drives ADR-0012 authorization predicates.

**Carried forward (deferred to later steps):**
- **WA ↔ WA Code budget tracking implementation** — Option B direction confirmed; design deferred until budget tracking is in scope.
- **Billing Rate entity/table** — temporal `(subtype, TAT) → rate` lookup. Likely Step 6c or 6d.
- **Concrete authorization roles, relationships, and per-command predicates** — Step 6c.
- **Document → Deliverable M:M** — confirmed; formal relationship declaration in Step 6c.
- **Quarantine as a per-entity violation-handling pattern** — excluded from history-pattern menu (ADR-0013); remains deferred per ADR-0011. Step 6d.
- **Bulk import file-upload relaxation** — 6b or implementation.
- **Project structure for managing N `document_types`** — defer to implementation phase.
- **History implementation shape** (event store, append-only tables, temporal tables) — Step 8.
- **Persistence isolation for cross-entity invariants** — Step 8.
- Whether existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

## Next session

**Step 6b (continued, session 5) — Workflows & lifecycles, continued.** See `planning/steps.md` for the full step brief.

### Prompt for the next session

> Continue Step 6b. Sessions 1–4 closed Block A and most of Block B. ADRs 0027–0030 are written.
>
> **Stack confirmed (no ADR yet):** backend Python/FastAPI/Ruff/SQLAlchemy/Pydantic/pytest; frontend Vite/React/TypeScript/TanStack Router/TanStack Query/openapi-ts/shadcn-ui/Storybook.
>
> **State machines finalized so far:** WA Code (6 states, ADR-0027), Deliverable (4 states, ADR-0029), WA (3 states, ADR-0030). Cross-project time conflict is a derived blocker, no entity (ADR-0028). WA ↔ WA Code budget tracking: Option B (mutate codes, RFAs as diff history), deferred implementation.
>
> **Session 5 scope — remaining entity lifecycles:**
>
> - **RFA** — states, commands, invariants. Must trigger WA Code transitions (`pending_rfa → rfa_in_review`, `rfa_in_review → issued/pending_rfa`) and WA supersession on approval. Terminal states confirmed: approved, rejected, withdrawn.
> - **Sample Batch** — collection, lab handoff, results, billing lifecycle. WA Code reference mandatory; non-billable / `acknowledged` pattern applies (ADR-0027).
> - **EmployeeRole / UserRole** — temporal grant/revoke patterns.
> - **Project** — likely substantial. Closure invariants span: DepFiling completeness, WA Code states (no open RFAs), Daily Log coverage (or acknowledged, ADR-0026), Deliverable status, cross-project time conflicts resolved (ADR-0028), non-billable records acknowledged (ADR-0027).
>
> **Process notes:**
> - Casual back-and-forth. Self-monitor context; flag wrap point if Project is too large to complete in session.
> - STOP-AND-CONFIRM gate applies — surface options in chat, await `approved`, only then write.
> - Do not write to `domain-model.md` (that's Step 6d).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6a complete; Step 6b in progress across multiple sessions)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0026)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
