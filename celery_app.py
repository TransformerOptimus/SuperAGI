from celery import Celery
# from superagi.task_queue.jobs.run_superagi_job import run_superagi_job
from superagi.models.agent_execution import AgentExecution
from superagi_job import run_superagi_job

celery_app = Celery('tasks', broker='redis://localhost:6379')

celery_app.conf.worker_concurrency = 10


@celery_app.task(name="test_function")
def test_fucntion(agent_execution:AgentExecution):
    # Implement your function logic here
    c = 0
    print("Inside Celery!")
    while c<1000:
        c = c+1
    print("Done!")
    run_superagi_job(agent_execution=agent_execution)
    print("Everything Done!")


# # @celery_app.task(name="run_superagi")
# # def run_superagi(agent_execution:AgentExecution):
#     # run_superagi_job()


# # celery -A celery_app worker --loglevel=info