from datetime import datetime

from superagi.lib.logger import logger
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.configuration import Configuration
from superagi.models.resource import Resource
from superagi.resource_manager.llama_document_summary import LlamaDocumentSummary
from superagi.resource_manager.resource_manager import ResourceManager


class ResourceSummarizer:
    """Class to summarize a resource."""

    def __init__(self, session):
        self.session = session

    def add_to_vector_store_and_create_summary(self, agent_id: int, resource_id: int, documents: list):
        """
        Add a file to the vector store and generate a summary for it.

        Args:
            agent_id (str): ID of the agent.
            resource_id (int): ID of the resource.
            openai_api_key (str): OpenAI API key.
            documents (list): List of documents.
        """
        agent = self.session.query(Agent).filter(Agent.id == agent_id).first()
        organization = agent.get_agent_organisation(self.session)
        model_api_key = Configuration.fetch_configuration(self.session, organization.id, "model_api_key")
        model_source = Configuration.fetch_configuration(self.session, organization.id, "model_source") or "OpenAi"
        try:
            ResourceManager(str(agent_id)).save_document_to_vector_store(documents, str(resource_id), model_api_key, model_source)
        except Exception as e:
            logger.error("add_to_vector_store_and_create_summary: Unable to save document to vector store.", e)

    def generate_agent_summary(self, agent_id: int, generate_all: bool = False) -> str:
        """Generate a summary of all resources for an agent."""
        agent_config_resource_summary = self.session.query(AgentConfiguration). \
            filter(AgentConfiguration.agent_id == agent_id,
                   AgentConfiguration.key == "resource_summary").first()
        resources = self.session.query(Resource).filter(Resource.agent_id == agent_id,Resource.channel == 'INPUT').all()
        if not resources:
            return

        resource_summary = " ".join([resource.name for resource in resources])
        agent_last_resource = self.session.query(AgentConfiguration). \
            filter(AgentConfiguration.agent_id == agent_id,
                   AgentConfiguration.key == "last_resource_time").first()


        if agent_config_resource_summary is not None:
            agent_config_resource_summary.value = resource_summary
        else:
            agent_config_resource_summary = AgentConfiguration(agent_id=agent_id, key="resource_summary",
                                                               value=resource_summary)
            self.session.add(agent_config_resource_summary)
        if agent_last_resource is not None:
            agent_last_resource.value = str(resources[-1].updated_at)
        else:
            agent_last_resource = AgentConfiguration(agent_id=agent_id, key="last_resource_time",
                                                     value=str(resources[-1].updated_at))
            self.session.add(agent_last_resource)
        self.session.commit()
