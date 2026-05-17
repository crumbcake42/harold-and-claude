# Handoff

## File contract

**Holds:** Transient state between Claude Code contexts — current phase pointer, last session summary, next session pointer and prompt, open questions, and pointers to all other planning files. Session execution rules live in `planning/sessions.md`; restructure log lives there too.
**Update when:** A session completes or wraps up (advance next-session pointer, summarize last session, refresh open questions, rewrite prompt); a phase changes; the step list in `steps.md` is restructured. Full protocol in `planning/_workflow.md` (Case 3, completion protocol).

The single source of truth between sessions. Read this first.

---

# **STOP-AND-CONFIRM GATE — READ BEFORE WRITING ANYTHING**

> **Every session starts in chat, not in a file. Surface the decisions; wait for explicit approval; then write.**
>
> For each decision on the table, deliver in chat (≤150 words each):
>
> - The fork(s) actually on the table
> - 2–3 candidate positions, each with **what it buys** and **what it gives up**
> - What it depends on or defers to
> - **Your recommendation, labeled as such, with reasoning.** Chime in on which option looks stronger and call out specific options to avoid. Per `CLAUDE.md`'s base rule: if you think an option is bad, say so and explain why. Recommendations do not pre-decide — the user retains the position.
>
> **Do NOT write ADRs. Do NOT modify any planning file (or any other file) in the proposal turn.** Wait for the user's explicit `approved` (or amendments) before touching files. If you're unsure whether something counts as a file modification, ask.
>
> If two decisions are genuinely inseparable, say so and explain why — but default to splitting. Roadmap length is not a constraint; splitting a session into more sessions is preferred over rushing a decision.
>
> **This gate exists because prior sessions (twice on 2026-04-28) stacked or pre-answered decisions by writing the answer into a file before agreement.** "The artifact is the deliberation" (rule 1 in `planning/sessions.md`) means the doc canvasses options before landing — it does **not** mean writing first and asking later. The gate is on **writes** (ADRs, planning files), not on **opinions**. Agreement on the position is gated on the chat-side proposal; the doc then writes it up.

---

## How to start a session

If the user says something like _"resume work"_ / _"start the next session"_ / _"run the next session"_ / _"do the next session block"_ / _"vamos"_ / _"yallah"_: follow `planning/_workflow.md`. That file owns the case-detection logic and the completion protocol.

---

## Current phase

**Implementation** — Phase 2, current as of 2026-05-17 per ADR-0054 (phase-transition; Conceptualization closed). The 9-milestone roadmap from `planning/roadmap.md` (M0 Foundations → M8 Cutover prep) is the canonical milestone-shape source; `planning/steps.md` mirrors the milestones as 9 steps (Step 1 = M0 Foundations with full brief; Steps 2–9 are stubs that expand into full briefs as each step opens per Case 2 sizing). Conceptualization-phase steps archived to `planning/steps.archive/conceptualization.md`. See `planning/phases.md` for the full phase roster and `planning/steps.md` for the current step list.

## Last session summary

**Session 25 — Step 9b: consolidation pass + `roadmap.md` + phase-transition ADR. ✓ COMPLETE (2026-05-17, ADR-0053 + ADR-0054, closes Conceptualization phase).** Case-3 scoped; ran the session-head sizing check first, then proceeded as a single Case-3 session per the partition mitigation's escape hatch.

**Session-head sizing check finding.** Scan of `decisions.md` for ADRs amended 2+ times turned up **18 ADRs** crossing the literal threshold — far past the session-23 preview's "1 firm + 1–2 borderline" estimate. Per the partition mitigation, this triggered re-running the Case 2 fit checklist on 9b. Three positions surfaced:
- **Position A (strict literal):** partition 9b into 9b + 9c + 9d... — 4–6 sessions of consolidation before phase-transition.
- **Position B (narrowed test):** apply a tighter qualifying test ("the original ADR's text misleads a present-day reader about the current model"). Only **ADR-0032** crosses that bar — its `dismissable | fix-only` binary, closure-gate text, Note subtype set, and registry size are all wrong relative to the current model after ADR-0042 / 0046 / 0049 + single-amender additions.
- **Position C (skip entirely):** rolled-up artifacts (`data-model.md` / `domain-model.md` / `mvp.md` / `architecture.md` / `roadmap.md`) already serve as Phase 2's foundation; the ADR log is the deliberation record.

**Position B-narrowed accepted.** Consolidate ADR-0032 alone via ADR-0053; the 17 other 2+-amender ADRs stay standing (their amender chains preserve correctly-readable models). The deviation from the literal "2+ amendments" framing of `steps.md` line 612 is recorded honestly in ADR-0054's Alternatives considered.

