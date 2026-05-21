"""Advisory-lock key vocabulary for the command pipeline's invariant step.

This module is policy: the set of named advisory-lock namespaces and the per-
namespace key-builder functions that produce concrete lock keys for the
dispatcher to acquire. The acquisition mechanism itself (the PostgreSQL
`pg_try_advisory_xact_lock` call and its SQLite degraded fallback) lives in
`app.adapters.postgres` per ADR-0051 + ADR-0052's adapter-boundary discipline.

Per ADR-0056: SERIALIZABLE is the default isolation primitive for cross-entity
invariant revalidation; invariants whose conflict surface is wide enough to
produce frequent serialization failures AND whose scope can be expressed as a
small set of named lock keys opt into `pg_try_advisory_xact_lock` via this
module's key-builders + the adapter's `try_advisory_xact_lock`. The closure-
readiness predicate cluster is the first user (keyed per-project).
"""

from enum import StrEnum
from uuid import UUID


class LockNamespace(StrEnum):
    """Every advisory-lock namespace used by the application.

    To introduce a new advisory-lock use, add an entry here AND a per-namespace
    key-builder function below. The load-time check in `validate_key_namespace`
    enforces that all keys passed to the adapter's `try_advisory_xact_lock`
    start with one of these prefixes.
    """

    CLOSURE_READINESS = "closure-readiness"


def closure_readiness_key(project_id: UUID) -> str:
    """Lock key for the closure-readiness predicate cluster (ADR-0056 D1.b)."""
    return f"{LockNamespace.CLOSURE_READINESS.value}:{project_id}"


_REGISTERED_PREFIXES = tuple(f"{ns.value}:" for ns in LockNamespace)


def validate_key_namespace(key: str) -> None:
    """Raise ValueError if `key` does not start with a registered LockNamespace
    prefix. Called by the adapter's `try_advisory_xact_lock` before any
    dialect-specific work, so unregistered keys fail identically on all
    engines.
    """
    if not key.startswith(_REGISTERED_PREFIXES):
        raise ValueError(
            f"Lock key {key!r} does not start with a registered namespace prefix. "
            f"Registered prefixes: {_REGISTERED_PREFIXES}. "
            f"Add an entry to LockNamespace and a per-namespace key-builder."
        )
