"""
Availability slot model — individual bookable time slots.

This is the MOST CRITICAL table for the booking system.
Slots are pre-generated from doctor schedules and individually lockable
via SELECT ... FOR UPDATE for concurrency-safe booking.
"""

import uuid
from datetime import date, time

from sqlalchemy import (
    Date,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import SlotStatus
from app.models.base import BaseModel


class AvailabilitySlot(BaseModel):
    __tablename__ = "availability_slots"
    __table_args__ = (
        # Prevent duplicate slots for same doctor at same date+time
        UniqueConstraint(
            "doctor_id", "date", "start_time", name="uq_doctor_date_start",
        ),
        # Primary query index: "available slots for doctor X on date Y"
        Index("idx_slot_doctor_date_status", "doctor_id", "date", "status"),
        # Slot lookup by date range
        Index("idx_slot_date", "date"),
    )

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    status: Mapped[SlotStatus] = mapped_column(
        SQLEnum(SlotStatus, name="slot_status", create_constraint=True),
        default=SlotStatus.AVAILABLE,
        nullable=False,
    )

    # --- Relationships ---
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="slots")
    appointment: Mapped["Appointment | None"] = relationship(
        "Appointment", back_populates="slot", uselist=False,
    )

    def __repr__(self) -> str:
        return f"<Slot {self.date} {self.start_time}-{self.end_time} ({self.status.value})>"
