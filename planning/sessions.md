# Session Conventions

## File contract

**Holds:** Durable conventions that apply to every session, regardless of phase or step — execution rules, the artifact-is-the-deliberation principle, and the note on session restructures. Does **not** hold the STOP-AND-CONFIRM gate (that lives in `handoff.md`) or the case-detection protocol (that lives in `_workflow.md`).
**Update when:** A session execution rule changes; a new restructure pattern is established and worth preserving as a convention. This file is low-churn — most sessions leave it untouched.

---

## Session execution rules

These apply to every conceptualization session, in addition to the per-session prompt. They exist because the session-split structure assumes one decision is deliberated at a time, in the artifact — not pre-picked in chat and then justified.

1. **The artifact is the deliberation.** Do not announce a position in chat before writing. Do not eliminate options before the doc canvasses them. Land positions only as the doc concludes.
2. **Stay inside the session's scope.** If a justification for the current decision requires reaching into a later step (auth shape, storage choice, lifecycle vocabulary), that is a signal the position is not decidable yet — push back on the step boundary, do not cross it.
3. **Treat prior ADRs as constraints to address, not exclusions to assume.** If a prior ADR appears to eliminate an option, name the tension inside the doc and deliberate it there. Do not dismiss the option in the pre-amble.
4. **Push back, do not pre-empt.** If the framework or step prompt seems wrong, say so before writing. Do not compensate by quietly importing other-step reasoning.

Cross-conversation context: an incident on 2026-04-28 (Step 2 startup) produced these rules. Memory entry `feedback_no_preanswering.md` captures the same ground from the assistant's side; `handoff.md`'s STOP-AND-CONFIRM gate is the durable in-repo restatement.

---

## Note on session restructures

Steps are split when scope exceeds one session. When a split happens:

- Insert the sub-steps into `steps.md` at the appropriate point, numbered with a decimal suffix (e.g., Step 2.1, Step 2.2) or renumbered if the plan allows.
- Update `handoff.md`'s Next session pointer to the first sub-step.
- Record the restructure here: state the original step, what triggered the split, and the resulting sub-step list. This creates an audit trail without polluting `handoff.md`.

**Restructure log:**

- **2026-04-28:** Original Step 2 ("Logic & invariants") stacked five large decisions into one block. Split into three steps to keep each decision deliberate:
  - **Step 2** — Transitions & history-semantics (coupled pair, kept together)
  - **Step 3** — Lifecycle rules & invariants (coupled pair, kept together)
  - **Step 4** — Authorization
  Original Steps 3–6 (Domain mapping → Data model & roadmap) shifted to Steps 5–8.

- **2026-04-29:** Step 5 (History & auditing patterns) added between Step 4 (authorization) and domain mapping. ADR-0003's universal history commitment narrowed by ADR-0006: historical state remains a named kind in the four-kind taxonomy but is now a per-entity decision from a defined menu. Choosing from the menu is required at entity definition time. Original Steps 5–8 (Domain mapping → Data model & roadmap) shifted to Steps 6–9.
