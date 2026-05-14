# Conceptualization Steps

## File contract

**Holds:** Ordered list of steps within the current phase — goal, inputs, outputs, done-when criteria, and decision options pre-canvassed for each step.
**Update when:** A step is added, split, reordered, or completed; phase restructuring occurs. Canonical step list; `handoff.md`'s next-session pointer references it by section heading.

Ordered plan for the conceptualization phase of `sca-tracker`. Each step is sized to ~30–60 min and is independently runnable by a fresh Claude given `handoff.md` + `decisions.md` + the step prompt.

The first five steps are deliberately **domain-agnostic** — the goal is an abstract framework for entities, state, transitions, lifecycle/invariants, authorization, and history patterns before the environmental-monitoring domain is layered on.

---

## Step 1 — Abstract entity & state framework

**Goal:** Define the abstract vocabulary the system will be built on (what is an "entity," what is "state," what is a "transition," what is a "relationship") without referencing the domain.

**Inputs:** `planning/handoff.md`, `planning/decisions.md`

**Outputs:**
- `planning/framework.md` — abstract framework doc
- New ADR entries in `planning/decisions.md` for any framework choices that close off alternatives

**Estimate:** 45–60 min

**Done when:** Reading `framework.md` cold, you can answer: "what does it mean for something to be an entity in this system, and what kinds of state can it have?"

---

## Step 2 — Transitions & history-semantics

**Goal:** Pick the unit of change at the logic layer and what each successful change leaves behind. These two decisions are coupled — picking "events as primary" for the unit largely forces "event-producing" for what's left behind — so they're discussed together.

**Decisions on the table:**
- *Transition unit.* Direct writes, commands as named operations, or events as primary?
  - *Direct writes.* Buys minimal abstraction; gives up a stable attachment point for guards/auth/history.
  - *Commands.* Buys a named surface for auth/guards/history/lifecycle to hang off; gives up some upfront vocabulary cost.
  - *Events as primary.* Buys automatic history; gives up read-side simplicity (projections, snapshots, schema-evolution overhead).
- *History semantics.* Event-producing, state-mutating with mandatory history capture, or state-mutating with bolted-on audit log?
  - *Event-producing.* Buys time-travel and integration-via-stream; gives up read-side simplicity.
  - *State-mutating + mandatory capture.* Buys cheap current-state reads and first-class history; gives up cross-cutting enforcement (drift risk if a write skips capture).
  - *State-mutating + audit log.* Buys minimal overhead. Note: ADR-0003's universal first-class-history commitment is superseded by ADR-0006 (per-entity decision). Audit-log as a per-entity pattern is now in scope for Step 5's menu. Step 2 should address whether it remains off the table as the framework-level default, and what that implies for the Step 5 menu.

**Inputs:** `framework.md`, `decisions.md`, `handoff.md`

**Outputs:**
- `planning/logic.md` — section on transitions and history semantics
- ADR entries for: transition unit, history-leave-behind shape

**Estimate:** 45–60 min

**Done when:** Reading the section cold, you can answer "what is the smallest named thing that changes state, and what does a successful change record?"

---

## Step 3 — Lifecycle rules & invariants

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

## Step 4 — Authorization

**Goal:** Pick the authorization shape and where the predicate lives. Concrete roles and relationships defer to domain mapping (Step 6).

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

## Step 5 — History & auditing patterns

**Goal:** Define the criteria that determine whether an entity needs historical state, and the menu of history patterns available for those that do. This step must complete before domain mapping — every entity definition in Step 6 requires an explicit history decision chosen from this menu.

**Inputs:** `framework.md`, `logic.md`, `decisions.md`, `handoff.md`

**Outputs:**
- `planning/history-patterns.md` — the menu of available patterns; for each: what it captures, what it commits to structurally, what it gives up, and a prototype example of an entity that would use it
- Selection criteria documenting how to choose between patterns, included in the same file
- ADR entry recording the pattern set and selection criteria

**Estimate:** 30–45 min

**Done when:** Given any entity, you can point to one pattern from the menu and justify the choice using the documented criteria. "No history" is an explicit option. At least two substantively different history-carrying options are available.

---

## Step 6 — Domain mapping

**Goal:** Project the abstract framework onto the actual domain (project-state tracking at an environmental monitoring agency). Identify the real entities, their states, lifecycles, relationships, and authorization predicates. Aim for the load-bearing 80%.

