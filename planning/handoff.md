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

**Implementation** — Phase 2. **Step 1 / M0 Foundations ✓ COMPLETE 2026-05-19 (Session 33).** **Step 2 / M1 Roster** partitioned 2026-05-19 (Session 34, Case 2) into 4 sub-steps. **Step 2.1 / M1.1 Auth substrate + frontend shell ✓ COMPLETE 2026-05-19 (Session 35).** **Step 2.1b / Frontend architecture & conventions** (inserted; not a roadmap milestone) ✓ **COMPLETE 2026-05-20** — 2.1b-A (Session 36; ADR-0064 / 0065) + 2.1b-B (Session 37; ADR-0066), both on branch **`m1/01b-fe-conventions`**. **Next: Session 38 / Step 2.2 / M1.2 Admin substrate + flat roster** — Case 2 sizing then implementation. **Branch ops at 2.1b close → Session 38 head:** FF-merge `m1/01b-fe-conventions` → `m1/roster` (closes Step 2.1b); then `git checkout -b m1/02-flat-roster` off `m1/roster`. M1.3 / M1.4 stubs in `steps.md`.

## Last session summary

**Session 37 — Step 2.1b-B / Port M1.1 auth + test/story colocation (2026-05-20).** Case 3 scoped session; closes Step 2.1b.

