from superagi.models.agent_config import AgentConfiguration

from superagi.models.knowledges import Knowledges
from superagi.models.vector_db_indices import VectordbIndices
from superagi.models.vector_dbs import Vectordbs
from superagi.models.vector_db_configs import VectordbConfigs
from superagi.models.toolkit import Toolkit
from superagi.vector_store.vector_factory import VectorFactory
from superagi.models.configuration import Configuration
from superagi.jobs.agent_executor import AgentExecutor

from typing import Any, Type, List
from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool

# from superagi.tools.file.read_file import ReadFileTool


class KnowledgeSearchSchema(BaseModel):
    query: str = Field(..., description="The query to search required from knowledge search")


class KnowledgeSearchTool(BaseTool):
    name: str = "Knowledge Search"
    args_schema: Type[BaseModel] = KnowledgeSearchSchema
    agent_id: int = None
    description = (
        "A tool for performing a Knowledge search on knowledge base which might have knowledge of the task you are pursuing."
        "To find relevant info, use this tool first before using other tools."
        "If you don't find sufficient info using Knowledge tool, you may use other tools."
        "If a question is being asked, responding with context from info returned by knowledge tool is prefered."
        "Input should be a search query."
    )

    def _execute(self, query: str):
        session = self.toolkit_config.session
        toolkit = session.query(Toolkit).filter(Toolkit.id == self.toolkit_config.toolkit_id).first()
        organisation_id = toolkit.organisation_id
        knowledge_id = session.query(AgentConfiguration).filter(AgentConfiguration.agent_id == self.agent_id, AgentConfiguration.key == "knowledge").first().value
        knowledge = Knowledges.get_knowledge_from_id(session, knowledge_id)
        if knowledge is None:
            return "Selected Knowledge not found"
        vector_db_index = VectordbIndices.get_vector_index_from_id(session, knowledge.vector_db_index_id)
        vector_db = Vectordbs.get_vector_db_from_id(session, vector_db_index.vector_db_id)
        db_creds = VectordbConfigs.get_vector_db_config_from_db_id(session, vector_db.id)
        model_api_key = Configuration.fetch_configuration(session, organisation_id, "model_api_key")
        model_source = Configuration.fetch_configuration(session, organisation_id, "model_source")
        embedding_model = AgentExecutor.get_embedding(model_source, model_api_key)
        try:
            if vector_db_index.state == "Custom":
                filters = None
            if vector_db_index.state == "Marketplace":
                filters = {"knowledge_name": knowledge.name}
            vector_db_storage = VectorFactory.build_vector_storage(vector_db.db_type, vector_db_index.name, embedding_model, **db_creds)
            search_result = vector_db_storage.get_matching_text(query, metadata=filters)
            return f"Result: \n{search_result['search_res']}"
        except Exception as err:
            return f"Error fetching text: {err}"
        