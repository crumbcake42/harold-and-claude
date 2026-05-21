"""Auth routes — login / logout / me.

Login is the **one documented exception** to the Command-pipeline rule:
the dispatcher requires a Caller, and login is the surface that produces
one. Implemented as a FastAPI route directly (M1.1 decision 8 / ADR-0061).

Logout and me are likewise route-level: they're substrate, not domain
state changes that need history/invariants/cascade.

401 response shape is intentionally generic ("invalid credentials") with
no user-existence signal — defensive against enumeration.
"""

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session as DbSession

from app.adapters.db import get_db
from app.auth.entities import User, UserRole
from app.auth.schemas import LoginRequest
from app.auth.security import (
    create_session,
    current_user,
    revoke_session,
    verify_password,
)
from app.config import settings
from app.engine.caller import Caller, Role

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.session_ttl_hours * 3600,
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=settings.session_cookie_name, path="/")


@router.post("/login", response_model=Caller)
def login(
    body: LoginRequest,
    response: Response,
    db: DbSession = Depends(get_db),
) -> Caller:
    user = db.query(User).filter(User.username == body.username).one_or_none()
    if user is None or user.soft_deleted_at is not None:
        # Same response shape as bad-password path -- no enumeration signal.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
        )
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
        )
    session_row = create_session(db, user.id)
    role_rows = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    db.commit()
    _set_session_cookie(response, session_row.id)
    return Caller(
        id=user.id,
        username=user.username,
        roles=frozenset(Role(r.role) for r in role_rows),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    session_token: str | None = Cookie(default=None, alias="session"),
    db: DbSession = Depends(get_db),
) -> Response:
    """Revoke the session row and clear the cookie. Works even when the
    session has already expired (cookie just gets cleared)."""
    if session_token is not None:
        revoke_session(db, session_token)
        db.commit()
    _clear_session_cookie(response)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=Caller)
def me(caller: Caller = Depends(current_user)) -> Caller:
    return caller
