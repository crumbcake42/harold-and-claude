"""Route request/response DTOs for the contracts slice.

Kept separate from the command `Payload` models (ADR-0070): these are the
OpenAPI wire contract the generated frontend client consumes. The field
overlap with `CreateContract.Payload` / `EditContract.Payload` is accepted,
not derived away (tracked as DRIFT-001 in `planning/DRIFTS.md`).

`CodeFlatFee` -- the `{code_type, fee}` sub-model -- is a leaf value type
shared by both the command Payloads and these DTOs; it is defined once in
`commands.py` and imported here.
"""

from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.features.contracts.commands import CodeFlatFee


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
