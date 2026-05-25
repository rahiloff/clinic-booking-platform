"""
Pytest configuration and fixtures.
Provides isolated AsyncSession, test DB engine, and async HTTPX client.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.db.base import Base
from app.api.deps import get_db

# We use an in-memory SQLite DB for smoke tests, but for concurrency/row-locking 
# testing, a real PostgreSQL instance is required. If running locally without docker,
# tests will fall back to sqlite, but SELECT FOR UPDATE behavior might differ.
# For true validation, run tests with POSTGRES_DB="test_docbook".
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Create all tables before tests run and drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    """Yields a fresh database session for a single test."""
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client():
    """Provides an async HTTP client that overrides the get_db dependency."""
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
        
    app.dependency_overrides[get_db] = override_get_db
    
    # Use ASGITransport for modern HTTPX and FastAPI testing
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client
        
    app.dependency_overrides.clear()
