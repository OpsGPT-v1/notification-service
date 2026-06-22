import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def build_message(event_type: str, payload: dict[str, Any]) -> str:
    incident_id = payload.get("incident_id", "unknown-incident")
    project_id = payload.get("project_id", "unknown-project")
    service_name = payload.get("service_name", "unknown-service")
    severity = payload.get("severity", "unknown-severity")
    root_cause = payload.get("root_cause")
    message = f"[OpsGPT] {event_type}: {incident_id} project={project_id} service={service_name} severity={severity}"
    if root_cause:
        message = f"{message} root_cause={root_cause}"
    return message


async def dispatch_notification(event_type: str, payload: dict[str, Any]) -> tuple[str, str | None]:
    channel = settings.notification_channel.lower()
    message = build_message(event_type, payload)

    if channel == "console":
        logger.info(message)
        return "delivered", "console notification logged"

    if channel == "slack":
        if not settings.slack_webhook_url:
            return "failed", "SLACK_WEBHOOK_URL is required when NOTIFICATION_CHANNEL=slack"
        try:
            async with httpx.AsyncClient(timeout=settings.notification_timeout_seconds) as client:
                response = await client.post(settings.slack_webhook_url, json={"text": message})
                response.raise_for_status()
            return "delivered", "slack notification delivered"
        except Exception as exc:
            logger.warning("Slack notification failed: %s", exc.__class__.__name__)
            return "failed", f"Slack delivery failed: {exc.__class__.__name__}"

    return "failed", f"Unsupported notification channel: {settings.notification_channel}"
