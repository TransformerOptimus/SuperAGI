import sys
from pathlib import Path

import pytest
from fastapi import HTTPException
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
from superagi.controllers.tool_config import get_all_tool_configs

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


def test_update_tool_config_success():
    toolkit_name = "test_toolkit"
    configs = [
        {
            "key": "test_key_1",
            "value": "test_value_1",
        },
        {
            "key": "test_key_2",
            "value": "test_value_2",
        },
    ]

    with patch('superagi.models.toolkit.ToolKit.get_toolkit_from_name', new=MockToolKit.get_toolkit_from_name) \
            as mock_get_toolkit_from_name, \
            mock_tool_config_db('superagi.controllers.tool_config.db') as mock_db_session:
        # Mock the get_toolkit_from_name function
        mock_toolkit = MagicMock()
        mock_get_toolkit_from_name.return_value = mock_toolkit

        # Mock
        mock_tool_config = MagicMock()
        mock_db_session.query().filter_by().first.return_value = mock_tool_config

        # Call the API endpoint
        response = client.post(f"/tool_configs/add/{toolkit_name}", json=configs)

        # Check status code
        assert response.status_code == 201

        # Check response content
        assert response.json() == {"message": "Tool configs updated successfully"}


# def test_update_tool_config_toolkit_not_found():
#     toolkit_name = "non_existent_toolkit"
#     configs = [
#         {
#             "key": "test_key_1",
#             "value": "test_value_1",
#         },
#         {
#             "key": "test_key_2",
#             "value": "test_value_2",
#         },
#     ]
#
#     with patch('superagi.models.toolkit.ToolKit.get_toolkit_from_name', new=MockToolKit.get_toolkit_from_name) \
#             as mock_get_toolkit_from_name, \
#             mock_tool_config_db('superagi.controllers.tool_config.db') as mock_db_session:
#         # Mock the get_toolkit_from_name function
#         mock_get_toolkit_from_name.return_value = None
#
#         # Call the API endpoint
#         response = client.post(f"/tool_configs/add/{toolkit_name}", json=configs)
#
#         # Print response content for debugging
#         print("DEBUG :: ")
#         print(response.json())
#
#
#         # Check status code
#         assert response.status_code == 404

# Check response content
# assert response.json() == {"detail": "Tool kit not found"}


# def test_get_all_tool_configs_success():
#     toolkit_name = "test_toolkit"
#
#     with patch('superagi.models.toolkit.ToolKit.get_toolkit_from_name', new=MockToolKit.get_toolkit_from_name) \
#             as mock_get_toolkit_from_name, \
#             mock_tool_config_db('superagi.controllers.tool_config.db') as mock_db_session, \
#             patch('superagi.helper.auth.get_user_organisation') as mock_user_organisation:
#         # patch('superagi.helper.auth.get_user_organisation') as mock_user_organisation:
#
#         mock_toolkit = MagicMock()
#         print("Mocks : ",mock_toolkit)
#         mock_get_toolkit_from_name.return_value = mock_toolkit
#         print(mock_toolkit)
#         mock_user_organisation.return_value = MagicMock()
#         print(mock_user_organisation)
#         print("ORG : =>")
#         print(mock_user_organisation.return_value)
#         mock_tool_configs = [MagicMock() for _ in range(3)]
#         print(mock_tool_configs)
#         mock_db_session.query().filter().all.return_value = mock_tool_configs
#         print(mock_db_session)
#         # assert 2 == 2
#         response = client.get(f"/tool_configs/get/toolkit/{toolkit_name}")
#         print("RESP : ",response)
#         assert response.status_code == 200
#         assert len(response.json()) == len(mock_tool_configs)

def mock_db_query(*args, **kwargs):
    magic_query = MagicMock()
    magic_query.filter.return_value = magic_query
    magic_query.filter_by.return_value = magic_query
    magic_query.first.return_value = magic_query
    magic_query.all.return_value = magic_query

    return magic_query


