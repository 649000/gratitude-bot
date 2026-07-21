import logging
import platform
import sys
from datetime import UTC, datetime

from fastapi import APIRouter
from sqlalchemy import text

from app.config import settings
from app.state import app_start_time

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check() -> dict:
    checks: dict[str, str] = {}

    try:
        from app.database import engine

        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()
        checks["database"] = "healthy"
    except Exception as exc:
        checks["database"] = f"unhealthy: {exc}"

    uptime = str(datetime.now(UTC) - app_start_time) if app_start_time else "unknown"

    return {
        "status": "ok" if checks["database"] == "healthy" else "degraded",
        "service": settings.app_name,
        "version": "0.1.0",
        "environment": settings.env,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "uptime": uptime,
        "checks": checks,
    }
