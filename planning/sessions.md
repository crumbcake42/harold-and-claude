# Conceptualization Sessions

Ordered plan for the conceptualization phase of `sca-tracker`. Each session is sized to ~30–60 min and is independently runnable by a fresh Claude given `handoff.md` + `decisions.md` + the session prompt.

The first five sessions are deliberately **domain-agnostic** — the goal is an abstract framework for entities, state, transitions, lifecycle/invariants, authorization, and history patterns before the environmental-monitoring domain is layered on.

---

## Session 1 — Abstract entity & state framework

**Goal:** Define the abstract vocabulary the system will be built on (what is an "entity," what is "state," what is a "transition," what is a "relationship") without referencing the domain.

**Inputs:** `planning/handoff.md`, `planning/decisions.md`

**Outputs:**
- `planning/framework.md` — abstract framework doc
- New ADR entries in `planning/decisions.md` for any framework choices that close off alternatives

**Estimate:** 45–60 min

**Done when:** Reading `framework.md` cold, you can answer: "what does it mean for something to be an entity in this system, and what kinds of state can it have?"

---

## Session 2 — Transitions & history-semantics

**Goal:** Pick the unit of change at the logic layer and what each successful change leaves behind. These two decisions are coupled — picking "events as primary" for the unit largely forces "event-producing" for what's left behind — so they're discussed together.

**Decisions on the table:**
- *Transition unit.* Direct writes, commands as named operations, or events as primary?
  - *Direct writes.* Buys minimal abstraction; gives up a stable attachment point for guards/auth/history.
  - *Commands.* Buys a named surface for auth/guards/history/lifecycle to hang off; gives up some upfront vocabulary cost.
  - *Events as primary.* Buys automatic history; gives up read-side simplicity (projections, snapshots, schema-evolution overhead).
- *History semantics.* Event-producing, state-mutating with mandatory history capture, or state-mutating with bolted-on audit log?
  - *Event-producing.* Buys time-travel and integration-via-stream; gives up read-side simplicity.
  - *State-mutating + mandatory capture.* Buys cheap current-state reads and first-class history; gives up cross-cutting enforcement (drift risk if a write skips capture).
  - *State-mutating + audit log.* Buys minimal overhead. Note: ADR-0003's universal first-class-history commitment is superseded by ADR-0006 (per-entity decision). Audit-log as a per-entity pattern is now in scope for Session 5's menu. Session 2 should address whether it remains off the table as the framework-level default, and what that implies for the Session 5 menu.

**Inputs:** `framework.md`, `decisions.md`, `handoff.md`

**Outputs:**
- `planning/logic.md` — section on transitions and history semantics
- ADR entries for: transition unit, history-leave-behind shape

**Estimate:** 45–60 min

**Done when:** Reading the section cold, you can answer "what is the smallest named thing that changes state, and what does a successful change record?"

---

## Session 3 — Lifecycle rules & invariants

**Goal:** Decide how lifecycle transitions are specified and where invariants are declared and enforced. Coupled because lifecycle rules are temporal invariants — splitting them invites duplicated reasoning.

**Decisions on the table:**
- *Lifecycle specification.* Declarative state machine (graph per entity type), guards as command preconditions, or imperative handlers?
  - *Declarative state machine.* Buys inspectability and model-checkability; gives up ceremony for trivial lifecycles.
  - *Guards on commands.* Buys lightness; gives up a single readable lifecycle definition.
  - *Imperative handlers.* Buys flexibility; gives up consistent lifecycle vocabulary across the system.
- *Invariant declaration & enforcement layer.* On entities, on commands, on read schemas? Write-path only, read-path only, or both?
  - *Write-path enforcement, command-rejection.* Buys clean atomicity boundary; gives up easy cross-entity invariant handling under concurrency.
  - *Read-path only.* Buys flexibility; gives up trustworthy persisted state.
  - *Both layers.* Buys defense in depth; gives up simplicity (two definitions, drift risk).
- *Violation handling.* Reject, error-with-allow, warn, quarantine?

**Inputs:** `framework.md`, `logic.md` (transitions section), `decisions.md`, `handoff.md`

**Outputs:**
- Append to `planning/logic.md` — section on lifecycle rules and invariants
- ADR entries for: lifecycle specification, invariant enforcement layer, violation handling

**Estimate:** 45–60 min

**Done when:** Given an entity from `framework.md`, you can describe its lifecycle vocabulary, where its rules live, and what happens when a write would violate an invariant.

---

## Session 4 — Authorization

