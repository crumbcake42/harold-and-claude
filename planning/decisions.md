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

---

## ADR-0025 — DepFiling carries audit log; delete policy is soft delete

- **Date:** 2026-05-11
- **Decision:** DepFiling's history pattern is audit log (ADR-0013 pattern 2). Best-effort accountability for filing-bundle construction — every command on a DepFiling produces an audit-log record (who, when, command + payload), but the entity is not history-carrying (no atomic capture, no point-in-time reconstruction). Contextual commentary on filings uses Notes (ADR-0018, polymorphic). Delete policy: soft delete.
- **Status:** accepted
- **Context:** ADR-0023 added DepFiling but deferred the history-pattern decision (and the dependent delete-policy decision). The accountability question for DepFiling is "who built this filing, with what required-doc set" — a real but bounded need. The filing's *completeness* is derived from its Documents (which carry their own history per ADR-0024), so DepFiling itself doesn't need point-in-time reconstruction. The mutable `required_doc_types` set evolves as scope is understood; an audit trail of those edits is enough.
- **Alternatives considered:**
  - *No history.* Rejected — the `required_doc_types` set is editable and `remove_required_doc_type` carries a structural invariant (ADR-0023). Edits to this set are accountability-relevant; losing them entirely would make filing-construction disputes unresolvable.
  - *Lifecycle capture.* Rejected — DepFiling has no lifecycle of its own per ADR-0023 (completeness is derived). Lifecycle capture without a lifecycle to capture collapses to "capture nothing," which is the no-history pattern.
  - *Comprehensive capture.* Rejected — accountability needs are bounded (filing-construction edits, not full schema reconstruction). Comprehensive overshoots; audit log fits the actual need and matches the "no own lifecycle, but mutable bundle definition" shape.
- **Consequences:** DepFiling joins the audit-log tier (alongside Employee, User, Time Entry, Contractor). The audit log is best-effort — capture is not framework-enforced inside the command pipeline per ADR-0008. Delete policy moves from deferred to soft delete — Documents reference DepFiling (1:M per ADR-0023), and audit-log records reference DepFiling; hard delete would orphan both. The handoff tables (history-pattern assignments, delete-policy assignments) move DepFiling out of the "Deferred" row.

---

## ADR-0026 — Daily Log is a Document type; Time Entry → Daily Log is a nullable reference required at project closure

