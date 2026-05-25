"""
Doctor Booking Platform — API Dependencies

Shared FastAPI dependencies used across route handlers.
Centralized here to avoid duplication and ensure consistency.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db  # noqa: F401 — re-exported for convenience


# Future dependencies will be added here:
# - get_current_user (JWT validation)
# - get_current_active_user (active check)
# - require_role("doctor") (role-based access)