**ADR-0053 written (consolidates ADR-0032 — blocker-and-resolution model).** Position 1a (narrow): supersedes ADR-0032 only; ADR-0042 / 0046 / 0049 stay accepted. Position 2a (reread-of-current-model): fresh shape, not ADR-0032's old binary-centered structure. Body covers: Note subtypes (`regular | blocker | resolution | audit_reason | write_off`); polymorphic target (entity OR history record per ADR-0040); lazy materialization; user-flagged blockers; cross-project paired-blocker materialization; resolution semantics (structural_fix / default_resolution / dismissal); closure gate = "no registry blocker holds" over not-written-off entities; canonical 10-entry registry (gap-preserving numbering since #1/#2 retired post-keep-FK); registry schema `(target, command_shape, optional compound_names, optional chain)`; chain shape `te_batches_by_coverage`; default-resolution command family (`default_resolve` generic + `resolve_overlap` / `resolve_overlap_paired` / `resolve_open_rfa` named compounds + `revoke_write_off`); nuclear-option guard; design pattern references (#11, #12, #14). ADR-0032 status flipped to `superseded by ADR-0053` (body preserved for deliberation context per "phase boundary doesn't make deliberation context worth less" framing).

**`planning/roadmap.md` written.** Fork 1b (medium granularity, 9 milestones) + Fork 2a (S/M/L sizing only, no week estimates). Milestone table: M0 Foundations (L), M1 Roster (M), M2 Contract+Project+WABundle (M), M3 WA+WA Code+RFA cycle (L), M4 Time Entry+Sample Batch (M), M5 Documents+Deliverables+DepFilings (L), M6 Closure gate+blockers+write-off (L), M7 Reads+reporting (M), M8 Cutover prep (S–M). Strictly sequential at the backend slice; frontend parallelizes within milestones. Per-milestone expansion paragraphs + ordering rationale + carry-forward landing index (all 7 command-shape carry-forwards + 5 implementation-phase carry-forwards from ADR-0051/0052 + the `resolve_overlap_paired` conditional carve-out land in specific milestones) + pointers.

**ADR-0054 written (phase-transition).** "Conceptualization phase complete; Implementation phase begins." Records the consolidation-pass deviation (Position B-narrowed) honestly in Alternatives considered; pre-enumerates Phase 3 as a stub per `phases.md`'s just-in-time enumeration principle. Triggers the four `phases.md` writes (lightweight gate).

**Four `phases.md` writes executed** (lightweight gate per `_workflow.md`): (a) Phase 1 status `current → complete` with archive pointer; (b) Phase 2 status `not started → current` with concrete Goal (build the MVP per `mvp.md` + `roadmap.md`) + Steps pointer; (c) `planning/steps.md` archived to `planning/steps.archive/conceptualization.md` (new directory created); (d) new `planning/steps.md` written for Implementation phase (9 steps mirroring M0–M8; Step 1 full brief, Steps 2–9 stubs with roadmap pointers); Phase 3 stub appended.

**Files touched:** `planning/decisions.md` (ADR-0053 + ADR-0054 appended; ADR-0032 status flipped). `planning/roadmap.md` (new). `planning/phases.md` (Phase 1/2 flipped; Phase 3 stub added). `planning/steps.md` (replaced — old archived). `planning/steps.archive/conceptualization.md` (new — archive of the conceptualization-phase steps). `planning/_file-rules.md` (regenerated — roadmap.md entry added; steps.md File contract refreshed for Implementation phase; phases.md unchanged; last-regen date 2026-05-17). `planning/handoff.md` (this file — phase pointer, last session summary, next session pointer + prompt, open questions, pointers).

---

## Open questions

**For the next session (Step 1 / M0 Foundations) — open at session head:**

- **Step 1 fit assessment.** M0 is sized L per `roadmap.md` and will not fit one session. The next session must run the Case 2 fit checklist before any work and propose a partition. Likely partition seams (surface as candidate options):
  - **Per-decision seam:** PaaS pick + Postgres offering as one session (write ADR-0055); per-invariant isolation primitives + audit-log write timing as another (write ADR-0056 or two ADRs); `Command` base class + dispatcher + history infrastructure as a third; repo skeletons + CI + adapter boundary as a fourth.
  - **Substrate-then-decisions seam:** repo skeletons + CI as one session; then the three ADR-laden sessions in any order.
  - **Decisions-first seam:** all three ADRs in one session (PaaS, isolation primitives, audit-log timing) before any code lands.
