# Decisions Log

## File contract

**Holds:** Append-only log of finalized design decisions (ADRs), each self-contained with date, status, context, alternatives considered, and consequences.
**Update when:** A session finalizes a decision (append new ADR entry); an existing ADR is superseded (add superseding entry, update the old entry's `Status` field to `superseded by #N`). Never edit accepted entries in place.

Append-only record of finalized design decisions. Each entry should be self-contained — a reader who has never seen this project before should be able to understand what was decided, why, and what was rejected.

## Schema

Each entry uses these fields:

- **Date** — YYYY-MM-DD the decision was finalized
- **Decision** — one sentence, action-first ("Use X for Y")
- **Status** — `accepted` | `superseded by #N` | `revisited`
- **Context** — what problem prompted the decision; what constraints applied
- **Alternatives considered** — at least one rejected option with a one-line reason for rejection
- **Consequences** — what this commits us to; what doors it closes

Entries are numbered sequentially. Once `accepted`, do not edit in place — supersede with a new entry.

---

## ADR-0001 — Treat existing `backend/` and `frontend/` directories as stale; restart greenfield

- **Date:** 2026-04-28
- **Status:** accepted
- **Context:** The repo already contains `backend/` and `frontend/` directories from an earlier scaffolding pass. The user explicitly chose to ignore them and treat the project as greenfield, so that stack and architecture decisions can be made deliberately during conceptualization rather than inherited by accident.
- **Alternatives considered:**
  - *Build on the existing scaffolding.* Rejected — the scaffolding's stack choices were never deliberate, and inheriting them would pre-empt Session 5.
  - *Delete the directories now.* Deferred — no need to delete until implementation starts; deletion can happen as part of the first implementation session.
- **Consequences:** Conceptualization sessions ignore the existing tree. Stack decisions in Session 5 are unconstrained. Existing directories will be cleared (or repurposed) at the start of implementation.

---

## ADR-0002 — Entities are defined by identity-over-mutation; values and relationships are distinct kinds

- **Date:** 2026-04-28
- **Status:** accepted
- **Context:** Session 1 needed a single, testable definition of "entity" that the rest of the framework hangs off. Without one, the line between entities, values, and relationships gets drawn ad-hoc per feature, and the data model fragments.
- **Alternatives considered:**
  - *Everything is an entity.* Rejected — collapses the value/entity distinction, which forces identity overhead onto things that don't need it (coordinates, money, enums) and makes equality semantics confusing.
  - *Entities defined by "important to the business."* Rejected — not a test, it's a vibe. Two reviewers would draw the line differently. The identity-over-mutation test is mechanical.
  - *Entities defined by "has a primary key in the database."* Rejected — confuses model with implementation. The framework should drive the schema, not the other way around.
- **Consequences:** Every modeling question gets routed through one test. Boundary cases (assignments, attachments, line items) get resolved consistently. Some things that feel "important" will be values, and that's fine.

---

## ADR-0003 — State is partitioned into four kinds: intrinsic, lifecycle, derived, historical

- **Date:** 2026-04-28
- **Status:** superseded by ADR-0006
- **Context:** Treating all of an entity's state as one undifferentiated bag leads to predictable failures: derived values get persisted and drift; status fields get treated as just-another-attribute and skip transition rules; history gets bolted on as an audit log and can't answer "what was true at time T." A taxonomy up front lets the rest of the system apply the right rule per kind.
- **Alternatives considered:**
  - *Two kinds — attributes and history.* Rejected — collapses lifecycle status into intrinsic attributes, which loses the structure that the logic layer (Session 2) is going to need. Status really is its own axis.
  - *No derived-state category; compute everything on read.* Rejected as a *framework* position — performance will force materialization for some derivations, and the framework should name that explicitly so materialization is governed (must be reproducible from inputs) rather than ad-hoc.
  - *History as audit log, separate from the model.* Rejected — the agency context (Session 3) is almost certainly going to need point-in-time queries for compliance/reporting. Treating history as first-class now avoids a costly retrofit.
- **Consequences:** Schemas and APIs must distinguish writeable inputs from derived outputs. Lifecycle status gets its own treatment in Session 2's transition rules. History implementation shape is deferred (event-sourcing vs. temporal tables vs. append-only) but the requirement that history exist is locked in.

---

## ADR-0004 — Relationships default to typed references; promote to associative entities only when they carry state

- **Date:** 2026-04-28
- **Status:** accepted
- **Context:** Two extreme defaults exist: (a) every relationship is just a foreign key, with extra fields bolted onto whichever side is convenient, or (b) every relationship is its own table/entity to keep options open. Both go wrong. (a) leads to "where do we store the assignment's start date?" thrash; (b) explodes the entity count and makes simple links look heavy.
- **Alternatives considered:**
  - *All relationships are entities.* Rejected — overweights simple links, inflates the ID space, makes ordinary "has-a" relationships look like first-class concepts when they aren't.
  - *All relationships are foreign keys; bolt extra fields onto one side.* Rejected — the bolt-on side is arbitrary and the extra fields outgrow that home. Classic source of bugs when an "assignment" gains a status.
  - *Default to ownership (cascade-delete) for parent-child.* Rejected as the *default* — most "X has many Y" relationships are not ownership. Cascade is a footgun when applied by reflex.
- **Consequences:** The promotion criterion ("does this relationship carry state of its own?") is mechanical and reviewable. Validity windows are allowed on plain references without forcing entity-hood. Ownership is opt-in and rare. Session 3 will surface real cases that may pressure-test this rule.

---

## ADR-0005 — Identity is a system-assigned UUID; natural keys are uniqueness constraints, not identifiers

- **Date:** 2026-04-28
- **Status:** accepted
- **Context:** The choice of primary identifier is one of the few decisions that's painful to reverse later — every reference in the system commits to it. The two real options are surrogate keys (UUID/serial assigned by us) or natural keys (something domain-meaningful like a project code).
- **Alternatives considered:**
  - *Natural keys as primary identifiers.* Rejected — every natural key in this kind of domain (project codes, sample numbers, agency identifiers) eventually changes, gets restructured, or gets reissued. A rename then breaks every reference. The pain is large and certain.
  - *Composite keys (type + natural key).* Rejected — solves nothing the surrogate solves and complicates every join.
  - *Auto-increment integers.* Rejected for the primary identifier — leaks information (creation order, volume), collides across environments, and isn't safe to expose. UUIDs avoid all three. (Integers may still appear as internal optimization; not the identity.)
- **Consequences:** One UUID column on every entity. References everywhere are typed UUIDs. Natural keys live as intrinsic attributes with uniqueness constraints and may freely change. No domain rename can break a reference. Cross-system identity (whether our UUIDs need to be stable across other agency systems) is deferred to Session 3.

---

## ADR-0006 — Historical state is a named kind; whether an entity carries it is a per-entity decision from a defined menu

- **Date:** 2026-04-29
- **Status:** accepted
- **Decision:** Treat historical state as a named kind in the four-kind taxonomy; require an explicit history-pattern decision for every entity at definition time, chosen from a menu defined before domain mapping begins.
- **Context:** ADR-0003 committed to historical state as a universal, first-class property of all entities, motivated partly by anticipated compliance and point-in-time reporting requirements. Those requirements are now out of scope. Accountability history (who changed what, when, with what note) remains a real requirement, but varies by entity — some entities are high-stakes for accountability (deliverables whose status is disputed; assignments with contested timelines); others (lookup tables, configuration data) have none. Applying first-class history universally adds complexity at every phase — transition design, data modeling, write paths, and test surface — without proportional benefit across the full entity set.

  A per-entity decision requires a disciplined process: a defined menu of history patterns must exist before entities are modeled, and choosing from the menu must be required at entity definition time, so that history needs are never overlooked.

- **Alternatives considered:**
  - *Keep universal first-class history (ADR-0003).* Rejected — the compliance motivation is removed; the accountability use case is real but scoped. Universal history adds measurable overhead to the transition layer, data model, write paths, and test coverage for every entity, including those with no accountability requirement.
  - *No explicit history category; treat as per-entity bolt-on with no framework guidance.* Rejected — reverts to the undisciplined approach ADR-0003 was written to prevent. Without a defined menu and a forcing function at entity-definition time, history decisions will be inconsistent and some needs will be missed.
  - *Entities-first: define all entities, then assess history needs in a single review pass.* Rejected as the workflow for this project — at the expected entity count, the review pass degrades in thoroughness and risks structural rework if history decisions require relationship changes after the entity model is set.
- **Consequences:** The four-kind state taxonomy is preserved; "historical" remains a named kind. A dedicated session (Session 5) defines the menu of available history patterns and the criteria for choosing before domain mapping begins. Choosing from the menu is required for every entity — no entity may be defined without a history decision. History implementation shape for entities that carry history remains deferred to the stack session (Session 8).
