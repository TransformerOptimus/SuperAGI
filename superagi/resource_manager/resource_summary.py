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
        model_source = Configuration.fetch_configuration(self.session, organization.id, "model_source")
        try:
            ResourceManager(str(agent_id)).save_document_to_vector_store(documents, str(resource_id), model_api_key, model_source)
        except Exception as e:
            logger.error("add_to_vector_store_and_create_summary: Unable to save document to vector store.", e)
        summary = None
        try:
            summary = LlamaDocumentSummary(model_api_key=model_api_key).generate_summary_of_document(documents)
        except Exception as e:
            logger.error("add_to_vector_store_and_create_summary - Unable to generate summary of document.", e)
        resource = self.session.query(Resource).filter(Resource.id == resource_id).first()
        resource.summary = summary
        self.session.commit()

    def generate_agent_summary(self, agent_id: int, generate_all: bool = False) -> str:
        """Generate a summary of all resources for an agent."""
        agent_config_resource_summary = self.session.query(AgentConfiguration). \
            filter(AgentConfiguration.agent_id == agent_id,
                   AgentConfiguration.key == "resource_summary").first()
        resources = self.session.query(Resource).filter(Resource.agent_id == agent_id,Resource.channel == 'INPUT').all()
        if not resources:
            return

        agent = self.session.query(Agent).filter(Agent.id == agent_id).first()
        organization = agent.get_agent_organisation(self.session)
        model_api_key = Configuration.fetch_configuration(self.session, organization.id, "model_api_key")
        model_source = Configuration.fetch_configuration(self.session, organization.id, "model_source")

        summary_texts = [resource.summary for resource in resources if resource.summary is not None]

        # generate_all is added because we want to generate summary for all resources when agent is created
        # this is set to false when adding individual resources
        if len(summary_texts) < len(resources) and generate_all:
            file_paths = [resource.path for resource in resources if resource.summary is None]
            for file_path in file_paths:
                if resources[0].storage_type == 'S3':
                    documents = ResourceManager(str(agent_id)).create_llama_document_s3(file_path)
                else:
                    documents = ResourceManager(str(agent_id)).create_llama_document(file_path)
                summary_texts.append(LlamaDocumentSummary(model_api_key=model_api_key, model_source=model_source).generate_summary_of_document(documents))

        agent_last_resource = self.session.query(AgentConfiguration). \
            filter(AgentConfiguration.agent_id == agent_id,
                   AgentConfiguration.key == "last_resource_time").first()
        if agent_last_resource is not None and \
                datetime.strptime(agent_last_resource.value, '%Y-%m-%d %H:%M:%S.%f') == resources[-1].updated_at \
                and not generate_all:
            return

        resource_summary = summary_texts[0] if summary_texts else None
        if len(summary_texts) > 1:
            resource_summary = LlamaDocumentSummary(model_api_key=model_api_key).generate_summary_of_texts(summary_texts)

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
