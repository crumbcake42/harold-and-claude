"""Contract admin routes — read + CRUD.

Read routes (`GET /contracts`, `GET /contracts/{id}`) go through a plain
`get_db` session: they are not Commands. Write routes (`POST` / `PUT` /
`DELETE`) dispatch `create/edit/delete_contract` through the Command
pipeline -- the dispatcher owns its own SERIALIZABLE session, so write
routes do not take `get_db`.

The HTTP request/response models live here, distinct from the command
`Payload` models: this module is the HTTP contract 2.2c's generated
client consumes. `ContractWriteRequest` serves both create and update
(both are full-form replacements of the editable fields).

Authorization: writes carry ADR-0047 Cluster 1's `role >= admin` on the
command predicate; reads require any authenticated user.
"""

from datetime import date
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session as DbSession

from app.adapters.db import get_db
from app.auth import current_user
from app.domain.commands.contract import (
    CodeFlatFee,
    CreateContract,
    DeleteContract,
    EditContract,
)
from app.domain.contract import Contract
from app.framework.caller import Caller
from app.framework.dispatcher import Dispatcher
from app.framework.runtime import get_dispatcher

router = APIRouter(prefix="/contracts", tags=["contracts"])


class ContractWriteRequest(BaseModel):
    """Request body for create (POST) and update (PUT). Both replace the
    full set of editable fields.
    """

    contract_number: str
    name: str | None = None
    start_date: date
    end_date: date | None = None
    code_flat_fee_schedule: list[CodeFlatFee] = Field(default_factory=list)


class ContractRead(BaseModel):
    """Contract as returned by the read + write routes. `validity` and
    `display_label` are ADR-0043 derivations read off the entity.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    contract_number: str
    name: str | None
    start_date: date
    end_date: date | None
    code_flat_fee_schedule: list[CodeFlatFee]
    validity: Literal["pending", "active", "expired"]
    display_label: str


@router.get("", response_model=list[ContractRead], dependencies=[Depends(current_user)])
def list_contracts(db: DbSession = Depends(get_db)) -> list[ContractRead]:
    rows = (
        db.query(Contract)
        .filter(Contract.deleted_at.is_(None))
        .order_by(Contract.contract_number)
        .all()
    )
    return [ContractRead.model_validate(row) for row in rows]


@router.get(
    "/{contract_id}",
    response_model=ContractRead,
    dependencies=[Depends(current_user)],
)
def get_contract(contract_id: UUID, db: DbSession = Depends(get_db)) -> ContractRead:
    contract = db.get(Contract, contract_id)
    if contract is None or contract.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contract not found")
    return ContractRead.model_validate(contract)


@router.post("", response_model=ContractRead, status_code=status.HTTP_201_CREATED)
def create_contract(
    body: ContractWriteRequest,
    caller: Caller = Depends(current_user),
    dispatcher: Dispatcher = Depends(get_dispatcher),
) -> ContractRead:
    contract = dispatcher.dispatch(
        CreateContract, CreateContract.Payload(**body.model_dump()), caller
    )
    return ContractRead.model_validate(contract)


@router.put("/{contract_id}", response_model=ContractRead)
def update_contract(
    contract_id: UUID,
    body: ContractWriteRequest,
    caller: Caller = Depends(current_user),
    dispatcher: Dispatcher = Depends(get_dispatcher),
) -> ContractRead:
    contract = dispatcher.dispatch(
        EditContract, EditContract.Payload(id=contract_id, **body.model_dump()), caller
    )
    return ContractRead.model_validate(contract)


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(
    contract_id: UUID,
    caller: Caller = Depends(current_user),
    dispatcher: Dispatcher = Depends(get_dispatcher),
) -> Response:
    dispatcher.dispatch(DeleteContract, DeleteContract.Payload(id=contract_id), caller)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
