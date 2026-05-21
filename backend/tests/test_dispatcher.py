"""End-to-end smoke tests for the M0.3 dispatcher pipeline.

Exercises the full pipeline (auth → lifecycle → apply → invariants → history
→ commit) against an in-memory SQLite database with the InMemorySink. Tests
both the success paths (comprehensive + lifecycle history records) and the
rejection paths (auth / lifecycle / invariant), plus retry behavior and
cascade safeguards.

Note: SQLite is the smoke-test target per ADR-0051 / ADR-0052 -- production-
equivalent behavior (SERIALIZABLE, advisory locks) requires Postgres; the
SQLite fallback is degraded-but-buildable per ADR-0056. Integration tests
against Postgres land in CI per the broader stack ADRs.
"""

from collections.abc import Iterator
from uuid import uuid4

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.postgres import set_serializable_isolation, try_advisory_xact_lock
from app.framework.caller import Caller
from app.framework.capture import (
    ComprehensiveRecord,
    InMemorySink,
    LifecycleRecord,
)
from app.framework.command import (
    _clear_registry_for_tests,
    cascade_drift_report,
    register,
    validate_registry,
)
from app.framework.dispatcher import Dispatcher
from app.framework.exceptions import (
    AuthorizationDenied,
    InvariantViolation,
    LifecycleViolation,
)
from tests.fixtures.smoketest.commands import (
    CloseSmokeLifecycle,
    CreateSmoke,
    CreateSmokeLifecycle,
    EditSmoke,
    EditSmokeLifecycleNote,
    EditSmokeNoAuth,
)
from tests.fixtures.smoketest.entities import SmokeBase, SmokeEntity, SmokeLifecycleEntity


def _make_caller() -> Caller:
    """Smoke-test caller -- empty roles; smoke commands use always_allow auth."""
    return Caller(id=uuid4(), username="smoke", roles=frozenset())


@pytest.fixture(autouse=True)
def _isolated_command_registry() -> Iterator[None]:
    """Reset the global command registry between tests so each test starts
    from a known state. Smoke-test commands register inside each test (or
    via a shared setup) rather than at module import.
    """
    _clear_registry_for_tests()
    yield
    _clear_registry_for_tests()


@pytest.fixture
def smoke_session_factory(
    sqlite_engine: Engine,
    sqlite_session_factory: sessionmaker[Session],
) -> sessionmaker[Session]:
    """Create the smoke-entity tables in the test SQLite engine and return
    the session factory bound to it. Pulls sqlite_engine + sqlite_session_factory
    from tests/conftest.py.
    """
    SmokeBase.metadata.create_all(sqlite_engine)
    return sqlite_session_factory


@pytest.fixture
def sink() -> InMemorySink:
    return InMemorySink()


