"""Fake commands for dispatcher smoke tests.

Each command exercises one path through the M0.3 pipeline; the smoke tests
assert the path's pipeline-step outcomes.
"""

from typing import Any, ClassVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.framework.caller import Caller
from app.framework.command import Command
from tests.fixtures.smoketest.entities import (
    SmokeAuditEntity,
    SmokeEntity,
    SmokeLifecycleEntity,
)
from tests.fixtures.smoketest.invariants import ValueIsPositive


def always_allow(
    caller: Caller, command_cls: type[Command], payload: BaseModel, session: Session
) -> bool:
    return True


def never_allow(
    caller: Caller, command_cls: type[Command], payload: BaseModel, session: Session
) -> bool:
    return False


# ---- Comprehensive-pattern commands (target SmokeEntity) ----


class CreateSmoke(Command):
    target_entity = SmokeEntity
    authorization = always_allow
    invariants: ClassVar[list[type]] = [ValueIsPositive]

    class Payload(BaseModel):
        value: int
        note: str = ""

    def handler(self, session: Session, payload: BaseModel) -> SmokeEntity:
        assert isinstance(payload, CreateSmoke.Payload)
        entity = SmokeEntity(value=payload.value, note=payload.note)
        session.add(entity)
        return entity


class EditSmoke(Command):
    target_entity = SmokeEntity
    authorization = always_allow
    invariants: ClassVar[list[type]] = [ValueIsPositive]

    class Payload(BaseModel):
        entity_id: UUID
        value: int

    def resolve_target(self, session: Session, payload: BaseModel) -> Any:
        assert isinstance(payload, EditSmoke.Payload)
        return session.get(SmokeEntity, payload.entity_id)

    def handler(self, session: Session, payload: BaseModel) -> SmokeEntity:
        assert isinstance(payload, EditSmoke.Payload)
        entity = session.get(SmokeEntity, payload.entity_id)
        assert entity is not None
        entity.value = payload.value
        return entity


class EditSmokeNoAuth(Command):
    """Auth-denied variant for testing the rejection path."""

    target_entity = SmokeEntity
    authorization = never_allow
    invariants: ClassVar[list[type]] = []

    class Payload(BaseModel):
        entity_id: UUID
        value: int

    def handler(self, session: Session, payload: BaseModel) -> SmokeEntity:
        assert isinstance(payload, EditSmokeNoAuth.Payload)
        entity = session.get(SmokeEntity, payload.entity_id)
        assert entity is not None
        entity.value = payload.value
        return entity


# ---- Lifecycle-pattern commands (target SmokeLifecycleEntity) ----


class CreateSmokeLifecycle(Command):
    target_entity = SmokeLifecycleEntity
    transition_name = "create"
    authorization = always_allow

    class Payload(BaseModel):
        note: str = ""

    def handler(self, session: Session, payload: BaseModel) -> SmokeLifecycleEntity:
        assert isinstance(payload, CreateSmokeLifecycle.Payload)
        entity = SmokeLifecycleEntity(note=payload.note, state="open")
        session.add(entity)
        return entity


class CloseSmokeLifecycle(Command):
    target_entity = SmokeLifecycleEntity
    transition_name = "close"
    authorization = always_allow

    class Payload(BaseModel):
        entity_id: UUID

    def resolve_target(self, session: Session, payload: BaseModel) -> Any:
        assert isinstance(payload, CloseSmokeLifecycle.Payload)
        return session.get(SmokeLifecycleEntity, payload.entity_id)

    def handler(self, session: Session, payload: BaseModel) -> SmokeLifecycleEntity:
        assert isinstance(payload, CloseSmokeLifecycle.Payload)
        entity = session.get(SmokeLifecycleEntity, payload.entity_id)
        assert entity is not None
        entity.state = "closed"
        return entity


class EditSmokeLifecycleNote(Command):
    """Non-lifecycle command on a lifecycle-pattern entity. Per ADR-0013
    pattern-4 definition, no history row is written.
    """

    target_entity = SmokeLifecycleEntity
    transition_name = None
    authorization = always_allow

    class Payload(BaseModel):
        entity_id: UUID
        note: str

    def handler(self, session: Session, payload: BaseModel) -> SmokeLifecycleEntity:
        assert isinstance(payload, EditSmokeLifecycleNote.Payload)
        entity = session.get(SmokeLifecycleEntity, payload.entity_id)
        assert entity is not None
        entity.note = payload.note
        return entity


# ---- Audit-log-pattern commands (target SmokeAuditEntity) ----


class CreateSmokeAudit(Command):
    target_entity = SmokeAuditEntity
    authorization = always_allow

    class Payload(BaseModel):
        label: str = ""

    def handler(self, session: Session, payload: BaseModel) -> SmokeAuditEntity:
        assert isinstance(payload, CreateSmokeAudit.Payload)
        entity = SmokeAuditEntity(label=payload.label)
        session.add(entity)
        return entity
