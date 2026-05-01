---
name: sca-tracker project context
description: What sca-tracker is, its current phase, and key structural decisions already locked
type: project
originSessionId: 924ceee8-3bbe-402c-9218-8cd7036c114d
---
sca-tracker is a project-state tracking tool for an environmental monitoring agency. It is in the **conceptualization phase** — no code is written; planning artifacts live in `planning/`.

**Why:** Deliberate design before implementation; stack and domain decisions are being made step-by-step to avoid inheriting bad defaults.

**Vocabulary:** Phase > Step > Session is the locked three-level hierarchy. A Step is a unit of deliberate work; a Session is one Claude Code context window. Most Steps fit in one Session; some are partitioned. Correct user drift to these terms.

**Step structure (9 steps in conceptualization):**
- Steps 1–5: domain-agnostic abstract framework (all done)
- Step 1 (done, 2026-04-28): entity/state vocabulary → `planning/framework.md`, ADR-0002–0005
- Step 2 (done, 2026-04-29): transitions & history-semantics → `planning/logic.md`, ADR-0007/0008
- Step 3 (done, 2026-04-30): lifecycle rules & invariants → `planning/logic.md`, ADR-0009/0010/0011, plus cross-entity acknowledgement gating pattern
- Step 4 (done, 2026-05-01): authorization → `planning/logic.md`, ADR-0012
- Step 5 (done, 2026-05-01): history & auditing patterns (four-pattern menu + selection criteria) → `planning/history-patterns.md`, ADR-0013
- Step 6 (in progress): domain mapping → eventually `planning/domain-model.md`. Split into 6a (entity identification, itself partitioned into 6a-i/6a-ii/6a-iii), 6b (workflows & lifecycles), 6c (relationships & authorization), 6d (domain model assembly). See `planning/steps.md` and `planning/handoff.md` for current sub-session pointer.
- Steps 7–9: MVP cut, stack/architecture, data model & roadmap

For the most recent ADR list and next-step pointer, always defer to `planning/decisions.md` and `planning/handoff.md` rather than this memory.

**Locked framework decisions:**
- Entity = identity over mutation (ADR-0002)
- Four-kind state taxonomy: intrinsic, lifecycle, derived, historical (ADR-0003, narrowed by ADR-0006)
- Relationships default to typed references; promote to entity only if they carry state (ADR-0004)
- Identity = system-assigned UUID; natural keys are uniqueness constraints (ADR-0005)
- Historical state is per-entity, chosen from a menu defined in Step 5 (ADR-0006)
- Commands are the unit of change at the logic layer (ADR-0007)
- For history-carrying entities, state mutation and history record are atomic, framework-enforced (ADR-0008)
- Lifecycle is a declarative state machine per entity type; commands declare which transition they effect (ADR-0009)
- Well-formedness invariants are declared on the schema element they constrain; enforcement is write-path only in the command pipeline (ADR-0010)
- Reject is the framework violation-handling default; quarantine deferred as a per-entity pattern (ADR-0011)
- Authorization is a declarative predicate over (caller, command, target), declared per command, evaluated first in the pipeline (ADR-0012)
- Four history patterns (no history / audit log / comprehensive capture / lifecycle capture); per-entity selection required at definition time; references in history records are typed UUIDs only, no snapshots (ADR-0013)

**Domain context (user-supplied 2026-04-30, kept abstract in framework):** the eventual app tracks projects with a three-layer state model — base expectations (template-set), inferred expectations (uploading a child entity infers another required child), and closeable gaps where each unfulfilled requirement needs explicit per-requirement user sign-off at close. Reconciled to the framework as: divergence-from-expected is state (per the four-kind taxonomy), not violation; closing-with-unacknowledged-pendings is enforced via cross-entity acknowledgement gating (named as a pattern in `logic.md`).

**Next step:** Step 6a-ii — History-pattern walk + remaining open modeling questions from 6a-i. See `planning/handoff.md` for full prompt and open questions. Gate: STOP-AND-CONFIRM applies; present decisions in chat with recommendations, wait for approval before writing files.
