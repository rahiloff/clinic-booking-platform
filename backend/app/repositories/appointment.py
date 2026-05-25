"""Appointment repository — database operations for appointments."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.enums import AppointmentStatus
from app.models.appointment import Appointment
from app.repositories.base import BaseRepository


class AppointmentRepository(BaseRepository[Appointment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Appointment, session)

    async def get_by_patient(
        self, patient_id: UUID, *, status: AppointmentStatus | None = None,
        skip: int = 0, limit: int = 50,
    ) -> list[Appointment]:
        """Get appointments for a patient, optionally filtered by status."""
        stmt = (
            select(self.model)
            .options(joinedload(self.model.slot))
            .where(self.model.patient_id == patient_id)
        )
        if status:
            stmt = stmt.where(self.model.status == status)
        stmt = stmt.order_by(self.model.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_by_doctor(
        self, doctor_id: UUID, *, status: AppointmentStatus | None = None,
        skip: int = 0, limit: int = 50,
    ) -> list[Appointment]:
        """Get appointments for a doctor's dashboard."""
        stmt = (
            select(self.model)
            .options(joinedload(self.model.patient))
            .options(joinedload(self.model.slot))
            .where(self.model.doctor_id == doctor_id)
        )
        if status:
            stmt = stmt.where(self.model.status == status)
        stmt = stmt.order_by(self.model.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_and_lock(self, appointment_id: UUID) -> Appointment | None:
        """Fetch appointment with row-level lock (for status changes)."""
        stmt = (
            select(self.model)
            .where(self.model.id == appointment_id)
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def has_active_booking(
        self, patient_id: UUID, doctor_id: UUID,
    ) -> bool:
        """Check if patient already has an active booking with this doctor."""
        active_statuses = [AppointmentStatus.BOOKED, AppointmentStatus.CONFIRMED]
        stmt = (
            select(self.model.id)
            .where(self.model.patient_id == patient_id)
            .where(self.model.doctor_id == doctor_id)
            .where(self.model.status.in_(active_statuses))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
