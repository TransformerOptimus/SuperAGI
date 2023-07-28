import unittest
from unittest.mock import Mock
from superagi.vector_embeddings.qdrant import Qdrant

class TestQdrant(unittest.TestCase):

    def setUp(self):
        self.embeddings = Qdrant()

    def test_vector_embeddings_empty_json(self):
        result = self.embeddings.get_vector_embeddings_from_chunks({})
        self.assertEqual(result, {})

    def test_vector_embeddings_from_chunks(self):
        chunk_json = {
            "chunk1": {
                "id": "1",
                "embeds": "embeds",
                "text": "text",
                "chunk": "chunk",
                "knowledge_name": "knowledge_name"
            },
            "chunk2": {
                "id": "2",
                "embeds": "embeds2",
                "text": "text2",
                "chunk": "chunk2",
                "knowledge_name": "knowledge_name2"
            }
        }

        result = self.embeddings.get_vector_embeddings_from_chunks(chunk_json)

        expected_output = {
            'ids': ['1', '2'],
            'payload': [
                {'text': 'text', 'chunk': 'chunk', 'knowledge_name': 'knowledge_name'},
                {'text': 'text2', 'chunk': 'chunk2', 'knowledge_name': 'knowledge_name2'}
            ],
            'vectors': ['embeds', 'embeds2']
        }

        self.assertDictEqual(result, expected_output)


if __name__ == '__main__':
    unittest.main()