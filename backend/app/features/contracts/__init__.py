"""Contracts feature slice -- contract admin CRUD (ADR-0043 / ADR-0047).

Importing this package imports the slice's `commands` module, which runs its
`register(...)` calls (ADR-0059) -- so importing `app.features.contracts`
anywhere is sufficient to register the slice's commands.
"""

from app.features.contracts.commands import (
    CreateContract,
    DeleteContract,
    EditContract,
)

__all__ = ["CreateContract", "DeleteContract", "EditContract"]
