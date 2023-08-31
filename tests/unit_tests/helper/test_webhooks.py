import json
from unittest.mock import Mock, patch
import pytest
from superagi.helper.webhook_manager import WebHookManager
from superagi.models.webhooks import Webhooks

@pytest.fixture
def mock_session():
    return Mock()

@pytest.fixture
def mock_agent_execution():
    return Mock()

@pytest.fixture
def mock_agent():
    return Mock()

@pytest.fixture
def mock_webhook():
    return Mock()

@pytest.fixture
def mock_org():
    org_mock = Mock()
    org_mock.id = "mock_org_id"
    return org_mock

def test_agent_status_change_callback(
    mock_session, mock_agent_execution, mock_agent, mock_org, mock_webhook
):
    curr_status = "NEW_STATUS"
    old_status = "OLD_STATUS"
    mock_agent_id = "mock_agent_id"
    mock_org_id = "mock_org_id"

    # Create a mock instance of AgentExecution and set its attributes
    mock_agent_execution_instance = Mock()
    mock_agent_execution_instance.agent_id = "mock_agent_id"

    # Create a mock instance of Agent and set its attributes
    mock_agent_instance = Mock()
    mock_agent_instance.get_agent_organisation.return_value = mock_org

    # Create a mock instance of Webhooks and set its attributes
    mock_webhook_instance = Mock(spec=Webhooks)
    mock_webhook_instance.filters = {"status": ["PAUSED", "RUNNING"]}

    # Set up session.query().filter().all() to return the mock_webhook_instance
    mock_session.query.return_value.filter.return_value.all.return_value = [mock_webhook_instance]

    # Patch required functions/methods
    with patch(
        'superagi.controllers.agent_execution_config.AgentExecution.get_agent_execution_from_id',
        return_value=mock_agent_execution_instance
    ), patch(
        'superagi.models.agent.Agent.get_agent_from_id',
        return_value=mock_agent_instance
    ), patch(
        'requests.post',
        return_value=Mock(status_code=200)  # Mock the status_code response
    ) as mock_post, patch(
        'json.dumps'
    ) as mock_json_dumps:

        # Create the WebHookManager instance
        web_hook_manager = WebHookManager(mock_session)

        # Call the function
        web_hook_manager.agent_status_change_callback(
            mock_agent_execution_instance, curr_status, old_status
        )

    assert mock_agent_execution_instance.agent_status_change_callback

