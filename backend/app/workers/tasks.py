"""
Celery Background Tasks.

Scheduled jobs using Celery and Redis.
"""

import asyncio
import structlog
from uuid import UUID

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.services.slot_generation_service import SlotGenerationService

logger = structlog.get_logger()

async def _async_generate_slots(doctor_id: UUID | None = None) -> int:
    """Async inner function to perform slot generation."""
    total_generated = 0
    async with AsyncSessionLocal() as db:
        service = SlotGenerationService(db)
        
        if doctor_id:
            total_generated = await service.generate_slots_for_doctor(doctor_id)
        else:
            from app.models.doctor import Doctor
            from sqlalchemy import select
            # Generate for all active doctors
            stmt = select(Doctor.id).where(Doctor.is_available.is_(True))
            result = await db.execute(stmt)
            for doc_id in result.scalars().all():
                try:
                    count = await service.generate_slots_for_doctor(doc_id)
                    total_generated += count
                except Exception as e:
                    logger.error("slot_generation_failed", doctor_id=str(doc_id), error=str(e))
        
        await db.commit()
    return total_generated


@celery_app.task(name="generate_future_slots")
def generate_future_slots(doctor_id_str: str | None = None):
    """
    Celery task to generate future slots for a doctor or all doctors.
    This can be hooked up to a celery beat schedule to run daily.
    """
    logger.info("generate_future_slots_task_started")
    doctor_id = UUID(doctor_id_str) if doctor_id_str else None
    
    # Celery workers run synchronous code, so we must run our async service in an event loop
    loop = asyncio.get_event_loop()
    count = loop.run_until_complete(_async_generate_slots(doctor_id))
    
    logger.info("generate_future_slots_task_completed", total_generated=count)
    return count
