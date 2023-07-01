import csv
import os

from llama_index import SimpleDirectoryReader
from llama_index.indices.response import ResponseMode
from llama_index.schema import Document
from sqlalchemy.orm import Session

from superagi.config.config import get_config
from superagi.helper.resource_helper import ResourceHelper
from superagi.helper.s3_helper import S3Helper
from superagi.lib.logger import logger
from superagi.types.vector_store_types import VectorStoreType


class ResourceManager:
    def __init__(self, session: Session, agent_id: int = None):
        self.session = session
        self.agent_id = agent_id

    def write_binary_file(self, file_name: str, data):
        if self.agent_id is not None:
            final_path = ResourceHelper.get_agent_resource_path(file_name, self.agent_id)
        else:
            final_path = ResourceHelper.get_resource_path(file_name)

        # if self.agent_id is not None:
        #     directory = os.path.dirname(final_path + "/" + str(self.agent_id) + "/")
        #     os.makedirs(directory, exist_ok=True)
        try:
            with open(final_path, mode="wb") as img:
                img.write(data)
                img.close()
            self.write_to_s3(file_name, final_path)
            logger.info(f"Binary {file_name} saved successfully")
            return f"Binary {file_name} saved successfully"
        except Exception as err:
            return f"Error: {err}"

    def write_to_s3(self, file_name, final_path):
        with open(final_path, 'rb') as img:
            resource = ResourceHelper.make_written_file_resource(file_name=file_name,
                                                                 agent_id=self.agent_id, channel="OUTPUT")
            if resource is not None:
                self.session.add(resource)
                self.session.commit()
                self.session.flush()
                if resource.storage_type == "S3":
                    s3_helper = S3Helper()
                    s3_helper.upload_file(img, path=resource.path)

    def write_file(self, file_name: str, content):
        if self.agent_id is not None:
            final_path = ResourceHelper.get_agent_resource_path(file_name, self.agent_id)
        else:
            final_path = ResourceHelper.get_resource_path(file_name)

        try:
            with open(final_path, mode="w") as file:
                file.write(content)
                file.close()
            self.write_to_s3(file_name, final_path)
            logger.info(f"{file_name} - File written successfully")
            return f"{file_name} - File written successfully"
        except Exception as err:
            return f"Error: {err}"

    def write_csv_file(self, file_name: str, csv_data):
        if self.agent_id is not None:
            final_path = ResourceHelper.get_agent_resource_path(file_name, self.agent_id)
        else:
            final_path = ResourceHelper.get_resource_path(file_name)

        try:
            with open(final_path, mode="w") as file:
                writer = csv.writer(file, lineterminator="\n")
                for row in csv_data:
                    writer.writerows(row)
            self.write_to_s3(file_name, final_path)
            logger.info(f"{file_name} - File written successfully")
            return f"{file_name} - File written successfully"
        except Exception as err:
            return f"Error: {err}"

    def get_agent_resource_path(self, file_name: str):
        return ResourceHelper.get_agent_resource_path(file_name, self.agent_id)

    @classmethod
    def create_llama_document(cls, file_path: str = None, file_object=None):
        """
        Creates a document index from a given directory.
        """

        if file_path is None and file_object is None:
            raise Exception("Either file_path or file_object must be provided")

        if file_path is not None and file_object is not None:
            raise Exception("Only one of file_path or file_object must be provided")

        save_directory = ResourceHelper.get_root_input_dir() + "/"

        if file_object is not None:
            file_path = save_directory + file_object.filename
            file_object.save(file_path)

        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()

        if file_object is not None:
            os.remove(file_path)

        return documents

    @classmethod
    def generate_summary_of_document(cls, documents: list[Document], openai_api_key: str = None):
        openai_api_key = openai_api_key or get_config("OPENAI_API_KEY")
        from llama_index import LLMPredictor, ServiceContext, ResponseSynthesizer, DocumentSummaryIndex
        from langchain.chat_models import ChatOpenAI
        os.environ["OPENAI_API_KEY"] = openai_api_key
        llm_predictor_chatgpt = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo",
                                                            openai_api_key=openai_api_key))
        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor_chatgpt, chunk_size=1024)
        response_synthesizer = ResponseSynthesizer.from_args(response_mode=ResponseMode.TREE_SUMMARIZE, use_async=True)
        doc_summary_index = DocumentSummaryIndex.from_documents(
            documents=documents,
            service_context=service_context,
            response_synthesizer=response_synthesizer
        )

        return doc_summary_index.get_document_summary(documents[0].doc_id)

    @classmethod
    def generate_summary_of_texts(cls, texts: list[str], openai_api_key: str):
        from llama_index import Document
        documents = [Document(doc_id=f"doc_id_{i}", text=text) for i, text in enumerate(texts)]
        return cls.generate_summary_of_document(documents, openai_api_key)

    @classmethod
    def llama_vector_store_factory(cls,vector_store_name: VectorStoreType, index_name, embedding_model):
        """
        Creates a llama vector store.
        """
        from superagi.vector_store.vector_factory import VectorFactory

        vector_factory_support = [VectorStoreType.PINECONE, VectorStoreType.WEAVIATE]
        if vector_store_name in vector_factory_support:
            vector_store = VectorFactory.get_vector_storage(vector_store_name, index_name,
                                                            embedding_model)
            if vector_store_name == VectorStoreType.PINECONE:
                from llama_index.vector_stores import PineconeVectorStore
                return PineconeVectorStore(vector_store.index)

            if vector_store_name == VectorStoreType.WEAVIATE:
                raise ValueError("Weaviate vector store is not supported yet.")

        if vector_store_name == VectorStoreType.REDIS:
            redis_url = get_config("REDIS_VECTOR_STORE_URL") or "redis://super__redis:6379"
            from llama_index.vector_stores import RedisVectorStore
            return RedisVectorStore(
                index_name=index_name,
                redis_url=redis_url,
                metadata_fields=["agent_id", "resource_id"]
            )

        if vector_store_name == VectorStoreType.CHROMA:
            from llama_index.vector_stores import ChromaVectorStore
            import chromadb
            from chromadb.config import Settings
            chroma_host_name = get_config("CHROMA_HOST_NAME") or "localhost"
            chroma_port = get_config("CHROMA_PORT") or 8000
            chroma_client = chromadb.Client(
                Settings(chroma_api_impl="rest", chroma_server_host=chroma_host_name,
                         chroma_server_http_port=chroma_port))
            chroma_collection = chroma_client.get_or_create_collection(index_name)
            return ChromaVectorStore(chroma_collection), chroma_collection

        if vector_store_name == VectorStoreType.QDRANT:
            from llama_index.vector_stores import QdrantVectorStore
            qdrant_host_name = get_config("QDRANT_HOST_NAME") or "localhost"
            qdrant_port = get_config("QDRANT_PORT") or 6333
            from qdrant_client import QdrantClient
            qdrant_client = QdrantClient(host=qdrant_host_name, port=qdrant_port)
            return QdrantVectorStore(client=qdrant_client, collection_name=index_name)

    @classmethod
    def save_document_to_vector_store(cls,documents: list, agent_id: str, resource_id: str):
        from llama_index import VectorStoreIndex, StorageContext
        import openai
        from superagi.vector_store.embedding.openai import OpenAiEmbedding
        model_api_key = get_config("OPENAI_API_KEY")
        for docs in documents:
            if docs.metadata is None:
                docs.metadata = {"agent_id": agent_id, "resource_id": resource_id}
            else:
                docs.metadata["agent_id"] = agent_id
                docs.metadata["resource_id"] = resource_id
        os.environ["OPENAI_API_KEY"] = get_config("OPENAI_API_KEY")
        vector_store = None
        storage_context = None
        vector_store_name = VectorStoreType.get_enum(get_config("RESOURCE_VECTOR_STORE") or "Redis")
        vector_store_index_name = get_config("RESOURCE_VECTOR_STORE_INDEX_NAME") or "super-agent-index"
        try:
            print(vector_store_name, vector_store_index_name)
            vector_store = cls.llama_vector_store_factory(vector_store_name, vector_store_index_name,
                                                      OpenAiEmbedding(model_api_key))
            if vector_store_name == VectorStoreType.CHROMA:
                vector_store, chroma_collection = vector_store
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
        except ValueError as e:
            logger.error(f"Vector store not found{e}")
        openai.api_key = get_config("OPENAI_API_KEY")
        try:
            index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
            index.set_index_id(f'Agent {agent_id}')
        except Exception as e:
            print(e)
        if vector_store_name == VectorStoreType.REDIS:
            vector_store.persist(persist_path="")