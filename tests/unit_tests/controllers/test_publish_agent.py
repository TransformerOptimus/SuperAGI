import pytest
from fastapi.testclient import TestClient
from unittest.mock import create_autospec, patch
from main import app
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.organisation import Organisation
from superagi.models.user import User
from sqlalchemy.orm import Session

client = TestClient(app)

@pytest.fixture
def mocks():
    # Mock tool kit data for testing
    mock_agent = Agent(id=1, name="test_agent", project_id=1, description="testing", agent_workflow_id=1, is_deleted=False)
    mock_agent_config = AgentConfiguration(id=1, agent_id=1, key="test_key", value="['test']")
    mock_execution = AgentExecution(id=1, agent_id=1, name="test_execution")
    mock_execution_config = [AgentExecutionConfiguration(id=1, agent_execution_id=1, key="test_key", value="['test']")]
    return mock_agent,mock_agent_config,mock_execution,mock_execution_config

def test_publish_template(mocks):
    with patch('superagi.helper.auth.get_user_organisation') as mock_get_user_org, \
        patch('superagi.helper.auth.get_current_user') as mock_get_user, \
        patch('superagi.helper.auth.db') as mock_auth_db,\
        patch('superagi.controllers.agent_template.db') as mock_db:
    
            mock_session = create_autospec(Session)
            mock_agent, mock_agent_config, mock_execution, mock_execution_config = mocks  

            mock_session.query.return_value.filter.return_value.first.return_value = mock_agent
            mock_session.query.return_value.filter.return_value.all.return_value = [mock_agent_config]
            mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_execution
            mock_session.query.return_value.filter.return_value.all.return_value = mock_execution_config 

            with patch('superagi.controllers.agent_execution_config.AgentExecution.get_agent_execution_from_id') as mock_get_exec:
                mock_get_exec.return_value = mock_execution
                response = client.post("/agent_templates/publish_template/agent_execution_id/1")    
                assert response.status_code == 201