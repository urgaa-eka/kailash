"""Celery application configuration for KAILASH AI background tasks."""
from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery
celery_app = Celery(
    "kailash_tasks",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["app.tasks.daily_learning"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "daily-intelligence-gathering": {
        "task": "app.tasks.daily_learning.daily_learning_pipeline",
        "schedule": crontab(hour=6, minute=0),  # Every day at 06:00 UTC
        "options": {"expires": 3600},  # Expire after 1 hour if not picked up
    },
}

if __name__ == "__main__":
    celery_app.start()
