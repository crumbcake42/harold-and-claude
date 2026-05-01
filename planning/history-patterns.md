# History Patterns

## File contract

**Holds:** The menu of per-entity history patterns and the selection criteria for choosing between them. Established in Step 5 before domain mapping. Every entity defined in Step 6 must choose from this menu.
**Update when:** A pattern is added, removed, or revised (requires a superseding ADR in `decisions.md` before editing). Selection criteria may be refined during domain mapping if edge cases surface, but the pattern set itself is stable.

The available history patterns for entities in `sca-tracker`. Each entity defined at domain-mapping time (Step 6) must select exactly one pattern from this menu. The choice is made at entity-definition time and is required — no entity may be defined without it (per ADR-0006).

Read order if you're cold: `framework.md` (four-kind state taxonomy, per-entity history decision) → `logic.md` (commands, mandatory capture, pipeline) → this file → `domain-model.md` (Step 6, where the choices are made).

---

## Pattern menu

Four patterns, ordered from lightest to heaviest commitment. The first two are **not history-carrying** in the ADR-0008 sense; the last two are.

---

### 1. No history

**What it captures:** Nothing. The current entity record is the sole record of the entity's state.

**Structural commitments:** None beyond the entity record itself. Commands mutate the entity record; no other artifact is produced.

**What it gives up:** All historical visibility. Once a field changes, its prior value is gone. No attribution of changes to callers. No point-in-time queries. If accountability questions arise later, the data to answer them does not exist and cannot be reconstructed.

**Prototype example:** A lookup-table entity (a category classification, a unit-of-measure definition) that changes rarely, whose changes are not disputed, and whose past values are never queried.

---

### 2. Audit log

**What it captures:** Command metadata — command name, caller identity, timestamp. Optionally: a summary of what was requested (command payload or description). No entity state is captured — neither before nor after values.

**Structural commitments:** Minimal. Logging is **not** framework-enforced; it is opt-in and best-effort. The audit log is a system-level facility, not a per-entity structured history chain. Log entries may be written asynchronously, may be lost under failure conditions, and are not atomic with the state mutation. The entity is **not** history-carrying per ADR-0008 — the command pipeline does not enforce capture.

**What it gives up:** State reconstruction. You can see that a command was executed, by whom, and when, but you cannot determine what the entity's state was before or after the command. Change attribution is partial — you know who acted but not exactly what changed. Gaps in the log are possible and undetectable.

**When to choose over "no history":** When basic operational observability ("who touched this?") is desired but the entity's accountability requirements do not justify mandatory capture. The documented tradeoff: this pattern provides convenience-level visibility, not evidentiary-grade history.

**Prototype example:** An entity representing a system configuration or a notification preference — changes should be roughly attributable for operational debugging, but disputes about past state are unlikely and full reconstruction is unnecessary.

---

### 3. Comprehensive capture

**What it captures:** Every successful command on the entity produces a structured history record, atomically with the state mutation (per ADR-0008). Each record contains:

- Command identity (the named operation)
- Caller identity
- Timestamp
- Sufficient state context to reconstruct the entity's complete state at that point in time

The exact representation of "sufficient state context" — full before/after snapshots, change deltas, or another form — is an implementation concern deferred to Step 8. The pattern commits to the **promise**: any past state is reconstructable from the history chain.

**Structural commitments:**

- The entity is **history-carrying** per ADR-0008. Capture is mandatory and framework-enforced — no command handler can skip it.
- The state mutation and the history record are atomic. A command cannot succeed without producing the history record. A history record cannot exist without a successful command.
- The history chain is sufficient for point-in-time state queries: "what was the entity's complete state at time T?" is answerable for any T in the entity's lifetime.
- Every command — lifecycle-affecting or not — produces a record. Routine attribute edits are captured with the same fidelity as lifecycle transitions.

**What it gives up:** Write-path overhead on every command (the history record is always produced). Storage growth proportional to command volume. Every schema change to the entity's state potentially affects the history-record format (since the record must capture full state). The overhead is justified only when the entity's accountability requirements demand it.

**Prototype example:** A high-stakes deliverable entity whose status is subject to dispute — "who approved this, and what did the deliverable look like when they approved it?" must be answerable precisely. Compliance, audit, or dispute-resolution requirements make full state reconstruction a first-class query.

---

### 4. Lifecycle capture

**What it captures:** Only lifecycle-affecting commands produce structured history records. Each record contains:

- Command identity (the lifecycle transition effected)
- Caller identity
- Timestamp
- The lifecycle transition (from-state and to-state)
- Sufficient state context to interpret the transition — enough to answer "what was the entity's state at the moment of this transition?" but not necessarily a full state snapshot at every intermediate point

Non-lifecycle commands (routine attribute edits that do not change lifecycle status) succeed normally but do **not** produce history records.

**Structural commitments:**

- The entity is **history-carrying**, but with a narrowed capture scope. Within that scope (lifecycle-affecting commands), capture is mandatory and framework-enforced — the pipeline treats these commands identically to comprehensive-capture commands.
- Outside that scope (non-lifecycle commands), the command succeeds without producing a history record. The pipeline distinguishes lifecycle-affecting from non-lifecycle-affecting commands using the same declaration that ADR-0009 already requires (commands declare whether they effect a lifecycle transition).
- The history chain records the entity's lifecycle journey: every status change is captured with attribution and sufficient context. The entity's intrinsic-attribute history between lifecycle transitions is not captured.

