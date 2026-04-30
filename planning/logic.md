# Logic

## File contract

**Holds:** Logic-layer semantics — the unit of change (transitions section), what successful changes leave behind (history-semantics section), and Steps 3 (lifecycle/invariants) and 4 (authorization) outputs as they land. Domain-agnostic; builds on `framework.md`'s vocabulary.
**Update when:** A logic-layer decision is finalized (Steps 2/3/4 each append a section); a logic-layer decision is revised (requires a superseding ADR in `decisions.md` before editing).

The logic layer sits on top of `framework.md`. It defines what a state change is, where the rules attach, and what each successful change records. Read `framework.md` first; this doc assumes its vocabulary (entity, the four kinds of state, relationships, UUID identity).

---

## Transitions

**The smallest named thing that changes state in the system is a *command*.** A command is a request specifying `(caller, named operation, target entity, payload)`. The framework either rejects it (with a reason) or applies it (producing a new state and, where applicable, a history record — see next section).

Properties:

- **Every state change is invoked through a command.** Direct writes against entity records are not part of the API surface, even for trivial attribute edits. "Rename project" is a command. "Update sample method" is a command. The vocabulary cost is real and front-loaded — every state change earns a name.
- **Commands are the uniform attachment surface for cross-cutting concerns.** Lifecycle rules, invariants, authorization predicates, and history capture all hang off commands rather than off individual write sites. Steps 3 and 4 will define the exact attachment shapes; Step 2 commits to the surface those steps build on.
- **A command's outcome is binary at the framework level: rejected or applied.** Rejection carries a reason; application produces the new entity state plus the history record (where the entity carries history). Partial application is not a framework outcome — multi-step operations that need atomicity are themselves commands.

Direct writes and events-as-primary were considered and rejected — see ADR-0007 for the alternatives and the reasons.

---

## History semantics

**For an entity that carries history, a successful command both mutates the entity record and writes a history record in the same transaction. Capture is structurally enforced by the command pipeline — it is not opt-in per command implementation.**

Per ADR-0006, whether an entity carries history is a per-entity decision made at definition time from the menu Step 5 will define. This section governs the case where an entity *does* carry history; the per-entity decision and the menu of patterns are out of scope here.

For entities declared history-carrying:

- The state mutation and the history record are written atomically. A command cannot succeed without producing the history record, and cannot produce the history record without succeeding. The framework owns this invariant; no command handler can opt out.
- The history record is sufficient to reconstruct the change. Exactly *what* gets recorded — full before/after, command + payload only, change deltas — is one of the things Step 5's pattern menu varies along.
- Current state remains the system of record. Reads return the current entity record directly; reconstructing past states means consulting the history record, not replaying anything.

For entities not declared history-carrying:

- A successful command mutates the entity record. No history record is written. The current entity record is the only record.

The "mandatory" in *mandatory capture* applies *within* the set of history-carrying entities. Capture is not best-effort there. Bolted-on audit log is **not** the framework-level default — it remains available as a Step 5 pattern for entities whose accountability needs are explicitly best-effort, but choosing it is an opt-in pattern with a documented tradeoff, not the framework default. See ADR-0008 for the alternatives and reasoning.

---

## Coupling between transitions and history semantics

The two decisions above are coupled. Commands give the framework a stable surface inside which mandatory capture is enforced — capture is a step of the command pipeline. Direct writes would have no such surface; capture would have to be re-enforced at every write site, with predictable drift. Events as the primary unit would force history universally and conflict with ADR-0006's per-entity opt-out (events would be emitted regardless of whether the entity is declared history-carrying).

Commands + state-mutating-with-mandatory-capture is the internally coherent pairing given ADR-0006.

---

## Lifecycle rules and invariants

The framework distinguishes two kinds of constraint that must hold over an entity's state:

- **Temporal invariants** — constraints on transitions. "An archived entity cannot be re-activated." "A submitted entity cannot be edited." These are *lifecycle rules*.
- **Atemporal invariants** — constraints on a single point-in-time state. "Field X is non-null." "If status is X then field Y must be set." "An associative entity's `valid_to` is not before its `valid_from`." These are *well-formedness invariants*.

Both attach to the same enforcement surface — the command pipeline, per ADR-0007 — but they declare in different places. The next three sub-sections cover lifecycle specification, well-formedness invariant declaration and enforcement, and violation handling. A fourth sub-section names a pattern that recurs when all three decisions are combined.

### Lifecycle specification

