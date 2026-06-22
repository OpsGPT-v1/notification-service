from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class NotificationRecord(Base):
    __tablename__ = "notification_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notification_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    incident_id: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    project_id: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    channel: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class NotificationDeliveryAttempt(Base):
    __tablename__ = "notification_delivery_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notification_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(40), nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    response_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    template_body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
