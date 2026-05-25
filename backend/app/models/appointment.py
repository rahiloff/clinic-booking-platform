"""
Appointment model — booking records linking patients to doctor slots.

Supports full booking lifecycle: booked → confirmed → completed/cancelled/no_show.
Partial unique index ensures only one active appointment per slot.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import AppointmentStatus
from app.models.base import BaseModel


class Appointment(BaseModel):
    __tablename__ = "appointments"
    __table_args__ = (
        # Patient dashboard: "my upcoming/past appointments"
        Index("idx_appt_patient_status", "patient_id", "status"),
        # Doctor dashboard: "today's appointments"
        Index("idx_appt_doctor_status", "doctor_id", "status"),
        # Safety net: only one non-cancelled appointment per slot
        Index(
            "idx_unique_active_slot",
            "slot_id",
            unique=True,
            postgresql_where=text("status != 'cancelled'"),
        ),
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False,
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False,
    )
    slot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("availability_slots.id"), nullable=False,
    )
    status: Mapped[AppointmentStatus] = mapped_column(
        SQLEnum(AppointmentStatus, name="appointment_status", create_constraint=True),
        default=AppointmentStatus.BOOKED,
        nullable=False,
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Doctor's notes after appointment",
    )

    # --- Cancellation tracking ---
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    cancelled_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True,
    )
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Relationships ---
    patient: Mapped["User"] = relationship(
        "User", back_populates="patient_appointments", foreign_keys=[patient_id],
    )
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="appointments")
    slot: Mapped["AvailabilitySlot"] = relationship(
        "AvailabilitySlot", back_populates="appointment",
    )
    canceller: Mapped["User | None"] = relationship("User", foreign_keys=[cancelled_by])

    def __repr__(self) -> str:
        return f"<Appointment {self.status.value} patient={self.patient_id}>"
