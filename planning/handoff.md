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

**Conceptualization** — steps are planning-only, no code is written. **Step 9a (`data-model.md`) complete 2026-05-17 (session 24) — no ADRs.** `planning/data-model.md` landed: 21 entity sections in roster order (each with attribute table `Attribute | Kind | Type / notes` + outgoing-references line + state-enum line + history-surface label) + `## Conventions` block (kind vocabulary, type-notes idiom, history-surface labels) + `## History tables` block (common metadata + 3 comprehensive + 6 lifecycle + `command_audit_log` + no-history bucket + reference-snapshotting recap per ADR-0052). Conceptualization-phase work remaining: **Step 9b (consolidation pass + `roadmap.md` + phase-transition ADR)** — last step before phase transition to Implementation. See `planning/phases.md` for the full phase roster and `planning/steps.md` for the current step list.

## Last session summary

**Session 24 — Step 9a `data-model.md`. ✓ COMPLETE (2026-05-17, no ADRs).** Case-3 scoped session; structural plan (Q1–Q6) already settled in session 23, executed cleanly with no surprises.

**Three watch-for items from session 23's Open questions checked against ADRs at session head before writing.** (i) **Note polymorphic `target` + `references` shape** — pinned by ADR-0018 + ADR-0040 (target = `(target_type, target_id)`; target_type extended to "entity OR history record"; Note-internal discriminator is `subtype`; per-subtype fields all spelled out across ADR-0032 / 0040 / 0042). No new Note-internal discriminator needed beyond `subtype` + `target_type`. (ii) **Time Entry `off_site_sub_intervals` storage representation** — semantic shape pinned (ADR-0034: list of disjoint `(start, end)` pairs, pairwise disjoint, entirely within `on_site_range`, positive duration); storage repr open and tagged via the conventions-block idiom ("to be implemented with JSONB-backed list; alternative: side table — implementation phase"). (iii) **Contract `code_flat_fee_schedule` storage representation** — same shape, same tagging (ADR-0043: non-temporal `{code_type, fee}` collection; storage repr open). None required surfacing as a STOP-AND-CONFIRM gate-pause since all three resolved within the agreed conventions idiom.

**`planning/data-model.md` written end-to-end.** Structure (per session-23 Q5): `## File contract` → `## Reading this file` → `## Conventions` (kind vocabulary `intrinsic | lifecycle | derived | reference | composite | identity | audit-metadata`; type-notes idiom; history-surface labels; derivation tag) → `## Per-entity attributes` (21 sub-sections in roster order) → `## History tables` (common metadata per ADR-0052 §S1 + 3 comprehensive + 6 lifecycle + `command_audit_log` + no-history bucket + reference-snapshotting recap) → `## Pointers`. Each entity section: flat attribute table (`Attribute | Kind | Type / notes`) + outgoing-references line + state-enum line + history-surface label.

