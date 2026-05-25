"""User model — patients, doctors, and admins."""

import uuid

from sqlalchemy import Boolean, Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import UserRole
from app.models.base import BaseModel
from app.models.mixins.soft_delete import SoftDeleteMixin


class User(SoftDeleteMixin, BaseModel):
    __tablename__ = "users"

    firebase_uid: Mapped[str | None] = mapped_column(
        String(128), unique=True, index=True, nullable=True,
    )
    phone: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role", create_constraint=True),
        default=UserRole.PATIENT,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # --- Relationships ---
    doctor_profile: Mapped["Doctor | None"] = relationship(
        "Doctor", back_populates="user", uselist=False,
    )
    patient_appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="patient",
        foreign_keys="Appointment.patient_id",
    )

    def __repr__(self) -> str:
        return f"<User {self.full_name} ({self.role.value})>"