# def test_get_all_tool_configs_success():
#     toolkit_name = "test_toolkit"
#
#     with patch('superagi.models.toolkit.ToolKit.get_toolkit_from_name', new=MockToolKit.get_toolkit_from_name) \
#             as mock_get_toolkit_from_name, \
#             patch('superagi.helper.auth.get_user_organisation') as mock_user_organisation, \
#             patch('superagi.controllers.tool_config.db') as mock_db, \
#             patch('superagi.helper.auth.db') as mock_auth_db:
#
#         mock_toolkit = MagicMock()
#         mock_get_toolkit_from_name.return_value = mock_toolkit
#         mock_user_organisation.return_value = MagicMock()
#
#         mock_tool_configs = [MagicMock() for _ in range(3)]
#
#         # Mock db.session.query calls for main function
#         mock_db.session.query.side_effect = mock_db_query
#         mock_db.session.query().filter_by().first.return_value = mock_toolkit
#         mock_db.session.query().filter().all.return_value = mock_tool_configs
#
#         # Mock db.session.query calls for get_user_organisation function
#         mock_auth_db.session.query.side_effect = mock_db_query
#         mock_auth_db.session.query().filter().first.return_value = MagicMock()
#         mock_auth_db.session.query().filter().first.return_value.organisation_id = MagicMock()
#         mock_auth_db.session.query().filter().first.return_value = MagicMock()
#
#         response = client.get(f"/tool_configs/get/toolkit/{toolkit_name}")
#
#         assert response.status_code == 200
#         assert len(response.json()) == len(mock_tool_configs)

def test_get_all_tool_configs_success():
    toolkit_name = "test_toolkit"

    with    patch('superagi.helper.auth.get_user_organisation') as mock_user_organisation, \
            patch('superagi.controllers.tool_config.db') as mock_db, \
            patch('superagi.helper.auth.db') as mock_auth_db:
        # Mock user_toolkits to include mock_toolkit
        my_mock_tookit = ToolKit(id=1, name="test_toolkit_1", description="test description", show_toolkit=True,
                                 organisation_id=1,
                                 tool_code_link="code-link")
        # user_toolkits = [
        #     ToolKit(id=1, name="test_toolkit_1", description="test description", show_toolkit=True, organisation_id=1,
        #             tool_code_link="code-link")]

        # mock_toolkit = ToolKit(id=1, name="test_toolkit_1", description="test description", show_toolkit=True, organisation_id=1,
        #             tool_code_link="code-link")

        # mock_toolkit = user_toolkits[0]

        # mock_toolkit = MagicMock()
        # mock_get_toolkit_from_name.return_value = mock_toolkit
        # mock_user_organisation.return_value = MagicMock()
        #
        mock_tool_configs = [MagicMock() for _ in range(3)]
        #
        #
        # # Mock db.session.query calls for main function
        # mock_db.session.query.side_effect = mock_db_query
        mock_db.session.query().filter_by().first.return_value = my_mock_tookit
        # mock_db.session.query().filter().all.return_value = mock_tool_configs
        mock_db.session.query().filter().all.return_value = [my_mock_tookit]
        #
        # # Mock db.session.query calls for get_user_organisation function
        # mock_auth_db.session.query.side_effect = mock_db_query
        # mock_auth_db.session.query().filter().first.return_value = MagicMock()
        # mock_auth_db.session.query().filter().first.return_value.organisation_id = MagicMock()
        # mock_auth_db.session.query().filter().first.return_value = MagicMock()

        response = client.get(f"/tool_configs/get/toolkit/{toolkit_name}")

        assert response.status_code == 200
        assert len(response.json()) == len(mock_tool_configs)


