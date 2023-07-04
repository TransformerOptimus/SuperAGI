from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app
from superagi.models.agent_execution_config import AgentExecutionConfiguration

client = TestClient(app)


@pytest.fixture
def mocks():
    # Mock tool kit data for testing
    mock_execution_config = AgentExecutionConfiguration(id=1, key="test_key", value="['test']")
    return mock_execution_config


def test_get_agent_execution_configuration_success(mocks):
    with patch('superagi.controllers.agent_execution_config.db') as mock_db:
        mock_execution_config = mocks
        mock_db.session.query.return_value.filter.return_value.all.return_value = [mock_execution_config]

        response = client.get("/agent_executions_configs/details/1")

        assert response.status_code == 200
        assert response.json() == {"test_key": ['test']}


def test_get_agent_execution_configuration_not_found():
    with patch('superagi.controllers.agent_execution_config.db') as mock_db:
        mock_db.session.query.return_value.filter.return_value.all.return_value = []
        response = client.get("/agent_executions_configs/details/1")

        assert response.status_code == 404
        assert response.json() == {"detail": "Agent Execution Configuration not found"}
