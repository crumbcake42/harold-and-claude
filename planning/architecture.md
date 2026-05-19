# Architecture

## File contract

**Holds:** One-page architecture sketch of `sca-tracker` — component boxes, data flow, and the boundaries between them. Covers the runtime stack (ADR-0051) and the data layer (ADR-0052) at the level of "what runs where, and what talks to what." Does **not** hold the conceptual data model (Step 9 → `data-model.md`), the roadmap (Step 9 → `roadmap.md`), or the implementation-phase concrete designs (`Command` dispatcher, PaaS vendor specifics, per-invariant isolation choices — all carry-forwards).
**Update when:** ADR-0051 or ADR-0052 are amended in a way that changes component boundaries or data flow; a new architectural-shape ADR lands; the PaaS vendor is pinned (vendor name + DB managed-offering name). Vendor pin is currently deferred per ADR-0055 — no Step-1.2-shaped trigger; lands when the user prompts circle-back, no later than M8 cutover if the project ships to production.

---

## Component sketch

```
                            ┌────────────────────────┐
                            │  Browser (office user) │
                            └───────────┬────────────┘
                                        │ HTTPS
                                        ▼
                        ┌───────────────────────────────┐
                        │  Managed PaaS                 │
                        │  (vendor deferred / ADR-0055) │
                        │  ───────────────────────────  │
                        │                               │
                        │  ┌─────────────────────────┐  │
                        │  │ CDN / static SPA host   │  │
                        │  │ (Vite build output:     │  │
                        │  │  React + TanStack)      │  │
                        │  └─────────────┬───────────┘  │
                        │                │ /api/* calls │
                        │                ▼              │
                        │  ┌─────────────────────────┐  │
                        │  │ API container (FastAPI) │  │
                        │  │ ─────────────────────── │  │
                        │  │  Routes (transport)     │  │
                        │  │       │                 │  │
                        │  │       ▼                 │  │
                        │  │  Command dispatcher     │  │
                        │  │   (auth → lifecycle →   │  │
                        │  │    apply → invariants → │  │
                        │  │    history → commit)    │  │
                        │  │       │                 │  │
                        │  │       ▼                 │  │
                        │  │  SQLAlchemy session     │  │
                        │  │  (engine adapter        │  │
                        │  │   boundary lives here)  │  │
                        │  └─────────────┬───────────┘  │
                        │                │              │
                        │                ▼              │
                        │  ┌─────────────────────────┐  │
                        │  │ Managed PostgreSQL 15+  │  │
                        │  │ (Neon free-tier dev /   │  │
                        │  │  PaaS-managed prod)     │  │
                        │  │ ─────────────────────── │  │
                        │  │  Entity tables (21)     │  │
                        │  │  History tables (9)     │  │
                        │  │  command_audit_log (1)  │  │
                        │  └─────────────────────────┘  │
                        └───────────────────────────────┘
```

---

## Boundaries and what they enforce

### Browser ↔ CDN/SPA
Static asset delivery. SPA bundle (Vite build of React + TanStack Router + TanStack Query + openapi-ts-generated hooks) is served from the same PaaS's CDN. No server-side rendering; no API middleware in the SPA path. Authentication tokens land in the browser via the same `/api/*` surface as the rest of the API.

### SPA ↔ API container
JSON over HTTPS. Contract is FastAPI's OpenAPI schema; openapi-ts consumes it at build time to generate the typed TanStack Query hooks the SPA calls. Type drift between FE and BE is structurally prevented — the schema is the contract.

