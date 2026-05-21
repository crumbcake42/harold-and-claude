"""Production capture sink -- the SQLAlchemy-backed `CaptureSink` adapter.

The `CaptureSink` port + the typed record variants live in
`app.framework.capture`; this module is the concrete adapter that INSERTs a
capture record into the per-entity history tables (comprehensive / lifecycle)
or the shared command_audit_log table, in the same transaction as the entity
mutation per ADR-0008 + ADR-0057.
"""

from sqlalchemy.orm import Session

from app.framework.capture import (
    AuditLogRecord,
    ComprehensiveRecord,
    HistoryRecord,
    LifecycleRecord,
)


class SqlAlchemyCaptureSink:
    """Production sink: INSERTs the record into the appropriate history table
    (per-entity for comprehensive / lifecycle; shared command_audit_log for
    audit-log entities) using the dispatcher's current session.

    Atomicity per ADR-0008 + ADR-0057: the sink calls session.add() only;
    the dispatcher's top-level commit (or rollback on any pipeline rejection)
    decides whether the row persists.

    Constructor injection of the registries: production wires
    COMPREHENSIVE_HISTORY + LIFECYCLE_HISTORY + CommandAuditLog from
    app.adapters.history; integration tests can wire smoke-only maps
    targeting smoke history tables on SmokeBase.
    """

    def __init__(
        self,
        comprehensive: dict[str, type],
        lifecycle: dict[str, type],
        audit_log_model: type,
    ) -> None:
        self._comprehensive = comprehensive
        self._lifecycle = lifecycle
        self._audit_log_model = audit_log_model

    def emit(self, record: HistoryRecord, session: Session) -> None:
        if isinstance(record, ComprehensiveRecord):
            model = self._comprehensive.get(record.entity_type)
            if model is None:
                raise KeyError(
                    f"no comprehensive-history model registered for entity_type "
                    f"{record.entity_type!r}"
                )
            session.add(
                model(
                    id=record.id,
                    entity_id=record.entity_id,
                    command_id=record.command_id,
                    command_name=record.command_name,
                    caller_id=record.caller_id,
                    at=record.at,
                    snapshot=record.snapshot,
                )
            )
            return
        if isinstance(record, LifecycleRecord):
            model = self._lifecycle.get(record.entity_type)
            if model is None:
                raise KeyError(
                    f"no lifecycle-history model registered for entity_type "
                    f"{record.entity_type!r}"
                )
            session.add(
                model(
                    id=record.id,
                    entity_id=record.entity_id,
                    command_id=record.command_id,
                    command_name=record.command_name,
                    caller_id=record.caller_id,
                    at=record.at,
                    from_state=record.from_state,
                    to_state=record.to_state,
                    transition_name=record.transition_name,
                    state_context=record.state_context,
                )
            )
            return
        if isinstance(record, AuditLogRecord):
            session.add(
                self._audit_log_model(
                    id=record.id,
                    entity_type=record.entity_type,
                    entity_id=record.entity_id,
                    command_id=record.command_id,
                    command_name=record.command_name,
                    caller_id=record.caller_id,
                    at=record.at,
                    payload_summary=record.payload_summary,
                )
            )
            return
        raise TypeError(f"unknown HistoryRecord variant: {type(record).__name__}")
