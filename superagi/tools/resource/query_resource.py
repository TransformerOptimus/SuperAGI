import logging
from typing import Type

import openai
from langchain.chat_models import ChatOpenAI
from llama_index import VectorStoreIndex, LLMPredictor, ServiceContext
from llama_index.vector_stores.types import ExactMatchFilter, MetadataFilters
from pydantic import BaseModel, Field

from superagi.config.config import get_config
from superagi.resource_manager.manager import ResourceManager
from superagi.tools.base_tool import BaseTool
from superagi.types.vector_store_types import VectorStoreType
from superagi.vector_store.embedding.openai import OpenAiEmbedding


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
        llm_predictor_chatgpt = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo",
                                                            openai_api_key=get_config("OPENAI_API_KEY")))
        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor_chatgpt)
        vector_store_name = VectorStoreType.get_enum(self.get_tool_config(key="RESOURCE_VECTOR_STORE") or "Redis")
        vector_store_index_name = self.get_tool_config(key="RESOURCE_VECTOR_STORE_INDEX_NAME") or "super-agent-index"
        logging.info(f"vector_store_name {vector_store_name}")
        logging.info(f"vector_store_index_name {vector_store_index_name}")
        vector_store = ResourceManager.llama_vector_store_factory(vector_store_name, vector_store_index_name,
                                                  OpenAiEmbedding(model_api_key))
        logging.info(f"vector_store {vector_store}")
        as_query_engine_args = dict(
            filters=MetadataFilters(
                filters=[
                    ExactMatchFilter(
                        key="agent_id",
                        value=str(self.agent_id)
                    )
                ]
            )
        )
        if vector_store_name == VectorStoreType.CHROMA:
            vector_store, chroma_collection = vector_store[0], vector_store[1]
            as_query_engine_args["chroma_collection"] = chroma_collection
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, service_context=service_context)
        query_engine = index.as_query_engine(
            **as_query_engine_args
        )
        response = query_engine.query(query)
        return response
