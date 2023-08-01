import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from superagi.models.marketplace_stats import MarketPlaceStats

class TestMarketPlaceStats(unittest.TestCase):

    @patch('requests.get')
    def test_get_knowledge_installation_number(self, mock_get):
        test_json = {'download_count':123}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_json
        mock_get.return_value = mock_response

        result = MarketPlaceStats.get_knowledge_installation_number(1)
        self.assertEqual(result, test_json)

    @patch('requests.get')
    def test_get_knowledge_installation_number_status_not_200(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = MarketPlaceStats.get_knowledge_installation_number(1)
        self.assertEqual(result, [])

    @patch('sqlalchemy.orm.Session')
    def test_update_knowledge_install_number_existing(self, mock_session):
        instance = MagicMock()
        instance.value = '5'
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = instance
        mock_session.query.return_value = mock_query

        MarketPlaceStats.update_knowledge_install_number(mock_session, 1, 10)

        self.assertEqual(instance.value, "10")

        mock_query.filter.assert_called()
        mock_session.commit.assert_called()
        
if __name__ == '__main__':
    unittest.main()
