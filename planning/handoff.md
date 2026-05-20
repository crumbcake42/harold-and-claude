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

**Implementation** — Phase 2. **Step 1 / M0 Foundations ✓ COMPLETE 2026-05-19 (Session 33).** **Step 2 / M1 Roster partitioned 2026-05-19 (Session 34, Case 2)** into 4 sub-steps. **Step 2.1 / M1.1 Auth substrate + frontend shell ✓ COMPLETE 2026-05-19 (Session 35).** Currently on branch **`m1/01-auth-shell`** (tip = `f0a651d`, two commits: backend slice `b7b75b6` + frontend/tests slice `f0a651d`). Sub-step status: **Step 2.1b / Frontend architecture & conventions inserted 2026-05-19** (an insertion between M1.1 and M1.2 — see `sessions.md` § Restructure log) is the next session; M1.2 follows it as Session 37; M1.3 / M1.4 stubs in `steps.md`. **Branch state pending:** `m1/01-auth-shell` not yet FF-merged to `m1/roster` (decision deferred to user signal). **Next branch op at Session 36 head:** FF-merge `m1/01-auth-shell` → `m1/roster` if not already done, then `git checkout -b m1/01b-fe-conventions` off `m1/roster`.

## Last session summary

**Session 35 — Step 2.1 / M1.1 Auth substrate + frontend shell (2026-05-19, Case 3 implementation).** Auth substrate landed end-to-end on `m1/01-auth-shell`. Three ADRs (ADR-0061 / 0062 / 0063), two implementation commits, one Neon migration applied, one non-obvious bug surfaced + fixed at browser verification, one new project memory.

**The six *how*-level decisions canvassed at session head + pinned:**

1. **Session token:** `secrets.token_urlsafe(32)` — 256 bits, URL-safe, opaque.
2. **Argon2 parameters:** explicit OWASP 2024 pin (`time_cost=2`, `memory_cost=19456 KiB`, `parallelism=1`, `hash_len=32`, `salt_len=16`) — hashes stay verifiable across `argon2-cffi` version bumps.
3. **`Caller` module:** new `app/framework/caller.py`; removed Protocol stub from `command.py`.
4. **`app.framework.auth`:** single module (~150 LOC).
5. **Frontend route guard:** TanStack Router file-based `_authenticated.tsx` layout + `beforeLoad` via `ensureQueryData`.
6. **Pytest fixture shape:** dependency-override of `current_user` for `as_superadmin / as_admin / as_coordinator / as_auditor`.

Plus the `bootstrap_admin` CLI uses stdlib `input()` + `getpass`; Click adoption deferred to the 3rd CLI command per the `app/cli/` convention.

