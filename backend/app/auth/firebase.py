"""
Doctor Booking Platform — Firebase Admin Setup

Initializes the Firebase Admin SDK as a singleton and provides token verification.
"""

import structlog
import firebase_admin
from firebase_admin import auth, credentials

from app.core.config import settings
from app.core.exceptions import AuthenticationError

logger = structlog.get_logger()

# Initialize Firebase App Singleton
def _init_firebase():
    if not firebase_admin._apps:
        try:
            # When GOOGLE_APPLICATION_CREDENTIALS is set in the environment,
            # initialize_app() automatically discovers it.
            # In development, you can also pass a dict or path explicitly.
            firebase_admin.initialize_app()
            logger.info("firebase_initialized")
        except Exception as e:
            logger.warning("firebase_initialization_failed", error=str(e))

_init_firebase()


def verify_firebase_token(id_token: str) -> dict:
    """
    Verifies a Firebase ID token using the Admin SDK.

    Args:
        id_token: The JWT string received from the frontend client.

    Returns:
        dict: The decoded token payload (contains uid, phone_number, etc.)

    Raises:
        AuthenticationError: If the token is invalid, expired, or malformed.
    """
    try:
        # Check if revoking tokens is necessary; check_revoked=False is faster.
        decoded_token = auth.verify_id_token(id_token, check_revoked=False)
        return decoded_token
    except auth.InvalidIdTokenError:
        logger.warning("firebase_invalid_token")
        raise AuthenticationError("Invalid Firebase token")
    except auth.ExpiredIdTokenError:
        logger.warning("firebase_expired_token")
        raise AuthenticationError("Expired Firebase token")
    except Exception as e:
        logger.error("firebase_verification_error", error=str(e))
        raise AuthenticationError("Could not verify credentials")
