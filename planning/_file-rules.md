# File Rules

*Generated index — do not edit manually. Regenerate by following the procedure in `planning/_workflow.md` (`_file-rules.md` regeneration procedure). Trigger: any `## File contract` block changes, or stale detection during Path B.*

*Last regenerated: 2026-04-29*

---

## handoff.md

**Holds:** Session state between Claude Code contexts — current phase, last session summary, next session pointer and prompt, open questions, session execution rules, and pointers to all other planning files.
**Update when:** A session completes or wraps up (advance next-session pointer, summarize last session, refresh open questions, rewrite prompt); a phase changes; the step list in `sessions.md` is restructured. Full protocol in `planning/_workflow.md` (Case 3, completion protocol).

---

## framework.md

**Holds:** Abstract entity/state/relationship/identity vocabulary — the foundational framework established in Session 1. Domain-agnostic.
**Update when:** A framework-level vocabulary decision is revised (rare; requires a superseding ADR in `decisions.md` before editing this file).

---

## decisions.md

**Holds:** Append-only log of finalized design decisions (ADRs), each self-contained with date, status, context, alternatives considered, and consequences.
**Update when:** A session finalizes a decision (append new ADR entry); an existing ADR is superseded (add superseding entry, update the old entry's `Status` field to `superseded by #N`). Never edit accepted entries in place.

---

## sessions.md

**Holds:** Ordered list of steps within the current phase — goal, inputs, outputs, done-when criteria, and decision options pre-canvassed for each step.
**Update when:** A step is added, split, reordered, or completed; phase restructuring occurs. Canonical step list; `handoff.md`'s next-session pointer references it by section heading.

---

## _workflow.md

**Holds:** Session-resumption protocol — case detection logic, sub-protocols for Cases 1/2/3, ambiguous-handoff paths, and the `_file-rules.md` regeneration procedure.
**Update when:** Workflow rules change (user explicitly requests an update); deferred sections are resolved in follow-up sessions.
