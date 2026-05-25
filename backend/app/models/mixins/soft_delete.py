"""Soft-delete mixin — marks records as deleted instead of removing them."""

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


class SoftDeleteMixin:
    """
    Adds a deleted_at column for soft-delete support.

    Usage:
        class User(BaseModel, SoftDeleteMixin):
            ...

    Query active records:
        select(User).where(User.deleted_at.is_(None))
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
