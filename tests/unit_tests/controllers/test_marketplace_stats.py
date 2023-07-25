import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app  # This should be the file where your FastAPI app is initiated
from superagi.models.marketplace_stats import MarketPlaceStats

class TestKnowledgeDownload(unittest.TestCase):
    @patch('superagi.controllers.marketplace_stats.db')
    def test_get_knowledge_download_number(self, mock_db):
        mock_result = MagicMock()
        mock_result.value = 10  # We mock that the value returned is 10
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_result
        
        client = TestClient(app)
        response = client.get("/marketplace/knowledge/downloads/123") # 123 is a mock knowledge_id
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 10)

    @patch('superagi.controllers.marketplace_stats.db')
    def test_get_knowledge_download_number_no_downloads(self, mock_db):
        mock_result = MagicMock()
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_result
       
        client = TestClient(app)
        response = client.get("/marketplace/knowledge/downloads/123") # 123 is a mock knowledge_id
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {})

if __name__ == '__main__':
    unittest.main()