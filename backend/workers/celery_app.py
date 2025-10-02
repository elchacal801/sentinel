"""
Celery Application Configuration
"""

import os
from celery import Celery

# Get configuration from environment
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "sentinel",
    broker=broker_url,
    backend=result_backend,
    include=["workers.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3000,  # 50 minutes soft limit
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Task routing
celery_app.conf.task_routes = {
    "workers.tasks.discover_assets_task": {"queue": "collection"},
    "workers.tasks.scan_ports_task": {"queue": "scanning"},
    "workers.tasks.collect_osint_task": {"queue": "osint"},
    "workers.tasks.scan_vulnerabilities_task": {"queue": "cybint"},
}
