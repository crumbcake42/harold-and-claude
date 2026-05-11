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

**Step 6b (continued, session 2) — Document lifecycle + DepFiling entity (2026-05-11).** Closed the structural picture for Document and added a new entity (DepFiling) for regulatory filing bundles. Session interrupted by user before completing the remaining entity lifecycles (Deliverable, WA Code, WA, etc.); writes ran on wrap-up signal.

**Major outputs:**

1. **Document lifecycle structurally complete (ADR-0024).** Per-`document_type` discriminator dispatches to a three-option menu:
   - **Simple** — `missing → saved`. Default for issued / externally authored / upload-and-done docs.
   - **Cycling-family** — single parameterized state machine for draft/review/approve workflows. Parameters: `base_state`, `external_pushback`, ordered `buckets[]` (each with submit-date, review-step chain, `on_full_approval ∈ {terminal, loop_to_base}`). Bucket names are baked into command names.
   - **Bespoke** — escape hatch for novel shapes.

   CPR validates parameter coverage as a 2-bucket parameterization (RFA: 2-step review, loop_to_base; RFP: 1-step review, terminal). 5 tracking dates fall out naturally. FAMR confirmed as cycling-family, single-step review.

   Code-time extensibility contract: register `document_type` value → pick pattern (or supply bespoke machine) → attach derivation source per ADR-0015 → declare commands and authorization predicates for non-trivial transitions. No framework change to add a new doc type.

2. **DepFiling added as 16th entity (ADR-0023).** TRU-numbered regulatory filing bundle, project-scoped (1:M Project → DepFiling). Primary state is an editable `required_doc_types` set seeded by UI-side templates (Regular: 4 ACPs; Emergency: 5 docs including Emergency Notification). No persisted `filing_type` attribute — templates are constants in client code, freely re-edited post-creation. 1:M with Document (not M:M). Derived docs default to simple `missing → saved`. Invariant: `remove_required_doc_type` rejected when the corresponding Document is in `saved` state. No lifecycle of its own; completeness is derived.

3. **Cycling-family "approved" is not strictly terminal.** External pushback (e.g., SCA rejecting a previously-approved doc when reviewing a Deliverable) can rewind any approved cycling doc to `base_state`. Modeled as the `external_pushback` parameter on the cycling state machine.

4. **Per-document_type assignments so far:**

   | Pattern | document_types |
   |---|---|
   | Simple `missing → saved` | ACP13, ACP7, ACP15, ACP21, Emergency Notification, ACP8, VAR9 (all DepFiling docs — issued externally) |
   | Cycling-family | CPR (RFA/RFP fork, 5 dates), FAMR (single-step review) |
   | Unsettled (next session) | COC, Daily Log |

