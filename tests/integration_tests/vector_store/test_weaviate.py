import unittest
from unittest.mock import Mock, patch, call, MagicMock
from superagi.vector_store.weaviate import create_weaviate_client, Weaviate, Document

class TestWeaviateClient(unittest.TestCase):
    @patch('weaviate.Client')
    @patch('weaviate.AuthApiKey')
    def test_create_weaviate_client(self, MockAuth, MockClient):
        # Test when url and api_key are provided
        auth_instance = MockAuth.return_value
        MockClient.return_value = 'client'
        self.assertEqual(create_weaviate_client('url', 'api_key'), 'client')
        MockAuth.assert_called_once_with(api_key='api_key')
        MockClient.assert_called_once_with(url='url', auth_client_secret=auth_instance)

        with self.assertRaises(ValueError):
            create_weaviate_client()  # Raises an error if no url is provided

class TestWeaviate(unittest.TestCase):

    def setUp(self):
        # create a new mock object for the client.batch attribute with the required methods for a context manager.
        mock_batch = MagicMock()
        mock_batch.__enter__.return_value = mock_batch
        mock_batch.__exit__.return_value = None

        self.client = Mock()
        self.client.batch = mock_batch

        self.embedding_model = Mock()
        self.weaviateVectorStore = Weaviate(self.client, self.embedding_model, 'class_name', 'text_field')

    def test_get_matching_text(self):
        self.client.query.get.return_value.with_near_vector.return_value.with_where.return_value.with_limit.return_value.do.return_value = {'data': {'Get': {'class_name': []}}}
        self.embedding_model.get_embedding.return_value = 'vector'
        self.weaviateVectorStore._get_metadata_fields = Mock(return_value=['field1', 'field2'])
        self.weaviateVectorStore._get_search_res = Mock(return_value='search_res')
        self.weaviateVectorStore._build_documents = Mock(return_value=['document1', 'document2'])
        self.assertEqual(self.weaviateVectorStore.get_matching_text('query', metadata={'field1': 'value'})
                         , {'search_res': 'search_res', 'documents': ['document1', 'document2']})
        self.embedding_model.get_embedding.assert_called_once_with('query')

    def test_add_texts(self):
        self.embedding_model.get_embedding.return_value = 'vector'
        self.weaviateVectorStore.add_embeddings_to_vector_db = Mock()
        texts = ['text1', 'text2']
        result = self.weaviateVectorStore.add_texts(texts)
        self.assertEqual(len(result), 2)    # We expect to get 2 IDs.
        self.assertTrue(isinstance(result[0], str))    # The IDs should be strings.
        self.embedding_model.get_embedding.assert_has_calls([call(texts[0]), call(texts[1])])
        self.assertEqual(self.weaviateVectorStore.add_embeddings_to_vector_db.call_count, 2)

    def test_add_embeddings_to_vector_db(self):
        embeddings = {'ids': ['id1', 'id2'], 'data_object': [{'field': 'value1'}, {'field': 'value2'}], 'vectors': ['v1', 'v2']}
        self.weaviateVectorStore.add_embeddings_to_vector_db(embeddings)
        calls = [call.add_data_object({'field': 'value1'}, class_name='class_name', uuid='id1', vector='v1'),
                call.add_data_object({'field': 'value2'}, class_name='class_name', uuid='id2', vector='v2')]

        self.client.batch.assert_has_calls(calls)

    def test_delete_embeddings_from_vector_db(self):
        # You need to setup appropriate return values from the Weaviate client
        self.weaviateVectorStore.delete_embeddings_from_vector_db(['id1', 'id2'])
        self.client.data_object.delete.assert_called()

if __name__ == '__main__':
    unittest.main()