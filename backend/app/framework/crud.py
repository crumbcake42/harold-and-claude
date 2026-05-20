"""Shared authoring helpers for admin-roster CRUD commands.

M1.2's admin-CRUD authoring shape is **hand-authored Command classes over
shared helpers** (not a generalized class factory): the five roster
entities are not uniform enough -- User hashes a password, Contract carries
a JSONB collection, School's delete policy differs -- for a factory to pay
off without escape-hatch parameters. This module holds the genuinely
repeated mechanics so each Command class stays thin and idiomatic
(ADR-0059) while the non-uniform parts stay explicit at the command.

Three helpers, reused across every roster entity's edit / delete commands:

  resolve_for_command  -- get-by-id, raising EntityNotFound on a missing or
                          soft-deleted row (so edit / delete reject cleanly).
  apply_scalar_fields  -- copy a named set of payload fields onto an entity.
                          Scalar only: JSONB-collection columns are handled
                          explicitly at the command (they need conversion
                          out of their Pydantic sub-models).
  soft_delete          -- stamp deleted_at for the soft-delete policy.
"""

from collections.abc import Iterable
from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.framework.exceptions import EntityNotFound


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
