"""Tests for the ADR-0047 chain-level authorization predicate factory."""

from uuid import uuid4

import pytest
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.engine.caller import Caller, Role
from app.engine.predicates import require_role
from tests.fixtures.smoketest.commands import CreateSmoke


# The predicate ignores command_cls / payload / session -- these are typed
# stand-ins so the call site stays pyright-clean.
class _EmptyPayload(BaseModel):
    pass


_PAYLOAD = _EmptyPayload()
_SESSION = Session()


def _caller(*roles: Role) -> Caller:
    return Caller(id=uuid4(), username="test", roles=frozenset(roles))


@pytest.mark.parametrize(
    ("held", "allowed"),
    [
        (Role.SUPERADMIN, True),
        (Role.ADMIN, True),
        (Role.COORDINATOR, False),
        (Role.AUDITOR, False),
    ],
)
def test_require_admin_admits_admin_and_above(held: Role, allowed: bool) -> None:
    predicate = require_role(Role.ADMIN)
    assert predicate(_caller(held), CreateSmoke, _PAYLOAD, _SESSION) is allowed


def test_require_role_admits_on_any_held_role() -> None:
    # Union semantics per ADR-0040: a multi-role caller passes if ANY role clears.
    predicate = require_role(Role.ADMIN)
    assert predicate(_caller(Role.AUDITOR, Role.ADMIN), CreateSmoke, _PAYLOAD, _SESSION)


def test_require_role_rejects_empty_roles() -> None:
    predicate = require_role(Role.ADMIN)
    assert predicate(_caller(), CreateSmoke, _PAYLOAD, _SESSION) is False


def test_require_coordinator_chain() -> None:
    predicate = require_role(Role.COORDINATOR)
    assert predicate(_caller(Role.ADMIN), CreateSmoke, _PAYLOAD, _SESSION) is True
    assert predicate(_caller(Role.AUDITOR), CreateSmoke, _PAYLOAD, _SESSION) is False


def test_predicate_name_is_legible() -> None:
    assert require_role(Role.ADMIN).__name__ == "require_role_admin"
