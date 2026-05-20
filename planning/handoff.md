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

**Implementation** — Phase 2. **Step 1 / M0 Foundations ✓ COMPLETE 2026-05-19 (Session 33).** **Step 2 / M1 Roster** partitioned 2026-05-19 (Session 34, Case 2) into 4 sub-steps. **Step 2.1 / M1.1 Auth substrate + frontend shell ✓ COMPLETE 2026-05-19 (Session 35).** **Step 2.1b / Frontend architecture & conventions** (inserted; not a roadmap milestone) ✓ **COMPLETE 2026-05-20** — 2.1b-A (Session 36; ADR-0064 / 0065) + 2.1b-B (Session 37; ADR-0066). **Step 2.2 / M1.2 Admin substrate + flat roster** partitioned 2026-05-20 (Session 38, Case 2) into 3 sub-steps — 2.2a (backend substrate + Contract exemplar) / 2.2b (backend remainder) / 2.2c (frontend admin pages); dev seed tooling scoped in. **Next: Session 39 / Step 2.2a** — Case 3 scoped session. **Branch op at Session 39 head:** `git checkout -b m1/02-flat-roster` off `m1/roster` (the 2.1b FF-merge is already satisfied — `m1/roster` == `m1/01b-fe-conventions` == `f3bb595`). M1.3 / M1.4 stubs in `steps.md`.

## Last session summary

**Session 38 — Step 2.2 / M1.2 Case 2 sizing + dev seed-tooling scope-in (2026-05-20).** Case 2 session; no implementation, no ADRs — the output is the M1.2 partition + this handoff advance.

**Case 2 sizing.** M1.2 ran the 7-signal fit checklist — 5 hard fires + 1 partial: multiple independently-deliberable decisions; multiple from-scratch artifacts; >60 min; input reading >3 planning files; cross-concern reach; + the seed framework depends on the `create_*` commands (intra-step ordering constraint). Partitioned into 3 sub-steps on a **decision-first** seam: **2.2a** settles the three backend abstractions (admin-CRUD authoring factory, admin auth-predicate factory, seed framework) and proves them against **Contract** — the hardest, most non-uniform entity (JSONB `code_flat_fee_schedule`, derived `validity`; hardest-first de-risks the abstractions); **2.2b** applies the settled pattern to the four remaining backend entities; **2.2c** builds the 5 frontend admin pages. Single shared branch `m1/02-flat-roster`. Full sub-step briefs in `steps.md` § Step 2.2a / 2.2b / 2.2c.

**Partition-shape deliberation.** User initially proposed a 4-way (Contract / Employee-alone / remainder / frontend); agent pushed back — an Employee-only sub-step is under-sized (one trivial entity on a settled pattern) and the Contract-first + Employee-checkpoint pair is redundant de-risking. Resolved at the agent's 3-way recommendation; Employee folds into the 2.2b backend-remainder.

