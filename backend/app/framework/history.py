"""Per-entity history tables + shared command_audit_log per ADR-0052.

Topology (ADR-0052 § Consequences):
  - 3 comprehensive history tables (Document / WA / RFA): one row per command,
    carries a full state snapshot.
  - 6 lifecycle history tables (Project / Sample Batch / Deliverable /
    EmployeeRole / WA Code / ContractorEngagement): one row per
    lifecycle-affecting command, carries from_state / to_state /
    transition_name / state_context.
  - 1 shared command_audit_log for the 7 audit-log entities (Employee / User /
    Time Entry / Contractor / DepFiling / Contract / WABundle):
    polymorphic (entity_type, entity_id); carries payload_summary; written
    in-txn with the entity mutation per ADR-0057.

Generator-shape decision (M0.3 / Step 1.3b, no ADR):
  Mixin-based explicit declarative classes over (a) fully-explicit-no-mixin
  and (b) dynamic factory. Each table is a grep-able class with a stable
  pyright type; column changes propagate via the two mixins; Alembic
  autogenerate sees each model as a normal declarative class. The factory
  alternative would collapse pyright type information to a generic class
  and obscure class-level introspection; fully-explicit-no-mixin would
  repeat the 7 common columns nine times. The mixin path is the natural
  middle.

FK timing (M0.3 / Step 1.3b):
  Per-entity history tables hold `entity_id` as a plain UUID column with
  no FK constraint at M0.3 -- the referenced entity tables don't exist
  yet. Each M1+ entity migration adds the FK alongside its entity table.
  data-model.md § Common metadata names the FK direction (history.entity_id
  -> entity.id); honoring it requires the entity table to exist first.

Column shape (matches the HistoryRecord variants in app.framework.capture):
  Common metadata: id, entity_id, command_id, command_name, caller_id, at.
  Comprehensive adds: snapshot.
  Lifecycle adds: from_state (nullable), to_state, transition_name,
    state_context.
  command_audit_log adds: entity_type, payload_summary.

data-model.md § Common metadata names two additional columns -- `sequence_no`
(gap-free per-entity ordering) and `command_payload` (full request payload) --
that are not carried by the 1.3a HistoryRecord variants. Deferred as additive
M1+ migrations if/when a consumer needs them; gap-free sequencing in particular
requires either a per-entity advisory lock or a serial-per-entity scheme that
the dispatcher does not currently provide.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.framework.adapter import json_column
from app.framework.db import Base


class CommonHistoryMixin:
    """The common-metadata columns every history row carries per ADR-0052
    § Consequences. Mixed into the two pattern mixins below (and used
    directly by CommandAuditLog) so the column list lives in one place.
    """

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    command_id: Mapped[UUID] = mapped_column(nullable=False)
    command_name: Mapped[str] = mapped_column(String, nullable=False)
    caller_id: Mapped[UUID] = mapped_column(nullable=False)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ComprehensiveHistoryMixin(CommonHistoryMixin):
    """Common columns + a full state snapshot per ADR-0052 § S2.
    Each concrete class declares __tablename__ + the (entity_id, at DESC)
    index in __table_args__.
    """

    snapshot: Mapped[dict] = mapped_column(json_column(), nullable=False)


class LifecycleHistoryMixin(CommonHistoryMixin):
    """Common columns + lifecycle-transition columns per ADR-0052 § S3.
    from_state is nullable (creation transitions have no prior state).
    """

    from_state: Mapped[str | None] = mapped_column(String, nullable=True)
    to_state: Mapped[str] = mapped_column(String, nullable=False)
    transition_name: Mapped[str] = mapped_column(String, nullable=False)
    state_context: Mapped[dict] = mapped_column(json_column(), nullable=False)


# ---- Comprehensive history tables (3) ----


class DocumentHistory(Base, ComprehensiveHistoryMixin):
    __tablename__ = "document_history"
    __table_args__ = (Index("ix_document_history_entity_id_at", "entity_id", "at"),)


class WAHistory(Base, ComprehensiveHistoryMixin):
    __tablename__ = "wa_history"
    __table_args__ = (Index("ix_wa_history_entity_id_at", "entity_id", "at"),)


class RFAHistory(Base, ComprehensiveHistoryMixin):
    __tablename__ = "rfa_history"
    __table_args__ = (Index("ix_rfa_history_entity_id_at", "entity_id", "at"),)


# ---- Lifecycle history tables (6) ----


class ProjectHistory(Base, LifecycleHistoryMixin):
    __tablename__ = "project_history"
    __table_args__ = (Index("ix_project_history_entity_id_at", "entity_id", "at"),)


class SampleBatchHistory(Base, LifecycleHistoryMixin):
    __tablename__ = "sample_batch_history"
    __table_args__ = (Index("ix_sample_batch_history_entity_id_at", "entity_id", "at"),)


class DeliverableHistory(Base, LifecycleHistoryMixin):
    __tablename__ = "deliverable_history"
    __table_args__ = (Index("ix_deliverable_history_entity_id_at", "entity_id", "at"),)


class EmployeeRoleHistory(Base, LifecycleHistoryMixin):
    __tablename__ = "employee_role_history"
    __table_args__ = (Index("ix_employee_role_history_entity_id_at", "entity_id", "at"),)


class WACodeHistory(Base, LifecycleHistoryMixin):
    __tablename__ = "wa_code_history"
    __table_args__ = (Index("ix_wa_code_history_entity_id_at", "entity_id", "at"),)


class ContractorEngagementHistory(Base, LifecycleHistoryMixin):
    __tablename__ = "contractor_engagement_history"
    __table_args__ = (
        Index("ix_contractor_engagement_history_entity_id_at", "entity_id", "at"),
    )


# ---- Shared audit-log table ----


class CommandAuditLog(Base, CommonHistoryMixin):
    """Polymorphic (entity_type, entity_id) audit log per ADR-0052 § Audit-log
    table. Used by the 7 audit-log entities (Employee, User, Time Entry,
    Contractor, DepFiling, Contract, WABundle). No DB-level FK on entity_id
    -- the referent's type is named by entity_type rather than known to the
    schema.
    """

    __tablename__ = "command_audit_log"
    __table_args__ = (
        Index("ix_command_audit_log_type_entity_at", "entity_type", "entity_id", "at"),
        Index("ix_command_audit_log_command_id", "command_id"),
    )

    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    payload_summary: Mapped[dict] = mapped_column(json_column(), nullable=False)


# ---- Registries (sink consumes these to route by entity name) ----

COMPREHENSIVE_HISTORY: dict[str, type[ComprehensiveHistoryMixin]] = {
    "Document": DocumentHistory,
    "WA": WAHistory,
    "RFA": RFAHistory,
}

LIFECYCLE_HISTORY: dict[str, type[LifecycleHistoryMixin]] = {
    "Project": ProjectHistory,
    "SampleBatch": SampleBatchHistory,
    "Deliverable": DeliverableHistory,
    "EmployeeRole": EmployeeRoleHistory,
    "WACode": WACodeHistory,
    "ContractorEngagement": ContractorEngagementHistory,
}
