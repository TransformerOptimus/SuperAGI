import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

import superagi.config.config
from unittest.mock import MagicMock, patch,Mock
from main import app
from unittest.mock import patch,create_autospec
from sqlalchemy.orm import Session
from superagi.controllers.api.agent import ExecutionStateChangeConfigIn,AgentConfigUpdateExtInput
from superagi.models.agent import Agent
from superagi.models.project import Project

client = TestClient(app)

@pytest.fixture
def mock_api_key_get():
    mock_api_key = "your_mock_api_key"
    return mock_api_key
@pytest.fixture
def mock_execution_state_change_input():
    return {

    }
@pytest.fixture
def mock_run_id_config():
    return {
        "run_ids":[1,2]
    }

@pytest.fixture
def mock_agent_execution():
    return {

    }
@pytest.fixture
def mock_run_id_config_empty():
    return {
        "run_ids":[]
    }

@pytest.fixture
def mock_run_id_config_invalid():
    return {
        "run_ids":[12310]
    }
@pytest.fixture
def mock_agent_config_update_ext_input():
    return AgentConfigUpdateExtInput(
        tools=[{"name":"Image Generation Toolkit"}],
        schedule=None,
        goal=["Test Goal"],
        instruction=["Test Instruction"],
        constraints=["Test Constraints"],
        iteration_interval=10,
        model="Test Model",
        max_iterations=100,
        agent_type="Test Agent Type"
    )

@pytest.fixture
def mock_update_agent_config():
    return {
        "name": "agent_3_UPDATED",
        "description": "AI assistant to solve complex problems",
        "goal": ["create a photo of a cat"],
        "agent_type": "Dynamic Task Workflow",
        "constraints": [
            "~4000 word limit for short term memory.",
            "Your long term memory is short, so immediately save important information to files.",
            "If you are unsure how you previously did something or want to recall past events, thinking about similar events will help you remember.",
            "No user assistance",
            "Exclusively use the commands listed in double quotes e.g. \"command name\""
        ],
        "instruction": ["Be accurate"],
        "tools":[
            {
                "name":"Image Generation Toolkit"
            }
        ],
        "iteration_interval": 500,
        "model": "gpt-4",
        "max_iterations": 100
    }
# Define test cases

def test_update_agent_not_found(mock_update_agent_config,mock_api_key_get):
    with patch('superagi.helper.auth.get_organisation_from_api_key') as mock_get_user_org, \
            patch('superagi.helper.auth.validate_api_key') as mock_validate_api_key, \
                patch('superagi.helper.auth.db') as mock_auth_db, \
                    patch('superagi.controllers.api.agent.db') as db_mock:

        # Mock the session
        mock_session = create_autospec(Session)
        # # Configure session query methods to return None for agent
        mock_session.query.return_value.filter.return_value.first.return_value = None
        response = client.put(
            "/v1/agent/1",
            headers={"X-API-Key": mock_api_key_get},  # Provide the mock API key in headers
            json=mock_update_agent_config
        )
        assert response.status_code == 404
        assert response.text == '{"detail":"Agent not found"}'


def test_get_run_resources_no_run_ids(mock_run_id_config_empty,mock_api_key_get):
    with patch('superagi.helper.auth.get_organisation_from_api_key') as mock_get_user_org, \
            patch('superagi.helper.auth.validate_api_key') as mock_validate_api_key, \
                patch('superagi.helper.auth.db') as mock_auth_db, \
                    patch('superagi.controllers.api.agent.db') as db_mock, \
                        patch('superagi.controllers.api.agent.get_config', return_value="S3") as mock_get_config:

        # Mock the session
        mock_session = create_autospec(Session)
        # # Configure session query methods to return None for agent
        mock_session.query.return_value.filter.return_value.first.return_value = None
        response = client.post(
            "v1/agent/resources/output",
            headers={"X-API-Key": mock_api_key_get},  # Provide the mock API key in headers
            json=mock_run_id_config_empty
        )
        assert response.status_code == 404
        assert response.text == '{"detail":"No execution_id found"}'

