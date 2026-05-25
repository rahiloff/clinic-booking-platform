"""
Doctor Booking Platform — SQLAlchemy Declarative Base

Central base class for all ORM models.
Import this in alembic/env.py so Alembic discovers all models for migrations.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    All models must inherit from this class.
    Alembic uses Base.metadata for auto-generating migrations.
    """

    pass
