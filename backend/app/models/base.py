"""
Doctor Booking Platform — Base Model Mixin

Provides reusable columns that every model needs:
- UUID primary key
- created_at / updated_at timestamps

All domain models should inherit from BaseModel instead of Base directly.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BaseModel(Base):
    """
    Abstract base model with UUID PK and audit timestamps.

    Usage:
        class User(BaseModel):
            __tablename__ = "users"
            name: Mapped[str] = mapped_column(...)
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
