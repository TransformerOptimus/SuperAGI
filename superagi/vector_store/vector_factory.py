import os

import pinecone
from pinecone import UnauthorizedException

from superagi.vector_store.pinecone import Pinecone
from superagi.vector_store import weaviate
from superagi.config.config import get_config


class VectorFactory:

    @classmethod
    def get_vector_storage(cls, vector_store, index_name, embedding_model):
        """
        Get the vector storage.

        Args:
            vector_store : The vector store name.
            index_name : The index name.
            embedding_model : The embedding model.

        Returns:
            The vector storage object.
        """
        if vector_store.lower() == "pinecone":
            try:
                api_key = get_config("PINECONE_API_KEY")
                env = get_config("PINECONE_ENVIRONMENT")
                if api_key is None or env is None:
                    raise ValueError("PineCone API key not found")
                pinecone.init(api_key=api_key, environment=env)

                if index_name not in pinecone.list_indexes():
                    sample_embedding = embedding_model.get_embedding("sample")
                    if "error" in sample_embedding:
                        print("Error in embedding model", sample_embedding)

                    # if does not exist, create index
                    pinecone.create_index(
                        index_name,
                        dimension=len(sample_embedding),
                        metric='dotproduct'
                    )
                index = pinecone.Index(index_name)
                return Pinecone(index, embedding_model, 'text')
            except UnauthorizedException:
                raise ValueError("PineCone API key not found")
        
        if vector_store.lower() == "weaviate":
            
            use_embedded = get_config("WEAVIATE_USE_EMBEDDED")
            url = get_config("WEAVIATE_URL")
            api_key = get_config("WEAVIATE_API_KEY")

            client = weaviate.create_weaviate_client(
                use_embedded=use_embedded,
                url=url,
                api_key=api_key
            )
            return weaviate.Weaviate(client, embedding_model, index_name, 'text')

        if vector_store.lower() == "redis":
            redis_url = get_config("REDIS_URL") or "redis://super__redis:6379"
            from llama_index.vector_stores import RedisVectorStore
            return RedisVectorStore(
                index_name=index_name,
                redis_url=redis_url,
                metadata_fields=["agent_id", "resource_id"]
            )

        if vector_store.lower() == "chroma":
            from llama_index.vector_stores import ChromaVectorStore
            import chromadb
            from chromadb.config import Settings
            chroma_host = get_config("CHROMA_HOST") or "chroma"
            chroma_port = get_config("CHROMA_PORT") or 8000
            # Example setup of the client to connect to your chroma server
            chroma_client = chromadb.Client(
                Settings(chroma_api_impl="rest", chroma_server_host=chroma_host, chroma_server_http_port=chroma_port))
            chroma_collection = chroma_client.get_or_create_collection(index_name)
            return ChromaVectorStore(chroma_collection), chroma_collection

        raise ValueError(f"Vector store {vector_store} not supported")
