"""
Slot Generation Engine.

Reads active doctor schedules and generates future AvailabilitySlot entries.
This must run periodically to populate the next 4 weeks.
"""

import structlog
from datetime import date, datetime, timedelta, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.doctor_schedule import DoctorSchedule
from app.models.availability_slot import AvailabilitySlot
from app.core.enums import SlotStatus
from app.repositories.slot import SlotRepository

logger = structlog.get_logger()

class SlotGenerationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.slot_repo = SlotRepository(db)

    async def generate_slots_for_doctor(self, doctor_id: UUID, weeks_ahead: int = 4) -> int:
        """
        Generate slots for a specific doctor for the next N weeks.
        Idempotent: skips already generated slots to avoid duplicate constraint errors.
        """
        # Fetch active schedules
        stmt = select(DoctorSchedule).where(DoctorSchedule.doctor_id == doctor_id).where(DoctorSchedule.is_active.is_(True))
        schedules = list((await self.db.execute(stmt)).scalars().all())
        
        if not schedules:
            return 0

        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=weeks_ahead * 7)

        # Pre-fetch existing slots in this window to avoid duplicate inserts
        existing_slots = await self.slot_repo.get_slots_by_date_range(doctor_id, start_date, end_date)
        existing_signatures = {(s.date, s.start_time) for s in existing_slots}

        new_slots_data = []

        # Iterate over each day in the window
        current_date = start_date
        while current_date <= end_date:
            day_of_week = current_date.weekday() # 0=Mon, 6=Sun
            
            # Find applicable schedules for this day
            day_schedules = [s for s in schedules if s.day_of_week == day_of_week]
            
            for sched in day_schedules:
                # Generate chunks based on slot_duration
                # Convert time to minutes for easy math
                current_time_mins = sched.start_time.hour * 60 + sched.start_time.minute
                end_time_mins = sched.end_time.hour * 60 + sched.end_time.minute
                
                while current_time_mins + sched.slot_duration <= end_time_mins:
                    s_hour, s_min = divmod(current_time_mins, 60)
                    slot_start = time(hour=s_hour, minute=s_min)
                    
                    # Check duplicate
                    if (current_date, slot_start) not in existing_signatures:
                        e_hour, e_min = divmod(current_time_mins + sched.slot_duration, 60)
                        slot_end = time(hour=e_hour, minute=e_min)
                        
                        new_slots_data.append({
                            "doctor_id": doctor_id,
                            "date": current_date,
                            "start_time": slot_start,
                            "end_time": slot_end,
                            "status": SlotStatus.AVAILABLE
                        })
                    
                    current_time_mins += sched.slot_duration
            
            current_date += timedelta(days=1)

        if new_slots_data:
            await self.slot_repo.bulk_create_slots(new_slots_data)
            logger.info("slots_generated", doctor_id=str(doctor_id), count=len(new_slots_data))

        return len(new_slots_data)
