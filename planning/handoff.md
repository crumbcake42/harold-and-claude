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
>
> **Gate applies to source code too.** Phase 2's surface includes implementation files; the "writes vs. opinions" framing covers source files. Non-trivial structural code decisions and ADR proposals earn a chat-side canvass before the write.

---

## How to start a session

If the user says something like _"resume work"_ / _"start the next session"_ / _"run the next session"_ / _"do the next session block"_ / _"vamos"_ / _"yallah"_: follow `planning/_workflow.md`. That file owns the case-detection logic and the completion protocol.

---

## Current phase

**Implementation** — Phase 2. **Step 1 / M0 Foundations ✓ COMPLETE 2026-05-19 (Session 33).** **Step 2 / M1 Roster** partitioned 2026-05-19 (Session 34, Case 2) into 4 sub-steps. **Step 2.1 / M1.1 Auth substrate + frontend shell ✓ COMPLETE 2026-05-19 (Session 35).** **Step 2.1b / Frontend architecture & conventions** (inserted; not a roadmap milestone) ✓ **COMPLETE 2026-05-20** — 2.1b-A (Session 36; ADR-0064 / 0065) + 2.1b-B (Session 37; ADR-0066). **Step 2.2 / M1.2 Admin substrate + flat roster** partitioned 2026-05-20 (Session 38, Case 2) into 3 sub-steps — 2.2a (backend substrate + Contract exemplar) / 2.2b (backend remainder) / 2.2c (frontend admin pages); dev seed tooling scoped in. **Step 2.2a ✓ COMPLETE 2026-05-20 (Session 39)** — branch `m1/02-flat-roster`, 7 commits; **ADRs deferred to Session 40** (user's call — a planning review of Session 39's commits precedes the ADR write). **Next: Session 40** — review Session 39 → write M1.2 ADRs from **ADR-0067** → **Step 2.2b**. M1.3 / M1.4 stubs in `steps.md`.

## Last session summary

