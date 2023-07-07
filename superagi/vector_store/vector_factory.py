import pinecone
from pinecone import UnauthorizedException

from superagi.vector_store.pinecone import Pinecone
from superagi.vector_store import weaviate
from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.types.vector_store_types import VectorStoreType


class VectorFactory:

    @classmethod
    def get_vector_storage(cls, vector_store: VectorStoreType, index_name, embedding_model):
        """
        Get the vector storage.

        Args:
            vector_store : The vector store name.
            index_name : The index name.
            embedding_model : The embedding model.

        Returns:
            The vector storage object.
        """
        vector_store = VectorStoreType.get_vector_store_type(vector_store)
        if vector_store == VectorStoreType.PINECONE:
            try:
                api_key = get_config("PINECONE_API_KEY")
                env = get_config("PINECONE_ENVIRONMENT")
                if api_key is None or env is None:
                    raise ValueError("PineCone API key not found")
                pinecone.init(api_key=api_key, environment=env)

                if index_name not in pinecone.list_indexes():
                    sample_embedding = embedding_model.get_embedding("sample")
                    if "error" in sample_embedding:
                        logger.error(f"Error in embedding model {sample_embedding}")

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

        raise ValueError(f"Vector store {vector_store} not supported")
