from sqlalchemy.orm import sessionmaker

from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.models.agent_config import AgentConfiguration
from superagi.models.resource import Resource
from superagi.resource_manager.llama_document_summary import LlamaDocumentSummary
from superagi.resource_manager.resource_manager import ResourceManager
from datetime import datetime


class ResourceSummarizer:
    """Class to summarize a resource."""

    def __int__(self, session):
        self.session = session

    @classmethod
    def add_to_vector_store_and_create_summary(self, agent_id: int, resource_id: int, documents: list):
        """
        Add a file to the vector store and generate a summary for it.

        Args:
            agent_id (str): ID of the agent.
            resource_id (int): ID of the resource.
            openai_api_key (str): OpenAI API key.
            documents (list): List of documents.
        """
        try:
            ResourceManager(agent_id).save_document_to_vector_store(documents, str(resource_id))
        except Exception as e:
            logger.error(e)
        summary = None
        try:
            summary = LlamaDocumentSummary().generate_summary_of_document(documents)
        except Exception as e:
            logger.error(e)
        resource = self.session.query(Resource).filter(Resource.id == resource_id).first()
        resource.summary = summary
        self.session.commit()

    def generate_agent_summary(self, agent_id: int) -> str:
        """Generate a summary of all resources for an agent."""
        agent_config_resource_summary = self.session.query(AgentConfiguration). \
            filter(AgentConfiguration.agent_id == agent_id,
                   AgentConfiguration.key == "resource_summary").first()
        resources = self.session.query(Resource).filter(Resource.agent_id == agent_id).all()
        summary_texts = [resource.summary for resource in resources if resource.summary is not None]
        if len(summary_texts) != len(resources):
            return

        agent_last_resource = self.session.query(AgentConfiguration). \
            filter(AgentConfiguration.agent_id == agent_id,
                   AgentConfiguration.key == "last_resource_id").first()
        if agent_last_resource is not None and \
                datetime.strptime(agent_last_resource.value, '%Y-%m-%d %H:%M:%S.%f') == resources[-1].updated_at:
            return

        resource_summary = LlamaDocumentSummary().generate_summary_of_texts(summary_texts)
        if agent_config_resource_summary is not None:
            agent_config_resource_summary.value = resource_summary
        else:
            agent_config_resource_summary = AgentConfiguration(agent_id=agent_id, key="resource_summary",
                                                               value=resource_summary)
            self.session.add(agent_config_resource_summary)
        if agent_last_resource is not None:
            agent_last_resource.value = str(self.session.updated_at)
        else:
            agent_last_resource = AgentConfiguration(agent_id=agent_id, key="last_resource_id",
                                                     value=str(resources[-1].updated_at))
            self.session.add(agent_last_resource)
        self.session.commit()
