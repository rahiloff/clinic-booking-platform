"""
Doctor Booking Platform — Global Exception Handlers

Registered once in main.py. Catches all exceptions and returns
standardized JSON error responses. No try/except blocks needed in routes.

Response format:
    {
        "success": false,
        "message": "Human-readable error",
        "error_code": "MACHINE_READABLE_CODE",
        "details": null
    }
"""

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import AppException

logger = structlog.get_logger()


def _error_response(
    status_code: int,
    message: str,
    error_code: str,
    details: dict | list | None = None,
) -> JSONResponse:
    """Build a standardized error JSON response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "error_code": error_code,
            "details": details,
        },
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle all custom AppException subclasses."""
    logger.warning(
        "app_exception",
        error_code=exc.error_code,
        message=exc.message,
        path=request.url.path,
    )
    return _error_response(exc.status_code, exc.message, exc.error_code, exc.details)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic/FastAPI request validation errors."""
    logger.warning(
        "validation_error",
        path=request.url.path,
        errors=exc.errors(),
    )
    return _error_response(422, "Validation error", "VALIDATION_ERROR", exc.errors())


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """Handle database constraint violations (unique, FK, etc.)."""
    logger.error(
        "integrity_error",
        path=request.url.path,
        detail=str(exc.orig),
    )
    return _error_response(409, "Database constraint violation", "CONFLICT")


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all for unexpected errors. Log full details, return generic message."""
    logger.exception(
        "unhandled_exception",
        path=request.url.path,
        error_type=type(exc).__name__,
    )
    return _error_response(500, "Internal server error", "INTERNAL_ERROR")


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app. Called once in main.py."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
