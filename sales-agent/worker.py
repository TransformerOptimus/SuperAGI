"""
Celery Worker Entry Point

Run with:
    celery -A worker.celery_app worker --loglevel=info
"""

from jobs.celery_app import celery_app

if __name__ == '__main__':
    celery_app.start()