**Each entity type with a lifecycle declares it as a state machine: a finite, named set of states (per `framework.md`'s lifecycle-status kind) plus the allowed transitions between them.** The state machine is the single source of truth for what states the entity can be in and which transitions are permitted.

- A command that effects a lifecycle transition **declares the transition it effects** by name. The command pipeline validates the entity's current lifecycle status against the state machine and rejects the command if the named transition is not permitted from that state.
- A command that does not affect lifecycle **declares itself non-lifecycle-affecting**. It mutates intrinsic attributes only; the pipeline does not check the state machine for it.
- For an entity type with no lifecycle, the state machine degenerates to a single state with no transitions. The declaration is mechanical, not ceremonial.
- Concrete lifecycle vocabularies — the actual state names per entity type — are deferred to Step 6. Step 3 picks the *shape* of lifecycle specification, not the contents.

Guards-as-command-preconditions and imperative handlers were considered and rejected — see ADR-0009. The dominant reason: `framework.md` commits lifecycle status as the entity's own dimension and the primary axis for "what can happen next." A specification scheme where the lifecycle is emergent from individual command preconditions does not honor that.

### Well-formedness invariants — declaration and enforcement

Two questions: where invariants are *declared*, and where they are *enforced*.

**Declared on the schema element they constrain:**

- *Intra-entity invariants* are declared on the entity type. They constrain the well-formedness of a single entity record.
- *Cross-entity invariants* are declared on the relationship type — relationships are typed per `framework.md`. They constrain interactions between entities, including cardinality limits and validity-window properties.

Invariants are not declared on commands. The same invariant would be re-declared on every command that touches the constrained schema element, with predictable drift between sites.

**Enforced on the write path, in the command pipeline.** Every command revalidates relevant invariants — those over any entity it mutates and any relationship it touches — *after* applying the proposed change. If any invariant fails, the command is rejected (see violation handling below); the proposed change is not persisted.

Read-path-only enforcement and both-layer enforcement were considered and rejected — see ADR-0010.

**Concurrency for cross-entity invariants** is a persistence-isolation concern, deferred to Step 8 (stack & architecture). The framework commits to *where* the check happens (the command pipeline, after the proposed change is applied, before the transaction commits); the persistence layer must provide isolation strong enough to make the check meaningful under concurrent commands. The exact mechanism (serializable transactions, optimistic locking, advisory locks) is a stack-session decision.

### Violation handling

**A command that would violate a lifecycle rule or a well-formedness invariant is rejected.** No state mutation is persisted; no history record is written, regardless of whether the target entity is history-carrying; the caller receives a rejection reason. This is the framework default and the only outcome internally consistent with ADR-0007's binary command outcome and ADR-0008's atomic state-mutation/history-capture pairing.

Violation handling responds to commands that break framework-declared rules. State-level divergence between *expected* and *actual* outcomes — when an entity's history reflects a course different from a baseline expectation set elsewhere — is not a violation. It is modeled as state, using `framework.md`'s four-kind taxonomy (intrinsic for declared expectations; derived for divergence computed from expectations and current state). The framework provides the substrate; the domain decides what to model.

Error-with-allow and warn alternatives were considered and rejected — see ADR-0011.

Quarantine — applying the command but isolating the affected entity in a side state outside its normal lifecycle — has real use cases (data ingestion, bulk imports, eventual-consistency scenarios where partial validity is preferable to total rejection), but is **not** the framework default. It adds machinery (a quarantine state co-existing with each entity's lifecycle) that not all entities need, and conflicts with concrete lifecycle vocabularies being deferred to Step 6. Quarantine remains in scope as a *deferred per-entity pattern* — analogous to how audit-log-as-pattern is preserved as a Step 5 menu option for entities with explicitly best-effort accountability needs. It is not commissioned as a pattern at this step; surfacing it preserves the option without committing to it.

### Pattern: cross-entity acknowledgement gating

A pattern that recurs across the three decisions: a parent entity's terminal lifecycle transition is gated on related entities having reached an acknowledged terminal state. The gate is structural, not advisory.

Where a parent may not complete its lifecycle until each related entity has reached one of an explicit set of terminal states, the constraint is a cross-entity invariant declared on the relationship type (per ADR-0010) and enforced as a precondition of the parent's named transition (per ADR-0009). Acknowledgement itself is a lifecycle transition on the related entity, invoked through its own named command (per ADR-0007); the command's history record (per ADR-0008, for history-carrying entities) captures the acknowledgement structurally. A parent transition attempted while any related entity is in a non-terminal state is rejected (per ADR-0011).

The framework's job is to make the acknowledgement structurally inescapable. What an acknowledgement *means* — what the related entity is, which terminal states count as acknowledged, what supporting data the acknowledgement command captures — is a domain concern (Step 6+).

---

## Coupling between lifecycle, invariants, and violation handling

Lifecycle rules and well-formedness invariants share the same enforcement surface (the command pipeline) and the same outcome on violation (command rejection). They declare in different places — state machine for lifecycle; entity or relationship type for well-formedness — because what they constrain differs (a process versus a static state). The structural shape Step 3 picks: *declaration* varies with what is being constrained; *enforcement* and *violation outcome* do not.

---

## Deferred — later steps

- **Authorization predicate** — how "can caller C run command X against target T" is answered. Step 4.
- **Per-entity history pattern menu and selection criteria** — what a history record contains for any given entity, and how to choose. Step 5.
- **Implementation shape for entities that carry history** — event store / temporal tables / append-only history tables. Step 8.
- **Reference snapshotting** — when a history-carrying entity references a non-history entity (or another history-carrying one), what gets captured in the history record so that the past reference remains interpretable. Surfaces as a Step 5 concern.
- **Quarantine as a per-entity violation-handling pattern** — applying-but-isolating semantics for entities whose accountability or ingestion characteristics warrant it. Available per ADR-0011; commissioning is deferred, most plausibly a Step 5 concern.