**Session 39 — Step 2.2a / M1.2 backend substrate + Contract exemplar (2026-05-20).** Case 3 scoped session. The three M1.2 backend abstractions are built and proven end-to-end against Contract; 71 backend tests + ruff + pyright green; frontend lint/typecheck/build green; migration applied to Neon. **ADRs not written this session** — deferred to a Session 40 review of the commits (user's call).

**Commits — branch `m1/02-flat-roster` (7), off `m1/roster`:**

- `3ee04ed` — fix: `pool_pre_ping` on the SQLAlchemy engine (Neon kills idle-suspended backends; pre-ping recycles stale pooled connections).
- `f004118` — admin auth-predicate factory (`require_role`) + CRUD authoring helpers (`app/framework/crud.py`) + `EntityNotFound`.
- `e21e964` — Contract entity + Alembic migration `6dd5906ef088` (applied to Neon).
- `ba71739` — `create/edit/delete_contract` + production dispatcher wiring (`app/framework/runtime.py`) + command bootstrap.
- `b6edbec` — Contract CRUD + read routes + dispatcher-exception→HTTP handlers.
- `c452d57` — `seed_db` CLI + seed framework + `just` recipes.
- `e553466` — regenerated OpenAPI contract + frontend client.

**Three approved abstractions delivered** (gated + approved at session head; ADRs from **ADR-0067** land at Session 40): (1) admin auth-predicate factory — `require_role(minimum)`; (2) admin-CRUD authoring — hand-authored Command classes over shared `crud.py` helpers (the **hybrid** shape, not a generalized class factory); (3) seed-tooling — `seed_db` dispatches CSV rows through the Command pipeline, skip-existing idempotency, JSONB sidecar CSV (`contract_code_fees.csv`), seeds at `app/cli/seeds/`.

**Five in-flight implementation decisions surfaced — queued for the Session 40 review** (see § Open questions "For Session 40"):

1. **Uniqueness as a handler pre-check, not an `Invariant`.** The dispatcher flushes before its invariant step, so a DB-UNIQUE-backed rule must be checked pre-flush in the handler (clean `InvariantViolation`); the DB UNIQUE constraint stays the hard backstop.
2. **No `created_*/updated_*` columns** on Contract — follows the M1.1 `User` precedent; `command_audit_log` covers who/when. (See the new Queued item — `data-model.md` divergence to review.)
3. **PascalCase command class names** — `command_audit_log.command_name` stores `"CreateContract"` (not the planning-doc `create_contract`); follows the M0.3 smoke-command precedent.
4. **`EntityNotFound(CommandRejected)`** added to the framework exception family → HTTP 404.
5. **ADR-0047 Cluster 1 class rule extends to Contract** (Contract was hoisted into M1.2 after ADR-0047 named `{Employee, School, Contractor, User}`).

**Live Neon data round-trip not run.** The migration is applied to Neon (schema-side adapter verified — `code_flat_fee_schedule` JSONB created on real Postgres). A real Contract write through the pipeline against Neon was not auto-run (avoids junk rows); the `json_column()→JSONB` data path is covered by SQLite tests, real-JSONB dogfood deferred to the running app / 2.2c.

**Untracked file.** `backend/app/cli/redact_csv.py` still untracked — 2.2b brings it into `app.cli` module shape and commits it.

`_file-rules.md` **not regenerated** — no `## File contract` block changed.

**Memory updated (1).** `feedback-review-inflight-decisions` — when a scoped session surfaces implementation decisions beyond the gated set, queue a next-session review before writing ADRs (don't auto-ADR them at wrap-up).

---

## Open questions

**Queued — frontend follow-ups (post-2.1b; not yet scheduled).** Raised by the user at Session 37 wrap-up; still queued — **not** part of M1.2's three sub-steps (2.2a/2.2b/2.2c).

- **Item 1 — theme toggle (small, its own step).** A light / dark / auto toggle in the admin shell header; button at `src/components/ThemeToggleBtn`. Substrate already exists — `src/index.css` has `:root` + `.dark` token blocks and `next-themes` is installed. Work: mount `<ThemeProvider>` from `next-themes` (not currently mounted — the Sonner `Toaster` just degrades to "system"), build `ThemeToggleBtn`, wire it into `pages/admin-shell`. `next-themes`' `enableSystem` gives "auto" free. ~30 min. A small dedicated standalone step — slot it between M1.2 sub-steps or after M1.2; out of scope for 2.2c.
- **Item 2 — themeable architecture (POST-MVP).** A theme registry + user-facing theme dropdown; each theme defines light + dark; a user picks either one theme (both modes) or distinct light/dark themes. Design the schema for the general case: a theme = one named token-value set for a single mode; a user preference = `(lightThemeId, darkThemeId, mode)`. Per-user persistence to a `User` preference is a **backend change** → firmly post-MVP, ADR-worthy when it lands (superseding ADR per `steps.md`'s contract). Not MVP — default theme suffices; not in `mvp.md`'s 6 must-haves. **Prep already done:** `PATTERNS.md` § UI components now mandates styling via semantic theme tokens only, which keeps this a drop-in; nothing else to build now.

**Queued — backend review (not yet scheduled).**

- **Audit-metadata columns vs. `data-model.md`.** `data-model.md` § Conventions defines a conceptual "standard audit-metadata" set (`created_at / created_by / updated_at / updated_by`, "the dispatcher writes uniformly"). The implementation never materialized these as columns — M1.1's `User` and M1.2's `Contract` (both audit-log-pattern entities) carry none; `command_audit_log` records who/when per command. Review whether to materialize the columns, amend `data-model.md` to drop the convention, or leave the divergence documented. **Not a priority** — raised by the user at Session 39 when M1.2's first entity landed.

**For Session 40 — review Session 39, then Step 2.2b.**

- **Session 40 opens with a planning discussion**, not implementation. Ratify-or-amend Session 39's five in-flight decisions (listed in the Session 39 summary above), then write the M1.2 ADRs from **ADR-0067**, then proceed to Step 2.2b. STOP-AND-CONFIRM applies to any amendment.
- **Three approved abstractions awaiting ADRs:** admin-CRUD authoring shape (hand-authored Command classes + `crud.py` helpers); admin auth-predicate factory (`require_role`); seed-tooling shape (`seed_db` through the pipeline, skip-existing, JSONB sidecar). Approved at the Session 39 gate; ADRs deferred per the user.
- **Step 2.2b Case 2 re-check.** 2.2a's authoring shape landed as hand-authored-over-helpers (not a generalized factory) — `steps.md` § Step 2.2b says to run the 7-signal checklist at session head when that is the case (4 entities × 3 commands is the heavier path). Run it; split if it fires.
- **Carry-forwards into 2.2b:** `User.employee_id` FK + UNIQUE in 2.2b's Employee migration (ADR-0061 — M1.1 left it a plain UUID); `redact_csv.py` → `app.cli` module shape + committed; `seed_db` coverage for all four entities; extract a shared `require_unique` helper from Contract's `_require_unique_number` (User's `username` is the second consumer).

**For Phase 2 broadly (M1+ outlook):**

- **Step 1 / M0 ✓ COMPLETE 2026-05-19** (Session 33). Substrate for every M1+ command in place: Command base + dispatcher with retry loop, history infrastructure with real capture sink, advisory-lock + SERIALIZABLE primitives behind a documented adapter, Alembic + CI green on SQLite.
- **Step 2.1 / M1.1 ✓ COMPLETE 2026-05-19** (Session 35). Auth substrate established for M1.2+ admin work. Per-role pytest fixtures available; concrete Caller flows through dispatcher.
- **Step 2.1b ✓ COMPLETE 2026-05-20** (Sessions 36–37). Frontend four-layer architecture + UI/form stack (shadcn `radix-lyra`, Tailwind 4, Zod, RHF) + API-client relocation + M1.1 auth port; `frontend/src/PATTERNS.md` is the conventions doc M1.2 frontend work (2.2c) consumes.
- **Step 2.2a ✓ COMPLETE 2026-05-20** (Session 39). M1.2's three backend abstractions (admin auth-predicate factory, admin-CRUD authoring helpers, `seed_db` framework) + Contract end-to-end (entity / commands / routes); production dispatcher wired; first M1+ `command_audit_log` writer. ADRs deferred to a Session 40 review.
- **PaaS vendor pick stays deferred per ADR-0055.** Do not re-propose vendor canvass at any M1+ step head. See [[project-vendor-pick-deferred]] for the 5 portability discipline notes.
- **Postgres CI service stays deferred** (Session 33 decision). Revisit if Docker access becomes reliable on the dev machine.
- **Neon dev DB stays current with alembic head per [[project-neon-current-policy]].** Apply migrations to Neon immediately at landing; throwaway sqlite OK for pre-commit iteration only.
- **MVP-attempt-1 rewind protocol** (per [[project-branching-convention]]): with `m0-complete` tag landed, rewind cost to restart M1 from M0 is one tag move. `m1-complete` lands at M1 close (after sub-steps 1.2, 1.3, 1.4).

**Carried into Phase 2 broadly:**

- **Auth substrate (M1.1).** Concrete Caller + per-role pytest fixtures + `current_user` dep + login/logout/me routes are now the M1.2+ baseline. M1.2 commands consume `Caller` for ADR-0047 predicates; tests use `as_admin` etc. from `conftest.py`.
- **Adapter boundary (M0.4).** Postgres-specific features live behind `app.framework.adapter`. M1+ entity tables consume `json_column()`; advisory-lock invariants land key-builders in `app.framework.locks` and call the adapter.
- **PaaS / vendor portability discipline** (ADR-0055 + [[project-vendor-pick-deferred]]). Postgres 15+ floor; no vendor-specific extensions; vanilla `psycopg`; CI on docker-compose Postgres when adopted.
- **Carry-forward landings.** Per `roadmap.md` § Carry-forward landing index. M1's carry-forward: ContractorEngagement signatures + date defaults (lands in M1.4).

**Process notes (apply to Phase 2 generally):**

- **STOP-AND-CONFIRM gate stays in force, including for source code.** Each sub-step opens with chat-side deliberation before any code or ADR write.
- **Commit pattern: preserve incremental checkpoints; FF sub-step branches to `m1/roster`; merge `m1/roster` → `dev` with `--no-ff` + tag `m1-complete` at M1 close** (per [[preserve-incremental-commits]] + [[project-branching-convention]]). **Per-entity granularity:** within a multi-entity sub-step, commit after each entity's additions land green — not only at sub-step close.
- **Seed coverage is a standing requirement** (Session 38): every entity-adding sub-step from M1.2 onward maintains `seed_db` coverage for the entities it introduces. `seed_db` dispatches CSV rows through the Command pipeline.
- **Contract-drift CI job enforces schema + client are in sync.** Any backend OpenAPI-surface change requires `just gen-openapi` + commit of `contracts/openapi.json` + `frontend/src/api/` (see [[committed-generated-artifacts]]).
- **Cross-check architecture.md out-of-band concerns at every Case 2 sizing** per [[check-out-of-band-concerns]] — applied at M1 (caught auth slip); apply at M2+. For M1.2 Case 2 sizing: the relevant out-of-band concerns are file storage (not surfaced until M5), background jobs (not surfaced until M3 RFA auto-draft regeneration), notifications (post-MVP). None of those apply to M1.2.
- **`mvp.md` is the canonical MVP scope reference.**
- **Migration discipline per [[project-neon-current-policy]].** Author migration → `uv run alembic upgrade head` against Neon → commit. Throwaway sqlite for shape iteration before commit.

## Next session

**Session 40 — review Session 39 → write M1.2 ADRs → Step 2.2b.** Session 40 opens with a planning discussion of Session 39's 7 commits + the five in-flight implementation decisions (see the Session 39 summary + the "For Session 40" Open-questions block). On ratification it writes the M1.2 ADRs from **ADR-0067**, then proceeds to **Step 2.2b / M1.2 backend remainder** (Employee / School / Contractor / User-admin-CRUD).

### Prompt for the next session

> Resume work. **Session 39 completed Step 2.2a** (M1.2 backend substrate + Contract exemplar) on branch `m1/02-flat-roster` — 7 commits, no ADRs yet.
>
> **Session 40 opens with a planning discussion, not implementation.** Review Session 39's 7 commits and the five in-flight implementation decisions (Session 39 summary + the "For Session 40" Open-questions block):
> 1. uniqueness as a handler pre-check, not an `Invariant` (the dispatcher flushes before its invariant step);
> 2. no `created_*/updated_*` columns on audit-log entities (follows the M1.1 `User` precedent; `command_audit_log` covers who/when);
> 3. PascalCase command class names as the registered / audit-logged `command_name`;
> 4. `EntityNotFound(CommandRejected)` framework addition → HTTP 404;
> 5. ADR-0047 Cluster 1 class rule extending to Contract.
>
> Ratify or amend each (STOP-AND-CONFIRM applies to amendments). **Then write the M1.2 ADRs from ADR-0067** — the three approved abstractions (admin-CRUD authoring shape; admin auth-predicate factory; seed-tooling shape) plus whatever the review settles.
>
> **Then Step 2.2b / M1.2 backend remainder** (Employee / School / Contractor / User-admin-CRUD). Run the `steps.md` § Step 2.2b Case 2 re-check first: 2.2a landed the admin-CRUD authoring shape as **hand-authored Command classes + shared helpers** (not a generalized factory), so 4 entities × 3 commands is the heavier path — run the 7-signal checklist before implementing; split if it fires. The full 2.2b brief is `steps.md` § Step 2.2b.
>
> **Carry-forwards into 2.2b:** `User.employee_id` FK + UNIQUE constraint lands in 2.2b's Employee migration (ADR-0061 — M1.1 left it a plain UUID); `redact_csv.py` is brought into `app.cli` module shape (`python -m app.cli.redact_csv`) and committed; `seed_db` coverage extends to all four entities (standing requirement); extract a shared `require_unique` helper from Contract's `_require_unique_number` once User's `username` is the second consumer.
>
> **Read first:** the Session 39 summary above + the "For Session 40" Open-questions block; the Session 39 commits (`git log m1/roster..HEAD --stat`); `steps.md` § Step 2.2b; ADR-0047 Cluster 1; `data-model.md` § Employee / School / Contractor / User; ADR-0061 § `user.employee_id` carry-forward.
>
> **Process notes:** STOP-AND-CONFIRM gate applies, including source code. Migration discipline per [[project-neon-current-policy]] (author → `uv run alembic upgrade head` on Neon → commit). Preserve incremental commits — per-entity checkpoint granularity for 2.2b's four entities. Branch `m1/02-flat-roster` shared across 2.2a/2.2b/2.2c, FF-merge to `m1/roster` at M1.2 close. Next ADR free: **ADR-0067**.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-18)
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 ✓ COMPLETE 2026-05-19 (Session 33)**; **Step 2 partitioned into 4 sub-steps 2026-05-19 (Session 34)**; **Step 2.1 ✓ COMPLETE 2026-05-19 (Session 35)**; **Step 2.1b ✓ COMPLETE 2026-05-20 (Sessions 36–37)**; **Step 2.2 partitioned into 2.2a/2.2b/2.2c 2026-05-20 (Session 38)**; **Step 2.2a ✓ COMPLETE 2026-05-20 (Session 39)**; M1.3 / M1.4 stubs; Steps 3–9 stubs)
- Archived step list (Phase 1): `planning/steps.archive/conceptualization.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0066; next ADR at write time: **ADR-0067**)
- **Roadmap (Step 9b output):** `planning/roadmap.md` — 9 milestones (M0 → M8). Canonical milestone-shape source for Phase 2.
- **MVP scope (Step 7 output):** `planning/mvp.md` — 6 must-have features + categorized "not now" list + 1 carve-out + 7 command-shape carry-forwards.
- **Domain model (Step 6d output):** `planning/domain-model.md` — 21 entities, relationship table, per-entity lifecycles, authorization predicates (via ADR-0047), history patterns, delete policy, 14 design patterns, blocker registry, vocabulary.
- **Data model (Step 9a output):** `planning/data-model.md` — conceptual data model: 21 entity sections + conventions block + history-table shapes per ADR-0052.
- **Architecture (Step 8b output):** `planning/architecture.md` — one-page sketch: component diagram, boundary semantics, 10-step data flow, **out-of-band concerns** (file storage / background jobs / notifications / auth) — cross-check at every Case 2 sizing per [[check-out-of-band-concerns]].
- **Consolidated blocker model (Session 25 / ADR-0053):** `planning/decisions.md` § ADR-0053.
- **Phase-transition (Session 25 / ADR-0054):** `planning/decisions.md` § ADR-0054.
- **Branching convention (memory):** [[project-branching-convention]] — `main` → `dev` → `m<N>/<slug>` → `m<N>/<sub-slug>`; tags on `dev` as rewind anchors (`m0-complete` applied 2026-05-19; `m<X>-complete` per milestone; `mvp-shipped` at MVP cutover).
- Framework (Step 1 output): `planning/framework.md`
- Logic (Steps 2–4 output): `planning/logic.md`
- History patterns (Step 5 output): `planning/history-patterns.md`
- Post-MVP feature candidates: `planning/post-mvp.md` (superseded by `mvp.md` § Not now; retained for trace continuity)
- File-location convention: planning artifacts live in `planning/`. `docs/` is reserved for user-facing documentation. `.claude/` is for harness configuration only.
