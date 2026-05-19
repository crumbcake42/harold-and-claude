"""Command dispatcher per ADR-0058.

The dispatcher runs the `logic.md` pipeline -- authorization → lifecycle →
apply → invariants → history → commit -- once per attempt, wrapped in a
small retry loop that catches the two contention modes (advisory-lock
fast-fail per ADR-0056 and Postgres serialization_failure under
SERIALIZABLE isolation) and re-runs the whole pipeline up to MAX_ATTEMPTS
times with jittered backoff. Retry exhaustion surfaces as TransientContention
(per ADR-0058); routes translate to HTTP 409 / 503. Auth / lifecycle /
invariant rejections (CommandRejected subclasses) propagate unwrapped --
they are caller-visible domain errors per ADR-0011, not transient
conditions.

Per-transaction SERIALIZABLE isolation per ADR-0056 (dispatcher-level, not
engine-level: reads / scripts / health checks going through the same engine
inherit default isolation). Cascade-invoke entry point lives here per
ADR-0060 since the call surface consumes dispatcher internals.
"""

import logging
import random
import time
import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.orm import Session, sessionmaker

from app.framework.capture import (
    AuditLogRecord,
    CaptureSink,
    ComprehensiveRecord,
    HistoryRecord,
    LifecycleRecord,
)
from app.framework.command import Caller, Command
from app.framework.exceptions import (
    AdvisoryLockUnavailable,
    AuthorizationDenied,
    CascadeViolation,
    InvariantViolation,
    LifecycleViolation,
    TransientContention,
)
from app.framework.locks import try_advisory_xact_lock

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
BACKOFF_BASE_MS = 20  # 20, 40, 80 with jitter; ~100ms total budget


def _is_serialization_failure(exc: BaseException) -> bool:
    """Detect Postgres serialization_failure (SQLSTATE 40001) wrapped by
    SQLAlchemy's DBAPIError. Returns False on non-Postgres dialects and on
    OperationalError shapes that are not serialization failures."""
    if not isinstance(exc, DBAPIError):
        return False
    orig = getattr(exc, "orig", None)
    if orig is None:
        return False
    sqlstate = getattr(orig, "sqlstate", None) or getattr(orig, "pgcode", None)
    return sqlstate == "40001"


def _jittered_backoff_seconds(attempt: int) -> float:
    """Exponential backoff with full jitter. attempt is 1-indexed."""
    base_ms = BACKOFF_BASE_MS * (2 ** (attempt - 1))
    jittered_ms = random.uniform(0, base_ms)
    return jittered_ms / 1000.0


def _snapshot_entity(entity: Any) -> dict[str, Any]:
    """Serialize an SQLAlchemy entity's column state to a dict.

    1.3a-grade: iterates declared columns via the SQLAlchemy mapper. References
    to other entities are not snapshotted -- typed-UUID refs only per ADR-0013 +
    ADR-0052 § S5 (foreign-key columns are values, so they appear as scalars;
    relationship-attribute traversals are skipped).
    """
    try:
        from sqlalchemy import inspect as sa_inspect
    except ImportError:
        return {}
    state = sa_inspect(entity)
    return {col.key: getattr(entity, col.key) for col in state.mapper.column_attrs}


