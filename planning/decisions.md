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

---

## ADR-0007 — Use commands as the unit of change at the logic layer

- **Date:** 2026-04-29
- **Decision:** Every state change in the system is invoked through a named *command* — `(caller, named operation, target entity, payload)`. Direct writes against entity records are not part of the API surface. The framework either rejects a command (with a reason) or applies it (producing the new entity state and, where applicable, a history record).
- **Status:** accepted
- **Context:** Step 2 needed to pick the smallest named thing the logic layer admits as a state change. Without a uniform unit, lifecycle rules, invariants, authorization, and history capture each need ad-hoc attachment points on every write site, with predictable drift over time. The choice of unit governs the surface that Steps 3 and 4 will hang off.
- **Alternatives considered:**
  - *Direct writes.* Rejected — no named attachment surface for guards, authorization, lifecycle, or history. Each cross-cutting concern would need its own intercept on every write site, drift between sites is near-certain, and the framework loses the surface that's the point of having a logic layer.
  - *Events as primary.* Rejected — strongest when history is universal; ADR-0006 made history per-entity, so events-as-primary inherits read-side projection cost (current state derived, schema evolution touches replays, snapshots become a separate concern) without compensating universal-history benefit. The per-entity history opt-out also becomes awkward — events get emitted regardless of whether the entity is declared history-carrying.
- **Consequences:** Every state change earns a name (vocabulary cost is paid at definition time). Commands are the uniform attachment surface for the cross-cutting concerns Steps 3 and 4 will define. Multi-step atomic operations are themselves commands; partial application is not a framework outcome. Direct entity writes are not part of the API surface, even for trivial attribute edits.

---

## ADR-0008 — A successful command on a history-carrying entity mutates state and writes a history record in the same transaction; capture is framework-enforced

- **Date:** 2026-04-29
- **Decision:** For entities declared history-carrying (per ADR-0006), a successful command both mutates the entity record and writes a history record atomically. Capture is structurally enforced inside the command pipeline — it is not opt-in per command handler. For entities not declared history-carrying, a successful command just mutates the entity record. Bolted-on audit log is **not** the framework-level default; it remains available as a Step 5 *pattern* for entities whose accountability needs are explicitly best-effort.
- **Status:** accepted
- **Context:** Step 2 needed to specify what a successful command leaves behind for entities that carry history. Three positions on the table: event-producing, state-mutating with mandatory capture, state-mutating with bolted-on audit log. ADR-0006 had already softened ADR-0003's universal history commitment to a per-entity decision, so the question is the framework-level mechanism *for entities that do carry history* — Step 5's menu picks per-entity patterns from that mechanism.
- **Alternatives considered:**
  - *Event-producing.* Rejected — current-state reads become projections (schema evolution touches replays, snapshots become a separate concern), and ADR-0006's per-entity opt-out is awkward to honor when events are produced universally by construction.
  - *State-mutating with bolted-on audit log as the framework-level default.* Rejected — exactly the structural failure mode ADR-0003 was originally written against. ADR-0006 softened ADR-0003 to "history is per-entity," not "history capture is best-effort." Once an entity is declared history-carrying, capture must be inescapable from the call site, or the declaration is meaningless.
- **Consequences:** For history-carrying entities, the state mutation and the history record are atomic — a command cannot succeed without producing the history record, and cannot produce the history record without succeeding. Current state remains the system of record; reads consult the entity record directly. Audit-log-as-pattern remains in scope as a Step 5 menu option for entities whose accountability needs are explicitly best-effort, but it is an opt-in pattern with a documented tradeoff, not the framework default. The exact contents of the history record (full before/after, command + payload only, deltas) and reference-snapshotting behavior are deferred to Step 5. Implementation shape (event store / temporal tables / append-only history tables) deferred to Step 8.

---

## ADR-0009 — Lifecycle is specified per entity type as a declarative state machine; commands declare which transition they effect

- **Date:** 2026-04-30
- **Decision:** Each entity type with a lifecycle declares a state machine — a finite, named set of states plus the allowed transitions between them. Commands that effect a lifecycle transition declare the transition by name; the command pipeline validates the entity's current status against the state machine and rejects the command if that transition is not permitted from that state. Commands that do not affect lifecycle declare themselves non-lifecycle-affecting and bypass the state-machine check. Concrete lifecycle vocabularies per entity type are deferred to Step 6; Step 3 picks the shape, not the contents.
- **Status:** accepted
- **Context:** Step 3 needed to pick how lifecycle is specified. `framework.md` commits lifecycle status as the entity's own dimension and the primary axis for "what can happen to this thing next." ADR-0007 commits commands as the unit of change and the framework's attachment surface for cross-cutting concerns. The question for Step 3 is whether lifecycle is a separate declaration the pipeline consults, or is emergent from per-command logic.
- **Alternatives considered:**
  - *Guards as command preconditions, no central state machine.* Each command checks `if status == X` at execution time. Rejected — lifecycle becomes emergent; answering "what states can this entity be in?" requires walking every command. Inspectability and model-checkability of the lifecycle as a system property are lost. Conflicts with the framework's commitment that lifecycle status is the entity's own dimension, not one attribute among many.
  - *Imperative handlers — each command decides ad hoc.* Rejected — gives up consistency, vocabulary, and model-checkability. Effectively reduces lifecycle to "whatever each handler does," abandoning lifecycle-as-named-kind in the four-kind taxonomy.
