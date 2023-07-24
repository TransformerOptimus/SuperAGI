import pytest
from unittest.mock import Mock, patch
from superagi.vector_store.document import Document
from superagi.vector_store.pinecone import Pinecone

class TestPinecone:
    @patch('superagi.vector_store.pinecone.pinecone')
    def setup_method(self, mock_pinecone):
        self.mock_index = Mock()
        mock_pinecone.index.Index.return_value = self.mock_index

        self.mock_embedding_model = Mock()
        self.text_field = 'text_field'
        self.namespace = 'namespace'

        self.pinecone = Pinecone(self.mock_index, self.mock_embedding_model, self.text_field, self.namespace)

    def test_init_checks_for_pinecone_installation(self):
        with pytest.raises(ValueError, match="Please install pinecone to use this vector store."):
            Pinecone(None)
        
    def test_init_checks_for_valid_index(self):
        with pytest.raises(ValueError, match="Please provide a valid pinecone index."):
            Pinecone("not_a_valid_index")

    def test_vector_store_server_as_expected(self):
        index_info = self.pinecone.index.describe_index_stats()
        assert self.pinecone.get_index_stats() == {"dimensions": index_info.dimension, "vector_count": index_info.total_vector_count}

    def test_add_texts_returns_expected_ids(self):
        texts = ['text1', 'text2', 'text3']
        ids = ['id1', 'id2', 'id3']
        embeddings = [(id, self.mock_embedding_model.get_embedding(text), {self.text_field: text}) for text, id in zip(texts, ids)]

        with patch.object(self.pinecone, 'add_embeddings_to_vector_db') as mock_add_embeddings:
            assert self.pinecone.add_texts(texts, ids=ids) == ids
            mock_add_embeddings.assert_called_once_with({"vectors": embeddings})

    def test_delete_embeddings(self):
        ids = ['id1', 'id2', 'id3']

        with patch.object(self.pinecone.index, 'delete') as mock_delete:
            self.pinecone.delete_embeddings_from_vector_db(ids)
            mock_delete.assert_called_once_with(ids=ids)