
import pinecone
from pinecone import UnauthorizedException
from superagi.vector_embeddings.pinecone import Pinecone
from superagi.vector_embeddings.qdrant import Qdrant
from superagi.types.vector_store_types import VectorStoreType

class VectorEmbeddingFactory:

    @classmethod
    def build_vector_storge(cls, vector_store: VectorStoreType):
        """
        Get the vector embeddings from final chunks.
        Args:
            vector_store : The vector store name.
        Returns:
            The vector storage object
        """
        vector_store = VectorStoreType.get_vector_store_type(vector_store)
        if vector_store == VectorStoreType.PINECONE:
            return Pinecone()

        if vector_store == VectorStoreType.QDRANT:
            return Qdrant()