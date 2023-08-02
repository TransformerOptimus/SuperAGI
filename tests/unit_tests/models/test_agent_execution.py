from unittest.mock import create_autospec

from sqlalchemy.orm import Session

from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution


def test_get_agent_execution_from_id():
    # Create a mock session
    session = create_autospec(Session)

    # Create a sample agent ID
    agent_execution_id = 1

    # Create a mock agent execution object to be returned by the session query
    mock_agent_execution = AgentExecution(id=agent_execution_id, name="Test Execution")

    # Configure the session query to return the mock agent
    session.query.return_value.filter.return_value.first.return_value = mock_agent_execution

    # Call the method under test
    agent = AgentExecution.get_agent_execution_from_id(session, agent_execution_id)

    # Assert that the returned agent object matches the mock agent
    assert agent == mock_agent_execution
