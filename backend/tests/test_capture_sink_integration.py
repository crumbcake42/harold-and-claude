"""End-to-end integration tests for SqlAlchemyCaptureSink.

Where test_dispatcher.py uses InMemorySink to assert what the dispatcher
constructs, this module wires the real SQLAlchemy-backed sink against
SmokeBase history tables and asserts that rows actually land in the DB --
in the same transaction as the entity mutation per ADR-0008 + ADR-0057.

Smoke fixtures (SmokeBase) keep these tests independent of the production
history models. Production wiring will register
COMPREHENSIVE_HISTORY + LIFECYCLE_HISTORY + CommandAuditLog when the first
domain command lands in M1+.
"""

from collections.abc import Iterator
from uuid import uuid4

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.capture import SqlAlchemyCaptureSink
from app.adapters.postgres import set_serializable_isolation, try_advisory_xact_lock
from app.framework.caller import Caller
from app.framework.command import _clear_registry_for_tests, register
from app.framework.dispatcher import Dispatcher
from app.framework.exceptions import InvariantViolation
from tests.fixtures.smoketest.commands import (
    CloseSmokeLifecycle,
    CreateSmoke,
    CreateSmokeAudit,
    CreateSmokeLifecycle,
)
from tests.fixtures.smoketest.entities import (
    SmokeAuditLog,
    SmokeBase,
    SmokeComprehensiveHistory,
    SmokeLifecycleHistory,
)


def _make_caller() -> Caller:
    return Caller(id=uuid4(), username="smoke", roles=frozenset())


@pytest.fixture(autouse=True)
def _isolated_command_registry() -> Iterator[None]:
    _clear_registry_for_tests()
    yield
    _clear_registry_for_tests()


@pytest.fixture
def smoke_session_factory(
    sqlite_engine: Engine, sqlite_session_factory: sessionmaker[Session]
) -> sessionmaker[Session]:
    SmokeBase.metadata.create_all(sqlite_engine)
    return sqlite_session_factory


@pytest.fixture
def sink() -> SqlAlchemyCaptureSink:
    return SqlAlchemyCaptureSink(
        comprehensive={"SmokeEntity": SmokeComprehensiveHistory},
        lifecycle={"SmokeLifecycleEntity": SmokeLifecycleHistory},
        audit_log_model=SmokeAuditLog,
    )


@pytest.fixture
def dispatcher(
    smoke_session_factory: sessionmaker[Session], sink: SqlAlchemyCaptureSink
) -> Dispatcher:
    return Dispatcher(
        session_factory=smoke_session_factory,
        sink=sink,
        set_isolation=set_serializable_isolation,
        try_advisory_lock=try_advisory_xact_lock,
    )


@pytest.fixture
def caller() -> Caller:
    return _make_caller()


# ---- Comprehensive: row lands with full snapshot ----


def test_comprehensive_record_inserts_row_with_snapshot(
    dispatcher: Dispatcher,
    caller: Caller,
    smoke_session_factory: sessionmaker[Session],
) -> None:
    register(CreateSmoke)

    entity = dispatcher.dispatch(CreateSmoke, CreateSmoke.Payload(value=42, note="hi"), caller)

    with smoke_session_factory() as session:
        rows = session.query(SmokeComprehensiveHistory).all()
        assert len(rows) == 1
        row = rows[0]
        assert row.entity_id == entity.id
        assert row.command_name == "CreateSmoke"
        assert row.caller_id == caller.id
        assert row.snapshot["value"] == 42
        assert row.snapshot["note"] == "hi"


# ---- Lifecycle: two events produce two rows with correct from_state/to_state ----


def test_lifecycle_records_capture_create_and_close_transitions(
    dispatcher: Dispatcher,
    caller: Caller,
    smoke_session_factory: sessionmaker[Session],
) -> None:
    register(CreateSmokeLifecycle)
    register(CloseSmokeLifecycle)

    created = dispatcher.dispatch(
        CreateSmokeLifecycle, CreateSmokeLifecycle.Payload(note="seed"), caller
    )
    dispatcher.dispatch(
        CloseSmokeLifecycle, CloseSmokeLifecycle.Payload(entity_id=created.id), caller
    )

    with smoke_session_factory() as session:
        rows = (
            session.query(SmokeLifecycleHistory)
            .order_by(SmokeLifecycleHistory.at)
            .all()
        )
        assert len(rows) == 2
        assert rows[0].from_state is None
        assert rows[0].to_state == "open"
        assert rows[0].transition_name == "create"
        assert rows[1].from_state == "open"
        assert rows[1].to_state == "closed"
        assert rows[1].transition_name == "close"


# ---- Audit log: row lands with payload_summary + entity_type ----


def test_audit_log_record_inserts_row_with_payload_summary(
    dispatcher: Dispatcher,
    caller: Caller,
    smoke_session_factory: sessionmaker[Session],
) -> None:
    register(CreateSmokeAudit)

    entity = dispatcher.dispatch(
        CreateSmokeAudit, CreateSmokeAudit.Payload(label="hello"), caller
    )

    with smoke_session_factory() as session:
        rows = session.query(SmokeAuditLog).all()
        assert len(rows) == 1
        row = rows[0]
        assert row.entity_type == "SmokeAuditEntity"
        assert row.entity_id == entity.id
        assert row.command_name == "CreateSmokeAudit"
        assert row.payload_summary == {"label": "hello"}


# ---- Rejection: invariant violation rolls back history alongside the mutation ----


def test_invariant_violation_rolls_back_history_row(
    dispatcher: Dispatcher,
    caller: Caller,
    smoke_session_factory: sessionmaker[Session],
) -> None:
    """ADR-0008 + ADR-0011: if any pipeline step rejects, the transaction
    rolls back -- both the entity mutation and the sink's session.add() are
    discarded together. The sink does not need its own rollback hook.
    """
    register(CreateSmoke)

    with pytest.raises(InvariantViolation):
        dispatcher.dispatch(CreateSmoke, CreateSmoke.Payload(value=0), caller)

    with smoke_session_factory() as session:
        assert session.query(SmokeComprehensiveHistory).count() == 0


# ---- Sink: unregistered entity type raises a useful KeyError ----


def test_sink_raises_keyerror_for_unregistered_entity_type(
    sink: SqlAlchemyCaptureSink,
    smoke_session_factory: sessionmaker[Session],
) -> None:
    from datetime import UTC, datetime

    from app.framework.capture import ComprehensiveRecord

    record = ComprehensiveRecord(
        id=uuid4(),
        entity_type="UnknownEntity",
        entity_id=uuid4(),
        command_id=uuid4(),
        command_name="DoStuff",
        caller_id=uuid4(),
        at=datetime.now(UTC),
        snapshot={},
    )
    with (
        smoke_session_factory() as session,
        pytest.raises(KeyError, match="UnknownEntity"),
    ):
        sink.emit(record, session)
