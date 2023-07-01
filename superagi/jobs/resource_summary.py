from sqlalchemy.orm import sessionmaker

from superagi.helper.llama_vector_store_helper import create_llama_document, \
    generate_summary_of_document, save_document_to_vector_store
from superagi.helper.llama_vector_store_helper import generate_summary_of_texts
from superagi.lib.logger import logger
from superagi.models.agent_config import AgentConfiguration
from superagi.models.db import connect_db
from superagi.models.resource import Resource


class ResourceSummarizer:

    @classmethod
    def add_to_vector_store_and_create_summary(cls, agent_id: int, resource_id: int, openai_api_key: str,
                                               file_path: str = None, file_object=None):
        """
        Add a file to the vector store and generate a summary for it.

        Args:
            file_path (str): Path of the file.
            file_object : File object.
            agent_id (str): ID of the agent.
            resource_id (int): ID of the resource.
            openai_api_key (str): OpenAI API key.
        """
        engine = connect_db()
        session = sessionmaker(bind=engine)
        db = session()
        documents = create_llama_document(file_path, file_object)
        try:
            save_document_to_vector_store(documents, str(agent_id), str(resource_id))
        except Exception as e:
            logger.error(e)
        summary = None
        try:
            summary = generate_summary_of_document(documents)
        except Exception as e:
            logger.error(e)
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        resource.summary = summary
        db.commit()

        # get all resources associated with the agent and check if all have summaries generated
        # if yes, then generate a summary for the agent and store it in the agent configuration

        # get all resources associated with the agent
        resources = db.query(Resource).filter(Resource.agent_id == agent_id).all()
        # check if all have summaries generated
        summary_texts = [resource.summary for resource in resources if resource.summary is not None]
        if len(summary_texts) != len(resources):
            return

        resource_summary = generate_summary_of_texts(summary_texts, openai_api_key)
        agent_resource_config = AgentConfiguration(agent_id=agent_id, key="resource_summary", value=resource_summary)
        agent_last_resource = AgentConfiguration(agent_id=agent_id, key="last_resource", value=str(resource.updated_at))
        db.add(agent_resource_config)
        db.add(agent_last_resource)
        db.commit()
        db.close()
