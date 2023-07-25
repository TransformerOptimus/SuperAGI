import unittest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app  # replace "your_module" with the name of your module, where your FastAPI app is defined

class TestSuperagiAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    # Mock the get_user_organisation function as it abstracts the authentication part
    @patch('superagi.helper.auth.get_user_organisation')  # replace 'your_module' with the name of your module
    def test_get_knowledge_list(self, get_user_organisation):
        get_user_organisation.return_value = MagicMock()
        response = self.client.get("/knowledges/get/list")
        self.assertEqual(response.status_code, 200)

    # # Patch the delete_knowledge method to avoid actual deletion
    @patch('superagi.models.knowledges.Knowledges.delete_knowledge')
    def test_delete_user_knowledge(self, delete_knowledge):
        delete_knowledge.return_value = None
        response = self.client.post("/knowledges/delete/1")
        self.assertEqual(response.status_code, 200)

    # Similar patches can be done for other functions

if __name__ == "__main__":
    unittest.main()