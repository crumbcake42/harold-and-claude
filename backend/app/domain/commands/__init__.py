"""Domain command package.

Importing this package imports every command module, which runs each
module's `register(...)` calls (ADR-0059) -- so by the time the app
entrypoint has imported `app.domain.commands`, the registry is complete.
The entrypoint then calls `validate_registry()` (ADR-0060) once.

Add an import line here when a new command module lands.
"""

from app.domain.commands import contract  # noqa: F401  -- registers Contract CRUD
