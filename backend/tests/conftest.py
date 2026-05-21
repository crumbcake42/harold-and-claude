from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.domain.auth  # noqa: F401 -- registers auth tables on Base.metadata
from app.adapters.db import json_serializer


@pytest.fixture
def sqlite_engine() -> Iterator[Engine]:
    """In-memory SQLite engine for test isolation.

    StaticPool keeps every connection on the same in-memory database so
    transactions across the test share state. Tests that need a fresh DB
    request this fixture; the engine is disposed at teardown. Uses the
    production JSON serializer so JSON column writes coerce UUIDs /
    datetimes the same way the production engine does.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
        json_serializer=json_serializer,
    )
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def sqlite_session_factory(sqlite_engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=sqlite_engine, autoflush=False, expire_on_commit=False, future=True
    )


# ---- M1.1 auth fixtures ----------------------------------------------------
#
# Two test seams are provided:
#
#   (1) `auth_client` -- a TestClient with get_db overridden to use an
#       in-memory SQLite engine that has the auth tables created. Auth
#       round-trip tests (login → me → logout) use this to exercise the
#       real cookie-based flow end-to-end.
#
#   (2) `as_superadmin` / `as_admin` / `as_coordinator` / `as_auditor` --
#       per-role fixtures that override the current_user FastAPI dependency
#       to return a pre-constructed Caller. M1.2+ command/route tests use
#       these to assert ADR-0047 authorization predicates without needing
#       to round-trip an actual login.
#
# Both seams use the in-memory SQLite engine; production-equivalent auth
# behavior (advisory locks, SERIALIZABLE) is not exercised here per the
# ADR-0051 / ADR-0052 / ADR-0056 SQLite-fallback discipline.


@pytest.fixture
def auth_client(
    sqlite_engine: Engine, sqlite_session_factory: sessionmaker[Session]
) -> Iterator[TestClient]:
    """TestClient with the production app + auth tables created in SQLite +
    get_db overridden to yield from the SQLite session factory.

    settings.cookie_secure is forced False for the duration of the fixture --
    TestClient runs on http://testserver, and httpx refuses to round-trip a
    Secure cookie over plain HTTP. Production keeps Secure=True via the
    .env / config default.
    """
    from app.adapters.db import Base, get_db
    from app.config import settings
    from app.main import app

    Base.metadata.create_all(sqlite_engine)

    def override_get_db() -> Iterator[Session]:
        db = sqlite_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    saved_secure = settings.cookie_secure
    settings.cookie_secure = False
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_db, None)
        settings.cookie_secure = saved_secure


def _override_current_user_with(role_value: str):
    """Return a (cleanup, caller) pair: cleanup pops the override, caller is
    the synthetic Caller the override returns.
    """
    from app.framework.auth import current_user
    from app.framework.caller import Caller, Role
    from app.main import app

    caller = Caller(
        id=uuid4(),
        username=f"{role_value}-test",
        roles=frozenset({Role(role_value)}),
    )

    def override() -> Caller:
        return caller

    app.dependency_overrides[current_user] = override
    return (lambda: app.dependency_overrides.pop(current_user, None), caller)


@pytest.fixture
def as_superadmin():
    cleanup, caller = _override_current_user_with("superadmin")
    yield caller
    cleanup()


@pytest.fixture
def as_admin():
    cleanup, caller = _override_current_user_with("admin")
    yield caller
    cleanup()


@pytest.fixture
def as_coordinator():
    cleanup, caller = _override_current_user_with("coordinator")
    yield caller
    cleanup()


@pytest.fixture
def as_auditor():
    cleanup, caller = _override_current_user_with("auditor")
    yield caller
    cleanup()
