from datetime import datetime

from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
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


class UserEmail(Base):
    __tablename__ = "user_emails"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255))
    provider: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(server_default="true")
    last_synced_at: Mapped[datetime | None]

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
        ForeignKey("user_emails.id", ondelete="CASCADE"), index=True
    )
    provider: Mapped[str] = mapped_column(String(50))
    external_id: Mapped[str] = mapped_column(String(255))
    from_email: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(511))
    received_at: Mapped[datetime]
    scanned_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "external_id",
            name="uq_emails_provider_external_id",
        ),
    )