**Backend (commit `b7b75b6`).** `app/framework/caller.py` (concrete Caller + Role StrEnum + `has_role_at_least`); `app/framework/command.py` (dropped Caller Protocol, imports from caller); `app/domain/auth.py` (User / UserRole / Session models — User.employee_id nullable plain UUID until M1.2's Employee migration adds the FK); `app/framework/auth.py` (argon2id hash/verify with pinned params + session CRUD + `current_user` dep with `_ensure_utc` SQLite-tz shim); `app/routes/auth.py` (POST `/auth/login`, POST `/auth/logout`, GET `/auth/me`); CORS middleware in `app/main.py`; config additions (`frontend_origin`, `session_cookie_name`, `session_ttl_hours`, `cookie_secure`); migration `25ea83fcec61_auth_substrate` (autogen + applied to Neon per [[project-neon-current-policy]]); pyproject (argon2-cffi dep + ruff `extend-immutable-calls` for FastAPI deps to suppress B008 false positives).

**Frontend + tests (commit `f0a651d`).** `app/cli/bootstrap_admin.py` (stdlib `input()` + `getpass`, idempotent on collision); per-role pytest fixtures + 13 new auth tests in `tests/test_auth.py` (40 total backend tests green); regenerated `contracts/openapi.json` + `frontend/src/api/`; frontend auth shell — `api/configure.ts` (client.setConfig with `credentials: 'include'`), `hooks/useCurrentUser.ts` (TanStack Query hook + `currentUserQueryOptions` for use in route loaders), `routes/login.tsx` (form + mutation), `routes/_authenticated.tsx` (`beforeLoad` redirect guard), `routes/_authenticated/index.tsx` (admin shell + logout button), `main.tsx` (`configureApiClient` + `queryClient` on router context), `__root.tsx` (typed router context).

**Non-obvious bug surfaced + fixed at browser verification (pinned in ADR-0063).** Original login `onSuccess` used `queryClient.invalidateQueries({queryKey: ['auth', 'me']})` then `navigate({to: '/'})`. With no active subscriber to the user query on the `/login` page, `invalidateQueries` (default `refetchType: 'active'`) marked stale but did not refetch. Then `navigate` ran; `_authenticated.beforeLoad` called `ensureQueryData` which returned the *stale-but-cached* null (ensureQueryData returns cached data even when stale; only fetches on missing); beforeLoad bounced back to `/login`. Fix: `queryClient.setQueryData(currentUserQueryKey, response.data)` — the login response already contains the Caller, so seed the cache directly. Rule pinned: for auth-state mutations where the response carries the new value, prefer `setQueryData` over `invalidateQueries`.

**The 8 locked *what*-level decisions from Session 34 → ADR partition:**

- ADR-0061 bundles decisions 1 (sessions) + 2 (argon2id) + 3 (bootstrap) + 4 (CORS) + 5 (CSRF deferral) + 8 (non-Command login).
- ADR-0062 records decision 6 (Caller concrete shape) — closes ADR-0059's *"Caller concrete shape"* carry-forward.
- ADR-0063 records decision 7 (frontend route guard) + the `setQueryData` rule from the bug above.

**Commits landed this session (2).**

1. `b7b75b6` on `m1/01-auth-shell` — M1.1 step 1/2: backend auth substrate.
2. `f0a651d` on `m1/01-auth-shell` — M1.1 step 2/2: bootstrap CLI + per-role fixtures + frontend auth shell.

Planning close-out (this commit) lands ADRs 0061 / 0062 / 0063 + steps.md (Step 2.1 marked complete) + handoff.md (this rewrite).

**ADRs landed this session (3).** ADR-0061 (auth substrate bundle), ADR-0062 (Caller concrete shape — closes ADR-0059 carry-forward), ADR-0063 (frontend route guard + `setQueryData` rule).

**Memories saved (1 new).** `project_neon_current_policy` — Neon dev DB stays current with alembic head; apply migrations to Neon immediately at landing; `.env`'s `DATABASE_URL` is authoritative; throwaway sqlite OK for pre-commit iteration only. Triggered by Session 33's `b555ac8d13da` migration never being applied to Neon, surfaced when M1.1's autogen failed with "Target database is not up to date."

**Files touched.** Backend: `app/cli/bootstrap_admin.py` (new), `app/config.py`, `app/domain/auth.py` (new), `app/framework/auth.py` (new), `app/framework/caller.py` (new), `app/framework/command.py`, `app/framework/db.py`, `app/framework/dispatcher.py`, `app/main.py`, `app/routes/auth.py` (new), `migrations/env.py`, `migrations/versions/25ea83fcec61_auth_substrate.py` (new), `pyproject.toml`, `uv.lock`, `tests/conftest.py`, `tests/test_auth.py` (new), `tests/test_capture_sink_integration.py`, `tests/test_dispatcher.py`, `tests/fixtures/smoketest/commands.py`. Frontend: `src/api/` (regenerated), `src/api/configure.ts` (new), `src/hooks/useCurrentUser.ts` (new), `src/main.tsx`, `src/routeTree.gen.ts`, `src/routes/__root.tsx`, `src/routes/index.tsx` (deleted → moved under `_authenticated/`), `src/routes/_authenticated.tsx` (new), `src/routes/_authenticated/index.tsx` (new), `src/routes/login.tsx` (new). Shared: `contracts/openapi.json` (regenerated). Planning: `decisions.md` (3 ADRs appended), `steps.md` (Step 2.1 marked complete), `handoff.md` (this rewrite). `_file-rules.md` **not regenerated** — no `## File contract` block changed.

**Verification at session close.** Backend: 40 pytest green (27 prior + 13 new), ruff clean. Frontend: 1 vitest green, ESLint clean, `tsc --noEmit` clean. Neon dev DB at head (`25ea83fcec61_auth_substrate` applied). Browser flow round-tripped by user — `/` → `/login` → login → admin shell at `/` → sign out → back at `/login`; invalid credentials → "invalid credentials" message.

---

## Open questions

**For Session 37 — Step 2.2 / M1.2 Admin substrate + flat roster** (Case 2 sizing then likely partitioned implementation). *Step 2.1b (frontend architecture & conventions) was inserted ahead of M1.2 on 2026-05-19 and is now Session 36; the M1.2 detail below is one session out and stays as forward reference.*

- **Branch op at session head:** if `m1/01-auth-shell` is not yet FF-merged to `m1/roster` (check `git log m1/roster..m1/01-auth-shell`), do that first. Then `git checkout -b m1/02-flat-roster` off `m1/roster`. Tag-anchor `m1.1-complete` on `m1/roster` is optional (the `m<X>-complete` convention is for milestone close per [[project-branching-convention]], not sub-step close).
- **Case 2 sizing required at session head.** Step 2.2 has a stub brief in `steps.md` — not a scoped prompt. Expect sizing to surface several fit-checklist signals: independently-deliberable decisions (admin-CRUD authoring shape — generalized factory vs hand-authored per entity, ADR-worthy; admin auth-predicate factory shape, ADR-worthy); five new entity tables (Employee, School, Contractor, User-side admin CRUD, Contract); cross-concern reach (backend entity authoring + first ADR-0047 predicate landing + frontend per-entity admin pages); likely >60 min duration. **Likely partition needed** — natural seam is backend entities + commands → backend admin routes → frontend admin pages. Hold the partition canvass at session head per Case 2 protocol; don't pre-decide.
- **ADR numbering.** Step 2.1b (Session 36) takes **ADR-0064** (poss. +ADR-0065 for the UI/form stack); M1.2 therefore starts at the next free number at its write time. M1.2 likely lands 1–2 ADRs: admin-CRUD authoring shape (generalized factory vs hand-authored), admin auth-predicate factory shape if non-obvious. First ADR-0047 predicate landing in M1+ code; the `role >= admin` Cluster 1 class rule is the first concrete use of `has_role_at_least` from ADR-0062.
- **Five entities to land** (per ADR-0047 Cluster 1):
  - **Employee** — HR-driven, no lifecycle, audit-log history per ADR-0052.
  - **School** — flat, no lifecycle, audit-log history.
  - **Contractor** — flat, no lifecycle, audit-log history.
  - **User** (admin-CRUD beyond M1.1's auth-substrate insert) — `edit_user` for password resets and `employee_id` link; `delete_user` per delete policy.
  - **Contract** — hoisted from M2 per Session 34 sizing. ADR-0044 carries the structural shape; admin-CRUD in character per ADR-0047 Cluster 1. The `code_flat_fee_schedule` (per ADR-0045) is the substantive attribute.
  - Add Employee FK + UNIQUE constraint to `user.employee_id` in the M1.2 migration (M1.1 left it as a plain UUID per the carry-forward note in ADR-0061 § Consequences).
- **Decision detail to canvass at session head:**
  - **Admin-CRUD authoring shape.** Generalized factory (`make_create_command(Entity, Payload)`) vs hand-authored Command per entity. Factory wins on volume (5 entities × 3 commands = 15); hand-authored wins on flexibility for non-uniform predicates. Worth a structured canvass. Likely ADR-worthy regardless of pick.
  - **Read routes** (`GET /<entity>`, `GET /<entity>/{id}`). Per-entity hand-authored, or generalized? Frontend admin pages need them in M1.2 — can't wait for M7's reporting work. Likely hand-authored (5 endpoints, low complexity).
  - **Admin auth-predicate factory.** ADR-0047 Cluster 1 class rule is uniform `role >= admin`. Encode once as a reusable predicate factory; or inline per command? Lean factory.
  - **Frontend admin page shape.** List + detail/form per entity, built on the shadcn/ui + four-layer conventions landed in Step 2.1b. Shadcn/ui is adopted there — no longer an open M1.2 decision; M1.2 consumes `frontend/src/PATTERNS.md`.
- **Read first at session head:** Session 35 summary above + Open questions for Session 36 + `planning/steps.md` § Step 2 high-level + § Step 2.2 stub + ADR-0040 (role catalog) + ADR-0047 (per-command authorization predicates — Cluster 1 is M1.2's surface) + ADR-0044 / ADR-0045 (Contract + WABundle structural shape, contract scoping) + ADR-0061 / 0062 (auth substrate + Caller from Session 35) + `data-model.md` § Roster entities (per-entity attribute rosters). Skim `app/framework/caller.py` + `app/framework/auth.py` (consumed by M1.2 routes); `app/domain/auth.py` (existing entity pattern that M1.2 entities mirror); `app/framework/history.py` (mixin pattern + audit-log shape for the 5 new entities); `tests/conftest.py` § per-role fixtures (M1.2 command tests build on these).
- **Coordination points:**
  - The User table got created in M1.1 with `employee_id` as a plain UUID + no FK. M1.2's Employee migration adds the FK + UNIQUE constraint via a follow-up alter. Verify the alter handles existing rows (the bootstrap superadmin will have null `employee_id`, which is the nullable-FK shape ADR-0041 Gap 5 anticipates).
  - First write-path commands hit M0.4's adapter boundary — `json_column()` for any JSONB columns (e.g., `Contract.code_flat_fee_schedule`); `SERIALIZABLE` isolation per ADR-0056 D1.a default. First chance to verify the adapter behaves as designed on real domain code.
- **Carry-forwards for M1.2 to land:**
  - `User.employee_id` FK + UNIQUE constraint (per ADR-0061 § Consequences carry-forward).
  - First ADR-0047 Cluster 1 predicate landing — formalize `role >= admin` class rule as a reusable predicate factory.

**For Phase 2 broadly (M1+ outlook):**

- **Step 1 / M0 ✓ COMPLETE 2026-05-19** (Session 33). Substrate for every M1+ command in place: Command base + dispatcher with retry loop, history infrastructure with real capture sink, advisory-lock + SERIALIZABLE primitives behind a documented adapter, Alembic + CI green on SQLite.
- **Step 2.1 / M1.1 ✓ COMPLETE 2026-05-19** (Session 35). Auth substrate established for M1.2+ admin work. Per-role pytest fixtures available; concrete Caller flows through dispatcher.
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
- **Commit pattern: preserve incremental checkpoints; FF sub-step branches to `m1/roster`; merge `m1/roster` → `dev` with `--no-ff` + tag `m1-complete` at M1 close** (per [[preserve-incremental-commits]] + [[project-branching-convention]]).
- **Contract-drift CI job enforces schema + client are in sync.** Any backend OpenAPI-surface change requires `just gen-openapi` + commit of `contracts/openapi.json` + `frontend/src/api/` (see [[committed-generated-artifacts]]).
- **Cross-check architecture.md out-of-band concerns at every Case 2 sizing** per [[check-out-of-band-concerns]] — applied at M1 (caught auth slip); apply at M2+. For M1.2 Case 2 sizing: the relevant out-of-band concerns are file storage (not surfaced until M5), background jobs (not surfaced until M3 RFA auto-draft regeneration), notifications (post-MVP). None of those apply to M1.2.
- **`mvp.md` is the canonical MVP scope reference.**
- **Migration discipline per [[project-neon-current-policy]].** Author migration → `uv run alembic upgrade head` against Neon → commit. Throwaway sqlite for shape iteration before commit.

## Next session

**Session 36 — Step 2.1b / Frontend architecture & conventions (Case 2 sizing, then implementation).** An inserted step (2026-05-19) — adapt-and-port `sca-ih-tracker`'s four-layer frontend architecture into this repo before M1.2's first substantial frontend feature. Branch op at session head: FF-merge `m1/01-auth-shell` → `m1/roster` if not already done, then `git checkout -b m1/01b-fe-conventions` off `m1/roster`. Full plan: `.claude/plans/i-want-to-have-fluttering-wozniak.md`. ADRs 0064+. **M1.2 follows as Session 37** (staged prompt below; detail under Open questions above).

### Prompt for the next session

> Resume work. **Step 2.1 / M1.1 ✓ COMPLETE** (Session 35). **Step 2.1b / Frontend architecture & conventions** is an inserted step (2026-05-19; not a roadmap milestone — see `sessions.md` § Restructure log). Adapt-and-port `sca-ih-tracker`'s mature four-layer frontend architecture into this repo so M1.2's first substantial frontend feature builds on settled conventions.
>
> **Full plan — read first:** `.claude/plans/i-want-to-have-fluttering-wozniak.md`. It is the scoped brief for this session; `steps.md` § Step 2.1b is the summary.
>
> **Branch op at session head:**
> ```
> git log m1/roster..m1/01-auth-shell    # confirm M1.1 commits not yet on m1/roster
> git checkout m1/roster
> git merge --ff-only m1/01-auth-shell   # if not already merged
> git checkout -b m1/01b-fe-conventions
> ```
> Confirm the branch name at session head — `m<N>/NN-subslug` has no clean insertion slot; `m1/01b-fe-conventions` is a minor suffix bend.
>
> **Case 2 sizing first.** The step is M–L. Likely 2-way partition — natural seam: **A** adopt + scaffold + document (install shadcn/Tailwind/Zod/RHF, wire `@/` alias, relocate `src/api/generated/`, scaffold the four-layer folders, add ESLint layering rules, write `PATTERNS.md` + `CLAUDE.md`); **B** port the M1.1 auth code into the four-layer model + test/story colocation. Surface the partition in chat per the STOP-AND-CONFIRM gate; don't pre-decide.
>
> **Locked scope** (planning side-session, 2026-05-19): doc + ESLint enforcement + port M1.1 auth; adopt shadcn/ui + Zod + react-hook-form now; conventions doc co-located (`frontend/src/PATTERNS.md` + thin `frontend/CLAUDE.md`). The port mapping, the adaptations (cookie-session variant of the route guard; no entity-abstractions yet), critical files, and verification steps are all in the plan file.
>
> **ADRs expected:** 1–2 at write time **ADR-0064+** — four-layer FE architecture + API barrel + test/story colocation + ESLint enforcement; poss. a second for the shadcn `radix-lyra` + Zod + RHF stack.
>
> **Read first:** the plan file; `steps.md` § Step 2.1b; ADR-0063 (frontend route-guard pattern — the port must preserve it); current `frontend/src/` (M1.1 auth shell). Reference repo: `C:\Users\crummy_P51\projects\sca-ih-tracker\frontend` — `src/PATTERNS.md`, `CLAUDE.md`, `eslint.config.js`, `src/features/schools/api/schools.ts`, `src/features/auth/api/hooks.ts`.
>
> **Out of scope:**
> - Any M1.2 roster entity / command / route / admin page (Session 37).
> - Entity-abstraction patterns (`EntityListPage`, `useEntityForm`, `DataTable`, comboboxes) — extracted just-in-time later, not invented now.
> - Backend changes; OpenAPI-surface changes.
>
> **Process notes:**
> - **STOP-AND-CONFIRM gate applies, including for source code.** Canvass the partition + non-obvious structural decisions in chat before writing.
> - **Commit pattern: preserve incremental checkpoints** — coherent atomic changes at green-state boundaries.
> - **Branch:** `m1/01b-fe-conventions` off `m1/roster`; FF-merge back to `m1/roster` at close.
> - **ADR numbering:** next at write time **ADR-0064**.
> - **On completion:** mark Step 2.1b complete in `steps.md`; promote the staged M1.2 prompt below to the active prompt; advance `handoff.md` to Session 37 / M1.2.

### Staged — Session 37 prompt (Step 2.2 / M1.2)

*Promoted to the active prompt when Step 2.1b closes. The M1.2 detail under Open questions above is the working reference until then; the prompt below predates the Step 2.1b insertion and will be refreshed at 2.1b close.*

> Resume work. **Step 2.1 / M1.1 ✓ COMPLETE** (Session 35 — auth substrate + frontend shell, ADRs 0061 / 0062 / 0063). Session 36 opens **Step 2.2 / M1.2 Admin substrate + flat roster** — Case 2 sizing then implementation.
>
> **Branch op at session head:**
> ```
> git log m1/roster..m1/01-auth-shell    # confirm M1.1 commits not yet on m1/roster
> git checkout m1/roster
> git merge --ff-only m1/01-auth-shell   # if not already merged
> git checkout -b m1/02-flat-roster
> ```
>
> **Case 2 sizing first.** Step 2.2 has a stub brief in `planning/steps.md` § Step 2.2 — not a scoped prompt. Run the 7-signal fit checklist per `_workflow.md` Case 2. Expect multiple signals to fire: 5 entity tables (Employee, School, Contractor, User-admin-CRUD, Contract); admin-CRUD authoring shape decision (ADR-worthy); admin auth-predicate factory shape (ADR-worthy); first ADR-0047 predicate landing in M1+ code; cross-concern reach (backend entities + commands + routes + frontend pages). **Likely partition needed.** Natural seam: backend entities + commands → backend admin routes → frontend admin pages. Don't pre-decide; surface partition options + tradeoffs in chat per the STOP-AND-CONFIRM gate.
>
> **Five entities to land:**
> - Employee, School, Contractor (flat, audit-log history per ADR-0052)
> - User admin-CRUD beyond M1.1's auth substrate (`edit_user` for password reset + employee link; `delete_user` per delete policy)
> - Contract (hoisted from M2 per Session 34 sizing — admin-roster CRUD per ADR-0047 Cluster 1; `code_flat_fee_schedule` per ADR-0045 is substantive)
> - Add Employee FK + UNIQUE constraint to `user.employee_id` (M1.1 left it as plain UUID; this is an M1.1→M1.2 carry-forward)
>
> **Decision detail to canvass at session head:**
> - Admin-CRUD authoring shape: generalized factory (`make_create_command(Entity, Payload)`) vs hand-authored per entity. ADR-worthy. Factory wins on volume (5 × 3 = 15 commands); hand-authored wins on flexibility for non-uniform predicates.
> - Read routes: hand-authored or generalized? Likely hand-authored.
> - Admin auth-predicate factory: encode ADR-0047 Cluster 1's `role >= admin` class rule as a reusable predicate factory.
> - Frontend admin page shape: list + detail/form per entity. **Shadcn/ui adoption decision was deferred per ADR-0051** — M1.2 forces it. Resurface or proceed with plain Tailwind/CSS.
>
> **ADRs expected:** 1–2 at write time **ADR-0064+**. Likely: admin-CRUD authoring shape; admin auth-predicate factory if non-obvious.
>
> **Read first:** Session 35 Last session summary above + Open questions for Session 36 + `planning/steps.md` § Step 2 high-level + § Step 2.2 stub + ADR-0040 (role catalog) + ADR-0047 (Cluster 1 admin predicates — M1.2's surface) + ADR-0044 (Contract structural shape) + ADR-0045 (Contract `code_flat_fee_schedule`) + ADR-0061 / 0062 (auth substrate + Caller from M1.1) + `data-model.md` § Roster entities (per-entity attribute rosters for the 5 entities). Skim `app/framework/caller.py` + `app/framework/auth.py` (consumed by M1.2 routes), `app/domain/auth.py` (entity pattern M1.2 entities mirror), `app/framework/history.py` (mixin pattern for the 5 entity history tables), `tests/conftest.py` § per-role fixtures (M1.2 command tests build on these).
>
> **Out of scope:**
> - Anything in M1.1's scope (closed Session 35 — auth substrate fully in place).
> - M1.3 entities + role administration commands (UserRole grant/revoke + `audit_reason` Note) — next sub-step.
> - M1.4 range-typed entities + `change_employee_role_rate` — sub-step after M1.3.
> - WABundle (M2's surface — though Contract is hoisted, WABundle is not; see ADR-0044/0048).
> - PaaS vendor pick (stays deferred per ADR-0055); Postgres CI service (stays deferred).
>
> **Process notes:**
> - **STOP-AND-CONFIRM gate applies, including for source code.** Each new domain-shape decision canvasses in chat before any code or ADR write.
> - **Migration discipline per [[project-neon-current-policy]]:** author → `uv run alembic upgrade head` on Neon → commit. Throwaway sqlite OK for shape iteration before commit.
> - **Commit pattern: preserve incremental checkpoints.** Coherent atomic changes at green-state boundaries, proper subjects.
> - **Branch:** `m1/02-flat-roster` off `m1/roster`. FF-merge back to `m1/roster` at M1.2 close.
> - **ADR numbering.** Next at write time **ADR-0064**.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-18)
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 ✓ COMPLETE 2026-05-19 (Session 33)**; **Step 2 partitioned into 4 sub-steps 2026-05-19 (Session 34)**; **Step 2.1 ✓ COMPLETE 2026-05-19 (Session 35)**; M1.2 / M1.3 / M1.4 stubs; Steps 3–9 stubs)
- Archived step list (Phase 1): `planning/steps.archive/conceptualization.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0063; next ADR at write time: **ADR-0064**)
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