### Routes ↔ Command dispatcher
Routes are transport; they decode HTTP, authenticate the caller, and dispatch to a named command. **Routes are not commands.** A route may invoke one command per request (the common case) or, for compound user-facing commands (`domain-model.md` § Design patterns #5), one named compound command that dispatches sub-commands atomically. The dispatcher is the only path that mutates the data layer.

### Command dispatcher ↔ SQLAlchemy session
Each command runs inside one SQLAlchemy session and one Postgres transaction. The dispatcher's pipeline order (authorization per ADR-0012 → lifecycle gate per ADR-0009 → apply mutation → well-formedness invariants per ADR-0010 → history write per ADR-0008 + ADR-0052 → commit) is uniform across every command. Rejection at any pipeline step rolls the transaction back; no mutation persists, no history row persists (per ADR-0011).

### SQLAlchemy session ↔ Postgres
The adapter boundary. Engine-specific features (JSONB ops, `pg_try_advisory_xact_lock`, `SERIALIZABLE` isolation) live behind named adapter functions, never inline in domain code. This keeps the SQLite-offline-fallback path buildable (with degraded equivalents — JSON-text columns, optimistic locking, default isolation) per ADR-0051's engine-portability discipline.

### Data layer internal topology
- **Entity tables** — one per entity in the 21-entity roster (`domain-model.md`).
- **History tables** — 9 per-entity append-only tables (3 comprehensive + 6 lifecycle per `domain-model.md` § History patterns per entity). Written in the same transaction as the entity mutation by the dispatcher's history step.
- **`command_audit_log`** — single shared table with polymorphic `(entity_type, entity_id)` reference for the 7 audit-log entities. Written by the dispatcher in-txn with the entity mutation (same SQLAlchemy session) per ADR-0057.

---

## Data flow — successful command

1. Browser sends an authenticated request to `/api/<resource>/<action>` (e.g., `POST /api/projects/{id}/close`).
2. FastAPI route validates the request payload against its Pydantic schema, resolves the caller, and dispatches to the named command (`close_project(project_id, payload)`).
3. Command dispatcher opens a SQLAlchemy session + Postgres transaction.
4. **Authorization** — the command's declarative predicate over `(caller, command, target)` (ADR-0012) is evaluated; rejection here aborts before any state read.
5. **Lifecycle gate** — if the command declares a lifecycle transition (ADR-0009), the target entity's current status is checked against the state machine; rejection aborts the transaction.
6. **Apply** — the command handler mutates the entity record (and any cascaded sub-command targets for compound commands).
7. **Well-formedness invariants** (ADR-0010) — intra-entity and cross-entity invariants for every entity and relationship touched are revalidated after the proposed change is applied. Cross-entity invariants use `SERIALIZABLE` isolation by default; `pg_try_advisory_xact_lock` is the opt-in primitive per the two-prong criterion + worked-example assignments in ADR-0056 (closure-readiness cluster → advisory lock per-project; EmployeeRole disjoint-ranges → SERIALIZABLE). Rejection aborts the transaction (ADR-0011 — no mutation, no history record).
8. **History write** — for history-carrying targets, the dispatcher writes the history row (comprehensive snapshot or lifecycle transition record per the entity's declared pattern) into the same transaction. For audit-log targets, the dispatcher emits a `command_audit_log` row in-txn per ADR-0057. For no-history targets, nothing.
9. **Commit** — the transaction commits; the entity mutation and history row become visible atomically.
10. Route returns the FastAPI response; SPA's TanStack Query cache invalidates the affected keys; UI re-fetches.

A rejected command produces no state change and no history (per ADR-0011); the caller receives the rejection reason as the HTTP error body.

---

## Out-of-band concerns

- **File storage** (uploaded Documents per `domain-model.md`'s Document entity). Not pinned at architecture sketch level; the obvious choice is object storage on the chosen PaaS (S3-compatible bucket) referenced by URL from the Document entity row. Deferred — bundled with the PaaS vendor pick per ADR-0055.
- **Background jobs / scheduled work.** Not in MVP scope per `mvp.md`. If added later, the PaaS-bundled worker primitive (Fly Machines / Render background workers / Railway cron) is the path; no separate queue infrastructure planned.
- **Email / notification side effects.** Not in MVP scope per `mvp.md`. When added, they live downstream of the command commit, not inside the dispatcher transaction (side effects must not block transaction commit).
- **Authentication mechanism.** Pinned at implementation kickoff; the architecture commits to "caller identity reaches the dispatcher" but not to the auth scheme (session cookies / JWT / OIDC against a managed identity provider all fit).

---

## Pointers

- Runtime stack: ADR-0051 (`decisions.md`).
- Data layer: ADR-0052 (`decisions.md`).
- Command pipeline semantics: `logic.md` + ADRs 0007 / 0008 / 0009 / 0010 / 0011 / 0012.
- History patterns: `history-patterns.md` + ADR-0006 + ADR-0013.
- Entity roster + per-entity patterns: `domain-model.md`.
- MVP scope envelope: `mvp.md` + ADR-0050.
