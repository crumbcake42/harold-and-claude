"""End-to-end auth substrate tests.

Covers the M1.1 plan's verification list:
  - login → /auth/me → /auth/logout round-trip via the real cookie path.
  - 401 on missing/invalid/expired session cookie.
  - login surfaces a generic message for both unknown user and bad password
    (no enumeration signal).
  - per-role override fixtures from conftest produce the expected Caller.

Per ADR-0051 / ADR-0052 / ADR-0056: SQLite is the smoke-test target;
production-equivalent auth runs against Postgres. argon2id hashing and the
cookie/session round-trip are dialect-agnostic so SQLite coverage is honest
for this slice.
"""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.domain.auth import Session as SessionRow
from app.domain.auth import User, UserRole
from app.framework.auth import hash_password
from app.framework.caller import Role


def _seed_admin(session_factory: sessionmaker[Session], username: str = "admin") -> User:
    with session_factory() as db:
        user = User(username=username, password_hash=hash_password("correct-horse"))
        db.add(user)
        db.flush()
        db.add(
            UserRole(
                user_id=user.id,
                role=Role.ADMIN.value,
                granted_at=datetime.now(UTC),
                granted_by=user.id,
            )
        )
        db.commit()
        db.refresh(user)
        return user


def test_login_sets_cookie_and_returns_caller(
    auth_client: TestClient, sqlite_session_factory: sessionmaker[Session]
) -> None:
    user = _seed_admin(sqlite_session_factory)

    response = auth_client.post(
        "/auth/login",
        json={"username": "admin", "password": "correct-horse"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "admin"
    assert body["id"] == str(user.id)
    assert body["roles"] == [Role.ADMIN.value]
    cookie = response.cookies.get(settings.session_cookie_name)
    assert cookie is not None and len(cookie) >= 32  # token_urlsafe(32)


def test_me_returns_caller_when_authenticated(
    auth_client: TestClient, sqlite_session_factory: sessionmaker[Session]
) -> None:
    _seed_admin(sqlite_session_factory)
    auth_client.post(
        "/auth/login",
        json={"username": "admin", "password": "correct-horse"},
    )

    response = auth_client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


def test_logout_clears_cookie_and_revokes_session(
    auth_client: TestClient, sqlite_session_factory: sessionmaker[Session]
) -> None:
    _seed_admin(sqlite_session_factory)
    auth_client.post(
        "/auth/login",
        json={"username": "admin", "password": "correct-horse"},
    )
    assert auth_client.get("/auth/me").status_code == 200

    logout = auth_client.post("/auth/logout")
    assert logout.status_code == 204

    # TestClient retains the cookie unless the server cleared it; subsequent
    # /auth/me should 401 either way (session row revoked).
    assert auth_client.get("/auth/me").status_code == 401

    # No live session rows for the user.
    with sqlite_session_factory() as db:
        assert db.query(SessionRow).count() == 0


def test_me_without_cookie_returns_401(auth_client: TestClient) -> None:
    response = auth_client.get("/auth/me")
    assert response.status_code == 401


def test_me_with_unknown_token_returns_401(auth_client: TestClient) -> None:
    auth_client.cookies.set(settings.session_cookie_name, "garbage-token-xyz")
    response = auth_client.get("/auth/me")
    assert response.status_code == 401


def test_me_with_expired_session_returns_401(
    auth_client: TestClient, sqlite_session_factory: sessionmaker[Session]
) -> None:
    user = _seed_admin(sqlite_session_factory)
    past = datetime.now(UTC) - timedelta(hours=1)
    with sqlite_session_factory() as db:
        db.add(
            SessionRow(
                id="expired-token",
                user_id=user.id,
                created_at=past - timedelta(hours=12),
                expires_at=past,
                last_seen_at=past,
            )
        )
        db.commit()
    auth_client.cookies.set(settings.session_cookie_name, "expired-token")
    response = auth_client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.parametrize(
    "username,password",
    [
        ("admin", "wrong-password"),
        ("does-not-exist", "anything"),
    ],
)
def test_login_failures_share_response_shape(
    auth_client: TestClient,
    sqlite_session_factory: sessionmaker[Session],
    username: str,
    password: str,
) -> None:
    """No enumeration signal: bad password and unknown user return the same
    401 body."""
    _seed_admin(sqlite_session_factory)
    response = auth_client.post(
        "/auth/login", json={"username": username, "password": password}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "invalid credentials"}


def test_login_with_soft_deleted_user_returns_401(
    auth_client: TestClient, sqlite_session_factory: sessionmaker[Session]
) -> None:
    user = _seed_admin(sqlite_session_factory)
    with sqlite_session_factory() as db:
        db.get(User, user.id).soft_deleted_at = datetime.now(UTC)  # type: ignore[union-attr]
        db.commit()
    response = auth_client.post(
        "/auth/login", json={"username": "admin", "password": "correct-horse"}
    )
    assert response.status_code == 401


# ---- Per-role override fixtures from conftest ------------------------------


def test_as_superadmin_fixture_returns_superadmin_caller(as_superadmin) -> None:
    assert Role.SUPERADMIN in as_superadmin.roles


def test_as_admin_fixture_returns_admin_caller(as_admin) -> None:
    assert as_admin.roles == frozenset({Role.ADMIN})


def test_as_coordinator_fixture_returns_coordinator_caller(as_coordinator) -> None:
    assert as_coordinator.roles == frozenset({Role.COORDINATOR})


def test_as_auditor_fixture_returns_auditor_caller(as_auditor) -> None:
    assert as_auditor.roles == frozenset({Role.AUDITOR})
