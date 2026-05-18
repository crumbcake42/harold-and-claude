"""Fake entities for dispatcher smoke tests.

Two entities exercise the two history patterns 1.3a needs to verify
(comprehensive + lifecycle). The third pattern (audit_log) reuses the
same code path as comprehensive in 1.3a (record-construction differs;
sink dispatch is identical) and lands in 1.3b alongside the real table.
"""

from uuid import UUID, uuid4

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
    # None as the from-state for creation commands; the dispatcher skips the
    # gate when resolve_target returns None, so this declaration is for
    # documentation -- the from_state on the lifecycle record will be None.
    state_machine: dict[str | None, set[str]] = {
        None: {"create"},
        "open": {"close"},
        "closed": set(),
    }

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    note: Mapped[str] = mapped_column(default="")
    state: Mapped[str] = mapped_column(default="open")
