import uuid

from sqlalchemy import BigInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )
    username: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    first_name: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    last_name: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    timezone: Mapped[str] = mapped_column(
        String(64),
        default="UTC",
    )

    gratitudes: Mapped[list["GratitudeEntry"]] = relationship(  # noqa: F821
        back_populates="user",
        cascade="all, delete-orphan",
    )
