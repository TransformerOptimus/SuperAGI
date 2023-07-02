import os

from llama_index import SimpleDirectoryReader

from superagi.config.config import get_config
from superagi.helper.resource_helper import ResourceHelper
from superagi.lib.logger import logger
from superagi.resource_manager.llama_vector_store_factory import LlamaVectorStoreFactory
from superagi.types.vector_store_types import VectorStoreType


class ResourceManager:
    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id

    def create_llama_document(self, file_path: str):
        """
        Creates a document index from a given file path.
        """
        if file_path is None:
            raise Exception("file_path must be provided")
        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()

        return documents

    def create_llama_document_s3(self, file_path: str):
        """
        Creates a document index from a given file path.
        """

        if file_path is None:
            raise Exception("file_path must be provided")

        import boto3
        s3 = boto3.client(
            's3',
            aws_access_key_id=get_config("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_config("AWS_SECRET_ACCESS_KEY"),
        )
        bucket_name = get_config("BUCKET_NAME")
        print(bucket_name, file_path)
        file = s3.get_object(Bucket=bucket_name, Key=file_path)
        file_name = file_path.split("/")[-1]
        save_directory = ResourceHelper.get_root_input_dir() + "/"
        file_path = save_directory + file_name
        with open(file_path, "wb") as f:
            contents = file['Body'].read()
            f.write(contents)

        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
        os.remove(file_path)
        return documents

    def save_document_to_vector_store(self, documents: list, resource_id: str):
        from llama_index import VectorStoreIndex, StorageContext
        import openai
        openai.api_key = get_config("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = get_config("OPENAI_API_KEY")
        for docs in documents:
            if docs.metadata is None:
                docs.metadata = {}
            docs.metadata["agent_id"] = str(self.agent_id)
            docs.metadata["resource_id"] = resource_id
        vector_store = None
        storage_context = None
        vector_store_name = VectorStoreType.get_vector_store_type(get_config("RESOURCE_VECTOR_STORE") or "Redis")
        vector_store_index_name = get_config("RESOURCE_VECTOR_STORE_INDEX_NAME") or "super-agent-index"
        try:
            vector_store = LlamaVectorStoreFactory(vector_store_name, vector_store_index_name).get_vector_store()
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
        except ValueError as e:
            logger.error(f"Vector store not found{e}")
        try:
            index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
            index.set_index_id(f'Agent {self.agent_id}')
        except Exception as e:
            print(e)
        # persisting the data in case of redis
        if vector_store_name == VectorStoreType.REDIS:
            vector_store.persist(persist_path="")
