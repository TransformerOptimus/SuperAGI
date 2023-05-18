import os

import pinecone
from pinecone import UnauthorizedException

from superagi.vector_store.pinecone import Pinecone
from superagi.config.config import get_config


class VectorFactory:

    @classmethod
    def get_vector_storage(cls, vector_store, index_name, embedding_model):
        if vector_store == "PineCone":
            try:
                api_key = get_config("PINECONE_API_KEY")
                env = get_config("PINECONE_ENVIRONMENT")
                pinecone.init(api_key=api_key, environment=env)

                if index_name not in pinecone.list_indexes():
                    sample_embedding = embedding_model.get_embedding("sample")

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
        else:
            raise Exception("Vector store not supported")
