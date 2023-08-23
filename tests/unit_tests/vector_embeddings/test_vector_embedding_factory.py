import unittest
from unittest.mock import patch
from superagi.vector_embeddings.vector_embedding_factory import VectorEmbeddingFactory

class TestVectorEmbeddingFactory(unittest.TestCase):

    @patch("superagi.vector_embeddings.pinecone.Pinecone.__init__", return_value=None)
    @patch("superagi.vector_embeddings.qdrant.Qdrant.__init__", return_value=None)
    @patch("superagi.vector_embeddings.weaviate.Weaviate.__init__", return_value=None)
    def test_build_vector_storage(self, mock_weaviate, mock_qdrant, mock_pinecone):
        test_data = {
            "1": {"id": 1, "embeds": [1,2,3], "text": "test", "chunk": "chunk", "knowledge_name": "knowledge"},
            "2": {"id": 2, "embeds": [4,5,6], "text": "test2", "chunk": "chunk2", "knowledge_name": "knowledge2"},
        }

        vector_storage = VectorEmbeddingFactory.build_vector_storage('Pinecone', test_data)

        mock_pinecone.assert_called_once_with(
            [1,2], [[1,2,3],[4,5,6]], [{"text": "test", "chunk": "chunk", "knowledge_name": "knowledge"}, {"text": "test2", "chunk": "chunk2", "knowledge_name": "knowledge2"}]
        )

        vector_storage = VectorEmbeddingFactory.build_vector_storage('Qdrant', test_data)

        mock_qdrant.assert_called_once_with(
            [1,2], [[1,2,3],[4,5,6]], [{"text": "test", "chunk": "chunk", "knowledge_name": "knowledge"}, {"text": "test2", "chunk": "chunk2", "knowledge_name": "knowledge2"}]
        )

        vector_storage = VectorEmbeddingFactory.build_vector_storage('Weaviate', test_data)

        mock_weaviate.assert_called_once_with(
            [1,2], [[1,2,3],[4,5,6]], [{"text": "test", "chunk": "chunk", "knowledge_name": "knowledge"}, {"text": "test2", "chunk": "chunk2", "knowledge_name": "knowledge2"}]
        )

if __name__ == "__main__":
    unittest.main()
