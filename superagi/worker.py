from __future__ import absolute_import

from celery import Celery

from superagi.config.config import get_config
from superagi.jobs.agent_executor import AgentExecutor

redis_url = get_config('REDIS_URL')

CELERY_IMPORTS = ('superagi.worker')
app = Celery("superagi", include=["superagi.worker"], imports=["superagi.worker"])
app.conf.broker_url = "redis://localhost:6379" #'redis://' + redis_url
app.conf.result_backend = "redis://localhost:6379" #'redis://' + redis_url
app.conf.worker_concurrency = 10
app.autodiscover_tasks(['superagi.worker'])


@app.task(bind=True)
def execute_agent(agent_execution_id: int):
    """Execute an agent step in background."""
    print(agent_execution_id)
    AgentExecutor().execute_next_action(agent_execution_id=agent_execution_id)
