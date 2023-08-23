from unittest.mock import create_autospec

from sqlalchemy.orm import Session
from superagi.models.agent_schedule import AgentSchedule

def test_find_by_agent_id():
    # Create a mock session
    session = create_autospec(Session)

    # Create a sample agent ID
    agent_id = 1

    # Create a mock agent schedule object to be returned by the session query
    mock_agent_schedule = AgentSchedule(id=1,agent_id=agent_id, start_time="2023-08-10 12:17:00", recurrence_interval="2 Minutes", expiry_runs=2)

    # Configure the session query to return the mock agent
    session.query.return_value.filter.return_value.first.return_value = mock_agent_schedule

    # Call the method under test
    agent_schedule = AgentSchedule.find_by_agent_id(session, agent_id)

    # Assert that the returned agent object matches the mock agent
    assert agent_schedule == mock_agent_schedule
