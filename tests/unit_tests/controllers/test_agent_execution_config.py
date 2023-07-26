from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration

client = TestClient(app)


@pytest.fixture
def mocks():
    # Mock tool kit data for testing
    mock_execution_config = [AgentExecutionConfiguration(id=1, key="test_key", value="['test']")]
    mock_execution = AgentExecution(id=1,name="test_execution")
    return mock_execution,mock_execution_config


def test_get_agent_execution_configuration_success(mocks):
    with patch('superagi.controllers.agent_execution_config.db') as mock_db:
        _,mock_execution_config = mocks
        mock_db.session.query.return_value.filter.return_value.all.return_value = mock_execution_config

        response = client.get("/agent_executions_configs/details/agent/1/agent_execution/1")

        assert response.status_code == 200
        assert response.json() == {"test_key": ['test']}


def test_get_agent_execution_configuration_not_found_failure():
    with patch('superagi.controllers.agent_execution_config.db') as mock_db:
        mock_db.session.query.return_value.filter.return_value.all.return_value = []
        mock_db.session.query.return_value.filter.return_value.first.return_value = None
        response = client.get("/agent_executions_configs/details/agent/1/agent_execution/1")

        assert response.status_code == 404
        assert response.json() == {"detail": "Agent Configuration not found"}


def test_get_agent_execution_configuration_not_found_success(mocks):
    with patch('superagi.controllers.agent_execution_config.db') as mock_db:
        mock_execution,mock_execution_config = mocks
        mock_db.session.query.return_value.filter.return_value.all.side_effect = [[], mock_execution_config]
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_execution
        response = client.get("/agent_executions_configs/details/agent/1/agent_execution/1")

        assert response.status_code == 200
