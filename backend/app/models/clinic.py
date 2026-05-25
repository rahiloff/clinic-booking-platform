"""Clinic model — medical practice or facility."""

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Clinic(BaseModel):
    __tablename__ = "clinics"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    timezone: Mapped[str] = mapped_column(
        String(50), default="Asia/Kolkata", nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # --- Relationships ---
    doctors: Mapped[list["Doctor"]] = relationship("Doctor", back_populates="clinic")

    def __repr__(self) -> str:
        return f"<Clinic {self.name}>"
