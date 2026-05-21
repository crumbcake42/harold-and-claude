"""Bootstrap the first superadmin user.

Usage:
    uv run python -m app.cli.bootstrap_admin

Prompts for username + password (confirmed twice), creates the User row and
the superadmin UserRole grant, prints the created user's id. Idempotent on
username collision: prints a friendly message and exits non-zero rather
than overwriting an existing user.

Stdlib `input()` + `getpass.getpass()` -- no Click dependency. Per the
app/cli/ convention pinned in Session 34's pre-M1.1 cleanup commit, Click
gets adopted when a 3rd CLI command lands (this is the 2nd, after
export_openapi).
"""

import getpass
import sys
from datetime import UTC, datetime
from uuid import uuid4

from app.adapters.db import SessionFactory
from app.auth.entities import User, UserRole
from app.auth.security import hash_password
from app.framework.caller import Role


def _read_password(prompt: str = "password: ") -> str:
    """Prompt for a password twice and confirm they match. Re-prompts on
    mismatch (no retry limit at MVP -- the user can ^C)."""
    while True:
        pw = getpass.getpass(prompt)
        confirm = getpass.getpass("confirm password: ")
        if pw == confirm:
            if not pw:
                print("password cannot be empty", file=sys.stderr)
                continue
            return pw
        print("passwords do not match -- try again", file=sys.stderr)


def main() -> int:
    username = input("username: ").strip()
    if not username:
        print("username cannot be empty", file=sys.stderr)
        return 1

    password = _read_password()

    with SessionFactory() as db:
        existing = db.query(User).filter(User.username == username).one_or_none()
        if existing is not None:
            print(
                f"user {username!r} already exists (id={existing.id}); "
                f"this command does not overwrite. delete the row manually or "
                f"pick a different username.",
                file=sys.stderr,
            )
            return 2

        # Bootstrap is the documented exception to the every-state-change-is-
        # a-Command rule (alongside login), so it stamps the ADR-0072 audit
        # columns itself -- the dispatcher is not in the loop. created_by /
        # updated_by are self-attributed: no prior caller exists. The id is
        # generated up front so it can fill the self-referencing columns.
        now = datetime.now(UTC)
        user_id = uuid4()
        user = User(
            id=user_id,
            username=username,
            password_hash=hash_password(password),
            created_at=now,
            created_by=user_id,
            updated_at=now,
            updated_by=user_id,
        )
        db.add(user)
        db.flush()

        grant = UserRole(
            user_id=user.id,
            role=Role.SUPERADMIN.value,
            granted_at=now,
            granted_by=user.id,  # self-granted at bootstrap (no prior caller exists)
        )
        db.add(grant)
        db.commit()

    print(f"created superadmin {username!r} (id={user.id})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
