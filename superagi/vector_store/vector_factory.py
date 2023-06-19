import os

import pinecone
from pinecone import UnauthorizedException

from superagi.vector_store.document import Document
from superagi.vector_store.embedding.openai import OpenAiEmbedding, BaseEmbedding
from superagi.vector_store.pinecone import Pinecone
from superagi.vector_store import weaviate
from superagi.config.config import get_config
from superagi.vector_store.redis import Redis


class VectorFactory:

    @classmethod
    def get_vector_storage(cls, vector_store: str, index_name: str, embedding_model: BaseEmbedding,
                           vector_group_id: str):
        """
            Get the vector storage.

            Args:
                vector_store : The vector store name.
                index_name : The index name.
                embedding_model : The embedding model.

            Returns:
                The vector storage object.
        """
        if vector_store == "Pinecone":
            try:
                api_key = get_config("PINECONE_API_KEY")
                env = get_config("PINECONE_ENVIRONMENT")
                if api_key is None or env is None:
                    raise ValueError("PineCone API key not found")
                pinecone.init(api_key=api_key, environment=env)
                index = Pinecone.create_index(index_name, embedding_model)
                return Pinecone(index, embedding_model, 'text', namespace=vector_group_id)
            except UnauthorizedException:
                raise ValueError("PineCone API key not found")
        
        if vector_store == "Weaviate":
            use_embedded = get_config("WEAVIATE_USE_EMBEDDED")
            url = get_config("WEAVIATE_URL")
            api_key = get_config("WEAVIATE_API_KEY")

            client = weaviate.create_weaviate_client(
                use_embedded=use_embedded,
                url=url,
                api_key=api_key
            )
            return weaviate.Weaviate(client, embedding_model, index_name, 'text')

        if vector_store == "Redis":
            index_name = "super-agent-index1"
            redis = Redis(index_name, OpenAiEmbedding(api_key=get_config("OPENAI_API_KEY")), vector_group_id)
            redis.create_index()
            return redis
        else:
            raise ValueError("Invalid vector store")
