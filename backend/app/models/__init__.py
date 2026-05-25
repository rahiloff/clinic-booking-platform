"""
Doctor Booking Platform — Model Registry

Import all models here so that:
1. SQLAlchemy Base.metadata knows about all tables
2. Alembic can detect them for autogenerate
3. Relationship strings (e.g., "User") resolve correctly

Import order follows FK dependency chain.
"""

from app.models.base import BaseModel  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.clinic import Clinic  # noqa: F401
from app.models.doctor import Doctor  # noqa: F401
from app.models.doctor_schedule import DoctorSchedule  # noqa: F401
from app.models.availability_slot import AvailabilitySlot  # noqa: F401
from app.models.appointment import Appointment  # noqa: F401

__all__ = [
    "BaseModel",
    "User",
    "Clinic",
    "Doctor",
    "DoctorSchedule",
    "AvailabilitySlot",
    "Appointment",
]
