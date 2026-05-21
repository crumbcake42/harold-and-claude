"""Unit tests for app.adapters.postgres -- the documented Postgres-specific
adapter boundary per ADR-0051 + ADR-0052.

These tests verify each adapter function's dialect-dispatch logic:
  - PostgreSQL branch (lock SQL emitted; isolation execution_options set;
    json_column produces a JSONB-variant type).
  - SQLite branch (lock returns True without executing SQL; isolation is a
    no-op; json_column falls back to portable JSON for non-PG dialects).

The PG branch is exercised by mocking session.bind.dialect.name -- the live-
engine PG path is verified by developers pointing DATABASE_URL at a real
Postgres (no CI gate for PG in M0; docker-compose deferred until vendor pick
per ADR-0055).

The SQLite branches are also exercised live by the 16 tests under
test_dispatcher.py + test_capture_sink_integration.py.
"""

from unittest.mock import MagicMock
from uuid import UUID

import pytest
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Dialect, Engine
from sqlalchemy.orm import sessionmaker

from app.adapters.postgres import (
    json_column,
    set_serializable_isolation,
    try_advisory_xact_lock,
)
from app.framework.locks import closure_readiness_key

# ----- json_column -----


def test_json_column_returns_json_type_with_postgresql_variant() -> None:
    """json_column() returns a SQLAlchemy JSON type. The PostgreSQL variant
    is JSONB; non-PostgreSQL dialects fall back to the base portable JSON.
    """
    col_type = json_column()
    assert isinstance(col_type, JSON)
    pg_variant = col_type.dialect_impl(_pg_dialect())
    assert isinstance(pg_variant, JSONB)


def test_json_column_falls_back_to_portable_json_on_sqlite() -> None:
    """On SQLite the JSON type does not promote to JSONB; the column writes
    via the text-backed JSON impl. Production-equivalence is documented as
    degraded.
    """
    col_type = json_column()
    sqlite_impl = col_type.dialect_impl(_sqlite_dialect())
    assert not isinstance(sqlite_impl, JSONB)


# ----- try_advisory_xact_lock -----


def test_try_advisory_xact_lock_emits_pg_call_on_postgresql() -> None:
    """On PostgreSQL the adapter executes pg_try_advisory_xact_lock(
    hashtextextended(:key, 0)) and returns the scalar result coerced to bool.
    """
    session = MagicMock()
    session.bind.dialect.name = "postgresql"
    session.execute.return_value.scalar.return_value = True

    acquired = try_advisory_xact_lock(session, closure_readiness_key(_fixed_uuid()))

    assert acquired is True
    assert session.execute.call_count == 1
    sql_text = session.execute.call_args.args[0]
    assert "pg_try_advisory_xact_lock" in str(sql_text)
    assert "hashtextextended" in str(sql_text)


def test_try_advisory_xact_lock_returns_false_on_postgresql_contention() -> None:
    """When pg_try_advisory_xact_lock returns false (contention), the adapter
    surfaces False so the dispatcher's retry loop can fast-fail per ADR-0056.
    """
    session = MagicMock()
    session.bind.dialect.name = "postgresql"
    session.execute.return_value.scalar.return_value = False

    acquired = try_advisory_xact_lock(session, closure_readiness_key(_fixed_uuid()))

    assert acquired is False


def test_try_advisory_xact_lock_returns_true_unconditionally_on_sqlite() -> None:
    """SQLite degraded fallback: no advisory-lock primitive, return True so
    the invariant proceeds. Not production-equivalent (per ADR-0056). No SQL
    executed.
    """
    session = MagicMock()
    session.bind.dialect.name = "sqlite"

    acquired = try_advisory_xact_lock(session, closure_readiness_key(_fixed_uuid()))

    assert acquired is True
    session.execute.assert_not_called()


def test_try_advisory_xact_lock_validates_key_namespace() -> None:
    """Keys not starting with a registered LockNamespace prefix raise
    ValueError regardless of dialect. Validation happens before any dialect
    branch, so unregistered keys fail identically on PG and SQLite.
    """
    session = MagicMock()
    session.bind.dialect.name = "postgresql"
    with pytest.raises(ValueError, match="registered namespace prefix"):
        try_advisory_xact_lock(session, "unregistered:bogus")


def test_try_advisory_xact_lock_handles_unbound_session() -> None:
    """A session with no engine bound (edge case) is treated as non-Postgres
    and falls through to the degraded-fallback return-True path.
    """
    session = MagicMock()
    session.bind = None

    acquired = try_advisory_xact_lock(session, closure_readiness_key(_fixed_uuid()))

    assert acquired is True


# ----- set_serializable_isolation -----


def test_set_serializable_isolation_applies_execution_option_on_postgresql() -> None:
    """On PostgreSQL the adapter sets isolation_level=SERIALIZABLE on the
    session's connection execution options per ADR-0056.
    """
    session = MagicMock()
    session.bind.dialect.name = "postgresql"

    set_serializable_isolation(session)

    session.connection.assert_called_once_with()
    session.connection.return_value.execution_options.assert_called_once_with(
        isolation_level="SERIALIZABLE"
    )


def test_set_serializable_isolation_is_noop_on_sqlite() -> None:
    """SQLite degraded fallback: no isolation switch (single-writer
    concurrency approximates SERIALIZABLE by removing concurrency).
    """
    session = MagicMock()
    session.bind.dialect.name = "sqlite"

    set_serializable_isolation(session)

    session.connection.assert_not_called()


def test_set_serializable_isolation_is_noop_on_unbound_session() -> None:
    """A session with no engine bound is a no-op (no connection to switch)."""
    session = MagicMock()
    session.bind = None

    set_serializable_isolation(session)

    session.connection.assert_not_called()


# ----- Live SQLite end-to-end (not mocked) -----


def test_adapter_functions_run_clean_against_real_sqlite_engine(
    sqlite_engine: Engine,
) -> None:
    """Smoke-check: bound to a real SQLite engine, the adapter's SQLite
    branches all run without raising. The 5 integration tests in
    test_capture_sink_integration.py also exercise json_column +
    set_serializable_isolation + try_advisory_xact_lock through the
    dispatcher end-to-end; this test confirms the bare adapter calls work
    in isolation as well.
    """
    factory = sessionmaker(bind=sqlite_engine, autoflush=False, future=True)
    session = factory()
    try:
        set_serializable_isolation(session)
        acquired = try_advisory_xact_lock(session, closure_readiness_key(_fixed_uuid()))
        assert acquired is True
    finally:
        session.close()


# ----- helpers -----


def _pg_dialect() -> Dialect:
    from sqlalchemy.dialects.postgresql.psycopg import PGDialect_psycopg

    return PGDialect_psycopg()


def _sqlite_dialect() -> Dialect:
    from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite

    return SQLiteDialect_pysqlite()


def _fixed_uuid() -> UUID:
    return UUID("00000000-0000-0000-0000-000000000001")
