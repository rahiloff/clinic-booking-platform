"""
Doctor Booking Platform — FastAPI Application Factory

Creates and configures the FastAPI application with:
- CORS middleware
- Request logging middleware (request IDs + duration tracking)
- Global exception handlers (standardized error responses)
- Structured logging (JSON in production, pretty in development)
- API router mounting
- Lifespan management (startup/shutdown)
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.api.v1.router import api_v1_router
from app.db.session import engine
from app.middleware.request_logging import RequestLoggingMiddleware

import sentry_sdk

logger = structlog.get_logger()

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        environment=settings.ENVIRONMENT,
    )

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan handler.

    Startup: Initialize logging, log application start.
    Shutdown: Dispose of database engine connections cleanly.
    """
    # --- Startup ---
    setup_logging(environment=settings.ENVIRONMENT)
    logger.info(
        "application_started",
        project=settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
    )
    yield
    # --- Shutdown ---
    logger.info("application_shutting_down")
    await engine.dispose()


def create_app() -> FastAPI:
    """
    Application factory pattern.

    Creates a configured FastAPI instance with all middleware,
    exception handlers, and routers.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description=(
            "Doctor Appointment Booking Platform API.\\n\\n"
            "## Authentication\\n"
            "All protected routes require a JWT Bearer token obtained from `/api/v1/auth/login`.\\n\\n"
            "## Responses\\n"
            "All endpoints return a standardized JSON structure: `{success: bool, message: str, data: dict|list}`."
        ),
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # --- Exception Handlers (must be before middleware) ---
    register_exception_handlers(app)

    # --- Middleware (order matters: last added = first executed) ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    # --- Mount API Routers ---
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    return app


# Application instance — used by uvicorn
app = create_app()
