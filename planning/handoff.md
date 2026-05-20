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

**Implementation** — Phase 2. **Step 1 / M0 Foundations ✓ COMPLETE 2026-05-19 (Session 33).** **Step 2 / M1 Roster** partitioned 2026-05-19 (Session 34, Case 2) into 4 sub-steps. **Step 2.1 / M1.1 Auth substrate + frontend shell ✓ COMPLETE 2026-05-19 (Session 35).** **Step 2.1b / Frontend architecture & conventions** (inserted; not a roadmap milestone) ✓ **COMPLETE 2026-05-20** — 2.1b-A (Session 36; ADR-0064 / 0065) + 2.1b-B (Session 37; ADR-0066). **Step 2.2 / M1.2 Admin substrate + flat roster** partitioned 2026-05-20 (Session 38, Case 2) into 3 sub-steps — 2.2a (backend substrate + Contract exemplar) / 2.2b (backend remainder) / 2.2c (frontend admin pages); dev seed tooling scoped in. **Step 2.2a ✓ COMPLETE 2026-05-20 (Session 39)** — branch `m1/02-flat-roster`, 7 commits. **Session 40 (2026-05-20) — backend-structure review:** found M1.1/M1.2 drifted from the Session-32 hexagonal `app/` design; settled plural naming + per-entity domain folders; ratified Session 39's five in-flight decisions (#2 reversed). M1.2 closeout (ADRs from **ADR-0067**) + conventions docs + structure refactor repackaged as a new inserted **Step 2.2b — Backend architecture & conventions** (2.2b-A planning / 2.2b-B refactor); old 2.2b/2.2c renumbered to **2.2c/2.2d**. **Next: Session 41 — Step 2.2b-A.** M1.3 / M1.4 stubs in `steps.md`.

## Last session summary

**Session 40 — backend-structure review (2026-05-20).** The session planned as the Session 39 ADR review opened instead as a user-led review of the backend file/folder structure M1.1/M1.2 produced. No code logic written; no ADRs written (correctly — they depend on forks 2.2b-A will settle). `redact_csv.py` committed (its own commit) so it is no longer carried untracked.

**Finding — drift from the agreed hexagonal `app/` design** (`planning/follow-ups/backend-directory-structure-rewind.md`, Session 32, ~70/30 confidence). The agreed design was per-entity folders inside `domain/` plus an `adapters/` folder for concrete I/O. What M1.1/M1.2 actually built: `domain/` flat (`domain/contract.py`) with a `domain/commands/` type-bucket; `adapters/` left empty while concrete-I/O code (`db.py`, `adapter.py`, `capture.py`, `history.py`, `locks.py`) piled into `framework/`; route files carry transport DTOs (`LoginRequest`, `ContractWriteRequest`, `ContractRead`) and cookie helpers. The user's three concerns were this drift, not a clash with hexagonal.

**Settled this session:**

- **Plural naming** — all folders + type-noun files plural (`domain/contracts/`, `entities.py`, `commands.py`); never singular.
- **Per-entity domain folders** — return to the agreed design; replaces the flat layout + the `domain/commands/` type-bucket.
- **Routes hold no transport DTOs / helpers** — they move to a transport-layer module, *not* into `domain/` (DTOs are the HTTP contract, not domain objects).
- **Session 39's five in-flight decisions ratified** — #1 uniqueness handler pre-check (provisional — revisit if proven insufficient), #3 PascalCase command-class names, #4 `EntityNotFound`→404, #5 ADR-0047 Cluster 1 → Contract: approved as-is. **#2 reversed** — materialize `created_*/updated_*` columns on audit-metadata entities so they surface in read schemas; resolves the `data-model.md` § Conventions divergence in the doc's favour. The columns are a dispatcher-maintained read projection of `command_audit_log`, not a rival source of truth.

**Outcome — new inserted Step 2.2b.** M1.2 closeout (ADRs from ADR-0067) + the conventions docs (`backend/CLAUDE.md` + `backend/app/PATTERNS.md`) + the structure refactor are packaged as **Step 2.2b — Backend architecture & conventions** (inserted; the backend twin of Step 2.1b), partitioned 2.2b-A (closeout + conventions) / 2.2b-B (refactor). Old 2.2b/2.2c renumbered to **2.2c/2.2d**. 2.2b runs before 2.2c so its four entities land on the corrected structure. Open forks for 2.2b-A: see § Open questions.

**Session 39 substrate (unchanged, input to 2.2b-A).** 2.2a's 7 commits on `m1/02-flat-roster` (`git log m1/roster..HEAD`) — Contract entity/commands/routes, the three approved abstractions (`require_role` factory; hand-authored Command classes over `crud.py` helpers; `seed_db` through the pipeline), production dispatcher wiring. 71 backend tests + ruff + pyright green; migration `6dd5906ef088` applied to Neon. A live Neon data round-trip was not run (schema-side verified only).