**Relationship to ADR-0008:** ADR-0008 states that "a successful command both mutates the entity record and writes a history record." Lifecycle capture refines this: the capture scope is declared at entity-definition time as part of the pattern choice, not opted-in per command handler. Within the declared scope, capture is mandatory and atomic. This is a refinement of ADR-0008's scope, not a violation of its mechanism — the pipeline still enforces capture for all commands within the pattern's declared scope.

**What it gives up:** Intrinsic-attribute change history between lifecycle transitions. If a field is edited three times between two lifecycle transitions, only the field's value at the moment of each transition is captured (via the state context in the transition record). Individual attribute edits are not attributable. Point-in-time state queries are answerable only at lifecycle-transition boundaries, not at arbitrary moments.

**Prototype example:** An assignment entity (person-to-project) whose lifecycle transitions matter for accountability (who activated it, who terminated it, when) but whose routine attribute edits (updating a note field, adjusting a role description) are low-stakes and high-frequency. Comprehensive capture would produce a high volume of low-value records; lifecycle capture retains the accountable transitions while skipping the noise.

---

## Selection criteria

### Decision tree

Answer the following questions in order. The first match determines the pattern.

1. **Must the entity's complete state be reconstructable at arbitrary past points in time?** Triggers: compliance requirements, dispute resolution where the exact prior state matters, regulatory point-in-time reporting obligations. → **Comprehensive capture.**

2. **Must lifecycle transitions be formally attributable — who moved it to what status, when, and in what context?** Triggers: accountability for status changes, workflow audit trails, approval chains. → **Lifecycle capture.**

3. **Is basic operational visibility desired — who touched this entity and when — without structural guarantees?** Triggers: debugging, operational monitoring, lightweight "what happened" queries where gaps are acceptable. → **Audit log.**

4. **None of the above.** The entity has no accountability, observability, or reconstruction requirements. → **No history.**

### Secondary factors

When two patterns seem equally applicable, use these factors to break the tie:

- **Change frequency.** High-frequency attribute edits on a comprehensive-capture entity produce storage pressure and write-path overhead. If the lifecycle transitions are the accountable events and the attribute edits are noise, lifecycle capture is the better fit.
- **Dispute likelihood.** If disputes about the entity's past state are plausible (even if not yet experienced), err toward comprehensive capture. The cost of retrofitting history after a dispute arises is much higher than the cost of capturing it proactively.
- **Regulatory or legal requirements.** External mandates override internal convenience. If a regulation requires point-in-time state queries, comprehensive capture is non-negotiable regardless of change frequency.
- **Promotion cost.** Moving from a lighter pattern to a heavier one is always forward-only (see below). If you're uncertain, choosing the heavier pattern now avoids the loss of history that promotion entails.

### Edge cases

- **An entity with no lifecycle but high accountability needs.** Lifecycle capture is inapplicable (there is no state machine to capture transitions of). Choose between comprehensive capture (if past state must be reconstructable) and audit log (if attribution without state reconstruction suffices).
- **An entity with a lifecycle but no accountability needs for any state.** The lifecycle exists for workflow control, but no one needs to audit it. Choose no history. The lifecycle state machine still governs transitions (per ADR-0009); it just doesn't produce history records.

---

## Cross-cutting concerns

### Reference snapshotting

When a history record for entity A references entity B (via a typed UUID per `framework.md`), the history record stores the **reference only** — the typed UUID of B at the time of the change. The history record does **not** snapshot B's state.

If you need to know what B looked like at the time of A's change:
- If B carries comprehensive capture, consult B's own history chain at that timestamp.
- If B carries lifecycle capture, consult B's lifecycle history at that timestamp (you'll get B's state at the nearest lifecycle-transition boundary, not at the exact moment).
- If B has no history or only an audit log, you can only see B's current state. The past state of the reference is not recoverable.

This is a direct consequence of the per-entity history decision (ADR-0006). Each entity owns its own history obligations. The framework does not mandate denormalized copies of referenced entities in history records. The tradeoff is explicit: if you need to interpret past references to an entity, that entity should carry a history pattern heavy enough to support it. This is a factor in the selection criteria — an entity that is frequently referenced by history-carrying entities may warrant a heavier history pattern than its own accountability needs would suggest.

### History-pattern promotion

An entity can be promoted from a lighter pattern to a heavier one (e.g., no history → comprehensive capture, or lifecycle capture → comprehensive capture). This is a **schema-level change**, not a data migration.

Constraints:
- **Forward-only.** History begins from the moment of promotion. Changes that occurred before the promotion were never captured and cannot be reconstructed. The entity's history chain starts at the promotion point, not at the entity's creation.
- **No backfill.** The framework does not pretend that retroactive history is possible. If a "no history" entity is promoted to comprehensive capture, its history chain will have a gap from creation to promotion. The gap is a permanent, acknowledged limitation.
- **Demotion is also possible** but destructive. Moving from comprehensive capture to no history does not delete existing history records (that would be a separate destructive operation), but new commands will stop producing them. The history chain becomes frozen at the demotion point.

Promotion is expected to be rare — the pattern choice at entity-definition time is intended to be durable. The promotion path exists to handle genuine requirement changes, not to substitute for careful initial selection.

### Quarantine

Quarantine — applying a command but isolating the affected entity in a side state outside its normal lifecycle — is **not** a history pattern. It is a violation-handling override: it changes what happens when a command fails a rule, not what a successful command records.

An entity's quarantine behavior is orthogonal to its history pattern. A quarantined entity could carry comprehensive capture, lifecycle capture, audit log, or no history. The history pattern governs what successful commands leave behind; quarantine governs what happens instead of rejection on failure.

Quarantine remains deferred per ADR-0011. If it is commissioned as a per-entity pattern in a later step, it will be a separate declaration — not a menu item here.
