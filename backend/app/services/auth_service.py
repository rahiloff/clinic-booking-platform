"""
Doctor Booking Platform — Authentication Service

Handles Firebase token verification, automatic user provisioning,
and internal JWT issuance. Business logic resides here.
"""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.firebase import verify_firebase_token
from app.core.enums import UserRole
from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import LoginResponse, TokenResponse

logger = structlog.get_logger()


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def login_with_firebase(self, firebase_token: str) -> LoginResponse:
        """
        Processes a Firebase ID token to log a user in or register them.

        1. Verify Firebase token.
        2. Extract UID and phone.
        3. Find existing user (by UID or phone).
        4. Auto-provision new patient if none exists.
        5. Generate internal JWT access token.
        """
        # 1. Verify token securely
        token_payload = verify_firebase_token(firebase_token)

        firebase_uid = token_payload.get("uid")
        phone_number = token_payload.get("phone_number")

        if not firebase_uid:
            raise AuthenticationError("Firebase token missing UID")
        
        # Phone numbers are expected because we use OTP login.
        # Fallback handling might be needed if using email auth later.
        if not phone_number:
            raise AuthenticationError("Firebase token missing phone number")

        # 2 & 3. Find user
        user = await self.user_repo.get_by_firebase_uid(firebase_uid)

        if not user:
            # Fallback: check if phone exists (maybe registered by admin earlier)
            user = await self.user_repo.get_by_phone(phone_number)
            if user:
                # Link existing user to this Firebase UID
                user.firebase_uid = firebase_uid
                logger.info("firebase_uid_linked", user_id=str(user.id))

        # 4. Auto-provision if entirely new
        if not user:
            user = User(
                firebase_uid=firebase_uid,
                phone=phone_number,
                full_name="New Patient",  # To be updated by user later
                role=UserRole.PATIENT,
                is_active=True,
            )
            self.db.add(user)
            await self.db.flush()
            logger.info("new_user_provisioned", user_id=str(user.id), role=user.role.value)

        # Ensure user is active before granting access
        if not user.is_active or user.deleted_at:
            logger.warning("inactive_user_login_attempt", user_id=str(user.id))
            raise AuthenticationError("User account is disabled or inactive")

        # 5. Generate internal JWT
        access_token = create_access_token(
            subject=str(user.id),
            role=user.role.value,
        )

        logger.info("user_login_success", user_id=str(user.id), role=user.role.value)

        token_response = TokenResponse(access_token=access_token)
        return LoginResponse(token=token_response, user=user)
