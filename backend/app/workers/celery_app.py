"""
Doctor Booking Platform — Celery Application

Configures Celery for background job processing.
Used for: appointment reminders, email notifications, cleanup tasks.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "docbook_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Reliability
    task_track_started=True,
    task_acks_late=True,            # Acknowledge after completion (crash-safe)
    worker_prefetch_multiplier=1,   # Fetch one task at a time

    # Result expiry
    result_expires=3600,            # 1 hour
)

# Auto-discover tasks from all app modules
# celery_app.autodiscover_tasks(["app.workers"])
