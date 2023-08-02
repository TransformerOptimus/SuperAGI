from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from superagi.controllers.tool_config import update_tool_config
from superagi.models.organisation import Organisation
from superagi.models.tool_config import ToolConfig
from superagi.models.toolkit import Toolkit

client = TestClient(app)


@pytest.fixture
def mocks():
    # Mock tool kit data for testing
    user_organisation = Organisation(id=1)
    toolkit_1 = Toolkit(
        id=1,
        name="toolkit_1",
        description="None",
        show_toolkit=None,
        organisation_id=1
    )
    toolkit_2 = Toolkit(
        id=1,
        name="toolkit_2",
        description="None",
        show_toolkit=None,
        organisation_id=1
    )
    user_toolkits = [toolkit_1, toolkit_2]
    tool_config = ToolConfig(
        id=1,
        key="test_key",
        value="test_value",
        toolkit_id=1
    )
    return user_organisation, user_toolkits, tool_config, toolkit_1, toolkit_2


# Test cases
def test_update_tool_configs_success():
    # Test data
    toolkit_name = "toolkit_1"
    configs = [
        {"key": "config_1", "value": "value_1"},
        {"key": "config_2", "value": "value_2"},
    ]

    with patch('superagi.models.toolkit.Toolkit.get_toolkit_from_name') as get_toolkit_from_name, \
            patch('superagi.controllers.tool_config.db') as mock_db:
        mock_db.query.return_value.filter_by.return_value.first.side_effect = [
            # First call to query
            MagicMock(
                toolkit_id=1, key="config_1", value="old_value_1"
            ),
            # Second call to query
            MagicMock(
                toolkit_id=1, key="config_2", value="old_value_2"
            ),
        ]

        result = update_tool_config(toolkit_name, configs)

        assert result == {"message": "Tool configs updated successfully"}


def test_get_all_tool_configs_success(mocks):
    user_organisation, user_toolkits, tool_config, toolkit_1, toolkit_2 = mocks

    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
            patch('superagi.controllers.tool_config.db') as mock_db, \
            patch('superagi.helper.auth.db') as mock_auth_db:
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = toolkit_1
        mock_db.session.query.return_value.filter.return_value.all.side_effect = [
            [tool_config]
        ]
        response = client.get(f"/tool_configs/get/toolkit/test_toolkit_1")

        # Assertions
        assert response.status_code == 200
        assert response.json() == [
            {
                'id': 1,
                'key': tool_config.key,
                'value': tool_config.value,
                'toolkit_id': tool_config.toolkit_id
            }
        ]


def test_get_all_tool_configs_toolkit_not_found(mocks):
    user_organisation, _, _, _, _ = mocks

    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
            patch('superagi.controllers.tool_config.db') as mock_db, \
            patch('superagi.helper.auth.db') as mock_auth_db:
        mock_db.session.query.return_value.filter.return_value.first.return_value = None
        response = client.get(f"/tool_configs/get/toolkit/nonexistent_toolkit")

        # Assertions
        assert response.status_code == 404
        assert response.json() == {'detail': 'ToolKit not found'}

def test_get_tool_config_success(mocks):
    # Unpack the fixture data
    user_organisation, user_toolkits, tool_config, toolkit_1, toolkit_2 = mocks

    # Mock the database session and query functions
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
            patch('superagi.controllers.tool_config.db') as mock_db, \
            patch('superagi.helper.auth.db') as mock_auth_db:
        mock_db.session.query.return_value.filter.return_value.all.return_value = user_toolkits
        mock_db.session.query.return_value.filter_by.return_value = toolkit_1
        mock_db.session.query.return_value.filter.return_value.first.return_value = tool_config

        # Call the function
        response = client.get(f"/tool_configs/get/toolkit/{toolkit_1.name}/key/{tool_config.key}")

        # Assertions
        assert response.status_code == 200
        assert response.json() == {
            "id": tool_config.id,
            "key": tool_config.key,
            "value": tool_config.value,
            "toolkit_id": tool_config.toolkit_id
        }


def test_get_tool_config_unauthorized(mocks):
    # Unpack the fixture data
    user_organisation, user_toolkits, tool_config, toolkit_1, toolkit_2 = mocks

    # Mock the database session and query functions
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
            patch('superagi.controllers.tool_config.db') as mock_db, \
            patch('superagi.helper.auth.db') as mock_auth_db:
        # Mock the toolkit filtering
        mock_db.session.query.return_value.filter.return_value.all.return_value = user_toolkits

        response = client.get(f"/tool_configs/get/toolkit/{toolkit_2.name}/key/{tool_config.key}")

        # Assertions
        assert response.status_code == 403
        assert response.json() == {"detail": "Unauthorized"}


def test_get_tool_config_not_found(mocks):
    # Unpack the fixture data
    user_organisation, user_toolkits, tool_config, toolkit_1, toolkit_2 = mocks

    # Mock the database session and query functions
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
            patch('superagi.controllers.tool_config.db') as mock_db, \
            patch('superagi.helper.auth.db') as mock_auth_db:
        # Mock the toolkit filtering
        mock_db.session.query.return_value.filter.return_value.all.return_value = user_toolkits
        mock_db.session.query.return_value.filter_by.return_value = toolkit_1
        mock_db.session.query.return_value.filter.return_value.first.return_value = None

        # Call the function with a non-existent toolkit
        response = client.get(f"/tool_configs/get/toolkit/{toolkit_1.name}/key/{tool_config.key}")

        # Assertions
        assert response.status_code == 404
        assert response.json() == {"detail": "Tool configuration not found"}
