"""Production wiring for the command dispatcher.

ADR-0059's Dispatcher takes its session factory + capture sink as
constructor args -- a test-ergonomics choice, no module-level singletons
inside the framework. Production still needs *one* configured dispatcher:
this module builds it (wired to the real per-entity history tables +
command_audit_log) and exposes it as a FastAPI dependency, so routes
inject it via `Depends(get_dispatcher)` and tests override it in
`app.dependency_overrides` with a SQLite-backed dispatcher.

`build_dispatcher` is also called directly by `app.cli.seed_db`, which
runs outside the request cycle.
"""

from sqlalchemy.orm import Session, sessionmaker

from app.adapters.capture import SqlAlchemyCaptureSink
from app.adapters.db import SessionFactory
from app.adapters.history import (
    COMPREHENSIVE_HISTORY,
    LIFECYCLE_HISTORY,
    CommandAuditLog,
)
from app.adapters.postgres import set_serializable_isolation, try_advisory_xact_lock
from app.engine.dispatcher import Dispatcher


def build_dispatcher(
    session_factory: sessionmaker[Session] = SessionFactory,
) -> Dispatcher:
    """Construct a Dispatcher wired to the real history tables. Defaults to
    the production SessionFactory; `seed_db` and tests pass their own.
    """
    sink = SqlAlchemyCaptureSink(
        comprehensive=COMPREHENSIVE_HISTORY,
        lifecycle=LIFECYCLE_HISTORY,
        audit_log_model=CommandAuditLog,
    )
    return Dispatcher(
        session_factory=session_factory,
        sink=sink,
        set_isolation=set_serializable_isolation,
        try_advisory_lock=try_advisory_xact_lock,
    )


_dispatcher = build_dispatcher()


def get_dispatcher() -> Dispatcher:
    """FastAPI dependency yielding the production dispatcher. Write routes
    depend on this; tests override it with a SQLite-backed dispatcher.
    """
    return _dispatcher
