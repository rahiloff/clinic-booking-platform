"""
Doctor & Public Endpoints.
Public facing APIs for fetching available doctors, details, and bookable slots.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date

from app.api.deps import get_db
from app.schemas.response import APIResponse, success, paginated
from app.schemas.doctor import DoctorResponse, DoctorListResponse
from app.schemas.slot import SlotResponse
from app.services.doctor_service import DoctorService
from app.repositories.slot import SlotRepository

router = APIRouter()

@router.get(
    "/",
    response_model=APIResponse,
    summary="List available doctors",
)
async def list_doctors(
    specialization: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = DoctorService(db)
    
    if specialization:
        doctors = await service.search_doctors_by_specialization(specialization, skip, limit)
        total = len(doctors) # Simplified total for search
    else:
        doctors = await service.list_available_doctors(skip, limit)
        total = await service.count_available_doctors()

    # Map to schema mapping joined fields correctly
    mapped = []
    for d in doctors:
        mapped.append(
            DoctorListResponse(
                id=d.id,
                user_id=d.user_id,
                clinic_id=d.clinic_id,
                specialization=d.specialization,
                bio=d.bio,
                consultation_fee=d.consultation_fee,
                experience_years=d.experience_years,
                is_available=d.is_available,
                created_at=d.created_at,
                doctor_name=d.user.full_name if d.user else None,
                clinic_name=d.clinic.name if d.clinic else None,
            ).model_dump()
        )

    return paginated(data=mapped, total=total, skip=skip, limit=limit)


@router.get(
    "/{doctor_id}",
    response_model=APIResponse,
    summary="Get doctor details",
)
async def get_doctor(doctor_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    service = DoctorService(db)
    doctor = await service.get_doctor_by_id(doctor_id)
    return success(data=DoctorResponse.model_validate(doctor).model_dump())


@router.get(
    "/{doctor_id}/slots",
    response_model=APIResponse,
    summary="Get available slots for a doctor",
)
async def get_available_slots(
    doctor_id: UUID,
    slot_date: date = Query(..., description="Date to fetch slots for"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Fetch all AVAILABLE slots for a specific doctor on a specific date."""
    # We use repository directly for simple fetch, no complex business logic needed
    slot_repo = SlotRepository(db)
    slots = await slot_repo.get_available_slots(doctor_id, slot_date)
    
    data = [SlotResponse.model_validate(s).model_dump() for s in slots]
    return success(data=data)
