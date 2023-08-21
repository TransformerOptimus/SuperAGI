import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import sessionmaker
from superagi.models.models import Models
from superagi.models.models_config import ModelsConfig

class TestGetModel(unittest.TestCase):
    @patch('superagi.models.db.connect_db')
    @patch('sqlalchemy.orm.sessionmaker')
    def test_get_model(self, mock_seshmaker, mock_connect):
        mock_seshmaker.return_value = sessionmaker()
        mock_session = MagicMock()
        mock_connect.return_value = mock_session

        mock_model_instance = MagicMock()
        mock_model_instance.model_name = "gpt-3.5-turbo"
        mock_model_instance.version = "1.0"
        mock_model_instance.end_point = "http://endpoint/test"
        mock_model_instance.model_provider_id = 1
        mock_provider_instance = MagicMock()
        mock_provider_instance.provider = "OpenAI"

        mock_session.query.side_effect = [
            MagicMock(
                first=MagicMock(return_value=mock_model_instance)),
            MagicMock(
                first=MagicMock(return_value=mock_provider_instance))
        ]

        from superagi.llms.llm_model_factory import get_model
        result = get_model(organisation_id="test_org", api_key="test_key")