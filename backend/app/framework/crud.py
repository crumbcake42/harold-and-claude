"""Shared authoring helpers for admin-roster CRUD commands.

M1.2's admin-CRUD authoring shape is **hand-authored Command classes over
shared helpers** (not a generalized class factory): the five roster
entities are not uniform enough -- User hashes a password, Contract carries
a JSONB collection, School's delete policy differs -- for a factory to pay
off without escape-hatch parameters. This module holds the genuinely
repeated mechanics so each Command class stays thin and idiomatic
(ADR-0059) while the non-uniform parts stay explicit at the command.

Four helpers, reused across the roster entities' CRUD commands:

  resolve_for_command  -- get-by-id, raising EntityNotFound on a missing or
                          soft-deleted row (so edit / delete reject cleanly).
  apply_scalar_fields  -- copy a named set of payload fields onto an entity.
                          Scalar only: JSONB-collection columns are handled
                          explicitly at the command (they need conversion
                          out of their Pydantic sub-models).
  soft_delete          -- stamp deleted_at for the soft-delete policy.
  require_unique       -- the natural-key uniqueness pre-check (ADR-0071),
                          run in create / edit handlers before flush.
"""

from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.framework.exceptions import EntityNotFound, InvariantViolation


def resolve_for_command[T](session: Session, model: type[T], entity_id: UUID) -> T:
    """Return the live entity of `model` with `entity_id`, or raise
    EntityNotFound. A row whose `deleted_at` is set counts as not found --
    soft-deleted entities are not editable / re-deletable. Models with no
    `deleted_at` attribute (e.g. School, no-soft-delete) are never treated
    as deleted.
    """
    entity = session.get(model, entity_id)
    if entity is None or getattr(entity, "deleted_at", None) is not None:
        raise EntityNotFound(f"{model.__name__} {entity_id} not found")
    return entity


def apply_scalar_fields(
    entity: object, payload: BaseModel, fields: Iterable[str]
) -> None:
    """Copy each named field from `payload` onto `entity`. Used by create
    (after constructing a blank entity) and edit (full-form replacement of
    the editable fields). Scalar fields only -- a JSONB-collection column
    is set explicitly at the command after converting its Pydantic
    sub-models to plain dicts.
    """
    for name in fields:
        setattr(entity, name, getattr(payload, name))


def soft_delete(entity: object) -> None:
    """Apply the soft-delete policy: stamp `deleted_at` with the current
    UTC time. The row is retained; history / audit references stay valid.
    """
    setattr(entity, "deleted_at", datetime.now(UTC))  # noqa: B010


def require_unique(
    session: Session,
    model: type[Any],
    field: str,
    value: object,
    *,
    exclude_id: UUID | None = None,
) -> None:
    """Natural-key uniqueness pre-check (ADR-0071): raise InvariantViolation
    if a live row of `model` already holds `value` in `field`. Run inside a
    create / edit handler *before* session.add / flush -- the pipeline
    flushes before its invariant step, so the DB UNIQUE constraint would
    otherwise fire a raw IntegrityError first. `exclude_id` skips the
    entity's own row so an edit can keep its current value.

    The DB UNIQUE constraint stays as the hard backstop: a violation that
    slips past this check under a concurrent race surfaces as
    IntegrityError -> 409. Extracted from Contract's private
    `_require_unique_number` when Employee's `username` became the second
    uniqueness consumer.
    """
    field_column = getattr(model, field)
    query = session.query(model.id).filter(field_column == value)
    if exclude_id is not None:
        query = query.filter(model.id != exclude_id)
    if query.first() is not None:
        raise InvariantViolation(f"{model.__name__}.{field} {value!r} already exists")
