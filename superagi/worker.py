from __future__ import absolute_import
from superagi.lib.logger import logger

from celery import Celery

from superagi.config.config import get_config
from datetime import timedelta
from celery import Celery
from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.helper.agent_schedule_helper import RunAgentSchedule
redis_url = get_config('REDIS_URL') or 'localhost:6379'
app = Celery("superagi", include=["superagi.worker"], imports=["superagi.worker"])
app.conf.broker_url = "redis://" + redis_url + "/0"
app.conf.result_backend = "redis://" + redis_url + "/0"
app.conf.worker_concurrency = 10

beat_schedule = {
    'initialize-schedule-agent': {
        'task': 'initialize-schedule-agent', 
        'schedule': timedelta(minutes=5),
    },
}
app.conf.beat_schedule = beat_schedule

@app.task(name="initialize-schedule-agent", autoretry_for=(Exception,), retry_backoff=2, max_retries=5)
def initialize_schedule_agent_task():
    RunAgentSchedule.update_next_scheduled_time()
    RunAgentSchedule.get_scheduled_agents()

@app.task(name="execute_agent", autoretry_for=(Exception,), retry_backoff=2, max_retries=5)
def execute_agent(agent_execution_id: int, time):
    """Execute an agent step in background."""
    from superagi.jobs.agent_executor import AgentExecutor
    logger.info("Execute agent:" + str(time) + "," + str(agent_execution_id))
    AgentExecutor().execute_next_action(agent_execution_id=agent_execution_id)
