"""Contract admin routes — read + CRUD.

Read routes (`GET /contracts`, `GET /contracts/{id}`) go through a plain
`get_db` session: they are not Commands. Write routes (`POST` / `PUT` /
`DELETE`) dispatch `create/edit/delete_contract` through the Command
pipeline -- the dispatcher owns its own SERIALIZABLE session, so write
routes do not take `get_db`.

The route DTOs live in `schemas.py` and the read-query logic in
`queries.py`, kept separate from the command `Payload` models (ADR-0070);
this slice's `schemas.py` is the HTTP wire contract the generated client
consumes.

Authorization: writes carry ADR-0047 Cluster 1's `role >= admin` on the
command predicate; reads require any authenticated user.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session as DbSession

from app.adapters.db import get_db
from app.auth import current_user
from app.engine.caller import Caller
from app.engine.dispatcher import Dispatcher
from app.features.contracts import queries
from app.features.contracts.commands import (
    CreateContract,
    DeleteContract,
    EditContract,
)
from app.features.contracts.schemas import ContractRead, ContractWriteRequest
from app.runtime import get_dispatcher

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.get("", response_model=list[ContractRead], dependencies=[Depends(current_user)])
def list_contracts(db: DbSession = Depends(get_db)) -> list[ContractRead]:
    return [ContractRead.model_validate(row) for row in queries.list_contracts(db)]


@router.get(
    "/{contract_id}",
    response_model=ContractRead,
    dependencies=[Depends(current_user)],
)
def get_contract(contract_id: UUID, db: DbSession = Depends(get_db)) -> ContractRead:
    contract = queries.get_contract(db, contract_id)
    if contract is None:
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
