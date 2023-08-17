from unittest.mock import create_autospec

from sqlalchemy.orm import Session
from superagi.models.api_key import ApiKey

def test_get_by_org_id():
    # Create a mock session
    session = create_autospec(Session)

    # Create a sample organization ID
    org_id = 1

    # Create a mock ApiKey object to be returned by the session query
    mock_api_keys = [
        ApiKey(id=1, org_id=org_id, key="key1", is_expired=False),
        ApiKey(id=2, org_id=org_id, key="key2", is_expired=False),
    ]

    # Configure the session query to return the mock api keys
    session.query.return_value.filter.return_value.all.return_value = mock_api_keys

    # Call the method under test
    api_keys = ApiKey.get_by_org_id(session, org_id)

    # Assert that the returned api keys match the mock api keys
    assert api_keys == mock_api_keys


def test_get_by_id():
    # Create a mock session
    session = create_autospec(Session)

    # Create a sample api key ID
    api_key_id = 1

    # Create a mock ApiKey object to be returned by the session query
    mock_api_key = ApiKey(id=api_key_id, org_id=1, key="key1", is_expired=False)

    # Configure the session query to return the mock api key
    session.query.return_value.filter.return_value.first.return_value = mock_api_key

    # Call the method under test
    api_key = ApiKey.get_by_id(session, api_key_id)

    # Assert that the returned api key matches the mock api key
    assert api_key == mock_api_key

def test_delete_by_id():
    # Create a mock session
    session = create_autospec(Session)

    # Create a sample api key ID
    api_key_id = 1

    # Create a mock ApiKey object to be returned by the session query
    mock_api_key = ApiKey(id=api_key_id, org_id=1, key="key1", is_expired=False)

    # Configure the session query to return the mock api key
    session.query.return_value.filter.return_value.first.return_value = mock_api_key

    # Call the method under test
    ApiKey.delete_by_id(session, api_key_id)

    # Assert that the api key's is_expired attribute is set to True
    assert mock_api_key.is_expired == True

    # Assert that the session.commit and session.flush methods were called
    session.commit.assert_called_once()
    session.flush.assert_called_once()

def test_edit_by_id():
    # Create a mock session
    session = create_autospec(Session)

    # Create a sample api key ID and new name
    api_key_id = 1
    new_name = "New Name"

    # Create a mock ApiKey object to be returned by the session query
    mock_api_key = ApiKey(id=api_key_id, org_id=1, key="key1", is_expired=False)

    # Configure the session query to return the mock api key
    session.query.return_value.filter.return_value.first.return_value = mock_api_key

    # Call the method under test
    ApiKey.update_api_key(session, api_key_id, new_name)

    # Assert that the api key's name attribute is updated
    assert mock_api_key.name == new_name

    # Assert that the session.commit and session.flush methods were called
    session.commit.assert_called_once()
    session.flush.assert_called_once()