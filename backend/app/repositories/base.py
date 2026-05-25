"""
Doctor Booking Platform — Base Repository

Generic async repository providing standard CRUD operations.
All domain repositories inherit from this to avoid duplicating
common database query patterns.

Design:
- Repositories ONLY handle database operations
- They never contain business logic
- They use flush() not commit() — the session dependency manages transactions
- This enables Unit of Work: one transaction per request, auto-commit/rollback
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic async CRUD repository.

    Usage:
        class UserRepository(BaseRepository[User]):
            def __init__(self, session: AsyncSession):
                super().__init__(User, session)

            async def get_by_phone(self, phone: str) -> User | None:
                stmt = select(self.model).where(self.model.phone == phone)
                result = await self.session.execute(stmt)
                return result.scalar_one_or_none()
    """

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: UUID) -> ModelType | None:
        """Fetch a single record by primary key."""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: list | None = None,
    ) -> list[ModelType]:
        """Fetch multiple records with optional filtering and pagination."""
        stmt = select(self.model)
        if filters:
            for condition in filters:
                stmt = stmt.where(condition)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, *, filters: list | None = None) -> int:
        """Count records with optional filtering."""
        stmt = select(func.count()).select_from(self.model)
        if filters:
            for condition in filters:
                stmt = stmt.where(condition)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(self, obj_in: dict[str, Any]) -> ModelType:
        """Create a new record. Uses flush() — commit happens at request end."""
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, id: UUID, obj_in: dict[str, Any]) -> ModelType | None:
        """Update an existing record by ID. Returns None if not found."""
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: UUID) -> bool:
        """Hard-delete a record by ID. Returns False if not found."""
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return False
        await self.session.delete(db_obj)
        await self.session.flush()
        return True
