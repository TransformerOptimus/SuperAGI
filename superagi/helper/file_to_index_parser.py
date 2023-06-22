from llama_index import SimpleDirectoryReader
import os

from superagi.jobs.agent_executor import AgentExecutor
from superagi.models.agent_execution import AgentExecution
from superagi.vector_store.embedding.openai import OpenAiEmbedding
from superagi.config.config import get_config

def create_document_index(file_path: str, agent_id: int, session):
    """
    Creates a document index from a given directory.
    """
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()

    return documents


def llama_vector_store_factory(vector_store, index_name, embedding_model, session, agent_id):
    """
    Creates a llama vector store.
    """
    model_api_key = get_config("OPENAI_API_KEY")
    # agent_execution = AgentExecution(agent_id=agent_id)
    # agent_executor = AgentExecutor()
    # model_api_key = agent_executor.get_model_api_key_from_execution(agent_execution, session)
    from superagi.vector_store.vector_factory import VectorFactory
    vector_store = VectorFactory.get_vector_storage("PineCone", "super-agent-index1",
                                                    OpenAiEmbedding(model_api_key))
    if vector_store is None:
        raise ValueError("Vector store not found")
    if vector_store == "PineCone":
        from llama_index.vector_stores import PineconeVectorStore
        return PineconeVectorStore(index_name, embedding_model, 'text')