**Constraint:** Every entity definition must include a history decision — choose one pattern from `history-patterns.md`. No entity may be defined without it.

**Done when:** A reader who knows the framework can name the top-level domain entities, how they relate, their lifecycle vocabularies, their authorization predicates, and which history pattern each carries.

Split into four sub-sessions (6a–6d). Domain context collected in the opening discussion is carried forward in `handoff.md`.

---

### Step 6a — Entity identification

Step 6a's scope (entity roster + cross-system-identity + soft-delete + per-entity history-pattern assignments) exceeded one session. Partitioned across three sessions: 6a-i (entity roster + scoping policies, complete), 6a-ii (history-pattern walk + remaining opens, complete), 6a-iii (use-case stress-test, complete — primary use case done, CPR walkthrough deferred to 6b opening).

Original goal, inputs, and done-when carried across all three sub-sessions: **Identify the domain entities, their intrinsic attributes, and their history-pattern assignments. Address cross-system identity and soft-delete/hard-delete as they bear on entity shape.** Done when the entity list is agreed, each entity has a history-pattern assignment, and the two scoping policies are resolved.

#### Step 6a-i — Entity roster + scoping policies (complete)

**Outputs (in `handoff.md` last session summary):**
- Entity roster (~17 entities)
- Cross-system identity position (deferred indefinitely)
- Soft-delete / guarded-delete position (no new `can_delete` mechanism; standard pipeline + cross-entity acknowledgement gating)
- Major modeling decisions (Document/RequiredDocument unification, set-based document derivation, WA versioning via supersession, EmployeeRole/UserRole split, Project Type as opaque label)
- Three design-pattern names pre-registered (temporal rate resolution, pre-conditional lifecycle gating, derived blocking status)
- Document = comprehensive history; other entities pending

**Actual:** ~60 min discussion, plus context spent on framework re-grounding and process-mode negotiation.

#### Step 6a-ii — History-pattern walk + remaining open modeling questions (complete)

**Goal:** Complete the per-entity history-pattern assignment required by ADR-0006 and resolve open modeling questions surfaced in 6a-i.

**Inputs:** 6a-i outputs (in `handoff.md`), `framework.md`, `history-patterns.md`, `decisions.md`.

**Outputs (in `handoff.md` last session summary):**
- All five open modeling questions resolved (Final Project Package, Document notes, WA versioning, Document→Deliverable cardinality, LabResult)
- Entity roster refined from 17 to 15 (Sample, Inspection, Daily Log dropped; Note added)
- History-pattern assignment for all 15 entities
- Per-entity soft/hard delete policy confirmed
- ADRs 0014–0019 written

**Actual:** ~60 min casual deliberation.

#### Step 6a-iii — Use-case stress-test (complete)

**Goal:** Pressure-test the entity model + set-based derivation + acknowledgement-gating patterns through 1–2 concrete use cases. Surface structural gaps; refine model if needed before proceeding to Step 6b.

**Inputs:** 6a-i + 6a-ii outputs (in `handoff.md`), all prior planning files.

**Outputs (in `handoff.md` last session summary):**
- Primary use case ("samples arrive before the WA is issued") walked through successfully
- Three model adjustments: WA Code project-scoped (ADR-0020), WA Code lifecycle capture (ADR-0021), derivation fires on expected codes with cascading transitions (ADR-0022)
- Three new design patterns: smart command inference, compound cascading commands, WA issuance reconciliation
- No structural gaps found
- Secondary use case (CPR 5-date walkthrough) deferred to Step 6b opening

**Actual:** ~45 min casual deliberation.

**Done when:** Use cases run through the model; no structural gaps surface; ready to proceed to Step 6b. ✓ (Primary use case complete; CPR deferred to 6b where it naturally exercises per-type lifecycle behavior.)

---

### Step 6b — Workflows & lifecycles

**Goal:** Map key workflows to command sequences and concrete lifecycle state machines per entity. Covers: scheduling, sample collection, lab results, document preparation, scope extension, chain-of-custody error handling.

**Inputs:** Step 6a output (via `handoff.md`), `logic.md` (lifecycle/command/invariant sections), `decisions.md`.

**Outputs:**
- Concrete lifecycle vocabularies (state names, transitions) per entity type
- Named commands per entity type
- Invariant declarations (intra-entity and cross-entity)

**Estimate:** 45–60 min

