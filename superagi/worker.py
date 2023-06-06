from __future__ import absolute_import

from celery import Celery

from superagi.config.config import get_config
from superagi.jobs.agent_executor import AgentExecutor
redis_url = get_config('REDIS_URL')

app = Celery("superagi", include=["superagi.worker"], imports=["superagi.worker"])
app.conf.broker_url = "redis://" + redis_url + "/0"
app.conf.result_backend = "redis://" + redis_url + "/0"
app.conf.worker_concurrency = 10

@app.task(name="execute_agent")
def execute_agent(agent_execution_id: int, time):
    """Execute an agent step in background."""
    print("Execute agent:" + str(time) + "," + str(agent_execution_id))
    AgentExecutor().execute_next_action(agent_execution_id=agent_execution_id)