`_file-rules.md` **not regenerated** — no `## File contract` block changed.

---

## Open questions

**Queued — frontend follow-ups (post-2.1b; not yet scheduled).** Raised by the user at Session 37 wrap-up; still queued — **not** part of M1.2's sub-steps (2.2a/2.2b/2.2c/2.2d).

- **Item 1 — theme toggle (small, its own step).** A light / dark / auto toggle in the admin shell header; button at `src/components/ThemeToggleBtn`. Substrate already exists — `src/index.css` has `:root` + `.dark` token blocks and `next-themes` is installed. Work: mount `<ThemeProvider>` from `next-themes` (not currently mounted — the Sonner `Toaster` just degrades to "system"), build `ThemeToggleBtn`, wire it into `pages/admin-shell`. `next-themes`' `enableSystem` gives "auto" free. ~30 min. A small dedicated standalone step — slot it between M1.2 sub-steps or after M1.2; out of scope for 2.2d.
- **Item 2 — themeable architecture (POST-MVP).** A theme registry + user-facing theme dropdown; each theme defines light + dark; a user picks either one theme (both modes) or distinct light/dark themes. Design the schema for the general case: a theme = one named token-value set for a single mode; a user preference = `(lightThemeId, darkThemeId, mode)`. Per-user persistence to a `User` preference is a **backend change** → firmly post-MVP, ADR-worthy when it lands (superseding ADR per `steps.md`'s contract). Not MVP — default theme suffices; not in `mvp.md`'s 6 must-haves. **Prep already done:** `PATTERNS.md` § UI components now mandates styling via semantic theme tokens only, which keeps this a drop-in; nothing else to build now.

**For Step 2.2b-A — settle the structure forks (STOP-AND-CONFIRM), then write the M1.2 ADRs + conventions docs.**

- **`framework/` cohesion.** It is a grab-bag of three things — the command engine (`command`/`dispatcher`/`caller`/`crud`/`exceptions`/`runtime`), concrete I/O (`db`/`adapter`/`capture`/`history`/`locks` + auth hashing/sessions), and transport (`error_handlers`). Fork: finish the hexagonal split (slim engine + populate the empty `adapters/` + move `error_handlers` to transport) vs. keep one folder. **Agent rec ~75%: finish the split** — renaming a grab-bag does not fix cohesion, and `db` as a name is wrong outright. `error_handlers`→transport is clear-cut regardless.
- **`routes/` shape.** Per-resource folders (`routes/contracts/{routes,schemas}.py`) vs. flat `routes/` + a schemas module. Either gets DTOs out of the handler files.
- **DTO vs command `Payload`.** `ContractWriteRequest` ≈ `CreateContract.Payload`. Fork: keep the pair separate vs. collapse. **Agent rec ~70%: keep separate** — a genuine layer seam (the HTTP contract evolves independently of the command payload).
- **Smaller:** `entities.py` vs `models.py` for the per-entity model file (agent lean `entities.py`); audit-column scope — audit_log entities only vs. uniform across all entities per `data-model.md` § Conventions (agent lean uniform).
- **ADRs to write** (from ADR-0067) — the three Session-39 approved abstractions (admin-CRUD authoring shape; `require_role` predicate factory; seed-tooling shape); the five ratified in-flight decisions; a backend-architecture ADR (twin of ADR-0064). Write them *after* the forks settle — several reference final code paths. The audit-metadata `data-model.md` divergence is resolved (decision #2: materialize) — the ADR records it; no separate review needed.

**For Step 2.2c (backend remainder) — carry-forwards.** `User.employee_id` FK + UNIQUE in the Employee migration (ADR-0061 — M1.1 left it a plain UUID); `seed_db` coverage for all four entities; extract a shared `require_unique` helper from Contract's `_require_unique_number` once User's `username` is the second consumer. (`redact_csv.py` — done, committed Session 40.)

**For Phase 2 broadly (M1+ outlook):**

- **Step 1 / M0 ✓ COMPLETE 2026-05-19** (Session 33). Substrate for every M1+ command in place: Command base + dispatcher with retry loop, history infrastructure with real capture sink, advisory-lock + SERIALIZABLE primitives behind a documented adapter, Alembic + CI green on SQLite.
- **Step 2.1 / M1.1 ✓ COMPLETE 2026-05-19** (Session 35). Auth substrate established for M1.2+ admin work. Per-role pytest fixtures available; concrete Caller flows through dispatcher.
- **Step 2.1b ✓ COMPLETE 2026-05-20** (Sessions 36–37). Frontend four-layer architecture + UI/form stack (shadcn `radix-lyra`, Tailwind 4, Zod, RHF) + API-client relocation + M1.1 auth port; `frontend/src/PATTERNS.md` is the conventions doc M1.2 frontend work (2.2d) consumes.
- **Step 2.2a ✓ COMPLETE 2026-05-20** (Session 39). M1.2's three backend abstractions (admin auth-predicate factory, admin-CRUD authoring helpers, `seed_db` framework) + Contract end-to-end (entity / commands / routes); production dispatcher wired; first M1+ `command_audit_log` writer. M1.2 closeout ADRs deferred to Step 2.2b-A.
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

**Session 41 — Step 2.2b-A / M1.2 closeout + backend conventions.** Settle the four structure forks (§ Open questions "For Step 2.2b-A"), write all deferred M1.2 ADRs from **ADR-0067**, and produce `backend/CLAUDE.md` + `backend/app/PATTERNS.md`. Planning + documentation — no code refactor (that is 2.2b-B). Big step: run a Case 2 check at session head.

### Prompt for the next session

> Resume work. **Session 40 completed a backend-structure review** (no code logic, no ADRs) and inserted **Step 2.2b — Backend architecture & conventions** before the backend-remainder step. Branch unchanged: `m1/02-flat-roster`.
>
> **Session 41 is Step 2.2b-A — M1.2 closeout + backend conventions.** Open with a STOP-AND-CONFIRM canvass of the four structure forks in `handoff.md` § Open questions "For Step 2.2b-A": (1) `framework/` cohesion — finish the hexagonal engine/`adapters`/transport split vs. keep one folder (agent rec ~75% finish it); (2) `routes/` shape — per-resource folders vs. flat + schemas module; (3) DTO vs command `Payload` — keep separate vs. collapse (agent rec ~70% keep separate); (4) `entities.py` vs `models.py` + audit-column scope. **The plural-naming rule and the per-entity-domain-folder layout are already settled — do not re-deliberate them.**
>
> On ratification, **write the M1.2 ADRs from ADR-0067**: the three Session-39 approved abstractions (admin-CRUD authoring shape; `require_role` predicate factory; seed-tooling shape); the five ratified in-flight decisions (#1 uniqueness pre-check; #2 **materialize** `created_*/updated_*` columns; #3 PascalCase command names; #4 `EntityNotFound`→404; #5 Cluster 1 → Contract); and a backend-architecture ADR (the twin of ADR-0064) covering the per-entity / framework-split / routes / naming conventions. Write the ADRs *after* the forks settle — several reference final code paths.
>
> Then produce **`backend/CLAUDE.md`** (thin, auto-loaded) + **`backend/app/PATTERNS.md`** (the conventions doc 2.2c+ consumes) — modelled on `frontend/CLAUDE.md` + `frontend/src/PATTERNS.md`.
>
> **No code refactor this session** — that is Step 2.2b-B, a separate Case 2 session that executes these patterns against the existing Contract + auth + framework + routes code and materializes the audit columns.
>
> **Case 2 check at session head:** 2.2b-A is big — four independent forks + ~8 ADRs + 2 docs. Run the 7-signal checklist; the likely seam is forks+ADRs vs. docs. Split if it fires.
>
> **Read first:** `handoff.md` § Session 40 summary + § Open questions "For Step 2.2b-A"; `steps.md` § Step 2.2b; `planning/follow-ups/backend-directory-structure-rewind.md`; the Session 39 commits (`git log m1/roster..HEAD --stat`); `frontend/CLAUDE.md` + `frontend/src/PATTERNS.md` + ADR-0064 as the doc/ADR model.
>
> **Process notes:** STOP-AND-CONFIRM gate applies to the forks and ADRs. Preserve incremental commits. Branch `m1/02-flat-roster` shared across 2.2a–2.2d, FF-merge to `m1/roster` at M1.2 close. Next ADR free: **ADR-0067**.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-18)
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 ✓ COMPLETE 2026-05-19 (Session 33)**; **Step 2 partitioned into 4 sub-steps 2026-05-19 (Session 34)**; **Step 2.1 ✓ COMPLETE 2026-05-19 (Session 35)**; **Step 2.1b ✓ COMPLETE 2026-05-20 (Sessions 36–37)**; **Step 2.2 partitioned into 2.2a/2.2b/2.2c 2026-05-20 (Session 38)**; **Step 2.2a ✓ COMPLETE 2026-05-20 (Session 39)**; **Step 2.2b — Backend architecture & conventions — inserted 2026-05-20 (Session 40), old 2.2b/2.2c renumbered to 2.2c/2.2d**; M1.3 / M1.4 stubs; Steps 3–9 stubs)
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
