"""Exceptions surfaced by the command dispatcher.

CommandRejected and its subclasses correspond to the rejection paths in
ADR-0011 (lifecycle / invariant violations) and ADR-0012 (authorization
denied). On any of these the dispatcher rolls back -- no mutation, no
history row -- and the caller receives the typed exception with a reason
suitable for translation to a user-facing message at the transport layer.

TransientContention is surfaced after the dispatcher's retry loop (per
ADR-0058 / Step 1.3a) exhausts its attempts on advisory-lock-unavailable
or Postgres serialization_failure; routes translate it to HTTP 409 / 503.
AdvisoryLockUnavailable is an internal signal raised by the invariant
step's lock acquisition; it is caught by the retry loop, not surfaced to
callers.
"""


class CommandRejected(Exception):
    """Base for pipeline-rejection paths (auth / lifecycle / invariant).

    Carries a `reason` string suitable for the caller to translate into a
    user-facing message. Per ADR-0011, no mutation persists and no history
    row is written when a rejection fires.
    """

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class AuthorizationDenied(CommandRejected):
    """Authorization predicate evaluated to False (ADR-0012)."""


class LifecycleViolation(CommandRejected):
    """The declared transition is not permitted from the entity's current
    state (ADR-0009 + ADR-0011).
    """


class InvariantViolation(CommandRejected):
    """A well-formedness invariant failed revalidation after the proposed
    change was applied (ADR-0010 + ADR-0011).
    """


class EntityNotFound(CommandRejected):
    """A command's target entity does not exist, or has been soft-deleted.

    Raised by edit / delete handlers when resolve-by-id finds no live row.
    Modeled as a CommandRejected so it shares the pipeline's rollback and
    the route layer's typed-rejection translation; the transport layer
    maps it to HTTP 404.
    """


class AdvisoryLockUnavailable(Exception):
    """Internal signal: pg_try_advisory_xact_lock returned False.

    Raised inside the invariant step when an advisory-lock-opt-in invariant
    cannot acquire its lock (ADR-0056). Caught by the dispatcher's retry
    loop; never surfaced to callers directly (the loop converts retry
    exhaustion into TransientContention).
    """

    def __init__(self, lock_key: str) -> None:
        super().__init__(f"advisory lock unavailable for key: {lock_key}")
        self.lock_key = lock_key


class CascadeViolation(Exception):
    """A handler attempted to cascade-invoke a sub-command that was not
    declared in its `cascade = [...]` list (ADR-0060). Indicates a
    declaration drift or a runtime dispatch bug; fails closed to prevent
    accidental auth-bypassed invocation of arbitrary commands.
    """

    def __init__(self, parent_name: str, child_name: str) -> None:
        super().__init__(
            f"command {parent_name!r} attempted to cascade-invoke "
            f"{child_name!r}, which is not in its declared cascade list"
        )
        self.parent_name = parent_name
        self.child_name = child_name


class DestructiveCascadeViolation(Exception):
    """Registry-load-time check (ADR-0060): a command marked `destructive = True`
    appears in another command's `cascade = [...]` list, but the parent did not
    declare `cascade_allowed_destructive = True`. Raised at registry validation
    (typically app startup), not at command dispatch -- the goal is to fail
    loudly before any request runs.
    """

    def __init__(self, parent_name: str, child_name: str) -> None:
        super().__init__(
            f"command {parent_name!r} cascades destructive command {child_name!r} "
            f"without declaring cascade_allowed_destructive = True"
        )
        self.parent_name = parent_name
        self.child_name = child_name


class TransientContention(Exception):
    """Retry loop exhausted on advisory-lock / serialization_failure (ADR-0058).

    Carries the underlying cause for diagnostics. Route layer translates to
    a transient-failure response (HTTP 409 / 503); the user is expected to
    retry the request.
    """

    def __init__(self, attempts: int, last_cause: BaseException) -> None:
        super().__init__(
            f"transient contention; retry loop exhausted after {attempts} attempts"
        )
        self.attempts = attempts
        self.last_cause = last_cause
