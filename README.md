# OpsGPT Notification Service

The **Notification Service** handles routing alerts and incident life-cycle events to outgoing operational communication channels. It processes event triggers (e.g. incident creation, status updates, AI analysis completion), formats standard alert summaries, logs delivery history in the database, and pushes interactive messages to configured webhooks.

---

## Supported Notification Channels

The service routes messages depending on the `NOTIFICATION_CHANNEL` setting:

1.  **Console Logs (`console`)**: Logs output directly to stdout using python logging. Ideal for local testing and debugging.
2.  **Slack Integration (`slack`)**: Calls a Slack Incoming Webhook endpoint. Formats structured notifications with links to incidents, severity flags, and key metadata. Requires setting `SLACK_WEBHOOK_URL`.

---

## Event Message Templates

The notification message is dynamically built using the following format:
```text
[OpsGPT] {event_type}: {incident_id} project={project_id} service={service_name} severity={severity} [root_cause={root_cause}]
```

### Supported Event Types
*   `incident_created`: Fired when a new correlation group generates a ticket.
*   `incident_status_updated`: Fired when an engineer updates status (e.g., acknowledged, resolved).
*   `incident_resolved`: Specific subset of status updates.
*   `resolution_notes_added`: Fired when resolution details are submitted.
*   `ai_analysis_completed`: Fired when the Azure AI Foundry analyzer completes root-cause diagnostics.
*   `slack_test`: Debug trigger.

---

## API Endpoints Reference

All paths are prefixed with `/api` or `/notifications`.

### 1. Operations & Diagnostics (`/notifications`)

| Method | Path | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/notifications/events` | None | **Ingest Event**. Receives event payloads, builds standard templates, dispatches message to target channel, and commits logs. |
| `POST` | `/notifications/slack/test` | None | **Slack Diagnostics**. Sends a test string to the configured Slack webhook URL to verify credentials. |
| `GET` | `/notifications` | None | Lists all logged notification records (limit 200). |
| `GET` | `/notifications/incident/{incident_id}` | None | Lists all notification records dispatched for a specific incident. |
| `GET` | `/notifications/{notification_id}` | None | Retrieves metadata for a single notification record. |
| `GET` | `/notifications/{notification_id}/attempts` | None | Retrieves all delivery attempts (attempt number, status code, response message) for a notification. |

---

## Database Logs & Retries

*   **`notification_records`**: Table documenting every notification event type, incident association, and delivery status.
*   **`notification_delivery_attempts`**: Audit table documenting every delivery run. In case of network errors or HTTP status errors (e.g., rate limits or socket timeouts), retry attempts are logged sequentially alongside downstream error payloads.

---

## Key Configurations & Environment Variables

| Environment Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://opsgpt_user:opsgpt_password@opsgpt-db:5432/opsgpt_db` | Connection string to PostgreSQL database. |
| `NOTIFICATION_CHANNEL` | `console` | Destination channel name (`console` or `slack`). |
| `SLACK_WEBHOOK_URL` | `""` | Slack Incoming Webhook destination URL. |
| `NOTIFICATION_RETRY_COUNT` | `3` | Maximum number of retry attempts for failed HTTP deliveries. |
| `NOTIFICATION_TIMEOUT_SECONDS`| `10` | Delivery HTTP client timeout limit. |
| `CORS_ORIGINS` | `*` | Allowed CORS origins list. |
| `DB_INIT_MAX_ATTEMPTS` | `30` | Number of times to check database connection on startup. |
| `DB_INIT_DELAY_SECONDS` | `2` | Delay between database connection checks. |
