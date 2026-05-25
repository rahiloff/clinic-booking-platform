"""Doctor repository — database operations for doctors."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.doctor import Doctor
from app.repositories.base import BaseRepository


class DoctorRepository(BaseRepository[Doctor]):
    def __init__(self, session: AsyncSession):
        super().__init__(Doctor, session)

    async def get_by_user_id(self, user_id: UUID) -> Doctor | None:
        """Find doctor profile by user ID."""
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_specialization(
        self, specialization: str, *, skip: int = 0, limit: int = 50,
    ) -> list[Doctor]:
        """List doctors by specialization."""
        stmt = (
            select(self.model)
            .where(self.model.specialization.ilike(f"%{specialization}%"))
            .where(self.model.is_available.is_(True))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_available_doctors(
        self, *, skip: int = 0, limit: int = 50,
    ) -> list[Doctor]:
        """List all available doctors with their user info eagerly loaded."""
        stmt = (
            select(self.model)
            .options(joinedload(self.model.user))
            .options(joinedload(self.model.clinic))
            .where(self.model.is_available.is_(True))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def count_available(self) -> int:
        """Count available doctors (for pagination)."""
        from sqlalchemy import func
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.is_available.is_(True))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
