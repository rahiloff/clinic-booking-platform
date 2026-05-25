"""create_initial_tables

Revision ID: d5878f8b2d70
Revises:
Create Date: 2026-05-25

Creates all Phase 2 tables:
  - users
  - clinics
  - doctors
  - doctor_schedules
  - availability_slots
  - appointments

Plus 3 PostgreSQL ENUM types:
  - user_role
  - slot_status
  - appointment_status
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "d5878f8b2d70"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# --- Enum types ---
user_role = sa.Enum("patient", "doctor", "admin", name="user_role")
slot_status = sa.Enum("available", "booked", "blocked", "expired", name="slot_status")
appointment_status = sa.Enum(
    "booked", "confirmed", "completed", "cancelled", "no_show",
    name="appointment_status",
)


def upgrade() -> None:
    """Create all initial tables with indexes and constraints."""

    # === ENUMS (created automatically by SA, but explicit for clarity) ===
    user_role.create(op.get_bind(), checkfirst=True)
    slot_status.create(op.get_bind(), checkfirst=True)
    appointment_status.create(op.get_bind(), checkfirst=True)

    # === USERS ===
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("firebase_uid", sa.String(128), unique=True, nullable=True),
        sa.Column("phone", sa.String(20), unique=True, nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="patient"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_firebase_uid", "users", ["firebase_uid"])
    op.create_index("ix_users_phone", "users", ["phone"])

    # === CLINICS ===
    op.create_table(
        "clinics",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="Asia/Kolkata"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_clinics_city", "clinics", ["city"])

    # === DOCTORS ===
    op.create_table(
        "doctors",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("clinic_id", UUID(as_uuid=True), sa.ForeignKey("clinics.id"), nullable=True),
        sa.Column("specialization", sa.String(100), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("consultation_fee", sa.Integer(), nullable=True, comment="Fee in smallest currency unit (paise)"),
        sa.Column("experience_years", sa.SmallInteger(), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_doctors_clinic_id", "doctors", ["clinic_id"])
    op.create_index("ix_doctors_specialization", "doctors", ["specialization"])

    # === DOCTOR SCHEDULES ===
    op.create_table(
        "doctor_schedules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("doctors.id"), nullable=False),
        sa.Column("day_of_week", sa.SmallInteger(), nullable=False, comment="0=Monday, 6=Sunday"),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("slot_duration", sa.SmallInteger(), nullable=False, server_default="30", comment="Duration in minutes"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        # Constraints
        sa.UniqueConstraint("doctor_id", "day_of_week", name="uq_doctor_day"),
        sa.CheckConstraint("day_of_week >= 0 AND day_of_week <= 6", name="ck_valid_day_of_week"),
        sa.CheckConstraint("start_time < end_time", name="ck_schedule_time_order"),
        sa.CheckConstraint("slot_duration IN (15, 20, 30, 45, 60)", name="ck_valid_slot_duration"),
    )
    op.create_index("ix_doctor_schedules_doctor_id", "doctor_schedules", ["doctor_id"])

    # === AVAILABILITY SLOTS ===
    op.create_table(
        "availability_slots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("doctors.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("status", slot_status, nullable=False, server_default="available"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        # Prevent duplicate slots
        sa.UniqueConstraint("doctor_id", "date", "start_time", name="uq_doctor_date_start"),
    )
    # Primary query: "available slots for doctor X on date Y"
    op.create_index("idx_slot_doctor_date_status", "availability_slots", ["doctor_id", "date", "status"])
    op.create_index("idx_slot_date", "availability_slots", ["date"])

    # === APPOINTMENTS ===
    op.create_table(
        "appointments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("doctors.id"), nullable=False),
        sa.Column("slot_id", UUID(as_uuid=True), sa.ForeignKey("availability_slots.id"), nullable=False),
        sa.Column("status", appointment_status, nullable=False, server_default="booked"),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True, comment="Doctor's notes after appointment"),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    # Dashboard indexes
    op.create_index("idx_appt_patient_status", "appointments", ["patient_id", "status"])
    op.create_index("idx_appt_doctor_status", "appointments", ["doctor_id", "status"])
    # Partial unique: only one active booking per slot (cancelled ones don't count)
    op.create_index(
        "idx_unique_active_slot",
        "appointments",
        ["slot_id"],
        unique=True,
        postgresql_where=sa.text("status != 'cancelled'"),
    )


def downgrade() -> None:
    """Drop all tables and enum types in reverse dependency order."""
    op.drop_table("appointments")
    op.drop_table("availability_slots")
    op.drop_table("doctor_schedules")
    op.drop_table("doctors")
    op.drop_table("clinics")
    op.drop_table("users")

    # Drop enum types
    appointment_status.drop(op.get_bind(), checkfirst=True)
    slot_status.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
