"""
Slot repository — database operations for availability slots.

Contains the critical locking query used during booking.
"""

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import SlotStatus
from app.models.availability_slot import AvailabilitySlot
from app.repositories.base import BaseRepository


class SlotRepository(BaseRepository[AvailabilitySlot]):
    def __init__(self, session: AsyncSession):
        super().__init__(AvailabilitySlot, session)

    async def get_available_slots(
        self, doctor_id: UUID, slot_date: date,
    ) -> list[AvailabilitySlot]:
        """Get all available slots for a doctor on a specific date."""
        stmt = (
            select(self.model)
            .where(self.model.doctor_id == doctor_id)
            .where(self.model.date == slot_date)
            .where(self.model.status == SlotStatus.AVAILABLE)
            .order_by(self.model.start_time)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_slots_by_date_range(
        self, doctor_id: UUID, start_date: date, end_date: date,
    ) -> list[AvailabilitySlot]:
        """Get all slots for a doctor within a date range (any status)."""
        stmt = (
            select(self.model)
            .where(self.model.doctor_id == doctor_id)
            .where(self.model.date >= start_date)
            .where(self.model.date <= end_date)
            .order_by(self.model.date, self.model.start_time)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_and_lock_slot(self, slot_id: UUID) -> AvailabilitySlot | None:
        """
        Fetch a slot with row-level lock (SELECT ... FOR UPDATE).

        This is the CRITICAL method for concurrency-safe booking.
        Concurrent transactions will WAIT until this lock is released.
        """
        stmt = (
            select(self.model)
            .where(self.model.id == slot_id)
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def bulk_create_slots(
        self, slots_data: list[dict],
    ) -> list[AvailabilitySlot]:
        """Create multiple slots at once (used by slot generation worker)."""
        db_slots = [self.model(**data) for data in slots_data]
        self.session.add_all(db_slots)
        await self.session.flush()
        return db_slots
