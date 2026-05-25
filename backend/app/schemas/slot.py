"""Slot schemas — request/response for availability slot endpoints."""

import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import SlotStatus


class SlotResponse(BaseModel):
    """Single slot returned in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    doctor_id: uuid.UUID
    date: date
    start_time: time
    end_time: time
    status: SlotStatus


class SlotQuery(BaseModel):
    """Query parameters for fetching available slots."""
    doctor_id: uuid.UUID
    date: date
    status: SlotStatus | None = SlotStatus.AVAILABLE


class ScheduleCreate(BaseModel):
    """Schema for creating/updating a doctor's weekly schedule."""
    day_of_week: int = Field(ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: time = Field(examples=["09:00:00"])
    end_time: time = Field(examples=["17:00:00"])
    slot_duration: int = Field(30, description="Minutes per slot")


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    doctor_id: uuid.UUID
    day_of_week: int
    start_time: time
    end_time: time
    slot_duration: int
    is_active: bool
