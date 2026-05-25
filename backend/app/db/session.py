"""
Doctor Booking Platform — Database Session Management

Provides:
- Async SQLAlchemy engine with connection pooling
- Async session factory
- Dependency-injectable session generator with auto-commit/rollback

Transaction Strategy (Unit of Work):
- get_db() yields a session for the duration of a request
- If the request succeeds → auto-commit
- If any exception is raised → auto-rollback
- Repositories use flush() only, never commit()
- This guarantees atomic operations per request
"""

from collections.abc import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

logger = structlog.get_logger()

# ---------- Engine ----------
# pool_pre_ping: Validates connections before use (handles stale connections)
# pool_size: Number of persistent connections in the pool
# max_overflow: Additional connections allowed beyond pool_size under load
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# ---------- Session Factory ----------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------- Dependency ----------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency-injectable async database session with auto-commit/rollback.

    Usage in routes:
        async def my_route(db: AsyncSession = Depends(get_db)):
            ...

    Transaction lifecycle:
        - Success: session.commit() is called automatically
        - Exception: session.rollback() is called, then exception re-raised
        - Always: session.close() is called
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
