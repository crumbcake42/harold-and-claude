from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.features.contracts  # noqa: F401  -- importing the slice registers its commands (ADR-0059)
from app.auth.routes import router as auth_router
from app.config import settings
from app.features.contracts.routes import router as contracts_router
from app.framework.command import validate_registry
from app.framework.error_handlers import register_error_handlers
from app.routes import healthcheck

# Registry-load-time guard (ADR-0060): fails loudly at import if a
# destructive command is cascaded without an explicit opt-in.
validate_registry()

app = FastAPI(title="sca-tracker", version="0.0.0")

# CORS for the local frontend dev server (and the deployed frontend origin
# at production time, set via settings.frontend_origin). allow_credentials=True
# is load-bearing -- the session cookie won't be sent cross-origin without it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Translate dispatcher-surfaced exceptions (ADR-0011 rejections, ADR-0058
# contention) to HTTP responses.
register_error_handlers(app)

app.include_router(healthcheck.router)
app.include_router(auth_router)
app.include_router(contracts_router)
