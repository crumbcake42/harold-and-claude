"""Contract HTTP route tests — read + CRUD through the FastAPI app.

Wires the production app over an in-memory SQLite DB: `get_db` and the
`get_dispatcher` dependency both point at the same SQLite engine, and
`current_user` is overridden with a synthetic Caller. Exercises the
route layer + the dispatcher-exception -> HTTP-status mapping.
"""

from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.framework.caller import Caller, Role
from app.framework.runtime import build_dispatcher


@pytest.fixture
def admin_client(
    sqlite_engine: Engine, sqlite_session_factory: sessionmaker[Session]
) -> Iterator[TestClient]:
    from app.adapters.db import Base, get_db
    from app.config import settings
    from app.framework.auth import current_user
    from app.framework.runtime import get_dispatcher
    from app.main import app

    Base.metadata.create_all(sqlite_engine)
    test_dispatcher = build_dispatcher(sqlite_session_factory)
    admin = Caller(id=uuid4(), username="admin", roles=frozenset({Role.ADMIN}))

    def _get_db() -> Iterator[Session]:
        db = sqlite_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_dispatcher] = lambda: test_dispatcher
    app.dependency_overrides[current_user] = lambda: admin
    saved_secure = settings.cookie_secure
    settings.cookie_secure = False
    try:
        with TestClient(app) as client:
            yield client
    finally:
        for dep in (get_db, get_dispatcher, current_user):
            app.dependency_overrides.pop(dep, None)
        settings.cookie_secure = saved_secure


def _body(contract_number: str = "SCA-2026-001", **over: object) -> dict[str, object]:
    body: dict[str, object] = {
        "contract_number": contract_number,
        "name": "Test Contract",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "code_flat_fee_schedule": [{"code_type": "ACP7", "fee": "1200.00"}],
    }
    body.update(over)
    return body


def _as_role(*roles: Role) -> None:
    """Swap the current_user override to a caller holding `roles`."""
    from app.framework.auth import current_user
    from app.main import app

    caller = Caller(id=uuid4(), username="test", roles=frozenset(roles))
    app.dependency_overrides[current_user] = lambda: caller


# ---- create ----


def test_create_returns_201_and_body(admin_client: TestClient) -> None:
    resp = admin_client.post("/contracts", json=_body())
    assert resp.status_code == 201
    data = resp.json()
    assert data["contract_number"] == "SCA-2026-001"
    # start 2026-01-01, end 2026-12-31 -> active for any 2026 run date.
    assert data["validity"] == "active"
    assert data["display_label"] == "Test Contract"
    assert data["code_flat_fee_schedule"] == [{"code_type": "ACP7", "fee": "1200.00"}]


def test_create_duplicate_number_409(admin_client: TestClient) -> None:
    admin_client.post("/contracts", json=_body(contract_number="DUP"))
    resp = admin_client.post("/contracts", json=_body(contract_number="DUP"))
    assert resp.status_code == 409


def test_create_denied_for_coordinator_403(admin_client: TestClient) -> None:
    _as_role(Role.COORDINATOR)
    resp = admin_client.post("/contracts", json=_body())
    assert resp.status_code == 403


# ---- read ----


def test_create_then_list(admin_client: TestClient) -> None:
    admin_client.post("/contracts", json=_body(contract_number="A-1"))
    admin_client.post("/contracts", json=_body(contract_number="A-2"))
    resp = admin_client.get("/contracts")
    assert resp.status_code == 200
    numbers = [c["contract_number"] for c in resp.json()]
    assert numbers == ["A-1", "A-2"]


def test_get_one(admin_client: TestClient) -> None:
    created = admin_client.post("/contracts", json=_body()).json()
    resp = admin_client.get(f"/contracts/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_missing_404(admin_client: TestClient) -> None:
    assert admin_client.get(f"/contracts/{uuid4()}").status_code == 404


def test_reads_require_auth_401(admin_client: TestClient) -> None:
    from app.framework.auth import current_user
    from app.main import app

    app.dependency_overrides.pop(current_user, None)
    assert admin_client.get("/contracts").status_code == 401


# ---- update ----


def test_update_replaces_fields(admin_client: TestClient) -> None:
    created = admin_client.post("/contracts", json=_body()).json()
    resp = admin_client.put(
        f"/contracts/{created['id']}",
        json=_body(name="Renamed", code_flat_fee_schedule=[]),
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed"
    assert resp.json()["code_flat_fee_schedule"] == []


def test_update_missing_404(admin_client: TestClient) -> None:
    resp = admin_client.put(f"/contracts/{uuid4()}", json=_body())
    assert resp.status_code == 404


# ---- delete ----


def test_delete_204_then_get_404(admin_client: TestClient) -> None:
    created = admin_client.post("/contracts", json=_body()).json()
    assert admin_client.delete(f"/contracts/{created['id']}").status_code == 204
    assert admin_client.get(f"/contracts/{created['id']}").status_code == 404
