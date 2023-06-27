import os
from typing import Type

from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
import openai
from llama_index import VectorStoreIndex, LLMPredictor, ServiceContext
from superagi.helper.file_to_index_parser import llama_vector_store_factory
from superagi.vector_store.embedding.openai import OpenAiEmbedding
from llama_index.vector_stores.types import ExactMatchFilter, MetadataFilters


class QueryResource(BaseModel):
    """Input for QueryResource tool."""
    query: str = Field(..., description="Description of the information to be queried")


class QueryResourceTool(BaseTool):
    """
    Read File tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "Query Resource"
    args_schema: Type[BaseModel] = QueryResource
    description: str = "Has the ability to get information from a resource"
    agent_id: int = None

    def _execute(self, query: str):
        model_api_key = get_config("OPENAI_API_KEY")
        openai.api_key = model_api_key
        llm_predictor_chatgpt = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo",openai_api_key=get_config("OPENAI_API_KEY")))
        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor_chatgpt)
        vector_store = llama_vector_store_factory('PineCone', 'super-agent-index1', OpenAiEmbedding(model_api_key))
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store,service_context=service_context)
        query_engine = index.as_query_engine(
            filters=MetadataFilters(
                filters=[
                    ExactMatchFilter(
                        key="agent_id",
                        value=str(self.agent_id)
                    )
                ]
            )
        )
        response = query_engine.query(query)
        return response