"""Contract entity + create/edit/delete_contract command tests.

Exercises the M1.2 2.2a backend slice end-to-end through a real Dispatcher
on SQLite: the admin-CRUD authoring helpers, the require_role(admin)
predicate, the ContractNumberUnique invariant, and the audit_log capture
path (a command_audit_log row written in-txn per ADR-0057).
"""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.db import Base
from app.adapters.history import CommandAuditLog
from app.features.contracts.commands import (
    CodeFlatFee,
    CreateContract,
    DeleteContract,
    EditContract,
)
from app.features.contracts.entities import Contract
from app.framework.caller import Caller, Role
from app.framework.dispatcher import Dispatcher
from app.framework.exceptions import (
    AuthorizationDenied,
    EntityNotFound,
    InvariantViolation,
)
from app.runtime import build_dispatcher

ADMIN = Caller(id=uuid4(), username="admin", roles=frozenset({Role.ADMIN}))
COORDINATOR = Caller(id=uuid4(), username="coord", roles=frozenset({Role.COORDINATOR}))


@pytest.fixture
def dispatcher(
    sqlite_engine: Engine, sqlite_session_factory: sessionmaker[Session]
) -> Dispatcher:
    """A Dispatcher wired to a fresh in-memory SQLite DB with all tables."""
    Base.metadata.create_all(sqlite_engine)
    return build_dispatcher(sqlite_session_factory)


def _create_payload(
    contract_number: str = "SCA-2026-001",
    name: str | None = "Test Contract",
    start_date: date = date(2026, 1, 1),
    end_date: date | None = date(2026, 12, 31),
    code_flat_fee_schedule: list[CodeFlatFee] | None = None,
) -> CreateContract.Payload:
    return CreateContract.Payload(
        contract_number=contract_number,
        name=name,
        start_date=start_date,
        end_date=end_date,
        code_flat_fee_schedule=(
            [CodeFlatFee(code_type="ACP7", fee=Decimal("1200.00"))]
            if code_flat_fee_schedule is None
            else code_flat_fee_schedule
        ),
    )


# ---- Entity-level derivations (ADR-0043) ----


def test_validity_pending_active_expired() -> None:
    pending = Contract(contract_number="P", start_date=date(2099, 1, 1))
    assert pending.validity == "pending"

    active_open = Contract(contract_number="A", start_date=date(2000, 1, 1))
    assert active_open.validity == "active"

    expired = Contract(
        contract_number="E", start_date=date(2000, 1, 1), end_date=date(2001, 1, 1)
    )
    assert expired.validity == "expired"


def test_display_label_derives_from_number_when_name_absent() -> None:
    # name absent -> 'C' + last 5 chars of contract_number.
    assert Contract(contract_number="SCA-2026-001").display_label == "C6-001"
    # name present -> name verbatim.
    assert Contract(contract_number="X", name="Named").display_label == "Named"


# ---- create_contract ----


def test_create_contract_persists_and_audits(
    dispatcher: Dispatcher, sqlite_session_factory: sessionmaker[Session]
) -> None:
    result = dispatcher.dispatch(CreateContract, _create_payload(), ADMIN)
    assert isinstance(result, Contract)

    with sqlite_session_factory() as s:
        row = s.get(Contract, result.id)
        assert row is not None
        assert row.contract_number == "SCA-2026-001"
        assert row.name == "Test Contract"
        # JSONB collection round-trips; Decimal serializes as a JSON string.
        assert row.code_flat_fee_schedule == [{"code_type": "ACP7", "fee": "1200.00"}]

        audit = (
            s.query(CommandAuditLog)
            .filter(CommandAuditLog.entity_id == result.id)
            .all()
        )
        assert len(audit) == 1
        assert audit[0].command_name == "CreateContract"
        assert audit[0].entity_type == "Contract"
        assert audit[0].caller_id == ADMIN.id


def test_create_contract_rejects_duplicate_number(dispatcher: Dispatcher) -> None:
    dispatcher.dispatch(CreateContract, _create_payload(contract_number="DUP"), ADMIN)
    with pytest.raises(InvariantViolation):
        dispatcher.dispatch(
            CreateContract,
            _create_payload(contract_number="DUP", start_date=date(2027, 1, 1)),
            ADMIN,
        )


def test_create_contract_denied_below_admin(dispatcher: Dispatcher) -> None:
    with pytest.raises(AuthorizationDenied):
        dispatcher.dispatch(CreateContract, _create_payload(), COORDINATOR)


def test_create_contract_empty_schedule(
    dispatcher: Dispatcher, sqlite_session_factory: sessionmaker[Session]
) -> None:
    result = dispatcher.dispatch(
        CreateContract, _create_payload(code_flat_fee_schedule=[]), ADMIN
    )
    with sqlite_session_factory() as s:
        row = s.get(Contract, result.id)
        assert row is not None
        assert row.code_flat_fee_schedule == []


# ---- edit_contract ----


def test_edit_contract_replaces_fields(
    dispatcher: Dispatcher, sqlite_session_factory: sessionmaker[Session]
) -> None:
    created = dispatcher.dispatch(CreateContract, _create_payload(), ADMIN)
    edited = dispatcher.dispatch(
        EditContract,
        EditContract.Payload(
            id=created.id,
            contract_number="SCA-2026-001",
            name="Renamed",
            start_date=date(2026, 1, 1),
            end_date=None,
            code_flat_fee_schedule=[],
        ),
        ADMIN,
    )
    assert isinstance(edited, Contract)
    with sqlite_session_factory() as s:
        row = s.get(Contract, created.id)
        assert row is not None
        assert row.name == "Renamed"
        assert row.end_date is None
        assert row.code_flat_fee_schedule == []


def test_edit_contract_missing_rejects(dispatcher: Dispatcher) -> None:
    with pytest.raises(EntityNotFound):
        dispatcher.dispatch(
            EditContract,
            EditContract.Payload(
                id=uuid4(), contract_number="X", start_date=date(2026, 1, 1)
            ),
            ADMIN,
        )


# ---- delete_contract ----


def test_delete_contract_soft_deletes(
    dispatcher: Dispatcher, sqlite_session_factory: sessionmaker[Session]
) -> None:
    created = dispatcher.dispatch(CreateContract, _create_payload(), ADMIN)
    deleted = dispatcher.dispatch(
        DeleteContract, DeleteContract.Payload(id=created.id), ADMIN
    )
    assert isinstance(deleted, Contract)
    assert deleted.deleted_at is not None
    with sqlite_session_factory() as s:
        row = s.get(Contract, created.id)
        assert row is not None  # soft delete -- the row stays
        assert row.deleted_at is not None


def test_deleted_contract_is_not_resolvable(dispatcher: Dispatcher) -> None:
    created = dispatcher.dispatch(CreateContract, _create_payload(), ADMIN)
    dispatcher.dispatch(DeleteContract, DeleteContract.Payload(id=created.id), ADMIN)
    # A soft-deleted contract counts as not-found for further commands.
    with pytest.raises(EntityNotFound):
        dispatcher.dispatch(
            DeleteContract, DeleteContract.Payload(id=created.id), ADMIN
        )
