import os

from superagi.vector_store import pinecone
from superagi.vector_store.pinecone import Pinecone


class VectorFactory:

    @classmethod
    def get_vector_storage(cls, vector_store, index_name, embedding_model):
        if vector_store == "PineCone":
            api_key = os.getenv("PINECONE_API_KEY")
            env = os.getenv("PINECONE_ENVIRONMENT")
            pinecone.init(api_key=api_key, enviroment=env)

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
        else:
            raise Exception("Vector store not supported")