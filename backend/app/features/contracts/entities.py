"""Contract entity (ADR-0043 / ADR-0044 / ADR-0045).

A Contract is the contractual basis a project is billed against: it
defines a default flat fee per WA code type and scopes employee billing
rates. M1.2 builds Contract first (Step 2.2a) -- the most non-uniform of
the five flat-roster entities (JSONB code_flat_fee_schedule, derived
validity) -- to prove the admin-CRUD abstractions against the hard case.

Schema notes:
  - contract_number is the uniqueness-constrained natural key (mandatory).
  - name is optional; when null the display label derives as 'C' + the
    last 5 chars of contract_number (ADR-0043 -- a derived label, not a
    stored default; nothing is ever written to name).
  - code_flat_fee_schedule is a non-temporal JSONB collection of
    {code_type, fee} pairs (ADR-0043), via json_column() -- JSONB on
    Postgres, portable JSON on SQLite, through the M0.4 adapter boundary.
  - validity is derived from (start_date, end_date?) + clock (ADR-0043) --
    no state machine, never stored.

History: command_audit_log (audit_log pattern) -- Contract is one of
ADR-0052's 7 audit-log entities.

Audit metadata: the four created_*/updated_* columns via AuditMetadataMixin
(ADR-0072) -- a dispatcher-maintained read projection, stamped by the
pipeline, never by a handler.

Delete: soft delete (deleted_at) per ADR-0043.
"""

from datetime import UTC, date, datetime
from typing import ClassVar
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.adapters.db import Base
from app.adapters.postgres import json_column
from app.engine.audit import AuditMetadataMixin


class Contract(Base, AuditMetadataMixin):
    __tablename__ = "contract"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    contract_number: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Non-temporal collection of {code_type, fee} dicts. fee round-trips as a
    # JSON string (the engine json_serializer coerces Decimal via str); the
    # API models re-coerce it back to Decimal. A code type absent from the
    # schedule resolves to unpriced per ADR-0045 -- no entry, no blocker.
    code_flat_fee_schedule: Mapped[list[dict]] = mapped_column(
        json_column(), nullable=False, default=list
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    history_pattern: ClassVar[str] = "audit_log"

    @property
    def validity(self) -> str:
        """Derived status per ADR-0043: `pending` (today before start_date),
        `active` (within term; an open end_date means +infinity), `expired`
        (today after end_date). Computed from dates + clock, never stored.
        """
        today = datetime.now(UTC).date()
        if today < self.start_date:
            return "pending"
        if self.end_date is not None and today > self.end_date:
            return "expired"
        return "active"

    @property
    def display_label(self) -> str:
        """ADR-0043 derived label: `name` when set, else 'C' + the last 5
        characters of contract_number.
        """
        return self.name if self.name else f"C{self.contract_number[-5:]}"
