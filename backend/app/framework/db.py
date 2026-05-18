from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings


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
    return create_engine(url, connect_args=connect_args, future=True, **engine_kwargs)


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
