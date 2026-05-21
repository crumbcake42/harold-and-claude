# Drift Registry

## File contract

**Holds:** A registry of surfaced drift — code or work that diverges from a written reference (`backend/app/PATTERNS.md`, `frontend/src/PATTERNS.md`, the `CLAUDE.md` files, `planning/roadmap.md`), and structural hazards where two artifacts that should stay congruent can silently diverge. Two tables: a **catalog** of drift *kinds* (`DRIFT-NNN` label → cause → remedy → count → status) and a **log** of *instances* (date, id, location, description).
**Update when:** A drift instance is surfaced (append to the log; bump the kind's count). A drift surfaces that fits no catalogued kind (propose a `DRIFT-NNN` label + cause + remedy; add the catalog row only after the user confirms the label — never log an instance under an unconfirmed label). A kind reaches its recurrence threshold (set its status to `flagged` and surface it for a root-cause review). A flagged kind's root cause is addressed (set status `resolved`).

---

## How this works

- **Drift** here means: code or work diverging from a written reference, or a structural hazard where two artifacts meant to stay congruent can silently fall out of sync.
- **Any** surfaced drift is logged here — whether surfaced by `_workflow.md`'s session-resumption drift checks, by code review, or ad hoc during work. DRIFTS.md does not add a scan; it is the sink for drift that other activity surfaces.
- Each drift **kind** has a `DRIFT-NNN` id, a cause, and a pre-identified remedy (the catalog). Each **instance** is a log row carrying the kind's id.
- **Counting is friction-based.** A log row is the kind's founding occasion plus each later occasion it causes real friction — an actual desync, a near-miss caught in review, or notable maintenance cost. Mechanically re-applying a settled pattern is *not* a logged instance.
- **Recurrence threshold: 5** per kind. Reaching it sets the kind `flagged` and prompts a review with the user to address the root cause — a prompt, never an automatic refactor.
- **New kinds:** propose a `DRIFT-NNN` label, cause, and remedy; add to the catalog only after the user confirms.

---

## Drift kinds (catalog)

| ID | Name | Cause | Pre-identified remedy | Count | Status |
|----|------|-------|-----------------------|------:|--------|
| DRIFT-001 | Parallel-definition drift | Two or more deliberately-separate declarations of one underlying shape, kept in sync by hand — they can silently diverge. | Adopt a shared `*WriteFields` base in the domain module, or generate the transport DTOs from the command `Payload`s (remedies weighed under ADR-0070). | 1 | tracking |
| DRIFT-002 | Layer-charter erosion | A module is placed in an architectural layer (`framework/`, `adapters/`, `auth/`) whose documented `PATTERNS.md` charter it does not fit — usually because it is broadly useful and the layer is the nearest "shared" home. Each misplacement is individually minor; unchecked they blur the layer boundary until the charter stops meaning anything. | Check a new module against the target layer's `PATTERNS.md` charter before placing it; a module that fits no layer cleanly earns an explicit, reviewable placement decision, not a default to the nearest shared folder. | 1 | tracking |

---

## Drift log

| Date | ID | Location | Description |
|------|-----|----------|-------------|
| 2026-05-20 | DRIFT-001 | `features/contracts` — `schemas` ↔ `commands` | Route DTO `ContractWriteRequest` and `CreateContract.Payload` declare the same field set independently. Founding instance — ADR-0070 confirmed DTO/`Payload` separation and accepted the duplication rather than deriving one from the other. |
| 2026-05-21 | DRIFT-002 | `app/framework/pagination.py` | `pagination.py` imports `fastapi.Query` — the sole FastAPI import in `framework/`, an otherwise transport-agnostic command engine; pagination is also a read-side concern in a write-side engine. Founding instance — a near-miss caught in a `/assess` review during Step 2.2d-1a. Post-registry recurrence of the Session-40 failure mode (concrete I/O accreting into `framework/`) that forced Step 2.2b. |
