import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import JSON, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings


def json_serializer(obj: Any) -> str:
    """Engine-wide JSON serializer used for both portable JSON and JSONB
    columns. Falls back to str() for non-JSON-native types (UUID, datetime,
    Decimal) so history snapshots and payload_summary dicts can hold typed-
    UUID references and timestamps without per-call coercion. Readers parse
    the typed form back from the string per ADR-0013's typed-UUID rule.
    """
    return json.dumps(obj, default=str)


class Base(DeclarativeBase):
    """Production declarative base. First occupants are the per-entity history
    tables + command_audit_log landing in M0.3 / Step 1.3b; domain entity
    tables join in M1+. Smoke-test fixtures use a separate SmokeBase to keep
    test tables out of production metadata.
    """


def json_column() -> JSON:
    """Cross-dialect JSON column type: JSONB on PostgreSQL, portable JSON
    (text-backed) on SQLite. Centralized here so M0.4's adapter boundary can
    wrap it without touching every history table. TODO(Step 1.4): replace
    with the documented adapter-boundary surface.
    """
    return JSON().with_variant(JSONB(), "postgresql")


def _build_engine(url: str) -> Engine:
    connect_args: dict[str, object] = {}
    engine_kwargs: dict[str, object] = {}
    if url.startswith("sqlite"):
        # SQLite in tests / offline-fallback: allow cross-thread access for the
        # FastAPI test client; use StaticPool for in-memory URLs so every
        # connection sees the same database.
        connect_args["check_same_thread"] = False
        if ":memory:" in url or url.endswith("sqlite://"):
            engine_kwargs["poolclass"] = StaticPool
    return create_engine(
        url,
        connect_args=connect_args,
        future=True,
        json_serializer=json_serializer,
        **engine_kwargs,
    )


engine: Engine = _build_engine(settings.database_url)

SessionFactory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


@contextmanager
def get_session() -> Iterator[Session]:
    """Yield a SQLAlchemy session scoped to a single unit of work.

    Routes / scripts that need a session outside the dispatcher should use this.
    The dispatcher manages its own session lifecycle (with SERIALIZABLE isolation
    set per-transaction per ADR-0056); callers that just need a session for reads
    or ad-hoc work get default isolation.
    """
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()


def is_postgres() -> bool:
    return engine.dialect.name == "postgresql"
