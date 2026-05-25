"""Schedule Service — Business logic for doctor weekly schedule template management."""

import structlog
from datetime import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from uuid import UUID

from app.core.exceptions import InputValidationError, NotFoundError, ConflictError
from app.models.doctor_schedule import DoctorSchedule
from app.repositories.base import BaseRepository

logger = structlog.get_logger()

class ScheduleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.schedule_repo = BaseRepository(DoctorSchedule, db)

    async def create_schedule(
        self, doctor_id: UUID, day_of_week: int, start_time: time, end_time: time, slot_duration: int
    ) -> DoctorSchedule:
        """Create a new recurring schedule checking for overlaps and valid durations."""
        if start_time >= end_time:
            raise InputValidationError("start_time must be before end_time")
        
        if slot_duration not in [15, 20, 30, 45, 60]:
            raise InputValidationError("slot_duration must be one of 15, 20, 30, 45, 60")

        # Overlap Check
        stmt = (
            select(DoctorSchedule)
            .where(DoctorSchedule.doctor_id == doctor_id)
            .where(DoctorSchedule.day_of_week == day_of_week)
            .where(
                or_(
                    and_(DoctorSchedule.start_time <= start_time, DoctorSchedule.end_time > start_time),
                    and_(DoctorSchedule.start_time < end_time, DoctorSchedule.end_time >= end_time),
                    and_(DoctorSchedule.start_time >= start_time, DoctorSchedule.end_time <= end_time),
                )
            )
        )
        overlap = (await self.db.execute(stmt)).scalar_one_or_none()
        if overlap:
            raise ConflictError("Schedule overlaps with an existing schedule for this day")

        schedule = DoctorSchedule(
            doctor_id=doctor_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            slot_duration=slot_duration,
            is_active=True,
        )
        self.db.add(schedule)
        await self.db.flush()
        logger.info("doctor_schedule_created", doctor_id=str(doctor_id), day=day_of_week)
        return schedule

    async def get_doctor_schedules(self, doctor_id: UUID) -> list[DoctorSchedule]:
        """Get all schedule templates for a doctor."""
        stmt = select(DoctorSchedule).where(DoctorSchedule.doctor_id == doctor_id).order_by(DoctorSchedule.day_of_week)
        return list((await self.db.execute(stmt)).scalars().all())

    async def delete_schedule(self, doctor_id: UUID, schedule_id: UUID) -> None:
        """Delete a schedule, verifying ownership."""
        schedule = await self.schedule_repo.get_by_id(schedule_id)
        if not schedule or schedule.doctor_id != doctor_id:
            raise NotFoundError("Schedule")
        
        await self.schedule_repo.delete(schedule_id)
        logger.info("doctor_schedule_deleted", schedule_id=str(schedule_id))
