"""
Doctor Booking Platform — V1 API Router

Aggregates all v1 endpoint routers into a single router.
Mounted at /api/v1 in main.py.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, auth, doctors, appointments, doctor_dashboard

api_v1_router = APIRouter()

# --- Health Check ---
api_v1_router.include_router(
    health.router,
    tags=["Health"],
)

# --- Authentication ---
api_v1_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# --- Doctors (Public Lookups) ---
api_v1_router.include_router(
    doctors.router,
    prefix="/doctors",
    tags=["Doctors"],
)

# --- Appointments (Patient Actions) ---
api_v1_router.include_router(
    appointments.router,
    prefix="/appointments",
    tags=["Appointments"],
)

# --- Doctor Dashboard (Secured Doctor Actions) ---
api_v1_router.include_router(
    doctor_dashboard.router,
    prefix="/doctor",
    tags=["Doctor Dashboard"],
)