**Incomplete scope (deferred to next session — 6b-continued-3):**
- COC lifecycle direction (typo confirmation needed)
- Daily Log lifecycle (cross-entity rule with Time Entry under consideration)
- DepFiling history pattern selection (audit log vs no history)
- Deliverable concrete lifecycle (states, commands, invariants — including ADR-0022's `pending_RFA → outstanding` gating)
- WA Code concrete state names + `dismissed` semantics
- WA pre-issuance states + supersession-immutability invariant
- WA ↔ WA Code budget tracking across versions
- Blocked-as-flag design
- Project, RFA, Sample Batch, EmployeeRole, UserRole lifecycles (likely a third 6b session)

**Revised entity roster (16 entities):**

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
| Audit log | Employee, User, Time Entry, Contractor |
| No history | School, Note |
| **Deferred** | **DepFiling** (audit log vs no history — pending) |

**Per-entity delete policy:**

| Policy | Entities | Notes |
|---|---|---|
| Soft delete (guarded hard-delete eligible) | Document, WA, RFA, Project, Sample Batch, Deliverable, EmployeeRole, UserRole, Employee, User, Time Entry, Contractor, WA Code | History-carrying or referenced by history records. |
| Hard delete | School, Note | No history, no external history references. |
| **Deferred** | **DepFiling** | Likely soft (Documents reference it). To finalize with history-pattern choice. |

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
- **COC** — Chain of Custody. Lifecycle direction unsettled (see open questions).
- **DepFiling** — Regulatory filing bundle, TRU-numbered. New entity (ADR-0023).
- **TRU** — Unique identifier the regulator assigns to a DepFiling. Natural key on DepFiling.
- **ACP / VAR** — Document-type prefixes for regulatory forms (ACP13, ACP7, ACP15, ACP21, ACP8, VAR9, etc.). All simple `missing → saved`.

## Open questions

**For the next 6b session (opening — small carryovers from this session):**
- **COC lifecycle direction.** User wrote "saved → missing" in chat — unclear whether typo for simple `missing → saved` or literal (COC authored locally, then sent to lab and missing until signed copy returned). Confirm direction before assigning a pattern.
- **Daily Log lifecycle.** Two sub-questions gate this:
  1. Which Time Entries imply a Daily Log? All? Only field/site entries? Driven by a WA Code attribute?
  2. Does one Daily Log cover one date or a date range?

  If the matching rule is mechanical, proposal is to make Time Entry a Document-derivation source (Daily Log slot per (employee, project, date) tuple with a Time Entry), with system-derived blocking when slots are missing. If the rule has many exceptions, leave it to operational notes per ADR-0018.
- **DepFiling history pattern.** Choose between audit log (best-effort accountability for who built the filing) and no history. Affects delete policy.

**For the next 6b session (main scope — entity lifecycles still to define):**
- **Deliverable** — concrete states, commands, invariants. ADR-0022 already specifies `pending_RFA → outstanding` gating on WA Code status; fill in the rest.
- **WA Code** — concrete state names (finalize from ADR-0021 placeholders: `expected` / `issued` / `pending_RFA` / `dismissed`); resolve **`dismissed` semantics** — what happens to Time Entries and Sample Batches referencing a dismissed code? Reassigned, kept as "work done, not billed," or other?
- **WA** — pre-issuance states + supersession-immutability invariant (ADR-0017 specifies the rule, needs to land in the state machine); concrete state names.
- **WA ↔ WA Code budget tracking** across WA versions — codes are project-scoped (ADR-0020) but the WA authorizes them and sets budgets. Where do the per-code budget terms live when the WA is superseded?
- **Blocked-as-flag design** — how `is_blocked` flag interacts with lifecycle transitions and gating.

**Likely deferred to a third 6b session:**
- **Project lifecycle** — state machine, commands, closure invariants (probably substantial).
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

**Step 6b (continued, session 3) — Workflows & lifecycles, continued.** See `planning/steps.md` for the full step brief.

### Prompt for the next session

> Continue Step 6b. Document is structurally done (ADR-0024): per-`document_type` dispatch from a three-pattern menu (simple / cycling-family / bespoke), with cycling-family parameterized over buckets × review-steps × terminal behavior. DepFiling added as 16th entity (ADR-0023): TRU-numbered regulatory filing bundle, project-scoped, editable `required_doc_types` set, no persisted filing-type, 1:M with Document. Roster is now 16 entities.
>
> **Opening (small carryovers — resolve quickly):**
> 1. COC direction — `missing → saved` or literally saved→missing (locally-authored-then-await-signed-return)? Was user typo ambiguous in the last session.
> 2. Daily Log — confirm the derivation rule (which Time Entries imply a log; one date or range?). If mechanical, commit to Time Entry as a Document-derivation source for Daily Log slots. If not, leave to operational notes.
> 3. DepFiling history pattern — audit log vs no history. Also locks delete policy.
>
> **Main scope: entity lifecycles still pending.** For each entity below, deliver: named state machine (state names + allowed transitions), named commands per transition, invariant declarations (intra-entity and cross-entity).
>
> - **Deliverable** — concrete states + commands; respect ADR-0022's `pending_RFA → outstanding` gating on WA Code status; compound-cascading-command behavior from WA Code issuance.
> - **WA Code** — finalize concrete state names (ADR-0021 placeholders: `expected` / `issued` / `pending_RFA` / `dismissed`). Resolve `dismissed` semantics for referencing Time Entries and Sample Batches.
> - **WA** — pre-issuance states + supersession-immutability invariant (ADR-0017).
> - **WA ↔ WA Code budget tracking** across WA versions — where do per-code budget terms live when the WA is superseded?
> - **Blocked-as-flag design** — `is_blocked` flag interaction with lifecycle and gating.
>
> **Defer to a third 6b session if context runs out:** Project, RFA, Sample Batch, EmployeeRole, UserRole lifecycles. Project lifecycle in particular is likely substantial (closure invariants span Deliverables, DepFilings, WA Codes).
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
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0024)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
