from sqlalchemy.orm import sessionmaker

from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.models.agent_config import AgentConfiguration
from superagi.models.db import connect_db
from superagi.models.resource import Resource
from superagi.resource_manager.resource_manager import ResourceManager

engine = connect_db()
session = sessionmaker(bind=engine)

class ResourceSummarizer:

    @classmethod
    def add_to_vector_store_and_create_summary(cls, agent_id: int, resource_id: int, documents: list):
        """
        Add a file to the vector store and generate a summary for it.

        Args:
            agent_id (str): ID of the agent.
            resource_id (int): ID of the resource.
            openai_api_key (str): OpenAI API key.
            documents (list): List of documents.
        """
        db = session()
        try:
            ResourceManager.save_document_to_vector_store(documents, str(agent_id), str(resource_id))
        except Exception as e:
            logger.error(e)
        summary = None
        try:
            summary = ResourceManager.generate_summary_of_document(documents)
        except Exception as e:
            logger.error(e)
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        resource.summary = summary
        db.commit()
        resources = db.query(Resource).filter(Resource.agent_id == agent_id).all()
        summary_texts = [resource.summary for resource in resources if resource.summary is not None]
        if len(summary_texts) != len(resources):
            return

        if len(summary_texts) == 1:
            resource_summary = summary_texts[0]
        else:
            openai_api_key = get_config("OPENAI_API_KEY")
            resource_summary = ResourceManager.generate_summary_of_texts(summary_texts, openai_api_key)

        agent_config_resource_summary = db.query(AgentConfiguration). \
            filter(AgentConfiguration.agent_id == agent_id,
                   AgentConfiguration.key == "resource_summary").first()

        agent_last_resource = db.query(AgentConfiguration). \
            filter(AgentConfiguration.agent_id == agent_id,
                   AgentConfiguration.key == "last_resource").first()

        if agent_config_resource_summary is not None:
            agent_config_resource_summary.value = resource_summary
        else:
            agent_config_resource_summary = AgentConfiguration(agent_id=agent_id, key="resource_summary",
                                                               value=resource_summary)
            db.add(agent_config_resource_summary)
        if agent_last_resource is not None:
            agent_last_resource.value = str(resource.updated_at)
        else:
            agent_last_resource = AgentConfiguration(agent_id=agent_id, key="last_resource",
                                                     value=str(resource.updated_at))
            db.add(agent_last_resource)
        db.commit()
        db.close()