# def test_get_all_tool_configs_success():
#     toolkit_name = "test_toolkit"
#
#     with patch('superagi.models.toolkit.ToolKit.get_toolkit_from_name', new=MockToolKit.get_toolkit_from_name) \
#             as mock_get_toolkit_from_name, \
#             patch('superagi.helper.auth.get_user_organisation') as mock_user_organisation, \
#             patch('superagi.controllers.tool_config.db') as mock_db, \
#             patch('superagi.helper.auth.db') as mock_auth_db:
#
#         mock_toolkit = MagicMock()
#         mock_get_toolkit_from_name.return_value = mock_toolkit
#         mock_user_organisation.return_value = MagicMock()
#
#         mock_tool_configs = [MagicMock() for _ in range(3)]
#
#         # Mock user_toolkits to include mock_toolkit
#         user_toolkits = [mock_toolkit]
#
#         # Mock db.session.query calls
#         mock_db.session.query.side_effect = mock_db_query
#         mock_db.session.query().filter_by().first.return_value = mock_toolkit
#         mock_db.session.query().filter(ToolConfig.toolkit_id == mock_toolkit.id).all.return_value = mock_tool_configs
#         mock_db.session.query().filter(
#             ToolKit.organisation_id == mock_user_organisation.return_value.id).all.return_value = user_toolkits
#
#         # Mock db.session.query calls for get_user_organisation function
#         mock_auth_db.session.query.side_effect = mock_db_query
#         mock_auth_db.session.query().filter().first.return_value = MagicMock()
#         mock_auth_db.session.query().filter().first.return_value.organisation_id = MagicMock()
#         mock_auth_db.session.query().filter().first.return_value = MagicMock()
#
#         response = client.get(f"/tool_configs/get/toolkit/{toolkit_name}")
#
#         assert response.status_code == 200
#         assert len(response.json()) == len(mock_tool_configs)

# def test_get_all_tool_configs_success():
#     toolkit_name = "test_toolkit"
#
#     user_organisation = Organisation()
#     user_organisation.id = 1
#
#     user_toolkits = [ToolKit(id=1, name=toolkit_name, organisation_id=user_organisation.id,tool_code_link="tool-code-link")]
#
#     test_toolkit = ToolKit(id=1, name=toolkit_name, organisation_id=user_organisation.id,tool_code_link="tool-code-link")
#     tool_configs = [ToolConfig(id=1, toolkit_id=test_toolkit.id)]  # add other required attributes here]
#
#     # with    patch("your_app.helper.auth.get_user_organisation", return_value=user_organisation) as mock_user_organisation, \
#     #         patch("your_app.controllers.too   l_config.db.session.query") as mock_db_query, \
#     #         patch("your_app.helper.auth.db") as mock_auth_db:
#     with    patch('superagi.helper.auth.get_user_organisation') as mock_user_organisation, \
#             patch('superagi.controllers.tool_config.db') as mock_db, \
#             patch('superagi.helper.auth.db') as mock_auth_db:


def test_get_all_tool_configs_success():
    toolkit_name = "test_toolkit"

    user_organisation = Organisation()
    user_organisation.id = 1

    user_toolkits = [
        Toolkit(id=1, name=toolkit_name, organisation_id=user_organisation.id, tool_code_link="tool-code-link")]

    test_toolkit = Toolkit(id=1, name=toolkit_name, organisation_id=user_organisation.id,
                           tool_code_link="tool-code-link")
    # tool_configs = [ToolConfig(id=1, toolkit_id=test_toolkit.id)]

    # with patch("your_app.controllers.tool_config.db") as mock_db, \
    #         patch("your_app.helper.auth.db") as mock_auth_db:
    with    patch('superagi.helper.auth.get_user_organisation') as mock_user_organisation, \
            patch('superagi.controllers.tool_config.db') as mock_db, \
            patch('superagi.helper.auth.db') as mock_auth_db:
        # Mock the database session and query
        mock_session = mock_db.session
        # mock_session.query.return_value.filter.return_value.all.return_value = user_toolkits
        mock_session.query.return_value.filter_by.return_value.first.return_value = test_toolkit
        # mock_session.query.return_value.filter.return_value.all.return_value = tool_configs
        # mock_session.query.return_value.filter.return_value.all.side_effect = lambda *args: (
        #     user_toolkits if args[0] == ToolKit.organisation_id == user_organisation.id else [test_toolkit]
        # )
        mock_session.query.return_value.filter.return_value.all.side_effect = [
            #     # First call to query
            MagicMock(
                toolkit_id=1, key="config_1", value="old_value_1"
            ),
            # Second call to query
            MagicMock(
                toolkit_id=1, key="config_2", value="old_value_2"
            ),
        ]
        # mock_db.query.return_value.filter_by.return_value.first.side_effect = [
        #     # First call to query
        #     MagicMock(
        #         toolkit_id=1, key="config_1", value="old_value_1"
        #     ),
        #     # Second call to query
        #     MagicMock(
        #         toolkit_id=1, key="config_2", value="old_value_2"
        #     ),
        # ]

        # Use the test client to send a request to the API endpoint
        client = TestClient(app)
        response = client.get(f"/tool_configs/get/toolkit/{toolkit_name}")

        # Assertions
        assert response.status_code == 200
        assert response.json() == [{"id": 1, "toolkit_id": 1}]  # Adjust the expected response as per your data model

        # # Verify that the database session and query were called
        # mock_session.query.assert_called_with(ToolKit)
        # mock_session.query.return_value.filter.assert_called_with(ToolKit.organisation_id == user_organisation.id)
        # mock_session.query.return_value.filter_by.assert_called_with(name=toolkit_name)
        # mock_session.query.assert_called_with(ToolConfig)
        # mock_session.query.return_value.filter.assert_called_with(ToolConfig.toolkit_id == test_toolkit.id)