- **Consequences:** Each entity type with a lifecycle has a single readable state-machine definition; rendering, model-checking (reachability, dead-end detection), and reviewing lifecycle as a system property are mechanical. Commands separate cleanly into lifecycle-affecting (which declare a named transition) and non-lifecycle-affecting (which do not). The pipeline check is inexpensive — given the entity's current status, a transition is either permitted or not. For entity types with no lifecycle, the state machine is a singleton; the declaration is mechanical, not ceremonial. ADR-0007 is honored: commands remain the effect/enforcement surface; the state machine is the declaration surface. The cost is a per-entity-type declaration in addition to the entity record itself; the benefit is that lifecycle is treatable as a first-class system property.

---

## ADR-0010 — Well-formedness invariants are declared on the schema element they constrain; enforcement is write-path only, in the command pipeline

- **Date:** 2026-04-30
- **Decision:** Atemporal (well-formedness) invariants are declared on the schema element they constrain — intra-entity invariants on the entity type; cross-entity invariants on the relationship type. Enforcement happens on the write path: every command revalidates relevant invariants for any entity it mutates and any relationship it touches, after applying the proposed change and before the transaction commits. On violation, the command is rejected (see ADR-0011). Persistence-isolation concerns for cross-entity invariants under concurrency are deferred to Step 8.
- **Status:** accepted
- **Context:** Step 3 needed to decide where well-formedness invariants live and where they are enforced. The Step 3 prompt framed this as one decision, but it has two distinct sub-questions: declaration site and enforcement layer. ADR-0007 commits commands as the framework's only logic-layer write surface; ADR-0008 commits to atomic state-mutation/history-capture for history-carrying entities. Both pin enforcement to the command pipeline; neither says where invariants are *declared*.
- **Alternatives considered:**
  - *Declare invariants on commands.* Each command that mutates a given entity declares its own invariant checks. Rejected — the same constraint would be re-declared on every command that touches the entity, with predictable drift between declarations. Duplicated reasoning at the declaration surface, even though enforcement is unified at the pipeline.
  - *Read-path-only enforcement.* Invalid state may persist; reads filter or warn. Rejected — conflicts directly with ADR-0007's commitment that a successful command leaves the system in a valid state, and with ADR-0008's history-capture invariant (a captured history record describing an invalid state is meaningless).
  - *Both-layer enforcement (defense in depth).* Enforce on both write and read paths. Rejected as the framework default — two definitions of an invariant drift; the cost of two surfaces outweighs the marginal benefit of redundant framework-level enforcement. Specific patterns may opt in where the use case warrants it; they are not the framework rule.
- **Consequences:** Invariants live next to the schema element they constrain — entity types own their well-formedness rules; relationship types own their cross-entity rules. Commands do not duplicate invariant declarations. The pipeline check happens after the proposed change is applied, before the transaction commits; on failure, the command is rejected and no mutation persists. Cross-entity invariants under concurrency are guaranteed only insofar as the persistence layer provides sufficient isolation; the choice of isolation mechanism (serializable transactions, optimistic locking, advisory locks) is a Step 8 concern. The framework commits to *where* the check happens, not to *what isolation guarantee* the persistence layer must provide.

---

## ADR-0011 — A command that would violate a lifecycle rule or well-formedness invariant is rejected; no mutation, no history record

