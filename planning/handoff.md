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

**Step 6b (continued, session 3) — Block A carryovers + WA Code dismiss semantics (2026-05-11).** Cleared Block A (COC direction, Daily Log structure, DepFiling history pattern) in one pass. Started Block B (entity lifecycles) with WA Code's dismissal cascade, which surfaced a coupling with Block B #8 (blocked-as-flag) via the "resolve-or-acknowledge" closure-blocker mechanic. Session wrapped before naming WA Code states/commands; writes ran on wrap-up signal.

**Major outputs:**

1. **COC lifecycle assigned (no ADR).** User confirmed prior-session "saved → missing" was a typo. COC follows the simple `missing → saved` default per ADR-0024's menu. Recorded in the per-`document_type` assignment table below.

2. **Daily Log structure (ADR-0026).** Daily Log is a Document type with simple `missing → saved` lifecycle. Daily Log → Time Entry is 1:M, modeled as a nullable typed reference (`daily_log`) on Time Entry. Time Entries can be created without a Daily Log link; project closure invariant requires every Time Entry on a closing Project to reference a Daily Log. No automatic derivation (log date ranges aren't deterministic). Per-page Daily Log assignment for visual review is deferred to `post-mvp.md`.

3. **DepFiling history pattern (ADR-0025).** Audit log (ADR-0013 pattern 2); delete policy is soft delete. Notes (ADR-0018) cover contextual commentary. Bounded accountability — captures `required_doc_types` edits and command authorship — without committing to point-in-time reconstruction.

4. **New planning file: `post-mvp.md`.** Holding pen for post-MVP feature candidates between now and Step 7's `mvp.md` out-of-scope section. First entry: per-page Daily Log assignment for visual audit review.

5. **WA Code dismiss semantics (in progress, not yet ADR).** Decision direction: `dismiss_wa_code(code)` cascade-unlinks (nulls) `wa_code` references on referencing Time Entries and Sample Batches. Null `wa_code` produces a derived "non-billable" flag on the affected record. Project closure invariant: every Time Entry and Sample Batch on a closing Project must have a non-null `wa_code` OR an explicit acknowledgement from the tracker. The "resolve-or-acknowledge" mechanic exposed a coupling with Block B #8 (blocked-as-flag): closure-blocker acknowledgement is a generalizable pattern, and the WA Code dismissal cascade is its first concrete instance.

**Incomplete scope (deferred to next session — 6b-continued-4):**
- Closure-blocker acknowledgement shape (per-record flag / project-level override list / Note-based) — recommendation made (per-record flag), not yet approved
- WA Code concrete state names, transitions, commands
- Deliverable concrete lifecycle (states, commands, invariants — including ADR-0022's `pending_RFA → outstanding` gating)
- WA pre-issuance states + supersession-immutability invariant
- WA ↔ WA Code budget tracking across versions
- Blocked-as-flag full design (likely consolidates with closure-blocker acknowledgement)
- Project, RFA, Sample Batch, EmployeeRole, UserRole lifecycles (likely a 6b session 5)

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
| 3 | WA | Contract document; supersedable via self-reference (ADR-0016, ADR-0017). Pre-issuance lifecycle. |
| 4 | WA Code | Project-scoped line item (ADR-0020). Lifecycle tracks authorization status (ADR-0021). |
| 5 | User | Auth identity (username/password). |
| 6 | Employee | Person doing project work; linked to User via typed reference (0..1 ↔ 0..1). |
| 7 | EmployeeRole | Temporal work-license assignment with `(role_type, rate, start_date, end_date?)`. |
| 8 | UserRole | App-access role with grant/revoke timestamps; drives ADR-0012 authorization predicates. |
| 9 | Time Entry | Billable hours record. Employee + site + date + hours + WA Code reference (mandatory). |
| 10 | Sample Batch | COC group. Carries sample type, TAT, location(s), composition `[{subtype, quantity}]`. WA Code reference (mandatory). |
| 11 | Document | Unified slot+file entity. Per-`document_type` lifecycle dispatch (ADR-0024). Derivation set spans WA Codes, DepFilings, project events. Derivation fires on expected codes (ADR-0022). |
| 12 | Deliverable | SCA-portal submission package; bundles Documents (M:M). Derivation fires on expected codes (ADR-0022). Lifecycle gated by WA Code status. |
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

**Design patterns (carried + added):**
1. Temporal rate resolution.
2. Pre-conditional lifecycle gating.
3. Derived blocking status.
4. Smart command inference.
5. Compound cascading commands.
6. WA issuance reconciliation.
7. **Parameterized cycling state machine.** A single declarative state machine generates per-`document_type` review-cycle lifecycles from a parameter schema (buckets × review-steps × terminal behavior).
8. **Set-based derivation extended.** Document derivation sources now include DepFiling (1:M) alongside WA Code. Same shape applies to any future source (e.g., Time Entry → Daily Log, under consideration).

**Vocabulary (carried + added):**
- **Tracker** — the app's user (job title: "project manager"; function: tracking).
- **Coordinator** — office staff who manage work. Not an app user in MVP.
- **Project / School / WA / WA Code** — as before.
- **FAMR** — Final Air Monitoring Report. Cycling-family doc with single-step review.
- **CPR** — Contractor Package Record. Cycling-family doc with 2 buckets (RFA, RFP), 5 tracking dates.
- **TAT** — Turnaround time for sample analysis.
- **COC** — Chain of Custody. Simple `missing → saved` per ADR-0024 menu (confirmed 2026-05-11).
- **DepFiling** — Regulatory filing bundle, TRU-numbered. New entity (ADR-0023).
- **TRU** — Unique identifier the regulator assigns to a DepFiling. Natural key on DepFiling.
- **ACP / VAR** — Document-type prefixes for regulatory forms (ACP13, ACP7, ACP15, ACP21, ACP8, VAR9, etc.). All simple `missing → saved`.

## Open questions

**For the next 6b session (immediate — picks up mid-Block-B):**
- **Closure-blocker acknowledgement shape.** Surfaced via WA Code dismissal cascade: when a structural closure invariant fails (e.g., a Time Entry with null `wa_code` after `dismiss_wa_code`), the tracker can either resolve (assign a new code) or acknowledge (accept the non-billable state and close anyway). Where does the acknowledgement live structurally? Three candidates:
  1. **Per-record flag** (`acknowledged_non_billable: bool` on Time Entry / Sample Batch). Granular; closure check is mechanical.
  2. **Closure-gate override list on Project.** Centralized; second source of truth → drift risk.
  3. **Note-based acknowledgement** (ADR-0018 polymorphic Note with `is_closure_acknowledgement: true`). Lightest; least machine-checkable.

  Recommendation made (Option 1, per-record flag) — not yet `approved`. Resolving this likely also resolves Block B #8 (blocked-as-flag) since both are closure-gate override patterns.

**For the next 6b session (main scope — entity lifecycles still to define):**
- **WA Code** — concrete state names (finalize from ADR-0021 placeholders: `expected` / `issued` / `pending_RFA` / `dismissed`); state-graph allowed transitions; named commands. `dismissed` semantics decided (cascade-unlink) but not yet ADR-written — pending closure-blocker shape resolution.
- **Deliverable** — concrete states, commands, invariants. ADR-0022 already specifies `pending_RFA → outstanding` gating on WA Code status; fill in the rest.
- **WA** — pre-issuance states + supersession-immutability invariant (ADR-0017 specifies the rule, needs to land in the state machine); concrete state names.
- **WA ↔ WA Code budget tracking** across WA versions — codes are project-scoped (ADR-0020) but the WA authorizes them and sets budgets. Where do the per-code budget terms live when the WA is superseded?
- **Blocked-as-flag design** — how `is_blocked` flag interacts with lifecycle transitions and gating. Probably consolidates with closure-blocker acknowledgement above.

**Likely deferred to a 6b session 5:**
- **Project lifecycle** — state machine, commands, closure invariants (probably substantial; closure-blocker acknowledgement shape feeds directly into this).
- **RFA lifecycle** — submission, approval, WA-amendment trigger.
- **Sample Batch lifecycle** — collection, lab handoff, results, billing.
- **EmployeeRole / UserRole lifecycles** — temporal grant/revoke patterns.

**Carried forward (deferred to later steps):**
- **Billing Rate entity/table** — temporal `(subtype, TAT) → rate` lookup. Likely Step 6c or 6d.
- **Concrete authorization roles, relationships, and per-command predicates** — Step 6c.
- **Document → Deliverable M:M** — confirmed; formal relationship declaration in Step 6c.
- **Quarantine as a per-entity violation-handling pattern** — excluded from history-pattern menu (ADR-0013); remains deferred per ADR-0011. Step 6d.
- **Bulk import file-upload relaxation** — 6b or implementation.
- **Project structure for managing N `document_types`** (concern: 40+ doc types could become organizational sprawl). User flagged; defer to implementation phase (Step 8 or first implementation step).
- **History implementation shape** (event store, append-only tables, temporal tables) — Step 8.
- **Persistence isolation for cross-entity invariants** — Step 8.
- Whether existing `backend/` and `frontend/` directories get deleted or repurposed — first implementation step.

## Next session

**Step 6b (continued, session 4) — Workflows & lifecycles, continued.** See `planning/steps.md` for the full step brief.

### Prompt for the next session

> Continue Step 6b mid-Block-B. Block A is closed: COC is simple `missing → saved`; Daily Log is a Document type with `daily_log` nullable typed reference on Time Entry, 1:M Daily Log → Time Entry, closure invariant requires non-null link (ADR-0026); DepFiling carries audit log + soft delete (ADR-0025). New planning file `post-mvp.md` holds out-of-MVP feature candidates (first entry: per-page Daily Log assignment for visual review).
>
> **WA Code dismiss semantics decided but not yet ADR-written.** Direction: `dismiss_wa_code(code)` cascade-unlinks `wa_code` references on Time Entries and Sample Batches; null `wa_code` → derived "non-billable" flag; project closure invariant requires non-null `wa_code` OR explicit tracker acknowledgement. The "resolve-or-acknowledge" mechanic is shared with Block B #8 (blocked-as-flag).
>
> **Immediate decision (gates WA Code ADR):** closure-blocker acknowledgement shape. Three candidates on the table — per-record flag, project-level override list, Note-based. Recommendation: per-record flag (Option 1). Resolve this first; it likely consolidates Block B #8 into the same ADR.
>
> **Then continue Block B:** for each entity below, deliver named state machine (state names + allowed transitions), named commands per transition, invariant declarations (intra-entity and cross-entity).
>
> - **WA Code** — finalize state names from ADR-0021 placeholders (`expected` / `issued` / `pending_RFA` / `dismissed`), allowed transitions, named commands. Write ADR covering dismiss-cascade + closure-blocker acknowledgement.
> - **Deliverable** — concrete states + commands; respect ADR-0022's `pending_RFA → outstanding` gating on WA Code status; compound-cascading-command behavior from WA Code issuance.
> - **WA** — pre-issuance states + supersession-immutability invariant (ADR-0017).
> - **WA ↔ WA Code budget tracking** across WA versions — where do per-code budget terms live when the WA is superseded?
>
> **Defer to a 6b session 5 if context runs out:** Project, RFA, Sample Batch, EmployeeRole, UserRole lifecycles. Project lifecycle in particular is likely substantial (closure invariants span Deliverables, DepFilings, WA Codes, plus the now-formalized acknowledgement shape).
>
> **Process notes:**
> - Stay in casual back-and-forth mode. Self-monitor context budget; flag wrap points.
> - STOP-AND-CONFIRM gate applies — surface options in chat, await `approved`, only then write.
> - Do not write to `domain-model.md` (that's Step 6d).
> - Compound cascading commands should be named and their cascade behavior specified.

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
