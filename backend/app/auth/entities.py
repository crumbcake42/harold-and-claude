"""User / UserRole / Session entity models (M1.1).

User and UserRole are domain entities from the 21-entity roster; Session is
the auth-substrate table holding live sessions per the M1.1 decision (DB-
backed server-side sessions; opaque random token in httpOnly Secure
SameSite=Lax cookie; 12h sliding TTL).

Schema notes:
  - User.employee_id is a plain UUID column (no FK constraint) at M1.1; the
    Employee table lands in M1.2 and its migration will add the FK + UNIQUE
    constraint then. Same pattern as app.adapters.history's deferred FKs.
  - UserRole is a composite-key associative entity per ADR-0036; role-grant
    commands (grant_user_role / revoke_user_role) land in M1.3.
  - Session.id IS the opaque session token (PK); lookup is by token. Tokens
    are produced via secrets.token_urlsafe(32) in app.auth.security.

History pattern:
  - User uses the audit_log pattern (it's one of ADR-0052's 7 audit-log
    entities). UserRole has no entity-level history in MVP -- grants/revokes
    surface via the User audit log per ADR-0040.
  - Session is substrate, not a domain entity; no history.

Audit metadata:
  - User carries the four created_*/updated_* columns via AuditMetadataMixin
    (ADR-0072). UserRole and Session do not -- UserRole is a composite-key
    associative entity and Session is auth substrate, not domain entities.
"""

from datetime import datetime
from typing import ClassVar
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.adapters.db import Base
from app.engine.audit import AuditMetadataMixin


class User(Base, AuditMetadataMixin):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    # FK + UNIQUE land in the Employee migration (M1.2). Plain UUID until then.
    employee_id: Mapped[UUID | None] = mapped_column(nullable=True)
    soft_deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    history_pattern: ClassVar[str] = "audit_log"


class UserRole(Base):
    __tablename__ = "user_role"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[str] = mapped_column(String, primary_key=True)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # FK lands when grant_user_role command exists (M1.3); plain UUID until then.
    granted_by: Mapped[UUID] = mapped_column(nullable=False)

    # No history_pattern: grants/revokes surface via the User audit log per ADR-0040.
    history_pattern: ClassVar[str] = "none"


class Session(Base):
    __tablename__ = "session"

    # The opaque token is the PK; lookup is WHERE id = :token.
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        Index("ix_session_user_id", "user_id"),
        Index("ix_session_expires_at", "expires_at"),
    )

    history_pattern: ClassVar[str] = "none"