**Three-point conventions deliberation (pre-implementation).** Before coding, three code-organization questions were resolved with the user and landed in **ADR-0066**: (1) the per-feature API barrel is `api/index.ts` (imported `@/features/<domain>/api`), not `api/<domain>.ts` — kills the `auth/api/auth` redundancy; (2) **auth is one folder** — `src/auth/` is a single cross-cutting auth/session module, **no `features/auth/`** (the reference repo's two-folder split was driven by its Zustand store, which ADR-0063 deleted for scank); (3) feature subfolders are a closed vocabulary (`components/` / `hooks/` / `api/`), created when populated, **no `services/`** (no service layer in a TanStack-Query + openapi-ts stack).

**What landed (the port).** `src/auth/` module — `api/{index,currentUser}.ts`, `hooks/{useCurrentUser,useLogin,useLogout}.ts`, `components/LoginForm.tsx` + colocated `.test.tsx` (4 tests) + `.stories.tsx`. `LoginForm` rebuilt on shadcn `Field` family + RHF + `standardSchemaResolver` + Zod (pure: props in, callback out). Pages `pages/login/` + `pages/admin-shell/`. Routes slimmed to config; `__root.tsx` mounts `<Toaster />`. Test infra `src/tests/` → `src/test/` (`setup.ts` + `renderWithProviders.tsx` + `queryClient.ts`). `routes/**` ESLint layering rule added (deferred from 2.1b-A); react-refresh exemption for tests/stories. `src/hooks/useCurrentUser.ts` removed; `src/hooks/` kept (`.gitkeep`).

**ADR-0063 preserved exactly.** `setQueryData` (not `invalidateQueries`) on login; cookie-session — no Zustand, no 401 interceptor; `beforeLoad` + `ensureQueryData` guard. Navigation kept in pages (the `src/auth/` hooks are routing-agnostic). Server-error UX is now a `toast` — a minor refinement over M1.1's inline `<p>` (the `Field` family handles Zod validation only).

**ADRs landed (1).** ADR-0066 (auth-as-module + `api/index.ts` barrel + feature subfolder vocabulary). ADR-0064 annotated — its `api/<domain>.ts` and its `features/auth/` carry-forward superseded.

**Verification.** `pnpm lint` / `typecheck` / `test` (4/4) / `build` all green. `routeTree.gen.ts` unchanged (route topology identical). Browser round-trip (`/` → `/login` → login → admin shell → sign out) is the standing acceptance check — needs the backend + Neon, same as M1.1.

**Commits (on `m1/01b-fe-conventions`).** 2.1b-B implementation checkpoints + close-out (ADR-0066 + planning advance). FF-merge `m1/01b-fe-conventions` → `m1/roster` closes Step 2.1b.

**Memories saved (1 new).** `reference-phosphor-icons` — verify/discover Phosphor icon names via one `Glob` on `dist/csr/`, never read the ~1500-icon index.

`_file-rules.md` **not regenerated** — no `## File contract` block changed.

---

## Open questions

**Queued — frontend follow-ups (post-2.1b; not yet scheduled).** Raised by the user at Session 37 wrap-up; fold into M1.2 sizing.

- **Item 1 — theme toggle (small, its own step).** A light / dark / auto toggle in the admin shell header; button at `src/components/ThemeToggleBtn`. Substrate already exists — `src/index.css` has `:root` + `.dark` token blocks and `next-themes` is installed. Work: mount `<ThemeProvider>` from `next-themes` (not currently mounted — the Sonner `Toaster` just degrades to "system"), build `ThemeToggleBtn`, wire it into `pages/admin-shell`. `next-themes`' `enableSystem` gives "auto" free. ~30 min. Keep it **out of** any "no behavior change" step — a small dedicated step (natural M1.2 opener or standalone).
- **Item 2 — themeable architecture (POST-MVP).** A theme registry + user-facing theme dropdown; each theme defines light + dark; a user picks either one theme (both modes) or distinct light/dark themes. Design the schema for the general case: a theme = one named token-value set for a single mode; a user preference = `(lightThemeId, darkThemeId, mode)`. Per-user persistence to a `User` preference is a **backend change** → firmly post-MVP, ADR-worthy when it lands (superseding ADR per `steps.md`'s contract). Not MVP — default theme suffices; not in `mvp.md`'s 6 must-haves. **Prep already done:** `PATTERNS.md` § UI components now mandates styling via semantic theme tokens only, which keeps this a drop-in; nothing else to build now.

**For Session 38 — Step 2.2 / M1.2 Admin substrate + flat roster** (next; Case 2 sizing then likely partitioned implementation).

- **Branch op at session head:** `git checkout -b m1/02-flat-roster` off `m1/roster` (after 2.1b-B's FF-merge has landed `m1/01b-fe-conventions` on `m1/roster`).
- **Case 2 sizing required at session head.** Step 2.2 has a stub brief in `steps.md` — not a scoped prompt. Expect sizing to surface several fit-checklist signals: independently-deliberable decisions (admin-CRUD authoring shape — generalized factory vs hand-authored per entity, ADR-worthy; admin auth-predicate factory shape, ADR-worthy); five new entity tables (Employee, School, Contractor, User-side admin CRUD, Contract); cross-concern reach (backend entity authoring + first ADR-0047 predicate landing + frontend per-entity admin pages); likely >60 min duration. **Likely partition needed** — natural seam is backend entities + commands → backend admin routes → frontend admin pages. Hold the partition canvass at session head per Case 2 protocol; don't pre-decide.
- **ADR numbering.** M1.2 starts at the next free number at its write time. M1.2 likely lands 1–2 ADRs: admin-CRUD authoring shape (generalized factory vs hand-authored), admin auth-predicate factory shape if non-obvious. First ADR-0047 predicate landing in M1+ code; the `role >= admin` Cluster 1 class rule is the first concrete use of `has_role_at_least` from ADR-0062.
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
- **Step 2.1b-A ✓ COMPLETE 2026-05-20** (Session 36). Frontend four-layer architecture + UI/form stack (shadcn `radix-lyra`, Tailwind 4, Zod, RHF) + API-client relocation in place; `frontend/src/PATTERNS.md` is the conventions doc M1.2 frontend work consumes. Step 2.1b-B (auth port) remains.
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

**Session 38 — Step 2.2 / M1.2 Admin substrate + flat roster.** Build the 5 flat roster entities (Employee / School / Contractor / User-admin-CRUD / Contract) + admin CRUD commands + read routes + per-entity admin pages. **Case 2 sizing first** — Step 2.2 carries a stub brief in `planning/steps.md`; expect a partition. **Branch ops at session head:** FF-merge `m1/01b-fe-conventions` → `m1/roster` (if not already done — closes Step 2.1b), then `git checkout -b m1/02-flat-roster` off `m1/roster`. Next ADR free is **ADR-0067**.

### Prompt for the next session

> Resume work. **Step 2.1b ✓ COMPLETE** (Sessions 36–37 — frontend four-layer architecture, UI/form stack, and the M1.1 auth port; ADR-0064 / 0065 / 0066). Session 38 opens **Step 2.2 / M1.2 Admin substrate + flat roster** — Case 2 sizing, then implementation.
>
> **Branch ops at session head:**
> ```
> git checkout m1/roster
> git merge --ff-only m1/01b-fe-conventions   # closes Step 2.1b, if not already merged
> git checkout -b m1/02-flat-roster
> ```
>
> **Case 2 sizing first.** Step 2.2 has a stub brief in `planning/steps.md` § Step 2.2 — not a scoped prompt. Run the 7-signal fit checklist per `_workflow.md` Case 2. Expect multiple signals: 5 entity tables (Employee, School, Contractor, User-admin-CRUD, Contract); admin-CRUD authoring shape (ADR-worthy); admin auth-predicate factory shape (ADR-worthy); first ADR-0047 predicate landing in M1+ code; cross-concern reach (backend entities + commands + routes + frontend pages). **Likely partition** — natural seam: backend entities + commands → backend admin routes → frontend admin pages. Surface partition options in chat per the STOP-AND-CONFIRM gate; don't pre-decide.
>
> **The detailed M1.2 working reference is the "For Session 38" block under Open questions above** — the five entities, the admin-CRUD / read-route / auth-predicate-factory decisions to canvass, coordination points, and carry-forwards (`User.employee_id` FK + UNIQUE; first `role >= admin` predicate factory). Read it first.
>
> **Frontend is now equipped.** `frontend/src/PATTERNS.md` is the conventions doc M1.2 frontend work consumes — four-layer architecture, per-feature `api/index.ts` barrel, shadcn/ui + RHF + Zod forms. The shadcn-adoption question is settled (ADR-0065) — no longer an open M1.2 decision. M1.2's Employee feature is the first canonical `src/features/<domain>/` exemplar (auth is not a feature — see ADR-0066).
>
> **Read first:** Session 37 Last session summary + the "For Session 38" Open questions block above; `planning/steps.md` § Step 2 + § Step 2.2; ADR-0040 (role catalog), ADR-0047 (Cluster 1 admin predicates), ADR-0044 / ADR-0045 (Contract shape + `code_flat_fee_schedule`), ADR-0061 / 0062 (auth substrate + Caller); `planning/data-model.md` § Roster entities. Skim `app/framework/caller.py` + `app/framework/auth.py`, `app/domain/auth.py` (entity pattern), `app/framework/history.py`, `tests/conftest.py` § per-role fixtures.
>
> **Out of scope:** M1.3 (role administration), M1.4 (range-typed entities); WABundle; PaaS vendor pick + Postgres CI (both stay deferred). The two queued frontend follow-ups (theme toggle, themeable architecture) under Open questions — item 1 is a small separate step, item 2 is post-MVP.
>
> **Process notes:** STOP-AND-CONFIRM gate applies, including source code. Migration discipline per [[project-neon-current-policy]] (author → `uv run alembic upgrade head` on Neon → commit). Preserve incremental commits. Branch `m1/02-flat-roster` off `m1/roster`, FF-merge back at M1.2 close. Next ADR free: **ADR-0067**.

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-18)
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 ✓ COMPLETE 2026-05-19 (Session 33)**; **Step 2 partitioned into 4 sub-steps 2026-05-19 (Session 34)**; **Step 2.1 ✓ COMPLETE 2026-05-19 (Session 35)**; **Step 2.1b ✓ COMPLETE 2026-05-20 (Sessions 36–37)**; M1.2 / M1.3 / M1.4 stubs; Steps 3–9 stubs)
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
