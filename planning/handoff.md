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

**Conceptualization** — steps are planning-only, no code is written. **Step 6d (domain model assembly) complete — the rolled-up domain projection now lives at `planning/domain-model.md`.** Conceptualization-phase work remaining: **Step 7 (MVP feature cut) → Step 8 (stack & architecture) → Step 9 (data-model sketch + roadmap + phase-transition ADR)**. See `planning/phases.md` for the full phase roster and `planning/steps.md` for the current step list.

## Last session summary

**Session 18 — Step 6d ADR write. ✓ COMPLETE (2026-05-15).** Case-3 scoped — write step, deliberation already done over 49 ADRs. Three light shape decisions surfaced at the STOP-AND-CONFIRM gate and were resolved in chat before the write (all three on the agent's recommendation):

- **D1 (section structure):** Hybrid — entity roster table up top + per-entity expansion paragraphs for the intricate ones + cross-cutting sections for relationships, lifecycles, authorization, history patterns, delete policy, design patterns, blocker registry, vocabulary, deferreds, pointers.
- **D2 (quarantine open question):** Confirm-and-codify deferred. No new ADR. The pattern remains available-but-uncommissioned per ADR-0011 + ADR-0013 + `history-patterns.md`; recorded in `domain-model.md` § Deferred / open questions.
- **D3 (command-shape carry-forwards):** Don't pull in — `split_entry`, `revoke_write_off`, revoke-line-item, `reassign_wa_project` deeper mechanics, `ContractorEngagement` signatures, smart-command-inference state, ADR-0031 auto-draft regeneration suppression all remain implementation-phase or residual; listed in `domain-model.md` § Deferred / open questions for traceability.

**`planning/domain-model.md` written** (~310 lines). Standalone reference for a framework-aware reader; covers the 21-entity roster + relationship table + per-entity lifecycles + authorization (class rules + non-uniform rows, anchored to ADR-0047) + history-pattern + delete-policy tables + 14 design patterns + 10-entry blocker registry + stabilized vocabulary + deferred block + pointers. **No new ADRs** — no domain-shape decision surfaced during the write.

**Step 6 ✓ COMPLETE** (6a → 6b core → 6b-residual → 6c-i → 6c-ii → 6c-iii-a → 6c-iii-b-i → 6c-iii-b-ii → 6c-iv-a → 6c-iv-b → 14a → 14b → 6c-iii-b complete → **6d complete**).

**Cumulative-tables migration.** The entity roster, relationship table, history-pattern assignments, delete policy, design-pattern catalog, blocker registry, role catalog, and vocabulary previously rolled up in this handoff's retained-session blocks **are now the stable surface in `domain-model.md`**. The handoff sheds them post-Step-6d and points at the rolled-up document. Future sessions read `domain-model.md` for those tables; the handoff continues to carry transient between-session state (last session summary, open questions, next pointer, prompt).

**`_file-rules.md` regenerated** (2026-05-15): added `domain-model.md` entry.

---

*(Prior session retained for context — Session 17 / Step 6c-iii-b-ii / ADR-0049.)*

**Session 17 — Step 6c-iii-b-ii ADR write. ✓ (2026-05-15, ADR-0049).** WA Code removal model — six coupled decisions: `dismiss_wa_code` narrowed to `{expected, pending_rfa}` targets only; new `removed` terminal (`issued → removed` via `approve_rfa` remove-target or `issue_wa` SCA-direct dropped-code); RFA hybrid line items typed `add | remove | budget` with coordinator-authored `add_rfa_line_item(bundle, code, type)`; generalized `issue_wa` (initial + SCA-direct branches, hard-gated against `in_review` RFAs); shared removal cascade under cascade-keep-FK across the three triggers (lifecycle record + immutable `write_off` Note on referencing TE / SB, FK kept not nulled); blocker registry trim (#1 / #2 formally removed as unfireable). Five sub-decisions D1–D5 surfaced + resolved at the STOP-AND-CONFIRM gate. Full detail in ADR-0049 (`decisions.md`); rolled-up vocabulary in `domain-model.md` § Vocabulary.

---

## Open questions

**No carry-forward open questions land on Step 7.** Step 6d resolved the quarantine open question (deferred per ADR-0011 / ADR-0013 / `history-patterns.md`, codified in `domain-model.md` § Deferred). All other carry-forwards from Step 6c-iii-b-ii / 6c-iii-b-i / 6c-ii / 6b-residual-2 / 6c-iv-a/b / 6c-iii-a are tracked in `domain-model.md` § Deferred / open questions (command-shape carry-forwards: implementation-phase or residual; not Step 7's concern).

**For the next session — Step 7 (MVP feature cut):**

Step 7 picks what the proof-of-concept must demonstrate. Per `steps.md` → Step 7: ≤7 must-have features, each one sentence; defensible "not now" list. ADR entry records the MVP scope decision (next ADR number: **ADR-0050**).

**Items in scope (per `steps.md` → Step 7):**

1. **Write `planning/mvp.md`** — in-scope vs. explicitly-out-of-scope features. ≤7 must-haves.
2. **Append an ADR** (ADR-0050) recording the MVP scope decision (rationale, alternatives, what's deferred).

**Inputs (per the step brief):** `domain-model.md` (the rolled-up domain), `decisions.md` (ADR-0001 through ADR-0049), `handoff.md` (this file), `post-mvp.md` (the holding pen — feature candidates already deferred).

**Sizing check.** Step brief estimates 30–45 min. Single coherent decision cluster (cut features into MVP vs. not-now), but the cut surface spans the full domain — every entity contributes potential features. **Expected to fit one window;** run the Case 2 fit checklist at session head — if signal 1 fires (the cut has more than one independently-deliberable sub-decision — e.g., command-surface cuts decoupled from data-shape cuts), partition before writing.

**Process notes:**
- STOP-AND-CONFIRM gate applies. The cut is the deliberation — surface candidate features-in vs. features-out before writing `mvp.md`. Recommendations carry confidence labels.
- Cut ruthlessly. The brief calls for ≤7 must-haves. If a feature is "nice to have," it goes in the out-of-scope section, not the must-have list.
- `post-mvp.md` already holds the deferred-feature catalog — consult it as the starting point for the out-of-scope section.

## Next session

**Step 7 — MVP feature cut.** Case-3 candidate (write step + one decision cluster). Goal: decide what the proof-of-concept must demonstrate; cut ruthlessly to ≤7 must-haves; produce a defensible "not now" list. Brief in `steps.md` → Step 7. Execution order: Step 6 ✓ → **Step 7** → Step 8 (stack & architecture) → Step 9 (data-model sketch + roadmap + phase-transition ADR). ADR number at write time: next is **ADR-0050**.

### Prompt for the next session

> Resume work. Next is **Step 7 — MVP feature cut**. Brief in `steps.md` → § Step 7. Per `_workflow.md` Case 3: read the brief; read this prompt + the **Open questions** block above + `domain-model.md` (the rolled-up domain) + `post-mvp.md` (deferred-feature catalog). Enter planning mode (STOP-AND-CONFIRM gate applies — the cut decisions are the deliberation); on `approved` proceed to write `planning/mvp.md` + append ADR-0050.
>
> **Sizing check at session head.** Per `_workflow.md` Case 2 — Step 7 is expected to fit one window (single coherent decision cluster). Run the fit checklist anyway: if signal 1 fires (the cut has more than one independently-deliberable sub-decision — e.g., command-surface cuts decoupled from data-shape cuts), or signal 7 fires (iterative-discovery framing on which features qualify), partition before writing.
>
> **Read first:** this prompt + the Open questions block above + `domain-model.md` for the entity/command/predicate surface + `post-mvp.md` for the deferred candidates + `decisions.md` for ADR pointers.
>
> **Items in scope (per `steps.md` → Step 7):**
> 1. Write `planning/mvp.md` — ≤7 must-have features, each one sentence; defensible "not now" list with rationale per item.
> 2. Append ADR-0050 — MVP scope decision: rationale for the cut, alternatives considered, what's deferred and why.
>
> **Out of scope — do not pull in:**
> - Stack / architecture / persistence shape (Step 8 — including history implementation shape).
> - Conceptual data model + DDL (Step 9).
> - Phase-transition ADR (Step 9).
> - Pre-transition ADR consolidation pass (Step 9 — scan `decisions.md` for ADRs with 2+ amendments and consolidate before the phase ends).
> - Command-shape work on `split_entry` / `revoke_write_off` / revoke-line-item / `reassign_wa_project` deeper mechanics / `ContractorEngagement` signatures / smart-command-inference landing state (all implementation-phase or residual per `domain-model.md` § Deferred).
>
> **Sequencing:** Step 6 ✓ → **Step 7 (this session)** → Step 8 → Step 9 → (phase transition).
>
> **Reference:** 21 entities (post-ADR-0048), 14 design patterns, roles `superadmin`/`admin`/`coordinator`/`auditor` with the predicate table in ADR-0047, 10-entry blocker registry (9 has-default-resolution + 1 fix-only), Conceptualization phase carries ADR-0001 through ADR-0049. Full detail in `domain-model.md`.
>
> **Process notes:**
> - STOP-AND-CONFIRM gate applies to the MVP cut itself and to ADR-0050.
> - Cut ruthlessly — the brief calls for ≤7 must-haves. "Nice to have" lands in out-of-scope.
> - Recommendation strength: state confidence on recommendations; when asked for contras, separate the exercise from any conclusion; don't flip out of agreeableness (`sessions.md` rule 5).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-15)
- Phase roster: `planning/phases.md`
- Step list (current phase): `planning/steps.md` (Step 6 ✓ COMPLETE — 6a / 6b core / 6b-residual / 6b-residual-2 / 6c-i / 6c-ii / 6c-iii-a / 6c-iii-b-i / 6c-iii-b-ii / 6c-iv-a / 6c-iv-b / 6d all complete; next: Step 7 — MVP feature cut)
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0049; next ADR at write time: ADR-0050)
- **Domain model (Step 6d output):** `planning/domain-model.md` — rolled-up domain projection: 21 entities, relationship table, per-entity lifecycles, authorization predicates (via ADR-0047), history patterns, delete policy, 14 design patterns, 10-entry blocker registry, vocabulary, deferred / open questions
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md`
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
