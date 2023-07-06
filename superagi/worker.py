from __future__ import absolute_import

from sqlalchemy.orm import sessionmaker

from superagi.helper.tool_helper import handle_tools_import
from superagi.lib.logger import logger

from celery import Celery

from superagi.config.config import get_config
from superagi.models.db import connect_db

redis_url = get_config('REDIS_URL') or 'localhost:6379'

app = Celery("superagi", include=["superagi.worker"], imports=["superagi.worker"])
app.conf.broker_url = "redis://" + redis_url + "/0"
app.conf.result_backend = "redis://" + redis_url + "/0"
app.conf.worker_concurrency = 10
app.conf.accept_content = ['application/x-python-serialize', 'application/json']


@app.task(name="execute_agent", autoretry_for=(Exception,), retry_backoff=2, max_retries=5)
def execute_agent(agent_execution_id: int, time):
    """Execute an agent step in background."""
    from superagi.jobs.agent_executor import AgentExecutor
    handle_tools_import()
    logger.info("Execute agent:" + str(time) + "," + str(agent_execution_id))
    AgentExecutor().execute_next_action(agent_execution_id=agent_execution_id)


@app.task(name="summarize_resource", autoretry_for=(Exception,), retry_backoff=2, max_retries=5, serializer='pickle')
def summarize_resource(agent_id: int, resource_id: int):
    """Summarize a resource in background."""
    from superagi.resource_manager.resource_summary import ResourceSummarizer
    from superagi.types.storage_types import StorageType
    from superagi.models.resource import Resource
    from superagi.resource_manager.resource_manager import ResourceManager

    engine = connect_db()
    Session = sessionmaker(bind=engine)
    session = Session()

    resource = session.query(Resource).filter(Resource.id == resource_id).first()
    file_path = resource.path

    if resource.storage_type == StorageType.S3.value:
        documents = ResourceManager(str(agent_id)).create_llama_document_s3(file_path)
    else:
        documents = ResourceManager(str(agent_id)).create_llama_document(file_path)

    logger.info("Summarize resource:" + str(agent_id) + "," + str(resource_id))
    resource_summarizer = ResourceSummarizer(session=session)
    resource_summarizer.add_to_vector_store_and_create_summary(agent_id=agent_id,
                                                               resource_id=resource_id,
                                                               documents=documents)
    resource_summarizer.generate_agent_summary(agent_id=agent_id)
    session.close()
