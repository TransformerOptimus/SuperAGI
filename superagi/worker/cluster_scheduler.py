from superagi.celery_config import app

from superagi.lib.logger import logger


@app.task(name="cluster_scheduler")
def cluster_scheduler():
    """Schedule pending cluster workflows"""
    from superagi.jobs.cluster_executor import ClusterExecutor
    ClusterExecutor.schedule_pending_executions()
    logger.info("Scheduling cluster runs")