def test_get_all_tool_configs_success():
    toolkit_name = "test_toolkit"

    user_organisation = Organisation()
    user_organisation.id = 1

    user_toolkits = [
        Toolkit(id=1, name=toolkit_name, organisation_id=user_organisation.id, tool_code_link="tool-code-link")]

    test_toolkit = Toolkit(id=1, name=toolkit_name, organisation_id=user_organisation.id,
                           tool_code_link="tool-code-link")
    tool_configs = [
        ToolConfig(id=1, toolkit_id=test_toolkit.id, key="config_1", value="old_value_1"),
        ToolConfig(id=2, toolkit_id=test_toolkit.id, key="config_2", value="old_value_2")
    ]

    # with patch("your_app.controllers.tool_config.db") as mock_db, \
    #         patch("your_app.helper.auth.db") as mock_auth_db:
    with    patch('superagi.helper.auth.get_user_organisation') as mock_user_organisation, \
            patch('superagi.controllers.tool_config.db') as mock_db, \
            patch('superagi.helper.auth.db') as mock_auth_db:
        # Mock the database session and query
        mock_session = mock_db.session
        mock_session.query.return_value.filter.return_value.all.side_effect = lambda *args: (
            user_toolkits if args[0] == Toolkit.organisation_id == user_organisation.id else tool_configs
        )

        # Use the test client to send a request to the API endpoint
        client = TestClient(app)
        response = client.get(f"/tool_configs/get/toolkit/{toolkit_name}")

        # Assertions
        assert response.status_code == 200
        assert response.json() == [
            {"id": 1, "toolkit_id": 1, "key": "config_1", "value": "old_value_1"},
            {"id": 2, "toolkit_id": 1, "key": "config_2", "value": "old_value_2"}
        ]  # Adjust the expected response as per your data model

        # Verify that the database session and query were called
        # mock_session.query.assert_called_with(ToolKit)
        # mock_session.query.return_value.filter.assert_called_with(ToolKit.organisation_id == user_organisation.id)
        # mock_session.query.return_value.filter_by.assert_called_with(name=toolkit_name)
        # mock_session.query.assert_called_with(ToolConfig)
        # mock_session.query.return_value.filter.assert_called_with(ToolConfig.toolkit_id == test_toolkit.id)


# @pytest.fixture
# def mock_toolkits():
#     # Mock tool kit data for testing
#     toolkit_name = "test_toolkit"
#     user_organisation = Organisation()
#     user_organisation.id = 1
#     toolkit = ToolKit(
#         id=1,
#         name=toolkit_name,
#         organisation_id=user_organisation.id,
#         tool_code_link="tool-code-link"
#     )
#     user_toolkits = [toolkit]
#     return toolkit_name, user_organisation, user_toolkits, toolkit
# @pytest.fixture
# def mock_toolkits():
#     # Mock tool kit data for testing
#     toolkit_name = "test_toolkit"
#     user_organisation = Organisation()
#     user_organisation.id = 1
#     toolkit = ToolKit(
#         id=1,
#         name=toolkit_name,
#         organisation_id=user_organisation.id,
#         tool_code_link="tool-code-link"
#     )
#     user_toolkits = [toolkit]
#     return toolkit_name, user_organisation, user_toolkits, toolkit
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


