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

**Implementation** — Phase 2. **Step 1 / M0 Foundations ✓ COMPLETE 2026-05-19 (Session 33).** **Step 2 / M1 Roster** partitioned 2026-05-19 (Session 34, Case 2) into 4 sub-steps. **Step 2.1 / M1.1 Auth substrate + frontend shell ✓ COMPLETE 2026-05-19 (Session 35).** **Step 2.1b / Frontend architecture & conventions** (inserted; not a roadmap milestone) partitioned 2026-05-20 (Session 36, Case 2) into **2.1b-A** (adopt + scaffold + document) and **2.1b-B** (port M1.1 auth + test/story colocation). **Step 2.1b-A ✓ COMPLETE 2026-05-20 (Session 36).** Currently on branch **`m1/01b-fe-conventions`** (off `m1/roster`; `m1/01-auth-shell` was FF-merged to `m1/roster` at Session 36 head). 2.1b-A's implementation + close-out commits land on this branch. **Next: Session 37 / Step 2.1b-B** — port the M1.1 auth code into the four-layer model + test/story colocation; same branch; FF-merge `m1/01b-fe-conventions` → `m1/roster` at 2.1b-B close (which closes Step 2.1b). M1.2 follows as Session 38; M1.3 / M1.4 stubs in `steps.md`.

## Last session summary

**Session 36 — Step 2.1b-A / Adopt + scaffold + document (2026-05-20).** Opened with a Case 2 partition of the inserted Step 2.1b, then ran 2.1b-A as a Case 3 implementation.

**Case 2 partition.** Step 2.1b split into **2.1b-A** (adopt + scaffold + document) and **2.1b-B** (port M1.1 auth + test/story colocation) — single branch `m1/01b-fe-conventions`, per the 1.3a/1.3b precedent. Fit-checklist signals 2 / 3 / 5 fired. The original scoped brief lived in `.claude/plans/` (harness-local, uncommitted) and did not survive a machine switch; the intact `sca-ih-tracker` reference repo + reconstructed `steps.md` sub-sub-step briefs became the working brief, and all dead `.claude/plans/` references were stripped from the planning files. See [[feedback-scoped-briefs-in-repo]].

**Branch op.** Committed the user's `SubmitEvent` fix on `m1/01-auth-shell` (`4a3b4a9`); FF-merged `m1/01-auth-shell` → `m1/roster`; branched `m1/01b-fe-conventions`.

**What landed (2.1b-A).**

- Generated OpenAPI client relocated `src/api/` → `src/api/generated/`; hand-written config → `src/api/configure.ts` (sibling of `generated/`, survives regeneration); `openapi-ts.config.ts` `output.path` updated; 4 M1.1 import sites fixed. CI drift check unaffected (`frontend/src/api/` is the parent path).
- `@/` import alias wired (Vite `resolve.alias` + tsconfig `paths`).
- UI/form stack installed: Tailwind 4, shadcn/ui `radix-lyra` (Button / Input / Card / Field family / Sonner — ported verbatim from sca-ih-tracker, plus transitive Label / Separator), Zod, react-hook-form, Phosphor, sonner. `components.json` + radix-lyra theme tokens in `src/index.css`.
- Four-layer folder skeleton (`pages/ features/ fields/ auth/`) + ESLint `no-restricted-imports` layering rules for `features/` + `pages/`.
- `src/PATTERNS.md` (conventions, adapted + scank-scoped) + thin `frontend/CLAUDE.md`.

**Implementation decisions.** The `routes/` ESLint layering rule is deferred to 2.1b-B — the un-ported M1.1 auth routes still import `@/api/generated/` directly, so enforcing it now would fail lint. `src/components/ui/**` is ESLint-ignored (vendored shadcn). `src/index.css` dropped sca-ih-tracker's brand fonts + typography plugin as not load-bearing.

**ADRs landed (2).** ADR-0064 (four-layer FE architecture + API barrel + ESLint enforcement) + ADR-0065 (shadcn `radix-lyra` + Tailwind 4 + Zod + RHF stack). ADR-0063's config-file-placement consequence amended with a forward pointer to ADR-0064.

**Verification.** `pnpm lint` / `typecheck` / `test` (1/1) / `build` all green. M1.1 auth functionally unchanged (import-path edits only); browser round-trip not re-verified — no behavioral change.

