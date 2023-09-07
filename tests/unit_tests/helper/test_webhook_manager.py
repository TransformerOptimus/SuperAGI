import pytest
import requests
from unittest.mock import Mock, patch
from superagi.helper.webhook_manager import WebHookManager  # Import the class containing the function to test
from unittest.mock import create_autospec
from sqlalchemy.orm import Session
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent import Agent
from superagi.models.organisation import Organisation
from superagi.models.webhooks import Webhooks
@pytest.fixture
def my_class():
    # create mock session
    session = create_autospec(Session)

    # instantiate the class with mock session
    my_instance = WebHookManager(session=session)

    return my_instance


def test_agent_status_change_callback(my_class):
    agent_execution_id = 1
    curr_status = "COMPLETED"
    old_status = "STARTED"

    # Create mock objects to be returned by the mocked methods
    mock_agent_execution = AgentExecution(agent_id=1)
    mock_agent = Agent()
    mock_org = Organisation()
    mock_webhook_obj = Webhooks()
    mock_request = Mock()
    mock_request.status_code = 200

    # Assign the return values of mock objects to mocked methods
    my_class.session.query.return_value.filter.return_value.first.return_value = mock_agent_execution
    Agent.get_agent_from_id.return_value = mock_agent
    mock_agent.get_agent_organisation.return_value = mock_org
    my_class.session.query.return_value.filter.return_value.all.return_value = [mock_webhook_obj]

    with patch.object(requests, 'post', return_value=mock_request) as mock_post:

        # Call the method under test
        my_class.agent_status_change_callback(agent_execution_id, curr_status, old_status)

        # Assert the necessary methods were called with expected arguments
        AgentExecution.get_agent_execution_from_id.assert_called_with(my_class.session, agent_execution_id)
        Agent.get_agent_from_id.assert_called_with(my_class.session, mock_agent_execution.agent_id)
        mock_agent.get_agent_organisation.assert_called_with(my_class.session)
        my_class.session.query.assert_called_with(Webhooks)
        mock_post.assert_called_with(mock_webhook_obj.url.strip(), data=json.dumps(webhook_obj_body),
                                     headers=mock_webhook_obj.headers)

        # Assert that the object was added and committed to session
        my_class.session.add.assert_called_once()
        my_class.session.commit.assert_called_once()
