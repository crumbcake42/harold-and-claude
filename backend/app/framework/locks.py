"""Advisory-lock primitives for the command pipeline's invariant step.

Per ADR-0056: SERIALIZABLE is the default isolation primitive for cross-entity
invariant revalidation. Invariants whose conflict surface is wide enough to
produce frequent serialization failures AND whose scope can be expressed as a
small set of named lock keys opt into `pg_try_advisory_xact_lock` via this
module's helpers. The closure-readiness predicate cluster is the first user
(keyed per-project).

The SQLite offline-fallback path returns True from `try_advisory_xact_lock` --
SQLite's single-writer model serializes writes already, so the advisory-lock
fast-fail signal does not apply; this is the degraded-but-buildable behavior
per ADR-0052 + ADR-0056 (explicitly not production-equivalent; the real
adapter boundary for Postgres-specific features lands in Step 1.4 / M0.4).
"""

from enum import StrEnum
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


class LockNamespace(StrEnum):
    """Every advisory-lock namespace used by the application.

    To introduce a new advisory-lock use, add an entry here AND a per-namespace
    key-builder function below. The registry-load-time check in
    `_validate_key_namespace` enforces that all keys passed to
    `try_advisory_xact_lock` start with one of these prefixes.
    """

    CLOSURE_READINESS = "closure-readiness"


def closure_readiness_key(project_id: UUID) -> str:
    """Lock key for the closure-readiness predicate cluster (ADR-0056 D1.b)."""
    return f"{LockNamespace.CLOSURE_READINESS.value}:{project_id}"


_REGISTERED_PREFIXES = tuple(f"{ns.value}:" for ns in LockNamespace)


def _validate_key_namespace(key: str) -> None:
    if not key.startswith(_REGISTERED_PREFIXES):
        raise ValueError(
            f"Lock key {key!r} does not start with a registered namespace prefix. "
            f"Registered prefixes: {_REGISTERED_PREFIXES}. "
            f"Add an entry to LockNamespace and a per-namespace key-builder."
        )


def try_advisory_xact_lock(session: Session, key: str) -> bool:
    """Try to acquire a transaction-scoped advisory lock.

    Returns True on acquisition, False on contention. On Postgres, calls
    `pg_try_advisory_xact_lock(hashtextextended(:key, 0))` -- the lock is
    released automatically at transaction commit or rollback. On SQLite,
    returns True unconditionally (degraded fallback per ADR-0056).
    """
    _validate_key_namespace(key)
    dialect = session.bind.dialect.name if session.bind is not None else ""
    if dialect == "postgresql":
        result = session.execute(
            text("SELECT pg_try_advisory_xact_lock(hashtextextended(:key, 0))"),
            {"key": key},
        ).scalar()
        return bool(result)
    return True
