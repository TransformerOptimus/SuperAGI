# import unittest
# from superagi.llms.llm_model_factory import get_model
# from superagi.llms.google_palm import GooglePalm
# from superagi.llms.openai import OpenAi
# from superagi.llms.replicate import Replicate
# from superagi.llms.hugging_face import HuggingFace
# from unittest.mock import patch, MagicMock, create_autospec
# from sqlalchemy.orm import Session
#
# class TestGetModel(unittest.TestCase):
#     @patch('superagi.llms.llm_model_factory.connect_db')
#     def test_get_model(self, mock_connect_db):
#         mock_session = MagicMock()
#         mock_connect_db().Session().return_value = mock_session
#
#         mock_model_instance = MagicMock()
#         mock_model_instance.model_name = "gpt-3.5-turbo"
#         mock_model_instance.model_provider_id = 1
#         mock_model_instance.version = "1.0.0"
#         mock_model_instance.end_point = "/api/models"
#
#         mock_provider_response = MagicMock()
#         mock_provider_response.provider = 'OpenAI'
#
#         mock_query = MagicMock()
#         mock_query.filter().first.side_effect = [mock_model_instance, mock_provider_response]
#         mock_session.query.return_value = mock_query
#
#         result = get_model("org_123", "api_key_123", model="gpt-3.5-turbo")
#
#         self.assertIsInstance(result, OpenAi)
#         self.assertEqual(result.model, "gpt-3.5-turbo")
#
# if __name__ == "__main__":
#     unittest.main()