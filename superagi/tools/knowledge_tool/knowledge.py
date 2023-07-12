import json
from abc import ABC, abstractmethod
from superagi.config.config import get_config
import openai

from typing import Type, List
from pydantic import BaseModel, Field

from superagi.helper.knowledge_tool import KnowledgeToolHelper
from superagi.helper.knowledge_db_helper import KnowledgeToolDbHelper
from superagi.models.agent_config import AgentConfiguration
from superagi.models.knowledge import Knowledge
from superagi.tools.base_tool import BaseTool
# from superagi.tools.file.read_file import ReadFileTool
import pandas as pd


# 1. define input schema
class KnowledgeSearchSchema(BaseModel):
    query: str = Field(..., description="The search query for knowledge store search")


# 2. setup name, arg, description
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
        knowledge_id = session.query(AgentConfiguration).filter(
            AgentConfiguration.agent_id == self.agent_id,
            AgentConfiguration.key == "knowledge").first()
        knowledge = session.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
        dbhelper = KnowledgeToolDbHelper(session)
        knowledge_details = dbhelper.get_knowledge_details(knowledge)
        query_knowledge = KnowledgeToolHelper()

        if knowledge_details["knowledge_vector_db_type"] == "Pinecone":
            vector_db_creds = dbhelper.get_pinecone_creds(knowledge_details["knowledge_vector_db_id"])
            req_context = query_knowledge.pinecone_get_match_vectors(query,vector_db_creds,knowledge_details)
        elif knowledge_details["knowledge_vector_db_type"] == "Qdrant":
            vector_db_creds = dbhelper.get_qdrant_creds(knowledge_details["knowledge_vector_db_id"])
            req_context = query_knowledge.pinecone_get_match_vectors(query,vector_db_creds,knowledge_details)
        return req_context



        
        
