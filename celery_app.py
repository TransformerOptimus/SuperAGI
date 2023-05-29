from celery import Celery
# from superagi.task_queue.jobs.run_superagi_job import run_superagi_job
from superagi.models.agent_execution import AgentExecution
from superagi_job import run_superagi_job
from superagi.models.db import connectDB
from sqlalchemy.orm import sessionmaker, query


celery_app = Celery('tasks', broker='redis://localhost:6379')

celery_app.conf.worker_concurrency = 10

engine = connectDB()
Session = sessionmaker(bind=engine)
session = Session()


@celery_app.task(name="test_function")
def test_fucntion(agent_execution:AgentExecution):
    # Implement your function logic here
    
    res=run_superagi_job(agent_execution=agent_execution)    

    db_agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution.id).first()
    db_agent_execution.status = "COMPLETED"
    session.add(db_agent_execution)
    session.commit()

    print("Completed!")
    print(res)



session.close()
# # @celery_app.task(name="run_superagi")
# # def run_superagi(agent_execution:AgentExecution):
#     # run_superagi_job()


# # celery -A celery_app worker --loglevel=info