"""
Doctor Booking Platform — Database Session Management

Provides:
- Async SQLAlchemy engine with connection pooling
- Async session factory
- Dependency-injectable session generator
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

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
    Dependency-injectable async database session.

    Usage in routes:
        async def my_route(db: AsyncSession = Depends(get_db)):
            ...

    Sessions are automatically closed after the request completes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
