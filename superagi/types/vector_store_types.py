from enum import Enum


class VectorStoreType(Enum):
    REDIS = 'redis'
    PINECONE = 'pinecone'
    CHROMA = 'chroma'
    WEAVIATE = 'weaviate'
    QDRANT = 'qdrant'
    LANCEDB = 'LanceDB'

    @classmethod
    def get_vector_store_type(cls, store):
        if store is None:
            raise ValueError("Vector store type cannot be None.")
        store = str(store).upper().strip()
        if store in cls.__members__:
            return cls[store]
        raise ValueError(f"{store} is not a valid vector store name.")

    def __str__(self):
        return self.value