- **Date:** 2026-05-11
- **Decision:** Daily Log is a Document type with the simple `missing → saved` lifecycle (per ADR-0024's menu). Daily Log → Time Entry is 1:M, modeled as a nullable typed reference on Time Entry (`daily_log`). Time Entries can be created without a Daily Log link. Project closure carries a cross-entity invariant: every Time Entry on a closing Project must reference a Daily Log. Daily Logs are tracker-created — no automatic derivation from Time Entries; slot existence comes from manual creation when the tracker is ready to upload.
- **Status:** accepted
- **Context:** ADR-0019 dropped Daily Log as a separate entity and merged it into Document. ADR-0023's deferred questions included Daily Log lifecycle direction and derivation rule. The framing question was whether Time Entries imply Daily Logs derivationally (parallel to WA Code → Document, ADR-0015). User confirmed that logs cover variable date ranges (a log may span any number of days), so source-to-slot mapping isn't deterministic enough for derivation. However, every Time Entry should ultimately be accounted for by a Daily Log; the system enforces this at project closure rather than continuously.
- **Alternatives considered:**
  - *Time Entry as Document-derivation source (parallel to WA Code, DepFiling).* Rejected — log coverage spans variable date ranges; no deterministic mapping from time entries to slot count.
  - *No relationship at all (Daily Logs and Time Entries are independent; coverage is tracker-eyeballed).* Rejected — closure-time validation that all work has narrative coverage is an accountability requirement; eyeballing produces no machine-checkable invariant.
  - *M:M Daily Log ↔ Time Entry (a time entry split across multiple logs).* Rejected — operationally a time entry's narrative belongs to one log. Finer granularity (per-page Daily Log assignment to Time Entries) is post-MVP, see `post-mvp.md`.
- **Consequences:** Time Entry schema gains a nullable `daily_log` typed reference. Two new commands on Time Entry: `link_to_daily_log` and `unlink_from_daily_log` (the latter for corrections). Project closure invariant adds another cross-entity acknowledgement gate (alongside DepFiling completeness from ADR-0023 and existing closure gates). Daily Log slot creation is manual; the tracker adds a Daily Log Document, uploads the file, and links Time Entries to it. Visual review of Time Entries against Daily Log pages (page-level cross-referencing) is post-MVP.

---

## ADR-0027 — WA Code concrete state machine, dismiss cascade, and closure-blocker acknowledgement pattern

- **Date:** 2026-05-12
- **Decision:** WA Code's concrete state machine has six states: `expected`, `pending_rfa`, `rfa_in_review`, `issued`, `budget_rfa_needed` (deferred placeholder), and `dismissed`. `dismiss_wa_code` cascade-unlinks `wa_code` references on all referencing Time Entries and Sample Batches; null `wa_code` derives a `non_billable` flag on those records; a per-record `acknowledged` flag resolves the resulting closure blocker. `rfa_in_review` is a locked state — no dismissal while an RFA is under review; the RFA must resolve first.
- **Status:** accepted (the `acknowledged: bool` field aspect is superseded by ADR-0032; state machine and dismiss cascade survive)
- **Context:** ADR-0021 established WA Code's lifecycle at placeholder level, deferring concrete state names and transitions to Step 6b. The dismiss-cascade direction was decided in the prior session (6b-s3) but not yet ADR-written, pending resolution of the closure-blocker acknowledgement shape. Step 6b-s4 finalized the acknowledgement pattern (per-record flag, Option 1 from three candidates), unblocking this ADR.
- **Alternatives considered:**
  - *Allow dismissal from `rfa_in_review`.* Rejected — dismissing a code while its adding-RFA is in review creates an integrity hole: the RFA outcome (approved/rejected) would have no valid target state. The RFA must be rejected or withdrawn first, returning the code to `pending_rfa`, before dismissal is permitted.
  - *Project-level override list for closure-blocker acknowledgement.* Rejected — a second source of truth on the Project entity; drift risk between the list and the actual record states. The per-record flag makes the closure check a simple predicate over Time Entry and Sample Batch records.
  - *Note-based acknowledgement (ADR-0018 polymorphic Note with `is_closure_acknowledgement: true`).* Rejected — least machine-checkable; the closure gate would need to interpret Note contents rather than query a boolean flag.
- **Consequences:**
  - **State machine.** Six states with the following transitions:
    - `expected → issued`: auto-triggered by WA issuance reconciliation (ADR-0022) when the WA includes this code.
    - `expected → pending_rfa`: auto-triggered by WA issuance reconciliation when the WA does not include this code.
    - `expected → dismissed`: `dismiss_wa_code`; delete instead if no Time Entry or Sample Batch has ever referenced this code.
    - `pending_rfa → rfa_in_review`: auto-triggered when an RFA targeting this code is submitted.
    - `pending_rfa → dismissed`: `dismiss_wa_code`; delete instead if unreferenced.
    - `rfa_in_review → issued`: auto-triggered by RFA approval.
    - `rfa_in_review → pending_rfa`: auto-triggered by RFA rejection or withdrawal.
    - `issued → dismissed`: `dismiss_wa_code`.
    - `issued → budget_rfa_needed`: auto-triggered when budget is exceeded [deferred — requires budget tracking].
    - `budget_rfa_needed → rfa_in_review`: auto-triggered when a budget-amendment RFA is submitted [deferred].
    - `budget_rfa_needed → dismissed`: `dismiss_wa_code` [deferred].
  - **Dismiss cascade.** `dismiss_wa_code` is a compound command (ADR-0007): (1) transitions WA Code to `dismissed`; (2) nulls `wa_code` on all referencing Time Entries and Sample Batches; (3) the derived `non_billable` flag evaluates to true on each affected record; (4) each affected record becomes a closure blocker on its project unless `acknowledged` is true. Delete (hard) is substituted when no references ever existed — no cascade needed, no audit trail required.
  - **Closure-blocker acknowledgement pattern.** A per-record `acknowledged: bool` field on Time Entry and Sample Batch resolves the non-billable closure blocker. The flag can be set ad-hoc (tracker visits the record) or during the project closure batch-acknowledge flow (gate surfaces all unacknowledged blockers). This is the first instantiation of a general pattern: any structural closure invariant that the tracker may knowingly override is resolved by a per-record flag on the blocking entity, not by a project-level list or Note.
  - **`rfa_in_review` shared.** The state covers both "RFA to add a missing code" and "RFA to amend budget" — the distinction is visible in the RFA entity's own record (subject field), not in the WA Code state. The tracker does not need aggregate queries by RFA purpose.
  - **Budget states deferred.** `budget_rfa_needed` and its transitions are named placeholders. No implementation commitment is made until budget tracking is designed.

---

## ADR-0028 — Cross-project time overlap is a derived blocker; no conflict entity

- **Date:** 2026-05-12
- **Decision:** When the same employee has time ranges across two projects that overlap, this is a derived cross-project blocker. Neither project involved may close until the overlap is resolved. The blocker is derived from first principles — same `employee_id`, overlapping `(start_time, end_time)`, different `project_id` — and dissolves automatically when the structural condition is fixed. No separate entity tracks the conflict.
- **Status:** accepted
- **Context:** Step 6b surfaced a scenario where a Sample Batch's collection time (or a Time Entry range) for one project overlaps an existing Time Entry range for the same employee on a different project. If the blocker were project-scoped, one project could close first, finalizing and locking its time entries — making the conflict irresolvable when the second project is later picked up. The conflict must therefore block both projects simultaneously.
- **Alternatives considered:**
  - *Project-scoped blocker (only the project the ambiguous record lands on is blocked).* Rejected — allows the other project to close and lock its time entries, eliminating the possibility of resolution. The scenario confirms that cross-project scope is necessary.
  - *Named conflict entity (`TimeConflict`) linking the affected records.* Rejected — the conflict is fully derivable from the data; materializing it adds a record lifecycle (create, resolve, clean up) without buying anything the derived query doesn't already provide. Automatic dissolution on structural fix is cleaner than requiring explicit record deletion.
- **Consequences:** Project closure gate includes a check for unresolved cross-project time overlaps on any of the project's Time Entries or Sample Batches. The overlap check is a range query on `(employee_id, start_time, end_time)`; a composite index on those three columns is the implementation-time requirement (not a domain model decision). Resolution is structural: the tracker adjusts a time entry's range, re-assigns a batch, or splits an entry (per the `split_entry` command pattern discussed in session). The blocker dissolves without any explicit acknowledgement step — it either exists or it doesn't. The `acknowledged` flag pattern (ADR-0027) does not apply here: a cross-project overlap is not a state the tracker accepts and moves past; it must be resolved.

---

## ADR-0029 — Deliverable concrete state machine, wasted flag, and delete condition

- **Date:** 2026-05-12
- **Decision:** Deliverable has four states: `pending_rfa`, `outstanding`, `under_review`, and `approved`. Rejection and withdrawal from review return to `outstanding` (no separate returned state; history captures the path). A derived `wasted` flag fires when the WA Code is dismissed and the Deliverable has either prepared documents or a submission attempt on record. A Deliverable in `outstanding` with no prepared documents and no submission history is hard-deleted when its WA Code is dismissed.
- **Status:** accepted
- **Context:** ADR-0022 established `pending_rfa` and `outstanding` as placeholder states for Deliverable's pre-submission lifecycle. Step 6b-s4 filled in the submission flow. The key UX driver for keeping both pre-submission states distinct is tracker efficiency: `outstanding` is an actionable queue ("ready to upload"); `pending_rfa` is a blocked queue ("waiting on WA Code authorization"). Merging them forces the tracker to inspect each Deliverable individually to determine uploadability.
- **Alternatives considered:**
  - *Single pre-submission state (no `pending_rfa`).* Rejected — without the distinction, the tracker cannot filter to "uploadable now" without inspecting each Deliverable individually. The two states serve different queues.
  - *`returned` state for SCA rejection.* Rejected — `outstanding` is sufficient; the Deliverable is back in the actionable queue regardless of whether it was previously submitted. The lifecycle history (via lifecycle capture, ADR-0013) records the full path: `outstanding → under_review → outstanding`.
  - *`wasted` as a persisted terminal state.* Rejected — `wasted` is fully derivable from WA Code status and Deliverable history (documents prepared or submission attempted). A persisted state would require a cascade command from `dismiss_wa_code` and introduce a state with no outbound transitions, adding lifecycle overhead for a rare edge case.
- **Consequences:**
  - **State machine:**
    - `pending_rfa → outstanding`: auto-triggered by WA Code issuance (ADR-0022 compound cascade).
    - `outstanding → under_review`: `submit_deliverable` (manual tracker command).
    - `under_review → approved`: auto-triggered by SCA portal acceptance (or manual tracker confirmation).
    - `under_review → outstanding`: `reject_deliverable` (SCA rejection) or `withdraw_deliverable` (tracker withdrawal). Both return to the actionable queue; history distinguishes them.
  - **`wasted` derived flag.** Condition: WA Code is `dismissed` AND (`status ∈ {under_review, approved}` OR at least one bundled Document is in `saved` state). Visible in the UI; does not change the Deliverable's persisted state.
  - **Delete on dismissal.** When WA Code is dismissed and the Deliverable is `outstanding` with no prepared documents (all bundled Documents in `missing` state, no prior submission), the Deliverable is hard-deleted. No cascade, no wasted flag — no work was done.
  - **Submission invariant.** `submit_deliverable` is guarded: all bundled Documents must be in `saved` state. A Deliverable with missing documents cannot be submitted.

---

## ADR-0030 — WA concrete state machine and supersession-immutability invariant

- **Date:** 2026-05-12
- **Decision:** WA has three states: `pending` (not yet received from SCA), `issued` (received and recorded), and `superseded` (replaced by a newer WA version). `issue_wa` is a compound command that transitions WA to `issued` and runs WA Code reconciliation (ADR-0022), atomically resolving the full "limbo" derivation chain. A `superseded` WA is immutable — no commands or RFA filings are accepted against it.
- **Status:** accepted
- **Context:** ADR-0016 and ADR-0017 established WA versioning via supersession and the immutability invariant but left the concrete state machine for Step 6b. The tracker does not participate in the SCA's internal drafting or approval process — the WA is issued externally and received by the tracker. The only pre-issuance state needed is "pending receipt." The WA entity must exist in `pending` state before receipt so that WA Codes can be associated with it speculatively, anchoring the limbo derivation chain: WA `pending` → WA Code `expected` → Deliverable `pending_rfa`. `issue_wa` resolves the whole chain atomically.
- **Alternatives considered:**
  - *More granular pre-issuance states (draft → pending_approval → issued).* Rejected — the tracker does not participate in the SCA's issuance process. The only distinction the tracker cares about is whether the WA has been received; internal SCA states are invisible to the system.
  - *No pre-issuance WA entity (create WA only on receipt).* Rejected — the WA entity needs to exist in `pending` state as an anchor for speculative WA Codes. Without it, the limbo derivation chain has no parent and WA Code reconciliation at issuance has no reference point.
- **Consequences:**
  - **State machine:**
    - `pending → issued`: `issue_wa` compound command. Runs WA Code reconciliation (ADR-0022): expected codes present on the issued WA transition `expected → issued`; expected codes absent from the WA transition `expected → pending_rfa`; unexpected codes on the WA are created directly in `issued`. Cascades Deliverable transitions for newly-issued codes (`pending_rfa → outstanding`).
    - `issued → superseded`: auto-triggered when `issue_wa` fires on a new WA for the same project that references this WA as the prior version (ADR-0016 self-reference).
  - **Immutability.** `superseded` is a terminal state. No commands are accepted; RFA filings against a superseded WA are rejected at the command guard.
  - **Limbo chain.** WA `pending` → WA Code `expected` → Deliverable `pending_rfa` are the same "limbo" concept at successive derivation levels. `issue_wa` resolves the full chain atomically.

---

## ADR-0031 — RFA concrete state machine, auto-generated drafts, and approval cascade

- **Date:** 2026-05-12
- **Decision:** RFA has five states: `draft`, `in_review`, `approved`, `rejected`, `withdrawn`. Drafts are system-generated and system-managed: when a WA Code first transitions to `pending_rfa` on a project, the system auto-creates a draft RFA (if none is open) and adds the code as a line item; subsequent `pending_rfa` transitions add line items; `dismiss_wa_code` (and any other path back out of `pending_rfa`) removes them. The tracker edits per-line budgets and free-text fields (subject, justification) but cannot manually add or remove line items. A shortfall flag (`requested_budget < observed_need`) is derived per line item and aggregated on the RFA; `submit_rfa` soft-warns but does not block. `approve_rfa` is a compound command that atomically: (1) creates an Amendment WA in `issued` state with `supersedes` = prior WA, (2) transitions target codes `rfa_in_review → issued` with RFA-specified budgets, (3) cascades affected Deliverables `pending_rfa → outstanding` (ADR-0022), (4) supersedes the prior WA `issued → superseded` (ADR-0030), (5) transitions the RFA `in_review → approved`. `reject_rfa` and `withdraw_rfa` return targeted codes `rfa_in_review → pending_rfa`; both are terminal for the RFA, and a fresh draft auto-generates from remaining unmet need. Authorization: `submit_rfa` and `withdraw_rfa` permitted to any tracker; `approve_rfa` / `reject_rfa` follow ADR-0030's dual-trigger pattern (auto on SCA portal event or manual tracker confirmation). A draft RFA whose line-item set empties before submission is hard-deleted. Comprehensive history capture (already assigned) is load-bearing from `in_review` onward.
- **Status:** accepted
- **Context:** ADR-0021 established WA Code's lifecycle at placeholder level with `pending_rfa` and `rfa_in_review` states; ADR-0027 finalized WA Code's state machine and noted that RFA submission triggers `pending_rfa → rfa_in_review` but deferred RFA's own state machine. ADR-0029 (Deliverable) and ADR-0030 (WA) similarly named RFA-driven transitions without specifying the RFA entity. The framing question was whether the tracker hand-authors RFA contents from blank, or whether the system derives them from observed structural need (codes in `pending_rfa`, budget gaps). The tracker confirmed the latter — an RFA is a record of accumulated unmet need on the project, so the system can generate the draft and warn on shortfalls. The approval cascade direction inherits from the limbo-chain resolution pattern (ADR-0030): for initial WAs the chain is resolved by `issue_wa`; for amendments the analog is `approve_rfa`, with no intervening `pending` phase because the codes were already anchored to the prior WA. Partial-approval scenarios (SCA approves some line items but not others, or modifies budgets) were considered and determined not to occur in practice — SCA processes RFAs as all-or-nothing decisions.
- **Alternatives considered:**
  - *Hand-authored RFA drafts (tracker composes payload from blank).* Rejected — the RFA's content is mechanically derivable from project state. Hand-authoring duplicates structural information the system already has and admits drafts inconsistent with the project's actual unmet need.
  - *Hard block on shortfall submission with an `acknowledged` flag override (parallel to ADR-0027).* Rejected — the downstream `budget_rfa_needed` loop already handles under-budgeted approvals; hard-blocking adds UX friction (the tracker may have verbally negotiated a lower number with SCA). Soft warning matches actual decision authority.
  - *Multiple draft RFAs per project, segmented by purpose (add-codes vs. amend-budget).* Rejected — SCA processes one RFA per amendment cycle. One open draft per project, combined-purpose-capable, matches the operational unit. Budget-amendment line items are deferred until budget tracking is in scope (ADR-0027 `budget_rfa_needed` placeholder).
  - *Creator-only `withdraw_rfa`.* Rejected — withdrawal is a project-level decision; restricting to the original submitter creates dead-letter problems when staff rotate. Comprehensive capture records who actually fired the command.
  - *Two-step approval cascade (`approve_rfa` produces Amendment WA in `pending`; separate `issue_wa` finalizes).* Rejected — Amendment WAs have no externally-arriving document to wait on; SCA's approval of the RFA is the issuance event. A `pending` Amendment WA would be a vestigial state with no real-world content and would split one event across two commands.
  - *Editable-at-approval payload (tracker records what SCA actually approved, potentially differing from submission).* Rejected — SCA does not partially approve RFAs in practice. Modifications happen via rejection/withdrawal of the original and submission of a new RFA, keeping the audit trail clean ("what we asked for = what was approved").
- **Consequences:**
  - **State machine:**
    - `(none) → draft`: auto-triggered by the first WA Code transition to `pending_rfa` on a project with no open draft. Line items are added/removed atomically with WA Code `pending_rfa` enter/exit.
    - `draft → in_review`: `submit_rfa` (any tracker). Target codes transition `pending_rfa → rfa_in_review` in the same transaction (ADR-0027). Soft-warns on shortfall.
    - `draft → (hard-deleted)`: when all line items have been removed (referenced codes dismissed or otherwise left `pending_rfa`) and no submission has occurred.
    - `in_review → approved`: `approve_rfa` compound command. Auto-trigger on SCA portal event or manual tracker confirmation. Cascade as described in the Decision.
    - `in_review → rejected`: `reject_rfa`. Auto-trigger or manual. Target codes return `rfa_in_review → pending_rfa`.
    - `in_review → withdrawn`: `withdraw_rfa` (any tracker). Target codes return `rfa_in_review → pending_rfa`.
  - **Auto-draft regeneration.** Rejection or withdrawal puts target codes back at `pending_rfa`. With unmet need still present, the system auto-creates a fresh draft covering those codes (plus any others currently `pending_rfa`). The rejected/withdrawn RFA remains in history as a discrete record of the failed cycle.
  - **Shortfall flag.** Derived per line item from `requested_budget < observed_need`; aggregated on the RFA. Surfaces as a submission warning. `observed_need` calculation is deferred to budget tracking implementation.
  - **Concurrent RFAs.** At most one RFA per project may be in `draft` state. Multiple RFAs in `in_review` or terminal states may coexist — a second draft can only auto-create after the prior draft is submitted, producing a new RFA entity. Two RFAs cannot target the same code in `in_review` simultaneously: submission locks the code at `rfa_in_review`, removing it from the `pending_rfa` pool that drives draft line items.
  - **Amendment WA composition.** The Amendment WA's code set is mechanically `(prior WA's codes) ∪ (RFA line items)` with budgets updated per the RFA's terms. The "unexpected codes" reconciliation path from ADR-0030 does not apply to amendments — the WA is system-generated from the RFA, not externally received.
  - **Hard-delete trigger.** Mirrors ADR-0027 (WA Code with no references) and ADR-0030 (pending WA on project cancellation): an entity that has never been externalized has no audit value when its reason to exist dissolves. The hard-delete path is the only path that loses RFA history records, and only for never-submitted drafts.
  - **Project cancellation.** Handling of open drafts and `in_review` RFAs on a cancelled project is deferred to the Project lifecycle decision later in this session.
  - **Delete on cancellation.** A `pending` WA whose WA Codes carry no Time Entry or Sample Batch references is hard-deleted when the project is cancelled. No accountability trail is needed — no work was ever done against it. WA Codes in the same condition are hard-deleted alongside it.

---

## ADR-0032 — Blocker-as-Note pattern with lazy materialization, dismissable/fix-only registry, and amendments to ADR-0018

- **Date:** 2026-05-12
- **Decision:** Closure blockers and operational blockers are unified under a single mechanism: typed Note subtypes on the existing polymorphic Note entity (ADR-0018). Notes gain a `subtype` discriminator (`regular | blocker | resolution`). System-derived blockers are computed from a registry over entity state and stay derived until a tracker engages with them (writes a comment or dismisses); on engagement they lazily materialize as a system-authored blocker Note. User-flagged blockers are tracker-authored blocker Notes from creation. Each registry entry is classified as `dismissable` (real-world acceptance path exists) or `fix-only` (structurally must be resolved). Dismissal is authorized to any tracker. Cross-project blockers materialize as paired blocker Notes (one per affected record) linked by an inter-Note reference. ADR-0018 is amended in three ways (subtype field, authorship class with nullable `created_by`, inter-Note reference field). ADR-0027's `acknowledged: bool` field aspect is superseded; its state machine and dismiss cascade survive.
- **Status:** accepted
- **Context:** ADR-0027 introduced a per-record `acknowledged: bool` field on Time Entry and Sample Batch to resolve the non-billable closure blocker. As Step 6b accumulated more closure-blocking conditions (Lab Report missing/invalid, COC missing, Daily Log missing on Time Entry, DepFiling required-doc missing, in-flight RFA at closure, cross-project time overlap, off-site sample collection), the per-record flag pattern was poised to proliferate across multiple entities with no single place to query "what is blocking project closure?" or attach commentary explaining a blocker's resolution path. Notes (ADR-0018) already attach polymorphically to any entity and accumulate over time — they are the natural anchor for blocker commentary, dismissal records, and resolution audit trails. The pivot unifies user-flagged "this is blocked because the contractor is unresponsive" with system-derived "this Sample Batch has no Lab Report" under one mechanism, with one query surface and one commentary affordance.
- **Alternatives considered:**
  - *Persist-all materialization (every blocker firing produces a system Note; every resolution produces a paired Note).* Rejected — generates Note churn for transient blockers (a Sample Batch whose `wa_code` is quickly relinked never matters operationally), requires an auto-resolution cross-cutting concern that scans for dissolved structural conditions, and materializes derived state contradicting ADR-0028's stance ("the conflict is fully derivable; materializing it adds a record lifecycle without buying anything"). Symmetric audit trail not worth the implementation weight.
  - *Per-entity `acknowledged: bool` flags (continuing ADR-0027's pattern).* Rejected — the flag would proliferate across at least six entities (Time Entry, Sample Batch, Document, DepFiling, RFA, possibly Project). Each instance carries its own ad-hoc validation logic. No unified query for project-level blockers. No commentary thread on what a tracker tried before accepting the blocker.
  - *Synthetic User row for system authorship.* Rejected — leaks a fiction record into the User table that has no username/password/role-assignment shape. Every user-list query, authorization predicate, and UI dropdown gains "is this a real user?" filtering. The system-ness of a record is a structural property of the record, not a deferred identity claim.
  - *Multi-target reference shape on Note (for cross-project blockers).* Rejected — cross-cutting schema change to ADR-0018's `(entity_type, entity_id)` reference; ambiguous authorship when two trackers engage at different times; shared commentary stream conflates the distinct investigation paths each project's tracker is running (different vendor contacts, different escalation timelines).
  - *Creator-only dismissal authorization.* Rejected — collapses for system-derived blockers (no human creator); creates a staff-rotation dead-letter problem where dismissals can't proceed if the original observer left the firm; inconsistent with `withdraw_rfa`'s any-tracker authorization (ADR-0031).
  - *Eager materialization on first surfacing (system writes a blocker Note the moment the structural condition fires, before any user engagement).* Rejected — equivalent to persist-all for system-derived blockers; produces records for blockers nobody ever cared about. The "did anyone care?" question is the operational divider, and lazy materialization captures it directly: engagement materializes, neglect leaves it derived.
- **Consequences:**
  - **Note subtype enum.** Notes carry `subtype: 'regular' | 'blocker' | 'resolution'`. `regular` is the ADR-0018 default behavior (commentary, no special semantics). `blocker` and `resolution` carry additional fields described below.
  - **Authorship class.** Note schema gains `authorship_class: 'user' | 'system'`. `created_by` becomes nullable (system-authored Notes have `created_by = null`; user-authored Notes carry the User reference as before). Edit predicate from ADR-0018 amends to `note.authorship_class == 'user' AND note.subtype == 'regular' AND caller == note.created_by` (system Notes are never user-editable; blocker and resolution Notes are immutable regardless of authorship — their content is structurally meaningful, not free-form). This pattern generalizes beyond blocker Notes: system-generated RFA drafts (ADR-0031) use the same `authorship_class = 'system'` shape.
  - **Blocker Note fields.** `subtype: 'blocker'`, `blocker_type` (registry key string, or `null` for user-flagged), `surfaced_at` (timestamp — when the structural condition first held; for system-authored Notes this is backfilled from underlying entity history at materialization time; for user-authored Notes equals `created_at`), `paired_blocker_ref` (nullable, points to a paired blocker Note for cross-project blockers).
  - **Resolution Note fields.** `subtype: 'resolution'`, `blocker_ref` (required, points to the blocker Note being resolved), `resolution_kind: 'dismissal' | 'structural_fix'`.
  - **Inter-Note reference field.** ADR-0018's Note schema gains a nullable `references` typed reference to another Note. Used by resolution Notes (pointing at the blocker they resolve via `blocker_ref`) and by paired blocker Notes (pointing at their counterpart via `paired_blocker_ref`). General use beyond these two cases (e.g., reply threading) is deferred to post-MVP — the MVP semantic is "this Note references that Note in a structurally-meaningful way."
  - **Lazy materialization rule.** A system-derived blocker stays derived (computed via a registry scan over entity state) until a tracker engages with it. Engagement triggers: (i) writing a Note about the blocker (regular subtype, attached to the blocked entity, semantically referencing the blocker — engagement is detected at the command surface, e.g., a `comment_on_blocker(target, blocker_type, message)` command); (ii) writing a dismissal (valid only for dismissable blockers). On the first engagement, the system atomically creates a system-authored blocker Note with `surfaced_at = <derived from entity history>`, `created_at = now`, then performs the engagement (attaching the user's regular Note or the dismissal resolution Note). Subsequent engagements find the blocker Note already materialized and append to it.
  - **User-flagged blockers.** A tracker creates a blocker Note directly on any entity with `authorship_class: 'user'`, `blocker_type: null` (no registry entry), `surfaced_at = created_at`. The tracker supplies the message. Resolution semantics are the same — a resolution Note references the blocker Note, with `resolution_kind: 'dismissal'` (tracker decided to move on) or `resolution_kind: 'structural_fix'` (the underlying issue was resolved; tracker logs this manually since the system has no structural condition to watch).
  - **Cross-project blocker materialization.** For blockers spanning two records on different projects (currently #8 cross-project time overlap), engagement by one project's tracker materializes the blocker Note on that side; engagement by the other project's tracker materializes a paired Note on its side. Both Notes carry `paired_blocker_ref` pointing at the counterpart. Each project's tracker maintains a separate investigation thread (separate regular Notes attached to their own side's blocker Note). When the structural condition dissolves, the system writes a resolution Note for each existing materialized blocker Note independently — if only one side ever engaged, only one resolution Note is created.
  - **Resolution semantics.**
    - *Structural fix (system-authored resolution).* When the underlying structural condition dissolves (registry predicate flips false), the system writes a resolution Note for each materialized blocker Note of that type+target, with `authorship_class: 'system'`, `resolution_kind: 'structural_fix'`. Derived (non-materialized) blockers simply stop being surfaced — no resolution Note is created, since there is no blocker Note to resolve.
    - *Dismissal (user-authored resolution).* The tracker fires a dismissal command. If the blocker Note doesn't yet exist (first engagement is the dismissal itself), the system materializes it first (as above), then creates a user-authored resolution Note with `resolution_kind: 'dismissal'`, referencing the blocker Note.
    - *Fix-only blockers cannot be dismissed.* The dismissal command rejects when targeting a `fix-only` registry entry. Only structural-fix resolution applies.
  - **Authorization.**
    - *Writing a regular Note (commentary):* per ADR-0018, any user.
    - *Writing a user-flagged blocker Note:* any tracker.
    - *Writing a dismissal resolution Note:* any tracker, on dismissable blockers only. Parallels `withdraw_rfa` (ADR-0031). The Note's `created_by` records who dismissed.
    - *System-authored Notes:* generated by the command pipeline; no user command writes them directly.
  - **Blocker-type registry (initial population).** Maintained alongside this ADR (and amended by subsequent ADRs that introduce new blockers):
    | # | Blocker | Class |
    |---|---|---|
    | 1 | Time Entry `wa_code=null` (non-billable orphan) | Dismissable |
    | 2 | Sample Batch `wa_code=null` (non-billable orphan) | Dismissable |
    | 3 | Sample Batch Lab Report state ∈ {`missing`, `invalid`} at closure | Dismissable |
    | 4 | Sample Batch COC `missing` at closure | Dismissable |
    | 5 | Time Entry with no `daily_log` reference at closure | Dismissable |
    | 6 | DepFiling required-doc `missing` at closure | Dismissable |
    | 7 | Open `draft` or `in_review` RFA at closure | Dismissable |
    | 8 | Cross-project time overlap on Employee | Fix-only |
    | 9 | Sample collection time not covered by employee on-site interval | Dismissable |

    New blocker types added by future ADRs append to the registry, each tagged dismissable or fix-only. The classification test: "is there a real-world acceptance path?" — yes ⇒ dismissable; no (logical impossibility) ⇒ fix-only.
  - **Project closure gate.** A project may close when both: (i) no `fix-only` blockers from the registry hold over any of its entities (derived check at closure time); (ii) every `dismissable` blocker either no longer holds derivationally OR has an associated dismissal resolution Note. Closure UI surfaces the unresolved-dismissable set as a batch-acknowledge flow.
  - **Notes still carry no history.** ADR-0018's no-history stance is preserved for all Note subtypes. The blocker Note IS the surface-record; the resolution Note IS the resolution-record; no edit history beyond `edited_at` for `regular` Notes (blocker and resolution Notes are immutable per the edit predicate above).
  - **Supersession of ADR-0027.** The per-record `acknowledged: bool` field on Time Entry and Sample Batch (introduced by ADR-0027 for blockers #1 and #2) is removed. Closure-blocker resolution for those entities now goes through the resolution-Note mechanism. The rest of ADR-0027 (WA Code state machine, `dismiss_wa_code` compound cascade, `rfa_in_review` lock) is untouched.
  - **Amendments to ADR-0018.** Three specific changes: (a) `subtype` field added (`regular | blocker | resolution`); (b) `authorship_class` field added (`user | system`) with `created_by` becoming nullable; (c) `references` typed reference to another Note added (used by `blocker_ref` semantics on resolution Notes and `paired_blocker_ref` semantics on paired blocker Notes). ADR-0018's polymorphic target reference, creator-only edit rule for regular user Notes, and no-history stance all stand.
  - **Relationship to ADR-0028.** ADR-0028 (cross-project time overlap as derived blocker, no conflict entity) is unchanged in its core stance: the conflict stays derivationally computed. This ADR adds: when a tracker engages with the overlap, a paired blocker Note materializes on each affected Time Entry. Auto-resolution on structural fix still applies. No supersession.
  - **Carry-forwards to ADR-0033 (Sample Batch).** Two questions touched by this ADR but resolved in the Sample Batch ADR: (i) smart-inference UI affordance — when blocker #9 fires, query for "same employee, same school, overlapping Time Entry on a different project" and surface "possibly misfiled — did you mean Project Y?"; (ii) what dismissal of blocker #9 structurally does to the batch (pure Note vs Note plus wa_code null-out).
  - **Carry-forward to ADR-0034 (Time Entry off-site intervals).** Registry entry #9 references the on-site interval structure that ADR-0034 will formally define. The registry entry holds as user-facing language; the implementation predicate will reference ADR-0034's structural fields.
  - **Carry-forward to Project lifecycle ADR (session 7).** The project closure gate above is the canonical closure predicate. The Project lifecycle ADR will define `close_project` and `cancel_project` commands against this predicate; the gate text stays here as the source of truth.
  - **Post-MVP additions** (separately recorded in `planning/post-mvp.md`): (a) "Track this" pin as an engagement trigger requires a notification system to be operationally meaningful; (b) Structured blocker assignment (`assigned_to` field, queryable my-blockers view, reassignment audit) requires notifications to deliver value and would force partial supersession of ADR-0018's no-history stance for blocker Notes. Both are deferred as a bundle.

---

## ADR-0033 — Sample Batch state machine, Lab Report document type, derivation source, relink command, chain-dismissal extension

- **Date:** 2026-05-12
- **Decision:** Sample Batch has a two-state machine: `received` (entry state, set on COC receipt at batch creation) → `billed` (terminal, set when the batch is finalized for billing). No `collected`, no `in_lab`, no `void` — the system doesn't model pre-receipt or void states because the tracker doesn't engage with batches until the COC arrives. Lab Report is a new `document_type` with a bespoke three-state machine per ADR-0024's escape hatch: `missing` → `saved`, `missing` → `invalid`, `saved` → `invalid`, `invalid` → `saved`. Sample Batch joins WA Code and DepFiling as a Document-derivation source under ADR-0015: each batch produces a COC document (created in `saved` state at batch creation) and a Lab Report document (created in `missing` state). The `relink_sample_batch_wa_code(batch, new_wa_code)` command is strict-gated to orphan recovery (current `wa_code` is null or in a `dismissed` code state); `new_wa_code` is not constrained to the current project's codes, supporting cross-project misfiling recovery by construction. The chain-dismissal rule from ADR-0032 applies specifically: dismissing blocker #9 atomically nulls `wa_code` and writes a paired auto-dismissal resolution Note for the resulting blocker #2. A smart-inference UI hint surfaces "possibly misfiled — did you mean Project Y?" when blocker #9 fires and a `(same employee + same school + overlapping Time Entry on a different project)` match exists. Sample Batch's history pattern remains lifecycle capture; delete policy remains soft delete.
- **Status:** accepted
- **Context:** Step 6b sessions 5–6 deliberated Sample Batch in pieces. Positions 1 and 2-amended (two-state machine and Lab Report as bespoke document type) were approved in chat in session 5 but couldn't be ADR-written because the closure-blocker shape depended on the blocker-pattern pivot. Session 6 resolved the blocker pattern (ADR-0032), then closed remaining Sample Batch questions (Position 4 relink command shape, Position 6 history pattern, smart-inference for misfiled batches, structural consequence of dismissing blocker #9). This ADR consolidates the full Sample Batch design.
- **Alternatives considered:**
  - *More granular Sample Batch state machine (e.g., `collected → in_lab → received → billed`).* Rejected — the tracker doesn't see batches until the COC arrives; pre-receipt states have no engagement surface. `in_lab` is a lab-side concern, not a tracker-side state; the lab's processing is opaque to the tracker until results arrive. Simpler is right.
  - *`void` state for invalidated batches.* Rejected — the soft-delete pipeline (per the soft-delete policy) handles the rare case of a batch that needs to disappear from active flows while preserving history. A first-class `void` state adds lifecycle weight for a rare path.
  - *Lab Report as a separate entity (not a Document type).* Rejected — Lab Report shares the upload-and-track shape of all other tracked documents (COC, Daily Log, ACPs, etc.). The Document discriminator dispatch (ADR-0024) is the established mechanism. Standing up Lab Report as a separate entity would duplicate file storage, derivation, and lifecycle plumbing that Document already provides.
  - *Lab Report as a simple `missing → saved` document type.* Rejected — labs occasionally return defective reports that need to be reissued (transposed sample IDs, incomplete analysis, etc.). A simple two-state machine forces the tracker to either accept the defective report as `saved` (lying to the system) or leave it `missing` (lying about whether the lab responded). The bespoke `invalid` state captures the genuine third operational state: the lab returned something, it's broken, we're waiting for an amended report. Closure-blocker logic (ADR-0032 registry entry #3) treats `invalid` as equivalent to `missing` for closure purposes.
  - *Permissive `relink_sample_batch_wa_code` (allow at any time, regardless of current wa_code state).* Rejected — sample collection codes are mechanically determined by `(sample_type, school)`; there is no operational scenario where a healthy batch needs to be re-routed to a different code on the same project, because no other code is right. Permissive gating opens an error surface (tracker accidentally re-routes a valid batch) with no countervailing operational benefit.
  - *Structured `reassign_sample_batch_project(batch, new_project, new_wa_code)` command for cross-project misfiling recovery in MVP.* Rejected — Sample Batch's project membership is derived from its wa_code per ADR-0020; changing the wa_code to a code on a different project IS the move. The existing `relink_sample_batch_wa_code` command, with `new_wa_code` unconstrained to the current project, handles the workflow without new surface area. A structured cross-project reassignment is post-MVP if a notification-coupled workflow ("alert Project Y's tracker that a batch is incoming") justifies the additional structure.
  - *Promote Sample Batch to comprehensive history capture.* Rejected — the original promotion motivations (capture `acknowledged` flag mutations, capture relink, capture composition edits) are mostly mooted by the blocker-Note pivot. Composition-edit history remains a gap, but it's operational data rather than contractual amendment shape; tracker-side explanatory Notes for composition edits provide the right friction level. Promotion is reversible if composition disputes prove frequent post-MVP.
  - *Smart-inference as a structured command with one-button reassignment.* Rejected for MVP — the diagnostic value of the hint is independent of whether the resolution is one-click. The existing dismiss-then-relink path (two clicks after triage) is auditable and unambiguous; bundling into a single "reassign to Project Y" command requires authorization design across two project boundaries (whose authority moves the batch?) and notification plumbing for the receiving project. Both are post-MVP concerns.
- **Consequences:**
  - **State machine.**
    - `(none) → received`: `create_sample_batch` on COC receipt. Required attributes: composition `[{subtype, quantity}]`, sample type (PCM / TEM / Bulk), TAT, location(s), employee reference (collector), collection time, wa_code reference. Composition invariant from ADR-0019 carries forward: PCM/TEM batches require a single subtype; Bulk batches allow mixed subtypes.
    - `received → billed`: triggered by billing-system finalization (specific command and authorization defined at billing-design time; this ADR establishes the state, not the billing flow).
  - **No state for void or pre-receipt.** Soft delete handles the rare invalidation case. Pre-receipt collection is a real-world phase but not a tracker-side state — the tracker engages on COC receipt.
  - **Commands.**
    - `create_sample_batch(...)` — creates the batch in `received`, generates COC Document in `saved`, generates Lab Report Document in `missing`. Smart command inference per ADR-0021 family: if the `(sample_type, school)` code doesn't exist on the project's WA, the wa_code is set null and the batch enters blocker #2 derivationally.
    - `edit_sample_batch_composition(batch, new_composition)` — updates composition. Not state-machine-relevant; not captured under lifecycle capture per the deliberated history pattern. Tracker-side Notes are the audit affordance for composition changes.
    - `relink_sample_batch_wa_code(batch, new_wa_code)` — strict-gated: permitted only when current wa_code is null or the current code is in `dismissed` state. `new_wa_code` is any wa_code in the system; not constrained to the current project. Triggers auto-relink when a deterministic `(sample_type, school) → wa_code` match becomes available on the current project (e.g., new WA issuance or RFA approval populates the matching code).
    - Lifecycle transition commands for Lab Report (per the document type's state machine, below).
  - **Lab Report `document_type`.**
    - **States:** `missing`, `saved`, `invalid`.
    - **Transitions:**
      - `missing → saved`: lab returns a valid report; tracker uploads and saves.
      - `missing → invalid`: lab returns a defective report up front; tracker records it as broken without ever marking it saved.
      - `saved → invalid`: tracker discovers errors in a previously-saved report (e.g., on closer inspection or downstream review).
      - `invalid → saved`: lab returns an amended report; tracker accepts.
    - **Closure-blocker condition (ADR-0032 registry entry #3):** state ∈ {`missing`, `invalid`}. Both states block closure (dismissable).
    - **Joins ADR-0024's per-`document_type` pattern menu** under the bespoke option. The cycling-family parameterized machine doesn't fit (Lab Report has no submit-review-approve loop; the lab is opaque, the report is either valid or it isn't). The simple `missing → saved` shape misses the `invalid` state. Bespoke is the right slot.
  - **Sample Batch as Document-derivation source (extending ADR-0015).** Sample Batch joins WA Code and DepFiling as a derivation source. Each batch derives two documents at creation:
    - COC document (document_type: `COC`, simple `missing → saved` per ADR-0024 menu). Created directly in `saved` state because COC arrival IS the batch creation trigger.
    - Lab Report document (document_type: `LabReport`, bespoke per above). Created in `missing` state.
    - The derivation set per-batch is fixed at exactly these two documents (no editable required-doc set as DepFiling has); the derivation rule is purely structural.
  - **Relink command details.**
    - Strict gating: rejected if current wa_code is non-null and the referenced code is not in `dismissed` state. Healthy batches cannot be relinked.
    - Cross-project use: `new_wa_code` may belong to any project. The batch's derived project membership flips to follow. No additional authorization gate in MVP (any tracker may relink); post-MVP role hierarchy may restrict.
    - Auto-relink: when a batch is orphaned (wa_code=null) on a project, the system continuously evaluates "does the project's WA now have a code matching `(batch.sample_type, batch.school)`?" If yes, auto-fires `relink_sample_batch_wa_code` to that code. Smart command inference pattern (ADR-0021 family).
  - **Chain-dismissal rule (extension of ADR-0032).** ADR-0032's lazy materialization rule says dismissal writes a resolution Note. This ADR adds: when a dismissal's structural side-effect causes another registry blocker's condition to fire, that secondary blocker is materialized as already-dismissed atomically with the primary dismissal.
    - **Concrete instance for blocker #9:** the dismissal of blocker #9 ("sample collection time not covered by employee on-site interval") atomically (a) writes the resolution Note for #9 with `resolution_kind: 'dismissal'`, (b) nulls `wa_code` on the batch (the structural side-effect declaring the batch non-billable for the project), (c) materializes a blocker Note for #2 (the resulting wa_code=null condition) with `authorship_class: 'system'`, (d) writes a paired auto-dismissal resolution Note for #2 with `resolution_kind: 'dismissal'`, `authorship_class: 'system'`, and `references` pointing at the #9 resolution Note as the causing-event.
    - **Generalization (in scope of ADR-0032 by extension).** Future ADRs that introduce blockers where one's dismissal structurally causes another's condition may opt into the chain-dismissal pattern by declaring the linkage in the registry. The chain-dismissal mechanism is part of the blocker pattern; the per-blocker declaration of which-dismissal-chains-which is per-ADR.
  - **Smart-inference hint for misfiled batch.** When blocker #9 holds for a Sample Batch (regardless of materialization state), the system runs the query `(same employee + same school + Time Entry on a different project whose interval covers the batch's collection time)`. If a hit exists, the UI surfaces "possibly misfiled — did you mean Project Y?" on the batch detail and on any materialized blocker Note for #9. This is read-side derivation; no state change. Resolution path is manual: tracker dismisses #9 (chain-dismisses → batch non-billable, wa_code=null), then fires `relink_sample_batch_wa_code` to a code on Project Y. Identity preserved; no data re-entered; full audit trail via the dismissal Notes and the relink event.
  - **History pattern: lifecycle capture (unchanged).** Sample Batch's lifecycle capture per ADR-0013 covers the `received → billed` transition and the `relink_sample_batch_wa_code` event (wa_code is state-machine-adjacent for billing identity). Composition edits, TAT edits, location edits are not captured under lifecycle; the tracker-side Notes affordance carries explanatory audit for these. The blocker-Note pattern (ADR-0032) carries dismissal audit.
  - **Delete policy: soft delete (unchanged).** Existing references from Notes, audit logs, and history records preclude hard delete. ADR-0027's "hard-delete-when-no-references-ever-existed" exception does not apply to Sample Batch — by construction a batch always has derived COC and Lab Report Documents that reference it.
  - **Amendments to other ADRs.**
    - **ADR-0024 (Document lifecycle menu):** `LabReport` joins the bespoke option with the three-state machine described above. The per-`document_type` assignment table grows: `LabReport` lands in the bespoke row alongside CPR and FAMR (cycling-family) — distinct sub-row for bespoke vs cycling-family.
    - **ADR-0015 (Document-derivation set):** Sample Batch added to the derivation-source roster (currently WA Code, DepFiling, project events). Documents derived from a Sample Batch: one COC, one Lab Report. The derivation rule is fixed (not editable); no parallel to DepFiling's editable `required_doc_types`.
    - **ADR-0032 (Blocker pattern):** chain-dismissal rule formalized for blocker #9 → blocker #2 linkage. The pattern is extensible — future blocker ADRs that need similar chain-dismissal semantics declare the linkage in the registry.
  - **Closure invariants reference the registry.** Project closure (defined in Project lifecycle ADR, session 7) will gate on no-unresolved-fix-only-blockers + no-unresolved-and-non-dismissed-dismissable-blockers, per ADR-0032's project closure gate text. This ADR doesn't redefine the gate; it just ensures the Sample Batch contribution to the blocker registry is complete (#2, #3, #4, #9 covered).
  - **Carry-forwards.**
    - **Billing finalization flow** (the `received → billed` trigger): deferred to billing-design step (likely Step 6c or later). This ADR establishes the state name and terminal placement only.
    - **Cross-project reassignment as a structured command**: deferred to post-MVP (separately recorded in `planning/post-mvp.md` alongside notifications, since the workflow benefits from notification coupling).

---

## ADR-0034 — Time Entry off-site intervals, structural shape, and dual-predicate overlap semantics

- **Date:** 2026-05-12
- **Decision:** Time Entry replaces its scalar `hours` field with structured time-range fields: `on_site_range: (start_time, end_time)` representing the employee's commitment window to the entry's project, and `off_site_sub_intervals: [(start_time, end_time)]` representing project-committed time away from the parent project's site (currently always lab-delivery travel). Sub-intervals must be entirely within `on_site_range` and pairwise disjoint. Net on-site time is derived: `on_site_range \ ⋃ off_site_sub_intervals`. The off-site sub-interval shape carries no `reason` field and no `drop_off_time` field in MVP — both deferred. Two structural predicates over this shape are pinned in this ADR: (i) the **cross-project overlap predicate** (ADR-0028 amendment) operates on the **gross on-site range**, because off-site sub-intervals are project-committed time and don't free the employee for another project's billing; (ii) **blocker #9** (sample collection time coverage, ADR-0032 registry entry) operates on **net on-site time**, because sample collection requires physical presence at the school and off-site sub-intervals are physical absences.
- **Status:** accepted
- **Context:** Time Entry has been a scalar-hours record since Step 6a, with the structural expansion deferred to a dedicated ADR. Step 6b sessions surfaced two structural pressures simultaneously: (a) sample collection blocker #9 needs to check whether the employee was physically at the school when the batch was collected, which scalar hours can't answer; (b) lab-delivery travel is real billable time during which the employee is committed to the project but not at the school, so collapsing all hours into "at school" loses fidelity. The structural shape resolves both: explicit on-site range with explicit off-site carve-outs preserves both the commitment span (for billing and cross-project conflict) and the presence span (for blocker #9 and any future presence-based check). The dual-predicate contrast — project commitment ≠ physical presence during an off-site sub-interval — is the key insight, and the two existing predicates that touch Time Entry already need that divergence resolved differently.
- **Alternatives considered:**
  - *Status quo: scalar `hours` field.* Rejected — can't answer blocker #9's "was the employee at the school at time T" question without an interval; the closest derivable proxy is "did the employee log any hours that day," which is too coarse for the misfiled-batch use case. Structural data is required.
  - *Flat list of disjoint on-site intervals (no nested off-site).* Rejected — architecturally equivalent to the chosen shape (the same workday decomposes into equivalent representations) but operationally awkward: tracker must split-and-resplit entries every time an off-site moment occurs, and the "this was one workday on Project A interrupted by a lab run" narrative becomes implicit rather than explicit. Off-site sub-intervals are first-class because they carry meaning the flat list erases.
  - *Off-site sub-intervals with a `reason` field (free-text or enum).* Rejected for MVP — the only operationally observed off-site reason today is lab delivery; capturing it would be ceremonial. Adding the field later is a deterministic backfill (all pre-feature rows = the implicit MVP reason) with no structural reshape. Deferred per MVP scope philosophy.
  - *Off-site sub-intervals with a `drop_off_time` scalar field for COC cross-checking.* Rejected for MVP — the COC's `relinquished_time` already captures the source-of-truth handoff moment, and managers cross-check by eye today without strain. Adding the field later is a nullable-scalar additive migration. Deferred.
  - *Net on-site time as the cross-project overlap predicate.* Rejected — depended on a misread of off-site semantics. Off-site sub-intervals are project-committed time, not employee-available time; a Project A off-site sub-interval doesn't free the employee for Project B's billing. Gross range is the right slice for the commitment question. The misread surfaced during deliberation when the user described how a workday with a Project B side-stop would actually be entered: Project A is split into morning and afternoon entries, with the Project B visit as a separate entry — not as one continuous Project A entry with Project B fit inside its off-site window.
  - *Gross range as blocker #9's predicate.* Rejected — Project A off-site sub-intervals are physical absences from the school; a sample can't be collected during one. Net time is the right slice for the presence question.
- **Consequences:**
  - **Time Entry schema change.** Replaces scalar `hours` with `on_site_range: (start_time, end_time)` and `off_site_sub_intervals: [(start_time, end_time)]` (list, possibly empty). Validation invariants:
    - `on_site_range.start < on_site_range.end`.
    - Each sub-interval is entirely within `on_site_range` (`.start >= on_site_range.start AND .end <= on_site_range.end`).
    - Sub-intervals are pairwise disjoint.
    - Each sub-interval has positive duration (`.start < .end`).
  - **Derived fields.**
    - **Net on-site time** = `on_site_range` minus the union of off-site sub-intervals. Represented as a set of disjoint intervals.
    - **Gross billable duration** (until billing ADR refines) = duration of `on_site_range`. Off-site sub-intervals contribute to billable hours because they are project-committed time (currently always lab delivery).
  - **Cross-project overlap predicate (ADR-0028 amendment).** The "same employee, overlapping time across two projects" check uses the **gross `on_site_range`** of each Time Entry. Two Time Entries on different projects for the same employee whose `on_site_range`s intersect produce the cross-project overlap blocker (#8, fix-only). Sample Batch collection-time-vs-other-project's-Time-Entry checks use the same gross-range slice on the Time Entry side. Rationale: project commitment is the question being asked, and project commitment spans the full on-site range including off-site sub-intervals.
  - **Blocker #9 predicate (ADR-0032 registry entry).** Becomes structural: "the batch's collection time does not fall within the **net on-site time** of any of the batch's employee's Time Entries on the batch's school on the batch's date." Off-site sub-intervals do not satisfy coverage. Rationale: physical presence is the question being asked.
  - **Dual-predicate explicit contrast.** Downstream readers and future predicates should reference this distinction:
    - Project commitment → gross on-site range.
    - Physical presence at the parent project's site → net on-site time.
    - Future predicates over Time Entry should pick the slice that matches their question and cite this ADR.
  - **Amendment to ADR-0028.** ADR-0028's cross-project overlap predicate is restated structurally: the overlap is `Time Entry A.on_site_range ∩ Time Entry B.on_site_range ≠ ∅` for the same employee across different projects. The derived-blocker stance and "no conflict entity" decision are unchanged.
  - **Amendment to ADR-0032 registry.** Entry #9's predicate language is updated to "sample collection time not within any Time Entry's net on-site time for that employee on that date and school." The dismissable classification and chain-dismissal-to-#2 linkage from ADR-0033 are unchanged.
  - **Validation at write time.** `create_time_entry` and `edit_time_entry` reject inputs violating the on-site range or sub-interval invariants. Sub-intervals that extend past the on-site range or overlap one another are rejected at the command guard.
  - **No `reason` field, no `drop_off_time` field.** Both deferred per MVP scope philosophy (not in current spreadsheet seed data; manual workflows handle the current need). Future ADRs adding either field do so as additive migrations with deterministic backfill — no structural reshape required.
  - **Day-of representation example (canonical).** A workday where Sam works at School X 09:00–17:00 with a lab run 12:00–13:00, plus a brief Project B stop at School Y 13:00–13:30, requires three Time Entries:
    - Project A, on-site 09:00–13:00, off-site sub-interval 12:00–13:00.
    - Project B, on-site 13:00–13:30, no sub-intervals.
    - Project A, on-site 14:00–17:00, no sub-intervals.

    The Project A entries are split because Sam's commitment to Project A is paused while Sam is working Project B. The 13:30–14:00 gap is unbilled travel between sites. This decomposition is the intended use of the structure.
  - **Carry-forward — billing.** Billable-hours calculation (Step 6c or later) inherits from this structure: gross `on_site_range` duration is the current billable quantity. Future discrimination (some off-site reasons billable, others not) requires the `reason` field to be added first; the structural shape supports the future cut without rework.
  - **Carry-forward — on-call-nearby and similar future off-site categories.** When a new off-site category arises where the employee *is* available to another project (e.g., on-call nearby for Project B while on-site for Project A), the migration is additive: (a) add `reason` field to sub-intervals, (b) backfill existing rows as the implicit MVP reason, (c) update the cross-project overlap predicate to discriminate by reason (sub-intervals with availability-yielding reasons reduce commitment span; those without don't). The structural shape survives intact.

---

## ADR-0035 — EmployeeRole temporal shape, Time Entry reference invariant, and disjoint-ranges-per-role-type rule

- **Date:** 2026-05-12
- **Decision:** EmployeeRole carries `(employee_id, role_type, rate, start_date, end_date?)` with full-day range semantics — both `start_date` and `end_date` are calendar dates interpreted as 00:00 and 23:59 of those days respectively, and the range `[start_date, end_date]` is closed at both ends (end_date is the last valid day, not the day-after). `end_date` is nullable while the role is open-ended. Time Entry holds a mandatory foreign key to a specific EmployeeRole row; the role's rate is read transitively at billing/calculation time. Write guards on `create_time_entry` and `edit_time_entry` enforce `time_entry.date ∈ [employee_role.start_date, employee_role.end_date ?? +∞]`. Rate changes are modeled by end-dating the current row at day D and creating a new row starting at day D+1 with the new rate; Time Entries on days ≤ D reference the old row, on days ≥ D+1 reference the new row. **Within a single `(employee_id, role_type)` pair, date ranges must be pairwise disjoint**, enforced on `create_employee_role` and `edit_employee_role`. Different role types may overlap freely (employee can hold TechRole and ProjectLead simultaneously). EmployeeRole has no state machine — temporal validity is computed from the date range. Lifecycle capture (already assigned via ADR-0013) records grant and close events; soft-delete policy (already assigned) gates accidental removal of rows referenced by Time Entries.
- **Status:** accepted
- **Context:** EmployeeRole was identified in Step 6a as a temporal work-license assignment carrying the billing rate, with the temporal rate resolution design pattern (#1) declared. The concrete shape (schema, Time Entry reference invariant, rate-change pattern, state-or-not) was deferred to Step 6b. Step 6b's prior sessions filled in the entities that reference EmployeeRole — Time Entry's structural expansion landed in ADR-0034, which made the date-vs-timestamp question for the boundary check explicit. The framing question for this ADR was whether temporal validity needed an explicit state machine layered on top, and what the Time Entry → EmployeeRole reference shape looks like given roles span full days only.
- **Alternatives considered:**
  - *Explicit `active | revoked` state machine on EmployeeRole.* Rejected — the enum is derivable from `(start_date, end_date)` and the system clock. Layering it on duplicates state, opens drift risk (the enum and the date range can disagree), and doesn't help any operational case. Temporal validity is the only state, computed at read time. Lifecycle capture provides the audit affordance for grant/close events.
  - *Mid-day role boundaries (timestamp-resolution `start_at`, `end_at?`).* Rejected — roles don't end mid-day in practice. Calendar-day resolution matches the operational unit (a person becomes a Tech on a date; their rate is established by a payroll decision that anchors to a date, not a moment). Timestamp resolution adds precision the domain doesn't use.
  - *Half-open range semantics `[start_date, end_date)`.* Rejected in favor of closed-closed `[start_date, end_date]`. The end_date IS the last valid day; rate-change pattern reads naturally as "end the old row at D, start the new row at D+1." Half-open would invert this: "end at D+1, start at D+1" — which is correct but harder to reason about when reading a single row.
  - *Time Entry references `(employee_id, role_type)` only; rate resolved by lookup at write time, not via FK.* Rejected — loses direct traceability ("which EmployeeRole row was this Time Entry billed against?") and forces every billing read to re-run the date-range lookup. FK-to-specific-row is the cleaner reference shape; the boundary invariant ensures the FK can't reference a row that doesn't cover the Time Entry's date.
  - *Snapshot the rate onto Time Entry at write time (rate field on Time Entry, not transitive read).* Rejected for MVP — the FK + transitive read avoids the snapshot drift question (what happens if the EmployeeRole's rate is corrected after a Time Entry was written?). The disjoint-ranges invariant plus the boundary check mean the FK uniquely identifies the rate; a snapshot would be redundant. Post-MVP, if retroactive rate corrections become a workflow concern, a snapshot field could be added without restructuring.
  - *Allow overlapping date ranges within the same `(employee_id, role_type)`.* Rejected — overlap makes rate resolution ambiguous on the overlap day. Disjoint-per-role-type is the structural guarantee that the FK from Time Entry is unambiguous. Different role types overlapping is fine (Alice as TechRole and ProjectLead simultaneously) because the role_type discriminator resolves the ambiguity.
- **Consequences:**
  - **Schema.** EmployeeRole = `(id, employee_id, role_type, rate, start_date, end_date?)`. `end_date` nullable.
  - **Range semantics.** `[start_date, end_date]` closed-closed at calendar-day resolution. A role with `end_date = 2026-03-15` is valid through end-of-day 2026-03-15. A role with `end_date = NULL` is open-ended.
  - **Time Entry FK.** Time Entry holds `employee_role_id` (mandatory). The rate used for billing is `time_entry.employee_role.rate`. No rate field on Time Entry itself.
  - **Boundary invariant (write guard).** On `create_time_entry` and `edit_time_entry`:
    - `time_entry.date >= employee_role.start_date`
    - `time_entry.date <= employee_role.end_date` (or `employee_role.end_date IS NULL`)
    - Violation rejects at the command guard.
  - **Disjoint-ranges-per-role-type invariant (write guard).** On `create_employee_role` and `edit_employee_role`:
    - For all existing EmployeeRole rows `R` with the same `(employee_id, role_type)`, the candidate's `[start_date, end_date]` must not intersect `R`'s `[start_date, end_date]`.
    - Open-ended rows (`end_date IS NULL`) treat their upper bound as `+∞` for the intersection check.
    - Violation rejects at the command guard.
  - **Rate-change command pattern.** A rate change for Alice's TechRole from rate R1 effective through D, to rate R2 starting D+1, is two operations executed atomically:
    1. `edit_employee_role(current_row, end_date = D)` — closes the open row (or shortens the existing closed row).
    2. `create_employee_role(employee = Alice, role_type = TechRole, rate = R2, start_date = D+1, end_date = NULL)` — opens the new row.
    
    The two commands could be bundled into a `change_employee_role_rate(role, new_rate, effective_date)` compound command for ergonomics; declaring that command is left to the workflows-and-commands consolidation step rather than this ADR.
  - **Role-close command.** `close_employee_role(role, end_date)` sets `end_date` on an open row. Rejects if any Time Entry exists for that employee_role with `time_entry.date > end_date` (closing the role would orphan future-referenced entries).
  - **No state machine.** EmployeeRole has no state field. "Is this role currently valid?" is computed: `start_date <= today AND (end_date IS NULL OR today <= end_date)`. "Was this role valid on date D?" is the same predicate with D substituted. The lifecycle capture history records the discrete grant and close events for audit purposes.
  - **History pattern (unchanged).** Lifecycle capture per ADR-0013. Captures `create_employee_role`, `edit_employee_role`, `close_employee_role` events. Rate-change pattern produces a close event on the old row and a create event on the new row.
  - **Delete policy (unchanged).** Soft-delete per the standard pipeline. Time Entries reference EmployeeRole rows; hard-delete is gated by the existence of references. The legitimate close path is `close_employee_role` (sets `end_date`); soft-delete handles "this row was created in error" correction cases.
  - **Future grants and future-effective closes.** The schema admits `start_date > today` (employee starts a role in the future) and `end_date > today` on an existing row (role scheduled to end). Both are operationally normal — payroll and HR decisions are commonly made in advance. The boundary invariant on Time Entry continues to apply (future Time Entries can reference the future role; past Time Entries cannot).
  - **Retroactive grants.** The schema also admits `start_date < today` for a new row (tracker realizes Alice has been doing TechRole work without a recorded EmployeeRole). Allowed in MVP, but the disjoint-ranges invariant still applies — the retroactive range cannot intersect an existing range for the same `(employee_id, role_type)`.
  - **Temporal rate resolution design pattern (#1) — formalized.** The pattern declared in Step 6a-i is now structurally specified: rate is read by FK traversal from Time Entry → EmployeeRole, with date-range integrity enforced at write time. Future entities needing similar temporal value lookup (e.g., billing rate per `(subtype, TAT)` per ADR-0027 carry-forward) follow the same shape: a temporal record with `(start_date, end_date?)` carrying the value, referenced by FK from the entity that needs the value, with a boundary invariant on the referencing entity's relevant date.
  - **Carry-forward — `change_employee_role_rate` compound command.** Declared as a candidate above; full command spec deferred to workflow-consolidation step.
  - **Carry-forward — retroactive rate corrections.** If post-MVP signal indicates that rate corrections after Time Entries have been written are a real workflow need (e.g., a payroll error discovered weeks later), the Time-Entry-snapshots-rate path becomes attractive. Reversible by adding a `rate_snapshot` field on Time Entry and updating the billing read to prefer the snapshot when present. Not in MVP scope.

---

## ADR-0036 — UserRole atemporal current-state shape, audit on User's log, history-pattern and delete-policy amendments

- **Date:** 2026-05-12
- **Decision:** UserRole is a pure current-state relation: `(user_id, role_type)` composite primary key, no timestamps, no state field, no temporal range. Grant creates the row; revoke hard-deletes it; re-grant creates a fresh row. Grant and revoke audit events are appended to User's audit log (User's already-assigned history pattern), each carrying `(user_id, role_type, actor, timestamp)` plus an optional `reason` field. UserRole's history-pattern assignment changes from lifecycle capture to **no history** — the row has no attributes to track edits on, and the cross-time grant/revoke history lives on User. UserRole's delete-policy assignment changes from soft-delete to **hard delete** — revoke is the operational deletion path, the audit log carries forensics, and UserRole has no incoming references that soft-delete would protect. "Created in error" cases are modeled as a revoke with `reason: 'created_in_error'` on the audit-log event rather than a separate soft-delete pipeline.
- **Status:** accepted
- **Context:** UserRole was identified in Step 6a as the app-access authorization substrate, distinct from EmployeeRole's billing-rate role. Step 6a-ii assigned UserRole lifecycle capture (history pattern) and soft-delete (delete policy) — both inherited from the assumption that UserRole would share temporal grant/revoke shape with EmployeeRole. Deliberation in Step 6b session 7 surfaced that this is wrong: UserRole has no temporal range (no future-effective grants, no scheduled revokes — a user simply has a role or doesn't), no attributes beyond the FK pair, and the cross-time history (when was role X granted, when revoked) belongs operationally on User as part of the user's overall audit trail rather than on UserRole itself. The lifecycle-capture assignment had no edit-events to capture and the soft-delete pipeline had no incoming references to protect.
- **Alternatives considered:**
  - *Lifecycle capture on UserRole (the original ADR-0014-era assignment).* Rejected — UserRole has no editable attributes (just the composite FK), so the only events lifecycle capture would record are creation and deletion. Those events already belong on User's audit log conceptually (they're things that happened to a user). Two audit substrates for the same events.
  - *Soft-delete UserRole rows on revoke, with `revoked_at` timestamp.* Rejected — accumulates revoked rows in the operational table, forces every authorization read to include a `WHERE revoked_at IS NULL` filter, and duplicates the audit affordance that User's audit log already provides. The soft-delete pattern is for "preserve for forensics when something references this row"; UserRole has no incoming references.
  - *Keep `granted_at` timestamp on the UserRole row.* Rejected — consistent shape with EmployeeRole's `start_date`, but provides no value here. EmployeeRole's `start_date` is load-bearing (Time Entries reference EmployeeRole and the date drives rate resolution); UserRole has no analogous downstream consumer of "when was this granted." If a UI needs to show "user has been admin since X," the audit log provides it via the most-recent `grant_user_role` event for that pair. Removing the field keeps the operational table at its minimum viable shape.
  - *Temporal `start_date / end_date?` range on UserRole.* Rejected by the user's framing: "I'll never set a user to be an admin for some date range." Temporal scheduling is not a workflow concern for app-access grants. Adding the fields ahead of demand would be ceremony.
  - *Separate "expunge" command for created-in-error cases (soft-delete pipeline preserved alongside revoke).* Rejected — two operations that do the same thing at the row level (remove the grant) with audit-trail differences. Collapsing into a single revoke command with an optional `reason` field on the audit-log event is the simpler shape.
- **Consequences:**
  - **Schema.** `UserRole = (user_id, role_type)`. Composite primary key (a user holds each role at most once at any moment). No other fields.
  - **Commands.**
    - `grant_user_role(user, role_type, reason?)` — creates the UserRole row (fails if it already exists). Appends `grant_user_role` event to User's audit log with `(user_id, role_type, actor, timestamp, reason?)`.
    - `revoke_user_role(user, role_type, reason?)` — hard-deletes the UserRole row (fails if it doesn't exist). Appends `revoke_user_role` event to User's audit log with `(user_id, role_type, actor, timestamp, reason?)`. `reason: 'created_in_error'` is one possible value for the correction case; free-text or enum shape for `reason` is deferred to authorization-design step (Step 6c).
  - **Audit on User's audit log.** User's pre-assigned audit-log history pattern (per ADR-0014-era assignments) gains two event types: `grant_user_role` and `revoke_user_role`. The audit log is the only cross-time record of UserRole activity.
  - **Re-grant semantics.** After revoke, a subsequent `grant_user_role` creates a fresh row. The audit log preserves the discrete sequence of grant/revoke events for the `(user_id, role_type)` pair; the current row carries no memory of prior grants.
  - **Current-roles query.** Authorization checks read `SELECT role_type FROM user_role WHERE user_id = ?` directly. No filter clauses, no temporal predicates.
  - **Amendment to per-entity history-pattern assignment table.** UserRole moves from "lifecycle capture" to "no history". The history-pattern table reads:
    | Pattern | Entities |
    |---|---|
    | Comprehensive capture | Document, WA, RFA |
    | Lifecycle capture | Project, Sample Batch, Deliverable, EmployeeRole, WA Code |
    | Audit log | Employee, User, Time Entry, Contractor, DepFiling |
    | No history | School, Note, UserRole |
  - **Amendment to per-entity delete-policy table.** UserRole moves from "soft delete (guarded hard-delete eligible)" to "hard delete". The delete-policy table reads:
    | Policy | Entities | Notes |
    |---|---|---|
    | Soft delete (guarded hard-delete eligible) | Document, WA, RFA, Project, Sample Batch, Deliverable, EmployeeRole, Employee, User, Time Entry, Contractor, WA Code, DepFiling | History-carrying or referenced by history records. |
    | Hard delete | School, Note, UserRole | No history, no external history references. |
  - **No state machine, no temporal validity computation.** UserRole's "is this grant active?" question is answered by row existence. No date comparison, no enum check.
  - **Authorization predicate substrate (ADR-0012 carry-forward).** ADR-0012 deferred concrete authorization roles and per-command predicates to a later step (Step 6c). This ADR establishes UserRole as the relation the predicates will read from; the concrete role catalog and predicates remain Step 6c's scope.
  - **Carry-forward — reason field shape.** Whether `reason` on grant/revoke events is free-text, enum, or both is deferred to Step 6c alongside concrete role definition. The audit-log event schema accommodates either shape.
  - **Carry-forward — security-immediate revoke semantics.** "Pull access at end of shift" is operationally a `revoke_user_role` call; whether session invalidation happens out-of-band (active sessions terminated, tokens revoked) is an implementation concern, not a domain decision. The domain shape supports immediate revoke; the runtime mechanics are deferred to the auth implementation step.

---

## ADR-0037 — Project state machine, RFP closure artifact, and cancellation/reopen cascades

- **Date:** 2026-05-12
- **Decision:** Project has three states: `active` (work in progress), `closed` (submitted to SCA; payment cycle open), and `cancelled` (terminated without submission). `close_project(project, rfp_file)` is a compound command that gate-checks ADR-0032's closure predicate, transitions the project's open RFP Document `missing → saved`, and transitions Project `active → closed`, all atomic. `cancel_project(project)` is a compound that cascades — hard-deletes `pending` WAs with no work-referenced codes + their codes (per ADR-0031); withdraws all `in_review` RFAs (under `withdraw_rfa`'s any-tracker authorization, ADR-0031); auto-deletes `draft` RFAs that empty as a side effect (per ADR-0031's existing empty-draft rule); transitions Project `active → cancelled`. `reopen_project` has two forms: from `closed`, `reopen_project(project, rfp_reason: 'rfp_rejected' | 'rfp_withdrawn')` transitions the current `saved` RFP to the named terminal state, derives a new RFP Document in `missing`, and transitions Project `closed → active`; from `cancelled`, `reopen_project(project)` is a pure state-flip (no RFP work, no structural reason capture). A new `document_type` **RFP** joins ADR-0024's bespoke pattern menu with four states (`missing`, `saved`, `rejected`, `withdrawn`); `rejected` and `withdrawn` are terminal. Project joins ADR-0015's Document-derivation source roster: every Project derives exactly one **non-terminal** RFP at any time — initial at project creation, new instance at each reopen-from-`closed` event. Terminal RFPs persist as historical record. ADR-0032's closure-blocker registry grows by one fix-only entry (#10): "project's non-terminal RFP not in `saved` state at closure."
- **Status:** accepted
- **Context:** The Project entity has been the load-bearing root of every other entity in the model since Step 6a, but its concrete lifecycle was deferred until ADR-0032's closure-gate text (the canonical closure predicate) and ADR-0031's RFA state machine (cancellation-cascade dependency) were in place. ADR-0031 explicitly punted "handling of open drafts and `in_review` RFAs on a cancelled project" to this ADR; ADR-0033 confirmed that closure invariants flow through the ADR-0032 registry rather than per-entity re-statement. The closure-artifact piece — that the SCA generates an RFP (Request for Payment) when we submit a project for payment, and that this RFP serves as the system-side closure receipt — emerged in this session's deliberation. Its structural shape parallels the contractor-side CPR's internal payment-request bucket at a different counterparty direction (SCA → us vs. us → contractor) and at the top level (its own `document_type`, not a bucket inside another). The reopen-RFP-replacement mechanic was decided in-session rather than deferred: the operational paths (SCA rejects payment, RFP withdrawn) are common enough that "do we need to handle this?" answered itself.
- **Alternatives considered:**
  - *Four-state machine with a `closing` phase between `active` and `closed`.* Rejected — the `closing` slot has nothing to enforce that the closure-gate UI (surfacing the to-do list of unresolved blockers) doesn't already enforce. Adds an extra command (`initiate_closure`) and an `active ↔ closing` loop that costs lifecycle weight for no operational lever (one tracker per project in MVP, no concurrent-edit pressure). Parallels ADR-0029's rejection of a `returned` Deliverable state — actionable queues, not lifecycle slots.
  - *Five-state machine (`closing` + `cancelling`).* Rejected — symmetric structure for symmetry's sake. `cancel_project` is a one-shot compound (cleanup + terminate), not a phased wind-down; a `cancelling` state has even less operational meaning than `closing`.
  - *Permanent terminals (no reopen).* Rejected — project identity is tied to the SCA-assigned identifier, so a "new project for the same SCA ID" workaround doesn't exist. Operational hits (SCA-payment rejection, rescinded cancellation) are common enough that locked terminals would force operational drift.
  - *RFP as simple `missing → saved` document_type.* Rejected — couldn't capture the reopen-cycle case (SCA rejects, project reopens, original RFP needs to be invalidated). Multi-Document with terminal-state retirement is the cleaner shape: each submission cycle is its own Document with its own outcome state, vs. one Document cycling through repeated `saved` rounds and losing the "first try / second try" temporal record.
  - *Single `closed_out` terminal RFP state with a reason discriminator field (instead of two distinct terminal states).* Rejected — operational events are distinct enough (rejection by SCA vs. withdrawal of the RFP) that distinct state names give cleaner query semantics ("show all rejected RFPs") and a more direct read of the document's lifecycle. The reason-field collapse is a smaller schema but loses the structural distinction.
  - *Reopen-from-`cancelled` requires a structural reason.* Rejected — no downstream state change depends on the reason, and self-reported reasons for course corrections in a tracker tool are unreliable (people will either be dishonest or use it to point fingers). Lifecycle capture records the reopen event; contextual rationale fits a regular user Note on the Project.
  - *Block on `in_review` RFAs at cancellation (require manual `withdraw_rfa` first).* Rejected — ADR-0031 already authorizes `withdraw_rfa` to any tracker, so the cascade doesn't escalate authority. Extra clicks at the most stressful path, plus gap-period risk if SCA approves the RFA mid-flow between manual withdrawal and cancellation.
  - *Mixed cascade policy (cascade drafts, block on `in_review`).* Rejected — draft cascading follows naturally from WA Code cleanup (drafts auto-empty per ADR-0031), so it's not a meaningful policy split. One uniform cascade is simpler.
  - *Project closure where closing IS the submission act (no RFP-saved gate; close transitions atomically with submission to SCA).* Rejected — the SCA portal submission is out-of-band; the RFP arrives back from SCA after submission as the SCA-side receipt. Treating RFP-saved as the closure trigger (via `close_project(rfp_file)`) keeps the system-recorded closure aligned with real-world evidence-of-submission rather than running ahead of it.
  - *Disambiguating "RFP" document_type name (e.g., "SCA RFP" or "Project RFP") to avoid acronym overlap with CPR's internal RFP bucket.* Rejected for MVP — current office vocabulary uses "RFP" without confusion at the two levels (top-level document_type vs CPR-internal bucket), and the two live at different schema levels. Disambiguation can land later if scale or onboarding pressure forces it.
- **Consequences:**
  - **State machine.** Three states with the following transitions:
    - `active → closed`: `close_project(project, rfp_file)` compound. Gate-checks ADR-0032's closure predicate (no `fix-only` blockers + every `dismissable` blocker either no longer holds derivationally OR has an associated dismissal resolution Note); transitions the project's open RFP Document `missing → saved`; transitions Project `active → closed`. All atomic.
    - `active → cancelled`: `cancel_project(project)` compound. See cascade below.
    - `closed → active`: `reopen_project(project, rfp_reason: 'rfp_rejected' | 'rfp_withdrawn')`. Compound: transitions current `saved` RFP → `rejected` or `withdrawn` per reason; derives a new RFP Document in `missing` on the project; transitions Project.
    - `cancelled → active`: `reopen_project(project)`. State-flip + lifecycle-capture record. No RFP change; the project's RFP (in `missing` since cancellation didn't go through closure) carries forward unchanged.
  - **`close_project` semantics.** The gate check reads ADR-0032's blocker registry — no re-statement of invariants in this ADR. All ten current registry entries are project-scope-relevant: entries #1–#9 attach to project-scoped entities (Time Entry, Sample Batch, DepFiling, RFA) or cross-project relationships (#8 — both projects involved per ADR-0028), and entry #10 (added by this ADR) attaches directly to Project. RFP-saved is registry entry #10; from the closure-command's perspective it's just one more registry item. The compound's atomicity ensures the RFP-save and project-close land together — there is no intermediate window where the RFP is saved but the project is still `active`.
  - **`cancel_project` cascade (atomic).** In order:
    1. Hard-delete `pending` WAs whose codes carry no Time Entry or Sample Batch references; hard-delete those codes alongside (per ADR-0031).
    2. Withdraw all `in_review` RFAs targeting the project. Each withdrawn RFA's target codes return `rfa_in_review → pending_rfa` per ADR-0031's `withdraw_rfa` semantics. **Auto-draft regeneration is suppressed on cancelled projects** — no fresh draft makes sense when the project is being terminated.
    3. `draft` RFAs that empty as a result of step 1's code deletions hard-delete per ADR-0031's existing empty-draft rule.
    4. Transition Project `active → cancelled`.
    5. Lifecycle capture records the cancellation event.

    *Not in the cascade:* `issued` WAs and their `issued`/`pending_rfa` codes stay (real work was done; audit preserved). Time Entries, Sample Batches, Deliverables, Documents, DepFilings, Notes all stay attached for audit; no state changes. Closure blockers become operationally moot on a cancelled project but are not structurally cleared — they remain derivable from registry scans, just no longer relevant to any closure command.

    *Authorization:* any tracker (MVP). Per-role refinement deferred to Step 6c.
  - **`cancel_project` does NOT pass through the closure gate.** Cancellation is its own terminal, not a special case of closure. Unresolved blockers do not block cancellation. This is intentional — cancellation is the "abandon the project, leave it for audit" path; gating it on the same predicate as `close_project` would prevent the operational use case (cancelling a project precisely because its blockers can't be resolved).
  - **`reopen_project` from `closed` semantics.** The `rfp_reason` parameter drives the RFP state transition: `'rfp_rejected'` → `saved → rejected`; `'rfp_withdrawn'` → `saved → withdrawn`. The compound is atomic — the new RFP exists in `missing` state from the moment the project flips back to `active`, so the closure-blocker registry (entry #10) immediately surfaces it as unresolved on the now-`active` project.
  - **`reopen_project` from `cancelled` semantics.** State-flip only. No structural reason captured; any contextual rationale attaches as a regular user Note on the Project per ADR-0018. The lifecycle-capture record carries actor + timestamp + transition; that suffices for the audit shape on this path.
  - **RFP `document_type` (new, bespoke).** Joins ADR-0024's bespoke row alongside Lab Report. Per-`document_type` assignment table grows to:
    | Pattern | document_types |
    |---|---|
    | Simple `missing → saved` | ACP13, ACP7, ACP15, ACP21, Emergency Notification, ACP8, VAR9 (DepFiling docs); COC; Daily Log |
    | Cycling-family | CPR (RFA/RFP fork, 5 dates), FAMR (single-step review) |
    | Bespoke | Lab Report (3 states), **RFP (4 states)** |

    **States:** `missing`, `saved`, `rejected`, `withdrawn`.
    **Transitions:**
    - `missing → saved`: at `close_project` time (compound; the only structural path into `saved`).
    - `saved → rejected`: at `reopen_project(project, 'rfp_rejected')` time.
    - `saved → withdrawn`: at `reopen_project(project, 'rfp_withdrawn')` time.
    - `rejected` and `withdrawn` are terminal — no outgoing transitions. Documents in these states persist as the audit record of a closed-out submission cycle.

    **No `missing → invalid` or `invalid → saved` paths** (unlike Lab Report). RFPs are SCA-side documents; we don't receive "defective RFPs" the way labs return defective reports. If SCA sends an RFP that turns out to be problematic, the operational path is reopen-with-`rfp_rejected` and a new RFP for the next cycle.

    **Authorship.** RFP is uploaded by the tracker as part of `close_project`; `authorship_class` (per ADR-0032 amendments to Note schema) does not apply — that field is on Note, not Document. Document's standard `created_by` carries the tracker reference.

  - **Per-Project RFP derivation rule (extends ADR-0015).** Project joins the Document-derivation source roster (currently WA Code, DepFiling, Sample Batch, project events; now adds Project as a direct source). Derivation rule per Project: exactly one RFP in non-terminal state (`missing` or `saved`) at any time. New non-terminal RFPs derive at:
    - Project creation (initial RFP in `missing`).
    - `reopen_project` from `closed` (the new submission cycle starts with a fresh `missing` RFP).

    Per-project invariant: `|{rfp : rfp.project = P, rfp.state ∈ {missing, saved}}| = 1` for every Project P. Terminal RFPs (`rejected`, `withdrawn`) are unbounded; they accumulate as the project cycles through reopen events. This is a different shape from Sample Batch's fixed-2-documents-per-source rule and from DepFiling's editable-required-doc-types rule — RFP derivation is event-driven (cycle-driven) rather than fixed or configurable.

  - **Closure blocker registry amendment (ADR-0032).** New entry appended:

    | # | Blocker | Class |
    |---|---|---|
    | 10 | Project's non-terminal RFP not in `saved` state at closure | Fix-only |

    Classification rationale: no real-world acceptance path. We cannot legitimately close a project without having submitted to SCA, and the RFP-saved state IS the system-side evidence of that submission. The blocker dissolves structurally when the RFP transitions to `saved` via `close_project`'s compound transaction. (Trivially: the blocker holding implies `close_project` hasn't fired, so the close-vs-blocker ordering is mechanically consistent.)

  - **Amendments to other ADRs.**
    - **ADR-0015 (Document-derivation set):** Project added to the derivation-source roster. Derivation rule is the per-project non-terminal-RFP invariant described above — distinct from Sample Batch's fixed-2-documents-per-source rule and DepFiling's editable-required-doc-types rule.
    - **ADR-0024 (Document lifecycle menu):** RFP joins the bespoke option with the four-state machine described above. Per-`document_type` assignment table updated.
    - **ADR-0031 (RFA):** the deferred "handling of open drafts and `in_review` RFAs on a cancelled project" question is resolved by the `cancel_project` cascade above. Auto-draft regeneration is suppressed on cancelled projects.
    - **ADR-0032 (Blocker pattern):** registry grows by entry #10 (fix-only).

  - **History pattern: lifecycle capture (unchanged from prior assignment).** Project state transitions are captured per ADR-0013 pattern 2: `active → closed`, `active → cancelled`, `closed → active`, `cancelled → active` each produce a lifecycle-capture record carrying command, actor, timestamp, and payload (`rfp_file` for `close_project`; `rfp_reason` and the new-RFP-id for `reopen_project` from `closed`; no extra payload for the other two). The new-RFP-id on reopen-from-`closed` is captured so the audit trail directly links the project's reopen event to the new RFP Document that derives from it.

  - **Delete policy: soft delete (unchanged).** Project carries lifecycle capture; history references preclude hard delete. The `cancel_project` path is not deletion — it's a terminal transition; the project record persists.

  - **Authorization: any tracker (MVP).** All three commands (`close_project`, `cancel_project`, `reopen_project`) are authorized to any tracker. Per-role refinement deferred to Step 6c alongside the concrete role catalog (ADR-0012 + ADR-0036 carry-forward).

  - **Naming.** "RFP" is reused for both the new top-level `document_type` (SCA → us) and CPR's internal payment-request bucket (contractor → us). The acronym overlap is accepted: the two live at different schema levels (document_type vs CPR-internal bucket), and current office vocabulary tolerates the ambiguity without operational confusion. Disambiguation deferred until scale or onboarding pressure forces it.

  - **Carry-forwards.**
    - **Per-role authorization predicates** for `close_project`, `cancel_project`, `reopen_project`: Step 6c.
    - **Post-MVP:** SCA-side RFP-rejection notification (would automate the trigger for `reopen_project` rather than requiring tracker action); long-tail "what if SCA never responds to a submission" (currently the `saved` RFP just sits indefinitely; a derived stale-RFP signal could surface later but is not a closure blocker for the original submitter).
