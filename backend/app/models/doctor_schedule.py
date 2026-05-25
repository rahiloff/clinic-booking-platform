"""Doctor schedule model — recurring weekly availability template."""

import uuid
from datetime import time

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    SmallInteger,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class DoctorSchedule(BaseModel):
    __tablename__ = "doctor_schedules"
    __table_args__ = (
        UniqueConstraint("doctor_id", "day_of_week", name="uq_doctor_day"),
        CheckConstraint(
            "day_of_week >= 0 AND day_of_week <= 6", name="ck_valid_day_of_week",
        ),
        CheckConstraint("start_time < end_time", name="ck_schedule_time_order"),
        CheckConstraint(
            "slot_duration IN (15, 20, 30, 45, 60)", name="ck_valid_slot_duration",
        ),
    )

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False, index=True,
    )
    day_of_week: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="0=Monday, 6=Sunday",
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    slot_duration: Mapped[int] = mapped_column(
        SmallInteger, default=30, nullable=False, comment="Duration in minutes",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # --- Relationships ---
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="schedules")

    def __repr__(self) -> str:
        return f"<DoctorSchedule day={self.day_of_week} {self.start_time}-{self.end_time}>"
