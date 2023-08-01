import unittest
from unittest.mock import Mock, patch
from superagi.models.vector_dbs import Vectordbs

class TestVectordbs(unittest.TestCase):
    def setUp(self):
        # Create a mock sql session
        self.mock_session = Mock()
        # Create an object of Vectordbs for testing
        self.test_vector_db = Vectordbs(name='test_db', db_type='test_db_type', organisation_id=1)

    @patch('requests.get')
    def test_fetch_marketplace_list(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'name': 'test_db'}]
        mock_get.return_value = mock_response

        # Assert that fetch_marketplace_list() returns the correct value
        self.assertListEqual(Vectordbs.fetch_marketplace_list(), [{'name': 'test_db'}])

    def test_get_vector_db_from_id(self):
        self.mock_session.query.return_value.filter.return_value.first.return_value = self.test_vector_db
        returned_db = Vectordbs.get_vector_db_from_id(self.mock_session, 1)
        # Assert that the returned db is the same as the set up test_vector_db
        self.assertEqual(returned_db, self.test_vector_db)

    def test_get_vector_db_from_organisation(self):
        self.mock_session.query.return_value.filter.return_value.all.return_value = [self.test_vector_db]
        returned_db_list = Vectordbs.get_vector_db_from_organisation(self.mock_session, Mock(id=1))
        # Assert that returned list of dbs contains the test_vector_db
        self.assertIn(self.test_vector_db, returned_db_list)

    def test_add_vector_db(self):
        # Assert that new db name matches the created db
        new_db = Vectordbs.add_vector_db(self.mock_session, 'test_db', 'test_db_type', Mock(id=1))
        self.assertEqual(new_db.name, 'test_db')

    def test_delete_vector_db(self):
        Vectordbs.delete_vector_db(self.mock_session, 1)
        # Assert that the session's delete method was called with the correct arguments
        self.mock_session.query.assert_called_once_with(Vectordbs)
        self.mock_session.query.return_value.filter.return_value.delete.assert_called_once()

if __name__ == "__main__":
    unittest.main()