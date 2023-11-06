import unittest

from superagi.vector_embeddings.qdrant import Qdrant

class TestQdrant(unittest.TestCase):

    def setUp(self):
        self.uuid = ['1234', '5678']
        self.embeds = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        self.metadata = [{'key1': 'value1'}, {'key2': 'value2'}]

        self.qdrant_obj = Qdrant(self.uuid, self.embeds, self.metadata)

    def test_init(self):
        self.assertEqual(self.qdrant_obj.uuid, self.uuid)
        self.assertEqual(self.qdrant_obj.embeds, self.embeds)
        self.assertEqual(self.qdrant_obj.metadata, self.metadata)

    def test_get_vector_embeddings_from_chunks(self):
        expected = {
            'ids': self.uuid,
            'payload': self.metadata,
            'vectors': self.embeds,
        }
        result = self.qdrant_obj.get_vector_embeddings_from_chunks()
        
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()