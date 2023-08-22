import unittest
from unittest import mock

class TestGetModel(unittest.TestCase):
    @mock.patch('superagi.models.db.connect_db')
    @mock.patch('sqlalchemy.orm.sessionmaker')
    @mock.patch.object(OpenAi, '__init__', return_value=None)  # Mock OpenAI class initialization
    def test_get_model(self, mock_openai_init, mock_sessionmaker, mock_connect_db):
        # Create session instance mock
        mock_session_instance = mock.MagicMock()
        # Connect the session instance to the engine
        mock_connect_db.return_value = mock_session_instance
        # Session maker returns a function
        mock_sessionmaker.return_value = mock.MagicMock(return_value=mock_session_instance)

        # Mock model and provider instances
        mock_model_instance = mock.MagicMock()
        mock_model_instance.model_name = "gpt-3.5-turbo"
        mock_model_instance.model_provider_id = 1

        mock_provider_instance = mock.MagicMock()
        mock_provider_instance.provider = "OpenAI"

        # Side effect of first call to session.query().first() will return model,
        # second call will return provider
        mock_session_instance.query().first.side_effect = [mock_model_instance, mock_provider_instance]

        from superagi.llms.llm_model_factory import get_model
        result = get_model(organisation_id="test_org", api_key="test_key")

        # Verify that the OpenAI class was instantiated with the correct arguments
        mock_openai_init.assert_called_once_with(model=mock_model_instance.model_name, api_key="test_key")