- **Date:** 2026-04-30
- **Decision:** When a command would violate a lifecycle rule (per ADR-0009) or a well-formedness invariant (per ADR-0010), the framework rejects the command. No state mutation is persisted. No history record is written, regardless of whether the target entity is history-carrying. The caller receives a rejection reason. This is the framework default. Quarantine — applying the command but isolating the affected entity in a side state — is preserved as a deferred per-entity pattern, not the framework default; whether to commission it as a pattern is left for a later step.
- **Status:** accepted
- **Context:** Step 3 needed to specify what happens when a command would violate a lifecycle rule or well-formedness invariant. ADR-0007 commits commands to a binary outcome (rejected with a reason, or applied — producing the new state and, where applicable, the history record). ADR-0008 commits the state mutation and history record to atomicity for history-carrying entities. The violation-handling decision determines whether either ADR is honored under failure. State-level divergence between expected and actual outcomes (e.g., a parent entity whose end-state diverges from a baseline set elsewhere) is a separate concern modeled as state via `framework.md`'s four-kind taxonomy; this ADR addresses framework-declared rule and invariant violations only.
- **Alternatives considered:**
  - *Error-with-allow.* Apply the proposed change, attach an error, persist the result. Rejected — directly conflicts with ADR-0007's binary outcome and ADR-0008's atomicity. A state mutation that "succeeded with errors" is exactly the in-between outcome both ADRs were written to forbid.
  - *Warn.* Apply, log a warning, no error returned. Rejected — equivalent to no enforcement. Persisting a known-invalid state silently is the failure mode the entire invariant declaration apparatus exists to prevent.
  - *Quarantine.* Apply the change but isolate the affected entity in a side state, preventing further normal operations until reviewed. Rejected as the framework default — has real use cases (data ingestion, bulk imports, eventual-consistency scenarios where partial validity is preferable to total rejection), but adds machinery (a quarantine state coexisting with each entity's lifecycle) that not all entities need, and conflicts with concrete lifecycle vocabularies being deferred to Step 6. Preserved as a deferred per-entity pattern, analogous to how audit-log-as-pattern is preserved in ADR-0008's framework as a Step 5 menu option for entities with explicitly best-effort accountability — available if a specific entity's accountability or ingestion characteristics warrant it, but not commissioned at this step.
- **Consequences:** Command rejection is structurally consistent with the binary-outcome and atomic-capture commitments. A rejected command produces nothing — no entity-record change, no history record, no partial side effect. The rejection reason is the only output the caller sees. Quarantine remains in the option space for a future step (most plausibly Step 5 if it fits the auditing-pattern shape, or a later step otherwise); it is not part of the framework default and does not appear in any entity's command pipeline by default. Whether quarantine becomes a per-entity pattern, and on what criteria, is a question for whichever step picks it up.

---

## ADR-0012 — Authorization predicates are declarative expressions over (caller, command, target), declared per command, evaluated first in the pipeline

- **Date:** 2026-05-01
- **Decision:** Authorization is a declarative predicate over `(caller, command, target)`, declared on each command. The predicate may reference caller properties (including role assignments), target properties (including lifecycle status), and caller-target relationships (typed references per `framework.md`). The pipeline evaluates authorization before lifecycle checks, state application, and invariant validation. Concrete roles, relationships, and per-command predicates are deferred to Step 6.
- **Status:** accepted
- **Context:** Step 4 needed to pick the authorization shape — the primary axis (what determines access), where the predicate is declared, and in what form. The framework already commits commands as the unit of change (ADR-0007) and the attachment surface for cross-cutting concerns; lifecycle (ADR-0009) and invariants (ADR-0010) attach to this surface declaratively. Authorization is the third cross-cutting concern. The choice must work for both role-based and relationship-based access patterns without committing to either exclusively, since the domain's actual access patterns are unknown until Step 6.
- **Alternatives considered:**
  - *Sub-question 1 — Primary axis:*
    - *RBAC (role-based).* Rejected — cannot naturally express relationship-based access ("the owner of entity X can edit X") without grafting relationship logic on top, at which point it is a hybrid that calls itself RBAC. The framework already has typed relationships (`framework.md`); ruling out relationship-based access at the framework level and adding it back per-command defeats the purpose of a framework-level decision.
    - *ReBAC (relationship-based).* Rejected as the sole primary axis — overkill for commands where access is purely role-gated, and forces every authorization check through a relationship graph even when a simple role check suffices. Relationship-based access is subsumed by the predicate form without being the only mechanism.
  - *Sub-question 2 — Predicate location:*
    - *On entity types.* Rejected — authorization is inherently per-command (different commands on the same entity have different authorization requirements). Declaring on the entity type forces a default-plus-override pattern (two declaration sites), which ADR-0010 rejected for invariants for the same structural reason.
    - *Separate policy layer.* Rejected — introduces a third artifact disconnected from both commands and entities. The framework has consistently placed declarations next to the thing being constrained; a separate policy artifact breaks that pattern without compensating benefit at this abstraction level.
  - *Sub-question 3 — Form:*
    - *Imperative (code in handlers).* Rejected — makes the authorization surface opaque. Answering "who can execute command X?" requires reading handler code. Inconsistent with the declarative pattern the framework has established for lifecycle (ADR-0009) and invariants (ADR-0010). The gap widens when predicates combine roles, relationships, and target state — exactly what the predicate-over-(caller, command, target) axis invites.
- **Consequences:** Authorization is the third declarative cross-cutting concern on the command pipeline, alongside lifecycle (ADR-0009) and invariants (ADR-0010). The predicate vocabulary — caller roles, caller-target relationships, target properties, logical connectives — is extensible at the framework level; the domain fills in concrete values at Step 6. The pipeline now has a defined evaluation order: authorization → lifecycle → apply → invariants → commit, with rejection at any step producing no mutation and no history record (per ADR-0011). Static analysis of the authorization surface is possible: "which commands can caller C execute?" and "who can execute command X on entity E?" are queries over predicate definitions. The predicate form subsumes RBAC and ReBAC as special cases; the domain is free to use whichever inputs are natural per command without a framework-level bias toward either.

---

## ADR-0013 — Four history patterns with per-entity selection; lifecycle capture refines ADR-0008's scope

- **Date:** 2026-05-01
- **Decision:** Define four history patterns as the per-entity menu required by ADR-0006: (1) no history, (2) audit log, (3) comprehensive capture, (4) lifecycle capture. Every entity defined at domain-mapping time must select exactly one. Patterns 1 and 2 are not history-carrying per ADR-0008; patterns 3 and 4 are. For history-carrying patterns, capture scope is declared at entity-definition time: comprehensive capture produces a history record for every command; lifecycle capture produces records only for lifecycle-affecting commands (using the same lifecycle/non-lifecycle declaration ADR-0009 requires). Within the declared scope, capture is mandatory and framework-enforced per ADR-0008. Selection criteria are documented alongside the patterns in `planning/history-patterns.md`. References in history records are typed UUIDs — no snapshots of referenced entities. Pattern promotion (lighter → heavier) is forward-only; past changes are irrecoverable. Quarantine is excluded from the history-pattern menu — it is a violation-handling concern orthogonal to history, and remains deferred per ADR-0011.
- **Status:** accepted
- **Context:** Step 5 needed to produce the menu of history patterns that ADR-0006 requires before domain mapping. ADR-0008 established mandatory capture as the framework mechanism for history-carrying entities; ADR-0006 established that history is a per-entity decision. The menu must offer at least two substantively different history-carrying options (per Step 5's brief), plus "no history" as an explicit option, and must address the audit-log pattern that ADR-0008 preserved as a Step 5 concern. Four open questions were on the table: reference snapshotting, promotion path, record contents per pattern, and quarantine.
- **Alternatives considered:**
  - *Single history-carrying pattern (comprehensive capture only).* Rejected — forces a binary choice between "full capture of everything" and "no capture." Entities with accountable lifecycles but high-frequency, low-stakes attribute edits would pay disproportionate overhead. The lifecycle-capture pattern fills this gap without reverting to best-effort.
  - *Lifecycle capture as a content variation (every command still produces a record, but non-lifecycle records are metadata-only).* Considered as a way to preserve ADR-0008's literal "every command writes a record" language. Rejected — producing empty or metadata-only records for non-lifecycle commands is structurally indistinguishable from not producing them, adds storage and pipeline overhead with no accountability benefit, and obscures the pattern's actual promise. Narrowing capture scope to lifecycle-affecting commands is cleaner and more honest about what the pattern commits to.
  - *Snapshot referenced entities in history records.* Rejected — creates coupling between the history-recording entity and the referenced entity's schema. Per-entity history (ADR-0006) means each entity owns its own history. If you need past state of a reference, consult the referenced entity's own history chain. The tradeoff is explicit and should influence the referenced entity's pattern selection.
  - *Exclude audit log from the menu.* Rejected — ADR-0008 explicitly preserved audit log as a Step 5 pattern for entities with best-effort accountability needs. Excluding it would leave a gap between "no history" and "mandatory capture" with no option for lightweight observability.
  - *Include quarantine in the history-pattern menu.* Rejected — quarantine governs what happens on command failure (violation handling), not what successful commands record (history). It is orthogonal to all four history patterns. Including it here conflates two independent per-entity decisions.
- **Consequences:** The menu is set: four patterns, two tiers (not history-carrying, history-carrying), with selection criteria documented. Step 6 must assign one pattern to every entity — no entity definition is complete without it. Lifecycle capture refines ADR-0008: "a successful command writes a history record" now reads "a successful command within the pattern's declared capture scope writes a history record." The refinement is narrow — only lifecycle capture uses a narrowed scope; comprehensive capture preserves ADR-0008's original "every command" semantics. Reference snapshotting is settled: typed UUIDs only, no denormalized copies. Entities frequently referenced by history-carrying entities may warrant heavier history patterns than their own accountability needs suggest — this is a selection-criteria consideration, not a framework mandate. Promotion is forward-only; past history is irrecoverable. History implementation shape (snapshots vs. deltas vs. temporal tables) remains deferred to Step 8.
