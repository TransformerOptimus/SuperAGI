import pinecone
from pinecone import UnauthorizedException
from superagi.vector_embeddings.pinecone import Pinecone
from superagi.vector_embeddings.qdrant import Qdrant
from superagi.types.vector_store_types import VectorStoreType

class VectorEmbeddingFactory:

    @classmethod
    def convert_final_chunks_to_embeddings(cls, vector_store: VectorStoreType, final_chunks):
        """
        Get the vector embeddings from final chunks.

        Args:
            vector_store : The vector store name.
            final_chunks: Final chunks of data.

        Returns:
            The vector embeddings.
        """
        vector_store = VectorStoreType.get_vector_store_type(vector_store)
        if vector_store.PINECONE:
            vector_embeddings = Pinecone.get_vector_embeddings_from_chunks(final_chunks)
        
        if vector_store.QDRANT:
            vector_embeddings = Qdrant.get_vector_embeddings_from_chunks(final_chunks)
        
        return vector_embeddings
