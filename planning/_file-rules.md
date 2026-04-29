# File Rules

*Generated index — do not edit manually. Regenerate by following the procedure in `planning/_workflow.md` (`_file-rules.md` regeneration procedure). Trigger: any `## File contract` block changes, or stale detection during Path B.*

*Last regenerated: 2026-04-29*

---

## handoff.md

**Holds:** Transient state between Claude Code contexts — current phase pointer, last session summary, next session pointer and prompt, open questions, and pointers to all other planning files. Session execution rules live in `planning/sessions.md`; restructure log lives there too.
**Update when:** A session completes or wraps up (advance next-session pointer, summarize last session, refresh open questions, rewrite prompt); a phase changes; the step list in `steps.md` is restructured. Full protocol in `planning/_workflow.md` (Case 3, completion protocol).

---

## phases.md

**Holds:** Canonical phase roster — name, one-line goal, status (current/complete/not started), and step-list pointer for each phase. Coarse granularity (~3–6 phases for zero-to-prod). Just-in-time enumeration: list the next phase before the current one ends; do not pre-enumerate to launch.
**Update when:** A phase transition occurs (update status, archive step list, create new step list); the next phase is scoped enough to name (add a stub entry). Triggered by a phase-transition ADR in `decisions.md`.

---

## steps.md

**Holds:** Ordered list of steps within the current phase — goal, inputs, outputs, done-when criteria, and decision options pre-canvassed for each step.
**Update when:** A step is added, split, reordered, or completed; phase restructuring occurs. Canonical step list; `handoff.md`'s next-session pointer references it by section heading.

---

## sessions.md

**Holds:** Durable conventions that apply to every session, regardless of phase or step — execution rules, the artifact-is-the-deliberation principle, and the note on session restructures. Does **not** hold the STOP-AND-CONFIRM gate (that lives in `handoff.md`) or the case-detection protocol (that lives in `_workflow.md`).
**Update when:** A session execution rule changes; a new restructure pattern is established and worth preserving as a convention. This file is low-churn — most sessions leave it untouched.

---

## framework.md

**Holds:** Abstract entity/state/relationship/identity vocabulary — the foundational framework established in Step 1. Domain-agnostic.
**Update when:** A framework-level vocabulary decision is revised (rare; requires a superseding ADR in `decisions.md` before editing this file).

---

## decisions.md

**Holds:** Append-only log of finalized design decisions (ADRs), each self-contained with date, status, context, alternatives considered, and consequences.
**Update when:** A session finalizes a decision (append new ADR entry); an existing ADR is superseded (add superseding entry, update the old entry's `Status` field to `superseded by #N`). Never edit accepted entries in place.

---

## _workflow.md

**Holds:** Session-resumption protocol — case detection logic, sub-protocols for Cases 1/2/3, ambiguous-handoff paths, and the `_file-rules.md` regeneration procedure.
**Update when:** Workflow rules change (user explicitly requests an update); deferred sections are resolved in follow-up sessions.
