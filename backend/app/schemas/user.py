"""User schemas — request/response validation for user endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import UserRole


# --- Request Schemas ---

class UserCreate(BaseModel):
    """Schema for creating a new user (internal, after Firebase auth)."""
    phone: str = Field(max_length=20, examples=["+919876543210"])
    full_name: str = Field(max_length=255, examples=["Rahil Shah"])
    role: UserRole = UserRole.PATIENT
    firebase_uid: str | None = Field(None, max_length=128)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: str | None = Field(None, max_length=255)
    is_active: bool | None = None


# --- Response Schemas ---

class UserResponse(BaseModel):
    """User data returned in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    phone: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
