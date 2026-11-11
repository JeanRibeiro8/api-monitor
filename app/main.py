from fastapi import FastAPI
from sqlalchemy import text

from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.monitors import router as monitors_router
from app.core.config import settings
from app.db.database import engine

app = FastAPI(title=settings.app_name, version="1.0.0", description="Monitor external HTTP services and store availability history.")
app.include_router(monitors_router)
app.include_router(dashboard_router)


@app.get("/health", tags=["Health"])
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        return {"status": "degraded", "database": "unavailable"}
