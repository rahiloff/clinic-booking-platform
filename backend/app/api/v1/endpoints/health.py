"""
Doctor Booking Platform — Health Check Endpoint

Production-grade health check that verifies:
- API is responsive
- PostgreSQL connection is alive
- Redis connection is alive

Used by Docker health checks, load balancers, and monitoring.
Returns standardized APIResponse format.
"""

import structlog
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings
from app.schemas.health import HealthData
from app.schemas.response import APIResponse, success

router = APIRouter()
logger = structlog.get_logger()


@router.get(
    "/health",
    response_model=APIResponse,
    summary="Health Check",
    description="Verify API, database, and cache connectivity.",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Deep health check endpoint.

    Checks:
        1. Database connectivity via a simple query
        2. Redis connectivity via PING command
    """
    # --- Check PostgreSQL ---
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"
        logger.warning("health_check_db_failed")

    # --- Check Redis ---
    redis_status = "healthy"
    try:
        redis_client = aioredis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.aclose()
    except Exception:
        redis_status = "unhealthy"
        logger.warning("health_check_redis_failed")

    # --- Build response ---
    all_healthy = db_status == "healthy" and redis_status == "healthy"
    overall = "healthy" if all_healthy else "degraded"

    health_data = HealthData(
        status=overall,
        environment=settings.ENVIRONMENT,
        version="0.1.0",
        database=db_status,
        redis=redis_status,
    )

    return success(data=health_data.model_dump(), message=f"System {overall}")
