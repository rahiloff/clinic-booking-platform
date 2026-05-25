"""Doctor schemas — request/response validation for doctor endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DoctorCreate(BaseModel):
    user_id: uuid.UUID
    clinic_id: uuid.UUID | None = None
    specialization: str = Field(max_length=100, examples=["Cardiologist"])
    bio: str | None = None
    consultation_fee: int | None = Field(None, ge=0, description="Fee in paise")
    experience_years: int | None = Field(None, ge=0, le=70)


class DoctorUpdate(BaseModel):
    specialization: str | None = Field(None, max_length=100)
    bio: str | None = None
    consultation_fee: int | None = Field(None, ge=0)
    experience_years: int | None = Field(None, ge=0, le=70)
    is_available: bool | None = None


class DoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    clinic_id: uuid.UUID | None
    specialization: str
    bio: str | None
    consultation_fee: int | None
    experience_years: int | None
    is_available: bool
    created_at: datetime


class DoctorListResponse(DoctorResponse):
    """Extended response with user name for listing pages."""
    doctor_name: str | None = None
    clinic_name: str | None = None
