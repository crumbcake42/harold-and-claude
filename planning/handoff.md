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

**Implementation** — Phase 2. **Step 1 / M0 Foundations ✓ COMPLETE 2026-05-19 (Session 33).** **Step 2 / M1 Roster partitioned 2026-05-19 (Session 34, Case 2)** into 4 sub-steps with **Contract hoisted from M2 to M1.2** (ADR-0045 makes EmployeeRole's `contract_id` mandatory) and **auth substrate pulled into M1.1** (`architecture.md` line 108 out-of-band concern never milestoned in `roadmap.md`; lesson saved as [[check-out-of-band-concerns]]). Currently on the **`m1/roster`** branch (tip = 3684fad, pre-M1.1 cleanup commit consolidating `backend/scripts/` → `backend/app/cli/`). Sub-step status: M1.1 next (auth substrate + frontend shell); M1.2 / M1.3 / M1.4 stubs in `steps.md`. **Next branch op at Session 35 head:** `git checkout -b m1/01-auth-shell` off `m1/roster`.

## Last session summary

**Session 34 — Step 1 / M0 close-out + Step 2 / M1 Case-2 sizing (2026-05-19).** Three landings: M0 closed with prescribed branch ops + one deviation; pre-M1.1 cleanup commit on `m1/roster`; M1 partitioned into 4 sub-steps with 8 locked decisions for M1.1.

**M0 close-out (branch ops at session head).** Executed the 5-op sequence prescribed in the Session 33 handoff with one deviation:

1. FF-merge `m0/04-adapter-boundary` → `m0/foundations` (clean; Step 1.4 landed into milestone branch).
2. Create local `dev` tracking `origin/dev`.
3. **Deviation: `.gitignore` seed commit on `dev`** (a47a0a8) before the merge. `origin/dev` was at the conceptualization-phase tip with no `.gitignore` files; merging `m0/foundations` would have left `backend/` / `frontend/` / `.vscode/` (containing `node_modules` / `__pycache__` / build artifacts) showing as untracked. Cherry-picked the 3 `.gitignore` files (root + backend + frontend) from `m0/foundations`, committed on `dev` first. Merge then clean.
4. `--no-ff` merge `m0/foundations` → `dev` (2332f75 — milestone TOC commit per [[preserve-incremental-commits]]).
5. `git tag m0-complete` (rewind anchor per [[project-branching-convention]]).
6. `git checkout -b m1/roster` off updated `dev`.

**Pre-M1.1 cleanup commit on `m1/roster` (3684fad).** Consolidated `backend/scripts/` → `backend/app/cli/`. User-driven: pointed out the old `scripts/export_openapi.py` carried a `sys.path.insert(BACKEND_ROOT)` hack only because it lived outside the `app` package. New `app/cli/export_openapi.py` imports natively; takes `--out` as a CLI arg (no more `REPO_ROOT = BACKEND_ROOT.parent` parenting chain); writes via `write_bytes` to bypass Windows CRLF translation. `justfile gen-openapi-schema` target updated to `python -m app.cli.export_openapi --out ../contracts/openapi.json`. `app/cli/` becomes home for app-internal commands; `bootstrap_admin.py` lands here in M1.1. Promote to Click/Typer at the 3rd command.

**M1 Case-2 sizing.** All 7 fit-checklist signals fired. Two scope additions resolved at sizing:

- **Contract hoisted from M2 to M1.2.** ADR-0045's mandatory `EmployeeRole.contract_id` left EmployeeRole without an upstream entity under the original M2 placement. Contract is admin-roster CRUD in character per ADR-0047 Cluster 1; M1's character.
- **Auth substrate pulled into M1.1.** `architecture.md` line 108 flagged authentication as out-of-band *"pinned at implementation kickoff"* — never milestoned. M1's "admin dashboard skeleton" forces the question. Lesson saved: [[check-out-of-band-concerns]] (cross-check architecture.md out-of-band concerns at every Case 2 sizing — three of four had been routed, auth slipped).

**Partition (4 sub-steps).** Brief in `planning/steps.md` § Step 2; M1.1 fully detailed, 1.2–1.4 stubbed:

| Sub-step | Title | Size | Branch | ADRs expected |
|---|---|---|---|---|
| 1.1 | Auth substrate + frontend shell | M+ (possibly L) | `m1/01-auth-shell` | 2–3 |
| 1.2 | Admin substrate + flat roster (incl. Contract) | M | `m1/02-flat-roster` | 1–2 |
| 1.3 | Role administration + `audit_reason` Note | S–M | `m1/03-role-admin` | 1 |
| 1.4 | Range-typed entities + `change_employee_role_rate` | M (possibly L) | `m1/04-range-typed` | 0–1 |

**8 locked decisions for M1.1** (chat-side canvass per STOP-AND-CONFIRM; no ADRs yet — authored up during M1.1 implementation):

1. **Session mechanism:** DB-backed server-side sessions; opaque random token in `httpOnly Secure SameSite=Lax` cookie; 12h sliding TTL.
2. **Password hashing:** argon2id via `argon2-cffi`.
3. **Bootstrap:** `app/cli/bootstrap_admin.py` CLI + pytest fixture.
4. **CORS:** `CORSMiddleware(allow_origins=[settings.FRONTEND_ORIGIN])`.
5. **CSRF tokens deferred** (`SameSite=Lax` cookies cover MVP threat surface).
6. **Caller concrete shape:** Pydantic `Caller(id: UUID, username: str, roles: frozenset[Role])`. Closes ADR-0059's *"Caller concrete shape"* carry-forward.
7. **Frontend route guard:** TanStack Router `_authenticated` route layout group with `beforeLoad`; API client interceptor redirects on 401.
8. **Login as non-Command surface:** dispatcher requires a Caller; login produces one. FastAPI route directly. Documented as the exception.

**Out of scope for M1.1** (MVP-deferred): password reset; login rate limiting / lockout; remember-me beyond 12h sliding TTL; 2FA / OAuth / SSO; immediate session invalidation on `revoke_user_role` (per `mvp.md` line 73 — next-request authorization check is MVP behavior); CSRF tokens.

**Commits landed this session (4).**

1. `a47a0a8` on `dev` — `.gitignore` seed before M0 merge.
2. `2332f75` on `dev` — `--no-ff` merge of `m0/foundations` (M0 milestone TOC commit).
3. `3684fad` on `m1/roster` — pre-M1.1 cleanup (`scripts/` → `app/cli/`).
4. (this commit) on `m1/roster` — Session 34 close-out: `planning/steps.md` (Step 2 expanded into 4 sub-steps) + `planning/handoff.md` (this rewrite).

**ADRs landed this session (0).** All M1.1 decisions deferred to ADR-write at implementation (ADR-0061+).

**Memories saved (1 new).** `feedback_check_out_of_band_concerns` — cross-check architecture.md's out-of-band concerns against milestone scope at every Case 2 sizing.

**Files touched.** `backend/.gitignore` + `frontend/.gitignore` + `.gitignore` (new on `dev` via seed commit). `backend/app/cli/__init__.py` (new), `backend/app/cli/export_openapi.py` (new), `backend/scripts/export_openapi.py` (deleted), `justfile` (gen-openapi-schema target updated) — all on `m1/roster` cleanup commit. `planning/steps.md` (Step 2 expanded). `planning/handoff.md` (this rewrite). `_file-rules.md` **not regenerated** — no `## File contract` block changed.

**Verification at session close.** `just gen-openapi-schema` runs cleanly via new module path; `contracts/openapi.json` byte-identical to pre-cleanup (CRLF fix via `write_bytes` confirmed). No backend test changes; Session 33's 27-test suite remains green.

---

## Open questions

**For the next session (Session 35 — Step 2.1 / M1.1 Auth substrate + frontend shell, Case 3 implementation):**

- **Branch op at session head:** `git checkout -b m1/01-auth-shell` off `m1/roster` (tip = 3684fad).
- **ADR numbering.** Next at write time **ADR-0061**. M1.1 likely lands 2–3 ADRs: auth substrate (bundle of D1+D2+D3+D4+D5+D8 — sessions + hashing + bootstrap + CORS + non-Command login); Caller concrete shape (D6, closes ADR-0059); optionally frontend route-guard pattern (D7) if non-obvious tradeoffs surface.
- **Decision detail still to canvass at session head** (the 8 locked decisions pinned the *what*; the *how* of some sub-pieces has substance):
  - Session token shape: `secrets.token_urlsafe(32)` is the obvious pick — flag if anything else is in play.
  - Argon2 parameters: stick with `argon2-cffi` library defaults or pin explicit `time_cost` / `memory_cost` / `parallelism`? Library defaults change between releases — explicit pinning is the safer choice for reproducible hash compatibility across machines.
  - `Caller` module location: `app.framework.caller` (new) vs. inline in `app.framework.command` (lives next to `Command`). Lean to new module for legibility; mild fork.
  - `app.framework.auth` internal partitioning: one module or split (hashing / session / dependency)? Likely one until size argues otherwise.
  - Frontend: TanStack Router file-based `_authenticated` group convention — confirm by trying it; rollback to programmatic routing if conventions clash.
  - Pytest fixture shape for "logged in as <role>": fixture composes `(User row + Session row + Caller dependency override on FastAPI app)`. Confirm dependency-override is cleanest vs. constructing the Caller separately.
- **Read first at session head:** Session 34 summary above + Open questions block + `planning/steps.md` § Step 2 high-level + § Step 2.1 (full M1.1 brief with 8 locked decisions) + ADR-0040 (role catalog) + ADR-0047 (per-command authorization predicates) + ADR-0059 (Command base class + Caller carry-forward). Skim `app/framework/command.py` (Caller Protocol shape — switching to concrete Caller is a M1.1 output), `app/framework/dispatcher.py` (Caller consumption call sites), `app/cli/export_openapi.py` (CLI module pattern that `bootstrap_admin.py` mirrors). Frontend skim: `frontend/src/routes/` (current TanStack Router setup), `frontend/src/api/` (openapi-ts client — the 401 interceptor wraps this).
- **Coordination point:** the dispatcher's auth step currently consumes Caller via Protocol; M1.1 switches it to the concrete Caller. May surface Caller-attribute additions (e.g., `roles` access pattern). One backend-↔-dispatcher integration moment during M1.1.

**For Phase 2 broadly (M1+ outlook):**

- **Step 1 / M0 ✓ COMPLETE 2026-05-19** (Session 33). Substrate for every M1+ command in place: Command base + dispatcher with retry loop, history infrastructure with real capture sink, advisory-lock + SERIALIZABLE primitives behind a documented adapter, Alembic + CI green on SQLite.
- **PaaS vendor pick stays deferred per ADR-0055.** Do not re-propose vendor canvass at any M1+ step head. See [[project-vendor-pick-deferred]] for the 5 portability discipline notes.
- **Postgres CI service stays deferred** (Session 33 decision). Revisit if Docker access becomes reliable on the dev machine.
- **MVP-attempt-1 rewind protocol** (per [[project-branching-convention]]): with `m0-complete` tag landed, rewind cost to restart M1 from M0 is one tag move.

**Carried into Phase 2 broadly:**

- **Auth substrate establishes the user-identity surface for all M1+ work.** M1.2+ admin pages assume a logged-in admin via the M1.1 dependency. The pytest "logged in as <role>" fixture is the test-side anchor for every M1+ command unit test.
- **Adapter boundary established (M0.4).** Postgres-specific features live behind `app.framework.adapter`. M1+ entity tables consume `json_column()`; advisory-lock invariants land key-builders in `app.framework.locks` and call the adapter.
- **PaaS / vendor portability discipline** (ADR-0055 + [[project-vendor-pick-deferred]]). Postgres 15+ floor; no vendor-specific extensions; vanilla `psycopg`; CI on docker-compose Postgres when adopted.
- **Carry-forward landings.** Per `roadmap.md` § Carry-forward landing index. M1's carry-forward: ContractorEngagement signatures + date defaults (lands in M1.4).

**Process notes (apply to Phase 2 generally):**

- **STOP-AND-CONFIRM gate stays in force, including for source code.** Each sub-step opens with chat-side deliberation before any code or ADR write.
- **Commit pattern: preserve incremental checkpoints; FF sub-step branches to `m1/roster`; merge `m1/roster` → `dev` with `--no-ff` + tag `m1-complete` at M1 close** (per [[preserve-incremental-commits]] + [[project-branching-convention]]).
- **Contract-drift CI job enforces schema + client are in sync.** Any backend OpenAPI-surface change requires `just gen-openapi` + commit of `contracts/openapi.json` + `frontend/src/api/` (see [[committed-generated-artifacts]]).
- **Cross-check architecture.md out-of-band concerns at every Case 2 sizing** per [[check-out-of-band-concerns]] — applied at M1 (caught auth slip); apply at M2+.
- **`mvp.md` is the canonical MVP scope reference.**

## Next session

**Session 35 — Step 2.1 / M1.1 Auth substrate + frontend shell (Case 3 implementation).** Branch op at session head: `git checkout -b m1/01-auth-shell` off `m1/roster` (tip = 3684fad). Then Case 3 implementation per the M1.1 brief in `planning/steps.md` § Step 2.1 — 8 locked decisions pinned; *how* canvass at session head before writing. Likely 2–3 ADRs landing (ADR-0061+).

### Prompt for the next session

> Resume work. **Step 1 / M0 Foundations ✓ COMPLETE** (Session 33). **Step 2 / M1 Roster partitioned into 4 sub-steps** (Session 34, Case 2). Session 35 implements **M1.1 Auth substrate + frontend shell** — Case 3 scoped.
>
> **Branch op at session head:**
> ```
> git checkout m1/roster
> git checkout -b m1/01-auth-shell
> ```
> Pre-M1.1 cleanup commit (3684fad — `scripts/` → `app/cli/` consolidation) is at `m1/roster`'s tip; M1.1 builds on top.
>
> **The 8 locked decisions for M1.1 are pinned in `planning/steps.md` § Step 2.1 ("Locked decisions" block).** Don't re-canvass them — they were settled at the Session 34 chat-side canvass per the STOP-AND-CONFIRM gate. **Do canvass the open detail items** (session token shape, argon2 parameter pinning, Caller module location, `app.framework.auth` internal partitioning, TanStack Router `_authenticated` group convention, pytest fixture shape) at session head before writing — these are the *how* of the locked *what*.
>
> **ADRs expected:** 2–3 at write time **ADR-0061+**. Likely shape: ADR-0061 auth substrate (sessions + hashing + bootstrap + CORS + non-Command login surface); ADR-0062 Caller concrete shape (resolves ADR-0059 carry-forward); optionally ADR-0063 frontend route-guard pattern. Final ADR partition decided during implementation; `steps.md` § Step 2.1 "Locked decisions" block is the source-of-truth for *what* each ADR pins.
>
> **Read first:** Session 34 Last session summary above + Open questions for Session 35 + `planning/steps.md` § Step 2 high-level + § Step 2.1 (full M1.1 brief) + ADR-0040 (role catalog) + ADR-0047 (per-command authorization predicates) + ADR-0059 (Command base class + Caller carry-forward). Skim `app/framework/command.py` (Caller Protocol shape — switching to concrete Caller is a M1.1 output), `app/framework/dispatcher.py` (Caller consumption call sites), `app/cli/export_openapi.py` (CLI module pattern that `bootstrap_admin.py` mirrors). Frontend skim: `frontend/src/routes/` (current TanStack Router setup), `frontend/src/api/` (openapi-ts generated client — the 401 interceptor wraps this).
>
> **Out of scope:**
> - Anything in M0's scope (closed Session 33).
> - M1.2 entities + admin CRUD shape (next sub-step after M1.1; flat roster + Contract).
> - Password reset, rate limiting, remember-me, 2FA / OAuth / SSO — all deferred per `mvp.md` and Session 34 canvass.
> - PaaS vendor pick (stays deferred per ADR-0055); Postgres CI service (stays deferred).
>
> **Process notes:**
> - **STOP-AND-CONFIRM gate applies, including for source code.** M1.1's *how* canvass at session head before writing.
> - **Commit pattern: preserve incremental checkpoints.** Each checkpoint = coherent atomic change at a green-state boundary, proper subject (no "wip:").
> - **Branch:** `m1/01-auth-shell` off `m1/roster`. FF-merge back to `m1/roster` at M1.1 close. Next sub-step branches off updated `m1/roster`.
> - **ADR numbering.** Next at write time **ADR-0061**.
> - **User-knowledge note.** Per [[user-postgres-concurrency-gap]]: argon2id parameters / session-token entropy are crypto-adjacent — ground vocabulary briefly when introducing primitives; offer worked examples for non-obvious choices (e.g., why `secrets.token_urlsafe(32)` over `uuid4()` for session tokens).

## Pointers

- Workflow protocol: `planning/_workflow.md`
- File rules registry (generated): `planning/_file-rules.md` (last regenerated 2026-05-18)
- Phase roster: `planning/phases.md` (Phase 1 ✓ complete 2026-05-17; Phase 2 current; Phase 3 stub)
- Step list (current phase): `planning/steps.md` (Phase 2 / Implementation — 9 steps mirroring roadmap M0–M8; **Step 1 ✓ COMPLETE 2026-05-19 (Session 33)**; **Step 2 partitioned into 4 sub-steps 2026-05-19 (Session 34)** — M1.1 detailed, M1.2 / M1.3 / M1.4 stubs; Steps 3–9 stubs)
- Archived step list (Phase 1): `planning/steps.archive/conceptualization.md`
- Session conventions: `planning/sessions.md`
- Decisions log: `planning/decisions.md` (currently ADR-0001 through ADR-0060; next ADR at write time: **ADR-0061**)
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
