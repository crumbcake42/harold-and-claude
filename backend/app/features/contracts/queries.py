"""Read-query functions backing the contracts slice's read routes.

Read routes are not Commands (ADR-0070): they take a plain session and the
query logic lives here, separate from the route's HTTP concerns. These
functions return entities; the route maps them to `ContractRead` DTOs.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.features.contracts.entities import Contract


def list_contracts(db: Session) -> list[Contract]:
    """All non-deleted contracts, ordered by `contract_number`."""
    return (
        db.query(Contract)
        .filter(Contract.deleted_at.is_(None))
        .order_by(Contract.contract_number)
        .all()
    )


def get_contract(db: Session, contract_id: UUID) -> Contract | None:
    """A single live contract by id, or `None` if missing or soft-deleted."""
    contract = db.get(Contract, contract_id)
    if contract is None or contract.deleted_at is not None:
        return None
    return contract
