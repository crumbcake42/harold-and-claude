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

## Deferred — later steps

- **Lifecycle rules and invariants** — which commands are valid in which lifecycle state, where invariants are declared, and what happens when a write would violate them. Step 3.
- **Authorization predicate** — how "can caller C run command X against target T" is answered. Step 4.
- **Per-entity history pattern menu and selection criteria** — what a history record contains for any given entity, and how to choose. Step 5.
- **Implementation shape for entities that carry history** — event store / temporal tables / append-only history tables. Step 8.
- **Reference snapshotting** — when a history-carrying entity references a non-history entity (or another history-carrying one), what gets captured in the history record so that the past reference remains interpretable. Surfaces as a Step 5 concern.
