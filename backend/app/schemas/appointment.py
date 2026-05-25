"""Appointment schemas — request/response for booking endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import AppointmentStatus


class AppointmentCreate(BaseModel):
    """Schema for booking an appointment."""
    slot_id: uuid.UUID
    reason: str | None = Field(None, max_length=500)


class AppointmentCancel(BaseModel):
    """Schema for cancelling an appointment."""
    cancellation_reason: str | None = Field(None, max_length=500)


class AppointmentResponse(BaseModel):
    """Appointment data returned in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    slot_id: uuid.UUID
    status: AppointmentStatus
    reason: str | None
    notes: str | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    created_at: datetime


class AppointmentDetailResponse(AppointmentResponse):
    """Extended response with joined data for detail views."""
    doctor_name: str | None = None
    patient_name: str | None = None
    slot_date: str | None = None
    slot_time: str | None = None
