from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def sqlite_engine() -> Iterator[Engine]:
    """In-memory SQLite engine for test isolation.

    StaticPool keeps every connection on the same in-memory database so
    transactions across the test share state. Tests that need a fresh DB
    request this fixture; the engine is disposed at teardown.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
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
