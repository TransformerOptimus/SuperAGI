import logging
import os
from typing import Optional
from typing import Type

import openai
from langchain.chat_models import ChatOpenAI
from llama_index import VectorStoreIndex, LLMPredictor, ServiceContext
from llama_index.vector_stores.types import ExactMatchFilter, MetadataFilters
from pydantic import BaseModel, Field

from superagi.config.config import get_config
from superagi.llms.base_llm import BaseLlm
from superagi.resource_manager.llama_vector_store_factory import LlamaVectorStoreFactory
from superagi.tools.base_tool import BaseTool
from superagi.types.vector_store_types import VectorStoreType
from superagi.vector_store.chromadb import ChromaDB


class QueryResource(BaseModel):
    """Input for QueryResource tool."""
    query: str = Field(..., description="the search query to search resources")


class QueryResourceTool(BaseTool):
    """
    Read File tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "QueryResource"
    args_schema: Type[BaseModel] = QueryResource
    description: str = "Tool searches resources content and extracts relevant information to perform the given task." \
                       "Tool is given preference over other search/read file tools for relevant data." \
                       "Resources content is taken from the files: {summary}"
    agent_id: int = None
    llm: Optional[BaseLlm] = None

    def _execute(self, query: str):
        openai.api_key = self.llm.get_api_key()
        os.environ["OPENAI_API_KEY"] = self.llm.get_api_key()
        llm_predictor_chatgpt = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name=self.llm.get_model(),
                                                            openai_api_key=get_config("OPENAI_API_KEY")))

        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor_chatgpt)
        vector_store_name = VectorStoreType.get_vector_store_type(
            self.get_tool_config(key="RESOURCE_VECTOR_STORE") or "Redis")
        vector_store_index_name = self.get_tool_config(key="RESOURCE_VECTOR_STORE_INDEX_NAME") or "super-agent-index"
        logging.info(f"vector_store_name {vector_store_name}")
        logging.info(f"vector_store_index_name {vector_store_index_name}")
        vector_store = LlamaVectorStoreFactory(vector_store_name, vector_store_index_name).get_vector_store()
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
            as_query_engine_args["chroma_collection"] = ChromaDB.create_collection(
                collection_name=vector_store_index_name)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, service_context=service_context)
        query_engine = index.as_query_engine(
            **as_query_engine_args
        )
        try:
            response = query_engine.query(query)
        except ValueError as e:
            logging.error(f"ValueError {e}")
            response = "Document not found"
        return response
