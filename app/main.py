import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import notifications
from app.core.config import settings
from app.db.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="OpsGPT Notification Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notifications.router)
app.include_router(notifications.router, prefix="/api")


@app.on_event("startup")
def startup() -> None:
    if not init_db():
        logger.error("Notification Service started without confirmed database initialization")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "notification-service",
        "channel": settings.notification_channel,
    }
