import os
from typing import Type

from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
import openai
from llama_index import VectorStoreIndex, LLMPredictor, ServiceContext
from superagi.helper.llama_vector_store_helper import llama_vector_store_factory
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
        llm_predictor_chatgpt = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo",
                                                            openai_api_key=get_config("OPENAI_API_KEY")))
        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor_chatgpt)
        vector_store_name = get_config("RESOURCE_VECTOR_STORE") or "Redis"
        vector_store_index_name = get_config("resource_vector_store_index_name") or "super-agent-index"
        print("vector_store_name", vector_store_name)
        print("vector_store_index_name", vector_store_index_name)
        vector_store = llama_vector_store_factory(vector_store_name, vector_store_index_name, OpenAiEmbedding(model_api_key))
        print("vector_store", vector_store)
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
        if vector_store_name == "chroma":
            vector_store, chroma_collection = vector_store[0], vector_store[1]
            as_query_engine_args["chroma_collection"] = chroma_collection
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, service_context=service_context)
        query_engine = index.as_query_engine(
            **as_query_engine_args
        )
        response = query_engine.query(query)
        return response