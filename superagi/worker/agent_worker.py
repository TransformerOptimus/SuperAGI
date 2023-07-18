from superagi.celery_config import app
from superagi.lib.logger import logger


@app.task(name="execute_agent", autoretry_for=(Exception,), retry_backoff=2, max_retries=5)
def execute_agent(agent_execution_id: int, time):
    """Execute an agent step in background."""
    from superagi.jobs.agent_executor import AgentExecutor
    logger.info("Execute agent:" + str(time) + "," + str(agent_execution_id))
    print("Execute agent:" + str(time) + "," + str(agent_execution_id))
    AgentExecutor().execute_next_action(agent_execution_id=agent_execution_id)
