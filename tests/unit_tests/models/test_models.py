from unittest.mock import MagicMock, patch

import pytest

from superagi.models.models import Models

@pytest.fixture
def mock_session():
    return MagicMock()

def test_create_model(mock_session):
    # Arrange
    model_name = "example_model"
    end_point = "example_end_point"
    model_provider_id = 1
    token_limit = 500
    model_type = "example_type"
    version = "v1.0"
    org_id = 1
    model_features = "example_model_feature"
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    # Act
    model = Models(model_name=model_name, end_point=end_point,
                   model_provider_id=model_provider_id, token_limit=token_limit,
                   type=model_type, version=version, org_id=org_id, model_features=model_features)
    mock_session.add(model)

    # Assert
    mock_session.add.assert_called_once_with(model)


def test_repr_method_models(mock_session):
    # Arrange
    model_name = "example_model"
    end_point = "example_end_point"
    model_provider_id = 1
    token_limit = 500
    model_type = "example_type"
    version = "v1.0"
    org_id = 1
    model_features = "example_model_feature"
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    # Act
    model = Models(model_name=model_name, end_point=end_point,
                 model_provider_id=model_provider_id, token_limit=token_limit,
                 type=model_type, version=version, org_id=org_id, model_features=model_features)
    model_repr = repr(model)

    # Assert
    assert model_repr == f"Models(id=None, model_name={model_name}, " \
                         f"end_point={end_point}, model_provider_id={model_provider_id}, " \
                         f"token_limit={token_limit}, " \
                         f"type={model_type}, " \
                         f"version={version}, " \
                         f"org_id={org_id}, " \
                         f"model_features={model_features})"


@patch('requests.get')
def test_fetch_marketplace_list(mock_get):
    # Specify the return value of the get method
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = ['model1', 'model2']
    mock_get.return_value = mock_response

    # Call the method
    result = Models.fetch_marketplace_list(1)

    # Verify the result
    assert result == ['model1', 'model2']

# @patch('superagi.models.models_config.ModelsConfig')
# @patch('logging.error')
# def test_get_model_install_details(mock_logging_error, mock_models_config, mock_session):
#     mock_model = MagicMock()
#     mock_model.model_name = 'model1'
#     mock_model.model_provider_id = 1
#
#     mock_marketplace_models = [{'model_name': 'model1', 'model_provider_id': 1}, {'model_name': 'model2', 'model_provider_id': 2}]
#     mock_session.query.return_value.filter.return_value.all.return_value = [mock_model]
#     mock_session.query.return_value.group_by.return_value.all.return_value = [('model1', 1)]
#     mock_config = MagicMock()
#     mock_config.provider = 'provider1'
#
#     def determine_provider(*args):
#         for arg in args:
#             # Check if mock_config can be returned
#             if isinstance(arg, int) and arg == 1:
#                 return mock_config
#         # Return None for all other situations
#         return None
#
#     mock_session.query.return_value.filter.return_value.first.side_effect = determine_provider
#
#     # Call the method
#     result = Models.get_model_install_details(mock_session, mock_marketplace_models, MagicMock())
#
#     # Verify the result
#     expected_result = [
#         {"model_name": "model1", "is_installed": True, "installs": 1, "provider": "provider1", "model_provider_id": 1},
#         {"model_name": "model2", "is_installed": False, "installs": 0, "provider": None, "model_provider_id": 2}
#     ]
#     assert result == expected_result
#     # Assert that logging.error has been called once when provider is None
#     mock_logging_error.assert_called_once()

def test_fetch_model_tokens(mock_session):
    # Specify the return value of the query
    mock_session.query.return_value.filter.return_value.all.return_value = [('model1', 500)]

    # Call the method
    result = Models.fetch_model_tokens(mock_session, 1)

    # Verify the result
    assert result == {'model1': 500}

def test_store_model_details_when_model_exists(mock_session):
    # Arrange
    mock_session.query.return_value.filter.return_value.first.return_value = MagicMock()
    mock_session.add = MagicMock()

    # Act
    response = Models.store_model_details(
        mock_session,
        organisation_id=1,
        model_name="example_model",
        description="description",
        end_point="end_point",
        model_provider_id=1,
        token_limit=500,
        type="type",
        version="v1.0",
        context_length=4096
    )

    # Assert
    assert response == {"error": "Model Name already exists"}

def test_store_model_details_when_model_not_exists(mock_session, monkeypatch):
    # Arrange
    mock_session.query.return_value.filter.return_value.first.return_value = None
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()
    mock_query = MagicMock()
    mock_fetch_model_by_id = MagicMock()

    # Patching the fetch_model_by_id method in the class
    monkeypatch.setattr('superagi.models.models_config.ModelsConfig.fetch_model_by_id', mock_fetch_model_by_id)
    mock_fetch_model_by_id.return_value = {"provider": "some_provider"}

    # Act
    response = Models.store_model_details(
        mock_session,
        organisation_id=1,
        model_name="example_model",
        description="description",
        end_point="end_point",
        model_provider_id=1,
        token_limit=500,
        type="type",
        version="v1.0",
        context_length=4096
    )

    # Assert
    assert response == {"success": "Model Details stored successfully", "model_id": None}
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

def test_store_model_details_when_unexpected_error_occurs(mock_session, monkeypatch):
    # Arrange
    mock_session.query.return_value.filter.return_value.first.return_value = None
    mock_session.add = MagicMock(side_effect=Exception("Unknown error"))
    mock_fetch_model_by_id = MagicMock()
    monkeypatch.setattr('superagi.models.models_config.ModelsConfig.fetch_model_by_id', mock_fetch_model_by_id)
    mock_fetch_model_by_id.return_value = {"provider": "some_provider"}

    # Act
    response = Models.store_model_details(
        mock_session,
        organisation_id=1,
        model_name="example_model",
        description="description",
        end_point="end_point",
        model_provider_id=1,
        token_limit=500,
        type="type",
        version="v1.0",
        context_length=4096
    )

    # Assert
    assert response == {"error": "Unexpected Error Occured"}

@patch('superagi.models.models_config.ModelsConfig')
def test_fetch_models(mock_models_config, mock_session):
    # Specify the return value of the query
    mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = [
        (1, "example_model", "description", "example_provider")
    ]

    # Call the method
    result = Models.fetch_models(mock_session, 1)

    # Verify the result
    assert result == [{
        "id": 1,
        "name": "example_model",
        "description": "description",
        "model_provider": "example_provider"
    }]

@patch('superagi.models.models_config.ModelsConfig')
def test_fetch_model_details(mock_models_config, mock_session):
    # Specify the return values for the query
    mock_session.query.return_value.join.return_value.filter.return_value.first.return_value = (
        1, "example_model", "description", "end_point", 100, "type1", "example_provider"
    )

    # Call the method
    result = Models.fetch_model_details(mock_session, 1, 1)

    # Verify the result
    assert result == {
        "id": 1,
        "name": "example_model",
        "description": "description",
        "end_point": "end_point",
        "token_limit": 100,
        "type": "type1",
        "model_provider": "example_provider"
    }