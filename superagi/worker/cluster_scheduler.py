from superagi.celery_config import app
from superagi.lib.logger import logger


@app.task(name="cluster_scheduler")
def cluster_scheduler():
    """Schedule pending cluster workflows"""
    from superagi.jobs.agent_executor import AgentExecutor
    logger.info("Scheduling cluster runs")

