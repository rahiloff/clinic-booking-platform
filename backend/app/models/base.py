"""
Doctor Booking Platform — Base Model

Abstract base providing UUID primary key and audit timestamps.
All domain models inherit from this instead of Base directly.
"""

import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins.timestamp import TimestampMixin


class BaseModel(TimestampMixin, Base):
    """
    Abstract base model with UUID PK and audit timestamps.

    Provides:
        - id: UUID v4 primary key
        - created_at: server-managed creation timestamp
        - updated_at: server-managed update timestamp
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
