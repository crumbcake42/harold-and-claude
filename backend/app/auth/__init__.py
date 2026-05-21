"""Auth module -- identity infrastructure (ADR-0070).

Owns the User / UserRole / Session entities, password hashing, the DB-backed
session lifecycle, the login / logout / me routes, and the `current_user`
FastAPI dependency that resolves a request into a `Caller`. It is a top-level
peer of `features/` -- not a feature -- because every request resolves it.

`current_user` is re-exported here because it is the cross-cutting dependency
every slice's routes inject; the entities and the rest of the surface are
imported from their specific submodules (`app.auth.entities`, etc.).
"""

from app.auth.security import current_user

__all__ = ["current_user"]