**Commits (on `m1/01b-fe-conventions`).** `4a3b4a9` (M1.1 `SubmitEvent` fix, rode the FF-merge); 2.1b-A implementation; 2.1b-A close-out (ADR-0064/0065 + steps.md/handoff advance).

**Memories saved (1 new).** `feedback-scoped-briefs-in-repo` — a scoped brief the handoff depends on must live in committed `planning/`, never `.claude/plans/` (harness-local; does not survive a machine switch).

`_file-rules.md` **not regenerated** — no `## File contract` block changed.

---

## Open questions

**For Session 37 — Step 2.1b-B / Port M1.1 auth + test/story colocation** (Case 3 scoped — `steps.md` § Step 2.1b-B is the brief).

- **Branch:** stay on `m1/01b-fe-conventions` — no branch op at session head (2.1b-A is already committed there). FF-merge `m1/01b-fe-conventions` → `m1/roster` at 2.1b-B close, which closes Step 2.1b entirely.
- **Scope.** A structural port — move the M1.1 auth code into the four-layer model with no behavior change: route files stay in `routes/` (config only), page compositions move to `pages/`, the login feature (`LoginForm` + a login/logout API barrel) to `features/auth/`, cross-cutting auth (`useCurrentUser` / `currentUserQueryOptions`, consumed by the route guard) to `src/auth/`. Rebuild `LoginForm` on shadcn (`Field` family) + react-hook-form + Zod. Add the `routes/` ESLint layering rule (deferred from 2.1b-A — see the NOTE in `eslint.config.js`). Test/story colocation: `src/tests/` → `src/test/` (infra only — setup, `renderWithProviders`, `createTestQueryClient`) + first colocated `*.test.tsx` + `*.stories.tsx`.
- **Preserve ADR-0063 exactly.** `setQueryData` (not `invalidateQueries`) on login success; cookie-session model — no Zustand store, no 401 interceptor (both explicitly rejected in ADR-0063); `beforeLoad` + `ensureQueryData` route guard. The browser round-trip (`/` → `/login` → login → admin shell → sign out) is the acceptance check.
- **Decisions to canvass at session head:** the `src/auth/` vs `features/auth/` boundary (which auth files are cross-cutting vs feature-scoped); whether logout is an API-barrel mutation or a cross-cutting helper.
- **ADR numbering.** Next free is **ADR-0066**; 2.1b-B may land 0 ADRs (structural port) or 1 if a non-obvious wrinkle surfaces. Amend `PATTERNS.md` if the port surfaces a convention wrinkle.
- **Read first:** `steps.md` § Step 2.1b-B + § Step 2.1b; `frontend/src/PATTERNS.md` (conventions to apply); ADR-0063 (route-guard pattern — preserve) + ADR-0064 (four-layer architecture); current `frontend/src/` auth files (`routes/login.tsx`, `routes/_authenticated.tsx`, `routes/_authenticated/index.tsx`, `hooks/useCurrentUser.ts`, `api/configure.ts`); the `sca-ih-tracker` reference repo at `C:\Users\msilberstein\Documents\sca-ih-tracker` — `src/features/auth/`, `src/auth/`, `src/pages/login/`, `src/test/`.

**For Session 38 — Step 2.2 / M1.2 Admin substrate + flat roster** (forward reference; Case 2 sizing then likely partitioned implementation).

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

**Session 37 — Step 2.1b-B / Port M1.1 auth + test/story colocation.** Port the M1.1 auth code into the four-layer model 2.1b-A established, and adopt test/story colocation. Case 3 scoped — `planning/steps.md` § Step 2.1b-B is the brief. No branch op at session head: stay on `m1/01b-fe-conventions`; FF-merge to `m1/roster` at close (closes Step 2.1b). Next ADR free is **ADR-0066** (likely none — structural port). **M1.2 follows as Session 38.**

### Prompt for the next session