@pytest.fixture
def dispatcher(
    smoke_session_factory: sessionmaker[Session], sink: InMemorySink
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


# ---- Comprehensive-pattern paths ----


def test_create_smoke_writes_comprehensive_record_and_persists_entity(
    dispatcher: Dispatcher,
    sink: InMemorySink,
    caller: Caller,
    smoke_session_factory: sessionmaker[Session],
) -> None:
    register(CreateSmoke)

    entity = dispatcher.dispatch(CreateSmoke, CreateSmoke.Payload(value=42, note="hi"), caller)

    assert isinstance(entity, SmokeEntity)
    assert entity.value == 42
    # Sink captured one comprehensive record.
    assert len(sink.records) == 1
    record = sink.records[0]
    assert isinstance(record, ComprehensiveRecord)
    assert record.entity_type == "SmokeEntity"
    assert record.entity_id == entity.id
    assert record.caller_id == caller.id
    assert record.command_name == "CreateSmoke"
    assert record.snapshot["value"] == 42
    assert record.snapshot["note"] == "hi"
    # Entity persisted in DB.
    with smoke_session_factory() as session:
        fetched = session.get(SmokeEntity, entity.id)
        assert fetched is not None
        assert fetched.value == 42


def test_edit_smoke_mutates_value_and_writes_second_record(
    dispatcher: Dispatcher,
    sink: InMemorySink,
    caller: Caller,
    smoke_session_factory: sessionmaker[Session],
) -> None:
    register(CreateSmoke)
    register(EditSmoke)

    created = dispatcher.dispatch(CreateSmoke, CreateSmoke.Payload(value=1), caller)
    edited = dispatcher.dispatch(
        EditSmoke, EditSmoke.Payload(entity_id=created.id, value=99), caller
    )

    assert edited.value == 99
    assert len(sink.records) == 2
    second = sink.records[1]
    assert isinstance(second, ComprehensiveRecord)
    assert second.snapshot["value"] == 99
    assert second.command_name == "EditSmoke"


# ---- Rejection paths (ADR-0011: no mutation, no history) ----


def test_authorization_denied_emits_no_record_and_persists_no_mutation(
    dispatcher: Dispatcher,
    sink: InMemorySink,
    caller: Caller,
    smoke_session_factory: sessionmaker[Session],
) -> None:
    register(CreateSmoke)
    register(EditSmokeNoAuth)

    created = dispatcher.dispatch(CreateSmoke, CreateSmoke.Payload(value=10), caller)
    sink.records.clear()  # ignore the create record

    with pytest.raises(AuthorizationDenied):
        dispatcher.dispatch(
            EditSmokeNoAuth,
            EditSmokeNoAuth.Payload(entity_id=created.id, value=999),
            caller,
        )

    assert sink.records == []
    with smoke_session_factory() as session:
        fetched = session.get(SmokeEntity, created.id)
        assert fetched is not None
        assert fetched.value == 10  # unchanged


def test_invariant_violation_rolls_back_and_emits_no_record(
    dispatcher: Dispatcher,
    sink: InMemorySink,
    caller: Caller,
    smoke_session_factory: sessionmaker[Session],
) -> None:
    register(CreateSmoke)

    # value=0 fails ValueIsPositive (which checks value > 0).
    with pytest.raises(InvariantViolation):
        dispatcher.dispatch(CreateSmoke, CreateSmoke.Payload(value=0), caller)

    assert sink.records == []
    with smoke_session_factory() as session:
        count = session.query(SmokeEntity).count()
        assert count == 0


# ---- Lifecycle-pattern paths ----


def test_create_smoke_lifecycle_writes_lifecycle_record_with_none_from_state(
    dispatcher: Dispatcher,
    sink: InMemorySink,
    caller: Caller,
) -> None:
    register(CreateSmokeLifecycle)

    entity = dispatcher.dispatch(
        CreateSmokeLifecycle, CreateSmokeLifecycle.Payload(note="seed"), caller
    )

    assert len(sink.records) == 1
    record = sink.records[0]
    assert isinstance(record, LifecycleRecord)
    assert record.from_state is None  # creation: target did not exist pre-handler
    assert record.to_state == "open"
    assert record.transition_name == "create"
    assert record.entity_id == entity.id


def test_close_smoke_lifecycle_writes_lifecycle_record_with_from_state(
    dispatcher: Dispatcher,
    sink: InMemorySink,
    caller: Caller,
) -> None:
    register(CreateSmokeLifecycle)
    register(CloseSmokeLifecycle)

    created = dispatcher.dispatch(
        CreateSmokeLifecycle, CreateSmokeLifecycle.Payload(), caller
    )
    sink.records.clear()

    closed = dispatcher.dispatch(
        CloseSmokeLifecycle, CloseSmokeLifecycle.Payload(entity_id=created.id), caller
    )

    assert closed.state == "closed"
    assert len(sink.records) == 1
    record = sink.records[0]
    assert isinstance(record, LifecycleRecord)
    assert record.from_state == "open"
    assert record.to_state == "closed"
    assert record.transition_name == "close"


def test_non_lifecycle_command_on_lifecycle_entity_writes_no_record(
    dispatcher: Dispatcher,
    sink: InMemorySink,
    caller: Caller,
) -> None:
    """ADR-0013 pattern-4: lifecycle-capture entities produce records only
    for lifecycle-affecting commands."""
    register(CreateSmokeLifecycle)
    register(EditSmokeLifecycleNote)

    created = dispatcher.dispatch(
        CreateSmokeLifecycle, CreateSmokeLifecycle.Payload(), caller
    )
    sink.records.clear()

    dispatcher.dispatch(
        EditSmokeLifecycleNote,
        EditSmokeLifecycleNote.Payload(entity_id=created.id, note="updated"),
        caller,
    )

    assert sink.records == []  # no history row for non-lifecycle command


def test_invalid_lifecycle_transition_rejected(
    dispatcher: Dispatcher,
    sink: InMemorySink,
    caller: Caller,
    smoke_session_factory: sessionmaker[Session],
) -> None:
    register(CreateSmokeLifecycle)
    register(CloseSmokeLifecycle)

    created = dispatcher.dispatch(
        CreateSmokeLifecycle, CreateSmokeLifecycle.Payload(), caller
    )
    dispatcher.dispatch(
        CloseSmokeLifecycle, CloseSmokeLifecycle.Payload(entity_id=created.id), caller
    )
    sink.records.clear()

    # Second close attempt: state is "closed"; no transitions permitted.
    with pytest.raises(LifecycleViolation):
        dispatcher.dispatch(
            CloseSmokeLifecycle,
            CloseSmokeLifecycle.Payload(entity_id=created.id),
            caller,
        )

    assert sink.records == []  # rejection emits no record
    with smoke_session_factory() as session:
        fetched = session.get(SmokeLifecycleEntity, created.id)
        assert fetched is not None
        assert fetched.state == "closed"  # unchanged


# ---- Cascade-safeguard tests (ADR-0060) ----


def test_validate_registry_passes_when_no_destructive_cascades() -> None:
    register(CreateSmoke)
    register(EditSmoke)
    validate_registry()  # should not raise


def test_cascade_drift_report_reports_no_invocations_for_simple_handlers() -> None:
    register(CreateSmoke)
    report = cascade_drift_report()
    assert report["CreateSmoke"]["declared"] == set()
    assert report["CreateSmoke"]["invoked"] == set()
    assert report["CreateSmoke"]["invoked_not_declared"] == set()
