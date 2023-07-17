import pinecone
from pinecone import UnauthorizedException

from superagi.vector_store.pinecone import Pinecone
from superagi.vector_store import weaviate
from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.types.vector_store_types import VectorStoreType
from superagi.vector_store import qdrant

from superagi.vector_store.qdrant import Qdrant


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
        if isinstance(vector_store, str):
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

        if vector_store == VectorStoreType.WEAVIATE:
            use_embedded = get_config("WEAVIATE_USE_EMBEDDED")
            url = get_config("WEAVIATE_URL")
            api_key = get_config("WEAVIATE_API_KEY")

            client = weaviate.create_weaviate_client(
                use_embedded=use_embedded,
                url=url,
                api_key=api_key
            )
            return weaviate.Weaviate(client, embedding_model, index_name, 'text')

        if vector_store == VectorStoreType.QDRANT:
            client = qdrant.create_qdrant_client()
            sample_embedding = embedding_model.get_embedding("sample")
            if "error" in sample_embedding:
                logger.error(f"Error in embedding model {sample_embedding}")

            Qdrant.create_collection(client, index_name, len(sample_embedding))
            return qdrant.Qdrant(client, embedding_model, index_name)

        raise ValueError(f"Vector store {vector_store} not supported")


    @classmethod
    def get_vector_index_stats(cls, vector_store: VectorStoreType, index_name, **creds):
        vector_store = VectorStoreType.get_vector_store_type(vector_store)
        if vector_store == VectorStoreType.PINECONE:
            api_key = creds["api_key"]
            environment = creds["environment"]
            try:
                pinecone.init(api_key=api_key, environment=environment)
                index = pinecone.Index(index_name)
                pinecone_object = Pinecone(index=index)
                index_stats = pinecone_object.get_index_stats()
            except UnauthorizedException:
                raise ValueError("PineCone API key not found")
            return index_stats

        if vector_store == VectorStoreType.QDRANT:
            try:
                client = qdrant.create_qdrant_client(creds["api_key"], creds["url"], creds["port"])
                qdrant_object = Qdrant(client=client, collection_name=index_name)
                index_stats = qdrant_object.get_index_stats()
            except:
                raise ValueError("Qdrant API key not found")
            return index_stats

    @classmethod
    def add_embeddings_to_vector_store(self, vector_store: VectorStoreType, index_name, **upsert_data_with_creds):
        vector_store = VectorStoreType.get_vector_store_type(vector_store)
        if vector_store == VectorStoreType.PINECONE:
            api_key = upsert_data_with_creds["creds"]["api_key"] if upsert_data_with_creds.has_key("creds") else None
            environment = upsert_data_with_creds["creds"]["environment"] if upsert_data_with_creds.has_key("creds") else None
            try:
                pinecone.init(api_key=api_key, environment=environment)
                index = pinecone.Index(index_name)
                pinecone_object = Pinecone(index=index)
                pinecone_object.add_embeddings_to_vector_db(embeddings=upsert_data_with_creds["embeddings"])
            except UnauthorizedException:
                raise ValueError("PineCone API key not found")

        if vector_store == VectorStoreType.QDRANT:
            try:
                api_key = upsert_data_with_creds["creds"]["api_key"] if upsert_data_with_creds.has_key("creds") else None
                url = upsert_data_with_creds["creds"]["url"] if upsert_data_with_creds.has_key("creds") else None
                port = upsert_data_with_creds["creds"]["port"] if upsert_data_with_creds.has_key("creds") else None
                client = qdrant.create_qdrant_client(api_key=api_key, url=url, port=port)
                qdrant_object = Qdrant(client=client, collection_name=index_name)
                qdrant_object.add_embeddings_to_vector_db(embeddings=upsert_data_with_creds["embeddings"])
            except:
                raise ValueError("Qdrant API key not found")

    @classmethod
    def delete_embeddings_from_vector_store(self, vector_store: VectorStoreType, index_name, vector_ids, **creds):
        vector_store = VectorStoreType.get_vector_store_type(vector_store)
        if vector_store == VectorStoreType.PINECONE:
            try:
                pinecone.init(api_key=creds["api_key"], environment=creds["environment"])
                index = pinecone.Index(index_name)
                pinecone_object = Pinecone(index=index)
                pinecone_object.delete_embeddings_from_vector_db(vector_ids=vector_ids)
            except UnauthorizedException:
                raise ValueError("PineCone API key not found")

        if vector_store == VectorStoreType.QDRANT:
            try:
                client = qdrant.create_qdrant_client(creds["api_key"], creds["url"], creds["port"])
                qdrant_object = Qdrant(client=client, collection_name=index_name)
                qdrant_object.delete_embeddings_from_vector_db(vector_ids=vector_ids)
            except:
                raise ValueError("Qdrant API key not found")
    
    @classmethod
    def match_query_with_text(cls, vector_store: VectorStoreType, index_name, query, filters, embedding_model, **creds):
        vector_store = VectorStoreType.get_vector_store_type(vector_store)
        if vector_store == VectorStoreType.PINECONE:
            try:
                pinecone.init(api_key=creds["api_key"], environment=creds["environment"])
                index = pinecone.Index(index_name)
                pinecone_object = Pinecone(index=index, embedding_model=embedding_model)
                search_result = pinecone_object.get_matching_text(query=query, metadata=filters)
            except UnauthorizedException:
                raise ValueError("PineCone API key not found")
        
        if vector_store == VectorStoreType.QDRANT:
            try:
                client = qdrant.create_qdrant_client(creds["api_key"], creds["url"], creds["port"])
                qdrant_object = Qdrant(client=client, collection_name=index_name, embedding_model=embedding_model)
                search_result = qdrant_object.get_matching_text(query=query, filters=filters)
            except:
                raise ValueError("Qdrant API key not found")
        
        return search_result