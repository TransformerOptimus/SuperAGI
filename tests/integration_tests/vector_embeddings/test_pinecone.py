import unittest
from superagi.vector_embeddings.pinecone import Pinecone  


class TestPinecone(unittest.TestCase):

    def setUp(self):
        self.uuid = ["id1", "id2"]
        self.embeds = ["embed1", "embed2"]
        self.metadata = ["metadata1", "metadata2"]
        self.pinecone_instance = Pinecone(self.uuid, self.embeds, self.metadata)

    def test_init(self):
        self.assertEqual(self.pinecone_instance.uuid, self.uuid)
        self.assertEqual(self.pinecone_instance.embeds, self.embeds)
        self.assertEqual(self.pinecone_instance.metadata, self.metadata)
    
    def test_get_vector_embeddings_from_chunks(self):
        expected = {
            'vectors': list(zip(self.uuid, self.embeds, self.metadata))
        }
        result = self.pinecone_instance.get_vector_embeddings_from_chunks()
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()