# def test_get_all_tool_configs_success(mock_toolkits):
#     toolkit_name, user_organisation, user_toolkits, toolkit = mock_toolkits
#
#     # class ToolKitQuery:
#     #     def filter(self, *args, **kwargs):
#     #         return self
#     #
#     #     def filter_by(self, **kwargs):
#     #         return self
#     #
#     #     def all(self):
#     #         return user_toolkits
#     #
#     # class ToolConfigQuery:
#     #     def filter(self, *args, **kwargs):
#     #         return self
#     #
#     #     def all(self):
#     #         return [ToolConfig()]
#
#     # with patch('your_app.controllers.get_user_organisation') as mock_get_user_org, \
#     #      patch('your_app.controllers.db') as mock_db:
#     with    patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
#             patch('superagi.controllers.tool_config.db') as mock_db, \
#             patch('superagi.helper.auth.db') as mock_auth_db:
#         # Mock the dependencies
#         mock_get_user_org.return_value = user_organisation
#
#         # Mock the query objects for ToolKit and ToolConfig
#         # mock_toolkit_query = MagicMock()
#         # mock_tool_config_query = MagicMock()
#
#         # mock_toolkit_query = toolkit
#         mock_tool_config_query = MagicMock()
#
#         mock_tool_config_query.filter.return_value.all.return_value.side_effect = [user_toolkits, [ToolConfig()]]
#
#         # mock_db.session.query.return_value.filter.return_value.all.return_value = user_toolkits
#         mock_db.session.query.return_value.filter_by.return_value.first.return_value = toolkit
#         # mock_db.session.query.return_value.filter.return_value.all.return_value = [ToolConfig()]
#
#         # Mock the behavior of the query objects
#         # mock_toolkit_query.filter.return_value.all.return_value = user_toolkits
#         # mock_toolkit_query.filter_by.return_value.first.return_value = toolkit
#
#         # mock_tool_config_query.filter.return_value.all.return_value = [ToolConfig()]
#
#         # Call the function being tested
#         result = get_all_tool_configs(toolkit_name, organisation=user_organisation)
#
#         # Assertions
#         assert isinstance(result, list)
#         assert len(result) == 1


def test_get_all_tool_configs_toolkit_not_found(mock_toolkits):
    toolkit_name, user_organisation, user_toolkits, _ = mock_toolkits

    # with patch('your_app.controllers.get_user_organisation') as mock_get_user_org, \
    #      patch('your_app.controllers.db') as mock_db:
    with    patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
            patch('superagi.controllers.tool_config.db') as mock_db, \
            patch('superagi.helper.auth.db') as mock_auth_db:
        query_1 = MagicMock()
        query_2 = MagicMock()

        # Mock the dependencies
        mock_get_user_org.return_value = user_organisation
        # mock_db.session.query.return_value.filter.return_value.all.return_value = user_toolkits
        # mock_db.session.query.return_value.filter_by.return_value.first.return_value = None
        query_1.filter.return_value.all.return_value = user_toolkits
        query_2.filter_by.return_value.first.return_value = None

        # Call the function being tested and assert the exception
        with pytest.raises(HTTPException) as exc:
            get_all_tool_configs(toolkit_name, organisation=user_organisation)

        assert exc.value.status_code == 404
        assert exc.value.detail == 'ToolKit not found'


#
# def test_get_all_tool_configs_unauthorized(mock_toolkits):
#     toolkit_name, user_organisation, user_toolkits, toolkit = mock_toolkits
#
#     # with patch('your_app.controllers.get_user_organisation') as mock_get_user_org, \
#     #      patch('your_app.controllers.db') as mock_db:
#     with    patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
#             patch('superagi.controllers.tool_config.db') as mock_db, \
#             patch('superagi.helper.auth.db') as mock_auth_db:
#         # Mock the dependencies
#         mock_get_user_org.return_value = user_organisation
#         mock_db.session.query.return_value.filter.return_value.all.return_value = user_toolkits
#         mock_db.session.query.return_value.filter_by.return_value.first.return_value = ToolKit(id=2)
#
#         # Call the function being tested and assert the exception
#         with pytest.raises(HTTPException) as exc:
#             get_all_tool_configs.get_all_tool_configs(toolkit_name)
#
#         assert exc.value.status_code == 403
#         assert exc.value.detail == 'Unauthorized'


