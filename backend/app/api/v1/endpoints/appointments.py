"""
Patient Appointment APIs.
Protected endpoints for patients to book and cancel their own appointments.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.api.deps.auth import require_patient
from app.models.user import User
from app.schemas.response import APIResponse, success, paginated
from app.schemas.appointment import AppointmentCreate, AppointmentCancel, AppointmentDetailResponse
from app.services.appointment_service import AppointmentService

router = APIRouter()

@router.post(
    "/",
    response_model=APIResponse,
    summary="Book an appointment",
)
async def book_appointment(
    request: AppointmentCreate,
    current_user: User = Depends(require_patient),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AppointmentService(db)
    appointment = await service.book_appointment(
        patient_id=current_user.id,
        slot_id=request.slot_id,
        reason=request.reason,
    )
    return success(data={"appointment_id": str(appointment.id)}, message="Appointment booked successfully")


@router.get(
    "/",
    response_model=APIResponse,
    summary="List my appointments",
)
async def get_my_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_patient),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AppointmentService(db)
    appointments = await service.get_patient_appointments(current_user.id, skip, limit)
    
    data = []
    for appt in appointments:
        resp = AppointmentDetailResponse.model_validate(appt)
        # Load joined properties for nice frontend display
        if appt.slot:
            resp.slot_date = appt.slot.date.isoformat()
            resp.slot_time = appt.slot.start_time.isoformat()
        if appt.doctor and appt.doctor.user:
            resp.doctor_name = appt.doctor.user.full_name
        data.append(resp.model_dump())

    return paginated(data=data, skip=skip, limit=limit, total=len(data))


@router.patch(
    "/{appointment_id}/cancel",
    response_model=APIResponse,
    summary="Cancel an appointment",
)
async def cancel_appointment(
    appointment_id: UUID,
    request: AppointmentCancel,
    current_user: User = Depends(require_patient),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AppointmentService(db)
    await service.cancel_appointment(
        appointment_id=appointment_id,
        cancelled_by=current_user.id,
        is_doctor=False,
        reason=request.cancellation_reason,
    )
    return success(message="Appointment cancelled successfully")
