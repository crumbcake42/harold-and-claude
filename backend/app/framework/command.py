"""Command base class + explicit registry per ADR-0059.

Every state-changing operation in the system is a Command subclass with
declared metadata (target entity, transition, authorization, invariants,
cascade, destructive flag) and a nested Payload Pydantic model. The
dispatcher (app.framework.dispatcher) consumes the declarations to run the
ADR-0012 / ADR-0009 / ADR-0010 / ADR-0008 / ADR-0011 pipeline.

The registry is an explicit dict mapping command-name -> Command class.
Subclasses register via register(MyCommand) -- typically at module-import
time alongside the class definition. Tests can build isolated registries
by reading the module dict.

Cascade-mechanism guards (registry-load-time destructive-cannot-cascade
check; drift test) and the cascade-invoke entry point land in a follow-up
commit per ADR-0060. This module declares the cascade / destructive
attributes so commands can be authored against the final surface from
the start.
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Protocol
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session


class Caller(Protocol):
    """The actor on whose behalf a command runs.

    1.3a defines the minimum surface (an id) for smoke testing; M1+ adds
    role / relationship attrs as the auth predicates land per ADR-0047.
    """

    id: UUID


class Invariant(ABC):
    """Well-formedness invariant declared on the schema element it constrains
    (ADR-0010); enforced by the dispatcher's invariant step after the handler
    has applied its mutation.

    `primitive` selects the isolation primitive per ADR-0056: "serializable"
    relies on the dispatcher's per-transaction SERIALIZABLE isolation; "advisory_lock"
    additionally acquires pg_try_advisory_xact_lock at the lock key returned by
    `lock_key(target)`. Lock-key strings must use a registered LockNamespace
    prefix (app.framework.locks.LockNamespace).
    """

    primitive: ClassVar[str] = "serializable"

    @classmethod
    def lock_key(cls, target: Any) -> str | None:
        """Return the advisory-lock key for the target; None for serializable
        invariants. Overridden by advisory-lock-opt-in invariants.
        """
        return None

    @classmethod
    @abstractmethod
    def check(cls, session: Session, target: Any) -> bool:
        """Return True if the invariant holds for the target; False to reject."""
        ...


class Command(ABC):
    """Base class for every state-changing operation.

    Subclasses declare metadata as class attrs + a nested Payload Pydantic
    model + a handler method. The dispatcher consumes the declarations to
    run the ADR-0012 / 0009 / 0010 / 0008 / 0011 pipeline.

    Class attrs:
      target_entity: SQLAlchemy model class the command operates on.
      transition_name: lifecycle transition name per ADR-0009 (None for
          non-lifecycle commands).
      authorization: callable (caller, command_cls, target_or_payload) -> bool
          evaluated first per ADR-0012.
      invariants: list of Invariant subclasses revalidated after handler per
          ADR-0010.
      cascade: list of sub-Command classes invoked from the handler per
          design pattern #5. Cascade-invoke machinery lands in the next
          commit per ADR-0060.
      destructive: marks commands whose effect is destructive (cascade
          guard per ADR-0060). Default False.
      cascade_allowed_destructive: parents legitimately invoking a
          destructive sub-command must declare this True to satisfy the
          ADR-0060 registry-load-time check. Default False.

    Subclasses declare Payload as a nested Pydantic model and implement
    handler(self, session, payload) -> target_entity_instance.
    """

    # Pipeline metadata -- subclasses override.
    target_entity: ClassVar[type]
    transition_name: ClassVar[str | None] = None
    authorization: ClassVar[Any]  # callable(caller, command_cls, target_or_payload) -> bool
    invariants: ClassVar[list[type[Invariant]]] = []
    cascade: ClassVar[list[type["Command"]]] = []
    destructive: ClassVar[bool] = False
    cascade_allowed_destructive: ClassVar[bool] = False

    # Nested payload schema -- subclasses MUST override with a Pydantic model.
    Payload: ClassVar[type[BaseModel]]

    @abstractmethod
    def handler(self, session: Session, payload: BaseModel) -> Any:
        """Apply the command's mutation. Returns the entity that was mutated /
        created -- the dispatcher's history step uses this as the capture target.
        """
        ...

    @classmethod
    def name(cls) -> str:
        return cls.__name__


# ---- Registry ----

_REGISTRY: dict[str, type[Command]] = {}


def register(command_cls: type[Command]) -> type[Command]:
    """Register a Command class. Idempotent on identity; raises on name collision
    with a different class. Returns the class so it can be used as a decorator
    if a subclass prefers that style.
    """
    name = command_cls.name()
    existing = _REGISTRY.get(name)
    if existing is not None and existing is not command_cls:
        raise ValueError(
            f"Command name collision: {name!r} already registered to {existing!r}; "
            f"cannot register {command_cls!r}"
        )
    _REGISTRY[name] = command_cls
    return command_cls


def get_command(name: str) -> type[Command]:
    """Look up a registered Command class by name. Raises KeyError if absent."""
    return _REGISTRY[name]


def registered_commands() -> dict[str, type[Command]]:
    """Snapshot of the registry. Returned dict is a copy; mutating it does
    not affect the registry."""
    return dict(_REGISTRY)


def _clear_registry_for_tests() -> None:
    """Test-only: reset the registry between tests that build isolated command
    sets. NOT for production use.
    """
    _REGISTRY.clear()
