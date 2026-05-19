from fastapi import FastAPI

from app.routes import healthcheck

app = FastAPI(title="sca-tracker", version="0.0.0")
app.include_router(healthcheck.router)
