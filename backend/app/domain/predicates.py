"""Authorization predicates for the Command pipeline (ADR-0047).

ADR-0047's per-command predicate table has two row types: explicit
per-command rows and class-rule clauses. The chain-level class rules --
`role >= admin` for admin-roster CRUD (Cluster 1), `role >= coordinator`
for the project-tracking clusters -- are uniform. This module encodes
them once as `require_role`, a factory producing the
`(caller, command_cls, payload, session) -> bool` callable the dispatcher
reads off `Command.authorization`.

Non-uniform predicates -- ADR-0040's parameterized grant/revoke authority,
the creator-only `edit_note` rule -- are deliberately NOT this module's
job: per ADR-0062 they are authored inline at their command. This module
covers only the linear-chain class rules.
"""

from collections.abc import Callable

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.framework.caller import Caller, Role, has_role_at_least
from app.framework.command import Command

# The shape the dispatcher's authorization step calls (ADR-0059 pipeline).
AuthPredicate = Callable[[Caller, type[Command], BaseModel, Session], bool]


def require_role(minimum: Role) -> AuthPredicate:
    """Return an authorization predicate admitting any caller who holds
    `minimum` or a higher role in ADR-0040's linear hierarchy
    (auditor < coordinator < admin < superadmin).

    The ADR-0047 Cluster 1 admin-roster CRUD class rule is
    `require_role(Role.ADMIN)` -- used verbatim by M1.2's five entities
    (Contract here; Employee / School / Contractor / User in 2.2b) and by
    every later cluster (`require_role(Role.COORDINATOR)`, ...).
    """

    def predicate(
        caller: Caller,
        command_cls: type[Command],
        payload: BaseModel,
        session: Session,
    ) -> bool:
        return has_role_at_least(caller, minimum)

    # A legible __name__ so a registry / introspection dump reads cleanly.
    predicate.__name__ = f"require_role_{minimum.value}"
    return predicate
