"""
Doctor Booking Platform — Custom Exception Hierarchy

Centralized exceptions for the entire application.
Each exception maps to a specific HTTP status code and error_code string.

Usage in services:
    from app.core.exceptions import NotFoundError, SlotConflictError

    raise NotFoundError("Doctor")
    raise SlotConflictError()

These are caught globally by handlers.py — no scattered try/except needed.
"""


class AppException(Exception):
    """Base exception for all application-level errors."""

    def __init__(
        self,
        message: str = "An error occurred",
        error_code: str = "APP_ERROR",
        status_code: int = 400,
        details: dict | list | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


# ---- Authentication & Authorization ----

class AuthenticationError(AppException):
    """Invalid or missing credentials (401)."""

    def __init__(self, message: str = "Authentication failed", details=None):
        super().__init__(message, "AUTH_ERROR", 401, details)


class AuthorizationError(AppException):
    """Valid credentials but insufficient permissions (403)."""

    def __init__(self, message: str = "Permission denied", details=None):
        super().__init__(message, "FORBIDDEN", 403, details)


# ---- Resource Errors ----

class NotFoundError(AppException):
    """Requested resource does not exist (404)."""

    def __init__(self, resource: str = "Resource", details=None):
        super().__init__(f"{resource} not found", "NOT_FOUND", 404, details)


class ConflictError(AppException):
    """Resource state conflict (409)."""

    def __init__(self, message: str = "Resource conflict", error_code: str = "CONFLICT", details=None):
        super().__init__(message, error_code, 409, details)


# ---- Booking-Specific Errors ----

class SlotConflictError(ConflictError):
    """Appointment slot is already taken or unavailable."""

    def __init__(self, details=None):
        super().__init__("Booking slot already taken", "SLOT_CONFLICT", details)


class DuplicateBookingError(ConflictError):
    """Patient already has an active booking for this doctor/date."""

    def __init__(self, details=None):
        super().__init__("You already have an active booking", "DUPLICATE_BOOKING", details)


# ---- Validation ----

class InputValidationError(AppException):
    """Business-level validation failure (422)."""

    def __init__(self, message: str = "Validation failed", details=None):
        super().__init__(message, "VALIDATION_ERROR", 422, details)


# ---- Rate Limiting ----

class RateLimitError(AppException):
    """Too many requests (429)."""

    def __init__(self, details=None):
        super().__init__("Rate limit exceeded", "RATE_LIMITED", 429, details)


# ---- Server Errors ----

class DatabaseError(AppException):
    """Unexpected database error (500). Details are logged, not exposed."""

    def __init__(self, message: str = "A database error occurred", details=None):
        super().__init__(message, "DATABASE_ERROR", 500, details)
