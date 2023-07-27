import unittest
from unittest.mock import Mock, MagicMock, call
from superagi.models.vector_db_indices import VectordbIndices

class TestVectordbIndices(unittest.TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.query_mock = self.mock_session.query.return_value
        self.filter_mock = self.query_mock.filter.return_value

    def test_get_vector_index_from_id(self):
        VectordbIndices.get_vector_index_from_id(self.mock_session, 1)
        self.mock_session.query.assert_called_with(VectordbIndices)
        self.filter_mock.first.assert_called_once()

    def test_get_vector_indices_from_vectordb(self):
        VectordbIndices.get_vector_indices_from_vectordb(self.mock_session, 1)
        self.mock_session.query.assert_called_with(VectordbIndices)
        self.filter_mock.all.assert_called_once()

    def test_delete_vector_db_index(self):
        VectordbIndices.delete_vector_db_index(self.mock_session, 1)
        self.mock_session.query.assert_called_with(VectordbIndices)
        self.filter_mock.delete.assert_called_once()
        self.mock_session.commit.assert_called_once()

    def test_add_vector_index(self):
        VectordbIndices.add_vector_index(self.mock_session, 'test', 1, 100, 'active')
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()

    def test_update_vector_index_state(self):
        VectordbIndices.update_vector_index_state(self.mock_session, 1, 'inactive')
        self.mock_session.query.assert_called_with(VectordbIndices)
        self.filter_mock.first.assert_called_once()
        self.mock_session.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()