"""Fake invariants for dispatcher smoke tests."""

from typing import Any

from sqlalchemy.orm import Session

from app.engine.command import Invariant


class ValueIsPositive(Invariant):
    """SmokeEntity.value must be > 0. Serializable primitive (default)."""

    primitive = "serializable"

    @classmethod
    def check(cls, session: Session, target: Any) -> bool:
        return getattr(target, "value", 0) > 0
