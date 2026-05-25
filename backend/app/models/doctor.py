"""Doctor model — doctor profile linked to a user account."""

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Doctor(BaseModel):
    __tablename__ = "doctors"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False,
    )
    clinic_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clinics.id"), nullable=True, index=True,
    )
    specialization: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True,
    )
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    consultation_fee: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Fee in smallest currency unit (paise)",
    )
    experience_years: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # --- Relationships ---
    user: Mapped["User"] = relationship("User", back_populates="doctor_profile")
    clinic: Mapped["Clinic | None"] = relationship("Clinic", back_populates="doctors")
    schedules: Mapped[list["DoctorSchedule"]] = relationship(
        "DoctorSchedule", back_populates="doctor",
    )
    slots: Mapped[list["AvailabilitySlot"]] = relationship(
        "AvailabilitySlot", back_populates="doctor",
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment", back_populates="doctor",
    )

    def __repr__(self) -> str:
        return f"<Doctor {self.specialization} (user={self.user_id})>"