# def test_get_all_tool_configs_success(mock_toolkits):
#     toolkit_name, user_organisation, user_toolkits, toolkit = mock_toolkits
#
#     with    patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
#             patch('superagi.controllers.tool_config.db') as mock_db, \
#             patch('superagi.helper.auth.db') as mock_auth_db:
#         toolkit = ToolKit(
#             id=1,
#             name=toolkit_name,
#             description="None",
#             show_toolkit=None,
#             organisation_id=1
#         )
#         user_toolkits = [toolkit]
#
#         # Mock the dependencies
#         mock_get_user_org.return_value = user_organisation
#
#         # mock_toolkit_query = toolkit
#         mock_tool_config_query = MagicMock()
#
#         mock_tool_config_query.filter.return_value.all.return_value.side_effect = [user_toolkits, [ToolConfig()]]
#
#         mock_db.session.query.return_value.filter_by.return_value.first.return_value = toolkit
#         # Call the function being tested
#         result = get_all_tool_configs(toolkit_name,organisation=user_organisation)
#
#         # Assertions
#         assert isinstance(result, list)
#         assert len(result) == 1

# def test_get_all_tool_configs_success(mock_toolkits):
#     toolkit_name, user_organisation, user_toolkits, toolkit = mock_toolkits
#
#     with    patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
#             patch('superagi.controllers.tool_config.db') as mock_db, \
#             patch('superagi.helper.auth.db') as mock_auth_db:
#         toolkit = Toolkit(
#             id=1,
#             name=toolkit_name,
#             description="None",
#             show_toolkit=None,
#             organisation_id=1
#         )
#         mock_query = MagicMock()
#
#         # Mock the first call to query.filter().all()
#         mock_query.filter.return_value.all.return_value = [user_toolkits]
#
#         # Mock the second call to query.filter().all()
#         mock_query.filter.return_value.all.side_effect = [[ToolConfig()]]
#
#         # Mock the session.query() call to return the query object
#         mock_db.session.query.return_value = mock_query
#
#         # user_toolkits = [toolkit]
#         #
#         # # Mock the dependencies
#         # mock_get_user_org.return_value = user_organisation
#         #
#         # # mock_toolkit_query = toolkit
#         # mock_tool_config_query = MagicMock()
#         #
#         # mock_tool_config_query.filter.return_value.all.side_effect = [user_toolkits, [ToolConfig()]]
#         #
#         # mock_db.session.query.return_value.filter_by.return_value.first.return_value = toolkit
#         # Call the function being tested
#         result = get_all_tool_configs(toolkit_name, organisation=user_organisation)
#
#         # Assertions
#         assert isinstance(result, list)
#         assert len(result) == 1


# def test_get_all_tool_configs_success(mock_toolkits):
#     toolkit_name, user_organisation, user_toolkits, toolkit = mock_toolkits
#
#     with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
#             patch('superagi.controllers.tool_config.db') as mock_db, \
#             patch('superagi.helper.auth.db') as mock_auth_db:
#         toolkit = ToolKit(
#             id=1,
#             name=toolkit_name,
#             description="None",
#             show_toolkit=None,
#             organisation_id=1
#         )
#         user_toolkits = [toolkit]
#
#         # Mock the dependencies
#         mock_get_user_org.return_value = user_organisation
#
#         # Mock the query and its filter method
#         mock_query = MagicMock()
#         mock_filter = MagicMock()
#         mock_query.filter_by.return_value = mock_filter
#
#         # Return the user_toolkits list when filter().all() is called
#         mock_filter.all.return_value = user_toolkits
#
#         mock_db.session.query.return_value = mock_query
#         mock_db.session.query.return_value.filter_by.return_value.first.return_value = toolkit
#
#         # Call the function being tested
#         result = get_all_tool_configs(toolkit_name, organisation=user_organisation)
#
#         # Assertions
#         assert isinstance(result, list)
#         assert len(result) == 1

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
