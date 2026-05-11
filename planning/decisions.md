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

---

## ADR-0014 — Document and RequiredDocument unified into a single entity with a slot-spanning lifecycle

- **Date:** 2026-05-01
- **Decision:** The conceptual distinction between a "required document slot" (the spec/expectation that a document is needed) and the "document file" (the actual artifact) is modeled as a single Document entity with a lifecycle that spans both stages. There is no separate RequiredDocument entity.
- **Status:** accepted
- **Context:** Early modeling had two candidates: a RequiredDocument entity (the slot — "this document is needed") and a Document entity (the file — "this document exists"). The slot and the file refer to the same identity — a document that is needed, then prepared, then submitted. Splitting them creates an artificial join and forces lifecycle coordination between two entities that track the same thing.
- **Alternatives considered:**
  - *Two entities (RequiredDocument + Document).* Rejected — the slot and the file are two stages of the same identity, not two things. Splitting forces a 1:1 join and duplicates lifecycle tracking. The promotion criterion from ADR-0004 does not fire — there is no independent state on the "requirement" that isn't better modeled as early lifecycle states on the Document itself.
- **Consequences:** Document's lifecycle includes states that predate the file's existence (e.g., `outstanding`, `not_required`). A Document can exist as a "needed but not yet prepared" slot. Entity count is reduced by one. Set-based derivation (see ADR-0015) governs whether a Document slot exists.

---

## ADR-0015 — Document existence is governed by a derivation set; documents are not owned by WA Codes

- **Date:** 2026-05-01
- **Decision:** A Document's existence and "required" status is governed by a derivation set — the collection of sources (WA Codes, project events) that imply the document is needed. Documents have a many-to-many relationship with their derivation sources. A Document persists as long as its derivation set is non-empty; it transitions to `not_required` (with history preserved) when the set becomes empty. Documents are not owned by any single WA Code.
- **Status:** accepted
- **Context:** Documents in the domain are implied by contractual scope (WA Codes) and project events, not created by a single parent. A WA Code addition may imply several documents; a single document may be implied by multiple WA Codes. WA Code removal (via RFA/Amendment) should not delete documents that are still implied by other sources. The ownership model (document belongs to one WA Code) fails under amendment scenarios where scope shifts between codes.
- **Alternatives considered:**
  - *Document owned by a single WA Code (1:M).* Rejected — breaks when a document is implied by multiple codes, or when a code is removed but the document is still needed for other reasons. Deletion/orphan semantics become fragile under amendment workflows.
  - *Document existence is manually managed (no derivation).* Rejected — forces the Tracker to manually track which documents are needed as scope changes, which is exactly the bookkeeping the system should handle.
- **Consequences:** The derivation set is the source of truth for "is this document needed." WA Code add/remove deltas the derivation set. Derivation-set emptiness triggers `not_required` transition, not deletion — history is preserved per the Document's history pattern. The many-to-many relationship between Documents and derivation sources does not carry independent state (no promotion to entity per ADR-0004). Amendment WA issuance (not RFA submission) is the point at which derivation-set deltas are applied.

---

## ADR-0016 — WA is supersedable via approved RFA; full version chain preserved

- **Date:** 2026-05-01
- **Decision:** An approved RFA produces an Amendment WA that supersedes the current WA. The full version chain (Initial WA → Amendment WA₁ → Amendment WA₂ → …) is preserved. The supersession mechanism and whether it uses a self-reference on WA or a separate version entity is an open question resolved later in this session.
- **Status:** accepted
- **Context:** Work Authorizations in the domain are amended through a formal Request for Amendment process. The original WA's terms (budget, scope, codes) are replaced by the amendment's terms, but the original must remain accessible for audit, billing reconciliation, and historical queries. The amendment is not a patch — it is a new WA that replaces the prior one.
- **Alternatives considered:**
  - *Mutate the WA in place (no versioning).* Rejected — destroys the prior terms. Billing, audit, and temporal rate resolution (design pattern from 6a-i) require knowing what the WA said at a given point in time.
  - *Version via change log on a single WA record.* Rejected — conflates the WA's own history pattern with version identity. An Amendment WA is a distinct contractual document, not an edit to the original. The version chain is a domain concept (contractual succession), not a history-capture concern.
