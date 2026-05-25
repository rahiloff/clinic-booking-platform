"""
Doctor Booking Platform — API Dependencies

Shared dependencies for route handlers.
"""

from app.db.session import get_db

__all__ = ["get_db"]