def test_get_run_resources_invalid_run_ids(mock_run_id_config_invalid,mock_api_key_get):
    with patch('superagi.helper.auth.get_organisation_from_api_key') as mock_get_user_org, \
            patch('superagi.helper.auth.validate_api_key') as mock_validate_api_key, \
                patch('superagi.helper.auth.db') as mock_auth_db, \
                    patch('superagi.controllers.api.agent.db') as db_mock, \
                        patch('superagi.controllers.api.agent.get_config', return_value="S3") as mock_get_config:

        # Mock the session
        mock_session = create_autospec(Session)
        # # Configure session query methods to return None for agent
        mock_session.query.return_value.filter.return_value.first.return_value = None
        response = client.post(
            "v1/agent/resources/output",
            headers={"X-API-Key": mock_api_key_get},  # Provide the mock API key in headers
            json=mock_run_id_config_invalid
        )
        assert response.status_code == 404
        assert response.text == '{"detail":"One or more run_ids not found"}'

def test_resume_agent_runs_agent_not_found(mock_execution_state_change_input,mock_api_key_get):
    with patch('superagi.helper.auth.get_organisation_from_api_key') as mock_get_user_org, \
            patch('superagi.helper.auth.validate_api_key') as mock_validate_api_key, \
                patch('superagi.helper.auth.db') as mock_auth_db, \
                    patch('superagi.controllers.api.agent.db') as db_mock:

        # Mock the session
        mock_session = create_autospec(Session)
        # # Configure session query methods to return None for agent
        mock_session.query.return_value.filter.return_value.first.return_value = None
        response = client.post(
            "/v1/agent/1/resume",
            headers={"X-API-Key": mock_api_key_get},  # Provide the mock API key in headers
            json=mock_execution_state_change_input
        )
        assert response.status_code == 404
        assert response.text == '{"detail":"Agent not found"}'


def test_pause_agent_runs_agent_not_found(mock_execution_state_change_input,mock_api_key_get):
    with patch('superagi.helper.auth.get_organisation_from_api_key') as mock_get_user_org, \
            patch('superagi.helper.auth.validate_api_key') as mock_validate_api_key, \
                patch('superagi.helper.auth.db') as mock_auth_db, \
                    patch('superagi.controllers.api.agent.db') as db_mock:

        # Mock the session
        mock_session = create_autospec(Session)
        # # Configure session query methods to return None for agent
        mock_session.query.return_value.filter.return_value.first.return_value = None
        response = client.post(
            "/v1/agent/1/pause",
            headers={"X-API-Key": mock_api_key_get},  # Provide the mock API key in headers
            json=mock_execution_state_change_input
        )
        assert response.status_code == 404
        assert response.text == '{"detail":"Agent not found"}'

def test_create_run_agent_not_found(mock_agent_execution,mock_api_key_get):
    with patch('superagi.helper.auth.get_organisation_from_api_key') as mock_get_user_org, \
            patch('superagi.helper.auth.validate_api_key') as mock_validate_api_key, \
                patch('superagi.helper.auth.db') as mock_auth_db, \
                    patch('superagi.controllers.api.agent.db') as db_mock:

        # Mock the session
        mock_session = create_autospec(Session)
        # # Configure session query methods to return None for agent
        mock_session.query.return_value.filter.return_value.first.return_value = None
        response = client.post(
            "/v1/agent/1/run",
            headers={"X-API-Key": mock_api_key_get},  # Provide the mock API key in headers
            json=mock_agent_execution
        )
        assert response.status_code == 404
        assert response.text == '{"detail":"Agent not found"}'

def test_create_run_project_not_matching_org(mock_agent_execution, mock_api_key_get):
    with patch('superagi.helper.auth.get_organisation_from_api_key') as mock_get_user_org, \
            patch('superagi.helper.auth.validate_api_key') as mock_validate_api_key, \
            patch('superagi.helper.auth.db') as mock_auth_db, \
            patch('superagi.controllers.api.agent.db') as db_mock:

        # Mock the session and configure query methods to return agent and project
        mock_session = create_autospec(Session)
        mock_agent = Agent(id=1, project_id=1, agent_workflow_id=1)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_agent
        mock_project = Project(id=1, organisation_id=2)  # Different organisation ID
        db_mock.Project.find_by_id.return_value = mock_project
        db_mock.session.return_value.__enter__.return_value = mock_session

        response = client.post(
            "/v1/agent/1/run",
            headers={"X-API-Key": mock_api_key_get},
            json=mock_agent_execution
        )

        assert response.status_code == 404
        assert response.text == '{"detail":"Agent not found"}'
