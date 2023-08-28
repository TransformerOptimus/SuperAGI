# from unittest.mock import MagicMock, patch
# from superagi.llms.openai import OpenAi
# from superagi.llms.replicate import Replicate
# from superagi.models.models_config import ModelsConfig
# from superagi.models.models import Models
# from superagi.models.db import connect_db
# from sqlalchemy.orm import sessionmaker
# import pytest
#
#
# @pytest.fixture
# def mock_db_session():
#     db_session = MagicMock()
#     db_session.query().filter().first().return_value = Models(model_name="gpt-3.5-turbo", org_id=1, model_provider_id=1)
#     db_session.query().filter().first().return_value = ModelsConfig(provider="OpenAI")
#     return db_session
#
#
# @patch("superagi.models.db.connect_db")
# @patch("sqlalchemy.orm.sessionmaker")
# def test_get_model_openai(mock_sessionmaker, mock_connect_db, mock_db_session):
#     mock_sessionmaker.return_value = MagicMock(return_value=mock_db_session)
#     mock_connect_db.return_value = MagicMock()
#
#     from superagi.llms.openai import OpenAi
#     result = OpenAi.get_model(organisation_id=1, api_key="TEST_KEY")
#
#     assert isinstance(result, OpenAi)
# #
# # @patch('superagi.models.db.connect_db')
# # @patch('superagi.llms.replicate.Replicate')
# # def test_get_model_replicate(mock_replicate, mock_db, mock_session_maker):
# #     mock_session_maker.query().filter().filter().first().return_value.provider = 'Replicate'
# #     from superagi.models.db import get_model
# #     result = get_model(organisation_id=1, api_key="TEST_KEY")
# #     assert isinstance(result, superagi.llms.replicate.Replicate)
# #
# # @patch('superagi.models.db.connect_db')
# # @patch('superagi.llms.google_palm.GooglePalm')
# # def test_get_model_google_palm(mock_google_palm, mock_db, mock_session_maker):
# #     mock_session_maker.query().filter().filter().first().return_value.provider = 'Google Palm'
# #     from superagi.models.db import get_model
# #     result = get_model(organisation_id=1, api_key="TEST_KEY")
# #     assert isinstance(result, superagi.llms.google_palm.GooglePalm)
# #
# # @patch('superagi.models.db.connect_db')
# # @patch('superagi.llms.hugging_face.HuggingFace')
# # def test_get_model_hugging_face(mock_hugging_face, mock_db, mock_session_maker):
# #     mock_session_maker.query().filter().filter().first().return_value.provider = 'Hugging Face'
# #     from superagi.models.db import get_model
# #     result = get_model(organisation_id=1, api_key="TEST_KEY")
# #     assert isinstance(result, superagi.llms.hugging_face.HuggingFace)