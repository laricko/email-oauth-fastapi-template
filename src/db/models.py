from datetime import datetime
from enum import StrEnum, auto

from sqlalchemy import ForeignKey, String, UniqueConstraint, func, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )


class User(Base):
    __tablename__ = "users"


class ProviderType(StrEnum):
    google = auto()
    yandex = auto()


class UserEmail(Base):
    __tablename__ = "user_emails"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255))
    provider: Mapped[str] = mapped_column(String(50))
    last_synced_at: Mapped[datetime | None]

    access_token: Mapped[str]
    refresh_token: Mapped[str | None]
    expires_at: Mapped[datetime]
    obtained_at: Mapped[datetime]

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "email",
            name="uq_user_emails_provider_email",
        ),
    )


class Email(Base):
    __tablename__ = "emails"

    user_email_id: Mapped[int] = mapped_column(
        ForeignKey("user_emails.id", ondelete="CASCADE")
    )
    external_id: Mapped[str] = mapped_column(String(255))
    from_email: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(511))
    snippet: Mapped[str] = mapped_column(String(511))
    recieved_at: Mapped[datetime]
    is_read: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (
        UniqueConstraint(
            "user_email_id",
            "external_id",
            name="uq_emails_external_id_user_email_id",
        ),
    )
