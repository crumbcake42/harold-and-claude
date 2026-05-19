from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import auth, healthcheck

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

app.include_router(healthcheck.router)
app.include_router(auth.router)
