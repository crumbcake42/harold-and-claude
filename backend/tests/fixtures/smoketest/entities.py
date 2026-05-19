"""Fake entities + smoke history tables for dispatcher and capture-sink tests.

Three entities exercise the three history patterns the dispatcher distinguishes
(comprehensive / lifecycle / audit_log). Three corresponding history tables
(reusing the production mixins from app.framework.history) let the integration
test wire SqlAlchemyCaptureSink against SmokeBase tables in isolation from the
production registries.
"""

from uuid import UUID, uuid4

from sqlalchemy import Index, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.framework.adapter import json_column
from app.framework.history import (
    CommonHistoryMixin,
    ComprehensiveHistoryMixin,
    LifecycleHistoryMixin,
)


class SmokeBase(DeclarativeBase):
    """Independent declarative base so smoke-test tables do not collide with
    domain-entity tables (when those land in M1+).
    """


class SmokeEntity(SmokeBase):
    """Comprehensive-pattern smoke entity. Every successful command on this
    entity produces a ComprehensiveRecord with a full state snapshot per
    ADR-0052.
    """

    __tablename__ = "smoke_entity"
    history_pattern = "comprehensive"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    value: Mapped[int]
    note: Mapped[str] = mapped_column(default="")


class SmokeLifecycleEntity(SmokeBase):
    """Lifecycle-pattern smoke entity. Only lifecycle-affecting commands
    produce records per ADR-0013 pattern-4 definition; non-lifecycle commands
    succeed silently (no history row).
    """

    __tablename__ = "smoke_lifecycle_entity"
    history_pattern = "lifecycle"
    state_machine: dict[str | None, set[str]] = {
        None: {"create"},
        "open": {"close"},
        "closed": set(),
    }

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    note: Mapped[str] = mapped_column(default="")
    state: Mapped[str] = mapped_column(default="open")


class SmokeAuditEntity(SmokeBase):
    """Audit-log-pattern smoke entity. Every successful command writes a row
    to the shared command_audit_log per ADR-0052; the row carries the
    command's payload_summary, not an entity snapshot.
    """

    __tablename__ = "smoke_audit_entity"
    history_pattern = "audit_log"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    label: Mapped[str] = mapped_column(default="")


# ---- Smoke history tables (SmokeBase-bound; reuse production mixins) ----


class SmokeComprehensiveHistory(SmokeBase, ComprehensiveHistoryMixin):
    __tablename__ = "smoke_comprehensive_history"
    __table_args__ = (Index("ix_smoke_comprehensive_history_entity_id_at", "entity_id", "at"),)


class SmokeLifecycleHistory(SmokeBase, LifecycleHistoryMixin):
    __tablename__ = "smoke_lifecycle_history"
    __table_args__ = (Index("ix_smoke_lifecycle_history_entity_id_at", "entity_id", "at"),)


class SmokeAuditLog(SmokeBase, CommonHistoryMixin):
    """Smoke mirror of CommandAuditLog. Same shape, separate table so the
    integration test can read its rows without scanning production tables.
    """

    __tablename__ = "smoke_audit_log"
    __table_args__ = (
        Index("ix_smoke_audit_log_type_entity_at", "entity_type", "entity_id", "at"),
        Index("ix_smoke_audit_log_command_id", "command_id"),
    )

    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    payload_summary: Mapped[dict] = mapped_column(json_column(), nullable=False)
