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

**Conceptualization** — steps are planning-only, no code is written. **Step 7 (MVP feature cut) complete — `planning/mvp.md` written + ADR-0050 landed.** **Step 8 partitioned 2026-05-15 (session 20) along the coupling-respecting seam (Option B) — 8a (stack: language/runtime + framework + deployment) → 8b (persistence + history-impl shape + `architecture.md`).** Conceptualization-phase work remaining: **Step 8a → Step 8b → Step 9 (data-model sketch + roadmap + phase-transition ADR)**. See `planning/phases.md` for the full phase roster and `planning/steps.md` for the current step list.

## Last session summary

**Session 20 — Step 8 sizing + partition. ✓ COMPLETE (2026-05-15).** Case-2 sizing session — ran the fit checklist on Step 8 at session head. **Four signals fired (1, 3, 4, 5):**
- Signal 1 — 5 sub-decisions cluster into ~3 coupling-groups: (lang/runtime + framework), (persistence + history-impl shape), (deployment).
- Signal 3 — >60 min with 5 sub-decisions + new file.
- Signal 4 — input reading >3 substantial planning files (`mvp.md`, `framework.md`, `logic.md`, `history-patterns.md`, `domain-model.md` § history-patterns).
- Signal 5 — cross-concern reach (runtime/serving vs. storage/history-impl).

**Step 8 partitioned along the coupling-respecting seam (Option B):**
- **Step 8a — Stack (language/runtime + framework + deployment).** Runtime-stack triple. Deployment rides with runtime; lang choice rules in/out most deployment options.
- **Step 8b — Persistence + history-impl shape + `architecture.md`.** Load-bearing data-layer pair + the one-page sketch (lands here after all 5 decisions are settled, avoiding drafting twice).

**Options considered:** Option A (handoff's original suggested seam — stack vs. data+deployment) — rejected; deployment couples more naturally with runtime than with persistence. Option C (3-way split — lang/framework | persistence/history-impl | deployment + architecture) — rejected; deployment alone doesn't carry a session.

**Files touched:** `planning/steps.md` — Step 8 expanded with the partition note + Step 8a + Step 8b sub-session briefs (mirroring the Step 6c-iii-b / Step 6c-iv pattern). `planning/handoff.md` — Current phase line, Last session summary, Open questions, Next session pointer + prompt, Pointers step-list line. No ADRs written; no other planning files touched. `_file-rules.md` not regenerated (no file contracts changed).

---

*(Prior session retained for context — Session 19 / Step 7 / `mvp.md` / ADR-0050.)*

**Session 19 — Step 7 ADR write. ✓ COMPLETE (2026-05-15, ADR-0050).** Case-3 scoped — the MVP cut. Three load-bearing forks (D1: hard-parts + usable-internal-tool; D2: full RFA cycle + third WA origin in; D3: full closure-gate + write-off + default-resolution in) plus three carve-outs (C1: multi-contract kept; C2: all four roles kept; C3: DepFiling kept) settled at the STOP-AND-CONFIRM gate before the write. `planning/mvp.md` written (~140 lines): 6 must-have features (Project lifecycle / WA+WA Code+RFA cycle / TE+SB / Documents+Deliverables+DepFilings / Closure gate+blockers+write-off / Roster+role admin) — under the ≤7 ceiling; categorized "not now" list folding in `post-mvp.md` verbatim + authorization/role-surface + billing-adjacent + model/config-evolution deferrals; one carve-out (`resolve_overlap_paired` slip-eligible behind `split_entry`); 7 command-shape carry-forwards (in MVP, mechanics pinned implementation-phase). `post-mvp.md` superseded as the active holding pen. No new entities, no new design patterns, no amendments to other ADRs. `_file-rules.md` regenerated (added `mvp.md` entry).

---

## Open questions

**No carry-forward open questions land on Step 8a.** Step 7's "not now" list (in `mvp.md`) covers all deferred surface; the seven command-shape carry-forwards (in `mvp.md` § Command-shape carry-forwards) are *in MVP* and their mechanics land in the implementation phase — not Step 8a's concern.

**For the next session — Step 8a (stack: language/runtime + framework + deployment):**

Step 8a picks the runtime stack — the three coupled decisions where the lang choice rules in/out most framework and deployment options. Per `steps.md` → Step 8a: decide only what the next step needs.

**Items in scope (per `steps.md` → Step 8a):**

1. **Language/runtime.** Candidate axes: ecosystem maturity for the use case, team familiarity, type-system shape (informs invariant-enforcement story per `logic.md`), deployment options it opens up.
2. **Framework.** Web/app framework within the lang ecosystem. Must comfortably host the command-pipeline shape (`logic.md`: commands as named operations + mandatory history capture at command boundary per ADR-0008).
3. **Deployment shape.** Monolith vs. service split; container vs. serverless; managed vs. self-hosted. MVP audience is the user's own office (per `mvp.md`) — operational simplicity weights heavy.

**Out of scope — deferred to 8b:** persistence engine, history implementation shape, `architecture.md` (lands in 8b after all 5 decisions are settled, avoiding drafting the sketch twice).

**Inputs (per the step brief):** `mvp.md` (the cut), `framework.md`, `logic.md`, `decisions.md` (esp. ADR-0001 stale-scaffolding stance — existing `backend/` / `frontend/` directories treated as stale, unconstrained), `handoff.md` (this file).

**Local decision at session head:** single ADR per concern, or bundled into one ADR? If bundled, name the bundle. The three decisions are coupled enough that one ADR may read more naturally; the three sub-rationales remain distinct.

**Process notes:**
- STOP-AND-CONFIRM gate applies. Each sub-decision (language/runtime, framework, deployment) surfaces its options + tradeoffs in chat before any ADR write.
- "Decide only what the next step needs" — Step 8's brief explicitly cautions against over-deciding. Step 8b picks up the data layer; Step 9 picks up the conceptual data model + roadmap. 8a should leave room for downstream choices that don't yet have load-bearing context.
- Recommendation strength: state confidence; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).

