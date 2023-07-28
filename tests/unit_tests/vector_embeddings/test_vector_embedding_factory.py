import unittest
from unittest.mock import patch
from superagi.types.vector_store_types import VectorStoreType
import superagi
from superagi.vector_embeddings.vector_embedding_factory import VectorEmbeddingFactory

class TestVectorEmbeddingFactory(unittest.TestCase):

  @patch('superagi.vector_embeddings.pinecone.Pinecone.__init__', return_value=None) 
  def test_build_vector_storge_pinecone(self, mock_pinecone):
      result = VectorEmbeddingFactory.build_vector_storge('PINECONE')
      mock_pinecone.assert_called_once()
      self.assertIsInstance(result, superagi.vector_embeddings.pinecone.Pinecone)

  @patch('superagi.vector_embeddings.qdrant.Qdrant.__init__', return_value=None)
  def test_build_vector_storge_qdrant(self, mock_qdrant):
      result = VectorEmbeddingFactory.build_vector_storge('QDRANT')
      mock_qdrant.assert_called_once()
      self.assertIsInstance(result, superagi.vector_embeddings.qdrant.Qdrant)

  def test_build_vector_storge_invalid(self):
      with self.assertRaises(ValueError):
          VectorEmbeddingFactory.build_vector_storge('INVALID')

if __name__ == '__main__':
    unittest.main()