"""Doctor Service — Business logic for doctor listings and lookup."""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.exceptions import NotFoundError
from app.repositories.doctor import DoctorRepository
from app.models.doctor import Doctor

logger = structlog.get_logger()

class DoctorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.doctor_repo = DoctorRepository(db)

    async def list_available_doctors(self, skip: int = 0, limit: int = 50) -> list[Doctor]:
        """Fetch all active, available doctors with their clinics and users."""
        return await self.doctor_repo.get_available_doctors(skip=skip, limit=limit)

    async def count_available_doctors(self) -> int:
        """Count all active, available doctors for pagination."""
        return await self.doctor_repo.count_available()

    async def search_doctors_by_specialization(
        self, specialization: str, skip: int = 0, limit: int = 50
    ) -> list[Doctor]:
        """Search available doctors by specialization string."""
        return await self.doctor_repo.get_by_specialization(
            specialization, skip=skip, limit=limit
        )

    async def get_doctor_by_id(self, doctor_id: UUID) -> Doctor:
        """Fetch a specific doctor. Raises NotFoundError if invalid."""
        doctor = await self.doctor_repo.get_by_id(doctor_id)
        if not doctor:
            raise NotFoundError("Doctor")
        return doctor
