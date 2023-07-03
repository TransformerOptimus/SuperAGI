 
import unittest
from unittest.mock import MagicMock
from superagi.vector_store.embedding.openai import BaseEmbedding
from superagi.vector_store.document import Document
from chromaDB_client import ChromaDBClient
from chromaDB import ChromaDB

class MockEmbeddingModel(BaseEmbedding):
    def get_embedding(self, text):
        return [0.1, 0.2, 0.3]  # Mock embedding representation

class ChromaDBTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock(spec=ChromaDBClient)
        self.embedding_model = MockEmbeddingModel()
        self.vector_store = ChromaDB(
            base_url='http://localhost:8000',  # Replace with your ChromaDB server URL
            embedding_model=self.embedding_model,
            text_field='text',
        )
        self.vector_store.client = self.mock_client

    def test_add_texts(self):
        texts = ['text1', 'text2', 'text3']
        metadatas = [{'meta': 'data1'}, {'meta': 'data2'}, {'meta': 'data3'}]
        ids = ['id1', 'id2', 'id3']
        namespace = 'namespace'
        batch_size = 2

        expected_data = {
            "vectors": [
                ('id1', [0.1, 0.2, 0.3], {'meta': 'data1'}),
                ('id2', [0.1, 0.2, 0.3], {'meta': 'data2'})
            ],
            "namespace": namespace,
            "batch_size": batch_size,
        }

        self.vector_store.add_texts(texts, metadatas, ids, namespace, batch_size=batch_size)

        self.mock_client.create_records.assert_called_once_with(expected_data)

    def test_get_matching_text(self):
        query = 'query'
        top_k = 5
        namespace = 'namespace'

        mock_response = {
            'matches': [
                {'metadata': {'text': 'text1', 'meta': 'data1'}},
                {'metadata': {'text': 'text2', 'meta': 'data2'}},
                {'metadata': {'text': 'text3', 'meta': 'data3'}}
            ]
        }
        self.mock_client.get_matching_records.return_value = mock_response

        expected_documents = [
            Document(text_content='text1', metadata={'text': 'text1', 'meta': 'data1'}),
            Document(text_content='text2', metadata={'text': 'text2', 'meta': 'data2'}),
            Document(text_content='text3', metadata={'text': 'text3', 'meta': 'data3'})
        ]

        documents = self.vector_store.get_matching_text(query, top_k, namespace)

        self.assertEqual(documents, expected_documents)
        self.mock_client.get_matching_records.assert_called_once_with([0.1, 0.2, 0.3], top_k, namespace)

if __name__ == '__main__':
    unittest.main()