**Four review-pass fixes applied** after the first end-to-end read: (a) **UserRole** — removed `granted_at` / `granted_by` from the row (ADR-0036 explicitly states "no timestamps"; grant audit lives on User's `command_audit_log` only). (b) **ContractorEngagement** — removed "composite-key component" wording on `wa_id` + `contractor_id` (ADR-0041 explicitly allows multiple rows per `(wa_id, contractor_id)` for re-engagement after CPR close; natural uniqueness is on `(wa_id, contractor_id, started_at)`). (c) **WABundle** — renamed `contract_status` → `issuance_phase` to avoid collision with Contract's `validity`; clarified the two derivations are independent. (d) **EmployeeRole / Time Entry `role_type`** — clarified this is the **operational** role catalog (`TechRole`, `ProjectLead`, ADR-0035), distinct from UserRole's auth-chain catalog (`superadmin/admin/coordinator/auditor`, ADR-0040). The two dimensions are separate.

**Files touched:** `planning/data-model.md` — new file created. `planning/_file-rules.md` — regenerated (data-model.md entry added between domain-model.md and architecture.md; last-regen date updated to 2026-05-17). `planning/steps.md` — Step 9a marked ✓ COMPLETE inline. `planning/handoff.md` — Current phase line, Last session summary, Open questions, Next session pointer + prompt, Pointers. No `decisions.md` changes (Q6 held — no design gap surfaced during attribute drafting that required a new ADR).

---

*(Prior session retained for context — Session 23 / Step 9 partitioning + Step 9a session plan.)*

**Session 23 — Step 9 partitioning + Step 9a session plan. ✓ COMPLETE (2026-05-16, no ADRs).** Case-2 sizing session. Ran the `_workflow.md` Case 2 fit checklist on Step 9 — **five signals fired** (1: >1 deliberable decisions — data-model + roadmap + consolidation + phase-transition; 2: >1 new artifact — `data-model.md` + `roadmap.md` + phase-transition ADR; 3: >60 min; 4: input reading exceeds ~3 substantial files — framework + logic + history-patterns + domain-model + mvp + architecture + decisions.md/52 ADRs; 5: cross-concern reach — data modeling vs. roadmap planning vs. archival/governance). Three partition options canvassed; **Option A (single-concern seam — 9a `data-model.md` / 9b consolidation + `roadmap.md` + phase-transition ADR) accepted with mitigation** (re-run the fit checklist at 9b's session head if the consolidation candidate scan turns up more than ~2 qualifying ADRs; partition further to a 9c if needed). Option B (three-way split) rejected — `roadmap.md` and consolidation don't compete for the same context budget. Option C (data-model + consolidation paired) rejected — separates the consolidation pass from the phase-transition ADR it directly enables, against the original "consolidation before phase-transition" sequencing.

**Consolidation-candidate preview (informs 9b sizing).** Quick scan of `decisions.md` Status lines: **ADR-0032** (extended by 0042, 0046, 0049 + registry amended by 0044 — 4 amendments; firm consolidation target). Borderline (verify at 9b's session head): **ADR-0027** (likely 2–3 amendments — `acknowledged` aspect superseded by 0032, further touched by 0045 / retired by 0049), **ADR-0037** (likely 1–2 — amended by 0043; verify 0044's reach). Single-amendment cases (no trigger): ADR-0017, ADR-0030, ADR-0035, ADR-0040. Net: probably 1 firm + 1–2 borderline → 9b stays under the partition-further threshold.

**Step 9a session plan canvassed; six structural choices (Q1–Q6) settled with recommendations accepted:** (Q1) per-entity outgoing-references line inline — cross-entity table stays in `domain-model.md`; (Q2) `state` enum noted per entity, transitions referenced; (Q3) flat per-entity table with `Attribute | Kind | Type / notes` columns; (Q4) Document is one entity row with `document_type` as an attribute; (Q5) ordering — `## File contract` → `## Reading this file` → `## Conventions` → `## Per-entity attributes` (21 sub-sections) → `## History tables` → `## Pointers`; (Q6) no new ADRs expected — if a substantive design gap surfaces during attribute drafting, surface at the gate and defer (likely to implementation phase). 9a executed in session 24.

---

## Open questions

**Carried into 9b — verify at 9b's session head before sizing:**

- **Consolidation candidate count.** Session-23 preview: 1 firm (**ADR-0032** — extended by 0042 + 0046 + 0049, registry amended by 0044 = 4 amendments) + 1–2 borderline (**ADR-0027** likely 2–3 amendments — `acknowledged` aspect superseded by 0032, further touched by 0045, retired by 0049; **ADR-0037** likely 1–2 — amended by 0043; verify 0044's reach). **Mitigation (carried from session-23 partition deliberation):** if the scan at 9b's session head turns up more than ~2 qualifying ADRs (>2 amendments each), re-run the Case 2 fit checklist on 9b and partition further — defer `roadmap.md` or the phase-transition ADR to a 9c.

- **Roadmap milestone shape.** Implementation-phase step list at coarse granularity, drawn from `mvp.md`'s 6 must-have features + the 7 command-shape carry-forwards (per `domain-model.md` § Deferred — `split_entry`, `revoke_write_off`, revoke-line-item, `reassign_wa_project` deeper mechanics, ContractorEngagement command-shape, ADR-0031 auto-draft regeneration suppression, smart-command-inference state) + the implementation-phase carry-forwards from ADR-0051 + ADR-0052 (PaaS vendor pick + managed-Postgres offering name; `Command` base class + dispatcher concrete design; per-invariant isolation-primitive assignment — `SERIALIZABLE` vs. `pg_try_advisory_xact_lock` per invariant; audit-log write timing in-txn vs. post-commit; `backend/` + `frontend/` stale-scaffolding cleanup per ADR-0001 + ADR-0051).

- **Phase-transition ADR shape.** "Conceptualization phase complete; implementation begins" — triggers the four `phases.md` writes per `_workflow.md`'s phase-roster protocol (mark Conceptualization complete; mark Implementation current; archive `steps.md` to `steps.archive/conceptualization.md`; create new `steps.md` drawing from `roadmap.md`). Lightweight gate.

**Process notes (apply to 9b):**
- STOP-AND-CONFIRM gate applies to each of the three 9b sub-activities: (i) consolidation pass — surface each candidate ADR's amendment scan + proposed consolidated text before writing; (ii) `roadmap.md` — surface the milestone list + sizing + ordering before writing; (iii) phase-transition ADR — surface text + the four `phases.md` writes block before executing.
- `roadmap.md` needs a `## File contract` block. Trigger `_file-rules.md` regeneration in the completion protocol since a new planning file is being added (alongside any phase-transition-driven `phases.md` regeneration).
- Consolidated ADRs start at **ADR-0053**; predecessor ADRs marked `superseded by #N` (do not edit predecessor body — supersession is a status flip only).
- Recommendation strength: state confidence; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).

**No 9a-execution open questions remain.** All three watch-for items from session 23 were resolved in session 24 (Note polymorphism pinned; off-site sub-intervals + `code_flat_fee_schedule` tagged via the conventions idiom — neither required an ADR).

## Next session

**Step 9b — Consolidation pass + `roadmap.md` + phase-transition ADR.** Last step of the Conceptualization phase. Three sub-activities: (i) pre-transition ADR consolidation pass (scan `decisions.md` for ADRs with 2+ amendments; firm candidate ADR-0032, borderline ADR-0027 / ADR-0037 — verify at session head); (ii) draft `planning/roadmap.md` with rough-sized implementation milestones; (iii) write the phase-transition ADR ("Conceptualization complete; implementation begins") + execute the four `phases.md` writes per `_workflow.md`'s phase-roster protocol. Brief in `steps.md` → § Step 9b. Execution order: Step 7 ✓ → Step 8a ✓ → Step 8b ✓ → Step 9a ✓ → **Step 9b** → (phase transition → Implementation).

**Partition mitigation (carry from session 23):** if the consolidation candidate scan at session head turns up more than ~2 qualifying ADRs, re-run the Case 2 fit checklist on 9b and partition further — defer `roadmap.md` or the phase-transition ADR to a 9c. Cheap; do not skip the check.

### Prompt for the next session

> Resume work. Next is **Step 9b — consolidation pass + `roadmap.md` + phase-transition ADR**. Brief in `steps.md` → § Step 9b. Step 9 was partitioned 2026-05-16 (Option A, single-concern seam); 9a (`data-model.md`) completed 2026-05-17. This is Case-3 scoped, but **start with a re-sizing check** before committing to single-session execution (see partition mitigation).
>
> **Read first:** this prompt + the Open questions block above + `_workflow.md` § phase-roster protocol + `mvp.md` (drives roadmap) + `data-model.md` (9a output, conceptual entity surface) + `architecture.md` + ADR-0051 + ADR-0052 (stack + data layer pin) + the consolidation-candidate source ADRs (esp. **ADR-0032** + its amenders 0042 / 0046 / 0049 / 0044; borderline **ADR-0027** + 0032 / 0045 / 0049; borderline **ADR-0037** + 0043 / 0044). `domain-model.md` § Deferred and § Post-MVP for roadmap-input carry-forwards.
>
> **Session-head sizing check (before drafting anything):**
> 1. Scan `decisions.md` for ADRs with 2+ amendments. Confirm the candidate count.
> 2. If >2 qualifying ADRs → run the `_workflow.md` Case 2 fit checklist on 9b; partition further (likely 9c carries `roadmap.md` or the phase-transition ADR).
> 3. If ≤2 → proceed as a single Case-3 session.
> 4. Surface the count + decision in chat before any writing.
>
> **Items in scope (per `steps.md` → Step 9b), sequenced:**
> 1. **Pre-transition ADR consolidation pass (one-time).** For each qualifying ADR (2+ amendments): draft a fresh, definitive ADR (starting at **ADR-0053**); mark predecessors `superseded by #N`. Sequenced before the phase-transition ADR per the original Step 9 framing. Per the session-9 framing in `steps.md` line 612: mid-phase compaction loses load-bearing deliberation context, but phase boundary is the right moment — the resulting record becomes foundation for implementation-phase work.
> 2. **`planning/roadmap.md`.** Ordered implementation milestones with rough sizing. Drawn from: `mvp.md`'s 6 must-have features; the 7 command-shape carry-forwards in `domain-model.md` § Deferred; the implementation-phase carry-forwards from ADR-0051 + ADR-0052 (PaaS vendor pick + managed-Postgres offering name; `Command` base class + dispatcher concrete design; per-invariant isolation-primitive assignment; audit-log write timing; `backend/` + `frontend/` stale-scaffolding cleanup). New file with `## File contract` block.
> 3. **Phase-transition ADR.** "Conceptualization phase complete; implementation begins." Triggers the four `phases.md` writes per `_workflow.md`'s phase-roster protocol — lightweight gate: announce the four writes in chat ("phase Conceptualization complete, archiving steps and creating new steps.md — ok?"); wait for yes before writing. The four writes: (a) mark Conceptualization complete in `phases.md`; (b) mark Implementation current; (c) archive current `steps.md` → `planning/steps.archive/conceptualization.md`; (d) create new `planning/steps.md` for Implementation phase (drawing from `roadmap.md`).
>
> **Out of scope — implementation phase:**
> - DDL (implementation phase first step).
> - Concrete `Command` base class + dispatcher design.
> - PaaS vendor pick + managed-Postgres offering name.
> - Per-invariant isolation-primitive assignment + audit-log write timing.
> - Stale-scaffolding cleanup of `backend/` + `frontend/`.
>
> **ADR numbering.** Next ADR at write time: **ADR-0053**. Consolidated ADRs use sequential numbers from there; phase-transition ADR follows.
>
> **Reference:** Conceptualization phase carries ADR-0001 through ADR-0052. 21 entities, 14 design patterns, 10-entry blocker registry. Data layer pinned (PostgreSQL 15+ via SQLAlchemy 2.0 + Alembic, 9 per-entity history tables + `command_audit_log`). Conceptual data model rolled up in `data-model.md` (21 entity sections, per-entity attribute rosters, history-surface assignments).
>
> **Process notes:**
> - STOP-AND-CONFIRM gate applies to each of the three sub-activities: surface each consolidated-ADR proposal, the roadmap milestone list, and the phase-transition ADR text in chat before writing.
> - `roadmap.md` needs a `## File contract` block. Trigger `_file-rules.md` regeneration in the completion protocol.
> - The four `phases.md` writes follow `_workflow.md`'s lightweight-gate protocol (announce + wait for yes; not full deliberation).
> - Predecessor ADRs marked `superseded by #N` — status flip only, do not edit predecessor body.
> - Recommendation strength: state confidence; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-17)
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6 ✓ COMPLETE — 6a / 6b core / 6b-residual / 6b-residual-2 / 6c-i / 6c-ii / 6c-iii-a / 6c-iii-b-i / 6c-iii-b-ii / 6c-iv-a / 6c-iv-b / 6d all complete; **Step 7 ✓ COMPLETE**; **Step 8 partitioned 2026-05-15 — 8a ✓ COMPLETE (ADR-0051), 8b ✓ COMPLETE (ADR-0052 + `architecture.md`)**; **Step 9 partitioned 2026-05-16 — 9a ✓ COMPLETE 2026-05-17 (`data-model.md`), 9b (consolidation pass + `roadmap.md` + phase-transition ADR)**; next: **Step 9b**)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0052; next ADR at write time: ADR-0053)
- **MVP scope (Step 7 output):** `planning/mvp.md` — 6 must-have features + categorized "not now" list + 1 carve-out + 7 command-shape carry-forwards + pointers. Canonical MVP-scope reference.
- **Domain model (Step 6d output):** `planning/domain-model.md` — rolled-up domain projection: 21 entities, relationship table, per-entity lifecycles, authorization predicates (via ADR-0047), history patterns, delete policy, 14 design patterns, 10-entry blocker registry, vocabulary, deferred / open questions
- **Data model (Step 9a output):** `planning/data-model.md` — conceptual data model: 21 entity sections (attribute table per entity with `Attribute | Kind | Type / notes`, outgoing-references line, state-enum line, history-surface label) + conventions block + history-table shapes per ADR-0052 (3 comprehensive + 6 lifecycle + `command_audit_log`). Conceptual only — not DDL.
- **Architecture (Step 8b output):** `planning/architecture.md` — one-page sketch: component diagram (Browser → CDN/SPA → API container → managed Postgres on managed PaaS), boundary semantics per layer, successful-command 10-step data flow, out-of-band concerns (file storage / background jobs / notifications / auth) flagged for implementation phase, pointers.
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md` (superseded by `mvp.md` § Not now; retained for trace continuity)
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