- **Consequences:** WA carries a version chain. The current (non-superseded) WA is the active one; superseded WAs are immutable but queryable. Derivation-set deltas (ADR-0015) are applied at Amendment WA issuance. The specific versioning mechanism (self-reference vs. separate entity) is resolved in ADR-0017.

---

## ADR-0017 — WA supersession uses a self-reference; no separate version entity

- **Date:** 2026-05-09
- **Decision:** WA carries a nullable `supersedes` typed reference to another WA. An Amendment WA points at the WA it replaces. The version chain is a linked list: Amendment₂ → Amendment₁ → Initial (where Initial has `supersedes = null`). The current (active) WA for a project is the one not superseded by any other WA. Superseded WAs are immutable — no commands can mutate a superseded WA (enforced as an invariant per ADR-0010). WA also carries a `version_type` attribute (`initial` vs. `amendment`) and an `effective_date`.
- **Status:** accepted
- **Context:** ADR-0016 established WA supersession via approved RFA but left the mechanism as an open question: self-reference on WA vs. a separate WA Version entity. This ADR resolves it.
- **Alternatives considered:**
  - *Separate WA Version entity.* Rejected — an Amendment WA has the same attributes (budget, codes, terms), lifecycle, and relationships as a WA. A Version entity would be a parallel structure mirroring WA in every way, with its own history-pattern decision, commands, and lifecycle — all delegating to the underlying WA. It is indirection without payoff. The self-reference is a single nullable field; the version chain is navigable by pointer traversal.
- **Consequences:** WA's schema gains three fields: `supersedes` (nullable typed reference to WA), `version_type` (`initial` | `amendment`), `effective_date`. "Find the current WA" = find the WA for this project where no other WA's `supersedes` points at it. No additional entity. The immutability invariant on superseded WAs prevents editing historical contractual terms.

---

## ADR-0018 — Note is a polymorphic commentary entity attachable to any entity

- **Date:** 2026-05-09
- **Decision:** Note is a standalone entity with a polymorphic typed reference `(entity_type, entity_id)` attachable to any entity. Notes accumulate over time as contextual commentary. Intrinsic attributes: `message`, `created_by` (→ User), `created_at`, `edited_at`, target reference. The `edit_note` command is restricted to the note's creator (authorization predicate: `caller == note.created_by`). Edited notes are flagged via `edited_at` timestamp. Notes are not deletable. No lifecycle. No history.
- **Status:** accepted
- **Context:** Document responsibility tracking required more than a single text field. Blockers evolve over time — e.g., "waiting on contractor" → "spoke to contractor on date 1" → "spoke to contractor on date 2" → "resolved after several attempts." A single `blocker_note` field can only hold one value; overwriting it loses the trail. The same commentary pattern applies across entity types (Documents, Deliverables, RFAs, Projects).
- **Alternatives considered:**
  - *Single `blocker_note` text field on Document.* Rejected — can hold one note at a time, does not support threaded commentary for evolving situations. Document's comprehensive history captures prior field values, but presents them as a history chain, not a readable thread. Also scoped to Document only.
  - *Note scoped to Documents only (foreign key instead of polymorphic reference).* Rejected — the same commentary pattern applies to other entity types. Starting with `document_id` and generalizing later requires a schema change. A polymorphic reference `(entity_type, entity_id)` costs nothing structurally and avoids the retrofit.
- **Consequences:** Note is added to the entity roster (15 entities total). The polymorphic reference enables commentary on any entity. Creator-only editing and non-deletability preserve the integrity of the commentary trail. No history pattern needed — the note itself is the historical record; immutability (except for creator typo edits) means there is no state to reconstruct. `edited_at` provides transparency about edits without full edit history, relying on user trust for good-faith corrections.

