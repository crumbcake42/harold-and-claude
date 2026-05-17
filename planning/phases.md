# Phases

## File contract

**Holds:** Canonical phase roster — name, goal, status, and step-list pointer for each phase. Coarse granularity (~3–6 phases for zero-to-prod). Just-in-time enumeration: list the next phase before the current one ends; do not pre-enumerate to launch.
**Update when:** A phase transition occurs (update status, archive step list, create new step list); the next phase is scoped enough to name (add a stub entry). Triggered by a phase-transition ADR in `decisions.md`.

Phase-change trigger: a dedicated ADR in `decisions.md` (e.g., "Conceptualization phase complete; implementation begins"). When that ADR lands, the agent (a) updates status here, (b) archives the current step list to `planning/steps.archive/<phase-name>.md`, (c) creates the new phase's `planning/steps.md`. Lightweight gate around those writes (single-line confirm), not full deliberation.

To inject a blocker or unplanned work mid-phase: insert a tagged step into `steps.md` at the appropriate point — see `sessions.md` (session conventions) for the injection pattern. Phase structure is not affected.

---

## Phase 1 — Conceptualization

**Status:** complete (2026-05-17, ADR-0054)
**Goal:** Produce the abstract framework, logic layer, and domain model that implementation will be built on — no code written.
**Steps:** [archived](steps.archive/conceptualization.md)

---

## Phase 2 — Implementation

**Status:** current
**Goal:** Build the MVP per `planning/mvp.md` and `planning/roadmap.md` — 6 must-have features delivered as 9 sequential milestones (M0 Foundations → M8 Cutover prep) on the stack pinned by ADR-0051 + ADR-0052.
**Steps:** [planning/steps.md](steps.md)

---

## Phase 3 — TBD

**Status:** not started
**Goal:** TBD — to be scoped before Phase 2 ends. Likely candidates: post-MVP feature delivery (per `mvp.md` § Not now); office-onboarding-and-operations once the MVP cutover lands.
**Steps:** TBD
