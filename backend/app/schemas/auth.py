"""Authentication schemas — request/response validation for auth endpoints."""

from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserResponse


class FirebaseLoginRequest(BaseModel):
    """Payload received from frontend after Firebase OTP success."""
    firebase_token: str


class TokenData(BaseModel):
    """Data extracted from internal JWT token."""
    user_id: str
    role: str


class TokenResponse(BaseModel):
    """Response payload containing JWT token."""
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    """Combined response containing both token and user profile."""
    model_config = ConfigDict(from_attributes=True)

    token: TokenResponse
    user: UserResponse