---

## ADR-0019 — Entity roster refined: Sample, Inspection, and Daily Log dropped; Final Project Package is derived state

- **Date:** 2026-05-09
- **Decision:** Drop Sample, Inspection, and Daily Log from the entity roster. Merge Daily Log into Document as a document type. Confirm Final Project Package as derived state on Project, not an entity. Roster moves from 17 (6a-i) + 1 (Note, ADR-0018) to 15 entities.
- **Status:** accepted
- **Context:** During the history-pattern walk and modeling review in 6a-ii, four candidates were evaluated against the entity identity test (ADR-0002) and the principle that entities should carry independent, mutation-surviving identity.
- **Alternatives considered:**
  - *Sample as entity.* Rejected — the system tracks sample quantities and types for billing, not individual samples. Individual samples don't have identity-over-mutation; they are line items counted in aggregate. Sample Batch carries composition as a structured value `[{subtype, quantity}]`. Sample Type and Sample Subtype remain curated vocabulary values. Batch composition invariant: PCM/TEM batches require a single subtype; Bulk batches allow mixed subtypes.
  - *Inspection as entity.* Rejected — imposes a "visit" grouping on field activities that don't need it. Whether multiple site visits constitute one or multiple inspections is an irrelevant distinction. Time Entry, Sample Batch, and Documents (daily logs) correlate naturally by site + date without a wrapper entity. No independent state on the visit beyond what its constituent records already carry.
  - *Daily Log as separate entity.* Rejected — daily logs are narrative reports that function as required documents on a project. Modeling as a Document type leverages the existing Document entity with its derivation-set governance (ADR-0015), comprehensive history, and file-upload capability. Date-gap detection (missing logs for days with time entries) is a user responsibility managed through Notes, not an automated system invariant.
  - *Final Project Package as entity.* Rejected — it is a generated PDF artifact (merged uploaded documents + generated billing documents) available when a project is closed. No identity-over-mutation; readiness is computed from Document/Deliverable state. The `close_project` command on Project is gated on a derived readiness condition (cross-entity acknowledgement gating pattern per `logic.md`).
- **Consequences:** Entity count reduced. Sample Batch is the sole sample-tracking entity; billing uses batch composition + temporal rate lookup `(subtype, TAT) → rate`. Daily logs participate in the Document lifecycle and derivation-set model. Inspection's absence means field activities are queried by site + date, not by a grouping ID. Final Project Package generation is a read-side operation triggered by project closure, not a command on an entity.

---

## ADR-0020 — WA Code is project-scoped; WA authorizes codes but does not own them

