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

**Conceptualization** — steps are planning-only, no code is written. **Step 7 (MVP feature cut) complete — `planning/mvp.md` written + ADR-0050 landed.** Conceptualization-phase work remaining: **Step 8 (stack & architecture) → Step 9 (data-model sketch + roadmap + phase-transition ADR)**. See `planning/phases.md` for the full phase roster and `planning/steps.md` for the current step list.

## Last session summary

**Session 19 — Step 7 ADR write. ✓ COMPLETE (2026-05-15, ADR-0050).** Case-3 scoped — the MVP cut. Three load-bearing forks + three carve-outs surfaced at the STOP-AND-CONFIRM gate and were resolved sequentially in chat before the write (all on the agent's recommendation):

- **D1 (proof-of-concept purpose):** Settled **(b) + (c)** — "hard parts" demonstrator + usable internal tool. MVP audience is the user's own office, to be usable for new projects at introduction. End-to-end paths must exist for every must-have. The dominant scope-decision test is **"is this tracked at the office today?"**
- **D2 (RFA + amendment cycle in MVP):** Settled **(a)** — full cycle in. RFA entity + hybrid `add`/`remove` line items + third WA origin (SCA-direct via generalized `issue_wa`). Both RFA-driven and SCA-direct amendments are common real cases at the office.
- **D3 (closure gate + blockers + default-resolution in MVP):** Settled **(a)** — full stack in. 10-entry registry + lazy materialization + `default_resolve` + named compounds + `revoke_write_off` + chain-dismissal `te_batches_by_coverage`. Carve-out flagged: `resolve_overlap_paired` may slip post-MVP if `split_entry`'s mechanics don't land in early implementation.
- **C1 (multi-contract in MVP):** Kept — Contract entity + per-`(employee, role_type, contract)` rate resolution + `code_flat_fee_schedule`. ADR-0043's driver remains immediately relevant.
- **C2 (all four roles in MVP):** Kept — `superadmin` / `admin` / `coordinator` / `auditor`. Admin required for `edit_wabundle` + roster CRUD; auditor read-only and cheap.
- **C3 (DepFiling in MVP):** Kept — TRU + editable `required_doc_types` + 7 ACP/VAR doc types. Parallel evidence track to Deliverables; office files these with regulators today.

**`planning/mvp.md` written** (~140 lines). Structure: § File contract / § Must-have features (6 numbered features, under the ≤7 ceiling — Notes commentary folded into #5 as substrate) / § Not now (post-MVP feature candidates from `post-mvp.md` + authorization/role-surface deferrals + billing-adjacent deferrals + model/config-evolution deferrals + dissolved-for-record) / § Carve-outs (single item: `resolve_overlap_paired`) / § Command-shape carry-forwards (7 items: `split_entry`, `revoke_write_off`, revoke-line-item, `reassign_wa_project` deeper mechanics, ContractorEngagement signatures, ADR-0031 auto-draft regeneration suppression, smart-command-inference landing state) / § Pointers.

**The 6 must-have features:** (1) Project lifecycle; (2) WA + WA Codes + RFA cycle; (3) Time Entries + Sample Batches; (4) Documents + Deliverables + DepFilings; (5) Closure gate + blockers + write-off (incl. polymorphic Notes substrate); (6) Roster + role administration.

**`post-mvp.md` superseded as the active holding pen.** All entries folded verbatim into `mvp.md` § Not now. New post-MVP candidates that surface in implementation-phase work should append to `mvp.md` § Not now rather than re-opening `post-mvp.md`. `post-mvp.md` retained for trace continuity.

**No new entities, no new design patterns, no new amendments to other ADRs.** Step 7 is a scope decision; the model is unchanged from the close of ADR-0049. Entity roster stays at 21; design pattern catalog stays at 14; blocker registry stays at 10.

**`_file-rules.md` regenerated** (2026-05-15): added `mvp.md` entry.

---

*(Prior session retained for context — Session 18 / Step 6d / `domain-model.md`.)*

**Session 18 — Step 6d. ✓ (2026-05-15).** Case-3 scoped — write step, deliberation already done over 49 ADRs. Three light shape decisions surfaced at the STOP-AND-CONFIRM gate (section structure / quarantine open question deferred / command-shape carry-forwards listed but not pulled in). `planning/domain-model.md` written (~494 lines): 21-entity roster + relationship table + per-entity lifecycles + authorization (class rules + non-uniform rows, anchored to ADR-0047) + history-pattern + delete-policy tables + 14 design patterns + 10-entry blocker registry + stabilized vocabulary + deferred block + pointers. No new ADRs. Cumulative-tables migration: the handoff sheds the entity roster, relationship table, history-pattern assignments, delete policy, design-pattern catalog, blocker registry, role catalog, and vocabulary post-Step-6d and points at `domain-model.md`. **Step 6 ✓ COMPLETE.**

---

## Open questions

**No carry-forward open questions land on Step 8.** Step 7's "not now" list (in `mvp.md`) covers all deferred surface; the seven command-shape carry-forwards (in `mvp.md` § Command-shape carry-forwards) are *in MVP* and their mechanics land in the implementation phase — not Step 8's concern.

**For the next session — Step 8 (stack & architecture):**

Step 8 picks the stack and the architectural shape. Per `steps.md` → Step 8: decide only what the next step needs. **History implementation shape (event store vs. append-only tables vs. temporal tables) is resolved here**, informed by Step 5's pattern menu and the per-entity history-pattern assignments in `domain-model.md` (3 entities Comprehensive / 6 Lifecycle / 7 Audit log / 5 No history).

**Items in scope (per `steps.md` → Step 8):**

1. **ADR entries** for: language/runtime, framework, persistence, deployment shape, **history implementation shape** (single ADR or split per concern — decide at session head).
2. **Write `planning/architecture.md`** — one-page sketch (component boxes, data flow).

**Inputs (per the step brief):** `mvp.md` (the cut), `framework.md`, `logic.md`, `history-patterns.md`, `decisions.md` (ADR-0001 through ADR-0050), `handoff.md` (this file). The existing `backend/` and `frontend/` directories per ADR-0001 are treated as stale — stack choices are unconstrained.

**Sizing check.** Step brief estimates 45–60 min. The decision cluster carries 5 sub-decisions (language/runtime, framework, persistence, deployment, history impl shape) — Signal 1 (independently-deliberable decisions) may fire. **Run the Case 2 fit checklist at session head.** Potential partition seam: stack/runtime/framework (one session) vs. persistence + history-impl shape + deployment (one session). The history-impl-shape decision is load-bearing and may anchor whichever session it lands in.

**Process notes:**
- STOP-AND-CONFIRM gate applies. Each sub-decision surfaces its options + tradeoffs in chat before any ADR write.
- "Decide only what the next step needs" — Step 8's brief explicitly cautions against over-deciding. Step 9 picks up the conceptual data model + roadmap; Step 8 should leave room for implementation-phase choices that don't yet have load-bearing context.
- The history-impl-shape decision must be reconciled with `framework.md`'s deferred list and the per-entity history pattern assignments in `domain-model.md`. The four patterns in use (Comprehensive / Lifecycle / Audit log / No history) constrain which implementation shapes are honest.
- Recommendation strength: state confidence; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).

## Next session

**Step 8 — Stack & architecture.** Case-2 candidate (5 sub-decisions may trip the fit checklist; assess at session head). Goal: pick the stack + architectural shape + history implementation shape; write the supporting ADRs + the `architecture.md` one-page sketch. Brief in `steps.md` → Step 8. Execution order: Step 7 ✓ → **Step 8** → Step 9 (data model sketch + roadmap + phase-transition ADR + pre-transition ADR consolidation pass). ADR numbers at write time: starting at **ADR-0051** (split across multiple ADRs likely).

### Prompt for the next session

> Resume work. Next is **Step 8 — Stack & architecture**. Brief in `steps.md` → § Step 8. Per `_workflow.md` Case 2: read the brief; run the fit checklist; if signals 1 / 5 fire (5 sub-decisions span stack + persistence + history-impl + deployment concerns), partition before writing. If the step fits, fall through to Case 3.
>
> **Read first:** this prompt + the Open questions block above + `mvp.md` (the cut — defines what the stack must support) + `framework.md` (substrate; deferred list includes history implementation shape) + `logic.md` (command pipeline; cross-entity invariant enforcement at command boundary) + `history-patterns.md` (the pattern menu — 4 patterns: Comprehensive, Lifecycle, Audit log, No history) + `domain-model.md` § History patterns per entity (3 / 6 / 7 / 5 distribution across patterns) + `decisions.md` for ADR pointers (esp. ADR-0001 stale-scaffolding stance).
>
> **Items in scope (per `steps.md` → Step 8):**
> 1. ADR entries for: language/runtime, framework, persistence, deployment shape, **history implementation shape**. Single ADR per concern or bundled — decide at session head; if bundled, name the bundle.
> 2. Write `planning/architecture.md` — one-page sketch (component boxes, data flow). New file; add a `## File contract` block.
>
> **Out of scope — do not pull in:**
> - Conceptual data model + DDL (Step 9).
> - Roadmap (Step 9).
> - Phase-transition ADR (Step 9).
> - Pre-transition ADR consolidation pass (Step 9 — scan `decisions.md` for ADRs with 2+ amendments and consolidate before the phase ends).
> - MVP feature cut (Step 7 — settled in ADR-0050 / `mvp.md`).
> - Command-shape carry-forwards (implementation phase per `mvp.md` § Command-shape carry-forwards).
>
> **Sequencing:** Step 7 ✓ → **Step 8 (this session)** → Step 9 → (phase transition).
>
> **Reference:** 21 entities (post-ADR-0048), 14 design patterns, roles `superadmin`/`admin`/`coordinator`/`auditor`, 10-entry blocker registry, Conceptualization phase carries ADR-0001 through ADR-0050. The MVP cut is 6 must-have features (Project lifecycle / WA+WA Code+RFA cycle / TE+SB / Documents+Deliverables+DepFilings / Closure gate+blockers+write-off / Roster+role admin). Full detail in `domain-model.md` + `mvp.md`.
>
> **History-impl-shape framing notes:**
> - 4 patterns in use across 21 entities: Comprehensive (3 — Document / WA / RFA), Lifecycle (6 — Project / Sample Batch / Deliverable / EmployeeRole / WA Code / ContractorEngagement), Audit log (7 — Employee / User / Time Entry / Contractor / DepFiling / Contract / WABundle), No history (5 — School / Note / UserRole / WACodeAssignment / WABundleSite).
> - Whichever implementation shape lands must honestly support all four patterns. Event store vs. append-only tables vs. temporal tables vs. hybrid are honest options; choose informed by the per-pattern reconstructability requirements in `history-patterns.md`.
> - ADR-0003 was superseded by ADR-0006 (per-entity history decision); ADR-0008 (mandatory capture at command boundary) is load-bearing on whichever implementation shape lands.
>
> **Process notes:**
> - STOP-AND-CONFIRM gate applies — sub-decisions surface in chat with options + tradeoffs before ADR writes.
> - "Decide only what the next step needs" — Step 8's brief explicitly cautions against over-deciding. Leave room for implementation-phase choices that don't yet have load-bearing context.
> - Recommendation strength: state confidence; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-15)
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6 ✓ COMPLETE — 6a / 6b core / 6b-residual / 6b-residual-2 / 6c-i / 6c-ii / 6c-iii-a / 6c-iii-b-i / 6c-iii-b-ii / 6c-iv-a / 6c-iv-b / 6d all complete; **Step 7 ✓ COMPLETE**; next: Step 8 — stack & architecture)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0050; next ADR at write time: ADR-0051)
- **MVP scope (Step 7 output):** `planning/mvp.md` — 6 must-have features + categorized "not now" list + 1 carve-out + 7 command-shape carry-forwards + pointers. Canonical MVP-scope reference.
- **Domain model (Step 6d output):** `planning/domain-model.md` — rolled-up domain projection: 21 entities, relationship table, per-entity lifecycles, authorization predicates (via ADR-0047), history patterns, delete policy, 14 design patterns, 10-entry blocker registry, vocabulary, deferred / open questions
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md` (superseded by `mvp.md` § Not now; retained for trace continuity)
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
