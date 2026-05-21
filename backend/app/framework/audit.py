"""Audit-metadata column mixin per ADR-0072.

The four `created_at` / `created_by` / `updated_at` / `updated_by` columns
every domain entity carries. They are a **dispatcher-maintained read
projection** over the authoritative who / what / when record in
`command_audit_log` and the per-entity history tables -- written uniformly
by the dispatcher's stamping step (ADR-0075), never by a handler.

`created_by` / `updated_by` are plain `UUID` columns with no FK, consistent
with `command_audit_log.caller_id`: the actor is always a `User` id, but the
column is a value, not a constrained reference.

The mixin lives in `app.framework` so the dispatcher can `isinstance`-check
a command's target to decide whether it carries audit columns. The engine
layer (`app.framework`) imports nothing from `app.adapters`; a declarative
mixin is a plain class -- it does not need `Base` -- so it sits here cleanly.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


class AuditMetadataMixin:
    """The four audit-metadata columns (ADR-0072), mixed into every domain
    entity alongside `Base`.

    The dispatcher stamps `created_*` on the creating command and `updated_*`
    on every command -- so at creation `created_* == updated_*`, and every
    later mutating command refreshes `updated_*` only (ADR-0075). All four are
    `NOT NULL`: every row has a creation moment, and `updated_*` is always
    populated from creation onward.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_by: Mapped[UUID] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_by: Mapped[UUID] = mapped_column(nullable=False)