**Dev seed tooling scoped into M1.2.** New requirement raised this session: a `seed_db` CLI loading redacted CSVs into the DB, pairing with the dropped-in `redact_csv.py`. **Decided: `seed_db` dispatches CSV rows through the Command pipeline** (not direct ORM inserts) — keeps seeded data real (invariants, history, audit-log rows) and avoids a second exception to the every-state-change-is-a-Command rule. **Standing requirement: every entity-adding sub-step from M1.2 onward maintains `seed_db` coverage.** Click adoption **deferred** (ADR-0061's "3rd CLI command" trigger restated as "when a unified `app.cli` subcommand group is wanted"); `seed_db` uses `argparse`. `just` recipes: idempotent env-setup (`install` + `alembic upgrade head`) split from interactive/destructive data-init (`bootstrap-admin`, `seed`); optional `first-run` chain.

**No ADRs landed.** M1.2's decisions (admin-CRUD authoring shape, predicate factory, seed-tooling shape) are recorded as locked/open inputs in the `steps.md` § Step 2.2a brief; ADRs are written when 2.2a implements them (from **ADR-0067**), matching the Session 34→35 locked-decisions-then-ADRs precedent.

**Untracked file.** `backend/app/cli/redact_csv.py` — dropped in by the user; a CSV-redaction utility for the seed pipeline. Stays untracked this session; 2.2b brings it into `app.cli` module shape and commits it.

`_file-rules.md` **not regenerated** — no `## File contract` block changed.

**Memory updated (1).** `preserve-incremental-commits` — added per-entity checkpoint-commit granularity (commit after each entity's additions within a multi-entity sub-step, not only at sub-step close).

---

## Open questions

**Queued — frontend follow-ups (post-2.1b; not yet scheduled).** Raised by the user at Session 37 wrap-up; still queued — **not** part of M1.2's three sub-steps (2.2a/2.2b/2.2c).

- **Item 1 — theme toggle (small, its own step).** A light / dark / auto toggle in the admin shell header; button at `src/components/ThemeToggleBtn`. Substrate already exists — `src/index.css` has `:root` + `.dark` token blocks and `next-themes` is installed. Work: mount `<ThemeProvider>` from `next-themes` (not currently mounted — the Sonner `Toaster` just degrades to "system"), build `ThemeToggleBtn`, wire it into `pages/admin-shell`. `next-themes`' `enableSystem` gives "auto" free. ~30 min. A small dedicated standalone step — slot it between M1.2 sub-steps or after M1.2; out of scope for 2.2c.
- **Item 2 — themeable architecture (POST-MVP).** A theme registry + user-facing theme dropdown; each theme defines light + dark; a user picks either one theme (both modes) or distinct light/dark themes. Design the schema for the general case: a theme = one named token-value set for a single mode; a user preference = `(lightThemeId, darkThemeId, mode)`. Per-user persistence to a `User` preference is a **backend change** → firmly post-MVP, ADR-worthy when it lands (superseding ADR per `steps.md`'s contract). Not MVP — default theme suffices; not in `mvp.md`'s 6 must-haves. **Prep already done:** `PATTERNS.md` § UI components now mandates styling via semantic theme tokens only, which keeps this a drop-in; nothing else to build now.

**For Session 39 — Step 2.2a / M1.2 backend substrate + Contract exemplar** (next; Case 3 scoped session).

- **The full 2.2a brief is `steps.md` § Step 2.2a** — Goal, the three decisions to canvass, In/Out of scope, Inputs, Done-when. Read it first; this block is the pointer, not a duplicate.
- **Branch op at session head:** `git checkout -b m1/02-flat-roster` off `m1/roster`. The 2.1b FF-merge is already satisfied (`m1/roster` == `m1/01b-fe-conventions` == `f3bb595`).
- **Three decisions to canvass at session head (STOP-AND-CONFIRM):** (1) admin-CRUD authoring shape — generalized factory vs hand-authored per entity; (2) admin auth-predicate factory shape — reusable factory over `has_role_at_least` (ADR-0062) vs inline; (3) seed-tooling design details — CSV→Payload mapping, JSONB-column representation in CSV, entity dependency ordering, idempotency, seed-folder location. The through-the-Command-pipeline decision is already locked (Session 38). All three ADR-worthy; ADRs land from **ADR-0067**.
- **Locked Session 38:** `seed_db` dispatches through the Command pipeline; Click deferred (`seed_db` uses `argparse`); `just` env-setup split from data-init. See `steps.md` § Step 2.2 scope-addition note.
- **Read routes** (`GET /<entity>` + `GET /<entity>/{id}`) land per-entity, hand-authored — low complexity, 2 endpoints/entity; frontend admin pages (2.2c) consume them, can't wait for M7's reporting work.
- **Coordination point — adapter boundary.** 2.2a's Contract is the first M1+ write-path domain code to hit M0.4's adapter — `json_column()` for `code_flat_fee_schedule`, `SERIALIZABLE` per ADR-0056. First chance to verify the adapter on real domain code.
- **Carry-forward for 2.2b (not 2.2a):** `User.employee_id` FK + UNIQUE constraint lands in 2.2b's Employee migration (M1.1 left it a plain UUID per ADR-0061 § Consequences).

**For Phase 2 broadly (M1+ outlook):**

- **Step 1 / M0 ✓ COMPLETE 2026-05-19** (Session 33). Substrate for every M1+ command in place: Command base + dispatcher with retry loop, history infrastructure with real capture sink, advisory-lock + SERIALIZABLE primitives behind a documented adapter, Alembic + CI green on SQLite.
- **Step 2.1 / M1.1 ✓ COMPLETE 2026-05-19** (Session 35). Auth substrate established for M1.2+ admin work. Per-role pytest fixtures available; concrete Caller flows through dispatcher.
- **Step 2.1b ✓ COMPLETE 2026-05-20** (Sessions 36–37). Frontend four-layer architecture + UI/form stack (shadcn `radix-lyra`, Tailwind 4, Zod, RHF) + API-client relocation + M1.1 auth port; `frontend/src/PATTERNS.md` is the conventions doc M1.2 frontend work (2.2c) consumes.
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

**Session 39 — Step 2.2a / M1.2 backend substrate + Contract exemplar.** Settle M1.2's three backend abstractions (admin-CRUD authoring factory, admin auth-predicate factory, seed framework) and prove them end-to-end against Contract. **Case 3 scoped session** — `planning/steps.md` § Step 2.2a carries the full brief. **Branch op at session head:** `git checkout -b m1/02-flat-roster` off `m1/roster`. Next ADR free: **ADR-0067**.

### Prompt for the next session

> Resume work. **Step 2.2 / M1.2 partitioned** 2026-05-20 (Session 38, Case 2) into 3 sub-steps. Session 39 opens **Step 2.2a / M1.2 backend substrate + Contract exemplar** — a Case 3 scoped session.
>
> **Branch op at session head:**
> ```
> git checkout -b m1/02-flat-roster m1/roster
> ```
> The 2.1b FF-merge is already satisfied — `m1/roster` == `m1/01b-fe-conventions` == `f3bb595`.
>
> **The full 2.2a brief is `planning/steps.md` § Step 2.2a** — Goal, the three decisions to canvass at session head, In/Out of scope, Inputs, Done-when. Read it first. 2.2a settles three backend abstractions (admin-CRUD authoring factory, admin auth-predicate factory, seed framework) and proves them end-to-end against **Contract** — the hardest, most non-uniform of the five M1.2 entities (JSONB `code_flat_fee_schedule`, derived `validity`). 2.2b then applies the result to the four remaining backend entities; 2.2c builds the frontend.
>
> **Three decisions to canvass at session head (STOP-AND-CONFIRM gate):** (1) admin-CRUD authoring shape — generalized factory vs hand-authored per entity; (2) admin auth-predicate factory shape — reusable factory over `has_role_at_least` vs inline; (3) seed-tooling design details — CSV→Payload mapping, JSONB-column representation in CSV, entity dependency ordering, idempotency, seed-folder location. The seed through-the-Command-pipeline decision is already locked (Session 38). All three are ADR-worthy; ADRs land this session from **ADR-0067**.
>
> **Locked from Session 38:** `seed_db` dispatches CSV rows through the Command pipeline (not direct ORM inserts — keeps seeded data real); Click adoption deferred (`seed_db` uses stdlib `argparse`); `just` env-setup split from interactive/destructive data-init. See `steps.md` § Step 2.2 scope-addition note. Standing requirement: every entity-adding sub-step from M1.2 onward maintains `seed_db` coverage.
>
> **Read first:** Session 38 summary above + the "For Session 39" Open-questions block; `steps.md` § Step 2.2 envelope + § Step 2.2a; ADR-0047 (Cluster 1 admin predicates), ADR-0040 (role catalog), ADR-0043 / ADR-0044 / ADR-0045 (Contract entity + shape + `code_flat_fee_schedule`), ADR-0061 / ADR-0062 (auth substrate + `Caller` + `has_role_at_least`); `data-model.md` § Contract. Skim `app/framework/{command,dispatcher,caller,history,adapter}.py`, `app/domain/auth.py` (entity pattern), `app/cli/bootstrap_admin.py` (CLI pattern), `tests/conftest.py` § per-role fixtures.
>
> **Out of scope:** Employee / School / Contractor / User-admin-CRUD (2.2b); all frontend (2.2c); M1.3 / M1.4; WABundle; PaaS vendor pick + Postgres CI (both stay deferred); the two queued frontend follow-ups (theme toggle, themeable architecture).
>
> **Process notes:** STOP-AND-CONFIRM gate applies, including source code. Migration discipline per [[project-neon-current-policy]] (author → `uv run alembic upgrade head` on Neon → commit). Preserve incremental commits (per-entity granularity from 2.2b on). Branch `m1/02-flat-roster` shared across 2.2a/2.2b/2.2c, FF-merge to `m1/roster` at M1.2 close. Next ADR free: **ADR-0067**.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-18)
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 ✓ COMPLETE 2026-05-19 (Session 33)**; **Step 2 partitioned into 4 sub-steps 2026-05-19 (Session 34)**; **Step 2.1 ✓ COMPLETE 2026-05-19 (Session 35)**; **Step 2.1b ✓ COMPLETE 2026-05-20 (Sessions 36–37)**; **Step 2.2 partitioned into 2.2a/2.2b/2.2c 2026-05-20 (Session 38)**; M1.3 / M1.4 stubs; Steps 3–9 stubs)
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
