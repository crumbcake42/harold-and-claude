# Postgres concurrency primer — self-study list

Generated 2026-05-18 (Session 29 — Step 1.2 / M0.2) at user request. The decisions landed in **ADR-0056** (per-invariant isolation primitive) and **ADR-0057** (audit-log write timing) lean on Postgres concurrency primitives that are unfamiliar terrain. This is a study list, not a tutorial — the sources below are where to start.

---

## Topics, foundational → applied

1. **MVCC (Multi-Version Concurrency Control)** — the model Postgres uses for reading without blocking writers. Background for everything else; explains why "isolation level" is a meaningful knob in Postgres rather than a fixed property.

2. **Transaction isolation levels** — Read Committed (Postgres default), Repeatable Read, Serializable. What anomalies each prevents (dirty reads, non-repeatable reads, phantoms, serialization anomalies) and what each costs.

3. **SERIALIZABLE in Postgres specifically (SSI — Serializable Snapshot Isolation)** — Postgres implements SSI, not lock-based serializability. Transactions proceed optimistically; on commit, Postgres checks for serialization anomalies and may reject one with `serialization_failure` (SQLSTATE 40001). The "predicate locking" mechanism — how Postgres tracks reads to detect conflicts — explains why wide-footprint reads under SERIALIZABLE cause frequent false-positive failures. This is the core reason ADR-0056 reaches for advisory locks on closure-readiness.

4. **`serialization_failure` retry semantics** — what application code does when SERIALIZABLE rejects a commit. Typically: catch the error, retry the whole txn from the start, give up after N attempts. Why retry is required even on read-only paths under SERIALIZABLE.

5. **Advisory locks** — user-defined integer-keyed mutexes managed by Postgres. Two dimensions: session-scoped vs. transaction-scoped (the `_xact_` variants auto-release at COMMIT/ROLLBACK), and blocking vs. non-blocking (the `_try_` variants return false instead of waiting). Cooperative — only txns that ask for the same key coordinate. ADR-0056 uses `pg_try_advisory_xact_lock` for closure-readiness.

6. **In-txn writes for accountability** — the simpler default ADR-0057 picked. Why coupling a write to the same transaction as its parent mutation yields the strongest "exists iff" guarantee, at the cost of pinning the write to the response latency path.

7. **Transactional outbox pattern** — the "post-commit via outbox" alternative ADR-0057 considered and deferred. Commit the entity mutation and an outbox row in the same txn; a separate sweeper process drains the outbox into the target table asynchronously. Preserves "no lost rows" without coupling write latency to user-visible response. Background for understanding what ADR-0057 *didn't* pick and when re-adoption would make sense.

---

## Sources

### Postgres official docs (canonical)

- **Transaction Isolation** — https://www.postgresql.org/docs/current/transaction-iso.html — all four isolation levels with examples. SERIALIZABLE section explains SSI mechanics.
- **Advisory Locks** — https://www.postgresql.org/docs/current/explicit-locking.html#ADVISORY-LOCKS — function reference + cooperative-locking semantics + session vs. xact scope.
- **MVCC introduction** — https://www.postgresql.org/docs/current/mvcc-intro.html — short intro chapter; pairs with the Transaction Isolation page.

### Plain-language explanations

- **PostgreSQL wiki — SSI** — https://wiki.postgresql.org/wiki/SSI — practical FAQ on Postgres's SSI implementation, including the predicate-locking machinery and retry semantics. Read this after the official Transaction Isolation page.
- **Markus Winand** — *Use The Index, Luke* (use-the-index-luke.com) and *SQL Performance Explained* (book). Well-regarded plain-language resources on SQL transaction behavior and isolation intuitions across DBs.
- **microservices.io — Transactional Outbox** — https://microservices.io/patterns/data/transactional-outbox.html — Chris Richardson's pattern reference card.
- **Brandur Leach's blog** (brandur.org) — search "outbox" and "postgres" for practical Postgres-specific writeups on the pattern; he runs a lot of production Postgres at Stripe-scale and writes accessibly.

### Deeper / optional

- **Ports & Grittner (2012), "Serializable Snapshot Isolation in PostgreSQL"** — VLDB paper; the formal model behind Postgres's SSI implementation. Academic; skim only if you want the underlying theory. Not needed for day-to-day reasoning.

---

## How these came up in sca-tracker

- **ADR-0052** (data-layer pin, 2026-05-16) committed to PostgreSQL 15+ as the persistence engine and named `SERIALIZABLE` + `pg_try_advisory_xact_lock` as the available primitives for cross-entity invariant enforcement.
- **ADR-0056** (this session) picked the criterion for choosing between them per invariant and assigned the two M0-visible candidates: closure-readiness → advisory lock per-project; EmployeeRole disjoint-ranges → SERIALIZABLE.
- **ADR-0057** (this session) picked in-txn writes over post-commit/outbox for `command_audit_log`.

Read ADR-0052, ADR-0056, ADR-0057 alongside the sources above — the ADRs name the concepts; the sources teach them.

---

## Suggested reading order

1. **MVCC intro** (Postgres docs) — 10 minutes.
2. **Transaction Isolation** (Postgres docs) — 30 minutes; the SERIALIZABLE section is the load-bearing read.
3. **PostgreSQL wiki SSI page** — 20 minutes; reinforces the docs with FAQ framing.
4. **Advisory Locks** (Postgres docs) — 15 minutes.
5. **microservices.io outbox** — 10 minutes; understand the alternative ADR-0057 deferred.
6. ADR-0056 + ADR-0057 in `planning/decisions.md` — re-read after the above; the language should be much less opaque.
