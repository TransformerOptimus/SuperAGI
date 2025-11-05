"""
Celery application for background task processing
"""

from celery import Celery
from config.config import config

# Create Celery app
celery_app = Celery(
    'sales_agent',
    broker=config.REDIS_URL,
    backend=config.REDIS_URL,
    include=['jobs.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)
