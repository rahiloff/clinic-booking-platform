"""User repository — database operations for users."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_phone(self, phone: str) -> User | None:
        """Find a user by phone number."""
        stmt = select(self.model).where(self.model.phone == phone)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_firebase_uid(self, firebase_uid: str) -> User | None:
        """Find a user by Firebase UID."""
        stmt = select(self.model).where(self.model.firebase_uid == firebase_uid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_users(self, *, skip: int = 0, limit: int = 100) -> list[User]:
        """List active (non-deleted, non-deactivated) users."""
        stmt = (
            select(self.model)
            .where(self.model.is_active.is_(True))
            .where(self.model.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