- **PaaS vendor candidates to canvass.** Neon is the dev default (per ADR-0051); production options include managed PaaS bundles (Render / Fly.io / Railway), AWS (RDS / Lightsail / EB), GCP (Cloud SQL / Cloud Run), Azure equivalents, and stay-on-Neon (Neon is also a production offering, not just dev). Surface the trade-offs at session head; recommend at the gate.
- **Per-invariant isolation primitives — first per-invariant choices.** ADR-0052 pinned the available primitives (`SERIALIZABLE` default + `pg_try_advisory_xact_lock` opt-in); the per-invariant choices for M0's substrate invariants are open. Domain-model.md § Design patterns #3 (closure-readiness derivation cluster) and the EmployeeRole disjoint-ranges invariant (per `(employee, role_type, contract)` per ADR-0045) are likely first candidates for advisory-lock evaluation.
- **Audit-log write timing.** In-txn (atomic with the entity mutation) vs. post-commit (best-effort, async). ADR-0052 explicitly permits post-commit but flags in-txn as "stronger than the pattern promises." Trade-offs: in-txn ties audit-log durability to the command's success (cleaner audit story; but a failing audit-log write rolls back the command, which may be too strict for non-critical commands); post-commit decouples but risks audit-log loss on crash between commit and audit write.

**Carried into Phase 2 broadly:**

