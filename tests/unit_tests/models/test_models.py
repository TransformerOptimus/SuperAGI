from unittest.mock import MagicMock, patch

import pytest

from superagi.models.models import Models

@pytest.fixture
def mock_session():
    return MagicMock()

def test_store_model_details(mock_session):
    # Arrange
    organisation_id = 1
    model_name = "example_model"
    description = "example_description"
    end_point = "example_end_point"
    model_provider_id = 1
    token_limit = 100
    type = "example_type"
    version = "example_version"
    mock_session.query.return_value.filter.return_value.first.return_value = None

    # Act
    result = Models.store_model_details(mock_session, organisation_id, model_name, description, end_point, model_provider_id, token_limit, type, version)

    # Assert
    assert result == {"success": "Model Details stored successfully"}

def test_repr_method_models(mock_session):
    # Arrange
    model_name = "example_model"
    end_point = "example_end_point"
    model_provider_id = 1
    token_limit = 100
    type = "example_type"
    version = "example_version"
    org_id = 1

    # Act
    model = Models(model_name=model_name, end_point=end_point, model_provider_id=model_provider_id, token_limit=token_limit, type=type, version=version, org_id=org_id)
    model_repr = repr(model)

    # Assert
    assert model_repr == f"Models(id=None, model_name={model_name}, " \
                         f"end_point={end_point}, model_provider_id={model_provider_id}, " \
                         f"token_limit={token_limit}, " \
                         f"type={type}, " \
                         f"type={version}, " \
                         f"org_id={org_id})"