"""
Doctor Booking Platform — Health Check Schema

Pydantic models for the health check endpoint response.
"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response schema for GET /api/v1/health."""

    status: str
    environment: str
    version: str
    database: str
    redis: str