**Done when:** Each entity with a lifecycle has a named state machine; each state change has a named command.

Step 6b's core scope completed across eight sessions (lifecycle ADRs 0027–0037). Two residual command-shape items were deferred and are picked up in Step 6b-residual below.

---

### Step 6b-residual — Workflow-consolidation pass

**Goal:** Close out residual command-shape and state-machine items deferred from Step 6b core, so the Step 6c-ii predicate enumeration has a complete and accurate command surface to work against.

**Items in scope (revised after session 9 deliberation):**

1. **Sample Batch state-machine cleanup + project-state-driven immutability formalization.** Session 9 deliberation reframed the original "billing finalization trigger" item: there is no separate billing event in MVP (the billing flow is a draft-invoice estimator with no state transitions). ADR-0033's `received → billed` transition was speculative based on a misread of `billed`'s semantics. Closure-snapshot membership is `Project.state`-derived, not per-entity sticky. Concrete work for this item:
   - **Amend ADR-0033** to drop the `billed` terminal state. Sample Batch becomes stateless (joins EmployeeRole / DepFiling / Note / UserRole). Lifecycle capture pattern stays (covers `create_sample_batch` and `relink_sample_batch_wa_code` as discrete events without a state field).
   - **Formalize the project-state-driven immutability rule** in the same amending ADR: commands on entities attached to a project in `closed` or `cancelled` state are rejected at command guard, except blocker-dismissal commands (per ADR-0032) and reopen-project commands (per ADR-0037). Confirm exception list during writing.
   - **Decide whether the rule earns a 13th design pattern entry** or just stands as a one-off project-lifecycle consequence.

2. **`change_employee_role_rate` compound command** (ADR-0035 carry-forward). Define the compound's parameters (`role`, `new_rate`, `effective_date`), the atomic sequence (close existing row at `effective_date − 1`, create new row at `effective_date`), guards inherited from the underlying simple commands (disjoint-ranges-per-role-type, no-orphan-future-Time-Entries), any new guards specific to the compound shape, and history-capture shape (one event vs. two underlying + compound marker).

**Out of scope:** authorization predicates (those land in Step 6c-ii); broader billing-design (rates, invoices, etc. — out of MVP).

**Inputs:** ADR-0033, ADR-0035, ADR-0037, `handoff.md` cumulative tables, `decisions.md`.

**Outputs:**
- ADR-0038 (or similar) amending ADR-0033 and formalizing project-state-driven immutability.
- ADR-0039 (or folded into the same ADR) for the rate-change compound command.
- Updated cumulative tables in `handoff.md` (Sample Batch entity row, state-machine list, pattern menu if applicable).

**Estimate:** Spanned two sessions (9 + 10). Session 9 covered deliberation for item 1; session 10 wrote ADR-0038 (item 1) and ADR-0039 (item 2).

**Done when:** ADR-0033's `billed` state is dropped via amendment; project-state-driven immutability rule is written down; rate-change compound is specified concretely enough that a per-command authorization predicate can be written against it without further design ambiguity. ✓ (Complete; ADR-0038 + ADR-0039 landed 2026-05-13.)

---

### Step 6b-residual-2 — Blocker-resolution model reframe

**Goal:** Replace ADR-0032's fix-only/dismissable blocker binary with the `write-off` model: every blocker has a fix path plus — where a coherent one exists — a **default-resolution** command that writes off the conflicting entities so the derived condition no longer holds.

**Why this surfaced:** Step 6c-ii session 13, cluster 7 (cross-project commands). "Fix-only" is partly dishonest — a mechanical acceptance path always exists (mutate the conflicting data until the derived condition dissolves); ADR-0028 calling cross-project overlap "fix-only" just pushed that mutation off-system into manual edits. Bringing it on-system as a defined command is auditable and structured.

