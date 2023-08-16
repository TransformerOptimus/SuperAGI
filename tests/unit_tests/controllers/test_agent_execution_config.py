from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration

client = TestClient(app)

@pytest.fixture
def mocks():
    # Mock tool kit data for testing
    mock_agent = Agent(id=1, name="test_agent", project_id=1, description="testing", agent_workflow_id=1, is_deleted=False)
    mock_agent_config = AgentConfiguration(id=1, agent_id=1, key="test_key", value="['test']")
    mock_execution = AgentExecution(id=54, agent_id=1, name="test_execution")
    mock_execution_config = [AgentExecutionConfiguration(id=64, agent_execution_id=1, key="test_key", value="['test']")]
    return mock_agent,mock_agent_config,mock_execution,mock_execution_config


def test_get_agent_execution_configuration_not_found_failure():
    with patch('superagi.controllers.agent_execution_config.db') as mock_db:
        mock_db.session.query.return_value.filter.return_value.all.return_value = []
        mock_db.session.query.return_value.filter.return_value.first.return_value = None
        response = client.get("/agent_executions_configs/details/agent_id/1/agent_execution_id/1")

        assert response.status_code == 404
        assert response.json() == {"detail": "Agent not found"}


def test_get_agent_execution_configuration_success(mocks):
    with patch('superagi.controllers.agent_execution_config.db') as mock_db:
        mock_agent, mock_agent_config, mock_execution, mock_execution_config = mocks

        # Configure the mock objects to return the mock values
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_agent
        mock_db.session.query.return_value.filter.return_value.all.return_value = [mock_agent_config]
        mock_db.session.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_execution
        mock_db.session.query.return_value.filter.return_value.all.return_value = mock_execution_config

        # Mock the AgentExecution.get_agent_execution_from_id method to return the mock_execution object
        with patch('superagi.controllers.agent_execution_config.AgentExecution.get_agent_execution_from_id') as mock_get_exec:
            mock_get_exec.return_value = mock_execution

            response = client.get("/agent_executions_configs/details/agent_id/1/agent_execution_id/1")

            assert response.status_code == 200


