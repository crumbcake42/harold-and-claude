# Framework

## File contract

**Holds:** Abstract entity/state/relationship/identity vocabulary — the foundational framework established in Step 1. Domain-agnostic.
**Update when:** A framework-level vocabulary decision is revised (rare; requires a superseding ADR in `decisions.md` before editing this file).

The abstract vocabulary `sca-tracker` is built on. Domain-agnostic by design — domain mapping happens in Step 6. This doc states one position per question; rejected alternatives live in `decisions.md`.

Read order if you're cold: this doc → `logic.md` (Steps 2–4 output, transitions/lifecycle/auth) → `history-patterns.md` (Step 5 output, history menu and selection criteria) → `domain-model.md` (Step 6 output, the projection onto the actual domain).

---

## Entity

**An entity is anything the system needs to refer to identically over time, even as its attributes change.**

The test: if you can imagine the thing being renamed, reclassified, or otherwise mutated and a user still expecting "that's the same one," it's an entity. If two instances with identical attributes are indistinguishable and interchangeable, it's a value, not an entity.

Three categories of thing exist in this system:

- **Entity** — has identity that persists across mutation. Carries state. Always referenced by ID, never by content.
- **Value** — fully described by its attributes. No identity beyond them. Two values with equal fields are the same value. Money amounts, dates, addresses-as-strings, enum tags.
- **Relationship** — a link between entities. May itself be an entity (see below) or may be a pure reference.

Boundary cases — resolve by asking *"could this thing change while still being the same thing?"*:

- A *file attachment* with metadata that may change → entity.
- A *coordinate* — change the numbers and it's a different coordinate → value.
- An *assignment of person to project* — if it has a start date, end date, role, then it can change while remaining "this assignment" → entity. If it's just "is X linked to Y, yes/no" → relationship.

## State

An entity's state is partitioned into four kinds. Each kind has different rules about how it's stored, mutated, and trusted.

1. **Intrinsic attributes** — facts the entity carries by being itself (a project's name, a sample's collection method). Mutable, but mutations are explicit events. The current value is authoritative.

2. **Lifecycle status** — where the entity is in some defined process (`draft → active → archived`). Always drawn from a finite, named set per entity type. Transitions are governed by rules (Session 2). Status is *the* primary axis for "what can happen to this thing next."

3. **Derived state** — computable from other state (`is_overdue`, `child_count`, `latest_reading`). **Never persisted as primary truth.** May be cached or materialized for performance, but the materialization must be reproducible from the underlying state. If a value can't be derived from inputs, it's not derived state — it's intrinsic.

4. **Historical state** — prior values of any of the above, plus the actors and timestamps of changes. Named as a distinct kind; whether an entity carries it, and in what form, is a per-entity decision made at entity definition time from a defined menu of history patterns. The menu is established in Session 5 before domain mapping begins. Choosing from the menu is required — no entity may be defined without a history decision. Not every entity needs history, but the decision must be explicit.

Rules that follow:

- Derived state never appears in a write API. You write the inputs; the system shows the derivation.
- Lifecycle status is not just an intrinsic attribute — it is the entity's own dimension and gets its own treatment in the logic layer.
- For entities that carry historical state, current state may be understood as a view over the change record at `now`. For entities without it, current state is the mutable entity record directly. Which applies is determined at entity definition time (see ADR-0006).

## Relationships

**Default: a relationship is a typed reference from one entity to another, with declared cardinality and an optional validity window.** A reference is just an ID plus the type of thing it points at — it carries no state of its own.

Promotion rules:

- **If the relationship carries state of its own** (a role, a quantity, dates, a status) → promote it to an entity. The "assignment" example above. This is the only criterion that matters.
- **If the relationship has a validity window** but no other state → still a reference, with `valid_from` / `valid_to` on the reference itself. Not enough state to justify entity-hood.
- **Cardinality** (1:1, 1:N, N:M) is declared per relationship type, not inferred. N:M between entities is allowed without an associative entity unless one of the promotion rules fires.

Ownership (parent-child with cascade) is *not* the default. Use it only when the child genuinely cannot exist without the parent — i.e., deleting the parent makes deleting the child the obviously correct semantics, not a convenience. Most "X has many Y" relationships are references, not ownership.

## Identity

**Every entity has a surrogate UUID assigned by the system at creation. That UUID is the entity's identity. Nothing else.**

Consequences:

- Natural keys (project codes, sample numbers, email addresses) exist as *uniqueness constraints* on intrinsic attributes, not as identifiers. They can change. References never use them.
- An entity's identity is opaque — a reference is just a typed UUID. You cannot tell anything about an entity from its ID.
- Two entities of different types may not collide on ID (UUID space is global, but type is part of every reference).
- Identity is assigned once and never reused. Soft-delete leaves the ID in place; hard-delete tombstones it.

This closes off the "natural key as primary key" path. The cost is one extra column everywhere; the benefit is that no domain rename ever breaks a reference.

---

## Deferred — needs the domain or later sessions

These intentionally aren't decided here. Flagging so Session 3+ knows to come back:

- **History implementation shape** (event-sourced vs. append-only vs. temporal tables) — depends on Session 2 (transitions) and Session 8 (stack). The framework requires that each entity has an explicit history decision; the implementation shape of entities that carry history is a stack-session concern.
- **History patterns menu** — the available per-entity patterns and the criteria for choosing are defined in Session 5, before domain mapping.
- **Cross-system identity** — whether sca-tracker IDs need to be stable across other agency systems, or whether external IDs are just intrinsic attributes. Depends on Session 6 integration story.
- **Soft-delete vs. hard-delete policy** — likely domain-driven (regulatory retention). Decide in Session 6.
- **Concrete lifecycle vocabularies** per entity — Session 6, once entities exist.
