import unittest
from unittest.mock import MagicMock, patch
from superagi.models.knowledges import Knowledges

class TestKnowledges(unittest.TestCase):

    def setUp(self):
        # Mock a session object
        self.session = MagicMock()

    def test_repr(self):
        test_knowledge = Knowledges(id=1, name='name', description='description', vector_db_index_id=1, organisation_id=1, contributed_by='contri')
        self.assertEqual(test_knowledge.__repr__(), "Knowledge(id=1, name='name', description='description', vector_db_index_id=1), organisation_id=1, contributed_by=contri)")

    @patch('requests.get')
    def test_fetch_marketplace_list(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response
        self.assertEqual(Knowledges.fetch_marketplace_list(1), {"key": "value"})

    def test_get_knowledge_install_details(self):
        self.session.query.return_value.filter.return_value.all.return_value = [Knowledges(name='knowledge1')]
        result = Knowledges.get_knowledge_install_details(self.session, [{"name": "knowledge1"}], MagicMock(id=1))
        self.assertEqual(result, [{'name': 'knowledge1', 'is_installed': True}])

    def test_get_organisation_knowledges(self):
        self.session.query.return_value.filter.return_value.all.return_value = [Knowledges(id=1, name="knowledge1", contributed_by="contributor")]
        result = Knowledges.get_organisation_knowledges(self.session, MagicMock(id=1))
        self.assertEqual(result, [{"id": 1, "name": "knowledge1", "contributed_by": "contributor"}])

    @patch('requests.get')
    def test_fetch_knowledge_details_marketplace(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response
        self.assertEqual(Knowledges.fetch_knowledge_details_marketplace('name'), {"key": "value"})

    def test_get_knowledge_from_id(self):
        self.session.query.return_value.filter.return_value.first.return_value = Knowledges(id=1)
        result = Knowledges.get_knowledge_from_id(self.session, 1)
        self.assertEqual(result.id, 1)

    def test_add_update_knowledges(self):
        self.session.query.return_value.filter.return_value.first.return_value = Knowledges(id=1, name="knowledge1", description="description", vector_db_index_id=1, organisation_id=1, contributed_by='contributor')
        result = Knowledges.add_update_knowledges(self.session, {"id": 1, "name": "knowledge2", "description": "new description", "index_id": 2, "organisation_id": 2, "contributed_by": "new contributor"})
        self.assertEqual(result.name, "knowledge2")
        self.assertEqual(result.description, "new description")
        self.session.commit.assert_called_once()

    def test_delete_knowledge(self):
        self.session.query.return_value.filter.return_value.delete.return_value = None
        Knowledges.delete_knowledge(self.session, 1)
        self.session.commit.assert_called_once()

    def test_delete_knowledge_from_vector_index(self):
        self.session.query.return_value.filter.return_value.delete.return_value = None
        Knowledges.delete_knowledge_from_vector_index(self.session, 1)
        self.session.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()