> Resume work. **Step 2.1b-A ✓ COMPLETE** (Session 36 — four-layer FE architecture + UI/form stack + API-client relocation; ADR-0064 / ADR-0065). Session 37 runs **Step 2.1b-B / Port M1.1 auth + test/story colocation** — a Case 3 scoped session that closes Step 2.1b.
>
> **Scoped brief — read first:** `planning/steps.md` § Step 2.1b-B (and § Step 2.1b for parent context). `frontend/src/PATTERNS.md` is the conventions doc the port must conform to.
>
> **No branch op at session head** — stay on `m1/01b-fe-conventions` (2.1b-A is already committed there). FF-merge `m1/01b-fe-conventions` → `m1/roster` at 2.1b-B close.
>
> **Scope — a structural port, no behavior change:**
> - Route files stay in `src/routes/` as config only; page compositions move to `src/pages/`; the login feature (`LoginForm` + a login/logout API barrel) to `src/features/auth/`; cross-cutting auth (`useCurrentUser` / `currentUserQueryOptions`, consumed by the route guard) to `src/auth/`.
> - Rebuild `LoginForm` on shadcn (`Field` family) + react-hook-form + Zod (`standardSchemaResolver`).
> - Add the `routes/` ESLint `no-restricted-imports` layering rule — deferred from 2.1b-A; see the NOTE in `eslint.config.js`.
> - Test/story colocation: rename `src/tests/` → `src/test/` (infra only — setup, `renderWithProviders`, `createTestQueryClient`); add the first colocated `*.test.tsx` + `*.stories.tsx`.
>
> **Preserve ADR-0063 exactly.** `setQueryData` (not `invalidateQueries`) on login success; cookie-session model — no Zustand store, no 401 interceptor (both explicitly rejected in ADR-0063); `beforeLoad` + `ensureQueryData` route guard. The browser round-trip (`/` → `/login` → login → admin shell → sign out) is the acceptance check.
>
> **Decisions to canvass at session head** (STOP-AND-CONFIRM gate): the `src/auth/` vs `features/auth/` boundary — which auth files are cross-cutting (route-guard-consumed) vs feature-scoped; whether logout is an API-barrel mutation or a cross-cutting helper.
>
> **Read first:** `steps.md` § Step 2.1b-B + § Step 2.1b; `frontend/src/PATTERNS.md`; ADR-0063 (route guard — preserve) + ADR-0064 (four-layer architecture); current `frontend/src/` auth files (`routes/login.tsx`, `routes/_authenticated.tsx`, `routes/_authenticated/index.tsx`, `hooks/useCurrentUser.ts`, `api/configure.ts`); the `sca-ih-tracker` reference at `C:\Users\msilberstein\Documents\sca-ih-tracker` — `src/features/auth/`, `src/auth/`, `src/pages/login/`, `src/test/{setup,renderWithProviders,queryClient}`.
>
> **Out of scope:**
> - Anything in 2.1b-A's scope (closed Session 36).
> - Any M1.2 roster entity / command / route / admin page (Session 38).
> - Entity-abstraction patterns (`EntityListPage`, `useEntityForm`, `DataTable`, comboboxes) — extracted just-in-time later.
> - Backend changes; OpenAPI-surface changes.
>
> **Process notes:**
> - **STOP-AND-CONFIRM gate applies, including for source code.** Canvass the two decisions above in chat before writing.
> - **Commit pattern: preserve incremental checkpoints.** `pnpm lint` / `typecheck` / `test` / `build` green at close; browser round-trip verified.
> - **Branch:** `m1/01b-fe-conventions`; FF-merge to `m1/roster` at close — closes Step 2.1b entirely.
> - **ADR numbering:** next free is **ADR-0066**.
> - **On completion:** mark Step 2.1b-B and Step 2.1b complete in `steps.md`; advance `handoff.md` to Session 38 / M1.2 (refresh the staged M1.2 prompt).

### Staged — Session 38 prompt (Step 2.2 / M1.2)

*Promoted to the active prompt when Step 2.1b-B closes (Session 37). The M1.2 detail under Open questions above is the working reference until then; the prompt below predates the Step 2.1b insertion and is refreshed when 2.1b-B closes.*

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
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 ✓ COMPLETE 2026-05-19 (Session 33)**; **Step 2 partitioned into 4 sub-steps 2026-05-19 (Session 34)**; **Step 2.1 ✓ COMPLETE 2026-05-19 (Session 35)**; **Step 2.1b partitioned into 2.1b-A / 2.1b-B 2026-05-20 (Session 36)**, **2.1b-A ✓ COMPLETE**; M1.2 / M1.3 / M1.4 stubs; Steps 3–9 stubs)
- Archived step list (Phase 1): `planning/steps.archive/conceptualization.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0065; next ADR at write time: **ADR-0066**)
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
