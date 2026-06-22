from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NotificationEventCreate(BaseModel):
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class NotificationRead(BaseModel):
    id: int
    notification_id: str
    event_type: str
    incident_id: str | None
    project_id: str | None
    channel: str
    status: str
    payload: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeliveryAttemptRead(BaseModel):
    id: int
    notification_id: str
    channel: str
    attempt_number: int
    status: str
    response_message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
