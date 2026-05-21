"""Command base class + explicit registry per ADR-0059.

Every state-changing operation in the system is a Command subclass with
declared metadata (target entity, transition, authorization, invariants,
cascade, destructive flag) and a nested Payload Pydantic model. The
dispatcher (app.engine.dispatcher) consumes the declarations to run the
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

import ast
import inspect
import textwrap
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.engine.caller import Caller
from app.engine.exceptions import DestructiveCascadeViolation

if TYPE_CHECKING:
    from app.engine.dispatcher import Dispatcher


class Invariant(ABC):
    """Well-formedness invariant declared on the schema element it constrains
    (ADR-0010); enforced by the dispatcher's invariant step after the handler
    has applied its mutation.

    `primitive` selects the isolation primitive per ADR-0056: "serializable"
    relies on the dispatcher's per-transaction SERIALIZABLE isolation; "advisory_lock"
    additionally acquires pg_try_advisory_xact_lock at the lock key returned by
    `lock_key(target)`. Lock-key strings must use a registered LockNamespace
    prefix (app.engine.locks.LockNamespace).
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
      creates: True for commands that create their target entity, False
          for commands that mutate an existing one (ADR-0075). The
          dispatcher reads it to stamp the ADR-0072 audit-metadata columns
          -- created_* only when creates is True, updated_* always. Default
          False (most commands mutate).

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
    creates: ClassVar[bool] = False

    # Nested payload schema -- subclasses MUST override with a Pydantic model.
    Payload: ClassVar[type[BaseModel]]

    # Dispatcher-set instance attrs (populated before handler runs by the
    # dispatcher). Not part of the public Command surface; consumers should
    # access these only via cascade_invoke() in the dispatcher module. None
    # defaults make Pyright aware of the attrs; the dispatcher's assignments
    # shadow these with instance values prior to any handler call.
    _session: Session | None = None
    _command_id: UUID | None = None
    _caller: "Caller | None" = None
    _dispatcher: "Dispatcher | None" = None

    def resolve_target(self, session: Session, payload: BaseModel) -> Any:
        """Return the existing entity instance the command operates on, or
        None for creation commands. Lifecycle-affecting commands (where
        `transition_name is not None`) MUST override this -- the dispatcher
        uses it to read `from_state` for the lifecycle gate and the history
        record. Default returns None (suitable for non-lifecycle commands
        and creation commands).
        """
        return None

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


# ---- Cascade safeguards (ADR-0060) ----


def validate_registry() -> None:
    """Registry-load-time guard per ADR-0060: no command marked
    `destructive = True` may appear in any other command's `cascade = [...]`
    list unless the parent declares `cascade_allowed_destructive = True`.

    Call at app startup (after all command modules have imported) and from
    tests that build isolated command sets. Raises DestructiveCascadeViolation
    on the first offending pair; fix and re-run.
    """
    for parent_cls in _REGISTRY.values():
        if parent_cls.cascade_allowed_destructive:
            continue
        for child_cls in parent_cls.cascade:
            if child_cls.destructive:
                raise DestructiveCascadeViolation(parent_cls.name(), child_cls.name())


def extract_handler_cascade_invocations(command_cls: type[Command]) -> set[str]:
    """Static-analysis drift check per ADR-0060: extract the Command class
    names a command's handler invokes via `cascade_invoke(...)`.

    Walks the handler source via AST; matches Call nodes whose func is
    `cascade_invoke` (bare or attribute). For each match, extracts the second
    positional argument's symbol name if it is a Name node (e.g.,
    `cascade_invoke(self, ChildCommand, payload, session)` -> {"ChildCommand"}).
    Dynamic dispatch (`cascade_invoke(self, some_var, ...)` where some_var is
    chosen at runtime) is invisible to this check -- a known limitation.

    Pair with the declared `cascade = [...]` list in a unit test to detect
    drift (declared but not invoked, or invoked but not declared).
    """
    try:
        source = inspect.getsource(command_cls.handler)
    except (OSError, TypeError):
        return set()
    tree = ast.parse(textwrap.dedent(source))
    invoked: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        is_cascade_call = (isinstance(func, ast.Name) and func.id == "cascade_invoke") or (
            isinstance(func, ast.Attribute) and func.attr == "cascade_invoke"
        )
        if not is_cascade_call:
            continue
        # Second positional arg is the child command class (first is `self`).
        if len(node.args) >= 2 and isinstance(node.args[1], ast.Name):
            invoked.add(node.args[1].id)
    return invoked


def cascade_drift_report() -> dict[str, dict[str, set[str]]]:
    """Walk every registered command; for each, compare declared cascade
    against statically-extracted handler invocations. Returns a per-command
    dict with `declared`, `invoked`, `declared_not_invoked`, `invoked_not_declared`
    sets (by class name). Empty `invoked_not_declared` is the safety-critical
    invariant; `declared_not_invoked` is a cleanliness signal.
    """
    report: dict[str, dict[str, set[str]]] = {}
    for parent_cls in _REGISTRY.values():
        declared = {child.name() for child in parent_cls.cascade}
        invoked = extract_handler_cascade_invocations(parent_cls)
        report[parent_cls.name()] = {
            "declared": declared,
            "invoked": invoked,
            "declared_not_invoked": declared - invoked,
            "invoked_not_declared": invoked - declared,
        }
    return report
