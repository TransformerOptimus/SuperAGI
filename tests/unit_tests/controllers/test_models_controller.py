from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@patch('superagi.controllers.models_controller.db')
def test_store_api_keys_success(mock_get_db):
    request = {
        "model_provider": "mock_provider",
        "model_api_key": "mock_key"
    }
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
        patch('superagi.helper.auth.db') as mock_auth_db:

        response = client.post("/models_controller/store_api_keys", json=request)
        assert response.status_code == 200

@patch('superagi.controllers.models_controller.db')
def test_get_api_keys_success(mock_get_db):
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
        patch('superagi.helper.auth.db') as mock_auth_db:
        response = client.get("/models_controller/get_api_keys")
        assert response.status_code == 200

@patch('superagi.controllers.models_controller.db')
@patch('superagi.controllers.models_controller.ModelsConfig.fetch_api_key', return_value = {})
def test_get_api_key_success(mock_fetch_api_key, mock_get_db):
    params = {
        "model_provider": "model"
    }
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
        patch('superagi.helper.auth.db') as mock_auth_db:
        response = client.get("/models_controller/get_api_key", params=params)
        assert response.status_code == 200

@patch('superagi.controllers.models_controller.db')
def test_verify_end_point_success(mock_get_db):
    with patch('superagi.helper.auth.db') as mock_auth_db:
        response = client.get("/models_controller/verify_end_point?model_api_key=mock_key&end_point=mock_point&model_provider=mock_provider")
        assert response.status_code == 200

@patch('superagi.controllers.models_controller.db')
def test_store_model_success(mock_get_db):
    request = {
        "model_name": "mock_model",
        "description": "mock_description",
        "end_point": "mock_end_point",
        "model_provider_id": 1,
        "token_limit": 10,
        "type": "mock_type",
        "version": "mock_version"
    }
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
        patch('superagi.helper.auth.db') as mock_auth_db:
        response = client.post("/models_controller/store_model", json=request)
        assert response.status_code == 200

@patch('superagi.controllers.models_controller.db')
def test_fetch_models_success(mock_get_db):
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
        patch('superagi.helper.auth.db') as mock_auth_db:
        response = client.get("/models_controller/fetch_models")
        assert response.status_code == 200

@patch('superagi.controllers.models_controller.db')
def test_fetch_model_details_success(mock_get_db):
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
        patch('superagi.helper.auth.db') as mock_auth_db:
        response = client.get("/models_controller/fetch_model/1")
        assert response.status_code == 200

@patch('superagi.controllers.models_controller.db')
def test_fetch_data_success(mock_get_db):
    request = {
        "model": "model"
    }
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
        patch('superagi.helper.auth.db') as mock_auth_db:
        response = client.post("/models_controller/fetch_model_data", json=request)
        assert response.status_code == 200

@patch('superagi.controllers.models_controller.db')
def test_get_marketplace_models_list_success(mock_get_db):
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
        patch('superagi.helper.auth.db') as mock_auth_db, \
        patch('superagi.controllers.models_controller.requests.get') as mock_get:

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = client.get("/models_controller/marketplace/list/0")
        assert response.status_code == 200

@patch('superagi.controllers.models_controller.db')
def test_get_marketplace_models_list_success(mock_get_db):
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
        patch('superagi.helper.auth.db') as mock_auth_db:
        response = client.get("/models_controller/marketplace/list/0")
        assert response.status_code == 200
