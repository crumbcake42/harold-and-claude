# Session Conventions

## File contract

**Holds:** Durable conventions that apply to every session, regardless of phase or step — execution rules, the artifact-is-the-deliberation principle, and the note on session restructures. Does **not** hold the STOP-AND-CONFIRM gate (that lives in `handoff.md`) or the case-detection protocol (that lives in `_workflow.md`).
**Update when:** A session execution rule changes; a new restructure pattern is established and worth preserving as a convention. This file is low-churn — most sessions leave it untouched.

---

## Session execution rules

These apply to every conceptualization session, in addition to the per-session prompt. They exist because the session-split structure assumes one decision is deliberated at a time, in the artifact — not pre-picked in chat and then justified.

1. **The artifact is the deliberation.** The doc is where positions land — once it concludes a position and the user approves, the position is committed. Recommendations in chat are welcome (and expected when canvassing decisions per the STOP-AND-CONFIRM gate); they do not pre-decide. The anti-pattern this rule guards against is *writing a position into a planning file before the user has agreed*, and *eliminating options before the doc canvasses them*. Both remain prohibited.
2. **Stay inside the session's scope.** If a justification for the current decision requires reaching into a later step (auth shape, storage choice, lifecycle vocabulary), that is a signal the position is not decidable yet — push back on the step boundary, do not cross it.
3. **Treat prior ADRs as constraints to address, not exclusions to assume.** If a prior ADR appears to eliminate an option, name the tension inside the doc and deliberate it there. Do not dismiss the option in the pre-amble.
4. **Push back, do not pre-empt.** If the framework or step prompt seems wrong, say so before writing. Do not compensate by quietly importing other-step reasoning.
5. **State recommendation strength; resist recency bias on contras.** When recommending a position, state confidence explicitly — distinguish "I'd push back hard on the other side" from "this is close, either works" from "weak lean." When asked to argue against a recommendation (or for a contra in general), separate the contra-exercise from the conclusion: deliver the strongest contra honestly, then explicitly say whether it changes the view and why. A flip is warranted only when the contra exposes something not weighed originally (in which case the original recommendation was under-defended); if the contra is real but already-weighed, hold the position and say so. Avoid the failure mode of "recommend A → contra → silently flip to B" without ever naming whether the flip was on merits or sycophantic.

Cross-conversation context: rules 1–4 originated from an incident on 2026-04-28 (Step 2 startup). `handoff.md`'s STOP-AND-CONFIRM gate is the durable in-repo restatement. Rule 5 originated from a pattern identified on 2026-05-13 (Step 6c-i, session 11).

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

- **2026-05-14:** Step 6b-residual-2 ("Blocker-resolution model reframe") added — an insertion, not a split. Triggered during Step 6c-ii session 13: working cluster 7 (cross-project commands), the deliberation exposed that ADR-0032's fix-only/dismissable blocker binary is partly dishonest — a mechanical acceptance path always exists, and "fix-only" just pushes that resolution off-system into manual edits. The reframe (per-blocker default-resolution commands; the `write-off` model) changes the command surface ADR-0042 must enumerate, so it sequences *before* ADR-0042. Execution order becomes: Step 6b-residual-2 → ADR-0042 write (closes Step 6c-ii) → Step 6c-iii → Step 6d. Placed in `steps.md` after Step 6b-residual — it is blocker-pattern/lifecycle work (6b territory), though discovered during 6c. No other steps renumbered.

- **2026-05-14:** Step 6c-iii ("Rename + WA-domain restructure") split into **Step 6c-iii-a** and **Step 6c-iii-b** — a `_workflow.md` Case 2 restructure, executed mid-session. Triggered during Step 6c-iv-b's planning: 6c-iv-b assumed ADR-0043's Project-side contract attachment, but deliberation established the contract is carried by the WA, not the project — re-attaching it needs the WABundle entity, still unbuilt (Step 6c-iii's headline item). Rather than amend ADR-0043 against a non-existent entity, Step 6c-iii was split:
  - **Step 6c-iii-a** — WABundle entity + WA restructure + contract re-attachment. Pulled forward ahead of Step 6c-iv-b (which depends on a settled `→ contract` resolution path). Completed same session (ADR-0044).
  - **Step 6c-iii-b** — the remainder: WA Code reparenting, `WAAuthorization` rename, `WACodeConf`, the WA-removal model. Stays in its original slot (after the Step 6c-ii predicate-table ADR).
  Execution order becomes: 14a → 6c-iv-a → 6c-iii-a → 6c-iv-b → 14b → Step 6c-ii predicate-table ADR → 6c-iii-b → 6d. No other steps renumbered. (Step 6c-iv was separately split into 6c-iv-a / 6c-iv-b earlier the same day.)

- **2026-05-19:** Step 2.1b ("Frontend architecture & conventions") inserted between Step 2.1 (M1.1) and Step 2.2 (M1.2) — an insertion, not a split (mirrors the 2026-05-14 Step 6b-residual-2 precedent). Triggered by a planning side-session: the user chose to adapt-and-port `sca-ih-tracker`'s mature four-layer frontend architecture (`routes → pages → features → components`, per-feature API barrels, test/story colocation) into this repo before M1.2 builds the first substantial frontend feature. The step **does not map to a roadmap milestone** — a documented exception to `steps.md`'s 1:1 step↔milestone contract. Execution order becomes: 2.1 → 2.1b → 2.2 → 2.3 → 2.4. No steps renumbered (decimal-suffix insertion). Plan: `.claude/plans/i-want-to-have-fluttering-wozniak.md`.
