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

**Sequencing — runs *before* the Step 6c-ii predicate-table ADR (6c-ii's deferred output).** The reframe adds a default-resolution command family; the predicate-table ADR's job is to enumerate the command surface, so it must wait for that surface to settle. This is the inverse of session 12's call to defer Step 6c-iii until *after* the predicate-table ADR — the WA restructure leaves predicates unchanged, this reframe does not. Execution order: session 14a (done) → Step 6c-iv-a (done) → Step 6c-iii-a → Step 6c-iv-b → session 14b → Step 6c-ii predicate-table ADR → Step 6c-iii-b → Step 6d.

**Items in scope:**

1. **Reassess the fix-only/dismissable binary.** New test: not "is there a real-world acceptance path?" but "does a coherent default-resolution exist?" Expected outcome — the binary shrinks rather than vanishes; #10 (non-terminal RFP not `saved` at closure) is the candidate genuine survivor (the saved RFP *is* what closure means; no entity to write off). One-by-one classification pass over all 11 registry blockers.
2. **Formalize the `write-off` model.** `write-off` / `written-off` (term locked session 13) = umbrella state/concept — an entity that exists but doesn't count (toward billing/conflicts). Carries a **reason**, drawn from the blocker registry (which blocker's default-resolution produced it) — audit/reporting-useful. Reconcile: `write-off` likely **subsumes `non_billable`** (ADR-0027); `wasted` (ADR-0029 Deliverable derived flag) and `invalid` (ADR-0033 Lab Report state) are distinct concepts — decide whether they fold in or stay separate.
3. **Define per-blocker default-resolution commands.** For each blocker with a coherent default-resolution, define the command (worked example: cross-project overlap → split the overlapped span out of both Time Entries and write off the slivers).
4. **Nuclear-option guard.** Default-resolutions are the destructive option; guard them — require a justification Note (per ADR-0032's dismissal-Note precedent), never auto-invoke.
5. ~~Open question — fold in the `dismiss_wa_code` cascade-shape?~~ **Resolved session 14 — dissolved.** The WA-removal redesign (session 14, now captured in Step 6c-iii item 6) keeps the WA Code row on dismissal rather than deleting it, so `wa_code`-scoped Documents never dangle — there is no orphan cascade to design. This item leaves Step 6b-residual-2 entirely; it folds into Step 6c-iii item 6 as a one-line confirmation.

**Session partition (agreed session 14 — Option A, model vs. application):** Step 6b-residual-2 tripped the Case 2 fit checklist (Signal 3 — the estimate itself flagged >1 session) and is split along the model/application dependency seam:
- **Session 14a — write-off model. ✓ COMPLETE (2026-05-14, ADR-0042).** Items 1 (binary reassessment, *abstract* — the new test and the reframed binary structure), 2 (formalize the `write-off` model + vocab reconciliation against `non_billable` / `wasted` / `invalid`), 4 (nuclear-option guard). The conceptual half. ADR-0042 captures: `write_off` Note subtype + derived write-off status; default-resolution model + coherence test; binary reframe (`has-default-resolution` / `fix-only` as a property, not gate logic) + closure-gate simplification; nuclear guard (never auto-invoke, mandatory justification); `revoke_write_off`; `resolution_kind` → `structural_fix | default_resolution | dismissal`; vocab (`non_billable` retired, `wasted` → derived label, `invalid` distinct); design pattern #14.
- **Session 14b — application. ✓ COMPLETE (2026-05-15, ADR-0046).** Item 1 (*concrete* — one-by-one classification pass over all 12 registry blockers, including ADR-0044's #12) and item 3 (per-blocker default-resolution command definitions). Ran as three deliberation clusters + the ADR-write turn. 14b-partial (2026-05-14) settled Cluster 1 (#1, #2, #9, #11) + Decision 0 (Hybrid command shape) in chat; 14b-continued (2026-05-15) settled Clusters 2 and 3, then wrote ADR-0046. **Outcomes:** 11 entries `has-default-resolution`, 1 `fix-only` (#10); Hybrid command shape — generic `default_resolve` covers 8 entries, three named compounds cover #7 (`resolve_open_rfa`, MVP add/remove-RFA case) and #8 (`resolve_overlap` / `resolve_overlap_paired` for single-side vs. joint paired-blocker resolution); one reusable named chain shape `te_batches_by_coverage` (4 instances — #5, #8, #11, #12); ADR-0032 registry schema extended with per-entry default-resolution metadata; Cluster-1 structural follow-ons landed (Fork A relink-gate relaxation, #9 chain-dismissal instance dissolved, #11 chain reframed to direct `write_off` Notes via the named chain).
- Seam rationale: 14b's classification ("does a coherent default-resolution exist?") and command definitions depend on 14a's model being fixed first. 14a is focused design; 14b is apply-the-template ×12 + write the registry ADR.

**Note on `write-off` reasons (session 14):** the write-off reason is *not* always blocker-registry-derived. An `expected`-code abandonment via `dismiss_wa_code` (Step 6c-iii item 6) produces a write-off whose reason is "code abandoned pre-issuance" — not a blocker. The 14a model must allow non-blocker reasons.

**Inputs:** ADR-0032 (blocker pattern + registry), ADR-0028 (cross-project overlap), ADR-0027 / ADR-0029 / ADR-0039 (vocab-reconciliation surface — `non_billable`, `wasted`, chain-dismissal pattern #12), ADR-0037 (#10 RFP blocker), `handoff.md` cumulative tables, `decisions.md`.

**Outputs:**
- ADR amending ADR-0032 (registry reclassification + binary reframe) and ADR-0028 (cross-project overlap gains a default-resolution). 14a produces the model-half (binary reframe + `write-off` model + nuclear guard); 14b produces the registry reclassification + per-blocker commands.
- Likely vocab-reconciliation amendments touching ADR-0027 (`non_billable` → `write-off`), possibly ADR-0029 / ADR-0039.
- Updated cumulative tables in `handoff.md` (blocker registry, vocabulary, possibly pattern menu).

**Estimate:** Sized session 14 (Case 2) — does not fit one window. Split into two sessions per the Option A partition above: 14a (write-off model, ✓ complete) then 14b (application, ✓ complete across 14b-partial 2026-05-14 + 14b-continued 2026-05-15). Item 5 dissolved.

**Done when:** The fix-only/dismissable binary is reassessed and the `write-off` model is written down (✓ 14a / ADR-0042); every registry blocker is classified (has-default-resolution vs. genuinely-fix-only); per-blocker default-resolution commands are defined for those that have them; the nuclear-option guard is specified (✓ 14a / ADR-0042); the command surface is settled enough that the Step 6c-ii predicate-table ADR can enumerate it. ✓ (Complete; ADR-0046 landed 2026-05-15.)

---

### Step 6c — Relationships & authorization

**Goal:** Map entity relationships (cardinality, ownership vs. reference, promotion decisions) and concrete authorization predicates. Roles scoped to project managers only (field staff deferred to post-MVP).

Step 6c is partitioned into sub-sessions (6c-i, 6c-ii, 6c-iii, 6c-iv). Two later splits, both 2026-05-14: 6c-iv split Option A into 6c-iv-a / 6c-iv-b; 6c-iii split into 6c-iii-a / 6c-iii-b when the Contract work established that the contract attaches to the WABundle, pulling WABundle introduction forward. The original brief is preserved here; sub-session briefs follow. Step 6c-iii (rename + restructure) was added during session 12 deliberation when the domain-model restructure surfaced; **6c-iii-a** (WABundle entity + contract re-attachment) executes early — ahead of 6c-iv-b, which depends on it — while **6c-iii-b** (the rename + WA-removal-model remainder) sequences *after* 6c-ii closes so the predicate-table ADR lands against the current entity surface rather than being double-amended. Step 6c-iv (Contract entity) was added 2026-05-14 as a new requirement; despite the label it executes ahead of 6c-ii's predicate-table ADR and 6c-iii-b — see its own execution-order note.

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

**✓ COMPLETE (2026-05-15, ADR-0047).** Per-`(role, command)` predicate table written. Two row types — explicit per-command rows for ADR-named commands plus class-rule clauses for unnamed commands grouped by entity scope. Three class rules — Cluster 1 admin-roster CRUD on {Employee, School, Contractor, User}, Cluster 4 Time Entry CRUD + DepFiling CRUD + per-`document_type` lifecycle dispatch (ADR-0024). Non-uniform predicates called out: `grant_user_role` / `revoke_user_role` parameterized per ADR-0040; `edit_note` creator-only (`caller == note.created_by`, non-chain — superadmin not exempt); `edit_wabundle` `role >= admin` per ADR-0044 (sits among WA-domain commands that are otherwise `role >= coordinator`). Four locked clarifications codified (MVP-flat coordinator scoping; project-state immutability stays a pre-condition; no system-caller primitive; `dismiss_wa_code` cascade-shape scope-flagged). Cascade rule + propagation rule + evaluation-order rule codified. `revoke_write_off` included (`role >= coordinator`, scenario (a) — general write-off lift; scenario (b) — misattribution-on-closed-project recovery — documented as a layered post-MVP compound needing `revoke_write_off` + ADR-0038 closed-project exception + cross-project Sample Batch reassignment). `split_entry` included (`role >= coordinator`). Resolves ADR-0012's per-command-predicate enumeration carry-forward.

**Goal:** Write per-command authorization predicates for every named command across Step 6b core ADRs and Step 6b-residual ADRs. Resolves ADR-0012's carry-forward (authorization predicate per command).

**Inputs:** Step 6c-i output (role catalog), all Step 6b + 6b-residual ADRs, the Step 6b-residual-2 ADRs (ADR-0042 blocker-resolution reframe + 14b's registry ADR — together they define the default-resolution command family this predicate-table ADR must enumerate), `logic.md` (authorization section), `decisions.md`.

**Outputs:**
- ADR-0047 — per-command predicate table.

**Actual:** Deliberation spanned sessions 12–13 (clusters 1–7 + four locked clarifications); ADR write was deferred behind Step 6b-residual-2 and Step 6c-iv. ADR-0047 written 2026-05-15 in a single Case 3 scoped session — deliberation already settled, this session was the write itself.

**Done when:** Every named command across the Step 6b + 6b-residual ADR surface has an articulated authorization predicate. Predicates may be uniform (`role ≥ coordinator`, MVP-flat per the locked clarification (1)) for the project-scoped surface; non-uniform predicates (cross-project commands, `grant_user_role` / `revoke_user_role` parameterized per ADR-0040 conservative grant authority, `edit_note` creator-only) called out explicitly. Class-rule clauses cover un-named commands grouped by entity scope. The predicate-table ADR is written. ✓ (Complete; ADR-0047 landed 2026-05-15.)

#### Step 6c-iii-a — WABundle entity, WA restructure, contract re-attachment

**✓ COMPLETE (2026-05-14, ADR-0044).** WABundle introduced (entity #20 — `contract_id` required at create, three nullable-pre-issuance/unique SCA identifiers, audit log, soft delete, no state machine); WA restructured under it (`wabundle_id`, `version_seq` replacing `supersedes`, WA → Project derived, "version" vocabulary); Contract re-attached to the WABundle (amends ADR-0043 — `Project.contract_id` removed, contract mutable via `issue_wa` / `edit_wabundle`, `reassign_project_contract` dissolved); WA-initialization closure blocker added (amends ADR-0032). `create_project` is now a Project + WABundle + v0-WA compound. Amends ADR-0043 / 0017 / 0030 / 0041 / 0032.

**Added 2026-05-14**, mid Step 6c-iv-b's planning. The Contract work (ADR-0043) retrofitted the contract onto Project, but deliberation established the contract is carried by the WA, not the project — so it re-attaches to the **WABundle** (the contractual-identity entity, originally 6c-iii item 1). WABundle introduction is pulled forward out of 6c-iii (now 6c-iii-b) because 6c-iv-b's `→ contract` resolution path depends on it.

**Execution order:** runs after 6c-iv-a, *before* 6c-iv-b. Order: 14a (done) → 6c-iv-a (done) → **6c-iii-a** → 6c-iv-b → 14b → Step 6c-ii predicate-table ADR → 6c-iii-b → 6d.

**Goal:** Introduce WABundle as the contractual-identity entity, restructure WA to sit under it, and re-attach Contract to WABundle — amending ADR-0043. Unblocks 6c-iv-b.

**Settled inputs (not re-deliberated):**
- **Project ↔ WABundle is 1:1; WA → WABundle is M:1** — the bundle holds the WA chain (initial + revisions).
- WABundle carries: a contract link, WA Number, Service ID, Job Number (SCA's WA identifier, distinct from the project number — our own tracking id).
- A WA revision may change only its WA Codes, `issued_date`, and `initialization_date`.
- A new project with no issued WA initializes its WABundle with a first "missing" WA carrying expected WA Codes.

**Items in scope:**

1. **WABundle entity definition** — natural key (among WA Number / Service ID / Job Number, per ADR-0005's UUID-identity + uniqueness-constraint discipline); the field set; history pattern (from `history-patterns.md`); delete policy.
2. **WA restructure** — WA sits under WABundle; WA's direct Project reference becomes derived-via-bundle; WA's own fields (`issued_date`, `initialization_date`); WA identity within the chain.
3. **Contract re-attachment** — WABundle → Contract; amend ADR-0043 (Project.contract_id removed or demoted to a soft expected-contract; `create_project` parameter change; contract becomes authoritative-at-WA-issuance, correctable).

**Out of scope — stays in 6c-iii-b:** WA Code reparenting (stays project-scoped per ADR-0020 for now — with Project ↔ WABundle 1:1 the `code → contract` path resolves either way), `WACodeConf`, the `WAAuthorization` rename, `reassign_wa_project` and the bundle ↔ project assignment-mutability question, the WA Code removal model.

**Parked, to slot:** the `initialization_date` *closure-blocker* semantics — time entries dated before the most-recent non-superseded WA's `initialization_date` are blocked. The field itself lands here; the blocker behavior is a circle-back item, decided before wrap if context permits, else scheduled.

**Inputs:** ADR-0017 (WA supersession), ADR-0020 (WA Code scoping), ADR-0030 (WA state machine), ADR-0041 (relationships), ADR-0043 (Contract), `handoff.md`'s Step 6c-iii backlog block + cumulative tables.

**Outputs:** WABundle-introduction ADR + ADR-0043 amendment (likely one ADR); amendments to ADR-0020 / 0030 / 0017 / 0041 as needed; updated cumulative tables in `handoff.md` (entity roster 19 → 20, relationships, history-pattern + delete-policy assignments).

**Estimate:** One session — three coupled decisions landing as one restructure. Split risk low (the cardinality reconciliation that was the sizing wildcard is now settled); flag a wrap point if it bloats.

**Done when:** WABundle is defined (key, fields, history pattern, delete policy); WA's restructure relative to WABundle is settled; Contract is re-attached to WABundle and ADR-0043 is amended; the ADR(s) are written; cumulative tables refreshed.

---

#### Step 6c-iii-b — Rename + WA-domain restructure (remainder)

**Goal:** Land the remainder of the WA-domain restructure that surfaced during Step 6c-ii session 12, after **Step 6c-iii-a** introduces the WABundle entity. Separates static code-type configuration from project-scoped code instances, renames the M:N link table to a name that grows naturally into the immediate post-MVP budget tracking work, and reparents WA Codes onto the WABundle. Folds in the Step 6b-residual-2 mis-attribution carry-forward and the WA Code removal model deliberated session 14 (item 6).

**Session partition (agreed 2026-05-15 — by item-cluster seam):** Step 6c-iii-b tripped the Case 2 fit checklist — **Signal 1** (two independently-deliberable decision clusters: items 1–5 = WABundle restructure surface, item 6 = WA Code removal model + RFA hybrid line items + third WA origin), **Signal 3** (>60 min — item 6 alone carries 5+ ADR amendments on top of items 1–5's own touchpoints), **Signal 5** (cross-concern reach: entity/relationship/scoping vs. state-machine/command-surface/RFA model). Split along the item-cluster seam:
- **Step 6c-iii-b-i — WABundle restructure surface.** Items 1–5.
- **Step 6c-iii-b-ii — WA Code removal model.** Item 6.
- Seam rationale: items 1–5 share the WABundle as their pivot (entity, relationship, identifier work); item 6 is state-machine surgery + RFA hybrid line-item model + cascade design whose only contact with the restructure is that WA Codes happen to live on the bundle. Time Entry / Sample Batch (item 5) stay project-scoped, so item 6's cascade design is independent of the reparent.

**Execution order:** 6c-iii-b-i → 6c-iii-b-ii. Listed order in the brief; item 6's cascade reads cleaner against the post-reparent relationship picture.

**Items in scope:**

1. **WA Code reparenting onto the WABundle** (replaces ADR-0020's project-scoping). The WABundle entity itself is introduced in **Step 6c-iii-a** (Project ↔ WABundle 1:1, WA → WABundle M:1 settled there); this step moves WA Codes to live on the bundle. *The original "introduce a contractual-identity entity" item moved to 6c-iii-a, where the Contract attaches to it.*
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

**Out of scope:** Per-command authorization predicates for any new commands introduced here (predicates inherit `role ≥ coordinator` from class rules; explicit rows added to the Step 6c-ii predicate-table ADR by amendment if any non-uniform predicate is needed). Budget tracking schema (post-MVP).

**Inputs:** ADR-0020, ADR-0027, ADR-0029, ADR-0030, ADR-0031, ADR-0033, ADR-0041, the Step 6c-ii predicate-table ADR (when written — deferred behind Steps 6b-residual-2 and 6c-iv), `planning/handoff.md` Last session summary (session 12 backlog detail + session 14 WA-removal detail).

**Outputs:**
- ADR for the restructure (WA Code reparenting, scoping changes, rename, reassign compound).
- ADR (or section of the restructure ADR) for the item-6 WA Code removal model.
- Amendments to ADR-0020 (scoping rationale), ADR-0027 (WA Code parent ref + state machine: `removed` added, `dismiss_wa_code` narrowed, delete-substitution dropped), ADR-0029 (`wasted` re-derivation), ADR-0030 (WA's project relationship via bundle + third WA origin), ADR-0031 (RFA's bundle-vs-project routing TBD + hybrid line-item model), ADR-0033 (relink guard `removed` branch), ADR-0041 (relationship table refresh).
- Updated cumulative tables in `handoff.md` (entity roster, relationships, vocabulary, WA Code state machine).

**Estimate:** Sized 2026-05-15 — Case 2 fit checklist signals 1 (independently-deliberable decision clusters), 3 (>60 min), 5 (cross-concern reach) fired. Split along the item-cluster seam into 6c-iii-b-i (items 1–5, WABundle restructure surface) + 6c-iii-b-ii (item 6, WA Code removal model).

**Done when:** WA Codes are reparented onto the WABundle; WAAuthorization is renamed; `reassign_wa_project(wa, new_project, move_work)` compound is specified with default `move_work` value settled; the item-6 WA Code removal model is written up (`dismiss_wa_code` narrowed, `removed` state, RFA hybrid line-item model, third WA origin); ADR amendments to 0020 / 0027 / 0029 / 0030 / 0031 / 0033 / 0041 written; entity roster + WA Code state machine cumulative tables refreshed.

---

##### Step 6c-iii-b-i — WABundle restructure surface

**Goal:** Land items 1–5 of Step 6c-iii-b — the WABundle-reparenting + rename + reassignment surface. State-machine and RFA-model work (item 6) deferred to 6c-iii-b-ii.

**In scope:**
- **Item 1 — WA Code reparenting onto WABundle.** Move WA Code's parent reference from Project (ADR-0020) to WABundle (ADR-0044). Mechanical given Project ↔ WABundle 1:1. Shortens the contract-resolution path (ADR-0045) from `code → project → WABundle → contract` to `code → WABundle → contract`. Amends ADR-0020.
- **Item 2 — `WACodeConf` as code-side static config** for the code-type catalog. Settle: DB entity vs. pure code-side config. Step 6c-iv-b's WA Code default flat fee (ADR-0045) keys on code type — inherits whatever shape lands here.
- **Item 3 — Rename `WAAuthorization` → `WACodeAssignment`** (top contender). Aligns with immediate post-MVP budget priority. Amends ADR-0041.
- **Item 4 — `reassign_wa_project(wa, new_project, move_work: bool)` compound.** With Project ↔ WABundle 1:1, the semantics of "reassign WA's project" need deliberation (does the WA move to a different bundle? does only the WA move while WA Codes stay on the old bundle?). `move_work` default value settled here. Folds in the mis-attribution carry-forward.
- **Item 5 — Confirm direct `project_id` on Time Entry / Sample Batch** (settled session 12 per the empirical-truth principle). Surface in the relationship-table refresh.

**Inputs:** ADR-0020 (WA Code scoping), ADR-0030 (WA state machine), ADR-0041 (relationships), ADR-0044 (WABundle), ADR-0045 (contract-resolution path), `handoff.md` cumulative tables.

**Output:** ADR for the WABundle restructure surface (WA Code reparenting + `WACodeConf` decision + rename + `reassign_wa_project` + relationship-table refresh). Amends ADR-0020, ADR-0030, ADR-0041. Updated cumulative tables in `handoff.md` (entity roster — WA Code parent change; relationships; vocabulary — `WACodeConf`, `WACodeAssignment`, `reassign_wa_project`).

**Done when:** WA Code's parent is reparented onto WABundle; `WACodeConf` placement settled (DB entity vs. code-side); `WAAuthorization` renamed (likely `WACodeAssignment`); `reassign_wa_project` semantics + `move_work` default settled; direct `project_id` on Time Entry / Sample Batch confirmed in the relationship-table refresh; the ADR is written; cumulative tables refreshed.

---

##### Step 6c-iii-b-ii — WA Code removal model

**Goal:** Land item 6 of Step 6c-iii-b — WA Code removal model + `dismiss_wa_code` narrowing + new `removed` terminal + RFA hybrid line-item model + third WA origin + shared removal cascade. Deliberated session 14; shape is settled, this step writes it up.

**In scope:**
- `dismiss_wa_code` narrowed: valid targets `expected` / `pending_rfa` only; `issued → dismissed` dropped; never hard-deletes (ADR-0027's delete-substitution dropped); optional `reason_text` → `audit_reason` Note via ADR-0040.
- New `removed` terminal state: `issued → removed` via RFA removal line item or SCA-direct corrected amendment.
- RFA hybrid instrument: line items typed `add | remove | budget` (budget deferred behind budget tracking); additions stay system-derived, removals coordinator-authored; `approve_rfa` composition `(prior ∪ adds) \ removes`; resolution polymorphic on line-item type.
- Third WA origin: SCA-direct corrected amendment (no RFA behind it); diff-based reconciliation against superseded WA (codes added → `issued`; codes dropped → `removed` + cascade; unchanged → `issued`). Likely shape: one externally-received-WA path branching on the version-chain marker, with `approve_rfa` staying the separate firm-initiated path.
- Shared removal cascade across three triggers (`dismiss_wa_code`, `approve_rfa` removal line items, SCA-direct amendment path): **inherits ADR-0048 §4's cascade-keep-FK principle** — keep the `wa_code` FK on referencing Time Entries / Sample Batches (the dismissed / removed code stays referenceable in its terminal state); emit a `write_off` Note on each referencing record, inheriting the trigger's reason; closure-blocker shape per ADR-0042 / ADR-0046 (new predicate replacing the retired #1 / #2; precise shape settles in this step).

**Inputs:** ADR-0027 (WA Code state machine), ADR-0029 (`wasted` derivation), ADR-0030 (WA state machine / origins), ADR-0031 (RFA state machine), ADR-0033 (relink guard), ADR-0044 (WABundle), ADR-0046 (write-off model), 6c-iii-b-i's restructure ADR (when written).

**Output:** ADR for the WA Code removal model (next number: **ADR-0049**; 6c-iii-b-i landed as ADR-0048 separately). Amends ADR-0027 (`removed` added, `dismiss_wa_code` narrowed, delete-substitution dropped, full cascade restated under cascade-keep-FK), ADR-0029 (`wasted` re-derivation — trigger extended `dismissed` → `dismissed OR removed`), ADR-0030 (third WA origin / `issue_wa` generalization), ADR-0031 (RFA hybrid line-item model), ADR-0033 (`relink_sample_batch_wa_code` guard gains a `removed` branch), **ADR-0042 / ADR-0046** (full cascade restatement under keep-FK principle; formal removal of registry entries #1 and #2; ADR-0046's `default_resolve` dispatch rows for #1 / #2 retired). Updated cumulative tables — WA Code state machine, vocabulary, blocker registry (12 → 10 entries before any new post-cascade predicate lands).

**Done when:** `dismiss_wa_code` narrowing + `removed` terminal + RFA hybrid line-item model + third WA origin + shared cascade (under cascade-keep-FK) are written up; ADR amendments to 0027 / 0029 / 0030 / 0031 / 0033 / 0042 / 0046 written; blocker registry trimmed (#1 / #2 formally removed); cumulative tables refreshed.

---

#### Step 6c-iv — Contract entity (new requirement, 2026-05-14)

**Execution order:** the `6c-iv` label places it in the relationships family for topical coherence (it introduces an entity, new relationships, and an invariant restructure); it does **not** execute after 6c-iii. Order: 14a (done) → 6c-iv-a (done) → **Step 6c-iii-a** (inserted 2026-05-14) → **6c-iv-b** → 14b → Step 6c-ii predicate-table ADR → 6c-iii-b → 6d. 6c-iv-b is gated behind 6c-iii-a — its contract-resolution path runs through the WABundle.

**Goal:** Introduce the **Contract** entity and retrofit the model: projects are opened against a contract; EmployeeRole rates and WA Code default flat fees become contract-scoped. Entity roster 18 → 19.

**Why this surfaced:** New requirement given 2026-05-14. Contracts define rate schedules (employee role rates) and code default flat fees; previously deferrable because new contracts are rare, but one was just signed, making it immediately relevant.

**Session partition (agreed 2026-05-14 — Option A, model vs. application):** Step 6c-iv tripped the Case 2 fit checklist — **Signal 1** (three independently-deliberable decisions: Contract entity definition + attachment-model fork / EmployeeRole invariant restructure / WA Code flat-fee scoping) and **Signal 5** (cross-concern reach: entity identification + rate resolution + WA Code config). Split along the model/application dependency seam, mirroring Step 6b-residual-2's Option A:
- **Step 6c-iv-a — Contract entity + Project wiring.** Items 1 + 2. The model half: what a Contract *is*, plus the load-bearing fork — does the rate / flat-fee schedule attach inline on Contract, or do EmployeeRole / WA Code rows FK to Contract and carry their own values?
- **Step 6c-iv-b — contract-scoping retrofit.** Items 3 + 4 + 5. The application half: apply 6c-iv-a's attachment decision to EmployeeRole and WA Code.
- Seam rationale: items 3 and 4 cannot be deliberated concretely until the attachment model is fixed in 6c-iv-a — the same model/application dependency seam used for Step 6b-residual-2.

**Items in scope:**

1. **Contract entity definition.** Attributes (contract identifier; effective dating?; how the rate schedule and code flat-fee schedule attach — inline on Contract vs. EmployeeRole / WA Code rows FK-ing to Contract and carrying their own values); history pattern (from `history-patterns.md`); delete policy; lifecycle/state (likely none, or `active` / `expired` — to deliberate).
2. **Project → Contract relationship.** M:1 mandatory, set at `create_project` (admin-side per ADR-0040 cluster 1). `create_project` gains a contract parameter. Mutability after creation — to deliberate (likely immutable: a project's contract is its contractual basis).
3. **EmployeeRole contract-scoping.** EmployeeRole gains a `contract_id`; the disjoint-ranges invariant moves from per-`(employee, role_type)` to per-`(employee, role_type, contract)` — an employee can hold the same role at different rates on different contracts, overlapping in time. Rate-resolution lookup `(employee, role_type, date)` → `(employee, role_type, contract, date)`, with the contract resolved Time Entry → project → contract. `change_employee_role_rate` (ADR-0039) dispatch keys on `(employee, role_type, contract)`. Amends ADR-0035, ADR-0039, ADR-0041.
4. **WA Code default flat fee against contract.** A WA Code's default flat fee is contract-defined (looked up by code type + contract). Interacts with the deferred budget-tracking work and with Step 6c-iii's `WACodeConf` idea — since 6c-iv runs first, it defines the contract side cleanly and 6c-iii's `WACodeConf` work inherits it. Amends ADR-0020 / ADR-0027.
5. **Blast-radius bound (user-stated — confirm, do not re-litigate):** the logic relating codes to required docs / Deliverables / Sample Batches / etc. is **unaffected** by the Contract introduction.

**Inputs:** ADR-0035 (EmployeeRole temporal shape), ADR-0039 (`change_employee_role_rate`), ADR-0020 (WA Code project-scoping), ADR-0027 (WA Code state machine), ADR-0037 (Project / `create_project`), ADR-0040 (admin-side roster management), ADR-0041 (relationships), `history-patterns.md`, `handoff.md` cumulative tables, `decisions.md`.

**Outputs:**
- **6c-iv-a:** ADR introducing Contract + the Project → Contract relationship + the attachment model. Entity roster 18 → 19; updated cumulative tables in `handoff.md` (roster, relationships, history-pattern assignments, delete-policy).
- **6c-iv-b:** retrofit ADR — amendments to ADR-0020, ADR-0027, ADR-0035, ADR-0039, ADR-0041 (and ADR-0037 if `create_project` text needs follow-up). Updated cumulative tables as needed.

**Done when:** Contract entity is defined (attributes, history pattern, delete policy, lifecycle); the attachment model (inline vs. FK) is settled; Project → Contract relationship is declared and `create_project` updated; EmployeeRole's contract-scoped uniqueness invariant + rate-resolution lookup + `change_employee_role_rate` impact are settled; WA Code default-flat-fee-against-contract is settled; blast-radius bound confirmed; both ADRs written; cumulative tables refreshed.

---

##### Step 6c-iv-a — Contract entity + Project wiring

**✓ COMPLETE (2026-05-14, ADR-0043).** Attachment model settled — lands split: employee rates FK-side (EmployeeRole keeps `rate`, gains `contract_id` in 6c-iv-b), code default flat fees inline on Contract's non-temporal `code_flat_fee_schedule`. Contract = `contract_number` + `start_date`/`end_date?` + `code_flat_fee_schedule` + optional `name`; no state machine (validity derived from dates); audit log; soft delete. `Project.contract_id` M:1 mandatory, immutable in MVP; `create_project` gains a `contract` param (amends ADR-0037). `reassign_project_contract` recorded as a post-MVP carry-forward.

**Goal:** Define the **Contract** entity and wire it to Project. The model half of Step 6c-iv — covers items 1 + 2 of the shared brief.

**In scope:**
- **Item 1 — Contract entity definition.** Attributes (contract identifier; effective dating?); **the load-bearing fork — does the rate schedule + code flat-fee schedule attach inline on Contract, or do EmployeeRole / WA Code rows FK to Contract and carry their own values?**; history pattern (from `history-patterns.md`); delete policy; lifecycle/state (likely none, or `active` / `expired`).
- **Item 2 — Project → Contract relationship.** M:1 mandatory, set at `create_project` (admin-side per ADR-0040 cluster 1); `create_project` gains a contract parameter; post-creation mutability (likely immutable: a project's contract is its contractual basis).

**Inputs:** ADR-0037 (Project / `create_project`), ADR-0040 (admin-side roster management), ADR-0041 (relationships), `history-patterns.md`, `handoff.md` cumulative tables, `decisions.md`. ADR-0035 / ADR-0039 / ADR-0020 / ADR-0027 are read for context but amended in 6c-iv-b.

**Output:** The Contract-introduction ADR (entity definition + Project → Contract relationship + the attachment model). Entity roster 18 → 19; updated cumulative tables in `handoff.md`.

**Done when:** Contract entity is fully defined (attributes, history pattern, delete policy, lifecycle); the attachment model (inline vs. FK) is settled; Project → Contract is declared and `create_project` updated; the ADR is written; cumulative tables refreshed. ✓ (Complete; ADR-0043 landed 2026-05-14.)

---

##### Step 6c-iv-b — Contract-scoping retrofit

**✓ COMPLETE (2026-05-14, ADR-0045).** EmployeeRole gains a mandatory `contract_id` (M:1 → Contract); the disjoint-ranges invariant restructures per-`(employee, role_type, contract)`; the rate-resolution lookup keys on `(employee, role_type, contract, date)`, with `contract` resolved via the **contract-resolution path** `→ project → WABundle → contract`; `change_employee_role_rate` (ADR-0039) gains a `contract` parameter; the ADR-0039/0041 out-of-role-range blocker predicate generalizes (no new registry entry — registry stays at 12). WA Code default flat fee is a read-time derivation against `Contract.code_flat_fee_schedule` (a code type absent from the schedule → null/unpriced, no blocker); WA Code stays project-scoped. Blast radius confirmed bounded — the contract dimension is a money-resolution axis only. Amends ADR-0035 / 0039 / 0041 / 0020; **ADR-0027 dropped** from the planned amendment set — no WA Code state-machine touchpoint exists. **Step 6c-iv complete** (6c-iv-a + 6c-iv-b both landed).

**Goal:** Apply 6c-iv-a's attachment model to EmployeeRole and WA Code. The application half of Step 6c-iv — covers items 3 + 4 + 5 of the shared brief.

**In scope:**
- **Item 3 — EmployeeRole contract-scoping.** `contract_id`; disjoint-ranges invariant per-`(employee, role_type)` → per-`(employee, role_type, contract)`; rate-resolution lookup gains the contract dimension (resolved Time Entry → project → contract); `change_employee_role_rate` (ADR-0039) dispatch keys on `(employee, role_type, contract)`.
- **Item 4 — WA Code default flat fee against contract.** Looked up by code type + contract; defines the contract side that Step 6c-iii's `WACodeConf` work inherits.
- **Item 5 — Blast-radius bound.** Confirm the code → required-docs / Deliverables / Sample-Batches derivation logic is unaffected — do not re-litigate.

**Inputs:** 6c-iv-a's Contract-introduction ADR (ADR-0043); **Step 6c-iii-a's WABundle + contract-re-attachment ADR** — the contract now attaches to the WABundle, so 6c-iv-b's `→ contract` resolution path runs through it; ADR-0035 (EmployeeRole temporal shape), ADR-0039 (`change_employee_role_rate`), ADR-0020 (WA Code project-scoping), ADR-0027 (WA Code state machine), ADR-0041 (relationships), `handoff.md` cumulative tables, `decisions.md`.

**Output:** The retrofit ADR — amendments to ADR-0035, ADR-0039, ADR-0041, ADR-0020, ADR-0027. Updated cumulative tables in `handoff.md` as needed.

**Done when:** EmployeeRole's contract-scoped uniqueness invariant + rate-resolution lookup + `change_employee_role_rate` impact are settled; WA Code default-flat-fee-against-contract is settled; blast-radius bound confirmed; the retrofit ADR is written; cumulative tables refreshed.

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
