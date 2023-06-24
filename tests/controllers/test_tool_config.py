import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from superagi.models.organisation import Organisation
from superagi.models.tool_config import ToolConfig
from superagi.models.toolkit import Toolkit

# Add the project directory to the Python module path
project_directory = Path('/home/abhijeet/AMAN/code/NewSuperAgi1/SuperAGI')
sys.path.insert(0, str(project_directory))

from unittest.mock import MagicMock, patch
from superagi.controllers.tool_config import update_tool_config
from main import app

client = TestClient(app)


class MockFastAPISQLAlchemy:
    query = MagicMock()

    def __init__(self):
        self.session = self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def commit(self):
        pass


class MockToolKit:
    id = 1

    @staticmethod
    def get_toolkit_from_name(session, toolkit_name):
        return MockToolKit()


# Patch db object of the tool_config module
def mock_tool_config_db(target):
    return patch(target, MockFastAPISQLAlchemy())


def mock_db_query(*args, **kwargs):
    magic_query = MagicMock()
    magic_query.filter.return_value = magic_query
    magic_query.filter_by.return_value = magic_query
    magic_query.first.return_value = magic_query
    magic_query.all.return_value = magic_query

    return magic_query


@pytest.fixture
def mock_toolkits():
    # Mock tool kit data for testing
    user_organisation = Organisation(id=1)
    toolkit_1 = Toolkit(
        id=1,
        name="tool_kit_1",
        description="None",
        show_toolkit=None,
        organisation_id=1
    )
    toolkit_2 = Toolkit(
        id=1,
        name="tool_kit_2",
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

    with patch('superagi.models.toolkit.Toolkit.get_toolkit_from_name', new=MockToolKit.get_toolkit_from_name), \
            mock_tool_config_db('superagi.controllers.tool_config.db') as mock_db:
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


def test_get_all_tool_configs_success(mock_toolkits):
    user_organisation, user_toolkits, tool_config, tool_kit_1, tool_kit_2 = mock_toolkits

    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
            patch('superagi.controllers.tool_config.db') as mock_db, \
            patch('superagi.helper.auth.db') as mock_auth_db:
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = tool_kit_1
        mock_db.session.query.return_value.filter.return_value.all.side_effect = [
            [tool_kit_1, tool_kit_2],
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


def test_get_all_tool_configs_toolkit_not_found(mock_toolkits):
    user_organisation, _, _, _, _ = mock_toolkits

    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
            patch('superagi.controllers.tool_config.db') as mock_db, \
            patch('superagi.helper.auth.db') as mock_auth_db:
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = None
        response = client.get(f"/tool_configs/get/toolkit/nonexistent_toolkit")

        # Assertions
        assert response.status_code == 404
        assert response.json() == {'detail': 'ToolKit not found'}
