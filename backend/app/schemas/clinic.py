"""Clinic schemas — request/response validation for clinic endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClinicCreate(BaseModel):
    name: str = Field(max_length=255, examples=["City Health Clinic"])
    address: str | None = None
    phone: str | None = Field(None, max_length=20)
    city: str | None = Field(None, max_length=100)
    timezone: str = Field("Asia/Kolkata", max_length=50)


class ClinicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    address: str | None
    phone: str | None
    city: str | None
    timezone: str
    is_active: bool
    created_at: datetime