- **Adapter boundary scope.** Postgres-specific features (JSONB, advisory locks, `SERIALIZABLE`) live behind the adapter per ADR-0051. M0 establishes the boundary; subsequent milestones add features behind it as they need them. SQLite offline fallback is buildable but **not production-equivalent** (explicit per ADR-0051).
- **Carry-forward landings.** All 7 command-shape carry-forwards land in specific milestones per `roadmap.md` § Carry-forward landing index. When each milestone opens, the carry-forwards landing in it should be raised at session head so the brief covers them.
- **MVP carve-out tracking.** `resolve_overlap_paired` (blocker #8 joint compound) ships in M6 conditionally on `split_entry`'s mechanics. If `split_entry` proves heavier than estimated when M6 opens, `resolve_overlap_paired` slips post-MVP per ADR-0050. Re-evaluate at M6 session head.

**Process notes (apply to Phase 2 generally):**

- **STOP-AND-CONFIRM gate stays in force.** Each step opens with chat-side deliberation before any code or ADR write. Code is files, no exception. The gate's "writes vs. opinions" framing applies to source code as much as to planning docs.
- **`Command` base class + dispatcher is the structural anchor for all of Phase 2.** ADR-0008's atomicity (entity mutation + history write in the same transaction) is framework-enforced via the dispatcher; no handler-level skip. Verify this invariant at every M1+ command-add.
- **Engine-portability discipline (ADR-0051 + ADR-0052).** Postgres-specific features stay behind the adapter; SQLite offline fallback uses degraded equivalents. Explicit not production-equivalent.
- **`mvp.md` is the canonical MVP scope reference.** Adding a feature beyond the 6 must-haves requires a superseding ADR. `mvp.md` § Carve-outs tracks the slip-eligible items; § Command-shape carry-forwards tracks the in-MVP-but-shape-deferred items.

## Next session

**Step 1 — M0 Foundations.** First step of the Implementation phase. Sized L per `roadmap.md`. Will not fit one session — the next session opens with a Case 2 fit checklist run + partition proposal. Brief in `steps.md` → § Step 1. Execution order: Step 1 → Step 2 → ... → Step 9 (sequential per `roadmap.md` § Ordering rationale).

### Prompt for the next session

> Resume work. Next is **Step 1 — M0 Foundations** (Phase 2 / Implementation, first step). Brief in `steps.md` → § Step 1. This is the first step of a new phase; foundations work needed before any domain command can land.
>
> **Read first:** this prompt + the Open questions block above + `planning/_workflow.md` (Case 2 protocol — Step 1 is L and will need partitioning) + `planning/roadmap.md` § M0 (canonical milestone shape) + `planning/steps.md` § Step 1 (per-step brief) + `planning/architecture.md` (component diagram + out-of-band concerns) + `planning/data-model.md` (history-table topology) + `planning/decisions.md` (esp. ADR-0001 stale-scaffolding, ADR-0051 runtime stack, ADR-0052 data layer, ADR-0053 blocker-and-resolution model, ADR-0054 phase-transition).
>
> **Session-head Case 2 sizing check (before drafting anything):**
> 1. Run the `_workflow.md` Case 2 fit checklist on Step 1 / M0. M0 is sized L per `roadmap.md`; this is essentially guaranteed to trip at least signals 1 (>1 deliberable decisions), 2 (>1 new artifact), 3 (>60 min). Partition is required, not optional.
> 2. Propose 2–3 partition options with trade-offs (candidate seams in the Open questions block above). Default recommendation: surface the **substrate-then-decisions seam** as the cleanest cut — repo skeletons + CI first (no deliberation; mechanical scaffold work), then ADR sessions for PaaS pick, isolation primitives + audit-log timing, dispatcher + history infrastructure in sequence.
> 3. On consensus, write the revised step entries to `steps.md`; update `handoff.md`'s next-session pointer to the first sub-step.
> 4. Fall through to Case 3 for the first sub-step.
>
> **In scope (per `steps.md` § Step 1, partition-pending):**
> 1. Stale-scaffolding cleanup of `backend/` + `frontend/` (ADR-0001 + ADR-0051).
> 2. PaaS vendor pick + managed-Postgres offering (ADR — likely ADR-0055).
> 3. Backend repo skeleton (FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic + Ruff + Pytest).
> 4. Frontend repo skeleton (Vite + React + TanStack Router + TanStack Query + openapi-ts + Storybook + ESLint + Prettier).
> 5. CI pipeline (Postgres integration tests).
> 6. `Command` base class + dispatcher with logic.md pipeline (auth → lifecycle → apply → invariants → history → commit).
> 7. History infrastructure (per-entity tables substrate + `command_audit_log` + dispatcher-enforced capture).
> 8. Per-invariant isolation-primitive assignment (ADR — likely ADR-0056 or bundled with #9).
> 9. Audit-log write timing (in-txn vs post-commit; ADR or bundled with #8).
> 10. Adapter boundary code for Postgres-specific features.
>
> **Out of scope (Phase 2 later milestones):** Domain-entity DDL (M1+); file storage backend (M5); per-invariant primitive choices for invariants that haven't been implemented yet (later milestones as their invariants land).
>
> **Process notes:**
> - **STOP-AND-CONFIRM gate applies to code, not just docs.** Phase 2's surface includes implementation files — the gate's "writes vs. opinions" framing covers source files. Each ADR proposal and each non-trivial structural code decision earns a chat-side canvass before the write.
> - **ADR numbering.** Next ADR at write time: **ADR-0055**.
> - **`mvp.md` is the canonical MVP scope reference.** Adding a feature beyond the 6 must-haves requires a superseding ADR.
> - **Engine-portability discipline.** Postgres-specific features stay behind the adapter; SQLite offline fallback uses degraded equivalents — explicitly not production-equivalent.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-17)
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; Step 1 full brief, Steps 2–9 stubs)
- Archived step list (Phase 1): `planning/steps.archive/conceptualization.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0054; next ADR at write time: **ADR-0055**)
- **Roadmap (Step 9b output):** `planning/roadmap.md` — 9 milestones (M0 → M8) with rough sizing (S/M/L), ordering rationale, carry-forward landing index. Canonical milestone-shape source for Phase 2.
- **MVP scope (Step 7 output):** `planning/mvp.md` — 6 must-have features + categorized "not now" list + 1 carve-out + 7 command-shape carry-forwards + pointers. Canonical MVP-scope reference.
- **Domain model (Step 6d output):** `planning/domain-model.md` — rolled-up domain projection: 21 entities, relationship table, per-entity lifecycles, authorization predicates (via ADR-0047), history patterns, delete policy, 14 design patterns, 10-entry blocker registry, vocabulary, deferred / open questions.
- **Data model (Step 9a output):** `planning/data-model.md` — conceptual data model: 21 entity sections (attribute table per entity with `Attribute | Kind | Type / notes`, outgoing-references line, state-enum line, history-surface label) + conventions block + history-table shapes per ADR-0052 (3 comprehensive + 6 lifecycle + `command_audit_log`). Conceptual only — not DDL.
- **Architecture (Step 8b output):** `planning/architecture.md` — one-page sketch: component diagram (Browser → CDN/SPA → API container → managed Postgres on managed PaaS), boundary semantics per layer, successful-command 10-step data flow, out-of-band concerns (file storage / background jobs / notifications / auth) flagged for implementation phase, pointers.
- **Consolidated blocker model (Session 25 / ADR-0053):** `planning/decisions.md` § ADR-0053 — current blocker-and-resolution model (supersedes ADR-0032).
- **Phase-transition (Session 25 / ADR-0054):** `planning/decisions.md` § ADR-0054 — phase-transition ADR.
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md` (superseded by `mvp.md` § Not now; retained for trace continuity)
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