- **Date:** 2026-05-10
- **Decision:** WA Code references Project, not WA. A WA Code is a project-level scope item whose identity persists across WA versions. The WA authorizes codes and sets their budgets, but the codes are not owned by any specific WA version. Rate resolution for time entries comes from EmployeeRole (temporal rate per ADR-0019's design patterns), not from WA Code or WA. Sample billing uses the deferred `(subtype, TAT) → rate` lookup. WA Code carries: code identifier, description, scope level (project or building), budget (from WA authorization), and derivation rules.
- **Status:** accepted
- **Context:** The use-case stress test (Step 6a-iii) walked through "samples arrive before the WA is issued" and surfaced the question of whether WA Code belongs to a specific WA version or to the Project. The WA supersession model (ADR-0017) creates a new WA entity for each amendment. If codes are WA-scoped, codes are duplicated across versions, Time Entry references are frozen to a specific WA version, and queries like "how many hours on code X?" must aggregate across versions. The user confirmed that only the latest WA is relevant — the tracker asks about a code across all time, not per WA version.
- **Alternatives considered:**
  - *WA Code scoped to a specific WA (WA Code → WA).* Rejected — creates duplicate code entities across WA versions. Time Entries from before an amendment reference codes on the superseded WA; new entries reference codes on the Amendment WA. "Code PCM-001 on WA v1" and "Code PCM-001 on WA v2" are different entities with different UUIDs representing the same conceptual scope item. Queries require cross-version aggregation. The duplication adds complexity without reflecting domain reality — the code is the same thing across amendments.
- **Consequences:** WA Code → Project (not WA Code → WA). The WA ↔ WA Code relationship is authorization, not ownership — the WA declares which codes are authorized and at what budget, but doesn't own the codes. When a WA is superseded, codes persist unchanged; the new WA's authorization terms apply. Budget on a code reflects the current WA's terms. Time Entry and Sample Batch reference the code directly; the code's identity is stable across WA versions.

---

## ADR-0021 — WA Code carries a lifecycle; promoted from no-history to lifecycle capture with soft delete

- **Date:** 2026-05-10
- **Decision:** WA Code has a lifecycle tracking authorization status. Concrete state names are deferred to Step 6b, but the stress test established at minimum: `expected` (anticipated but WA not yet issued), `issued` (confirmed on an issued WA), `pending_RFA` (not on the issued WA, RFA needed), and `dismissed` (tracker decided the code isn't needed). WA Code is promoted from no-history to lifecycle capture (ADR-0013 pattern 4). Delete policy changes from hard delete to soft delete.
- **Status:** accepted
- **Context:** The stress test surfaced that WA Code is not a static lookup. It tracks authorization status over time — codes are created as expectations, confirmed or flagged when the WA is issued, and may be dismissed. These lifecycle transitions are accountability-relevant: "who confirmed this code?" and "when was it flagged for RFA?" are real questions. The lifecycle capture decision tree (ADR-0013) asks "must lifecycle transitions be formally attributable?" — yes, for WA Code's authorization transitions.
- **Alternatives considered:**
  - *Keep WA Code at no-history.* Rejected — WA Code's lifecycle transitions (especially `pending_RFA` and `dismissed`) are decisions that should be attributable. The WA's comprehensive history captures WA-level events but not per-code authorization status changes, since codes are now project-scoped (ADR-0020) and not owned by the WA.
  - *Promote to comprehensive capture.* Rejected — WA Code's intrinsic attributes (code identifier, description, scope level) change rarely and are low-stakes. Lifecycle capture covers the accountable transitions without adding overhead for routine attribute edits.
- **Consequences:** WA Code joins the lifecycle-capture tier: lifecycle-affecting commands produce mandatory history records; non-lifecycle commands do not. The history-pattern assignment table is updated (WA Code moves from "No history" to "Lifecycle capture"). Delete policy moves from hard to soft (history records reference the code; hard delete would orphan them). WA Code's lifecycle is simple but accountable — the RFA entity's comprehensive history provides the detailed audit trail for the amendment workflow, while the code's lifecycle capture records the status transitions themselves.

---

## ADR-0022 — Document and Deliverable derivation fires on expected WA Codes; code issuance cascades lifecycle transitions

- **Date:** 2026-05-10
- **Decision:** Document and Deliverable derivation (ADR-0015) fires when WA Codes are in `expected` state, not only when `issued`. Document and Deliverable slots appear as soon as a WA Code exists, regardless of authorization status. Deliverables derived from unissued codes begin their lifecycle in a pre-authorization state (e.g., `pending_RFA`); they transition to an actionable state (e.g., `outstanding`) when the code reaches `issued`. WA Code issuance is a compound command that atomically transitions the code and cascades lifecycle transitions to all derived Documents and Deliverables. Derived blocking status from WA Code authorization state is automatic and structural; operational blockers are user-initiated via Notes (ADR-0018).
- **Status:** accepted
- **Context:** The stress test established that field work (sample collection, time entry, document preparation) routinely begins before the WA is formally issued. If derivation only fires on `issued` codes, the system shows zero required documents during the pre-authorization period — a blind spot during the period when work is actively happening. The tracker needs to see "these documents will be needed" as early as possible. Additionally, WA Codes may be created bottom-up by smart commands (e.g., recording a time entry infers and creates a missing expected WA Code), further requiring that derivation fires immediately on code creation.
- **Alternatives considered:**
  - *Derivation fires only on `issued` codes.* Rejected — creates a blind spot during the pre-WA period. The system cannot show required documents, track preparation progress, or surface blocking status until the formal WA arrives. This defeats the purpose of allowing pre-WA work tracking.
  - *Deliverable lifecycle not gated by code status (Deliverables are always actionable).* Rejected — a Deliverable submitted to the SCA portal for unauthorized work is operationally invalid. The tracker confirmed that Deliverables cannot be submitted without an issued code. The `pending_RFA → outstanding` transition enforces this structurally.
- **Consequences:** The system is useful from the moment work begins. Document and Deliverable slots appear incrementally as scope is discovered (top-down from tracker setup or bottom-up from work recording). Deliverables have a pre-authorization lifecycle phase gated by code status. Code issuance is a compound command with cascading effects — one command on WA Code triggers transitions on related Documents and Deliverables (per ADR-0007, multi-step atomic operations are themselves commands). Derived blocking status (from code authorization state) and operational blocking (from Notes) are independent, both visible, complementary signals.

---

## ADR-0023 — DepFiling entity for regulatory filing bundles; editable required-doc set, no persisted filing-type

- **Date:** 2026-05-11
- **Decision:** Add DepFiling as the 16th domain entity. A DepFiling is a regulatory filing bundle identified by a TRU number, project-scoped (1:M Project → DepFiling). Its primary state is an editable `required_doc_types` set, seeded at creation time from a UI-side template (Regular: `[ACP13, ACP7, ACP15, ACP21]`; Emergency: `[Emergency Notification, ACP13, ACP7, ACP15, ACP21]`). Templates are constants in client code, not persisted on the entity. DepFiling has no lifecycle of its own; its completeness is a derived predicate over the state of its required Documents. DepFiling serves as a Document-derivation source per ADR-0015 (1:M DepFiling → Document, not M:M). Documents derived from a DepFiling default to the simple `missing → saved` lifecycle. DepFiling's history pattern is deferred to the next 6b session.
- **Status:** accepted
- **Context:** The system tracks regulatory submissions ("notification filings," internally identified by TRU numbers) whose constituent documents must be present in the project closeout package. These groupings are not Deliverables — no SCA-portal submission, no own lifecycle, 1:M with Documents rather than M:M — but they are also not just freestanding documents: each TRU number identifies a coherent bundle whose required document set differs from the project's other docs and can be edited by the user as scope evolves. The required documents (ACPs and others) are *issued* externally, not generated, so anything received is required by definition.
- **Alternatives considered:**
  - *Filings as additional document types without a grouping entity.* Rejected — the TRU number is identity-bearing (the regulator's identifier for the filing) and a project may carry multiple filings whose required-doc sets differ. Without an entity, the TRU has no home and the required-doc set has no parent.
  - *Persist `filing_type` (Regular/Emergency) as an attribute on DepFiling.* Rejected — templates exist only to seed the `required_doc_types` set at creation; once seeded, the set is freely editable (e.g., a filing opened as Emergency may have its Emergency Notification removed if reclassified). A persisted `filing_type` would add a redundant axis that can drift from the actual required-doc set, when the actual set is the source of truth. "Which filings included an Emergency Notification?" is answered by querying `required_doc_types ∋ "Emergency Notification"`.
  - *M:M between DepFiling and Document.* Rejected — each derived document belongs to exactly one filing (an Emergency Notification doc filed under TRU-12345 is not shared with TRU-67890). 1:M derivation is the natural shape, parallel to WA Code → Document.
- **Consequences:** Entity roster grows 15 → 16. DepFiling joins WA Code as a Document-derivation source under ADR-0015. `remove_required_doc_type(filing, doc_type)` carries a transition invariant: rejected when the corresponding Document is in `saved` state — issued documents that have been received are, by definition, required and cannot be unrequired. Project closure gates on all DepFiling required Documents being in `saved` state (cross-entity acknowledgement gating per established pattern). DepFiling has no state machine; "completeness" is derived. History pattern selection (audit log for "who built the filing" vs no history) is deferred.

---

## ADR-0024 — Document lifecycle dispatches per `document_type` from a three-pattern menu; cycling-family is parameterized

- **Date:** 2026-05-11
- **Decision:** Document's lifecycle is dispatched per `document_type` discriminator. The discriminator selects from a fixed three-option menu:
  1. **Simple** — `missing → saved`. Default for issued, externally authored, or upload-and-done docs.
  2. **Cycling-family** — a single parameterized state machine handling draft/review/approve workflows. Parameters: `base_state`, `external_pushback` boolean, ordered `buckets[]` (each with name, submit-date field, ordered review-steps [reviewer-role + reviewed-date field], and `on_full_approval ∈ {terminal, loop_to_base}`).
  3. **Bespoke** — declare a new state machine. Escape hatch for shapes that fit neither.

  Adding a new tracked doc type is a code-time change: register the `document_type` value, pick a pattern (or supply a bespoke state machine), attach derivation source(s) per ADR-0015, declare commands and authorization predicates (ADR-0012) for non-trivial transitions.
- **Status:** accepted
- **Context:** Step 6b's opening question was whether document types beyond CPR (cycling) and simple docs (`missing → saved`) require their own state machines. The user confirmed that all observed draft/review/approve workflows share CPR's topology with different labels and review-chain shapes (and the same property that "approved" is hopefully-but-not-strictly terminal — external pushback can rewind any approved doc). A single parameterized cycling state machine subsumes them, with the bespoke option preserved for genuinely novel shapes. The discriminator dispatch itself was validated in the prior session (6b partial, CPR walkthrough); this ADR formalizes the menu, the parameter schema, and the code-time extensibility contract.
- **Alternatives considered:**
  - *Single state machine for all Documents.* Rejected previously (god-entity problem); discriminator dispatch is the established model.
  - *Distinct cycling state machines per type (one declaration per cycling doc type).* Rejected — different labels and review chains but identical topology mean N copies of the same logic with predictable drift between them. Parameterization centralizes the shape.
  - *Runtime-configurable state machines (UI for end-user authoring).* Rejected — significant engineering lift (reachability validation, schema evolution for in-flight entities, UI machinery) and the rate of new doc types in this domain is slow enough that code-time extension fits the operational tempo.
  - *State machines as data tables (config-driven indirection).* Considered but not chosen — the parameter schema is small enough that direct in-code declarations per `document_type` are clearer than a data-driven indirection layer.
- **Consequences:** The `document_type` registry is the single source of truth for which lifecycle pattern (and parameters) applies where. Document remains a single entity (ADR-0014) with per-type dispatch. Adding a cycling-family doc type is parameter supply, not state-machine authoring. CPR validates parameter coverage: 2 buckets (RFA, RFP), a 2-step review chain on RFA (`contractor_manager → sca`, `on_full_approval: loop_to_base`), a 1-step review chain on RFP (`contractor_manager`, `on_full_approval: terminal`), and 5 tracking dates falling out naturally. Bucket names are baked into command names to disambiguate the surface (e.g., `submit_rfa` vs. `submit_rfp`, `contractor_manager_approve_rfa` vs. `contractor_manager_approve_rfp`). Per-`document_type` pattern assignments accumulate as doc types are confirmed (next session continues this). Project structure for managing N document types as the registry grows is deferred to implementation phase (potentially Step 8 or first implementation step).
