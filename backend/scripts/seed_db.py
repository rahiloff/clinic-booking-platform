"""
Deterministic Database Seeder.
Used to bootstrap the local environment with predictable, safe demo data.
"""

import asyncio
import structlog
from datetime import time
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.clinic import Clinic
from app.models.doctor import Doctor
from app.models.doctor_schedule import DoctorSchedule
from app.models.availability_slot import AvailabilitySlot
from app.models.appointment import Appointment
from app.core.enums import UserRole
from app.services.slot_generation_service import SlotGenerationService
from app.core.security import hash_password

logger = structlog.get_logger()

async def clear_db(db: AsyncSession):
    """Clean existing data."""
    await db.execute(delete(Appointment))
    await db.execute(delete(AvailabilitySlot))
    await db.execute(delete(DoctorSchedule))
    await db.execute(delete(Doctor))
    await db.execute(delete(Clinic))
    await db.execute(delete(User))
    await db.flush()

async def seed_data():
    logger.info("seeding_started")
    async with AsyncSessionLocal() as db:
        await clear_db(db)

        # 1. Create Users
        patient_user = User(phone="+1234567890", full_name="Demo Patient", role=UserRole.PATIENT, is_active=True)
        doctor_user = User(phone="+1999999999", full_name="Dr. Sarah Connor", role=UserRole.DOCTOR, is_active=True)
        admin_user = User(phone="+1000000000", full_name="System Admin", role=UserRole.ADMIN, is_active=True)
        db.add_all([patient_user, doctor_user, admin_user])
        await db.flush()

        # 2. Create Clinic
        clinic = Clinic(
            name="Downtown Medical Center",
            address="123 Health Ave, Medical District",
            phone="+18005550199",
            city="New York",
            timezone="America/New_York",
            is_active=True
        )
        db.add(clinic)
        await db.flush()

        # 3. Create Doctor Profile
        doctor = Doctor(
            user_id=doctor_user.id,
            clinic_id=clinic.id,
            specialization="Cardiology",
            bio="Board-certified cardiologist with 15 years of experience.",
            consultation_fee=15000, # $150.00
            experience_years=15,
            is_available=True
        )
        db.add(doctor)
        await db.flush()

        # 4. Create Schedules (Mon-Fri 9 AM to 5 PM, 30 min slots)
        for day in range(5): # 0=Mon, 4=Fri
            schedule = DoctorSchedule(
                doctor_id=doctor.id,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0),
                slot_duration=30,
                is_active=True
            )
            db.add(schedule)
        await db.flush()

        # 5. Generate Future Slots
        slot_service = SlotGenerationService(db)
        generated_count = await slot_service.generate_slots_for_doctor(doctor.id, weeks_ahead=2)

        await db.commit()
        logger.info("seeding_completed", slots_generated=generated_count)

if __name__ == "__main__":
    asyncio.run(seed_data())
