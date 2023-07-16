from unittest.mock import create_autospec

from sqlalchemy.orm import Session

from superagi.models.agent import Agent


def test_get_agent_from_id():
    # Create a mock session
    session = create_autospec(Session)

    # Create a sample agent ID
    agent_id = 1

    # Create a mock agent object to be returned by the session query
    mock_agent = Agent(id=agent_id, name="Test Agent", project_id=1, description="Agent for testing")

    # Configure the session query to return the mock agent
    session.query.return_value.filter.return_value.first.return_value = mock_agent

    # Call the method under test
    agent = Agent.get_agent_from_id(session, agent_id)

    # Assert that the returned agent object matches the mock agent
    assert agent == mock_agent
