"""Contract admin-CRUD commands (ADR-0043/0044/0045, ADR-0047 Cluster 1).

create / edit / delete_contract -- the first ADR-0047 Cluster 1 predicate
landing in M1+ code, and the first production write-path domain commands.
All three are `role >= admin` per the Cluster 1 class rule (Contract is
admin-roster CRUD in character; the class rule's entity set extends from
{Employee, School, Contractor, User} to include Contract, hoisted into
M1.2 after ADR-0047 was written).

Authoring shape: hand-authored Command classes over the shared helpers in
`app.framework.crud` (the M1.2 admin-CRUD authoring decision). The
non-uniform part -- Contract's JSONB `code_flat_fee_schedule`, whose
Pydantic sub-models must be converted to plain dicts before they hit the
JSON column -- stays explicit here rather than disappearing into a
factory parameter.

Natural-key uniqueness note: `contract_number` is checked in the handler,
*before* session.add/flush, via the shared `require_unique` helper
(ADR-0071). It cannot be a dispatcher Invariant -- the pipeline flushes
after the handler but before its invariant step, so the DB UNIQUE
constraint would fire at flush before any Invariant could run. The handler
pre-check yields a clean InvariantViolation; the DB UNIQUE constraint stays
as the hard backstop against a concurrent race.
"""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.features.contracts.entities import Contract
from app.framework.caller import Role
from app.framework.command import Command, register
from app.framework.crud import (
    apply_scalar_fields,
    require_unique,
    resolve_for_command,
    soft_delete,
)
from app.framework.predicates import require_role

# Scalar (non-JSONB) columns copied straight from payload to entity by both
# create and edit. code_flat_fee_schedule is handled explicitly -- see below.
_SCALAR_FIELDS = ("contract_number", "name", "start_date", "end_date")


class CodeFlatFee(BaseModel):
    """One {code_type, fee} entry in a Contract's flat-fee schedule."""

    code_type: str
    fee: Decimal


def _schedule_to_json(items: list[CodeFlatFee]) -> list[dict]:
    """Convert the payload's Pydantic sub-models to plain JSON-able dicts
    for the JSONB column. mode="json" renders Decimal as a string, which
    the engine's json_serializer would do anyway -- doing it here keeps
    the stored shape explicit.
    """
    return [item.model_dump(mode="json") for item in items]


class CreateContract(Command):
    target_entity = Contract
    authorization = require_role(Role.ADMIN)
    creates = True  # dispatcher stamps created_* on this command (ADR-0075)

    class Payload(BaseModel):
        contract_number: str
        name: str | None = None
        start_date: date
        end_date: date | None = None
        code_flat_fee_schedule: list[CodeFlatFee] = Field(default_factory=list)

    def handler(self, session: Session, payload: BaseModel) -> Contract:
        assert isinstance(payload, CreateContract.Payload)
        require_unique(session, Contract, "contract_number", payload.contract_number)
        contract = Contract()
        apply_scalar_fields(contract, payload, _SCALAR_FIELDS)
        contract.code_flat_fee_schedule = _schedule_to_json(payload.code_flat_fee_schedule)
        session.add(contract)
        return contract


class EditContract(Command):
    target_entity = Contract
    authorization = require_role(Role.ADMIN)

    class Payload(BaseModel):
        id: UUID
        contract_number: str
        name: str | None = None
        start_date: date
        end_date: date | None = None
        code_flat_fee_schedule: list[CodeFlatFee] = Field(default_factory=list)

    def handler(self, session: Session, payload: BaseModel) -> Contract:
        assert isinstance(payload, EditContract.Payload)
        contract = resolve_for_command(session, Contract, payload.id)
        require_unique(
            session,
            Contract,
            "contract_number",
            payload.contract_number,
            exclude_id=payload.id,
        )
        apply_scalar_fields(contract, payload, _SCALAR_FIELDS)
        contract.code_flat_fee_schedule = _schedule_to_json(payload.code_flat_fee_schedule)
        return contract


class DeleteContract(Command):
    target_entity = Contract
    authorization = require_role(Role.ADMIN)

    class Payload(BaseModel):
        id: UUID

    def handler(self, session: Session, payload: BaseModel) -> Contract:
        assert isinstance(payload, DeleteContract.Payload)
        contract = resolve_for_command(session, Contract, payload.id)
        soft_delete(contract)
        return contract


register(CreateContract)
register(EditContract)
register(DeleteContract)