class Dispatcher:
    """Runs Command instances through the auth → lifecycle → apply → invariants
    → history → commit pipeline, with retry on contention.

    Constructor injection per ADR-0059's test-ergonomics consequence:
    session_factory + sink come in as args; tests construct
    Dispatcher(session_factory=test_factory, sink=InMemorySink()).
    """

    def __init__(self, session_factory: sessionmaker[Session], sink: CaptureSink) -> None:
        self.session_factory = session_factory
        self.sink = sink

    def dispatch(
        self,
        command_cls: type[Command],
        payload: BaseModel,
        caller: Caller,
    ) -> Any:
        """Execute a top-level command on behalf of `caller`. Retries on
        contention; raises TransientContention on exhaustion. CommandRejected
        subclasses (auth / lifecycle / invariant) propagate unwrapped.
        """
        last_cause: BaseException | None = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                return self._run_pipeline(command_cls, payload, caller, cascade_parent=None)
            except AdvisoryLockUnavailable as e:
                last_cause = e
                if attempt == MAX_ATTEMPTS:
                    raise TransientContention(attempts=attempt, last_cause=e) from e
                logger.warning(
                    "advisory-lock contention on attempt %d/%d for %s; retrying",
                    attempt,
                    MAX_ATTEMPTS,
                    command_cls.name(),
                )
                time.sleep(_jittered_backoff_seconds(attempt))
            except OperationalError as e:
                if not _is_serialization_failure(e):
                    raise
                last_cause = e
                if attempt == MAX_ATTEMPTS:
                    raise TransientContention(attempts=attempt, last_cause=e) from e
                logger.warning(
                    "serialization_failure on attempt %d/%d for %s; retrying",
                    attempt,
                    MAX_ATTEMPTS,
                    command_cls.name(),
                )
                time.sleep(_jittered_backoff_seconds(attempt))
        # Unreachable: every iteration either returns or raises.
        raise TransientContention(
            attempts=MAX_ATTEMPTS, last_cause=last_cause or RuntimeError("no last cause")
        )

    def _run_pipeline(
        self,
        command_cls: type[Command],
        payload: BaseModel,
        caller: Caller,
        cascade_parent: Command | None,
    ) -> Any:
        """Run one pipeline attempt. Cascade children share the parent's
        session + transaction; top-level dispatch opens its own session and
        sets per-transaction SERIALIZABLE isolation per ADR-0056.
        """
        if cascade_parent is not None:
            # Cascade child: reuse parent's session (parent commits or rolls back).
            session = cascade_parent._session  # noqa: SLF001
            command_id = cascade_parent._command_id  # noqa: SLF001
            assert session is not None and command_id is not None, (
                "cascade_parent has no dispatcher context -- _run_pipeline called "
                "for a cascade child outside of a top-level dispatch"
            )
            return self._run_steps(
                command_cls,
                payload,
                caller,
                session=session,
                command_id=command_id,
                skip_auth=True,
            )

        # Top-level: open session, set isolation, run, commit/rollback.
        session = self.session_factory()
        try:
            if session.bind is not None and session.bind.dialect.name == "postgresql":
                session.connection().execution_options(isolation_level="SERIALIZABLE")
            command_id = uuid.uuid4()
            try:
                result = self._run_steps(
                    command_cls,
                    payload,
                    caller,
                    session=session,
                    command_id=command_id,
                    skip_auth=False,
                )
                session.commit()
                return result
            except BaseException:
                session.rollback()
                raise
        finally:
            session.close()

    def _run_steps(
        self,
        command_cls: type[Command],
        payload: BaseModel,
        caller: Caller,
        *,
        session: Session,
        command_id: uuid.UUID,
        skip_auth: bool,
    ) -> Any:
        """The six-step pipeline body. Called both top-level and cascade-child."""
        command = command_cls()
        # Attach session + command_id + dispatcher + caller so cascade-invoke
        # (and the handler, if it needs them for cascade orchestration) can
        # reach them. Private-named per Python convention; consumers of the
        # Command surface should not touch these.
        command._session = session  # noqa: SLF001
        command._command_id = command_id  # noqa: SLF001
        command._caller = caller  # noqa: SLF001
        command._dispatcher = self  # noqa: SLF001

        # Step 1 — Authorization (ADR-0012). Skipped for cascade children per
        # ADR-0047 / ADR-0060: cascade inherits auth from the originating
        # user-facing command.
        if not skip_auth:
            predicate = command_cls.authorization
            if not predicate(caller, command_cls, payload, session):
                raise AuthorizationDenied(
                    f"caller {caller.id} not authorized for {command_cls.name()}"
                )

        # Step 2 — Lifecycle gate (ADR-0009). Resolve target if applicable;
        # for lifecycle-affecting commands, verify the declared transition is
        # permitted from the entity's current state.
        from_state: str | None = None
        target: Any = None
        if command_cls.transition_name is not None:
            target = command.resolve_target(session, payload)
            if target is not None:
                from_state = getattr(target, "state", None)
                state_machine = getattr(type(target), "state_machine", None)
                if state_machine is None:
                    raise LifecycleViolation(
                        f"{type(target).__name__} has no state_machine declared"
                    )
                permitted = state_machine.get(from_state, set())
                if command_cls.transition_name not in permitted:
                    raise LifecycleViolation(
                        f"transition {command_cls.transition_name!r} not permitted from "
                        f"state {from_state!r} on {type(target).__name__}"
                    )

        # Step 3 — Apply (handler mutation). Returns the entity that was
        # operated on (created or mutated); the history step uses this as
        # the capture target.
        target = command.handler(session, payload)
        # Make pending state visible to invariant queries.
        session.flush()

        # Step 4 — Invariants (ADR-0010 + ADR-0056). Per-invariant primitive
        # acquisition: advisory-lock-opt-in invariants try the lock first
        # (fast-fail signal lifted by the retry loop above); SERIALIZABLE
        # invariants rely on the per-transaction isolation set in
        # _run_pipeline.
        for invariant_cls in command_cls.invariants:
            if invariant_cls.primitive == "advisory_lock":
                key = invariant_cls.lock_key(target)
                if key is not None and not try_advisory_xact_lock(session, key):
                    raise AdvisoryLockUnavailable(key)
            if not invariant_cls.check(session, target):
                raise InvariantViolation(
                    f"invariant {invariant_cls.__name__} violated on {type(target).__name__}"
                )

        # Step 5 — History / capture (ADR-0008 / ADR-0013 / ADR-0052 /
        # ADR-0057). The capture record's variant is determined by the
        # target entity's declared history_pattern.
        record = self._build_capture_record(
            command_cls=command_cls,
            payload=payload,
            caller=caller,
            target=target,
            command_id=command_id,
            from_state=from_state,
        )
        if record is not None:
            self.sink.emit(record, session)

        # Step 6 — Commit happens at top-level only; cascade children
        # participate in the parent's transaction.
        return target

    def _build_capture_record(
        self,
        *,
        command_cls: type[Command],
        payload: BaseModel,
        caller: Caller,
        target: Any,
        command_id: uuid.UUID,
        from_state: str | None,
    ) -> HistoryRecord | None:
        """Construct the per-pattern HistoryRecord variant or return None for
        no-history entities. Pattern is read from `target.history_pattern`
        (class attr on the SQLAlchemy model).
        """
        history_pattern = getattr(type(target), "history_pattern", "none")
        if history_pattern == "none":
            return None
        common = {
            "id": uuid.uuid4(),
            "entity_type": type(target).__name__,
            "entity_id": target.id,
            "command_id": command_id,
            "command_name": command_cls.name(),
            "caller_id": caller.id,
            "at": datetime.now(UTC),
        }
        if history_pattern == "comprehensive":
            return ComprehensiveRecord(**common, snapshot=_snapshot_entity(target))
        if history_pattern == "lifecycle":
            if command_cls.transition_name is None:
                # Lifecycle-pattern entity touched by a non-lifecycle command:
                # no row written per ADR-0013 pattern-4 definition.
                return None
            return LifecycleRecord(
                **common,
                from_state=from_state,
                to_state=getattr(target, "state", ""),
                transition_name=command_cls.transition_name,
                state_context={},
            )
        if history_pattern == "audit_log":
            return AuditLogRecord(**common, payload_summary=payload.model_dump(mode="json"))
        raise ValueError(f"unknown history_pattern {history_pattern!r} on {type(target).__name__}")


def cascade_invoke(
    parent_command: Command,
    child_command_cls: type[Command],
    child_payload: BaseModel,
) -> Any:
    """Invoke a sub-command from inside a compound command's handler per
    ADR-0060. Runtime guard G1: child_command_cls MUST appear in
    type(parent_command).cascade -- otherwise CascadeViolation. The child
    runs auth-bypassed (cascade inherits auth from the parent's
    originating user-facing command per ADR-0047) inside the parent's
    transaction (the parent commits or rolls back for everyone).
    """
    parent_cls = type(parent_command)
    if child_command_cls not in parent_cls.cascade:
        raise CascadeViolation(parent_cls.name(), child_command_cls.name())

    # Reuse the dispatcher embedded on the parent's session-scoped context.
    dispatcher = parent_command._dispatcher  # noqa: SLF001
    caller = parent_command._caller  # noqa: SLF001
    assert dispatcher is not None and caller is not None, (
        "cascade_invoke called outside dispatcher context -- parent_command "
        "must be inside an in-flight dispatch (typically called from a handler)"
    )
    return dispatcher._run_pipeline(  # noqa: SLF001
        child_command_cls, child_payload, caller, cascade_parent=parent_command
    )
