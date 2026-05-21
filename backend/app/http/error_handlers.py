"""Translate dispatcher-surfaced exceptions to HTTP responses.

The Command dispatcher raises typed exceptions and lets them propagate
unwrapped (ADR-0011 rejections; ADR-0058 contention); the route layer
owns the HTTP mapping. Registered once on the app at startup via
`register_error_handlers`.

Response body is `{"detail": "..."}` -- the same shape FastAPI's own
HTTPException produces, so clients see one error format everywhere.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.engine.exceptions import (
    AuthorizationDenied,
    CommandRejected,
    EntityNotFound,
    TransientContention,
)


def _detail(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


def register_error_handlers(app: FastAPI) -> None:
    """Wire the dispatcher-exception -> HTTP-status handlers onto `app`.

    FastAPI resolves a handler by walking the exception's MRO, so the
    AuthorizationDenied / EntityNotFound handlers take precedence over the
    CommandRejected base handler for their own types.
    """

    @app.exception_handler(AuthorizationDenied)
    async def _on_auth_denied(request: Request, exc: AuthorizationDenied) -> JSONResponse:
        return _detail(403, exc.reason)

    @app.exception_handler(EntityNotFound)
    async def _on_not_found(request: Request, exc: EntityNotFound) -> JSONResponse:
        return _detail(404, exc.reason)

    @app.exception_handler(CommandRejected)
    async def _on_rejected(request: Request, exc: CommandRejected) -> JSONResponse:
        # LifecycleViolation / InvariantViolation, and any future rejection
        # not given a more specific handler above.
        return _detail(409, exc.reason)

    @app.exception_handler(TransientContention)
    async def _on_contention(request: Request, exc: TransientContention) -> JSONResponse:
        return _detail(503, "the system is busy; please retry")

    @app.exception_handler(IntegrityError)
    async def _on_integrity(request: Request, exc: IntegrityError) -> JSONResponse:
        # Hard DB-constraint backstop -- e.g. a unique-key race a handler
        # pre-check did not catch. The dispatcher has already rolled back.
        return _detail(409, "the request conflicts with existing data")
