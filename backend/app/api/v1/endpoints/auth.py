"""
Doctor Booking Platform — Authentication Endpoints

Handles login and user profile retrieval.
Kept extremely thin by delegating to AuthService and Dependencies.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.deps.auth import get_current_user
from app.models.user import User
from app.schemas.auth import FirebaseLoginRequest, LoginResponse
from app.schemas.response import APIResponse, success
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/login",
    response_model=APIResponse,
    summary="Login via Firebase Token",
    description="Validates a Firebase ID token and returns an internal JWT access token.",
)
async def login(
    request: FirebaseLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Login endpoint.
    Automatically provisions a new patient if the user doesn't exist.
    """
    auth_service = AuthService(db)
    login_result = await auth_service.login_with_firebase(request.firebase_token)
    
    return success(
        data=login_result.model_dump(),
        message="Login successful",
    )


@router.get(
    "/me",
    response_model=APIResponse,
    summary="Get Current User",
    description="Returns the profile of the currently authenticated user.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Current user endpoint.
    Protected by JWT dependency.
    """
    user_data = UserResponse.model_validate(current_user)
    return success(
        data=user_data.model_dump(),
        message="Profile retrieved successfully",
    )
