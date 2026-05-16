# File Rules

*Generated index — do not edit manually. Regenerate by following the procedure in `planning/_workflow.md` (`_file-rules.md` regeneration procedure). Trigger: any `## File contract` block changes, or stale detection during Path B.*

*Last regenerated: 2026-05-15*

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

## logic.md

**Holds:** Logic-layer semantics — the unit of change (transitions section), what successful changes leave behind (history-semantics section), and Steps 3 (lifecycle/invariants) and 4 (authorization) outputs as they land. Domain-agnostic; builds on `framework.md`'s vocabulary.
**Update when:** A logic-layer decision is finalized (Steps 2/3/4 each append a section); a logic-layer decision is revised (requires a superseding ADR in `decisions.md` before editing).

---

## history-patterns.md

**Holds:** The menu of per-entity history patterns and the selection criteria for choosing between them. Established in Step 5 before domain mapping. Every entity defined in Step 6 must choose from this menu.
**Update when:** A pattern is added, removed, or revised (requires a superseding ADR in `decisions.md` before editing). Selection criteria may be refined during domain mapping if edge cases surface, but the pattern set itself is stable.

---

## domain-model.md

**Holds:** The rolled-up domain projection — the entities, relationships, lifecycles, authorization predicates, history patterns, design patterns, blocker registry, and vocabulary that map `framework.md` / `logic.md` / `history-patterns.md` onto the SCA-tracker domain. Standalone reference for a framework-aware reader.
**Update when:** A domain-shape ADR lands in `decisions.md` (entity added/removed/renamed; relationship shape changes; lifecycle/state-machine change; predicate row added/changed; design pattern added/retired; vocabulary term added/revised). The handoff's cumulative tables are the in-flight working surface during a session; this file is the post-session source of truth between sessions.

---

## mvp.md

**Holds:** The MVP feature cut — ≤7 must-have features (each one sentence + brief expansion), the defensible "not now" list with per-item rationale, the in-MVP carve-outs that may slip, and the in-MVP command-shape carry-forwards whose mechanics land in the implementation phase (distinct from "not now").
**Update when:** A must-have is added or cut; a "not now" item is promoted to MVP; an in-MVP carve-out is resolved (kept or slipped); a command-shape carry-forward's mechanics are settled (move out of the carry-forward list). Source decision is ADR-0050; substantive shape changes require a superseding ADR before editing.

---

## decisions.md

**Holds:** Append-only log of finalized design decisions (ADRs), each self-contained with date, status, context, alternatives considered, and consequences.
**Update when:** A session finalizes a decision (append new ADR entry); an existing ADR is partially revised (preferred: append a new ADR with an "Amendments to other ADRs" section naming the prior ADR and the surface being modified; the prior ADR's `Status` stays `accepted`); an existing ADR is wholly obsolete (supersession: append a superseding entry, update the prior entry's `Status` to `superseded by #N`). Never edit accepted entries in place. Wholesale supersession is rare in this project — amendment is the dominant tool for partial revisions, and traceability between an ADR and its amendments relies on grep ("amends ADR-NN" in later ADR text).

---

## post-mvp.md

**Holds:** Post-MVP feature candidates — name, one-line description, one-line "why interesting." Holding pen between now and Step 7's `mvp.md` out-of-scope section.
**Update when:** A feature idea surfaces that's worth remembering but explicitly out of MVP scope. Consolidated into `mvp.md`'s out-of-scope section when Step 7 runs.

---

## _workflow.md

**Holds:** Session-resumption protocol — case detection logic, sub-protocols for Cases 1/2/3, ambiguous-handoff paths, and the `_file-rules.md` regeneration procedure.
**Update when:** Workflow rules change (user explicitly requests an update); deferred sections are resolved in follow-up sessions.
