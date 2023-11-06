import unittest
from superagi.vector_embeddings.base import VectorEmbeddings
from superagi.vector_embeddings.weaviate import Weaviate

class TestWeaviate(unittest.TestCase):

    def setUp(self):
        self.weaviate = Weaviate(uuid="1234", embeds=[0.1, 0.2, 0.3, 0.4], metadata={"info": "sample data"})

    def test_init(self):
        self.assertEqual(self.weaviate.uuid, "1234")
        self.assertEqual(self.weaviate.embeds, [0.1, 0.2, 0.3, 0.4])
        self.assertEqual(self.weaviate.metadata, {"info": "sample data"})

    def test_get_vector_embeddings_from_chunks(self):
        expected_result = {
            "ids": "1234",
            "data_object": {"info": "sample data"},
            "vectors": [0.1, 0.2, 0.3, 0.4]
        }
        self.assertEqual(self.weaviate.get_vector_embeddings_from_chunks(), expected_result)


if __name__ == '__main__':
    unittest.main()
