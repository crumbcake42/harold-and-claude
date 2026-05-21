"""Capture-sink interface for the command pipeline's history step.

Per ADR-0008 + ADR-0013 + ADR-0052: a successful command on a history-carrying
entity writes a history row atomically with the entity mutation; a successful
command on an audit-log entity writes a command_audit_log row in-txn per
ADR-0057. The dispatcher's history step does not know about tables -- it
constructs a typed HistoryRecord and calls sink.emit(record). The sink
implementation owns table-specific INSERT machinery.

This module holds the `CaptureSink` port, the typed record variants, and the
in-memory test stubs. The concrete SQLAlchemy-backed sink that INSERTs into
the per-entity history tables and the shared command_audit_log lives in
`app.adapters.capture`.
"""

from datetime import datetime
from typing import Literal, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session


class _BaseRecord(BaseModel):
    """Common metadata fields per ADR-0052.

    All history-table rows AND command_audit_log rows carry these columns.
    Frozen by design -- a capture record represents a moment-in-time event;
    mutation after construction would corrupt the audit story.
    """

    model_config = ConfigDict(frozen=True)

    id: UUID
    entity_type: str
    entity_id: UUID
    command_id: UUID
    command_name: str
    caller_id: UUID
    at: datetime


class ComprehensiveRecord(_BaseRecord):
    """History record for entities under the comprehensive-capture pattern
    (Document / WA / RFA per ADR-0052). One row per command on the entity.
    """

    kind: Literal["comprehensive"] = "comprehensive"
    snapshot: dict


class LifecycleRecord(_BaseRecord):
    """History record for entities under the lifecycle-capture pattern
    (Project / Sample Batch / Deliverable / EmployeeRole / WA Code /
    ContractorEngagement per ADR-0052). One row per lifecycle-affecting
    command on the entity (non-lifecycle commands produce no record per
    ADR-0013).
    """

    kind: Literal["lifecycle"] = "lifecycle"
    from_state: str | None
    to_state: str
    transition_name: str
    state_context: dict


class AuditLogRecord(_BaseRecord):
    """Audit-log row for entities under the audit-log pattern (Employee / User
    / Time Entry / Contractor / DepFiling / Contract / WABundle per ADR-0052).
    Polymorphic on (entity_type, entity_id); written in-txn per ADR-0057.
    """

    kind: Literal["audit_log"] = "audit_log"
    payload_summary: dict


HistoryRecord = ComprehensiveRecord | LifecycleRecord | AuditLogRecord


class CaptureSink(Protocol):
    """Interface the dispatcher's history step calls to persist a capture record.

    The dispatcher passes its current session at emit time so the sink can
    INSERT the history row in the same transaction as the entity mutation
    per ADR-0008 + ADR-0057. The session argument is part of the contract
    even for sinks that ignore it (InMemorySink, NullSink) -- callers always
    have a session, and forcing the parameter prevents accidental
    session-less wiring.
    """

    def emit(self, record: HistoryRecord, session: Session) -> None: ...


class InMemorySink:
    """Append-to-list sink for tests. Inspect `records` after a dispatch to
    assert what was captured. Ignores the session argument.
    """

    def __init__(self) -> None:
        self.records: list[HistoryRecord] = []

    def emit(self, record: HistoryRecord, session: Session) -> None:
        self.records.append(record)


class NullSink:
    """No-op sink for tests that exercise other pipeline aspects."""

    def emit(self, record: HistoryRecord, session: Session) -> None:
        return None
