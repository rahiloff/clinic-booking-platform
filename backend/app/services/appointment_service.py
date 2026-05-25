"""
Appointment Service — The Core Booking Engine.

Handles concurrency-safe booking, conflict validation, and cancellations.
"""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone

from app.core.enums import SlotStatus, AppointmentStatus
from app.core.exceptions import SlotConflictError, NotFoundError, DuplicateBookingError, AuthorizationError
from app.models.appointment import Appointment
from app.repositories.slot import SlotRepository
from app.repositories.appointment import AppointmentRepository
from app.repositories.doctor import DoctorRepository

logger = structlog.get_logger()

class AppointmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.slot_repo = SlotRepository(db)
        self.appt_repo = AppointmentRepository(db)
        self.doctor_repo = DoctorRepository(db)

    async def book_appointment(self, patient_id: UUID, slot_id: UUID, reason: str | None = None) -> Appointment:
        """
        Concurrency-safe appointment booking.
        1. Lock the slot using SELECT FOR UPDATE.
        2. Check for duplicate active appointments for this patient-doctor pair.
        3. Mutate slot state.
        4. Flush appointment to session.
        """
        # 1. Lock slot
        slot = await self.slot_repo.get_and_lock_slot(slot_id)
        if not slot:
            raise NotFoundError("Slot")
        
        if slot.status != SlotStatus.AVAILABLE:
            logger.warning("slot_conflict_detected", slot_id=str(slot_id))
            raise SlotConflictError()

        # 2. Check for active booking to prevent spamming the doctor
        has_active = await self.appt_repo.has_active_booking(patient_id, slot.doctor_id)
        if has_active:
            raise DuplicateBookingError()

        # 3. Create appointment
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=slot.doctor_id,
            slot_id=slot_id,
            status=AppointmentStatus.BOOKED,
            reason=reason,
        )
        self.db.add(appointment)
        
        # 4. Mark slot booked
        slot.status = SlotStatus.BOOKED
        
        await self.db.flush()
        logger.info("appointment_booked", appointment_id=str(appointment.id), patient_id=str(patient_id), slot_id=str(slot_id))
        
        return appointment

    async def cancel_appointment(self, appointment_id: UUID, cancelled_by: UUID, is_doctor: bool, reason: str | None = None) -> None:
        """
        Concurrency-safe cancellation.
        Rolls back slot to AVAILABLE and audits the cancellation.
        """
        appointment = await self.appt_repo.get_and_lock(appointment_id)
        if not appointment:
            raise NotFoundError("Appointment")

        # Authorization
        if not is_doctor and appointment.patient_id != cancelled_by:
            raise AuthorizationError("You do not own this appointment")
        if is_doctor and appointment.doctor_id != cancelled_by:
            raise AuthorizationError("This appointment does not belong to your clinic")

        # Validation
        if appointment.status in (AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED, AppointmentStatus.NO_SHOW):
            raise SlotConflictError("Appointment is already finalized or cancelled")

        # Update appointment
        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancelled_at = datetime.now(timezone.utc)
        appointment.cancelled_by = cancelled_by
        appointment.cancellation_reason = reason

        # Free the slot
        slot = await self.slot_repo.get_and_lock_slot(appointment.slot_id)
        if slot:
            slot.status = SlotStatus.AVAILABLE

        await self.db.flush()
        logger.info("appointment_cancelled", appointment_id=str(appointment_id), by=str(cancelled_by))

    async def get_patient_appointments(self, patient_id: UUID, skip: int = 0, limit: int = 50) -> list[Appointment]:
        return await self.appt_repo.get_by_patient(patient_id, skip=skip, limit=limit)
