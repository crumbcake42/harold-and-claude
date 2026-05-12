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

**Step 6b (continued, session 5) — RFA lifecycle landed; Sample Batch partially deliberated; blocker-pattern architectural pivot raised mid-session (2026-05-12).** Wrapped early at user request to continue on a different computer. Incomplete scope: Sample Batch ADR not written; EmployeeRole, UserRole, Project not started. Blocker-as-Note pattern under active deliberation — must resolve before Sample Batch ADR can be written.

**Major outputs:**

1. **RFA state machine and auto-generated drafts (ADR-0031).** Five states: `draft`, `in_review`, `approved`, `rejected`, `withdrawn`. Drafts are system-generated and system-managed — first `pending_rfa` WA Code transition on a project auto-creates a draft RFA (if none open); subsequent `pending_rfa` codes add line items; dismissal removes them. Tracker edits per-line budgets + free-text fields; cannot manually add/remove line items. Shortfall flag (`requested_budget < observed_need`) soft-warns at submission, does not block. `approve_rfa` is a compound mega-command that atomically creates Amendment WA directly in `issued` state (no intervening `pending`), transitions target codes `rfa_in_review → issued`, cascades Deliverables `pending_rfa → outstanding`, supersedes prior WA, and marks RFA `approved`. Amendment WA's code set is mechanically `(prior WA's codes) ∪ (RFA line items)`. `reject_rfa` and `withdraw_rfa` return target codes to `pending_rfa` (terminal for RFA, fresh draft auto-generates). At most one draft per project. Empty draft hard-deleted (never-submitted; no audit value). Withdraw permitted to any tracker. Partial approvals confirmed not to occur in practice — modifications happen via reject/withdraw + new RFA.

2. **Sample Batch positions approved in chat (no ADR yet — pending blocker-pattern decision):**
   - **Position 1 (approved):** two-state machine `received → billed` (terminal). No `collected`, no `in_lab`, no `void`. Batch enters post-analysis on COC receipt.
   - **Position 2 (approved, amended):** Lab Report becomes a new `document_type` with a **bespoke three-state machine** (`missing`, `saved`, `invalid`) per ADR-0024's escape hatch — `saved → invalid` (tracker discovered errors), `invalid → saved` (amended report accepted), `missing → invalid` also allowed (lab returned a defective report up front). The `invalid` state was added at user's request so history captures holdup. Sample Batch becomes a **Document derivation source** (parallel to ADR-0023's DepFiling → Document), producing COC (saved at batch creation) and Lab Report (missing initially). Adds Sample Batch to the derivation-source list (currently WA Code, DepFiling, project events).
   - **Position 3+ (in flight):** generalization of ADR-0027's `acknowledged` flag was being deliberated when the user pivoted to a broader blocker-as-Note proposal. See item 3.

3. **Blocker-as-Note architectural pivot (UNRESOLVED — biggest open question).** User proposed replacing ADR-0027's per-record `acknowledged: bool` flag with a uniform mechanism: Notes (ADR-0018) gain a `blocking` subtype with required resolution. Derived blockers generate system-created blocker Notes; resolution comes from either fix-triggered system resolution Notes or user dismissal ("something went wrong, moving on"). Implications touch three existing ADRs:
   - **ADR-0018 extension** (3–4 specific changes): subtypes (regular/blocker/resolution), system authorship class, inter-Note references (resolution → blocker), preserved immutability and polymorphism.
   - **ADR-0028 amendment:** introduces a **dismissable vs. fix-only** dichotomy on blocker types. Dismissable: orphans (wa_code=null), missing artifacts (Lab Report missing, COC missing, Daily Log missing), incomplete derivations (DepFiling required doc missing), in-flight RFAs at closure. Fix-only: logical impossibilities — same employee at two places at once (ADR-0028), sample collection time outside on-site interval. Implementation requires a small **blocker-type registry** classifying each type.
   - **ADR-0027 partial supersession:** only the `acknowledged: bool` field aspect; WA Code state machine and dismiss cascade survive untouched.

   User confirmed commit-now (no implementation yet; refactor cost real). Recommended materialization rule: **persist-only-dismissals** (Notes created only when a tracker dismisses a blocker; derived blockers stay derived and computed at query time; avoids system-Note churn, transient-alarm handling, and auto-resolve cross-cutting concern). Persist-all alternative (every blocker lifecycle as Note pair) discussed; rejected as too noisy for limited audit value over existing comprehensive-capture chains.

   **OPEN FORK PENDING USER POSITION:** persist-only-dismissals vs persist-all materialization. Other forks pending the persist decision: cross-project blocker attachment (two paired Notes vs multi-target reference); authorization for dismissal (likely any tracker, parallel to `withdraw_rfa`).

4. **Off-site intervals on Time Entry surfaced (Sample Batch F-clause).** Time Entry needs structured intervals: on-site range + list of off-site sub-intervals with reasons. Cross-validation invariant: sample collection time must fall within an on-site interval for some Time Entry of that employee on that date. Falls into the **fix-only** category of the proposed blocker dichotomy. Recommend separate ADR for Time Entry structural expansion + cross-validation invariant, written before Project lifecycle (closure invariants will reference it).

5. **Sample Batch history pattern — promotion proposed (unresolved).** Currently lifecycle capture per handoff cumulative table. With blocker-pattern pivot in flight, the question of comprehensive-capture promotion (to capture `acknowledge`/`relink_wa_code`/composition edits) is deferred until the blocker-Note ADR lands — composition edits and relink may end up being directly observable through their commands, and blocker dismissal is captured via the resolution Note rather than a flag mutation, which changes the calculus.

**Cumulative tables below reflect ADR-locked state only. Sample Batch position 1, position 2-amended, and the blocker-pattern positions are approved in chat but not yet ADR'd; they are not reflected in the tables until the corresponding ADRs land.**

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

**For session 6 — immediate (blocker-pattern decision blocks Sample Batch ADR):**
- **Blocker-as-Note pattern — persist-only-dismissals vs persist-all.** Resume here. Recommendation on table: persist-only-dismissals (lighter; derived blockers stay derived; Notes only materialize on tracker dismissal). User leaning maximal-with-commit-now; needs explicit position on materialization rule.
- **Cross-project blocker attachment under Note model.** ADR-0028 overlap involves two records (Time Entry on each project). Notes attach to one polymorphic target. Options: paired blocker Notes (one per record, auto-resolve together) vs multi-target Note reference (changes ADR-0018's reference shape). Pending persist decision.
- **Authorization for blocker dismissal.** Likely any tracker (parallel to `withdraw_rfa` per ADR-0031). Pin when blocker-pattern ADR is written.
- **Blocker-type registry.** Explicit classification for each blocker type as dismissable or fix-only. Initial set: non-billable orphans / Lab Report missing / COC missing / Daily Log missing / DepFiling required-doc missing / in-flight RFA at closure (dismissable); cross-project time overlap / sample collection time outside on-site interval (fix-only).

**For session 6 — Sample Batch closing items (blocked on blocker-pattern):**
- **Position 4 (not yet posed):** `relink_sample_batch_wa_code(batch, new_wa_code)` command — allowed when current `wa_code` is null; sets new code, flips `non_billable` derivation false; under blocker-Note model, the dismissal Note remains as audit. Surface mechanism (UI query: same school + same employee + collection in another project's time entry) is implementation-time.
- **Position 5:** off-site intervals on Time Entry + cross-validation invariant — separate ADR before Project. Falls into fix-only blocker category.
- **Position 6:** Sample Batch history-pattern promotion to comprehensive — re-evaluate after blocker-Note ADR (composition edits + relink command may not need promotion if blocker dismissals are captured via Notes rather than flag mutations).

**For session 6+ — remaining lifecycles:**
- **EmployeeRole / UserRole** — temporal grant/revoke patterns. Small.
- **Project** — substantial. Likely its own session (session 7) given blocker-pattern ADR + Sample Batch ADR + Time Entry ADR will eat session 6. Closure invariants span: DepFiling completeness, WA Code states (no open RFAs), Daily Log coverage (or dismissed), Deliverable status, cross-project time conflicts resolved, non-billable records dismissed. Under blocker-Note model, closure check = "no unresolved fix-only blockers + no unresolved-and-non-dismissed dismissable blockers."

**RFA edge case deferred from ADR-0031:**
- **Project cancellation handling for open drafts and `in_review` RFAs.** Handled when Project lifecycle is written.

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

**Step 6b (continued, session 6) — Resume mid-deliberation: blocker-as-Note architectural pivot, then Sample Batch ADR.** See `planning/steps.md` for the full step brief.

### Prompt for the next session

> Resume Step 6b mid-session. Session 5 wrapped early at user request to continue on a different computer; ADR-0031 (RFA) was the only ADR finalized. **Sample Batch positions 1 and 2-amended are approved in chat but not ADR'd — they cannot land as an ADR until the blocker-pattern question below is resolved, because the closure-blocker shape in Sample Batch depends on it.**
>
> **Immediate pickup — the open fork:** the user proposed replacing ADR-0027's per-record `acknowledged: bool` flag with a **uniform blocker-as-Note pattern**. Notes (ADR-0018) gain a `blocking` subtype with required resolution; derived blockers may either materialize as system-generated Notes or stay derived (with Notes created only on user dismissal). The user agreed to commit now (no implementation has happened yet; refactor cost is real). They confirmed:
> - ADR-0018 extension is acceptable (subtypes, system authorship class, inter-Note references; immutability and polymorphism preserved).
> - ADR-0028's fix-only-vs-dismissable dichotomy is workable (small blocker-type registry classifying each type).
> - ADR-0027's `acknowledged` field aspect can be superseded (rest of ADR-0027 survives untouched).
>
> **What's pending:** the **materialization rule** for derived blockers — persist-only-dismissals (recommended in session 5) vs persist-all. Persist-only-dismissals: Notes materialize only when the tracker dismisses a blocker; derived blockers are computed at query time; no system-Note churn or transient-alarm handling. Persist-all: every blocker lifecycle as a Note pair (creation by system on trigger, resolution by system on fix or by user on dismissal); fuller audit trail but heavy. User to decide.
>
> **Once materialization rule lands, the blocker-pattern ADR should:**
> - Define blocker Note subtype + resolution Note subtype.
> - Define system authorship class (synthetic User row vs nullable `created_by` with flag — pick one).
> - Define blocker-type registry (dismissable: non-billable wa_code=null, Lab Report missing, COC missing, Daily Log missing, DepFiling required-doc missing, in-flight RFA at closure; fix-only: cross-project overlap, sample collection outside on-site interval).
> - Handle cross-project blocker attachment (paired Notes on each affected record; auto-resolve together on structural fix).
> - Authorization: any tracker can write a dismissal Note (parallel to `withdraw_rfa` from ADR-0031).
> - Supersede ADR-0027's `acknowledged: bool` field (rest of ADR-0027 survives).
> - Amend ADR-0018 with explicit subtype/authorship/reference extensions.
> - Reference ADR-0028 with the dichotomy framing (no supersession; that ADR's rule survives, just slotted into a uniform mechanism).
>
> **Then resume Sample Batch:**
> - Re-pose Position 3 (closure-blocker pattern) under the new model — likely collapses to "Sample Batch closure blockers (wa_code=null, Lab Report missing/invalid) generate dismissable blocker Notes per the pattern."
> - Position 4: `relink_sample_batch_wa_code` command.
> - Position 5: separate Time Entry ADR for off-site intervals + cross-validation (fix-only blocker).
> - Position 6: history-pattern promotion to comprehensive — re-evaluate; may not be necessary under blocker-Note model.
> - Write Sample Batch ADR.
>
> **Then the remaining session 6 scope (if context allows):**
> - **Time Entry structural expansion ADR** (off-site intervals, cross-validation invariant).
> - **EmployeeRole / UserRole** (temporal grant/revoke; small; one ADR each or one combined).
>
> **Project lifecycle moves to its own session (session 7)** given the in-flight blocker-pattern ADR + Sample Batch ADR + Time Entry ADR will likely fill session 6. Project's closure invariants will reference the blocker-Note model directly (closure check = "no unresolved fix-only blockers + no unresolved-and-non-dismissed dismissable blockers"), so the model has to land first.
>
> **State machines finalized so far:** WA Code (6 states, ADR-0027), Deliverable (4 states, ADR-0029), WA (3 states, ADR-0030), RFA (5 states, ADR-0031). Cross-project time conflict is a derived blocker, no entity (ADR-0028 — will be slotted into blocker-type registry but not superseded). WA ↔ WA Code budget tracking: Option B (mutate codes, RFAs as diff history), deferred implementation.
>
> **Stack confirmed (no ADR yet, Step 8 will write):** backend Python/FastAPI/Ruff/SQLAlchemy/Pydantic/pytest; frontend Vite/React/TypeScript/TanStack Router/TanStack Query/openapi-ts/shadcn-ui/Storybook.
>
> **Process notes:**
> - Casual back-and-forth. Self-monitor context.
> - STOP-AND-CONFIRM gate applies — surface options in chat, await `approved`, only then write.
> - Do not write to `domain-model.md` (that's Step 6d).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6a complete; Step 6b in progress across multiple sessions)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0031)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
