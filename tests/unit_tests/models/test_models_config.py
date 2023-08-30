from unittest.mock import MagicMock, patch

import pytest

from superagi.models.models_config import ModelsConfig

@pytest.fixture
def mock_session():
    return MagicMock()

def test_create_models_config(mock_session):
    # Arrange
    provider = "example_provider"
    api_key = "example_api_key"
    org_id = 1
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    # Act
    model_config = ModelsConfig(provider=provider, api_key=api_key, org_id=org_id)
    mock_session.add(model_config)

    # Assert
    mock_session.add.assert_called_once_with(model_config)

def test_repr_method_models_config(mock_session):
    # Arrange
    provider = "example_provider"
    api_key = "example_api_key"
    org_id = 1
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    # Act
    model_config = ModelsConfig(provider=provider, api_key=api_key, org_id=org_id)
    model_config_repr = repr(model_config)

    # Assert
    assert model_config_repr == f"ModelsConfig(id=None, provider={provider}, " \
                                f"org_id={org_id})"

# @patch('superagi.helper.encyption_helper.decrypt_data', return_value='decrypted_api_key')
# @patch('superagi.helper.encyption_helper.encrypt_data', return_value='encrypted_api_key')
# def test_store_api_key(mock_encrypt_data, mock_decrypt_data, mock_session):
#     # Arrange
#     organisation_id = 1
#     model_provider = "example_provider"
#     model_api_key = "example_api_key"
#
#     # Mock existing entry
#     mock_existing_entry = MagicMock()
#     mock_session.query.return_value.filter.return_value.first.return_value = mock_existing_entry
#     # Call the method
#     response = ModelsConfig.store_api_key(mock_session, organisation_id, model_provider, model_api_key)
#
#     # Assert
#     mock_existing_entry.api_key = 'encrypted_api_key'
#     mock_session.add.assert_called_once_with(mock_existing_entry)
#     mock_session.commit.assert_called_once()
#     assert response == {'message': 'The API key was successfully stored'}
#
#     # Mock new entry
#     mock_session.query.return_value.filter.return_value.first.return_value = None
#     # Call the method
#     response = ModelsConfig.store_api_key(mock_session, organisation_id, model_provider, model_api_key)
#
#     # Assert
#     # The new_entry is local to the store_api_key method, we cannot directly assert its properties.
#     # But we can check if a new entry is added.
#     mock_session.add.assert_called()
#     mock_session.commit.assert_called()
#     assert response == {'message': 'The API key was successfully stored'}

# @patch('superagi.helper.encyption_helper.decrypt_data', return_value='decrypted_api_key')
# def test_fetch_api_keys(mock_decrypt_data, mock_session):
#     # Arrange
#     organisation_id = 1
#     # Mock api_key_info
#     mock_session.query.return_value.filter.return_value.all.return_value = [("example_provider", "encrypted_api_key")]
#
#     # Call the method
#     api_keys = ModelsConfig.fetch_api_keys(mock_session, organisation_id)
#
#     # Assert
#     assert api_keys == [{"provider": "example_provider", "api_key": "decrypted_api_key"}]
#
# @patch('superagi.helper.encyption_helper.decrypt_data', return_value='decrypted_api_key')
# def test_fetch_api_key(mock_session):
#     # Arrange
#     organisation_id = 1
#     model_provider = "example_provider"
#     # Mock api_key_data
#     mock_api_key_data = MagicMock()
#     mock_api_key_data.id = 1
#     mock_api_key_data.provider = "provider"
#     mock_api_key_data.api_key = "encrypted_api_key"
#     mock_session.query.return_value.filter.return_value.first.return_value = mock_api_key_data
#
#     # Call the method
#     api_key = ModelsConfig.fetch_api_key(mock_session, organisation_id, model_provider)
#
#     # Assert
#     assert api_key == [{'id': 1, 'provider': "provider", 'api_key': "encrypted_api_key"}]

def test_fetch_model_by_id(mock_session):
    # Arrange
    organisation_id = 1
    model_provider_id = 1
    # Mock model
    mock_model = MagicMock()
    mock_model.provider = 'some_provider'
    mock_session.query.return_value.filter.return_value.first.return_value = mock_model

    # Call the method
    model = ModelsConfig.fetch_model_by_id(mock_session, organisation_id, model_provider_id)
    assert model == {"provider": "some_provider"}

def test_fetch_model_by_id_marketplace(mock_session):
    # Arrange
    model_provider_id = 1
    # Mock model
    mock_model = MagicMock()
    mock_model.provider = 'some_provider'
    mock_session.query.return_value.filter.return_value.first.return_value = mock_model

    # Call the method
    model = ModelsConfig.fetch_model_by_id_marketplace(mock_session, model_provider_id)
    assert model == {"provider": "some_provider"}