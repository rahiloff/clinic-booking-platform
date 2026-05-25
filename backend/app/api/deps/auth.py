"""
Doctor Booking Platform — Auth Dependencies

Provides current user extraction, JWT validation, and role-based access control.
These dependencies are used to protect endpoints.
"""

from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.enums import UserRole
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user import UserRepository

# HTTPBearer automatically checks for the Authorization header
# and extracts the Bearer token.
token_auth_scheme = HTTPBearer()


async def get_current_user(
    token_details: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency that extracts and validates the JWT, and returns the current User.
    Raises AuthenticationError if token is invalid, expired, or user is disabled.
    """
    token = token_details.credentials
    payload = decode_access_token(token)

    if not payload:
        raise AuthenticationError("Invalid or expired access token")

    if payload.get("token_type") != "access":
        raise AuthenticationError("Invalid token type")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationError("Token payload missing subject")

    from uuid import UUID
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise AuthenticationError("Invalid user ID format in token")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise AuthenticationError("User not found")

    if not user.is_active or user.deleted_at:
        raise AuthenticationError("User account is disabled or inactive")

    return user


def require_role(allowed_roles: list[UserRole]) -> Callable:
    """
    Dependency factory for role-based access control.
    Use this to restrict endpoints to specific roles.

    Example:
        @router.get("/admin", dependencies=[Depends(require_role([UserRole.ADMIN]))])
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise AuthorizationError(
                f"Requires one of roles: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return role_checker


# Shortcuts for common role requirements
async def require_patient(
    current_user: User = Depends(require_role([UserRole.PATIENT, UserRole.ADMIN]))
) -> User:
    """Dependency for patient-only (or admin) endpoints."""
    return current_user


async def require_doctor(
    current_user: User = Depends(require_role([UserRole.DOCTOR, UserRole.ADMIN]))
) -> User:
    """Dependency for doctor-only (or admin) endpoints."""
    return current_user


async def require_admin(
    current_user: User = Depends(require_role([UserRole.ADMIN]))
) -> User:
    """Dependency for admin-only endpoints."""
    return current_user
