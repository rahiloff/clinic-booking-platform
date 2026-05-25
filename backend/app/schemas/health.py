"""
Doctor Booking Platform — Health Check Schema

Pydantic models for the health check endpoint.
Uses the standardized APIResponse wrapper.
"""

from pydantic import BaseModel


class HealthData(BaseModel):
    """Health check data payload."""

    status: str
    environment: str
    version: str
    database: str
    redis: str
