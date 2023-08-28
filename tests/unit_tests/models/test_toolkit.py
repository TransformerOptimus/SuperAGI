from unittest.mock import MagicMock, patch, call,create_autospec,Mock

import pytest

from superagi.models.organisation import Organisation
from superagi.models.toolkit import Toolkit
from superagi.models.tool import Tool
from sqlalchemy.orm import Session

@pytest.fixture
def mock_session():
    return MagicMock()

# Mocked tool
@pytest.fixture
def mock_tool():
    tool = MagicMock(spec=Tool)
    tool.id = 1
    return tool

# Mocked session
@pytest.fixture
def mock_session(mock_tool):
    session = MagicMock()
    query = session.query
    query.return_value.filter.return_value.all.return_value = [mock_tool]
    query.return_value.filter.return_value.first.return_value = mock_tool
    return session

# marketplace_url = "http://localhost:8001"
marketplace_url = "https://app.superagi.com/api"


def test_add_or_update_existing_toolkit(mock_session):
    # Arrange
    name = "example_toolkit"
    description = "Example toolkit description"
    show_toolkit = True
    organisation_id = 1
    tool_code_link = "https://example.com/toolkit"

    existing_toolkit = Toolkit(
        name=name,
        description="Old description",
        show_toolkit=False,
        organisation_id=organisation_id,
        tool_code_link="https://old-link.com"
    )

    mock_session.query.return_value.filter.return_value.first.return_value = existing_toolkit

    # Act
    result = Toolkit.add_or_update(mock_session, name, description, show_toolkit, organisation_id, tool_code_link)

    # Assert
    assert result == existing_toolkit
    assert result.name == name
    assert result.description == description
    assert result.show_toolkit == show_toolkit
    assert result.organisation_id == organisation_id
    assert result.tool_code_link == tool_code_link
    mock_session.add.assert_not_called()  # Make sure add was not called
    mock_session.commit.assert_called_once()
    mock_session.flush.assert_called_once()


def test_add_or_update_new_toolkit(mock_session):
    # Arrange
    name = "example_toolkit"
    description = "Example toolkit description"
    show_toolkit = True
    organisation_id = 1
    tool_code_link = "https://example.com/toolkit"

    mock_session.query.return_value.filter.return_value.first.return_value = None

    # Act
    result = Toolkit.add_or_update(mock_session, name, description, show_toolkit, organisation_id, tool_code_link)

    # Assert
    assert isinstance(result, Toolkit)
    assert result.name == name
    assert result.description == description
    assert result.show_toolkit == show_toolkit
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
        result = Toolkit.fetch_marketplace_list(page)

        # Assert
        assert result == expected_response
        mock_get.assert_called_once_with(
            f"{marketplace_url}/toolkits/marketplace/list/{str(page)}",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

def test_fetch_marketplace_detail_success():
    # Arrange
    search_str = "search string"
    toolkit_name = "tool kit name"
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
        result = Toolkit.fetch_marketplace_detail(search_str, toolkit_name)

        # Assert
        assert result == expected_response
        mock_get.assert_called_once_with(
            f"{marketplace_url}/toolkits/marketplace/{search_str.replace(' ', '%20')}/{toolkit_name.replace(' ', '%20')}",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

def test_fetch_marketplace_detail_error():
    # Arrange
    search_str = "search string"
    toolkit_name = "tool kit name"

    # Mock the requests.get method to simulate an error response
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 500

        # Act
        result = Toolkit.fetch_marketplace_detail(search_str, toolkit_name)

        # Assert
        assert result is None
        mock_get.assert_called_once_with(
            f"{marketplace_url}/toolkits/marketplace/{search_str.replace(' ', '%20')}/{toolkit_name.replace(' ', '%20')}",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )



def test_get_toolkit_from_name_existing_toolkit(mock_session):
    # Arrange
    toolkit_name = "example_toolkit"
    organisation = Organisation(id=1)
    expected_toolkit = Toolkit(name=toolkit_name,organisation_id=organisation.id)

    # Mock the session.query method
    mock_session.query.return_value.filter_by.return_value.first.return_value = expected_toolkit

    # Act
    result = Toolkit.get_toolkit_from_name(mock_session, toolkit_name,organisation)

    # Assert
    assert result == expected_toolkit
    mock_session.query.assert_called_once_with(Toolkit)
    mock_session.query.return_value.filter_by.assert_called_once_with(name=toolkit_name,organisation_id=organisation.id)
    mock_session.query.return_value.filter_by.return_value.first.assert_called_once()

def test_get_toolkit_from_name_nonexistent_toolkit(mock_session):
    # Arrange
    toolkit_name = "nonexistent_toolkit"

    # Mock the session.query method to return None
    mock_session.query.return_value.filter_by.return_value.first.return_value = None
    organisation = Organisation(id=1)

    # Act
    result = Toolkit.get_toolkit_from_name(mock_session, toolkit_name,organisation)

    # Assert
    assert result is None
    mock_session.query.assert_called_once_with(Toolkit)
    mock_session.query.return_value.filter_by.assert_called_once_with(name=toolkit_name,organisation_id=organisation.id)
    mock_session.query.return_value.filter_by.return_value.first.assert_called_once()

def test_get_toolkit_installed_details(mock_session):
    # Arrange
    marketplace_toolkits = [
        {"name": "Toolkit 1"},
        {"name": "Toolkit 2"},
        {"name": "Toolkit 3"}
    ]
    organisation = Organisation(id=1)

    installed_toolkits = [
        Toolkit(name="Toolkit 1"),
        Toolkit(name="Toolkit 3")
    ]
    mock_session.query.return_value.filter.return_value.all.return_value = installed_toolkits

    # Act
    result = Toolkit.get_toolkit_installed_details(mock_session, marketplace_toolkits, organisation)

    # Assert
    assert len(result) == 3
    assert result[0]["name"] == "Toolkit 1"
    assert result[0]["is_installed"] is True
    assert result[1]["name"] == "Toolkit 2"
    assert result[1]["is_installed"] is False
    assert result[2]["name"] == "Toolkit 3"
    assert result[2]["is_installed"] is True
    mock_session.query.assert_called_once()
    mock_session.query.return_value.filter.return_value.all.assert_called_once()

# Test function
def test_fetch_tool_ids_from_toolkit(mock_tool, mock_session):
    # Arranging
    toolkit_ids = [1, 2, 3]
    
    # Act
    result = Toolkit.fetch_tool_ids_from_toolkit(mock_session, toolkit_ids)

    # Assert
    assert result == [mock_tool.id for _ in toolkit_ids]

def test_get_tool_and_toolkit_arr_with_nonexistent_toolkit():
    # Create a mock session
    session = create_autospec(Session)

    # Configure the session query to return None for toolkit
    session.query.return_value.filter.return_value.first.return_value = None

    # Call the method under test with a non-existent toolkit
    agent_config_tools_arr = [
        {"name": "NonExistentToolkit", "tools": ["Tool1", "Tool2"]},
    ]

    # Use a context manager to capture the raised exception and its message
    with pytest.raises(Exception) as exc_info:
        Toolkit.get_tool_and_toolkit_arr(session,1, agent_config_tools_arr)

    # Assert that the expected error message is contained within the raised exception message
    expected_error_message = "One or more of the Tool(s)/Toolkit(s) does not exist."
    assert expected_error_message in str(exc_info.value)
