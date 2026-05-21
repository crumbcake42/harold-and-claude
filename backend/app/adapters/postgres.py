"""Adapter boundary for Postgres-specific data-layer features per ADR-0051 +
ADR-0052 + ADR-0056.

This module (`app.adapters.postgres`) is the single documented seam for the
three Postgres-specific primitives that have no portable equivalent;
non-Postgres engines (SQLite is the only other supported target, used as
offline-fallback per ADR-0051) receive degraded equivalents. `json_column()`
is used at table-declaration time; `set_serializable_isolation` and
`try_advisory_xact_lock` are injected into the command dispatcher, so the
engine in `app.engine` imports nothing from `app.adapters`.

Per ADR-0052 § Engine-portability discipline:
    "JSONB ops, advisory locks, and SERIALIZABLE isolation are
    Postgres-specific. All three sit behind the documented adapter boundary
    [...] the SQLite-offline-fallback path uses degraded equivalents [...]
    not production-equivalent -- explicit, acknowledged."

The three functions:

  json_column()
      Column type for JSON-bearing history columns. JSONB on PostgreSQL,
      portable JSON (text-backed) on SQLite. Production-equivalent: PostgreSQL
      gains the JSONB indexing / containment-op surface; SQLite reads and
      writes correctly but has no JSONB ops and no GIN indexing.

  try_advisory_xact_lock(session, key)
      Per ADR-0056 D1.b: the closure-readiness predicate cluster opts into
      `pg_try_advisory_xact_lock` keyed per-project. Production-equivalent:
      PostgreSQL acquires a transaction-scoped advisory lock and fast-fails
      on contention. Degraded SQLite: returns True unconditionally -- SQLite's
      single-writer model serializes writes already, so the advisory-lock
      fast-fail signal does not apply. Not production-equivalent (the fast-
      fail semantics that the dispatcher's retry loop converts to a domain-
      level retry signal are absent).

  set_serializable_isolation(session)
      Per ADR-0052 + ADR-0056 D1.a: SERIALIZABLE is the default isolation
      primitive for cross-entity invariant revalidation. Set per-transaction
      at the dispatcher's top-level pipeline entry. Production-equivalent:
      PostgreSQL switches the transaction to SERIALIZABLE. Degraded SQLite:
      no-op -- SQLite's single-writer model approximates serializability by
      removing concurrency, not by handling it. Not production-equivalent
      (the SERIALIZABLE primitive's behavior under contention -- the
      `serialization_failure` signal -- does not arise; ADR-0010's cross-
      entity revalidation behavior is unverifiable on SQLite).
"""

from sqlalchemy import JSON, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

from app.engine.locks import validate_key_namespace


def json_column() -> JSON:
    """Cross-dialect JSON column type. Returns a SQLAlchemy JSON type that
    `with_variant`s to JSONB on PostgreSQL; SQLite gets text-backed JSON.

    Used at table-declaration time -- the returned type is consumed by
    `mapped_column(json_column(), ...)` in `app.adapters.history`.
    """
    return JSON().with_variant(JSONB(), "postgresql")


def try_advisory_xact_lock(session: Session, key: str) -> bool:
    """Try to acquire a transaction-scoped advisory lock per ADR-0056.

    PostgreSQL: calls `pg_try_advisory_xact_lock(hashtextextended(:key, 0))`;
    returns True on acquisition, False on contention. The lock is released
    automatically at transaction commit or rollback.

    SQLite: returns True unconditionally. Degraded fallback per ADR-0056 --
    not production-equivalent.

    The key must start with a registered `LockNamespace` prefix per
    `app.engine.locks`; validation raises `ValueError` otherwise.
    """
    validate_key_namespace(key)
    dialect = session.bind.dialect.name if session.bind is not None else ""
    if dialect == "postgresql":
        result = session.execute(
            text("SELECT pg_try_advisory_xact_lock(hashtextextended(:key, 0))"),
            {"key": key},
        ).scalar()
        return bool(result)
    return True


def set_serializable_isolation(session: Session) -> None:
    """Set the current transaction's isolation level to SERIALIZABLE per
    ADR-0052 + ADR-0056 D1.a.

    PostgreSQL: procures the session's connection with the
    `isolation_level=SERIALIZABLE` execution option, scoped to that
    transaction (SQLAlchemy restores the connection's default isolation when
    it returns to the pool).

    SQLite: no-op. SQLite's single-writer concurrency approximates
    serializability by removing concurrency; degraded fallback per ADR-0056 --
    not production-equivalent.

    Called once per top-level dispatch in `Dispatcher._run_pipeline`. MUST be
    the first operation on the session: the `isolation_level` option is
    applied as the connection is first procured, and SQLAlchemy refuses to
    alter it once the session's transaction has autobegun. `_run_pipeline`
    calls this before any other session use.
    """
    if session.bind is not None and session.bind.dialect.name == "postgresql":
        session.connection(execution_options={"isolation_level": "SERIALIZABLE"})
