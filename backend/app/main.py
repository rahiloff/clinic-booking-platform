"""
Doctor Booking Platform — FastAPI Application Factory

Creates and configures the FastAPI application with:
- CORS middleware
- API router mounting
- Lifespan management (startup/shutdown)
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_v1_router
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan handler.

    Startup: Any initialization (connection pools are lazy in SQLAlchemy).
    Shutdown: Dispose of database engine connections cleanly.
    """
    # --- Startup ---
    yield
    # --- Shutdown ---
    await engine.dispose()


def create_app() -> FastAPI:
    """
    Application factory pattern.

    Creates a configured FastAPI instance with all middleware and routers.
    This pattern makes testing easier and keeps config centralized.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="0.1.0",
        description="Doctor Appointment Booking Platform API",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # --- CORS Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Mount API Routers ---
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    return app


# Application instance — used by uvicorn
app = create_app()
