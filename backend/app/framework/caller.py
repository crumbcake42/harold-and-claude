"""Caller — the concrete actor passed through the dispatcher pipeline.

Resolves ADR-0059's "Caller concrete shape" carry-forward. The dispatcher
(app.framework.dispatcher) and ADR-0047 authorization predicates consume the
concrete Caller produced by app.framework.auth.current_user; the Protocol stub
that previously lived in app.framework.command is removed in this commit.

Role catalog per ADR-0040: superadmin > admin > coordinator > auditor (linear
hierarchy with conservative grant authority). The hierarchy is an emergent
semantic property of the per-(role, command) permission table; has_role_at_least
encodes the chain for class-rule predicates ("role >= coordinator", etc.).
Per-target-role predicates (grant_user_role / revoke_user_role) inline their
own logic per ADR-0047 non-uniform rows.
"""

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Role(StrEnum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    AUDITOR = "auditor"


# Linear-hierarchy ordering per ADR-0040. Higher index = more authority.
# Keep adjacent to the Role enum so additions force a conscious chain choice.
_CHAIN_ORDER: tuple[Role, ...] = (
    Role.AUDITOR,
    Role.COORDINATOR,
    Role.ADMIN,
    Role.SUPERADMIN,
)
_CHAIN_RANK: dict[Role, int] = {role: idx for idx, role in enumerate(_CHAIN_ORDER)}


class Caller(BaseModel):
    """The actor on whose behalf a command runs.

    Constructed by app.framework.auth.current_user from the session lookup.
    Passed to Dispatcher.dispatch and consumed by ADR-0047 authorization
    predicates. Frozen so callers cannot be mutated mid-pipeline.
    """

    model_config = ConfigDict(frozen=True)

    id: UUID
    username: str
    roles: frozenset[Role]


def has_role_at_least(caller: Caller, minimum: Role) -> bool:
    """True if the caller holds any role at or above `minimum` in the linear
    hierarchy (ADR-0040). Use for class-rule predicates ("role >= coordinator").
    Non-uniform predicates (grant_user_role parameterized authority) should
    read caller.roles directly per ADR-0047.
    """
    threshold = _CHAIN_RANK[minimum]
    return any(_CHAIN_RANK[role] >= threshold for role in caller.roles)
