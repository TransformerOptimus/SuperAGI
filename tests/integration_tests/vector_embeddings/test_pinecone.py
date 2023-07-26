import unittest
from unittest.mock import patch, MagicMock
from typing import Any
from superagi.vector_embeddings.pinecone import Pinecone

# now, the unittests:
class TestPinecone(unittest.TestCase):

    # assuming that there is a setUp method to set initial vars
    def setUp(self):
        self.pinecone = Pinecone()
        self.sample_json = {
            '1': {"id": "1", "embeds": "embeds1", 'text': 'text1', 'chunk': 'chunk1', 'knowledge_name': 'knowledge1'},
            '2': {"id": "2", "embeds": "embeds2", 'text': 'text2', 'chunk': 'chunk2', 'knowledge_name': 'knowledge2'}
        }

    # testing for the non-empty json
    def test_get_vector_embeddings_from_chunks(self):
        result = self.pinecone.get_vector_embeddings_from_chunks(self.sample_json)
        expected_result = {
            'vectors': [(
                "1", 
                "embeds1", 
                {'text': 'text1', 'chunk': 'chunk1', 'knowledge_name': 'knowledge1'}
            ), (
                "2", 
                "embeds2", 
                {'text': 'text2', 'chunk': 'chunk2', 'knowledge_name': 'knowledge2'}
            )]
        }
        self.assertDictEqual(result, expected_result)

    # testing for an empty json
    def test_get_vector_embeddings_from_chunks_empty(self):
        result = self.pinecone.get_vector_embeddings_from_chunks({})
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()