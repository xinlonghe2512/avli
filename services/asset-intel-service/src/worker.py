"""Celery configuration and initialization."""

from celery import Celery

from src.core.config import settings

message_broker_url = f"redis://:{settings.MESSAGE_BROKER_PASSWORD}@{settings.MESSAGE_BROKER_HOST}:{settings.MESSAGE_BROKER_PORT}/{settings.MESSAGE_BROKER_DB}"

worker = Celery(
    "avli",
    broker=message_broker_url,
    backend=message_broker_url,
    include=["src.tasks.chat"],
)

# Recommended Celery configuration
worker.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Singapore",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    result_expires=3600,  # 1 hour
)
