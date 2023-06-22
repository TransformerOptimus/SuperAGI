from unittest.mock import MagicMock, patch

import pytest

from superagi.models.tool_kit import ToolKit
# from superagi.models.tool_kit import T
@pytest.fixture
def mock_session():
    return MagicMock()

marketplace_url = "http://localhost:8001"


def test_add_or_update_existing_toolkit(mock_session):
    # Arrange
    name = "example_toolkit"
    description = "Example toolkit description"
    show_tool_kit = True
    organisation_id = 1
    tool_code_link = "https://example.com/toolkit"

    existing_toolkit = ToolKit(
        name=name,
        description="Old description",
        show_tool_kit=False,
        organisation_id=organisation_id,
        tool_code_link="https://old-link.com"
    )

    mock_session.query.return_value.filter.return_value.first.return_value = existing_toolkit

    # Act
    result = ToolKit.add_or_update(mock_session, name, description, show_tool_kit, organisation_id, tool_code_link)

    # Assert
    assert result == existing_toolkit
    assert result.name == name
    assert result.description == description
    assert result.show_tool_kit == show_tool_kit
    assert result.organisation_id == organisation_id
    assert result.tool_code_link == tool_code_link
    mock_session.add.assert_not_called()  # Make sure add was not called
    mock_session.commit.assert_called_once()
    mock_session.flush.assert_called_once()


def test_add_or_update_new_toolkit(mock_session):
    # Arrange
    name = "example_toolkit"
    description = "Example toolkit description"
    show_tool_kit = True
    organisation_id = 1
    tool_code_link = "https://example.com/toolkit"

    mock_session.query.return_value.filter.return_value.first.return_value = None

    # Act
    result = ToolKit.add_or_update(mock_session, name, description, show_tool_kit, organisation_id, tool_code_link)

    # Assert
    assert isinstance(result, ToolKit)
    assert result.name == name
    assert result.description == description
    assert result.show_tool_kit == show_tool_kit
    assert result.organisation_id == organisation_id
    assert result.tool_code_link == tool_code_link
    mock_session.add.assert_called_once_with(result)
    mock_session.commit.assert_called_once()
    mock_session.flush.assert_called_once()



def test_fetch_marketplace_list_success():
    # Arrange
    page = 1
    expected_response = [
        {
            "id": 1,
            "name": "ToolKit 1",
            "description": "Description 1"
        },
        {
            "id": 2,
            "name": "ToolKit 2",
            "description": "Description 2"
        }
    ]

    # Mock the requests.get method
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = expected_response

        # Act
        result = ToolKit.fetch_marketplace_list(page)

        # Assert
        assert result == expected_response
        mock_get.assert_called_once_with(
            f"{marketplace_url}/tool_kits/marketplace/list/{str(page)}",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

def test_fetch_marketplace_detail_success():
    # Arrange
    search_str = "search string"
    tool_kit_name = "tool kit name"
    expected_response = {
        "id": 1,
        "name": "ToolKit 1",
        "description": "Description 1"
    }

    # Mock the requests.get method
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = expected_response

        # Act
        result = ToolKit.fetch_marketplace_detail(search_str, tool_kit_name)

        # Assert
        assert result == expected_response
        mock_get.assert_called_once_with(
            f"{marketplace_url}/tool_kits/marketplace/{search_str.replace(' ', '%20')}/{tool_kit_name.replace(' ', '%20')}",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

def test_fetch_marketplace_detail_error():
    # Arrange
    search_str = "search string"
    tool_kit_name = "tool kit name"

    # Mock the requests.get method to simulate an error response
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 500

        # Act
        result = ToolKit.fetch_marketplace_detail(search_str, tool_kit_name)

        # Assert
        assert result is None
        mock_get.assert_called_once_with(
            f"{marketplace_url}/tool_kits/marketplace/{search_str.replace(' ', '%20')}/{tool_kit_name.replace(' ', '%20')}",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )



def test_get_tool_kit_from_name_existing_tool_kit(mock_session):
    # Arrange
    tool_kit_name = "example_tool_kit"
    expected_tool_kit = ToolKit(name=tool_kit_name)

    # Mock the session.query method
    mock_session.query.return_value.filter_by.return_value.first.return_value = expected_tool_kit

    # Act
    result = ToolKit.get_tool_kit_from_name(mock_session, tool_kit_name)

    # Assert
    assert result == expected_tool_kit
    mock_session.query.assert_called_once_with(ToolKit)
    mock_session.query.return_value.filter_by.assert_called_once_with(name=tool_kit_name)
    mock_session.query.return_value.filter_by.return_value.first.assert_called_once()

def test_get_tool_kit_from_name_nonexistent_tool_kit(mock_session):
    # Arrange
    tool_kit_name = "nonexistent_tool_kit"

    # Mock the session.query method to return None
    mock_session.query.return_value.filter_by.return_value.first.return_value = None

    # Act
    result = ToolKit.get_tool_kit_from_name(mock_session, tool_kit_name)

    # Assert
    assert result is None
    mock_session.query.assert_called_once_with(ToolKit)
    mock_session.query.return_value.filter_by.assert_called_once_with(name=tool_kit_name)
    mock_session.query.return_value.filter_by.return_value.first.assert_called_once()
