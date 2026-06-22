import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.models import NotificationDeliveryAttempt, NotificationRecord
from app.schemas.schemas import DeliveryAttemptRead, NotificationEventCreate, NotificationRead
from app.services.dispatcher import dispatch_notification

router = APIRouter(prefix="/notifications", tags=["notifications"])


def new_notification_id() -> str:
    return f"NOTIF-{uuid.uuid4().hex[:12].upper()}"


@router.post("/events", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
async def create_notification_event(
    payload: NotificationEventCreate,
    db: Session = Depends(get_db),
) -> NotificationRecord:
    notification_id = new_notification_id()
    channel = settings.notification_channel.lower()
    delivery_status, response_message = await dispatch_notification(payload.event_type, payload.payload)
    record = NotificationRecord(
        notification_id=notification_id,
        event_type=payload.event_type,
        incident_id=payload.payload.get("incident_id"),
        project_id=payload.payload.get("project_id"),
        channel=channel,
        status=delivery_status,
        payload=payload.payload,
    )
    db.add(record)
    db.add(
        NotificationDeliveryAttempt(
            notification_id=notification_id,
            channel=channel,
            attempt_number=1,
            status=delivery_status,
            response_message=response_message,
        )
    )
    db.commit()
    db.refresh(record)
    return record


@router.post("/slack/test")
async def test_slack() -> dict:
    if settings.notification_channel.lower() != "slack":
        return {"status": "skipped", "message": "Notification channel is not slack"}
    delivery_status, response_message = await dispatch_notification(
        "slack_test",
        {"incident_id": "test", "project_id": "test", "service_name": "notification-service", "severity": "info"},
    )
    return {"status": delivery_status, "message": response_message}


@router.get("", response_model=list[NotificationRead])
def list_notifications(db: Session = Depends(get_db)) -> list[NotificationRecord]:
    return db.query(NotificationRecord).order_by(NotificationRecord.created_at.desc()).limit(200).all()


@router.get("/incident/{incident_id}", response_model=list[NotificationRead])
def list_notifications_for_incident(
    incident_id: str,
    db: Session = Depends(get_db),
) -> list[NotificationRecord]:
    return (
        db.query(NotificationRecord)
        .filter(NotificationRecord.incident_id == incident_id)
        .order_by(NotificationRecord.created_at.desc())
        .all()
    )


@router.get("/{notification_id}", response_model=NotificationRead)
def get_notification(
    notification_id: str,
    db: Session = Depends(get_db),
) -> NotificationRecord:
    record = db.query(NotificationRecord).filter(NotificationRecord.notification_id == notification_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return record


@router.get("/{notification_id}/attempts", response_model=list[DeliveryAttemptRead])
def get_notification_attempts(
    notification_id: str,
    db: Session = Depends(get_db),
) -> list[NotificationDeliveryAttempt]:
    return (
        db.query(NotificationDeliveryAttempt)
        .filter(NotificationDeliveryAttempt.notification_id == notification_id)
        .order_by(NotificationDeliveryAttempt.created_at.asc())
        .all()
    )
