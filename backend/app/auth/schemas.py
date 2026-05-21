"""Route request/response DTOs for the auth module.

Kept separate from the auth routes themselves (ADR-0070): these are the HTTP
wire contract the generated frontend client consumes. The login response is
the `Caller` model (`app.engine.caller`); only the request body needs a
dedicated DTO here.
"""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str