## Next session

**Step 8a — Stack (language/runtime + framework + deployment).** Case-3 scoped — the partition decision settled session 20; this session is one of the two halves of Step 8. Goal: pick language/runtime + framework + deployment shape; write the supporting ADR(s). Brief in `steps.md` → Step 8a. Execution order: Step 7 ✓ → Step 8 partitioned ✓ → **Step 8a** → Step 8b (persistence + history-impl + `architecture.md`) → Step 9 (data model sketch + roadmap + phase-transition ADR + pre-transition ADR consolidation pass). ADR numbers at write time: starting at **ADR-0051**.

### Prompt for the next session

> Resume work. Next is **Step 8a — Stack (language/runtime + framework + deployment)**. Brief in `steps.md` → § Step 8a. Case-3 scoped — the partition was settled session 20.
>
> **Read first:** this prompt + the Open questions block above + `mvp.md` (the cut — defines what the stack must support) + `framework.md` (substrate) + `logic.md` (command pipeline; framework must host it — commands as named operations, mandatory history capture at command boundary per ADR-0008) + `decisions.md` for ADR pointers (esp. ADR-0001 stale-scaffolding stance — existing `backend/` / `frontend/` directories treated as stale; stack choices unconstrained).
>
> **Items in scope (per `steps.md` → Step 8a):**
> 1. **Language/runtime.** Candidate axes: ecosystem maturity, team familiarity, type-system shape (informs invariant-enforcement story per `logic.md`), deployment options.
> 2. **Framework.** Web/app framework within the lang ecosystem. Must host the command pipeline.
> 3. **Deployment shape.** Monolith vs. service split; container vs. serverless; managed vs. self-hosted. MVP audience is the user's own office — operational simplicity weights heavy.
>
> Single ADR per concern or bundled — decide at session head; if bundled, name the bundle.
>
> **Out of scope — do not pull in (deferred to 8b):**
> - Persistence engine.
> - History implementation shape (event store vs. append-only tables vs. temporal tables vs. hybrid).
> - `planning/architecture.md` (one-page sketch lands in 8b after all 5 stack decisions settle, avoiding double-drafting).
>
> **Out of scope — later steps:**
> - Conceptual data model + DDL (Step 9).
> - Roadmap (Step 9).
> - Phase-transition ADR + pre-transition ADR consolidation pass (Step 9).
> - MVP feature cut (Step 7 — settled in ADR-0050 / `mvp.md`).
> - Command-shape carry-forwards (implementation phase per `mvp.md` § Command-shape carry-forwards).
>
> **Sequencing:** Step 7 ✓ → Step 8 partitioned ✓ → **Step 8a (this session)** → Step 8b → Step 9 → (phase transition).
>
> **Reference:** 21 entities (post-ADR-0048), 14 design patterns, roles `superadmin`/`admin`/`coordinator`/`auditor`, 10-entry blocker registry, Conceptualization phase carries ADR-0001 through ADR-0050. The MVP cut is 6 must-have features (Project lifecycle / WA+WA Code+RFA cycle / TE+SB / Documents+Deliverables+DepFilings / Closure gate+blockers+write-off / Roster+role admin). Full detail in `domain-model.md` + `mvp.md`.
>
> **Process notes:**
> - STOP-AND-CONFIRM gate applies — each sub-decision surfaces in chat with options + tradeoffs before any ADR write.
> - "Decide only what the next step needs" — leave room for 8b and downstream choices that don't yet have load-bearing context.
> - Recommendation strength: state confidence; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-15)
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6 ✓ COMPLETE — 6a / 6b core / 6b-residual / 6b-residual-2 / 6c-i / 6c-ii / 6c-iii-a / 6c-iii-b-i / 6c-iii-b-ii / 6c-iv-a / 6c-iv-b / 6d all complete; **Step 7 ✓ COMPLETE**; **Step 8 partitioned 2026-05-15 — 8a (stack: lang/runtime + framework + deployment) → 8b (persistence + history-impl + `architecture.md`)**; next: **Step 8a**)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0050; next ADR at write time: ADR-0051)
- **MVP scope (Step 7 output):** `planning/mvp.md` — 6 must-have features + categorized "not now" list + 1 carve-out + 7 command-shape carry-forwards + pointers. Canonical MVP-scope reference.
- **Domain model (Step 6d output):** `planning/domain-model.md` — rolled-up domain projection: 21 entities, relationship table, per-entity lifecycles, authorization predicates (via ADR-0047), history patterns, delete policy, 14 design patterns, 10-entry blocker registry, vocabulary, deferred / open questions
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md` (superseded by `mvp.md` § Not now; retained for trace continuity)
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
