from __future__ import absolute_import

from celery import Celery
from superagi.config.config import get_config
redis_url = get_config('REDIS_URL') or 'localhost:6379'

app = Celery("superagi", include=["superagi.worker"], imports=["superagi.worker"])
app.conf.broker_url = "redis://" + redis_url + "/0"
app.conf.result_backend = "redis://" + redis_url + "/0"
app.conf.worker_concurrency = 10
app.conf.beat_schedule = {
    'cluster_scheduler': {
        'task': 'cluster_scheduler',
        'schedule': 10.0,
    },
}
app.autodiscover_tasks(["superagi.worker.agent_worker","superagi.worker.cluster_scheduler"])