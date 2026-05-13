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

**Step 6b (continued, session 6) — Blocker-as-Note pattern (ADR-0032) and Sample Batch + Lab Report (ADR-0033) landed; ADR-0027 acknowledged-flag aspect superseded; Time Entry ADR proposal staged but not yet approved (2026-05-12).** Productive session. Two substantial ADRs written; the architectural pivot that blocked session 5 is now resolved. Time Entry off-site-intervals ADR (ADR-0034) staged in chat with recommendations on all three forks; carries to session 7. EmployeeRole, UserRole, Project still not started.

**Major outputs:**

1. **Blocker-as-Note pattern (ADR-0032).** Unifies closure blockers and operational blockers under typed Note subtypes (`regular | blocker | resolution`) on the existing polymorphic Note entity (ADR-0018). Key decisions:
   - **Materialization rule: lazy on user engagement (refined from session 5's "persist-only-dismissals").** System-derived blockers stay derived (registry scan) until a tracker engages — either writes a comment about the blocker or dismisses it. At first engagement the blocker Note materializes (system-authored) with `surfaced_at` backfilled from underlying entity history and `created_at = now`. Transient blockers no one cared about never materialize. Refined to "any engagement trigger" (not just dismissal) so the investigation thread has an anchor when trackers actively work a blocker.
   - **Authorship class: nullable `created_by` + `authorship_class: 'user' | 'system'` enum** on Note. Edit predicate from ADR-0018 amended to `authorship_class == 'user' AND subtype == 'regular' AND caller == note.created_by`. System-authored Notes are never user-editable; blocker and resolution Notes are immutable regardless of authorship. Generalizes beyond blocker Notes — system-generated RFA drafts (ADR-0031) use the same shape.
   - **Cross-project blockers: paired Notes with inter-Note reference.** When the second project's tracker engages, a paired Note materializes on its side; both Notes carry `paired_blocker_ref`. Each project's tracker maintains a separate investigation thread (operationally right — different vendor contacts, different escalation paths). Resolution Notes are written independently per side.
   - **Dismissal authorization: any tracker** (parallel to `withdraw_rfa` per ADR-0031). Project-level decision, uniform across origin types, no staff-rotation dead-letter risk.
   - **Dismissable/fix-only registry: 9 entries, 8 dismissable + 1 fix-only.** Initial population locked; future ADRs append. Classification test: "is there a real-world acceptance path?" Yes ⇒ dismissable; no (logical impossibility) ⇒ fix-only.
   - **Chain-dismissal pattern.** When one blocker's dismissal structurally causes another's condition to fire, the secondary materializes as already-dismissed atomically (linked via `references` field on the resolution Note pointing at the causing dismissal).
   - **Project closure gate:** no `fix-only` blockers + every `dismissable` blocker either no longer holds OR has a dismissal resolution Note. Closure UI surfaces unresolved-dismissable set as batch-acknowledge flow.
   - **Amends ADR-0018** in three ways (subtype field, authorship-class + nullable created_by, inter-Note `references` field). **Partial supersession of ADR-0027** (acknowledged-flag aspect only; state machine and dismiss cascade survive). **References ADR-0028** (no supersession; cross-project overlap stays derived, just slots into the uniform mechanism).

2. **Sample Batch + Lab Report (ADR-0033).** Consolidates Sample Batch design end-to-end:
   - **State machine: `received → billed` (two states, terminal).** Tracker engages on COC receipt; no pre-receipt or void states. `received → billed` trigger deferred to billing-design step.
   - **Lab Report as new `document_type` with bespoke three-state machine** (`missing`, `saved`, `invalid`) per ADR-0024's escape hatch. All four transitions valid (`missing → saved`, `missing → invalid`, `saved → invalid`, `invalid → saved`). Closure-blocker fires on state ∈ {missing, invalid}. ADR-0024 menu amended.
   - **Sample Batch as Document-derivation source** (joins WA Code, DepFiling). Each batch derives one COC document (saved at creation) and one Lab Report document (missing initially). ADR-0015 amended.
   - **`relink_sample_batch_wa_code` command — strict orphan-recovery gating + cross-project use by construction.** Permitted only when current wa_code is null or its code is in `dismissed` state. `new_wa_code` is not constrained to the current project's codes — cross-project misfiling recovery uses the same command. Sample-to-wa-code mapping is mechanically deterministic per `(sample_type, school)`, so smart auto-relink fires when a deterministic match becomes available.
   - **Chain-dismissal rule for blocker #9 → #2 linkage.** Dismissing #9 atomically: writes resolution Note for #9, nulls `wa_code`, materializes blocker Note for #2 (system-authored), writes paired auto-dismissal resolution Note for #2 referencing the #9 dismissal. Generalization of the chain-dismissal pattern lives in ADR-0032.
   - **Smart-inference UI hint for misfiled batch.** When blocker #9 holds, system queries `(same employee + same school + Time Entry on a different project covering the collection time)` and surfaces "possibly misfiled — did you mean Project Y?" Read-side derivation; no state change. Resolution path is manual (dismiss #9 + relink to Project Y's code).
   - **History pattern: lifecycle capture (unchanged).** Composition edits handled via tracker discipline + explanatory Notes; promotion to comprehensive deferred pending post-MVP signal.

3. **ADR-0027 partial supersession.** The per-record `acknowledged: bool` field on Time Entry and Sample Batch is removed; closure-blocker resolution for those entities goes through the resolution-Note mechanism. WA Code state machine and `dismiss_wa_code` compound cascade are untouched.

4. **Time Entry off-site intervals (ADR-0034) — proposal staged in chat, awaits approval.** Three forks deliberated:
   - **Interval representation:** on-site range + list of off-site sub-intervals with reasons (recommended) vs flat list of disjoint on-site intervals vs status-quo scalar `hours`.
   - **Off-site reason shape:** free-text (recommended for MVP) vs enum+free-text fallback.
   - **Cross-project overlap predicate (ADR-0028 amendment):** net on-site time (recommended) vs gross on-site range.
   - All three Position A recommended. User did not approve; carries to session 7. Blocker #9's predicate becomes "batch's collection time does not fall within any Time Entry's net on-site interval for that employee on that date."

5. **Post-MVP additions written to `post-mvp.md`:** (a) Track-this pin for blockers (notification-coupled); (b) Structured blocker assignment + notifications (would force partial supersession of ADR-0018's no-history stance); (c) Structured cross-project Sample Batch reassignment (one-command move with notification handoff). All three bundle naturally — they share a notification substrate.

**Cumulative tables below reflect ADR-locked state through ADR-0033.**

**Per-`document_type` assignments (cumulative):**

| Pattern | document_types |
|---|---|
| Simple `missing → saved` | ACP13, ACP7, ACP15, ACP21, Emergency Notification, ACP8, VAR9 (all DepFiling docs — issued externally); COC; Daily Log |
| Cycling-family | CPR (RFA/RFP fork, 5 dates), FAMR (single-step review) |
| Bespoke | Lab Report (3 states: `missing`, `saved`, `invalid`; 4 transitions including `saved → invalid` for tracker-discovered errors and `invalid → saved` for amended reports) |

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
| 9 | Time Entry | Billable hours record. Employee + site + date + hours + WA Code reference (mandatory). Structural expansion (on-site range + off-site sub-intervals) staged for ADR-0034 (session 7). |
| 10 | Sample Batch | COC group. Carries sample type, TAT, location(s), composition `[{subtype, quantity}]`. WA Code reference (mandatory, nullable via dismiss cascade only). States: `received` / `billed` (ADR-0033). Document-derivation source (COC + Lab Report). |
| 11 | Document | Unified slot+file entity. Per-`document_type` lifecycle dispatch (ADR-0024). Derivation set spans WA Codes, DepFilings, project events. Derivation fires on expected codes (ADR-0022). |
| 12 | Deliverable | SCA-portal submission package; bundles Documents (M:M). States: `pending_rfa` / `outstanding` / `under_review` / `approved` (ADR-0029). `wasted` derived flag. |
| 13 | Contractor | On-site abatement (or other) third party. |
| 14 | RFA | Request for Amendment; carries pending WA edits. May be auto-created during WA issuance reconciliation. |
| 15 | Note | Polymorphic commentary; typed reference to any entity. Subtypes `regular | blocker | resolution` (ADR-0032). `authorship_class: 'user' | 'system'` + nullable `created_by`. Inter-Note `references` field. Regular user Notes are creator-editable per ADR-0018; blocker and resolution Notes are immutable. Not deletable. |
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
11. **Blocker-as-Note with lazy materialization.** System-derived blockers stay derived (registry scan) until a tracker engages (comment or dismissal). First engagement materializes a blocker Note (system-authored) with `surfaced_at` backfilled from entity history. Dismissable vs fix-only classification per registry. Cross-project blockers materialize as paired Notes linked via `paired_blocker_ref`. (ADR-0032)
12. **Chain-dismissal.** When dismissing one blocker structurally causes another's condition to fire, the secondary materializes as already-dismissed atomically; the secondary's resolution Note `references` the primary dismissal Note. (ADR-0032; first concrete instance in ADR-0033 for blocker #9 → #2.)

**Vocabulary (cumulative):**
- **Tracker** — the app's user (job title: "project manager"; function: tracking).
- **Coordinator** — office staff who manage work. Not an app user in MVP.
- **Project / School / WA / WA Code** — as before. School = site = building for MVP. Sample collection codes are school-scoped (e.g., "asbestos sampling at school A"); a WA may authorize work across multiple schools and carry multiple sample-collection codes (one per `(sample_type, school)`).
- **FAMR** — Final Air Monitoring Report. Cycling-family doc with single-step review.
- **CPR** — Contractor Package Record. Cycling-family doc with 2 buckets (RFA, RFP), 5 tracking dates.
- **TAT** — Turnaround time for sample analysis.
- **COC** — Chain of Custody. Simple `missing → saved` per ADR-0024 menu. Derived from Sample Batch (ADR-0033); created in `saved` state at batch creation.
- **Lab Report** — Bespoke 3-state document type (`missing`, `saved`, `invalid`) per ADR-0033. Derived from Sample Batch; created in `missing` state.
- **DepFiling** — Regulatory filing bundle, TRU-numbered. New entity (ADR-0023).
- **TRU** — Unique identifier the regulator assigns to a DepFiling. Natural key on DepFiling.
- **ACP / VAR** — Document-type prefixes for regulatory forms (ACP13, ACP7, ACP15, ACP21, ACP8, VAR9, etc.). All simple `missing → saved`.
- **Wasted** — derived flag on Deliverable: WA Code dismissed after documents prepared or submission attempted. Entity stays in current state; flag signals retroactive invalidity.
- **Limbo chain** — WA `pending` → WA Code `expected` → Deliverable `pending_rfa`. Resolves atomically when `issue_wa` fires.
- **Blocker** — A structural condition (registry entry from ADR-0032) or user-flagged Note declaring something is held up. Dismissable (real-world acceptance path exists) or fix-only (logical impossibility, must be resolved).
- **Materialized blocker** — A blocker that exists as a persisted Note record (vs purely-derived, registry-only). System-derived blockers materialize on first user engagement.
- **Engagement** — A tracker writing a comment about a blocker or dismissing it. The trigger for lazy materialization of system-derived blockers.
- **Chain-dismissal** — When dismissing one blocker structurally causes another's condition to fire, the secondary is materialized as already-dismissed atomically. Linked via the resolution Note's `references` field.

## Open questions

**For session 7 — immediate:**
- **Time Entry off-site intervals ADR (ADR-0034) — staged but not yet approved.** Three forks proposed in chat with Position A recommended on each: (1) interval representation = on-site range + off-site sub-intervals with reasons, (2) reason shape = free-text for MVP, (3) cross-project overlap predicate (ADR-0028 amendment) = net on-site time. User did not say `approved` before wrap. Pick up by re-posing forks (or accept recommendations) and writing the ADR. Blocker #9's predicate becomes "batch's collection time does not fall within any Time Entry's net on-site interval for that employee on that date."
- **EmployeeRole / UserRole lifecycle ADRs.** Temporal grant/revoke patterns. Small — likely one ADR each or one combined. Should fit alongside ADR-0034 in session 7.

**For session 8 (Project):**
- **Project lifecycle ADR.** Substantial. Closure invariants span: no fix-only blockers + every dismissable blocker resolved (per ADR-0032 closure gate text). DepFiling completeness, WA Code states (no open RFAs), Daily Log coverage, Deliverable status, cross-project time conflicts, non-billable records — all flow through the registry now. Cancellation handling for open drafts and `in_review` RFAs (deferred from ADR-0031) lands here.

**Carry-forwards from ADR-0033 worth re-checking:**
- **Billing finalization flow** (the `received → billed` Sample Batch trigger): specific command and authorization at billing-design step.
- **Cross-project Sample Batch reassignment as a structured command**: in `post-mvp.md` alongside notifications.

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

**Step 6b (continued, session 7) — Time Entry off-site intervals ADR (ADR-0034) + EmployeeRole / UserRole ADRs.** See `planning/steps.md` for the full step brief. Project lifecycle stays in session 8.

### Prompt for the next session

> Resume Step 6b. Session 6 landed ADR-0032 (blocker-as-Note pattern with lazy materialization, dismissable/fix-only registry, paired cross-project Notes, any-tracker dismissal authorization, chain-dismissal extension) and ADR-0033 (Sample Batch + Lab Report bespoke document type + Sample Batch as derivation source + `relink_sample_batch_wa_code` command + smart-inference for misfiled batches). ADR-0027's `acknowledged: bool` field aspect is superseded; state machine and dismiss cascade survive.
>
> **Immediate pickup — ADR-0034 Time Entry off-site intervals.** The proposal is fully staged in session 6's chat history with my recommendation on every fork. User did not say `approved` before wrap, so the gate stands. Three coupled forks:
> 1. **Interval representation:** Position A (recommended) — `on_site_range: (start_time, end_time)` + `off_site_sub_intervals: [(start_time, end_time, reason)]`, with sub-intervals required to be entirely within the on-site range and disjoint. Net on-site time = on-site range minus sub-intervals; this drives billing and cross-validation. Alternative B was a flat list of disjoint on-site intervals (architecturally equivalent, operationally awkward). C (status quo scalar `hours`) drops the invariant.
> 2. **Off-site reason shape:** Position A (recommended) — free-text `reason: str`. Enum can be added post-MVP if billing rules need to differentiate (e.g., "travel between sites" billable on a different code).
> 3. **Cross-project overlap predicate (ADR-0028 amendment):** Position A (recommended) — predicate uses net on-site time, not gross. Off-site sub-intervals legitimately reduce conflict surface; B (gross range) would produce false-positive fix-only blockers.
>
> Re-pose the forks or accept recommendations, then write ADR-0034. The ADR should also pin blocker #9's predicate as "batch's collection time does not fall within any Time Entry's net on-site interval for that employee on that date" (currently captured in the registry as user-facing language; ADR-0034 makes it structural).
>
> **Then EmployeeRole / UserRole.** Both are temporal grant/revoke entities — small, similar shape. The user has not yet deliberated either's state machine in depth. The framing question: temporal validity is expressed as `(start_date, end_date?)` with `end_date` nullable for current assignments; what state machine (if any) sits alongside? Candidate: no state machine — temporal validity is the only "state," computed via date comparison. Alternative: explicit `active | revoked` flag captured at revoke time. Pose as a fork; the no-state-machine option is the recommendation pending discussion.
>
> **State machines locked through session 6:** WA Code (6 states, ADR-0027 — `acknowledged` field aspect superseded by ADR-0032), Deliverable (4 states, ADR-0029), WA (3 states, ADR-0030), RFA (5 states, ADR-0031), Sample Batch (2 states, ADR-0033), Lab Report document_type (3 states bespoke, ADR-0033).
>
> **Pattern menu through session 6:** 12 design patterns cumulative; blocker-as-Note (#11) and chain-dismissal (#12) added in session 6.
>
> **Stack confirmed (no ADR yet, Step 8 will write):** backend Python/FastAPI/Ruff/SQLAlchemy/Pydantic/pytest; frontend Vite/React/TypeScript/TanStack Router/TanStack Query/openapi-ts/shadcn-ui/Storybook.
>
> **Process notes:**
> - Casual back-and-forth. Self-monitor context.
> - STOP-AND-CONFIRM gate applies — surface options in chat, await `approved`, only then write.
> - Do not write to `domain-model.md` (that's Step 6d).
> - Project lifecycle is session 8, not session 7. Session 7 = ADR-0034 + EmployeeRole/UserRole. Project's closure invariants reference ADR-0032's project closure gate text directly.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md`
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6a complete; Step 6b in progress across multiple sessions)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0033)
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output; all sections written): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
