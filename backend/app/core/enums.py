"""
Doctor Booking Platform — Centralized Enums

All enum types used across models, schemas, and services.
Using Python str+Enum so values serialize to strings naturally.
SQLAlchemy creates native PostgreSQL ENUM types for type safety at the DB level.
"""

import enum


class UserRole(str, enum.Enum):
    """User roles for access control."""
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class SlotStatus(str, enum.Enum):
    """Availability slot lifecycle states."""
    AVAILABLE = "available"
    BOOKED = "booked"
    BLOCKED = "blocked"
    EXPIRED = "expired"


class AppointmentStatus(str, enum.Enum):
    """Appointment lifecycle states."""
    BOOKED = "booked"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
