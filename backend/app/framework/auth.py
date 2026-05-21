"""Authentication substrate per the M1.1 plan (ADR-0061).

Three responsibilities collected in one module:

  - **Password hashing.** argon2id via argon2-cffi with OWASP 2024 parameters
    pinned explicitly (time_cost=2, memory_cost=19456 KiB, parallelism=1,
    hash_len=32, salt_len=16). Pinned rather than using library defaults so
    hashes from any machine stay verifiable across argon2-cffi version bumps.

  - **Session lifecycle.** DB-backed server-side sessions per the M1.1
    decision: opaque random token via secrets.token_urlsafe(32) (256 bits
    entropy) stored as the session row's PK; httpOnly Secure SameSite=Lax
    cookie carries the token; 12h sliding TTL refreshed on each request.
    Revoke = DELETE.

  - **FastAPI current_user dependency.** Reads the session cookie, looks up
    the row (verifying not expired), refreshes last_seen_at, loads the
    user's roles, and returns the concrete Caller (app.framework.caller).
    Raises HTTPException(401) on any miss/expiration. This is the single
    seam at which "the request" becomes "the actor" for the dispatcher.

Out of scope per Session 34 canvass + mvp.md: password reset; login rate
limiting / lockout; remember-me beyond 12h sliding TTL; 2FA / OAuth / SSO;
immediate session invalidation on `revoke_user_role` (next-request
authorization check is MVP behavior); CSRF tokens (SameSite=Lax covers MVP
threat surface).
"""

import secrets
from datetime import UTC, datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.adapters.db import get_db
from app.config import settings
from app.domain.auth import Session as SessionRow
from app.domain.auth import User, UserRole
from app.framework.caller import Caller, Role

# Pinned argon2id parameters per OWASP 2024 guidance (M1.1 decision). Module-
# level singleton -- PasswordHasher is thread-safe.
_HASHER = PasswordHasher(
    time_cost=2,
    memory_cost=19456,
    parallelism=1,
    hash_len=32,
    salt_len=16,
)


def hash_password(plain: str) -> str:
    """Return an argon2id hash string suitable for storage in user.password_hash."""
    return _HASHER.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time-ish verify. Returns False on mismatch or malformed hash."""
    try:
        return _HASHER.verify(hashed, plain)
    except VerifyMismatchError:
        return False
    except Exception:
        # Malformed hash, unsupported algorithm, etc. -- treat as auth failure
        # rather than leaking internal errors to the login surface.
        return False


# ---- Session lifecycle ----


def _generate_token() -> str:
    """256-bit URL-safe random session token."""
    return secrets.token_urlsafe(32)


def create_session(db: DbSession, user_id, ttl_hours: int | None = None) -> SessionRow:
    """Insert a fresh session row and return it. Caller is responsible for
    setting the cookie on the response."""
    now = datetime.now(UTC)
    ttl = ttl_hours if ttl_hours is not None else settings.session_ttl_hours
    row = SessionRow(
        id=_generate_token(),
        user_id=user_id,
        created_at=now,
        expires_at=now + timedelta(hours=ttl),
        last_seen_at=now,
    )
    db.add(row)
    db.flush()
    return row


def _ensure_utc(dt: datetime) -> datetime:
    """SQLite-portability shim: SQLite TIMESTAMP doesn't preserve timezone;
    rows come back naive. Postgres preserves the tz. Treat naive as UTC
    (which matches the convention all session writes use)."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


def lookup_session(db: DbSession, token: str) -> SessionRow | None:
    """Return the live session row for `token`, or None if missing/expired."""
    row = db.get(SessionRow, token)
    if row is None:
        return None
    if _ensure_utc(row.expires_at) <= datetime.now(UTC):
        return None
    return row


def refresh_session(db: DbSession, row: SessionRow, ttl_hours: int | None = None) -> None:
    """Slide last_seen_at + expires_at forward to keep the session alive."""
    now = datetime.now(UTC)
    ttl = ttl_hours if ttl_hours is not None else settings.session_ttl_hours
    row.last_seen_at = now
    row.expires_at = now + timedelta(hours=ttl)
    db.flush()


def revoke_session(db: DbSession, token: str) -> None:
    """Hard-delete the session row. Idempotent (no-op if absent)."""
    row = db.get(SessionRow, token)
    if row is not None:
        db.delete(row)
        db.flush()


# ---- FastAPI dependency: current_user → Caller ----


def _load_caller(db: DbSession, user: User) -> Caller:
    """Build a concrete Caller from a User row + its UserRole rows."""
    role_rows = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    roles: frozenset[Role] = frozenset(Role(r.role) for r in role_rows)
    return Caller(id=user.id, username=user.username, roles=roles)


def current_user(
    session_token: str | None = Cookie(default=None, alias="session"),
    db: DbSession = Depends(get_db),
) -> Caller:
    """FastAPI dependency producing the Caller for the current request.

    Raises 401 if the session cookie is missing, the session row is missing
    or expired, or the user has been soft-deleted. Refreshes last_seen_at +
    expires_at on success (sliding TTL).
    """
    if session_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated")
    row = lookup_session(db, session_token)
    if row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="session expired")
    user = db.get(User, row.user_id)
    if user is None or user.soft_deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not active")
    refresh_session(db, row)
    caller = _load_caller(db, user)
    # commit so refresh + any session-state side-effects land. FastAPI doesn't
    # auto-commit non-Command route deps; we own this transaction.
    db.commit()
    return caller