**Sequencing — runs *before* ADR-0042 (Step 6c-ii's deferred output).** The reframe adds a default-resolution command family; ADR-0042's job is to enumerate the command surface, so it must wait for that surface to settle. This is the inverse of session 12's call to defer Step 6c-iii until *after* ADR-0042 — the WA restructure leaves predicates unchanged, this reframe does not. Execution order: this step → ADR-0042 write (closes 6c-ii) → Step 6c-iii → Step 6d.

**Items in scope:**

1. **Reassess the fix-only/dismissable binary.** New test: not "is there a real-world acceptance path?" but "does a coherent default-resolution exist?" Expected outcome — the binary shrinks rather than vanishes; #10 (non-terminal RFP not `saved` at closure) is the candidate genuine survivor (the saved RFP *is* what closure means; no entity to write off). One-by-one classification pass over all 11 registry blockers.
2. **Formalize the `write-off` model.** `write-off` / `written-off` (term locked session 13) = umbrella state/concept — an entity that exists but doesn't count (toward billing/conflicts). Carries a **reason**, drawn from the blocker registry (which blocker's default-resolution produced it) — audit/reporting-useful. Reconcile: `write-off` likely **subsumes `non_billable`** (ADR-0027); `wasted` (ADR-0029 Deliverable derived flag) and `invalid` (ADR-0033 Lab Report state) are distinct concepts — decide whether they fold in or stay separate.
3. **Define per-blocker default-resolution commands.** For each blocker with a coherent default-resolution, define the command (worked example: cross-project overlap → split the overlapped span out of both Time Entries and write off the slivers).
4. **Nuclear-option guard.** Default-resolutions are the destructive option; guard them — require a justification Note (per ADR-0032's dismissal-Note precedent), never auto-invoke.
5. ~~Open question — fold in the `dismiss_wa_code` cascade-shape?~~ **Resolved session 14 — dissolved.** The WA-removal redesign (session 14, now captured in Step 6c-iii item 6) keeps the WA Code row on dismissal rather than deleting it, so `wa_code`-scoped Documents never dangle — there is no orphan cascade to design. This item leaves Step 6b-residual-2 entirely; it folds into Step 6c-iii item 6 as a one-line confirmation.

**Session partition (agreed session 14 — Option A, model vs. application):** Step 6b-residual-2 tripped the Case 2 fit checklist (Signal 3 — the estimate itself flagged >1 session) and is split along the model/application dependency seam:
- **Session 14a — write-off model.** Items 1 (binary reassessment, *abstract* — the new test and the reframed binary structure), 2 (formalize the `write-off` model + vocab reconciliation against `non_billable` / `wasted` / `invalid`), 4 (nuclear-option guard). The conceptual half.
- **Session 14b — application.** Item 1 (*concrete* — the one-by-one classification pass over all 11 registry blockers) and item 3 (per-blocker default-resolution command definitions). The enumerative half: apply 14a's model to the registry.
- Seam rationale: 14b's classification ("does a coherent default-resolution exist?") and command definitions depend on 14a's model being fixed first. 14a is focused design; 14b is apply-the-template ×11 + write the registry ADR.

**Note on `write-off` reasons (session 14):** the write-off reason is *not* always blocker-registry-derived. An `expected`-code abandonment via `dismiss_wa_code` (Step 6c-iii item 6) produces a write-off whose reason is "code abandoned pre-issuance" — not a blocker. The 14a model must allow non-blocker reasons.

**Inputs:** ADR-0032 (blocker pattern + registry), ADR-0028 (cross-project overlap), ADR-0027 / ADR-0029 / ADR-0039 (vocab-reconciliation surface — `non_billable`, `wasted`, chain-dismissal pattern #12), ADR-0037 (#10 RFP blocker), `handoff.md` cumulative tables, `decisions.md`.

**Outputs:**
- ADR amending ADR-0032 (registry reclassification + binary reframe) and ADR-0028 (cross-project overlap gains a default-resolution). 14a produces the model-half (binary reframe + `write-off` model + nuclear guard); 14b produces the registry reclassification + per-blocker commands.
- Likely vocab-reconciliation amendments touching ADR-0027 (`non_billable` → `write-off`), possibly ADR-0029 / ADR-0039.
- Updated cumulative tables in `handoff.md` (blocker registry, vocabulary, possibly pattern menu).

**Estimate:** Sized session 14 (Case 2) — does not fit one window. Split into two sessions per the Option A partition above: 14a (write-off model) then 14b (application). Item 5 dissolved.

**Done when:** The fix-only/dismissable binary is reassessed and the `write-off` model is written down; every registry blocker is classified (has-default-resolution vs. genuinely-fix-only); per-blocker default-resolution commands are defined for those that have them; the nuclear-option guard is specified; the command surface is settled enough that ADR-0042 can enumerate it.

---

### Step 6c — Relationships & authorization

**Goal:** Map entity relationships (cardinality, ownership vs. reference, promotion decisions) and concrete authorization predicates. Roles scoped to project managers only (field staff deferred to post-MVP).

Step 6c is partitioned into three sub-sessions (6c-i, 6c-ii, 6c-iii). The original brief is preserved here; sub-session briefs follow. Step 6c-iii (rename + restructure) was added during session 12 deliberation when the domain-model restructure surfaced; it sequences *after* 6c-ii closes so ADR-0042 lands against the current entity surface rather than being double-amended.

**Original inputs:** Steps 6a–6b output (via `handoff.md`), `framework.md` (relationships), `logic.md` (authorization), `decisions.md`.

**Original outputs:**
- Relationship declarations per entity pair (type, cardinality, ownership, promotion rationale)
- Authorization roles and per-command predicates

**Done when:** Every entity-to-entity link is declared with type and cardinality; every command has an authorization predicate.

#### Step 6c-i — Role catalog + relationship declarations

**Goal:** Enumerate the concrete role catalog (per ADR-0036's UserRole substrate; MVP scoped to project-manager / coordinator), and declare entity-to-entity relationships across the full 16-entity roster.

**Inputs:** Step 6a–6b output, `framework.md` (relationships), `decisions.md`, ADR-0036 (UserRole shape).

**Outputs:**
- ADR for the concrete role catalog (role names, descriptions, who-can-grant authority).
- ADR (or extension of the above) covering relationship declarations: for every entity pair that holds a structural link, cardinality + ownership/reference + promotion rationale where applicable. Many pair-links are already declared in their owning entity's ADR (e.g., Time Entry → EmployeeRole in ADR-0035) — this step consolidates and fills gaps (Document ↔ Deliverable M:M; any other unresolved pairs).

**Estimate:** 45–60 min.

**Done when:** The role catalog is enumerated with per-role description; every entity pair with a structural link is declared with cardinality and ownership.

#### Step 6c-ii — Per-command authorization predicates

**Goal:** Write per-command authorization predicates for every named command across Step 6b core ADRs and Step 6b-residual ADRs. Resolves ADR-0012's carry-forward (authorization predicate per command).

**Inputs:** Step 6c-i output (role catalog), all Step 6b + 6b-residual ADRs, Step 6b-residual-2 ADR (blocker-resolution reframe — defines the default-resolution command family ADR-0042 must enumerate), `logic.md` (authorization section), `decisions.md`.

**Outputs:**
- ADR-0042 for the per-command predicate table.

**Estimate:** Deliberation spans sessions 12–13; the ADR-0042 write is deferred until after Step 6b-residual-2. Session 12: four substrate clarifications + clusters 1–5 predicate work in chat. Session 13: clusters 6–7 predicate work in chat — and surfaced the blocker-resolution reframe (now Step 6b-residual-2), which changes the command surface ADR-0042 must enumerate, so the write was deferred behind it. All seven clusters are deliberated; see `planning/handoff.md` last session summary for the locked clarifications and cluster-by-cluster predicate state.

**Done when:** Every named command across the Step 6b + 6b-residual ADR surface has an articulated authorization predicate. Predicates may be uniform (`role ≥ coordinator`, MVP-flat per the locked clarification (1)) for the project-scoped surface; non-uniform predicates (cross-project commands, `grant_user_role` / `revoke_user_role` parameterized per ADR-0040 conservative grant authority, `edit_note` creator-only) called out explicitly. Class-rule clauses cover un-named commands grouped by entity scope. ADR-0042 written.

#### Step 6c-iii — Rename + WA-domain restructure

**Goal:** Land a domain-model restructure that surfaced during Step 6c-ii session 12: introduce a contractual-identity entity above the WA chain, separate static code-type configuration from project-scoped code instances, and rename the M:N link table to a name that grows naturally into the immediate post-MVP budget tracking work. Folds in the Step 6b-residual-2 mis-attribution carry-forward and the WA Code removal model deliberated session 14 (item 6).

**Items in scope:**

1. **Introduce a contractual-identity entity** (working name `WABundle`) parallel to Project. Bundle is the SCA's contract identity — the WA chain (initial + amendments) plus line items. WA Codes live on the bundle (replaces ADR-0020's project-scoping). The bundle gets assigned to a project (M:1).
2. **`WACodeConf` as code-side static config** for the code-type catalog. Possibly code-side rather than DB entity; settled here.
3. **Rename `WAAuthorization`** to a name aligned with the new shape and the budget-priority direction (top contender `WACodeAssignment`).
4. **`reassign_wa_project(wa, new_project, move_work: bool)` compound command** with optional `move_work` flag controlling whether related Time Entries / Sample Batches follow the WA or stay on the original project. Default value settled here.
5. Confirm **Time Entry / Sample Batch keep direct `project_id`** (empirical-truth principle settled session 12) and surface it in the relationship table refresh.
6. **WA Code removal model + `dismiss_wa_code` narrowing + third WA origin.** Deliberated session 14 (productive tangent off Step 6b-residual-2 sizing); shape is settled, this step writes it up.
   - **`dismiss_wa_code` narrowed.** Valid targets: `expected`, `pending_rfa` only — the `issued → dismissed` transition is dropped. Stays a state-transition command and never hard-deletes (ADR-0027's delete-substitution is dropped — it always transitions, even for never-referenced codes; dismissed code rows are kept). Optional `reason_text` parameter → `audit_reason` Note via ADR-0040's existing pattern, attached to the WA Code's lifecycle-capture record for the dismissal event.
   - **New `removed` terminal state.** `issued → removed`, reached when an issued code is removed via an RFA removal line item or an SCA-direct corrected amendment. Distinct from `dismissed` ("never made it onto a WA").
   - **RFA becomes a hybrid instrument.** Line items gain a type: `add | remove | budget` (budget deferred behind budget tracking). Additions stay system-derived from `pending_rfa` codes; removals are coordinator-authored — this scopes ADR-0031's "coordinator cannot manually add or remove line items" principle to additions only. Consequences: draft creation is no longer purely system-triggered (a coordinator adding a removal item can open a draft); `approve_rfa` composition goes from `prior ∪ line items` to `(prior ∪ adds) \ removes`; `approve_rfa` / `reject_rfa` / `withdraw_rfa` resolution becomes polymorphic on line-item type (add-targets → `issued` / `pending_rfa`; remove-targets → `removed` / `issued`).
   - **Third WA origin.** ADR-0030 / ADR-0031 enumerated only two WA origins (initial-external via `issue_wa`; amendment-via-RFA via `approve_rfa`). A third exists: SCA-direct corrected amendment — an externally-arrived amendment WA with no RFA behind it. Needs diff-based reconciliation against the superseded WA (codes added → `issued`; codes dropped → `removed` + cascade; unchanged → `issued`). Likely clean shape to deliberate: one externally-received-WA path handling both initial and SCA-direct amendments, branching on whether `supersedes` is set; `approve_rfa` stays the separate firm-initiated path.
   - **Shared removal cascade.** The cascade (null `wa_code` on referencing Time Entries / Sample Batches → write-off + closure blocker) is shared logic invoked from three triggers: `dismiss_wa_code`, `approve_rfa` (removal line items), and the SCA-direct amendment path.
   - **Item 5 of Step 6b-residual-2 dissolved here.** The WA-Code-scoped Document orphan cascade (ADR-0041 carry-forward) is moot: with the WA Code row kept (not deleted), a `wa_code`-scoped Document still points at a valid row (now `dismissed` / `removed`) — no dangling reference, no cascade needed. Residual sub-question (low urgency): is a Document scoped to a dead code fine as inert evidence, or does it want re-scoping?
   - **Touchpoints / amendments:** ADR-0027 (WA Code state machine — `dismissed` kept, `removed` added, `issued → dismissed` dropped, `dismiss_wa_code` narrowed, delete-substitution dropped, design pattern #9's hard-delete branch no longer exercised by WA Code); ADR-0029 (`wasted` flag re-derivation — extend trigger `dismissed` → `dismissed OR removed`); ADR-0030 (WA origins / `issue_wa` generalization); ADR-0031 (RFA hybrid line-item model); ADR-0033 (`relink_sample_batch_wa_code` guard gains a `removed` branch).

**Out of scope:** Per-command authorization predicates for any new commands introduced here (predicates inherit `role ≥ coordinator` from class rules; explicit rows added to ADR-0042 by amendment if any non-uniform predicate is needed). Budget tracking schema (post-MVP).

**Inputs:** ADR-0020, ADR-0027, ADR-0029, ADR-0030, ADR-0031, ADR-0033, ADR-0041, ADR-0042 (when written — deferred behind Step 6b-residual-2), `planning/handoff.md` Last session summary (session 12 backlog detail + session 14 WA-removal detail).

**Outputs:**
- ADR for the restructure (entity introduction, scoping changes, rename, reassign compound).
- ADR (or section of the restructure ADR) for the item-6 WA Code removal model.
- Amendments to ADR-0020 (scoping rationale), ADR-0027 (WA Code parent ref + state machine: `removed` added, `dismiss_wa_code` narrowed, delete-substitution dropped), ADR-0029 (`wasted` re-derivation), ADR-0030 (WA's project relationship via bundle + third WA origin), ADR-0031 (RFA's bundle-vs-project routing TBD + hybrid line-item model), ADR-0033 (relink guard `removed` branch), ADR-0041 (relationship table refresh).
- Updated cumulative tables in `handoff.md` (entity roster, relationships, vocabulary, WA Code state machine).

**Estimate:** Originally one session; the session-14 addition of item 6 (WA Code removal model) likely pushes it over. Run Case 2 sizing when 6c-iii is reached.

**Done when:** Contractual-identity entity is defined; WA Code's parent is settled (project vs. bundle); WAAuthorization is renamed; `reassign_wa_project(wa, new_project, move_work)` compound is specified with default `move_work` value settled; the item-6 WA Code removal model is written up (`dismiss_wa_code` narrowed, `removed` state, RFA hybrid line-item model, third WA origin); ADR amendments to 0020 / 0027 / 0029 / 0030 / 0031 / 0033 / 0041 written; entity roster + WA Code state machine cumulative tables refreshed.

---

### Step 6d — Domain model assembly

**Goal:** Reconcile sub-session outputs into `planning/domain-model.md`. Address any remaining open questions (quarantine, etc.). Write ADR entries.

**Inputs:** Steps 6a–6c output (via `handoff.md`), all prior planning files.

**Outputs:**
- `planning/domain-model.md` — the mapped domain
- ADR entries for domain-shape decisions

**Estimate:** 30–45 min

**Done when:** `domain-model.md` is written, ADRs are appended, and a reader who knows the framework can name the top-level domain entities, how they relate, their lifecycles, their authorization predicates, and which history pattern each carries.

---

## Step 7 — MVP feature cut

**Goal:** Decide what the proof-of-concept must demonstrate. Cut ruthlessly.

**Inputs:** `domain-model.md`, `decisions.md`, `handoff.md`

**Outputs:**
- `planning/mvp.md` — in-scope vs. explicitly-out-of-scope features
- ADR entry recording the MVP scope decision

**Estimate:** 30–45 min

**Done when:** `mvp.md` lists ≤7 must-have features, each one sentence, and a defensible "not now" list.

---

## Step 8 — Stack & architecture

**Goal:** Pick the stack and the architectural shape (monolith? service split? where does state live?). Decide only what the next step needs. History implementation shape (event store vs. append-only tables vs. temporal tables) is resolved here, informed by Step 5's pattern menu.

**Inputs:** `mvp.md`, `framework.md`, `logic.md`, `history-patterns.md`, `decisions.md`, `handoff.md`

**Outputs:**
- ADR entries for: language/runtime, framework, persistence, deployment shape, history implementation shape
- `planning/architecture.md` — one-page sketch (component boxes, data flow)

**Estimate:** 45–60 min

**Done when:** Each major stack/architecture choice has an ADR with at least one alternative considered.

---

## Step 9 — Data model sketch & roadmap

**Goal:** Conceptual data model (entities, attributes, relationships — **not** DDL) plus an implementation roadmap.

**Inputs:** All prior planning files

**Outputs:**
- `planning/data-model.md` — conceptual model
- `planning/roadmap.md` — ordered implementation milestones with rough sizing
- Final ADR entry: "Conceptualization phase complete; implementation begins"

**Pre-transition ADR consolidation (one-time):** Before writing the final phase-transition ADR, scan `decisions.md` for ADRs with 2+ amendments and consolidate each into a fresh, definitive ADR (mark old ones `superseded by #N`). Per session-9 deliberation: mid-phase compaction loses load-bearing deliberation context, but phase boundary is the right moment — deliberation is settled, and the resulting record becomes the foundation for implementation-phase work. Skip if no ADR has accumulated 2+ amendments by the time Step 9 runs.

**Done when:** Roadmap has dated milestones, and `handoff.md` is updated to point at the first implementation step.