**Goal:** Pick the authorization shape and where the predicate lives. Concrete roles and relationships defer to domain mapping (Session 6).

**Decisions on the table:**
- *Primary axis.* Role-based (RBAC), relationship-based (ReBAC), predicate over (caller, command, target), or hybrid?
  - *RBAC.* Buys simplicity and tooling; gives up natural relationship-based access ("the lead of X can edit X").
  - *ReBAC.* Buys natural ownership/membership patterns; gives up off-the-shelf tooling, requires a relationship graph somewhere.
  - *Predicate over (caller, command, target).* Buys generality (subsumes RBAC and ReBAC); gives up tooling and risks unbounded predicate complexity.
- *Predicate location.* On commands, on entities, in a separate policy layer?
- *Form.* Declarative (inspectable, testable) or imperative (code in handlers)?

**Inputs:** `framework.md`, `logic.md`, `decisions.md`, `handoff.md`

**Outputs:**
- Append to `planning/logic.md` — section on authorization
- ADR entry for the authorization shape

**Estimate:** 30–45 min

**Done when:** You can describe how a "can caller C do command X on entity E?" question is answered, in framework terms, without naming any concrete role or relationship.

---

## Session 5 — History & auditing patterns

**Goal:** Define the criteria that determine whether an entity needs historical state, and the menu of history patterns available for those that do. This session must complete before domain mapping — every entity definition in Session 6 requires an explicit history decision chosen from this menu.

**Inputs:** `framework.md`, `logic.md`, `decisions.md`, `handoff.md`

**Outputs:**
- `planning/history-patterns.md` — the menu of available patterns; for each: what it captures, what it commits to structurally, what it gives up, and a prototype example of an entity that would use it
- Selection criteria documenting how to choose between patterns, included in the same file
- ADR entry recording the pattern set and selection criteria

**Estimate:** 30–45 min

**Done when:** Given any entity, you can point to one pattern from the menu and justify the choice using the documented criteria. "No history" is an explicit option. At least two substantively different history-carrying options are available.

---

## Session 6 — Domain mapping

**Goal:** Project the abstract framework onto the actual domain (project-state tracking at an environmental monitoring agency). First pass — identify the real entities, their states, their relationships. Don't worry about completeness; aim for the load-bearing 80%.

**Constraint:** Every entity definition must include a history decision — choose one pattern from `history-patterns.md`. No entity may be defined without it.

**Inputs:** `framework.md`, `logic.md`, `history-patterns.md`, `decisions.md`, `handoff.md`. User will supply domain context in the session prompt.

**Outputs:**
- `planning/domain-model.md` — the mapped domain, with history pattern noted per entity
- ADR entries for domain shape decisions

**Estimate:** 45–60 min

**Done when:** A reader who knows the framework can name the top-level domain entities, how they relate, and which history pattern each carries.

---

## Session 7 — MVP feature cut

**Goal:** Decide what the proof-of-concept must demonstrate. Cut ruthlessly.

**Inputs:** `domain-model.md`, `decisions.md`, `handoff.md`

**Outputs:**
- `planning/mvp.md` — in-scope vs. explicitly-out-of-scope features
- ADR entry recording the MVP scope decision

**Estimate:** 30–45 min

**Done when:** `mvp.md` lists ≤7 must-have features, each one sentence, and a defensible "not now" list.

---

## Session 8 — Stack & architecture

**Goal:** Pick the stack and the architectural shape (monolith? service split? where does state live?). Decide only what the next session needs. History implementation shape (event store vs. append-only tables vs. temporal tables) is resolved here, informed by Session 5's pattern menu.

**Inputs:** `mvp.md`, `framework.md`, `logic.md`, `history-patterns.md`, `decisions.md`, `handoff.md`

**Outputs:**
- ADR entries for: language/runtime, framework, persistence, deployment shape, history implementation shape
- `planning/architecture.md` — one-page sketch (component boxes, data flow)

**Estimate:** 45–60 min

**Done when:** Each major stack/architecture choice has an ADR with at least one alternative considered.

---

## Session 9 — Data model sketch & roadmap

**Goal:** Conceptual data model (entities, attributes, relationships — **not** DDL) plus an implementation roadmap.

**Inputs:** All prior planning files

**Outputs:**
- `planning/data-model.md` — conceptual model
- `planning/roadmap.md` — ordered implementation milestones with rough sizing
- Final ADR entry: "Conceptualization phase complete; implementation begins"

**Done when:** Roadmap has dated milestones, and `handoff.md` is updated to point at the first implementation session.
