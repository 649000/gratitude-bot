import uuid
from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

# Re-export app models for scheduler convenience
from app.models.gratitude import GratitudeEntry  # noqa: F401
from app.models.preference import UserPreference  # noqa: F401
from app.models.prompt import Prompt  # noqa: F401
from app.models.user import User  # noqa: F401

__all__ = [
    "GratitudeEntry",
    "Prompt",
    "ScheduledMessage",
    "User",
    "UserPreference",
]


class ScheduledMessage(Base, TimestampMixin):
    __tablename__ = "scheduled_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    message_type: Mapped[str] = mapped_column(
        Enum("weekly", "monthly", "yearly", name="message_type_enum"),
        nullable=False,
    )
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    entry_ids: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    entry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        Enum("pending", "sent", "failed", name="message_status_enum"),
        nullable=False,
        default="pending",
        index=True,
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship()
