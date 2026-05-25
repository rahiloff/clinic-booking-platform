"""
Doctor Dashboard APIs.
Secured endpoints for doctors to manage their schedules, slots, and view appointments.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.api.deps.auth import require_doctor
from app.models.user import User
from app.schemas.response import APIResponse, success, paginated
from app.schemas.slot import ScheduleCreate, ScheduleResponse
from app.schemas.appointment import AppointmentDetailResponse
from app.services.schedule_service import ScheduleService
from app.services.slot_generation_service import SlotGenerationService
from app.repositories.appointment import AppointmentRepository
from app.repositories.doctor import DoctorRepository
from app.core.exceptions import NotFoundError

router = APIRouter()

async def get_doctor_id_for_user(user: User, db: AsyncSession) -> UUID:
    repo = DoctorRepository(db)
    doc = await repo.get_by_user_id(user.id)
    if not doc:
        raise NotFoundError("Doctor Profile")
    return doc.id

# --- Schedules ---

@router.post("/schedules", response_model=APIResponse, summary="Create a recurring schedule")
async def create_schedule(
    request: ScheduleCreate,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
) -> dict:
    doc_id = await get_doctor_id_for_user(current_user, db)
    service = ScheduleService(db)
    schedule = await service.create_schedule(
        doctor_id=doc_id,
        day_of_week=request.day_of_week,
        start_time=request.start_time,
        end_time=request.end_time,
        slot_duration=request.slot_duration
    )
    return success(data=ScheduleResponse.model_validate(schedule).model_dump())

@router.get("/schedules", response_model=APIResponse, summary="Get my schedules")
async def get_schedules(
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
) -> dict:
    doc_id = await get_doctor_id_for_user(current_user, db)
    service = ScheduleService(db)
    schedules = await service.get_doctor_schedules(doc_id)
    return success(data=[ScheduleResponse.model_validate(s).model_dump() for s in schedules])

@router.delete("/schedules/{schedule_id}", response_model=APIResponse, summary="Delete a schedule")
async def delete_schedule(
    schedule_id: UUID,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
) -> dict:
    doc_id = await get_doctor_id_for_user(current_user, db)
    service = ScheduleService(db)
    await service.delete_schedule(doc_id, schedule_id)
    return success(message="Schedule deleted successfully")

# --- Slot Generation Trigger ---
# In production this is a celery task, but useful to expose for manual trigger

@router.post("/generate-slots", response_model=APIResponse, summary="Trigger slot generation")
async def trigger_slot_generation(
    weeks: int = Query(4, ge=1, le=12),
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
) -> dict:
    doc_id = await get_doctor_id_for_user(current_user, db)
    service = SlotGenerationService(db)
    count = await service.generate_slots_for_doctor(doc_id, weeks_ahead=weeks)
    return success(message=f"Generated {count} new slots for the next {weeks} weeks")

# --- Appointments ---

@router.get("/appointments", response_model=APIResponse, summary="View clinic appointments")
async def list_clinic_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
) -> dict:
    doc_id = await get_doctor_id_for_user(current_user, db)
    repo = AppointmentRepository(db)
    appointments = await repo.get_by_doctor(doc_id, skip=skip, limit=limit)
    
    data = []
    for appt in appointments:
        resp = AppointmentDetailResponse.model_validate(appt)
        if appt.slot:
            resp.slot_date = appt.slot.date.isoformat()
            resp.slot_time = appt.slot.start_time.isoformat()
        if appt.patient:
            resp.patient_name = appt.patient.full_name
        data.append(resp.model_dump())

    return paginated(data=data, skip=skip, limit=limit, total=len(data))
