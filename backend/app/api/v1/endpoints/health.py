"""
Doctor Booking Platform — Health Check Endpoint

Production-grade health check that verifies:
- API is responsive
- PostgreSQL connection is alive
- Redis connection is alive

Used by Docker health checks, load balancers, and monitoring.
"""

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Verify API, database, and cache connectivity.",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
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

    # --- Check Redis ---
    redis_status = "healthy"
    try:
        redis_client = aioredis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.aclose()
    except Exception:
        redis_status = "unhealthy"

    # --- Determine overall status ---
    all_healthy = db_status == "healthy" and redis_status == "healthy"

    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        environment=settings.ENVIRONMENT,
        version="0.1.0",
        database=db_status,
        redis=redis_status,
    )
