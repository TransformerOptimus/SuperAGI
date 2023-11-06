import unittest
from unittest.mock import Mock, patch
from superagi.models.vector_db_configs import VectordbConfigs

class TestVectordbConfigs(unittest.TestCase):
    def setUp(self):
        self.session_mock = Mock()
        self.vector_db_id_mock = 1
        self.db_creds_mock = {"key1": "value1", "key2": "value2"}

    @patch('superagi.models.vector_db_configs.VectordbConfigs')
    def test_get_vector_db_config_from_db_id(self, model_mock):
        vectordb_mock = Mock()
        vectordb_mock.key = "key1"
        vectordb_mock.value = "value1"
        self.session_mock.query().filter().all.return_value = [vectordb_mock]
        result = VectordbConfigs.get_vector_db_config_from_db_id(self.session_mock, self.vector_db_id_mock)
        self.assertEqual(result, {"key1": "value1"})

    @patch('superagi.models.vector_db_configs.VectordbConfigs')
    def test_add_vector_db_config(self, model_mock):
        VectordbConfigs.add_vector_db_config(self.session_mock, self.vector_db_id_mock, self.db_creds_mock)
        self.assertEqual(self.session_mock.add.call_count, len(self.db_creds_mock))
        self.assertTrue(self.session_mock.commit.called)
  
    @patch('superagi.models.vector_db_configs.VectordbConfigs')
    def test_delete_vector_db_configs(self, model_mock):
        VectordbConfigs.delete_vector_db_configs(self.session_mock, self.vector_db_id_mock)
        self.assertTrue(self.session_mock.query(model_mock).filter(model_mock.vector_db_id == self.vector_db_id_mock).delete.called)
        self.assertTrue(self.session_mock.commit.called)

if __name__ == '__main__':
    unittest.main()